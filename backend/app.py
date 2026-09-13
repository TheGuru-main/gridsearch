"""
GSP OpenBox + Fantasy — combined backend.
OpenBox registration flow preserved.
Fantasy fed by scraper storage.
"""
import os
import time
import uuid
import json
import sqlite3
import math
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bubblejumbo_middleware import BubbleJumboMiddleware, bj_bridge

DB_PATH = Path("storage/transfers.db")

app = FastAPI(title="GSP OpenBox")
app.add_middleware(BubbleJumboMiddleware)
app.include_router(bj_bridge)


# ═══════════════════════════════════════════════════════
#  DB helpers
# ═══════════════════════════════════════════════════════
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def current_gameweek():
    epoch = time.mktime(time.strptime("2024-08-01", "%Y-%m-%d"))
    return int((time.time() - epoch) // (7 * 86400)) + 1


def player_points(player_id: str, week: int) -> float:
    """Deterministic until real match stats are wired."""
    seed = f"{player_id}:{week}"
    h = 0
    for c in seed:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return round((h % 120) / 10 + 1.0, 1)


def player_price(player_id: str, position: str, market_value: Optional[int]) -> int:
    base = {"Goalkeeper": 50, "Defender": 70, "Midfielder": 90, "Attacker": 110,
            "GK": 50, "DEF": 70, "MID": 90, "FWD": 110}.get(position, 60)
    if market_value:
        base += min(150, market_value // 1_000_000)
    h = sum(ord(c) for c in player_id) % 80
    return min(500, base + h)


# ═══════════════════════════════════════════════════════
#  FANTASY ENDPOINTS
# ═══════════════════════════════════════════════════════
@app.get("/api/fantasy/tournaments")
async def tournaments():
    conn = db()
    rows = conn.execute("""
        SELECT tournament_id, COUNT(*) as club_count
        FROM clubs
        GROUP BY tournament_id
        ORDER BY tournament_id
    """).fetchall()
    return {"tournaments": [dict(r) for r in rows]}


@app.get("/api/fantasy/tournaments/{tid}")
async def tournament_detail(tid: str):
    conn = db()
    clubs = conn.execute("""
        SELECT id, name, country, col
        FROM clubs WHERE tournament_id = ? ORDER BY col
    """, (tid,)).fetchall()
    return {"tournament_id": tid, "clubs": [dict(c) for c in clubs]}


@app.get("/api/fantasy/clubs/{club_id}/players")
async def club_players(club_id: str):
    conn = db()
    rows = conn.execute("""
        SELECT id, name, position, number, nationality, market_value, photo_url
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
    out = []
    for r in rows:
        d = dict(r)
        d["points_this_week"] = player_points(d["id"], week)
        d["price"] = player_price(d["id"], d["position"] or "", d["market_value"])
        out.append(d)
    return {"club_id": club_id, "week": week, "players": out}


@app.get("/api/fantasy/transfers")
async def transfers(days: int = 30):
    conn = db()
    rows = conn.execute("""
        SELECT player_name, from_club, to_club, fee, transfer_type, date, source
        FROM transfers
        WHERE date >= date('now', ?)
        ORDER BY date DESC LIMIT 200
    """, (f"-{days} days",)).fetchall()
    return {"transfers": [dict(r) for r in rows]}


@app.get("/api/fantasy/hot")
async def hot_players():
    """Top scorer simulation per tournament for the current week."""
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
            "price": player_price(top[0]["id"], top[0]["position"] or "", None),
        })
    return {"week": week, "hot": out}


# ═══════════════════════════════════════════════════════
#  OPENBOX ENDPOINTS (unchanged from prototype, moved here)
# ═══════════════════════════════════════════════════════
# The existing OpenBox flows (auth, upload, wallet, messages, groups)
# stay in the frontend as they were — localStorage + IndexedDB.
# Backend only provides what the frontend can't do locally:
# fantasy player data, transfers, hot list, and BubbleJumbo.

@app.get("/api/health")
async def health():
    return {"ok": True, "gameweek": current_gameweek()}


app.mount("/", StaticFiles(directory="static", html=True), name="static")