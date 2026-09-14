"""
Storage helpers for the scraper. All operate on a SQLAlchemy Session.
"""
import time
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models import Club, Player, Transfer, SyncLog
from database import init_db


def upsert_club(db: Session, club: Dict):
    obj = db.get(Club, club["id"])
    if obj:
        obj.name = club["name"]
        obj.country = club.get("country")
        obj.col = club.get("col")
        obj.updated_at = time.time()
    else:
        db.add(Club(
            id=club["id"],
            tournament_id=club.get("tournament_id"),
            name=club["name"],
            country=club.get("country"),
            col=club.get("col"),
            updated_at=time.time(),
        ))


def upsert_player(db: Session, player: Dict):
    obj = db.get(Player, player["id"])
    if obj:
        obj.name = player["name"]
        obj.position = player.get("position")
        obj.club_id = player.get("club_id")
        obj.tournament_id = player.get("tournament_id")
        obj.number = player.get("number")
        obj.nationality = player.get("nationality")
        obj.market_value = player.get("market_value")
        obj.photo_url = player.get("photo_url")
        obj.updated_at = time.time()
    else:
        db.add(Player(
            id=player["id"],
            name=player["name"],
            position=player.get("position"),
            club_id=player.get("club_id"),
            tournament_id=player.get("tournament_id"),
            number=player.get("number"),
            nationality=player.get("nationality"),
            market_value=player.get("market_value"),
            photo_url=player.get("photo_url"),
            updated_at=time.time(),
        ))


def insert_transfer(db: Session, t: Dict) -> bool:
    exists = db.query(Transfer).filter_by(
        player_name=t["player_name"],
        from_club=t.get("from_club"),
        to_club=t.get("to_club"),
        date=t.get("date"),
    ).first()
    if exists:
        return False
    db.add(Transfer(
        player_name=t["player_name"],
        from_club=t.get("from_club"),
        to_club=t.get("to_club"),
        fee=t.get("fee"),
        transfer_type=t.get("transfer_type"),
        date=t.get("date"),
        source=t.get("source"),
        source_url=t.get("source_url"),
        tournament_hint=t.get("tournament_hint"),
        scraped_at=time.time(),
    ))
    return True


def log_sync(db: Session, task: str, status: str, count: int, message: str = ""):
    db.add(SyncLog(task=task, status=status, count=count, message=message))
    db.commit()


def get_recent_transfers(db: Session, days: int = 30) -> List[Dict]:
    # Postgres: interval via SQL
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    rows = db.query(Transfer).filter(Transfer.date >= cutoff).order_by(Transfer.date.desc()).all()
    return [
        {
            "player_name": r.player_name,
            "from_club": r.from_club,
            "to_club": r.to_club,
            "fee": r.fee,
            "transfer_type": r.transfer_type,
            "date": r.date,
            "source": r.source,
            "source_url": r.source_url,
        }
        for r in rows
    ]