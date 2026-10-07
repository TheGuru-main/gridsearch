"""
GSP OpenBox + Fantasy — combined backend.
- Auth, wallet, OpenBox items, fantasy
- Multi-source scraper admin (Transfermarkt CSV + Bzzoiro, resumable)
- News via GNews
- BubbleJumbo middleware wraps everything
"""
import os
import time
import uuid
import json
import threading
import hashlib
import httpx
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, init_db, SessionLocal
from models import (
    User, SessionToken, LedgerEntry, OpenBoxItem,
    Club, Player, Transfer, SyncLog, SyncState
)
from bubblejumbo_middleware import BubbleJumboMiddleware, bj_bridge

# ═══════════════════════════════════════════════════════
#  PATHS
# ═══════════════════════════════════════════════════════
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
STATIC_DIR = ROOT_DIR / "static"
UPLOAD_DIR = BACKEND_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════
WELCOME_BYFLINTS = 100000

TOURNAMENT_BASE = {
    "npfl": 280, "egypt_pl": 195, "sa_psl": 180, "botola": 175,
    "cafcl": 600, "cafcc": 450,
    "brasileirao_b": 180, "brasileirao_a": 190, "argentina_primera": 250,
    "mls": 350, "ligamx": 300, "j1": 200, "saudi_pl": 350,
    "eredivisie": 400, "portugal": 450, "turkey": 400,
    "epl": 500, "laliga": 330, "seriea": 400, "bundes": 350, "ligue1": 300,
    "ucl": 800, "uel": 700, "uecl": 600,
    "libertadores": 500, "sudamericana": 450,
    "concacaf_cl": 450, "afc_cl": 500,
    "worldcup": 1000, "afcon": 800, "euro": 900, "copa_america": 800,
}

POSITION_BONUS = {
    "GK": 23.5, "DEF": 35, "MID": 40, "FWD": 60,
    "Goalkeeper": 23.5, "Defender": 35, "Midfielder": 40, "Attacker": 60,
}

CATEGORY_COL = {"app": 0, "game": 1, "video": 2, "other": 3}

UPLOAD_FEE = {"app": 200000, "game": 200000, "video": 150000, "other": 0}
DOWNLOAD_FEE = 3000
UPLOADER_SHARE = 3000

SCRAPER_TOKEN = os.environ.get("SCRAPER_TOKEN", "openbox2026run")
GNEWS_KEY = os.environ.get("GNEWS_KEY", "")
BZZ_BASE = "https://sports.bzzoiro.com/api/v2"


# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


def current_gameweek() -> int:
    epoch = time.mktime(time.strptime("2026-01-01", "%Y-%m-%d"))
    return int((time.time() - epoch) // (7 * 86400)) + 1


def player_points(player_id: str, week: int) -> float:
    seed = f"{player_id}:{week}"
    h = 0
    for c in seed:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return round((h % 120) / 10 + 1.0, 1)


def player_price(tournament_id: str, player_id: str, position: str) -> int:
    base = TOURNAMENT_BASE.get(tournament_id, 400)
    pos_bonus = POSITION_BONUS.get(position or "", 40)
    h = sum(ord(c) for c in player_id) % 60
    return base + pos_bonus + h


def require_user(request: Request, db: Session) -> User:
    token = request.cookies.get("openbox_token")
    if not token:
        raise HTTPException(401, "Not authenticated")
    sess = db.get(SessionToken, token)
    if not sess:
        raise HTTPException(401, "Invalid session")
    user = db.get(User, sess.phone)
    if not user:
        raise HTTPException(401, "User missing")
    return user


def ledger_add(db: Session, phone: str, amount: float, reason: str, ref: str = ""):
    db.add(LedgerEntry(phone=phone, amount=amount, reason=reason, ref=ref, created_at=time.time()))
    user = db.get(User, phone)
    if user:
        user.byflints = (user.byflints or 0.0) + amount


def balance(db: Session, phone: str) -> float:
    user = db.get(User, phone)
    return float(user.byflints) if user else 0.0


def _bzz_headers():
    t = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {t}"} if t else {}


def _admin_guard(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")


# ═══════════════════════════════════════════════════════
#  FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(title="GSP OpenBox")
app.add_middleware(BubbleJumboMiddleware)
app.include_router(bj_bridge)


@app.on_event("startup")
def on_startup():
    init_db()
    # Resume interrupted Bzzoiro sync
    try:
        from bzz_sync import _run_sync_all
        db = SessionLocal()
        try:
            s = db.get(SyncState, "bzz_all")
            if s and s.running == 1:
                print("[startup] resuming interrupted Bzzoiro sync", flush=True)
                threading.Thread(target=_run_sync_all, args=(True,), daemon=True).start()
        finally:
            db.close()
    except Exception as e:
        print(f"[startup] resume check failed: {e}", flush=True)


# ═══════════════════════════════════════════════════════
#  PYDANTIC MODELS
# ═══════════════════════════════════════════════════════
class SignupReq(BaseModel):
    full_name: str
    phone: str
    email: str
    password: str
    dob: str
    talent: str
    country: str


class LoginReq(BaseModel):
    phone: str
    password: str


# ═══════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════
@app.post("/api/auth/signup")
def signup(req: SignupReq, db: Session = Depends(get_db)):
    if db.get(User, req.phone):
        raise HTTPException(400, "Phone already registered")
    user = User(
        phone=req.phone, full_name=req.full_name, email=req.email,
        password_hash=hash_password(req.password), dob=req.dob,
        talent=req.talent, country=req.country, byflints=0.0,
        created_at=time.time(),
    )
    db.add(user)
    db.commit()

    ledger_add(db, req.phone, WELCOME_BYFLINTS, "welcome_bonus", "signup")
    token = uuid.uuid4().hex
    db.add(SessionToken(token=token, phone=req.phone, created_at=time.time()))
    db.commit()

    resp = JSONResponse({
        "ok": True, "phone": req.phone,
        "full_name": req.full_name, "byflints": WELCOME_BYFLINTS,
    })
    resp.set_cookie("openbox_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return resp


@app.post("/api/auth/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.get(User, req.phone)
    if not user or user.password_hash != hash_password(req.password):
        raise HTTPException(401, "Invalid credentials")
    token = uuid.uuid4().hex
    db.add(SessionToken(token=token, phone=req.phone, created_at=time.time()))
    db.commit()
    resp = JSONResponse({
        "ok": True, "phone": user.phone,
        "full_name": user.full_name, "byflints": user.byflints,
    })
    resp.set_cookie("openbox_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return resp


@app.post("/api/auth/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("openbox_token")
    if token:
        sess = db.get(SessionToken, token)
        if sess:
            db.delete(sess)
            db.commit()
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("openbox_token")
    return resp


@app.get("/api/me")
def me(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    return {
        "phone": user.phone, "full_name": user.full_name,
        "email": user.email, "talent": user.talent,
        "country": user.country, "byflints": user.byflints,
    }



@app.on_event("startup")
def on_startup():
    init_db()

    # Schema drift guard: add missing columns to sync_state
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("""
            ALTER TABLE sync_state ADD COLUMN IF NOT EXISTS unmapped_clubs INTEGER DEFAULT 0
        """))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    # Resume interrupted Bzzoiro sync
    try:
        from bzz_sync import _run_sync_all
        db = SessionLocal()
        try:
            s = db.get(SyncState, "bzz_all")
            if s and s.running == 1:
                print("[startup] resuming interrupted Bzzoiro sync", flush=True)
                threading.Thread(target=_run_sync_all, args=(True,), daemon=True).start()
        finally:
            db.close()
    except Exception as e:
        print(f"[startup] resume check failed: {e}", flush=True)



# ═══════════════════════════════════════════════════════
#  WALLET
# ═══════════════════════════════════════════════════════
@app.get("/api/wallet")
def wallet(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    rows = db.query(LedgerEntry).filter_by(phone=user.phone)\
        .order_by(LedgerEntry.created_at.desc()).limit(200).all()
    return {
        "balance": user.byflints,
        "ledger": [
            {"amount": r.amount, "reason": r.reason, "ref": r.ref, "created_at": r.created_at}
            for r in rows
        ],
    }


# ═══════════════════════════════════════════════════════
#  OPENBOX ITEMS
# ═══════════════════════════════════════════════════════
@app.post("/api/openbox/upload")
async def ob_upload(
    request: Request,
    title: str = Form(...),
    kind: str = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    price_byflints: float = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    fee = UPLOAD_FEE.get(category, 5)
    if user.byflints < fee:
        raise HTTPException(402, f"Need {fee} byflints. Have {user.byflints}")

    item_id = "item-" + uuid.uuid4().hex[:12]
    ext = Path(file.filename).suffix
    stored_name = f"{item_id}{ext}"
    dest = UPLOAD_DIR / stored_name

    size = 0
    with dest.open("wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
            size += len(chunk)

    db.add(OpenBoxItem(
        id=item_id, title=title, kind=kind, category=category,
        description=description, uploader=user.phone,
        price_byflints=price_byflints, fee_paid=fee,
        filename=stored_name, file_size=size, mime_type=file.content_type,
        gsp_col=CATEGORY_COL.get(category, 3), gsp_row=1,
        created_at=time.time(),
    ))
    ledger_add(db, user.phone, -fee, f"upload:{title}", item_id)
    db.commit()
    return {"ok": True, "item_id": item_id, "balance": balance(db, user.phone)}


@app.get("/api/openbox/items")
def ob_list(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(OpenBoxItem)
    if category:
        q = q.filter(OpenBoxItem.category == category)
    rows = q.order_by(OpenBoxItem.created_at.desc()).limit(200).all()
    return {"items": [
        {
            "id": r.id, "title": r.title, "kind": r.kind, "category": r.category,
            "description": r.description, "uploader": r.uploader,
            "price_byflints": r.price_byflints, "gsp_col": r.gsp_col, "gsp_row": r.gsp_row,
            "downloads": r.downloads, "earnings": r.earnings, "created_at": r.created_at,
            "file_size": r.file_size, "mime_type": r.mime_type,
        }
        for r in rows
    ]}


@app.get("/api/openbox/items/{item_id}")
def ob_detail(item_id: str, db: Session = Depends(get_db)):
    item = db.get(OpenBoxItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return {
        "id": item.id, "title": item.title, "kind": item.kind,
        "category": item.category, "description": item.description,
        "uploader": item.uploader, "price_byflints": item.price_byflints,
        "gsp_col": item.gsp_col, "gsp_row": item.gsp_row,
        "downloads": item.downloads, "earnings": item.earnings,
        "file_size": item.file_size, "created_at": item.created_at,
    }


@app.post("/api/openbox/items/{item_id}/download")
def ob_download(item_id: str, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    item = db.get(OpenBoxItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    if item.uploader == user.phone:
        return {"ok": True, "message": "own_item_free",
                "download_url": f"/api/openbox/file/{item_id}"}
    if user.byflints < DOWNLOAD_FEE:
        raise HTTPException(402, f"Need {DOWNLOAD_FEE} byflints. Have {user.byflints}")

    ledger_add(db, user.phone, -DOWNLOAD_FEE, f"download:{item.title}", item_id)
    ledger_add(db, item.uploader, UPLOADER_SHARE, f"earn_from:{item.title}", item_id)
    item.downloads = (item.downloads or 0) + 1
    item.earnings = (item.earnings or 0.0) + UPLOADER_SHARE
    db.commit()

    return {
        "ok": True,
        "balance": balance(db, user.phone),
        "download_url": f"/api/openbox/file/{item_id}",
    }


@app.get("/api/openbox/file/{item_id}")
def ob_file(item_id: str, request: Request, db: Session = Depends(get_db)):
    require_user(request, db)
    item = db.get(OpenBoxItem, item_id)
    if not item or not item.filename:
        raise HTTPException(404, "File missing")
    path = UPLOAD_DIR / item.filename
    if not path.exists():
        raise HTTPException(404, "File missing on disk")
    return FileResponse(path, media_type=item.mime_type or "application/octet-stream", filename=item.title)


# ═══════════════════════════════════════════════════════
#  FANTASY
# ═══════════════════════════════════════════════════════
@app.get("/api/fantasy/tournaments")
def tournaments(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = db.query(Club.tournament_id, func.count(Club.id)).group_by(Club.tournament_id).all()
    return {"tournaments": [{"tournament_id": tid, "club_count": cnt} for tid, cnt in rows]}


@app.get("/api/fantasy/tournaments/{tid}")
def tournament_detail(tid: str, db: Session = Depends(get_db)):
    clubs = db.query(Club).filter_by(tournament_id=tid).order_by(Club.col).all()
    return {
        "tournament_id": tid,
        "base_price": TOURNAMENT_BASE.get(tid, 400),
        "clubs": [
            {"id": c.id, "name": c.name, "country": c.country, "col": c.col}
            for c in clubs
        ],
    }


@app.get("/api/fantasy/clubs/{club_id}/players")
def club_players(club_id: str, db: Session = Depends(get_db)):
    rows = db.query(Player).filter_by(club_id=club_id).all()
    week = current_gameweek()
    tid = club_id.split(":")[0]
    out = []
    for p in rows:
        out.append({
            "id": p.id, "name": p.name, "position": p.position,
            "number": p.number, "nationality": p.nationality,
            "market_value": p.market_value,
            "points_this_week": player_points(p.id, week),
            "price": player_price(tid, p.id, p.position or ""),
        })
    return {"club_id": club_id, "week": week, "players": out}


@app.get("/api/fantasy/transfers")
def transfers(days: int = 30, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    rows = db.query(Transfer).filter(Transfer.date >= cutoff)\
        .order_by(Transfer.date.desc()).limit(200).all()
    return {"transfers": [
        {
            "player_name": r.player_name, "from_club": r.from_club,
            "to_club": r.to_club, "fee": r.fee, "transfer_type": r.transfer_type,
            "date": r.date, "source": r.source,
        }
        for r in rows
    ]}


@app.get("/api/fantasy/hot")
def hot_players(db: Session = Depends(get_db)):
    week = current_gameweek()
    tids = [row[0] for row in db.query(Club.tournament_id).distinct().all()]
    out = []
    for tid in tids:
        players = db.query(Player).filter_by(tournament_id=tid).limit(500).all()
        if not players:
            continue
        scored = [(p, player_points(p.id, week)) for p in players]
        top_p, top_pts = max(scored, key=lambda x: x[1])
        out.append({
            "tournament_id": tid,
            "player": {
                "id": top_p.id, "name": top_p.name,
                "position": top_p.position, "club_id": top_p.club_id,
            },
            "points": top_pts,
            "price": player_price(tid, top_p.id, top_p.position or ""),
        })
    return {"week": week, "hot": out}


@app.post("/api/fantasy/sync-club")
def sync_single_club(request: Request, tid: str = "", cid: str = "",
                     db: Session = Depends(get_db)):
    """Sync one club's squad from Bzzoiro on demand."""
    if not tid or not cid:
        raise HTTPException(400, "tid and cid required")

    registry_key = f"{tid}:{cid}"

    # Already has players? Done.
    existing = db.query(Player).filter_by(club_id=registry_key).count()
    if existing > 0:
        return {"ok": True, "cached": True, "players": existing, "message": "Already populated."}

    # Look up which Bzzoiro club matches this registry entry
    from registry_map import REGISTRY, match_club
    t = REGISTRY.get(tid)
    if not t:
        return {"ok": False, "error": f"Tournament '{tid}' not in registry"}

    # Find bzz_* club whose name maps to this registry club
    bzz_clubs = db.query(Club).filter(Club.id.like("bzz_%")).all()
    target_id = None
    target_name = None
    target_country = ""
    for c in bzz_clubs:
        if match_club(tid, c.name) == cid:
            target_id = c.id
            target_name = c.name
            target_country = c.country or ""
            break

    if not target_id:
        return {
            "ok": False,
            "error": "Club not yet in Bzzoiro DB. Run Sync All from /admin.html first."
        }

    team_id = target_id.split(":")[-1]

    # Fetch squad from Bzzoiro
    h = _bzz_headers()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set on Render"}

    try:
        with httpx.Client(timeout=30, headers=h) as c:
            r = c.get(f"{BZZ_BASE}/teams/{team_id}/squad/")
            if r.status_code != 200:
                return {"ok": False, "error": f"Bzzoiro HTTP {r.status_code}"}
            payload = r.json()
    except Exception as e:
        return {"ok": False, "error": f"Bzzoiro fetch failed: {e}"}

    # Extract squad list
    squad = payload if isinstance(payload, list) else (
        payload.get("results") if isinstance(payload, dict) else []
    ) or []

    # Write to DB
    from storage import upsert_club, upsert_player

    def _pos(code):
        ch = (code or "").upper()[:1]
        return {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}.get(ch, "MID")

    try:
        upsert_club(db, {
            "id": registry_key,
            "tournament_id": tid,
            "name": target_name,
            "country": target_country,
            "col": 0,
        })
        count = 0
        for p in squad:
            if not isinstance(p, dict):
                continue
            pid = p.get("id")
            if not pid:
                continue
            upsert_player(db, {
                "id": f"{registry_key}:{pid}",
                "name": p.get("name") or "",
                "position": _pos(p.get("position")),
                "club_id": registry_key,
                "tournament_id": tid,
                "number": p.get("shirt_number"),
                "nationality": p.get("nationality") or p.get("nationality_code"),
                "market_value": p.get("market_value"),
                "photo_url": p.get("image_url"),
            })
            count += 1
        db.commit()
        return {"ok": True, "players": count, "registry_key": registry_key}
    except Exception as e:
        db.rollback()
        return {"ok": False, "error": f"DB write failed: {e}"}


# ═══════════════════════════════════════════════════════
#  NEWS — GNews proxy
# ═══════════════════════════════════════════════════════
_news_cache = {"at": 0, "items": []}


@app.get("/api/news")
def get_news(category: str = "sports", limit: int = 25):
    if not GNEWS_KEY:
        return {"news": [], "note": "GNEWS_KEY not set on server."}

    now = time.time()
    if now - _news_cache["at"] < 900 and _news_cache["items"]:
        return {"news": _news_cache["items"][:limit]}

    try:
        with httpx.Client(timeout=15) as c:
            r = c.get("https://gnews.io/api/v4/top-headlines", params={
                "category": category, "lang": "en", "max": 25, "apikey": GNEWS_KEY,
            })
            data = r.json()
            if "errors" in data or "error" in data:
                return {"news": [], "error": str(data.get("errors") or data.get("error"))}
            items = []
            for a in data.get("articles", []):
                items.append({
                    "title": a.get("title"),
                    "description": a.get("description"),
                    "url": a.get("url"),
                    "image": a.get("image"),
                    "source": (a.get("source") or {}).get("name"),
                    "published_at": a.get("publishedAt"),
                })
            _news_cache["items"] = items
            _news_cache["at"] = now
            return {"news": items[:limit]}
    except Exception as e:
        return {"news": [], "error": str(e)}


# ═══════════════════════════════════════════════════════
#  TRANSFERS LIVE — GNews multi-region
# ═══════════════════════════════════════════════════════
_transfers_cache = {}

_TRANSFER_QUERIES = {
    "europe":  "football transfer Premier League OR La Liga OR Serie A OR Bundesliga OR Ligue 1",
    "africa":  "football transfer NPFL OR CAF OR Egypt OR Morocco OR South Africa",
    "americas":"football transfer MLS OR Liga MX OR Brasileirao OR Argentine OR Libertadores",
    "asia":    "football transfer Saudi Pro League OR J-League OR AFC Champions League",
    "world":   "football transfer signing OR loan OR fee agreed",
}


@app.get("/api/transfers/live")
def transfers_live(region: str = "world", limit: int = 30):
    if not GNEWS_KEY:
        return _fallback_transfers(region, limit, note="GNEWS_KEY not set.")

    now = time.time()
    entry = _transfers_cache.get(region)
    if entry and now - entry["at"] < 900 and entry["items"]:
        return {"region": region, "source": "gnews-cache", "transfers": entry["items"][:limit]}

    query = _TRANSFER_QUERIES.get(region, _TRANSFER_QUERIES["world"])

    try:
        with httpx.Client(timeout=20) as c:
            r = c.get("https://gnews.io/api/v4/search", params={
                "q": query, "lang": "en", "max": 30,
                "sortby": "publishedAt", "apikey": GNEWS_KEY,
            })
            data = r.json()
    except Exception as e:
        return _fallback_transfers(region, limit, note=f"GNews error: {e}")

    if "errors" in data or "error" in data:
        return _fallback_transfers(region, limit,
            note=str(data.get("errors") or data.get("error")))

    items = []
    for a in data.get("articles", []):
        title = a.get("title") or ""
        player, from_club, to_club, fee = _parse_transfer(title)
        items.append({
            "player_name": player or title[:80],
            "from_club": from_club, "to_club": to_club, "fee": fee,
            "transfer_type": "news",
            "date": (a.get("publishedAt") or "")[:10],
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"), "image": a.get("image"),
            "title": title, "description": a.get("description") or "",
            "published_at": a.get("publishedAt"),
        })

    _transfers_cache[region] = {"at": now, "items": items}
    return {"region": region, "source": "gnews", "transfers": items[:limit]}


def _fallback_transfers(region: str, limit: int, note: str = ""):
    db = SessionLocal()
    try:
        rows = db.query(Transfer).order_by(Transfer.date.desc()).limit(limit).all()
        return {"region": region, "source": "db", "note": note, "transfers": [
            {"player_name": r.player_name, "from_club": r.from_club,
             "to_club": r.to_club, "fee": r.fee, "transfer_type": r.transfer_type,
             "date": r.date, "source": r.source, "url": r.source_url}
            for r in rows
        ]}
    finally:
        db.close()


def _parse_transfer(title: str):
    import re
    player = from_club = to_club = fee = None
    m = re.search(r"[£€$]\s?\d+(?:\.\d+)?\s?(?:m|million|k)", title, re.IGNORECASE)
    if m:
        fee = m.group(0)
    m = re.search(r"^([A-Z][\w\s\.\-]+?)\s+(?:sign|signs|complete|completed|agree|agrees|seal|seals)\s+(.+)", title)
    if m:
        to_club = m.group(1).strip()
    m = re.search(r"^([A-Z][\w\s\.\-]+?)\s+(?:join|joins)\s+([A-Z][\w\s\.\-]+)", title)
    if m:
        player = m.group(1).strip()
        to_club = to_club or m.group(2).strip()
    return player, from_club, to_club, fee


# ═══════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════
@app.get("/api/health")
def health():
    return {"ok": True, "gameweek": current_gameweek()}


# ═══════════════════════════════════════════════════════
#  ADMIN — Environment diagnostic
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/scraper-diag")
def admin_scraper_diag(request: Request):
    _admin_guard(request)
    report = {"env": {}, "imports": {}}
    report["env"]["DATABASE_URL_set"] = bool(os.environ.get("DATABASE_URL"))
    report["env"]["GNEWS_KEY_set"] = bool(GNEWS_KEY)
    report["env"]["BZZOIRO_TOKEN_set"] = bool(os.environ.get("BZZOIRO_TOKEN"))
    report["env"]["SCRAPER_TOKEN_set"] = bool(os.environ.get("SCRAPER_TOKEN"))
    try:
        from database import engine
        report["imports"]["database"] = "ok"
        report["db_host"] = str(engine.url).split("@")[-1] if "@" in str(engine.url) else "?"
    except Exception as e:
        report["imports"]["database"] = f"FAIL: {e}"
    for name in ("models", "tm_import", "bzz_sync"):
        try:
            __import__(name)
            report["imports"][name] = "ok"
        except Exception as e:
            report["imports"][name] = f"FAIL: {e}"
    try:
        import httpx, csv
        report["imports"]["deps"] = "ok"
    except Exception as e:
        report["imports"]["deps"] = f"FAIL: {e}"
    return report


# ═══════════════════════════════════════════════════════
#  ADMIN — Bzzoiro
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/bzz-test")
def bzz_test(request: Request):
    _admin_guard(request)
    h = _bzz_headers()
    if not h:
        return {"error": "BZZOIRO_TOKEN not set"}
    try:
        with httpx.Client(timeout=15) as c:
            r = c.get(f"{BZZ_BASE}/leagues/", headers=h)
        return {"status": r.status_code, "body": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/admin/bzz-leagues")
def bzz_leagues(request: Request):
    _admin_guard(request)
    h = _bzz_headers()
    if not h:
        return {"error": "BZZOIRO_TOKEN not set"}
    results = []
    url = f"{BZZ_BASE}/leagues/"
    try:
        with httpx.Client(timeout=20) as c:
            while url and len(results) < 300:
                r = c.get(url, headers=h)
                if r.status_code != 200:
                    break
                data = r.json()
                results.extend(data.get("results") or [])
                url = data.get("next")
        return {"count": len(results), "leagues": [
            {"id": l.get("id"), "name": l.get("name"), "country": l.get("country")}
            for l in results
        ]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/admin/bzz-sync")
def bzz_sync_ep(request: Request):
    _admin_guard(request)
    lid = request.query_params.get("league_id", "")
    if not lid:
        raise HTTPException(400, "league_id required")
    try:
        from bzz_sync import sync_league
        return sync_league(int(lid))
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}


@app.get("/api/admin/bzz-league-info")
def bzz_league_info(request: Request):
    _admin_guard(request)
    lid = request.query_params.get("league_id", "")
    if not lid:
        raise HTTPException(400, "league_id required")
    h = _bzz_headers()
    if not h:
        return {"error": "BZZOIRO_TOKEN not set"}
    from registry_map import match_tournament
    try:
        with httpx.Client(timeout=15, headers=h) as c:
            r = c.get(f"{BZZ_BASE}/leagues/{lid}/")
        if r.status_code != 200:
            return {"status": r.status_code, "error": r.text[:200]}
        lg = r.json()
        name = lg.get("name") or ""
        return {
            "id": lg.get("id"), "name": name,
            "country": lg.get("country"),
            "current_season": (lg.get("current_season") or {}).get("name"),
            "registry_match": match_tournament(name),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/admin/bzz-sync-all")
def bzz_sync_all(request: Request):
    _admin_guard(request)
    import traceback
    try:
        # Step 1 — verify SyncState is registered on Base
        from database import engine, Base
        import models
        from sqlalchemy import inspect
        insp = inspect(engine)
        tables = sorted(insp.get_table_names())
        if "sync_state" not in tables:
            # Try to create it now
            Base.metadata.create_all(bind=engine)
            insp = inspect(engine)
            tables = sorted(insp.get_table_names())

        # Step 2 — verify the class is usable
        from bzz_sync import start_sync_all, _load_state
        from database import SessionLocal
        db = SessionLocal()
        try:
            s = _load_state(db)
            state_ok = True
            state_id = s.id
        finally:
            db.close()

        # Step 3 — start the background thread
        result = start_sync_all()

        return {
            "ok": True,
            "tables": tables,
            "sync_state_ok": state_ok,
            "sync_state_id": state_id,
            "start_result": result,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


@app.get("/api/admin/bzz-progress")
def bzz_progress(request: Request):
    _admin_guard(request)
    from bzz_sync import get_state
    return get_state()


@app.get("/api/admin/bzz-stop")
def bzz_stop(request: Request):
    _admin_guard(request)
    from bzz_sync import stop_sync
    return stop_sync()


# ═══════════════════════════════════════════════════════
#  ADMIN — Transfermarkt CSV
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/tm-check")
def tm_check(request: Request):
    _admin_guard(request)
    urls = [
        "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/team_details/team_details.csv",
        "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/player_profiles/player_profiles.csv",
    ]
    out = []
    try:
        with httpx.Client(timeout=60, follow_redirects=True) as c:
            for u in urls:
                r = c.head(u)
                size = int(r.headers.get("content-length") or 0)
                out.append({
                    "file": u.split("/")[-1],
                    "status": r.status_code,
                    "size_mb": round(size / 1024 / 1024, 2),
                })
        return {"sources": out, "all_ok": all(x["status"] == 200 for x in out)}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/admin/tm-import")
def tm_import_ep(request: Request):
    _admin_guard(request)
    try:
        from tm_import import import_all
        return import_all()
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}


@app.get("/api/admin/tm-inspect")
def tm_inspect(request: Request):
    _admin_guard(request)
    out = {}
    try:
        with httpx.Client(timeout=60, follow_redirects=True) as c:
            for label, url in [
                ("teams", "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/team_details/team_details.csv"),
                ("players", "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/player_profiles/player_profiles.csv"),
            ]:
                r = c.get(url, headers={"Range": "bytes=0-2000"})
                out[label] = {
                    "status": r.status_code,
                    "content_length": r.headers.get("content-length"),
                    "lines": (r.text or "").split("\n")[:4],
                }
        return out
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════
#  ADMIN — DB inspection
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/db-counts")
def db_counts(request: Request):
    _admin_guard(request)
    from collections import Counter
    db = SessionLocal()
    try:
        clubs = db.query(Club).all()
        players = db.query(Player).all()
        transfers = db.query(Transfer).count()
        return {
            "clubs_total": len(clubs),
            "players_total": len(players),
            "transfers_total": transfers,
            "clubs_by_tournament": dict(Counter(c.tournament_id for c in clubs)),
            "players_by_tournament": dict(Counter(p.tournament_id for p in players)),
        }
    finally:
        db.close()

@app.get("/api/admin/db-create-tables")
def db_create_tables(request: Request):
    _admin_guard(request)
    import models
    from database import engine, Base
    from sqlalchemy import inspect
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    return {"tables": sorted(insp.get_table_names())}


@app.get("/api/admin/db-logs")
def db_logs(request: Request):
    _admin_guard(request)
    db = SessionLocal()
    try:
        rows = db.query(SyncLog).order_by(SyncLog.ran_at.desc()).limit(30).all()
        return {"logs": [
            {"task": r.task, "status": r.status, "count": r.count,
             "message": r.message, "ran_at": r.ran_at}
            for r in rows
        ]}
    finally:
        db.close()


@app.post("/api/admin/db-wipe-players")
def db_wipe_players(request: Request):
    _admin_guard(request)
    db = SessionLocal()
    try:
        n = db.query(Player).delete()
        db.commit()
        return {"ok": True, "deleted": n}
    finally:
        db.close()


@app.post("/api/admin/db-wipe-all")
def db_wipe_all(request: Request):
    _admin_guard(request)
    db = SessionLocal()
    try:
        p = db.query(Player).delete()
        c = db.query(Club).delete()
        t = db.query(Transfer).delete()
        db.commit()
        return {"ok": True, "players": p, "clubs": c, "transfers": t}
    finally:
        db.close()


@app.post("/api/admin/db-wipe-transfers")
def db_wipe_transfers(request: Request):
    _admin_guard(request)
    db = SessionLocal()
    try:
        n = db.query(Transfer).delete()
        db.commit()
        return {"ok": True, "deleted": n}
    finally:
        db.close()


@app.post("/api/admin/db-clean")
def db_clean(request: Request):
    """
    Delete any tm:* or bzz_* row that didn't map into a registry tournament.
    Preserves rows whose tournament_id matches a registry key.
    """
    _admin_guard(request)
    from sqlalchemy import text
    db = SessionLocal()
    try:
        p = db.execute(text(
            "DELETE FROM players WHERE tournament_id LIKE 'tm%' OR tournament_id LIKE 'bzz\\_%' ESCAPE '\\'"
        )).rowcount
        c = db.execute(text(
            "DELETE FROM clubs WHERE tournament_id LIKE 'tm%' OR tournament_id LIKE 'bzz\\_%' ESCAPE '\\'"
        )).rowcount
        db.commit()
        return {"ok": True, "players_deleted": p, "clubs_deleted": c}
    finally:
        db.close()


# ============================================================
#  BUBBLEJUMBO SECURITY TEST PAGE
#  Served directly by FastAPI - no static folder needed
# ============================================================
from fastapi.responses import HTMLResponse

@app.get("/bj-test", response_class=HTMLResponse)
def bj_test_page():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BubbleJumbo Security Test</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:monospace;background:#0a0a0f;color:#e8e8f0;padding:16px;font-size:13px;line-height:1.5}
h1{font-size:1rem;color:#00d2ff;margin-bottom:8px}
h3{font-size:0.8rem;color:#b8aaff;margin:20px 0 8px;text-transform:uppercase;letter-spacing:.08em}
button{padding:10px 18px;border-radius:6px;border:none;background:#6c5ce7;color:#fff;font-weight:700;font-size:13px;cursor:pointer;margin:4px 4px 4px 0;font-family:inherit}
button:hover{background:#8b7cf7}
pre{background:#12121a;border:1px solid #2a2a3d;border-radius:6px;padding:10px;font-size:11px;max-height:500px;overflow:auto;white-space:pre-wrap;word-break:break-word;color:#00ff88}
pre.err{color:#ff6b6b}
.note{background:#12121a;border-left:3px solid #ffd700;padding:8px 10px;font-size:.75rem;color:#aaa;margin:8px 0;border-radius:4px}
.stat{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0;font-size:.75rem}
.stat .pill{padding:3px 10px;border-radius:12px;background:#1a1a26}
.stat .pass{background:rgba(0,255,136,.15);color:#00ff88}
.stat .trap{background:rgba(255,107,107,.15);color:#ff6b6b}
.stat .blocked{background:rgba(255,215,0,.15);color:#ffd700}
</style>
</head>
<body>
<h1>BubbleJumbo Security Test</h1>
<div class="note">Runs against this domain. Every request goes through BubbleJumbo middleware. Watch for TRAP after attack phases.</div>
<h3>Run</h3>
<button onclick="runAll()">Run Full Test</button>
<button onclick="runPhase('recon')">Recon</button>
<button onclick="runPhase('brute')">Brute</button>
<button onclick="runPhase('inject')">Inject</button>
<button onclick="runPhase('flood')">Flood</button>
<button onclick="runPhase('ua')">Bad UA</button>
<button onclick="runPhase('phish')">Phishing</button>
<button onclick="clearLog()">Clear</button>
<div class="stat">
<span class="pill">pass: <span id="s-pass">0</span></span>
<span class="pill trap">trap: <span id="s-trap">0</span></span>
<span class="pill blocked">blocked: <span id="s-blocked">0</span></span>
<span class="pill">errors: <span id="s-err">0</span></span>
</div>
<h3>Output</h3>
<pre id="log">Ready. Tap Run Full Test.</pre>
<script>
(function(){
var stats={pass:0,trap:0,blocked:0,err:0};
function target(){return window.location.origin}
function log(m,e){var el=document.getElementById('log');el.textContent+="\\n"+m;el.scrollTop=el.scrollHeight;if(e)el.className='err'}
function clearLog(){document.getElementById('log').textContent='Ready.';stats={pass:0,trap:0,blocked:0,err:0};renderStats()}
function renderStats(){document.getElementById('s-pass').textContent=stats.pass;document.getElementById('s-trap').textContent=stats.trap;document.getElementById('s-blocked').textContent=stats.blocked;document.getElementById('s-err').textContent=stats.err}
function sleep(ms){return new Promise(function(r){setTimeout(r,ms)})}
async function probe(label,method,path,opts){
opts=opts||{};var started=Date.now();var res,text;
try{
var init={method:method,redirect:'follow',credentials:'include',headers:opts.headers||{}};
if(opts.json){init.headers['Content-Type']='application/json';init.body=JSON.stringify(opts.json)}
res=await fetch(target()+path,init);text=await res.text();
}catch(e){stats.err++;renderStats();log('['+label+'] NETWORK ERROR: '+e.message,true);return}
var elapsed=Date.now()-started;
var trap=text.indexOf('Verification Required')!==-1||text.indexOf('7x7')!==-1;
var verdict=trap?'TRAP':([401,403,429].indexOf(res.status)!==-1?'BLOCKED':'PASS');
var notice=res.headers.get('x-bj-notice')||'';
if(verdict==='TRAP')stats.trap++;else if(verdict==='BLOCKED')stats.blocked++;else stats.pass++;
renderStats();
log('['+label+'] status='+res.status+' time='+elapsed+'ms verdict='+verdict+(notice?' notice='+notice:''));
if(verdict!=='PASS')log('   body: '+text.slice(0,150).replace(/\\s+/g,' '));
}
async function phaseRecon(){log('\\n---- Recon ----');var p=['/admin','/.env','/config.py','/wp-admin','/api/admin/db-counts'];for(var i=0;i<p.length;i++){await probe(p[i],'GET',p[i]);await sleep(150)}}
async function phaseBrute(){log('\\n---- Brute login ----');for(var i=0;i<15;i++){await probe('login#'+(i+1),'POST','/api/auth/login',{json:{phone:'2348000000000',password:'guess'+i}});await sleep(150)}}
async function phaseInject(){log('\\n---- Inject ----');await probe('sqli','GET',"/api/fantasy/clubs/epl:ars' UNION SELECT * FROM users--/players");await probe('trav','GET','/api/openbox/file/../../etc/passwd');await probe('xss','GET','/api/fantasy/tournaments?q=<script>alert(1)</script>')}
async function phaseFlood(){log('\\n---- Flood 30 ----');for(var i=0;i<30;i++){try{var r=await fetch(target()+'/api/health');if(r.status===429){log('   rate-limited at #'+(i+1));return}}catch(e){log('   err #'+(i+1)+': '+e.message,true);return}}log('   completed 30 with no rate-limit')}
async function phaseUA(){log('\\n---- Bad UA ----');var a=['sqlmap/1.7','Nikto','Nmap NSE','curl/8.4',''];for(var i=0;i<a.length;i++){await probe('ua='+(a[i]||'empty'),'GET','/api/health',{headers:{'User-Agent':a[i]}});await sleep(150)}}
async function phasePhish(){log('\\n---- Phishing ----');await probe('bj_flag','GET','/?bj_phishing=1');await probe('referer','GET','/',{headers:{'Referer':'https://evil.example.com/login'}});await probe('both','GET','/?bj_phishing=1',{headers:{'Referer':'https://phish.example.com/steal'}})}
async function runPhase(n){clearLog();if(n==='recon')await phaseRecon();if(n==='brute')await phaseBrute();if(n==='inject')await phaseInject();if(n==='flood')await phaseFlood();if(n==='ua')await phaseUA();if(n==='phish')await phasePhish()}
async function runAll(){clearLog();log('Target: '+target());await probe('baseline-home','GET','/');await probe('baseline-health','GET','/api/health');await phaseRecon();await phaseBrute();await phaseInject();await phaseFlood();await phaseUA();await phasePhish();log('\\n==== DONE ====');log('Summary: pass='+stats.pass+' trap='+stats.trap+' blocked='+stats.blocked+' errors='+stats.err)}
window.runAll=runAll;window.runPhase=runPhase;window.clearLog=clearLog;
})();
</script>
</body>
</html>"""
    return HTMLResponse(content=html)

# ═══════════════════════════════════════════════════════
#  STATIC — must be last
# ═══════════════════════════════════════════════════════
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")