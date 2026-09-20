"""
ORM models. One table per domain:
- User, Session, LedgerEntry  → auth + wallet
- OpenBoxItem                 → uploads
- Club, Player, Transfer      → fantasy + scraper
- SyncLog                     → scraper audit
"""
import time
from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, Index, UniqueConstraint, BigInteger
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    phone = Column(String(32), primary_key=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200))
    password_hash = Column(String(128), nullable=False)
    dob = Column(String(32))
    talent = Column(String(64))
    country = Column(String(8))
    byflints = Column(Float, default=0.0, nullable=False)
    created_at = Column(Float, default=time.time)


class SessionToken(Base):
    __tablename__ = "sessions"

    token = Column(String(64), primary_key=True)
    phone = Column(String(32), ForeignKey("users.phone"), nullable=False, index=True)
    created_at = Column(Float, default=time.time)


class LedgerEntry(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(32), ForeignKey("users.phone"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(200))
    ref = Column(String(128))
    created_at = Column(Float, default=time.time)


class OpenBoxItem(Base):
    __tablename__ = "openbox_items"

    id = Column(String(32), primary_key=True)
    title = Column(String(300), nullable=False)
    kind = Column(String(32))
    category = Column(String(32), index=True)
    description = Column(Text)
    uploader = Column(String(32), ForeignKey("users.phone"), index=True)
    price_byflints = Column(Float, default=0.0)
    fee_paid = Column(Float, default=0.0)
    filename = Column(String(200))
    file_size = Column(BigInteger)
    mime_type = Column(String(128))
    gsp_col = Column(Integer)
    gsp_row = Column(Integer)
    downloads = Column(Integer, default=0)
    earnings = Column(Float, default=0.0)
    created_at = Column(Float, default=time.time)


class Club(Base):
    __tablename__ = "clubs"

    id = Column(String(64), primary_key=True)
    tournament_id = Column(String(32), index=True)
    name = Column(String(200), nullable=False)
    country = Column(String(64))
    col = Column(Integer)
    updated_at = Column(Float, default=time.time)


class Player(Base):
    __tablename__ = "players"

    id = Column(String(80), primary_key=True)
    name = Column(String(200), nullable=False)
    position = Column(String(32))
    club_id = Column(String(64), ForeignKey("clubs.id"), index=True)
    tournament_id = Column(String(32), index=True)
    number = Column(Integer)
    nationality = Column(String(64))
    market_value = Column(BigInteger)
    photo_url = Column(String(400))
    updated_at = Column(Float, default=time.time)

    __table_args__ = (
        Index("idx_players_tournament", "tournament_id"),
    )


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String(200), nullable=False)
    from_club = Column(String(200))
    to_club = Column(String(200))
    fee = Column(String(64))
    transfer_type = Column(String(32))
    date = Column(String(16), index=True)
    source = Column(String(32))
    source_url = Column(String(400))
    tournament_hint = Column(String(32))
    scraped_at = Column(Float, default=time.time)

    __table_args__ = (
        UniqueConstraint("player_name", "from_club", "to_club", "date", name="uq_transfer"),
    )

class SyncLog(Base):
    __tablename__ = "sync_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task = Column(String(64))
    status = Column(String(16))
    count = Column(Integer, default=0)
    message = Column(Text)
    ran_at = Column(Float, default=time.time)

class SyncState(Base):
    __tablename__ = "sync_state"

    id = Column(String(32), primary_key=True)
    running = Column(Integer, default=0)
    current_index = Column(Integer, default=0)
    total_leagues = Column(Integer, default=0)
    candidate_ids = Column(Text)
    completed_ids = Column(Text)
    clubs_written = Column(Integer, default=0)
    players_written = Column(Integer, default=0)
    mapped_clubs = Column(Integer, default=0)
    unmapped_clubs = Column(Integer, default=0)
    errors = Column(Text)
    started_at = Column(Float, default=0)
    updated_at = Column(Float, default=time.time)
