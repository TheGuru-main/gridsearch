"""
Transfermarkt CSV import — verified paths and columns.
Downloads two CSVs from GitHub, populates clubs + players in Neon.
"""
import csv
import io
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

GH = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt"

TEAMS_CSV   = f"{GH}/team_details/team_details.csv"
PLAYERS_CSV = f"{GH}/player_profiles/player_profiles.csv"


def _download(url: str) -> str:
    with httpx.Client(timeout=180, follow_redirects=True) as c:
        r = c.get(url)
    r.raise_for_status()
    return r.text


def import_clubs() -> dict:
    stats = {"written": 0, "errors": []}
    print("[tm] downloading teams CSV...")
    try:
        text = _download(TEAMS_CSV)
    except Exception as e:
        return {"written": 0, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    try:
        for i, row in enumerate(reader):
            cid = (row.get("club_id") or "").strip()
            if not cid:
                continue
            name = (row.get("club_name") or "").strip()
            # Skip youth/reserve squads if you want a cleaner DB
            # if "U23" in name or "Under" in name or " II" in name: continue
            upsert_club(db, {
                "id": f"tm:{cid}",
                "tournament_id": (row.get("competition_slug") or "other").strip()[:40],
                "name": name,
                "country": (row.get("country_name") or "").strip(),
                "col": i % 30,
            })
            stats["written"] += 1
            if stats["written"] % 500 == 0:
                db.commit()
                print(f"[tm] clubs committed: {stats['written']}")
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"clubs write: {e}")
    finally:
        db.close()
    print(f"[tm] clubs total: {stats['written']}")
    return stats


def import_players() -> dict:
    stats = {"written": 0, "errors": []}
    print("[tm] downloading players CSV (26 MB)...")
    try:
        text = _download(PLAYERS_CSV)
    except Exception as e:
        return {"written": 0, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    try:
        for i, row in enumerate(reader):
            pid = (row.get("player_id") or "").strip()
            if not pid:
                continue
            club_id = (row.get("current_club_id") or "").strip()
            pos = (row.get("position") or row.get("player_main_position") or "").strip()
            upsert_player(db, {
                "id": f"tm:{pid}",
                "name": (row.get("player_name") or "").strip(),
                "position": _normalize_pos(pos),
                "club_id": f"tm:{club_id}" if club_id else None,
                "tournament_id": "transfermarkt",
                "number": None,
                "nationality": (row.get("citizenship") or "").strip(),
                "market_value": None,
                "photo_url": (row.get("player_image_url") or "").strip(),
            })
            stats["written"] += 1
            if stats["written"] % 2000 == 0:
                db.commit()
                print(f"[tm] players committed: {stats['written']}")
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"players write: {e}")
    finally:
        db.close()
    print(f"[tm] players total: {stats['written']}")
    return stats


def _normalize_pos(p: str) -> str:
    p = (p or "").lower()
    if "goalkeeper" in p or p == "gk": return "GK"
    if "defender" in p or "back" in p or p == "def": return "DEF"
    if "midfield" in p or p == "mid": return "MID"
    if "forward" in p or "attack" in p or "striker" in p or p == "fwd": return "FWD"
    return "MID"


def import_all() -> dict:
    init_db()
    clubs = import_clubs()
    players = import_players()

    db = SessionLocal()
    try:
        log_sync(db, "tm:import",
                 "ok" if not (clubs["errors"] or players["errors"]) else "partial",
                 players["written"],
                 f"clubs={clubs['written']} players={players['written']}")
    finally:
        db.close()

    return {
        "ok": not (clubs["errors"] or players["errors"]),
        "clubs": clubs["written"],
        "players": players["written"],
        "errors": clubs["errors"] + players["errors"],
    }