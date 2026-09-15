import time
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

from models import Club, Player, Transfer, SyncLog
from database import init_db


def upsert_club(db: Session, club: Dict):
    db.execute(text("""
        INSERT INTO clubs (id, tournament_id, name, country, col, updated_at)
        VALUES (:id, :tid, :name, :country, :col, :updated_at)
        ON CONFLICT (id) DO UPDATE SET
            tournament_id = EXCLUDED.tournament_id,
            name          = EXCLUDED.name,
            country       = EXCLUDED.country,
            col           = EXCLUDED.col,
            updated_at    = EXCLUDED.updated_at
    """), {
        "id": club["id"],
        "tid": club.get("tournament_id"),
        "name": club["name"],
        "country": club.get("country"),
        "col": club.get("col"),
        "updated_at": time.time(),
    })


def upsert_player(db: Session, player: Dict):
    db.execute(text("""
        INSERT INTO players (id, name, position, club_id, tournament_id,
                             number, nationality, market_value, photo_url, updated_at)
        VALUES (:id, :name, :position, :club_id, :tid,
                :number, :nationality, :market_value, :photo, :updated_at)
        ON CONFLICT (id) DO UPDATE SET
            name          = EXCLUDED.name,
            position      = EXCLUDED.position,
            club_id       = EXCLUDED.club_id,
            tournament_id = EXCLUDED.tournament_id,
            number        = EXCLUDED.number,
            nationality   = EXCLUDED.nationality,
            market_value  = EXCLUDED.market_value,
            photo_url     = EXCLUDED.photo_url,
            updated_at    = EXCLUDED.updated_at
    """), {
        "id": player["id"],
        "name": player["name"],
        "position": player.get("position"),
        "club_id": player.get("club_id"),
        "tid": player.get("tournament_id"),
        "number": player.get("number"),
        "nationality": player.get("nationality"),
        "market_value": player.get("market_value"),
        "photo": player.get("photo_url"),
        "updated_at": time.time(),
    })


def insert_transfer(db: Session, t: Dict) -> bool:
    existing = db.execute(text("""
        SELECT 1 FROM transfers
        WHERE player_name = :pn AND date = :d
          AND COALESCE(from_club, '') = COALESCE(:fc, '')
          AND COALESCE(to_club, '')   = COALESCE(:tc, '')
        LIMIT 1
    """), {
        "pn": t["player_name"], "d": t.get("date"),
        "fc": t.get("from_club"), "tc": t.get("to_club"),
    }).first()
    if existing:
        return False
    db.execute(text("""
        INSERT INTO transfers
            (player_name, from_club, to_club, fee, transfer_type,
             date, source, source_url, tournament_hint, scraped_at)
        VALUES (:pn, :fc, :tc, :fee, :tt, :d, :src, :su, :th, :st)
    """), {
        "pn": t["player_name"], "fc": t.get("from_club"), "tc": t.get("to_club"),
        "fee": t.get("fee"), "tt": t.get("transfer_type"), "d": t.get("date"),
        "src": t.get("source"), "su": t.get("source_url"),
        "th": t.get("tournament_hint"), "st": time.time(),
    })
    return True


def log_sync(db: Session, task: str, status: str, count: int, message: str = ""):
    db.execute(text("""
        INSERT INTO sync_log (task, status, count, message, ran_at)
        VALUES (:t, :s, :c, :m, :r)
    """), {"t": task, "s": status, "c": count, "m": message, "r": time.time()})
    db.commit()


def get_recent_transfers(db: Session, days: int = 30) -> List[Dict]:
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    rows = db.execute(text("""
        SELECT player_name, from_club, to_club, fee, transfer_type, date, source
        FROM transfers WHERE date >= :cut
        ORDER BY date DESC LIMIT 200
    """), {"cut": cutoff}).fetchall()
    return [dict(r._mapping) for r in rows]