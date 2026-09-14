"""
Import the salimt/football-datasets Transfermarkt CSVs into Neon.
One-shot. 92,671 players, 2,175 clubs.
"""
import csv, io
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

GH_RAW = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/raw"


def _download(path: str) -> str:
    url = f"{GH_RAW}/{path}"
    with httpx.Client(timeout=120, follow_redirects=True) as c:
        r = c.get(url)
    r.raise_for_status()
    return r.text


def import_all() -> dict:
    stats = {"clubs": 0, "players": 0, "errors": []}
    init_db()

    # ─── Clubs ───
    try:
        text = _download("teams_details/teams_details.csv")
        reader = csv.DictReader(io.StringIO(text))
        db = SessionLocal()
        try:
            for row in reader:
                tid = row.get("team_id") or row.get("club_id")
                if not tid: continue
                upsert_club(db, {
                    "id": f"tm:{tid}",
                    "tournament_id": "transfermarkt",
                    "name": row.get("name") or row.get("club_name") or "",
                    "country": row.get("country_name") or "",
                    "col": 0,
                })
                stats["clubs"] += 1
                if stats["clubs"] % 500 == 0: db.commit()
            db.commit()
        finally:
            db.close()
    except Exception as e:
        stats["errors"].append(f"clubs: {e}")

    # ─── Players ───
    try:
        text = _download("player_profiles/player_profiles.csv")
        reader = csv.DictReader(io.StringIO(text))
        db = SessionLocal()
        try:
            for i, row in enumerate(reader):
                pid = row.get("player_id")
                if not pid: continue
                club_id = row.get("current_club_id") or ""
                upsert_player(db, {
                    "id": f"tm:{pid}",
                    "name": row.get("player_name") or "",
                    "position": row.get("position") or row.get("player_main_position"),
                    "club_id": f"tm:{club_id}" if club_id else None,
                    "tournament_id": "transfermarkt",
                    "number": None,
                    "nationality": row.get("citizenship") or row.get("citizenship_country"),
                    "market_value": None,
                    "photo_url": row.get("player_image_url"),
                })
                stats["players"] += 1
                if stats["players"] % 1000 == 0: db.commit()
            db.commit()
        finally:
            db.close()
    except Exception as e:
        stats["errors"].append(f"players: {e}")

    db = SessionLocal()
    try:
        log_sync(db, "tm:import", "ok" if not stats["errors"] else "partial",
                 stats["players"], "; ".join(stats["errors"][:2]))
    finally:
        db.close()
    stats["ok"] = not stats["errors"]
    return stats