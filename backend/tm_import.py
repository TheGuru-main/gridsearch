"""
Transfermarkt CSV import — corrected.
- No .csv extension on URLs
- teams_details (plural)
- Filters youth clubs (U18, U23, II, Youth)
- Parses club ID from "Current club URL"
- Skips retired / without-club players
- Batched commits with progress printed
"""
import csv
import io
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

GH = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/raw"

TEAMS_URL   = f"{GH}/teams_details/teams_details"
PLAYERS_URL = f"{GH}/player_profiles/player_profiles"

# Youth / reserve club detection
YOUTH_TOKENS = ["under", "u18", "u19", "u20", "u21", "u23", "youth", " ii", " ii ", "b team", "reserves"]


def _is_youth(name: str, slug: str) -> bool:
    hay = f"{name or ''} {slug or ''}".lower()
    return any(tok in hay for tok in YOUTH_TOKENS)


def _download(url: str, label: str) -> str:
    print(f"[tm] downloading {label}...", flush=True)
    with httpx.Client(timeout=300, follow_redirects=True) as c:
        r = c.get(url)
    r.raise_for_status()
    print(f"[tm] {label} downloaded: {len(r.text)} bytes", flush=True)
    return r.text


def _club_id_from_url(url: str) -> str:
    """Extract numeric club ID from Transfermarkt URL like /napoli/startseite/verein/6195"""
    if not url:
        return ""
    if "verein/" in url:
        return url.split("verein/")[-1].split("/")[0].split("?")[0].strip()
    return ""


def import_clubs() -> dict:
    stats = {"written": 0, "skipped_youth": 0, "errors": []}
    try:
        text = _download(TEAMS_URL, "teams")
    except Exception as e:
        return {"written": 0, "skipped_youth": 0, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    try:
        for i, row in enumerate(reader):
            cid = (row.get("club_id") or "").strip()
            if not cid:
                continue
            name = (row.get("club_name") or "").strip()
            slug = (row.get("club_slug") or "").strip()
            # Skip youth clubs
            if _is_youth(name, slug):
                stats["skipped_youth"] += 1
                continue

            upsert_club(db, {
                "id": f"tm:{cid}",
                "tournament_id": (row.get("competition_slug") or "other").strip()[:40] or "other",
                "name": name,
                "country": (row.get("country_name") or "").strip(),
                "col": i % 30,
            })
            stats["written"] += 1
            if stats["written"] % 500 == 0:
                db.commit()
                print(f"[tm] clubs committed: {stats['written']}", flush=True)
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"clubs write: {e}")
    finally:
        db.close()
    print(f"[tm] clubs written: {stats['written']}, youth skipped: {stats['skipped_youth']}", flush=True)
    return stats


def import_players() -> dict:
    stats = {"written": 0, "skipped_retired": 0, "skipped_no_club": 0, "errors": []}
    try:
        text = _download(PLAYERS_URL, "players")
    except Exception as e:
        return {"written": 0, "skipped_retired": 0, "skipped_no_club": 0, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    try:
        for i, row in enumerate(reader):
            pid = (row.get("player_id") or "").strip()
            if not pid:
                continue

            club_url = (row.get("Current club URL") or "").strip()
            club_name = (row.get("Current club") or "").strip()

            # Skip retired and without club
            low = club_url.lower()
            if "retired" in low:
                stats["skipped_retired"] += 1
                continue
            if "vereinslos" in low or not club_url:
                stats["skipped_no_club"] += 1
                continue

            club_id = _club_id_from_url(club_url)
            if not club_id:
                stats["skipped_no_club"] += 1
                continue

            # Skip youth clubs
            if _is_youth(club_name, ""):
                continue

            pos = (row.get("Position") or row.get("player_main_position") or "").strip()
            upsert_player(db, {
                "id": f"tm:{pid}",
                "name": (row.get("player_name") or "").strip(),
                "position": _normalize_pos(pos),
                "club_id": f"tm:{club_id}",
                "tournament_id": "transfermarkt",
                "number": None,
                "nationality": (row.get("Citizenship") or "").strip(),
                "market_value": None,
                "photo_url": (row.get("player_image_url") or "").strip(),
            })
            stats["written"] += 1
            if stats["written"] % 2000 == 0:
                db.commit()
                print(f"[tm] players committed: {stats['written']}", flush=True)
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"players write: {e}")
    finally:
        db.close()
    print(f"[tm] players written: {stats['written']}", flush=True)
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
                 f"clubs={clubs['written']} youth_skipped={clubs['skipped_youth']} players={players['written']}")
    finally:
        db.close()

    return {
        "ok": not (clubs["errors"] or players["errors"]),
        "clubs": clubs["written"],
        "clubs_skipped_youth": clubs["skipped_youth"],
        "players": players["written"],
        "players_skipped_retired": players["skipped_retired"],
        "players_skipped_no_club": players["skipped_no_club"],
        "errors": clubs["errors"] + players["errors"],
    }