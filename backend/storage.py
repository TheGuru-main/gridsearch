"""
SQLite storage for transfers, players, and clubs.
"""
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path("storage/transfers.db")
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS clubs (
            id TEXT PRIMARY KEY,
            tournament_id TEXT,
            name TEXT NOT NULL,
            country TEXT,
            col INTEGER,
            updated_at REAL
        );

        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT,
            club_id TEXT,
            tournament_id TEXT,
            number INTEGER,
            nationality TEXT,
            market_value INTEGER,
            photo_url TEXT,
            updated_at REAL,
            FOREIGN KEY(club_id) REFERENCES clubs(id)
        );

        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            from_club TEXT,
            to_club TEXT,
            fee TEXT,
            transfer_type TEXT,
            date TEXT,
            source TEXT,
            source_url TEXT,
            tournament_hint TEXT,
            scraped_at REAL,
            UNIQUE(player_name, from_club, to_club, date)
        );

        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            status TEXT,
            count INTEGER,
            message TEXT,
            ran_at REAL
        );

        CREATE INDEX IF NOT EXISTS idx_players_club ON players(club_id);
        CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(date);
    """)
    conn.commit()
    return conn


def upsert_club(conn, club: Dict):
    c = conn.cursor()
    c.execute("""
        INSERT INTO clubs (id, tournament_id, name, country, col, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            country=excluded.country,
            col=excluded.col,
            updated_at=excluded.updated_at
    """, (
        club["id"], club.get("tournament_id"), club["name"],
        club.get("country"), club.get("col"), time.time()
    ))
    conn.commit()


def upsert_player(conn, player: Dict):
    c = conn.cursor()
    c.execute("""
        INSERT INTO players (id, name, position, club_id, tournament_id,
                             number, nationality, market_value, photo_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            position=excluded.position,
            club_id=excluded.club_id,
            tournament_id=excluded.tournament_id,
            number=excluded.number,
            nationality=excluded.nationality,
            market_value=excluded.market_value,
            photo_url=excluded.photo_url,
            updated_at=excluded.updated_at
    """, (
        player["id"], player["name"], player.get("position"),
        player.get("club_id"), player.get("tournament_id"),
        player.get("number"), player.get("nationality"),
        player.get("market_value"), player.get("photo_url"),
        time.time()
    ))
    conn.commit()


def insert_transfer(conn, t: Dict) -> bool:
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR IGNORE INTO transfers
                (player_name, from_club, to_club, fee, transfer_type,
                 date, source, source_url, tournament_hint, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["player_name"], t.get("from_club"), t.get("to_club"),
            t.get("fee"), t.get("transfer_type"), t.get("date"),
            t.get("source"), t.get("source_url"),
            t.get("tournament_hint"), time.time()
        ))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        print(f"[storage] insert failed: {e}")
        return False


def log_sync(conn, task: str, status: str, count: int, message: str = ""):
    c = conn.cursor()
    c.execute("""
        INSERT INTO sync_log (task, status, count, message, ran_at)
        VALUES (?, ?, ?, ?, ?)
    """, (task, status, count, message, time.time()))
    conn.commit()


def get_recent_transfers(conn, days: int = 30) -> List[Dict]:
    c = conn.cursor()
    c.execute("""
        SELECT player_name, from_club, to_club, fee, transfer_type,
               date, source, source_url
        FROM transfers
        WHERE date >= date('now', ?)
        ORDER BY date DESC
    """, (f"-{days} days",))
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, row)) for row in c.fetchall()]