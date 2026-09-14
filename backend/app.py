"""
GSP OpenBox + Fantasy — combined backend.
- Auth: SQLite users, 1070 byflints at signup
- Wallet: ledger-backed balance
- OpenBox items: 4-column grid (row always 1)
- Fantasy: tournaments, players, transfers, hot list
- BubbleJumbo middleware wraps everything
"""
import os, time, uuid, hashlib
from pathlib import Path
import httpx, csv, io, time as _time
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import User, SessionToken, LedgerEntry, OpenBoxItem, Club, Player, Transfer, SyncLog
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
WELCOME_BYFLINTS = 1070

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

POSITION_BONUS = {"GK": 23.5, "DEF": 35, "MID": 40, "FWD": 60,
                  "Goalkeeper": 23.5, "Defender": 35, "Midfielder": 40, "Attacker": 60}

CATEGORY_COL = {"app": 0, "game": 1, "video": 2, "other": 3}

UPLOAD_FEE = {"app": 200000, "game": 200000, "video": 150000, "other": 0}
DOWNLOAD_FEE = 3000
UPLOADER_SHARE = 3000

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


def current_gameweek() -> int:
    epoch = time.mktime(time.strptime("2026-26-01", "%Y-%m-%d"))
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


# ═══════════════════════════════════════════════════════
#  FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(title="GSP OpenBox")
app.add_middleware(BubbleJumboMiddleware)
app.include_router(bj_bridge)


@app.on_event("startup")
def on_startup():
    init_db()


# ═══════════════════════════════════════════════════════
#  MODELS
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


# ═══════════════════════════════════════════════════════
#  WALLET
# ═══════════════════════════════════════════════════════
@app.get("/api/wallet")
def wallet(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    rows = db.query(LedgerEntry).filter_by(phone=user.phone).order_by(LedgerEntry.created_at.desc()).limit(200).all()
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
    return {"tournaments": [
        {"tournament_id": tid, "club_count": cnt} for tid, cnt in rows
    ]}


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
    rows = db.query(Transfer).filter(Transfer.date >= cutoff).order_by(Transfer.date.desc()).limit(200).all()
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


# ═══════════════════════════════════════════════════════
#  HEALTH + STATIC
# ═══════════════════════════════════════════════════════
@app.get("/api/health")
def health():
    return {"ok": True, "gameweek": current_gameweek()}

# ═══════════════════════════════════════════════════════
#  ADMIN — run the scraper on demand
# ═══════════════════════════════════════════════════════
SCRAPER_TOKEN = os.environ.get("SCRAPER_TOKEN", "CHANGE_ME")

@app.get("/api/admin/scraper-diag")
def admin_scraper_diag(request: Request):
    """Report what the scraper environment looks like. No side effects."""
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")

    report = {"env": {}, "imports": {}, "db": {}}

    # Env vars
    report["env"]["DATABASE_URL_set"] = bool(os.environ.get("DATABASE_URL"))
    report["env"]["SPORTMONKS_KEY_set"] = bool(os.environ.get("SPORTMONKS_KEY"))
    report["env"]["GNEWS_KEY_set"] = bool(os.environ.get("GNEWS_KEY"))
    report["env"]["SCRAPER_TOKEN_set"] = bool(os.environ.get("SCRAPER_TOKEN"))

    # Imports
    try:
        from database import engine
        report["imports"]["database"] = "ok"
        report["db"]["url_prefix"] = str(engine.url).split("@")[-1] if "@" in str(engine.url) else "?"
    except Exception as e:
        report["imports"]["database"] = f"FAIL: {e}"

    try:
        import models
        report["imports"]["models"] = "ok"
    except Exception as e:
        report["imports"]["models"] = f"FAIL: {e}"

    try:
        from run_sync import main as sync_main
        report["imports"]["run_sync"] = "ok"
    except Exception as e:
        report["imports"]["run_sync"] = f"FAIL: {e}"

    try:
        from config import SPORTMONKS_KEY, LEAGUES
        report["imports"]["config"] = "ok"
        report["env"]["leagues_count"] = len(LEAGUES)
    except Exception as e:
        report["imports"]["config"] = f"FAIL: {e}"

    try:
        import httpx, feedparser
        from bs4 import BeautifulSoup
        report["imports"]["deps"] = "ok"
    except Exception as e:
        report["imports"]["deps"] = f"FAIL: {e}"

    return report


@app.get("/api/admin/run-scraper")
def admin_run_scraper(request: Request):
    """Runs the scraper synchronously so errors come back in the HTTP response."""
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")

    import sys, asyncio
    from pathlib import Path

    # Make sure sibling modules are importable
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    out_lines = []

    def log(msg):
        out_lines.append(str(msg))
        print("[scraper]", msg, flush=True)

    try:
        log("importing run_sync...")
        from run_sync import main as sync_main

        log("starting sync (this may take minutes)...")
        # Fire the actual run
        asyncio.run(sync_main())
        log("sync completed")

        return {"ok": True, "output": out_lines}

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log("EXCEPTION: " + str(e))
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e), "traceback": tb, "output": out_lines}
        )

# ═══════════════════════════════════════════════════════
#  SPORTMONKS ADMIN — run scraper one league at a time
# ═══════════════════════════════════════════════════════
from config import LEAGUES as SP_LEAGUES

@app.get("/api/admin/sp-test")
def sp_test(request: Request):
    """Test SportMonks API with a single call. Returns raw response."""
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")
    from sp_diag import sp_raw_league
    return sp_raw_league(8)   # EPL as a known-good test


@app.get("/api/admin/sp-find")
def sp_find(request: Request, q: str = ""):
    """Search SportMonks leagues by name."""
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")
    from sp_diag import sp_find_league
    return sp_find_league(q or "premier")


@app.get("/api/admin/sp-sync")
def sp_sync(request: Request, league: str = "epl"):
    """Sync one league. Blocks until done. Returns stats."""
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403, "Forbidden")
    if league not in SP_LEAGUES:
        raise HTTPException(400, f"Unknown league '{league}'. Known: {list(SP_LEAGUES.keys())}")
    from sp_diag import sync_one_league
    import traceback
    try:
        return sync_one_league(league, SP_LEAGUES[league])
    except Exception as e:
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

# ═══════════════════════════════════════════════════════
#  MULTI-SOURCE SCRAPER ADMIN
# ═══════════════════════════════════════════════════════
# ─── TheSportsDB ───
TSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"

@app.get("/api/admin/tsdb-test")
def tsdb_test(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    with httpx.Client(timeout=15) as c:
        r = c.get(f"{TSDB_BASE}/all_leagues.php")
    try:
        data = r.json()
        return {"status": r.status_code, "leagues_count": len(data.get("leagues") or [])}
    except Exception:
        return {"status": r.status_code, "raw": r.text[:300]}

@app.get("/api/admin/tsdb-preview")
def tsdb_preview(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    league = request.query_params.get("league", "English Premier League")
    with httpx.Client(timeout=20) as c:
        r = c.get(f"{TSDB_BASE}/search_all_teams.php", params={"l": league})
    try:
        data = r.json()
        teams = data.get("teams") or []
        return {"status": r.status_code, "count": len(teams),
                "teams": [{"id": t.get("idTeam"), "name": t.get("strTeam"),
                           "stadium": t.get("strStadium")} for t in teams[:25]]}
    except Exception:
        return {"status": r.status_code, "raw": r.text[:300]}

@app.get("/api/admin/tsdb-sync")
def tsdb_sync(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    league = request.query_params.get("league", "English Premier League")
    from tsdb_sync import sync_league
    try:
        return sync_league(league)
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

# ─── Bzzoiro ───
BZZ_BASE = "https://sports.bzzoiro.com/api/v2"

def _bzz_headers():
    import os
    t = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {t}"} if t else {}

@app.get("/api/admin/bzz-test")
def bzz_test(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    h = _bzz_headers()
    if not h:
        return {"error": "BZZOIRO_TOKEN not set on Render. Register at sports.bzzoiro.com/register, then add env var."}
    with httpx.Client(timeout=15) as c:
        r = c.get(f"{BZZ_BASE}/leagues/", headers=h)
    try:
        return {"status": r.status_code, "body": r.json()}
    except Exception:
        return {"status": r.status_code, "raw": r.text[:300]}

@app.get("/api/admin/bzz-leagues")
def bzz_leagues(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    h = _bzz_headers()
    if not h: return {"error": "BZZOIRO_TOKEN not set"}
    results = []
    url = f"{BZZ_BASE}/leagues/"
    with httpx.Client(timeout=20) as c:
        while url and len(results) < 200:
            r = c.get(url, headers=h)
            if r.status_code != 200: break
            data = r.json()
            results.extend(data.get("results") or [])
            url = data.get("next")
    return {"count": len(results),
            "leagues": [{"id": l.get("id"), "name": l.get("name"),
                         "country": l.get("country")} for l in results]}

@app.get("/api/admin/bzz-sync")
def bzz_sync(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    lid = request.query_params.get("league_id", "")
    if not lid: raise HTTPException(400, "league_id required")
    from bzz_sync import sync_league
    try:
        return sync_league(int(lid))
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

# ─── Transfermarkt CSV ───
@app.get("/api/admin/tm-check")
def tm_check(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    url = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/raw/player_profiles/player_profiles.csv"
    with httpx.Client(timeout=20, follow_redirects=True) as c:
        r = c.head(url)
    return {"available": r.status_code == 200, "status": r.status_code,
            "size_bytes": r.headers.get("content-length"),
            "source": "github.com/salimt/football-datasets"}

@app.post("/api/admin/tm-import")
def tm_import(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    from tm_import import import_all
    try:
        return import_all()
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

# ─── DB helpers ───
@app.get("/api/admin/db-counts")
def db_counts(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    from collections import Counter
    db = SessionLocal()
    try:
        clubs = db.query(Club).all()
        players = db.query(Player).all()
        return {
            "clubs_total": len(clubs),
            "players_total": len(players),
            "clubs_by_tournament": dict(Counter(c.tournament_id for c in clubs)),
            "players_by_tournament": dict(Counter(p.tournament_id for p in players)),
        }
    finally:
        db.close()

@app.get("/api/admin/db-logs")
def db_logs(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    db = SessionLocal()
    try:
        rows = db.query(SyncLog).order_by(SyncLog.ran_at.desc()).limit(30).all()
        return {"logs": [{"task": r.task, "status": r.status, "count": r.count,
                          "message": r.message, "ran_at": r.ran_at} for r in rows]}
    finally:
        db.close()

@app.post("/api/admin/db-wipe-players")
def db_wipe_players(request: Request):
    if request.query_params.get("token", "") != SCRAPER_TOKEN:
        raise HTTPException(403)
    db = SessionLocal()
    try:
        n = db.query(Player).delete()
        db.commit()
        return {"ok": True, "deleted": n}
    finally:
        db.close()

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")