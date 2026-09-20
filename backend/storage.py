"""
Storage layer for scrapers.
- ON CONFLICT upserts for clubs, players, transfers
- FK safety: auto-creates stub club rows when a player references a missing club
- Batch helpers for large imports
- No implicit commits; callers control transaction boundaries
"""
import time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from models import Club, Player, Transfer, SyncLog
from database import init_db


# ═══════════════════════════════════════════════════════
#  CLUBS
# ═══════════════════════════════════════════════════════
def upsert_club(db: Session, club: Dict):
    """Insert or update a club. Idempotent."""
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


def club_exists(db: Session, club_id: str) -> bool:
    row = db.execute(
        text("SELECT 1 FROM clubs WHERE id = :id LIMIT 1"),
        {"id": club_id},
    ).first()
    return bool(row)


def ensure_club(db: Session, club_id: str, name: str = "",
                tournament_id: str = "", country: str = "", col: int = 0):
    """Create the club if missing. Used for FK safety before player inserts."""
    tid = tournament_id or (club_id.split(":")[0] if ":" in club_id else "tm")
    upsert_club(db, {
        "id": club_id,
        "tournament_id": tid,
        "name": name or club_id,
        "country": country,
        "col": col,
    })


# ═══════════════════════════════════════════════════════
#  PLAYERS
# ═══════════════════════════════════════════════════════
def upsert_player(db: Session, player: Dict, auto_create_club: bool = True):
    """
    Insert or update a player. Idempotent.
    If auto_create_club is True and the club_id is missing, creates a stub row
    so the FK constraint on players.club_id doesn't reject the insert.
    """
    club_id = player.get("club_id")
    if auto_create_club and club_id and not club_exists(db, club_id):
        # Derive a display name from the club_id (e.g. "tm:123" → "tm:123")
        ensure_club(db, club_id, name=club_id,
                    tournament_id=player.get("tournament_id") or "")

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
        "club_id": club_id,
        "tid": player.get("tournament_id"),
        "number": player.get("number"),
        "nationality": player.get("nationality"),
        "market_value": player.get("market_value"),
        "photo": player.get("photo_url"),
        "updated_at": time.time(),
    })


def delete_players_by_name(db: Session, name: str,
                           only_source_prefix: Optional[str] = None) -> int:
    """
    Delete players matching name.
    Optionally restrict to a source prefix (e.g. 'tm:%').
    Used to remove stale Transfermarkt rows after Bzzoiro reports a transfer.
    """
    if not name:
        return 0
    if only_source_prefix:
        result = db.execute(text("""
            DELETE FROM players
            WHERE name = :n AND id LIKE :prefix
        """), {"n": name, "prefix": only_source_prefix})
    else:
        result = db.execute(text("""
            DELETE FROM players WHERE name = :n
        """), {"n": name})
    return result.rowcount or 0


def find_players_by_name(db: Session, name: str) -> List[Dict]:
    rows = db.execute(text("""
        SELECT id, name, club_id, tournament_id, position
        FROM players WHERE name = :n
    """), {"n": name}).fetchall()
    return [dict(r._mapping) for r in rows]


# ═══════════════════════════════════════════════════════
#  BATCH HELPERS (for large imports)
# ═══════════════════════════════════════════════════════
def bulk_upsert_clubs(db: Session, clubs: List[Dict]):
    """
    Faster path: pre-ensure all clubs exist, then upsert in bulk.
    Use when you have hundreds+ clubs to write at once.
    """
    for c in clubs:
        upsert_club(db, c)


def bulk_upsert_players(db: Session, players: List[Dict], auto_create_club: bool = True):
    """
    Insert many players in one pass.
    Auto-creates missing clubs lazily (tracks created ids to avoid duplicate work).
    """
    created_clubs = set()
    for p in players:
        club_id = p.get("club_id")
        if auto_create_club and club_id and club_id not in created_clubs:
            if not club_exists(db, club_id):
                ensure_club(db, club_id, name=club_id,
                            tournament_id=p.get("tournament_id") or "")
            created_clubs.add(club_id)
        upsert_player(db, p, auto_create_club=False)


# ═══════════════════════════════════════════════════════
#  TRANSFERS
# ═══════════════════════════════════════════════════════
def insert_transfer(db: Session, t: Dict) -> bool:
    """Insert a transfer. Returns False if it already exists."""
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


def get_recent_transfers(db: Session, days: int = 30) -> List[Dict]:
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    rows = db.execute(text("""
        SELECT player_name, from_club, to_club, fee, transfer_type, date, source
        FROM transfers WHERE date >= :cut
        ORDER BY date DESC LIMIT 200
    """), {"cut": cutoff}).fetchall()
    return [dict(r._mapping) for r in rows]


# ═══════════════════════════════════════════════════════
#  SYNC LOG
# ═══════════════════════════════════════════════════════
def log_sync(db: Session, task: str, status: str, count: int, message: str = ""):
    db.execute(text("""
        INSERT INTO sync_log (task, status, count, message, ran_at)
        VALUES (:t, :s, :c, :m, :r)
    """), {"t": task, "s": status, "c": count, "m": message, "r": time.time()})
    db.commit()


# ═══════════════════════════════════════════════════════
#  CLEANUP HELPERS
# ═══════════════════════════════════════════════════════
def delete_unmapped_clubs(db: Session) -> int:
    """Delete clubs whose tournament_id isn't a registry tournament."""
    result = db.execute(text("""
        DELETE FROM clubs
        WHERE tournament_id LIKE 'tm%' OR tournament_id LIKE 'bzz_%'
    """))
    return result.rowcount or 0


def delete_unmapped_players(db: Session) -> int:
    """Delete players whose tournament_id isn't a registry tournament."""
    result = db.execute(text("""
        DELETE FROM players
        WHERE tournament_id LIKE 'tm%' OR tournament_id LIKE 'bzz_%'
    """))
    return result.rowcount or 0