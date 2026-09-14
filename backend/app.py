"""
GSP OpenBox + Fantasy — combined backend.
- Auth: SQLite users, 1070 byflints at signup
- Wallet: ledger-backed balance
- OpenBox items: 4-column grid (row always 1)
- Fantasy: tournaments, players, transfers, hot list
- BubbleJumbo middleware wraps everything
"""
import os, time, uuid, json, sqlite3, math, hashlib
from pathlib import Path
from typing import List, Optional, Dict
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bubblejumbo_middleware import BubbleJumboMiddleware, bj_bridge

DB_PATH = Path(__file__).resolve().parent / "storage" / "transfers.db"
UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════
WELCOME_BYFLINTS = 1070

# Minimum byflints per player, per tournament tier
TOURNAMENT_BASE = {
    "npfl": 190, "egypt_pl": 183, "sa_psl": 190, "botola": 170,
    "cafcl": 450, "cafcc": 450,
    "brasileirao_b": 380, "brasileirao_a": 390, "argentina_primera": 350,
    "mls": 400, "ligamx": 200, "j1": 400, "saudi_pl": 450,
    "eredivisie": 400, "portugal": 450, "turkey": 400,
    "epl": 300, "laliga": 240, "seriea": 290, "bundes": 550, "ligue1": 300,
    "ucl": 800, "uel": 700, "uecl": 600,
    "libertadores": 500, "sudamericana": 450,
    "concacaf_cl": 450, "afc_cl": 500,
    "worldcup": 1000, "afcon": 800, "euro": 900, "copa_america": 800,
}

POSITION_BONUS = {"GK": 23, "DEF": 30, "MID": 40, "FWD": 60,
                  "Goalkeeper": 23, "Defender": 30, "Midfielder": 40, "Attacker": 60}

# OpenBox 4-column grid: category → column index
CATEGORY_COL = {"app": 0, "game": 1, "video": 2, "other": 3}

UPLOAD_FEE = {"app": 150_000, "game": 2_000_000, "video": 100_000, "other": 0}
DOWNLOAD_FEE = 3_000
UPLOADER_SHARE = 2.5
PLATFORM_SHARE = 0.5

# ═══════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════
def init_app_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            dob TEXT,
            talent TEXT,
            country TEXT,
            byflints REAL DEFAULT 0,
            created_at REAL
        );

        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT,
            ref TEXT,
            created_at REAL,
            FOREIGN KEY(phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            phone TEXT NOT NULL,
            created_at REAL,
            FOREIGN KEY(phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS openbox_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            kind TEXT,
            category TEXT,
            description TEXT,
            uploader TEXT,
            price_byflints REAL DEFAULT 0,
            fee_paid REAL DEFAULT 0,
            filename TEXT,
            file_size INTEGER,
            mime_type TEXT,
            gsp_col INTEGER,
            gsp_row INTEGER,
            downloads INTEGER DEFAULT 0,
            earnings REAL DEFAULT 0,
            created_at REAL,
            FOREIGN KEY(uploader) REFERENCES users(phone)
        );

        CREATE INDEX IF NOT EXISTS idx_items_cat ON openbox_items(category);
        CREATE INDEX IF NOT EXISTS idx_items_uploader ON openbox_items(uploader);
        CREATE INDEX IF NOT EXISTS idx_ledger_phone ON ledger(phone);
    """)
    conn.commit()
    return conn


init_app_db()


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


def current_gameweek() -> int:
    epoch = time.mktime(time.strptime("2024-08-01", "%Y-%m-%d"))
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


def get_user_from_token(token: str) -> Optional[dict]:
    if not token:
        return None
    conn = db()
    row = conn.execute("""
        SELECT u.* FROM sessions s JOIN users u ON s.phone = u.phone
        WHERE s.token = ?
    """, (token,)).fetchone()
    return dict(row) if row else None


def require_user(request: Request) -> dict:
    token = request.cookies.get("openbox_token")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Not authenticated")
    return user


def ledger_add(conn, phone: str, amount: float, reason: str, ref: str = ""):
    conn.execute("""
        INSERT INTO ledger (phone, amount, reason, ref, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (phone, amount, reason, ref, time.time()))
    conn.execute("UPDATE users SET byflints = byflints + ? WHERE phone = ?",
                 (amount, phone))
    conn.commit()


def balance(conn, phone: str) -> float:
    row = conn.execute("SELECT byflints FROM users WHERE phone = ?", (phone,)).fetchone()
    return float(row["byflints"]) if row else 0.0


# ═══════════════════════════════════════════════════════
#  FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(title="GSP OpenBox")
app.add_middleware(BubbleJumboMiddleware)
app.include_router(bj_bridge)


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
async def signup(req: SignupReq):
    conn = db()
    existing = conn.execute("SELECT 1 FROM users WHERE phone = ?", (req.phone,)).fetchone()
    if existing:
        raise HTTPException(400, "Phone already registered")

    conn.execute("""
        INSERT INTO users (phone, full_name, email, password_hash, dob, talent, country, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (req.phone, req.full_name, req.email, hash_password(req.password),
          req.dob, req.talent, req.country, time.time()))
    conn.commit()

    # Grant welcome byflints
    ledger_add(conn, req.phone, WELCOME_BYFLINTS, "welcome_bonus", "signup")

    token = uuid.uuid4().hex
    conn.execute("INSERT INTO sessions (token, phone, created_at) VALUES (?, ?, ?)",
                 (token, req.phone, time.time()))
    conn.commit()

    response = JSONResponse({
        "ok": True,
        "phone": req.phone,
        "full_name": req.full_name,
        "byflints": WELCOME_BYFLINTS,
    })
    response.set_cookie("openbox_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return response


@app.post("/api/auth/login")
async def login(req: LoginReq):
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE phone = ?", (req.phone,)).fetchone()
    if not row or row["password_hash"] != hash_password(req.password):
        raise HTTPException(401, "Invalid credentials")

    token = uuid.uuid4().hex
    conn.execute("INSERT INTO sessions (token, phone, created_at) VALUES (?, ?, ?)",
                 (token, req.phone, time.time()))
    conn.commit()

    response = JSONResponse({
        "ok": True,
        "phone": row["phone"],
        "full_name": row["full_name"],
        "byflints": row["byflints"],
    })
    response.set_cookie("openbox_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return response


@app.post("/api/auth/logout")
async def logout(request: Request):
    token = request.cookies.get("openbox_token")
    if token:
        conn = db()
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    response = JSONResponse({"ok": True})
    response.delete_cookie("openbox_token")
    return response


@app.get("/api/me")
async def me(request: Request):
    user = require_user(request)
    conn = db()
    return {
        "phone": user["phone"],
        "full_name": user["full_name"],
        "email": user["email"],
        "talent": user["talent"],
        "country": user["country"],
        "byflints": balance(conn, user["phone"]),
    }


# ═══════════════════════════════════════════════════════
#  WALLET
# ═══════════════════════════════════════════════════════
@app.get("/api/wallet")
async def wallet(request: Request):
    user = require_user(request)
    conn = db()
    rows = conn.execute("""
        SELECT amount, reason, ref, created_at FROM ledger
        WHERE phone = ? ORDER BY created_at DESC LIMIT 200
    """, (user["phone"],)).fetchall()
    return {
        "balance": balance(conn, user["phone"]),
        "ledger": [dict(r) for r in rows],
    }


# ═══════════════════════════════════════════════════════
#  OPENBOX ITEMS  (4-column grid, row always 1)
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
):
    user = require_user(request)
    conn = db()

    fee = UPLOAD_FEE.get(category, 5)
    if balance(conn, user["phone"]) < fee:
        raise HTTPException(402, f"Need {fee} byflints to upload. Have {balance(conn, user['phone'])}")

    item_id = "item-" + uuid.uuid4().hex[:12]
    ext = Path(file.filename).suffix
    stored_name = f"{item_id}{ext}"
    dest = UPLOAD_DIR / stored_name

    size = 0
    with dest.open("wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
            size += len(chunk)

    gsp_col = CATEGORY_COL.get(category, 3)
    gsp_row = 1

    conn.execute("""
        INSERT INTO openbox_items
        (id, title, kind, category, description, uploader, price_byflints,
         fee_paid, filename, file_size, mime_type, gsp_col, gsp_row, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item_id, title, kind, category, description, user["phone"],
          price_byflints, fee, stored_name, size, file.content_type,
          gsp_col, gsp_row, time.time()))
    conn.commit()

    ledger_add(conn, user["phone"], -fee, f"upload:{title}", item_id)

    return {"ok": True, "item_id": item_id, "balance": balance(conn, user["phone"])}


@app.get("/api/openbox/items")
async def ob_list(category: Optional[str] = None):
    conn = db()
    if category:
        rows = conn.execute("""
            SELECT id, title, kind, category, description, uploader,
                   price_byflints, gsp_col, gsp_row, downloads, earnings, created_at,
                   file_size, mime_type
            FROM openbox_items WHERE category = ? ORDER BY created_at DESC LIMIT 200
        """, (category,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, title, kind, category, description, uploader,
                   price_byflints, gsp_col, gsp_row, downloads, earnings, created_at,
                   file_size, mime_type
            FROM openbox_items ORDER BY created_at DESC LIMIT 200
        """).fetchall()
    return {"items": [dict(r) for r in rows]}


@app.get("/api/openbox/items/{item_id}")
async def ob_detail(item_id: str):
    conn = db()
    row = conn.execute("SELECT * FROM openbox_items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    d = dict(row)
    d.pop("filename", None)  # don't leak
    return d


@app.post("/api/openbox/items/{item_id}/download")
async def ob_download(item_id: str, request: Request):
    user = require_user(request)
    conn = db()
    row = conn.execute("SELECT * FROM openbox_items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")

    item = dict(row)
    if item["uploader"] == user["phone"]:
        return {"ok": True, "message": "own_item_free",
                "download_url": f"/api/openbox/file/{item_id}"}

    if balance(conn, user["phone"]) < DOWNLOAD_FEE:
        raise HTTPException(402, f"Need {DOWNLOAD_FEE} byflints. Have {balance(conn, user['phone'])}")

    ledger_add(conn, user["phone"], -DOWNLOAD_FEE, f"download:{item['title']}", item_id)
    ledger_add(conn, item["uploader"], UPLOADER_SHARE, f"earn_from:{item['title']}", item_id)
    conn.execute("""
        UPDATE openbox_items
        SET downloads = downloads + 1, earnings = earnings + ?
        WHERE id = ?
    """, (UPLOADER_SHARE, item_id))
    conn.commit()

    return {
        "ok": True,
        "balance": balance(conn, user["phone"]),
        "download_url": f"/api/openbox/file/{item_id}",
    }


@app.get("/api/openbox/file/{item_id}")
async def ob_file(item_id: str, request: Request):
    require_user(request)
    conn = db()
    row = conn.execute("SELECT filename, mime_type, title FROM openbox_items WHERE id = ?",
                       (item_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    path = UPLOAD_DIR / row["filename"]
    if not path.exists():
        raise HTTPException(404, "File missing")
    return FileResponse(path, media_type=row["mime_type"] or "application/octet-stream",
                        filename=row["title"])


# ═══════════════════════════════════════════════════════
#  FANTASY
# ═══════════════════════════════════════════════════════
@app.get("/api/fantasy/tournaments")
async def tournaments():
    conn = db()
    rows = conn.execute("""
        SELECT tournament_id, COUNT(*) as club_count
        FROM clubs GROUP BY tournament_id ORDER BY tournament_id
    """).fetchall()
    return {"tournaments": [dict(r) for r in rows]}


@app.get("/api/fantasy/tournaments/{tid}")
async def tournament_detail(tid: str):
    conn = db()
    clubs = conn.execute("""
        SELECT id, name, country, col FROM clubs
        WHERE tournament_id = ? ORDER BY col
    """, (tid,)).fetchall()
    return {
        "tournament_id": tid,
        "base_price": TOURNAMENT_BASE.get(tid, 400),
        "clubs": [dict(c) for c in clubs],
    }


@app.get("/api/fantasy/clubs/{club_id}/players")
async def club_players(club_id: str):
    conn = db()
    rows = conn.execute("""
        SELECT id, name, position, number, nationality, market_value
        FROM players WHERE club_id = ?
        ORDER BY
            CASE position
                WHEN 'Goalkeeper' THEN 1 WHEN 'GK' THEN 1
                WHEN 'Defender' THEN 2 WHEN 'DEF' THEN 2
                WHEN 'Midfielder' THEN 3 WHEN 'MID' THEN 3
                ELSE 4
            END,
            name
    """, (club_id,)).fetchall()
    week = current_gameweek()
    tid = club_id.split(":")[0]
    out = []
    for r in rows:
        d = dict(r)
        d["points_this_week"] = player_points(d["id"], week)
        d["price"] = player_price(tid, d["id"], d["position"] or "")
        out.append(d)
    return {"club_id": club_id, "week": week, "players": out}


@app.get("/api/fantasy/transfers")
async def transfers(days: int = 30):
    conn = db()
    rows = conn.execute("""
        SELECT player_name, from_club, to_club, fee, transfer_type, date, source
        FROM transfers WHERE date >= date('now', ?)
        ORDER BY date DESC LIMIT 200
    """, (f"-{days} days",)).fetchall()
    return {"transfers": [dict(r) for r in rows]}


@app.get("/api/fantasy/hot")
async def hot_players():
    conn = db()
    week = current_gameweek()
    tournaments = conn.execute("SELECT DISTINCT tournament_id FROM clubs").fetchall()
    out = []
    for t in tournaments:
        tid = t["tournament_id"]
        rows = conn.execute("""
            SELECT id, name, position, club_id FROM players
            WHERE tournament_id = ? LIMIT 500
        """, (tid,)).fetchall()
        if not rows:
            continue
        scored = [(dict(r), player_points(r["id"], week)) for r in rows]
        top = max(scored, key=lambda x: x[1])
        out.append({
            "tournament_id": tid,
            "player": top[0],
            "points": top[1],
            "price": player_price(tid, top[0]["id"], top[0]["position"] or ""),
        })
    return {"week": week, "hot": out}


# ═══════════════════════════════════════════════════════
#  HEALTH + STATIC
# ═══════════════════════════════════════════════════════
@app.get("/api/health")
async def health():
    return {"ok": True, "gameweek": current_gameweek()}


from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR    = BACKEND_DIR.parent
STATIC_DIR  = ROOT_DIR / "static"
STORAGE_DIR = BACKEND_DIR / "storage"
UPLOAD_DIR  = STORAGE_DIR / "uploads"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")