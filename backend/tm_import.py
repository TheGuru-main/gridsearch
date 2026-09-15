"""
Transfermarkt CSV import — corrected URLs and registry mapping.
Source: github.com/salimt/football-datasets
- Fixes: /raw/ removed from URLs
- Fixes: uses registry_map.canonical_club_id to write clubs under app IDs
- Fixes: builds a tm_id -> canonical_id map so players inherit the correct club
"""
import csv
import io
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync
from registry_map import match_tournament, canonical_club_id, REGISTRY

# ── Verified 2026-09 URLs (no /raw/ in path) ──
GH = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt"
TEAMS_URL   = f"{GH}/team_details/team_details.csv"
PLAYERS_URL = f"{GH}/player_profiles/player_profiles.csv"

YOUTH_TOKENS = ["under", "u18", "u19", "u20", "u21", "u23",
                "youth", " ii", " ii ", "b team", "reserves", "academy"]


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


def _get(row: dict, *names):
    """Try multiple column names (snake_case or Title Case)."""
    for n in names:
        v = row.get(n)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return ""


def _club_id_from_url(url: str) -> str:
    """Extract numeric club ID from URLs like /napoli/startseite/verein/6195"""
    if not url:
        return ""
    if "/verein/" in url:
        return url.split("/verein/")[-1].split("/")[0].split("?")[0].strip()
    return ""

def import_clubs() -> dict:
    stats = {"written": 0, "skipped_youth": 0, "skipped_dup": 0,
             "mapped": 0, "unmapped": 0, "errors": [],
             "tm_to_canonical": {}}
    try:
        text = _download(TEAMS_URL, "teams")
    except Exception as e:
        return {**stats, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    seen = set()
    try:
        for i, row in enumerate(reader):
            cid = _get(row, "club_id", "Club ID")
            if not cid:
                continue
            name = _get(row, "club_name", "Club Name", "name")
            slug = _get(row, "club_slug", "Club Slug", "slug")
            country = _get(row, "country_name", "Country Name", "country")
            comp_slug = _get(row, "competition_slug", "Competition Slug")
            comp_name = _get(row, "competition_name", "Competition Name")

            if _is_youth(name, slug):
                stats["skipped_youth"] += 1
                continue

            tid = match_tournament(comp_slug) or match_tournament(comp_name)
            canonical = canonical_club_id(tid, name, "tm", cid)

            # Skip duplicates within this batch
            if canonical in seen:
                stats["skipped_dup"] += 1
                continue
            seen.add(canonical)

            stats["tm_to_canonical"][str(cid)] = canonical

            if tid and canonical.startswith(f"{tid}:"):
                stats["mapped"] += 1
            else:
                stats["unmapped"] += 1

            upsert_club(db, {
                "id": canonical,
                "tournament_id": canonical.split(":")[0],
                "name": name,
                "country": country,
                "col": i % 30,
            })
            stats["written"] += 1
            if stats["written"] % 500 == 0:
                db.commit()
                seen = set()   # reset after commit
                print(f"[tm] clubs committed: {stats['written']}", flush=True)
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"clubs write: {e}")
    finally:
        db.close()

    print(f"[tm] clubs: {stats['written']} written, "
          f"{stats['skipped_youth']} youth, {stats['skipped_dup']} dup, "
          f"{stats['mapped']} mapped", flush=True)
    return stats

def _normalize_pos(p: str) -> str:
    p = (p or "").lower()
    if "goalkeeper" in p or p == "gk": return "GK"
    if "defender" in p or "back" in p or p == "def": return "DEF"
    if "midfield" in p or p == "mid": return "MID"
    if "forward" in p or "attack" in p or "striker" in p or "winger" in p or p == "fwd":
        return "FWD"
    return "MID"

def import_players(tm_to_canonical: dict) -> dict:
    stats = {"written": 0, "skipped_retired": 0, "skipped_no_club": 0,
             "skipped_youth": 0, "mapped": 0, "unmapped": 0,
             "stub_clubs": 0, "errors": []}
    try:
        text = _download(PLAYERS_URL, "players")
    except Exception as e:
        return {**stats, "errors": [f"download: {e}"]}

    reader = csv.DictReader(io.StringIO(text))
    db = SessionLocal()
    known_clubs = set()   # canonical ids we've already ensured exist
    try:
        for i, row in enumerate(reader):
            pid = _get(row, "player_id", "Player ID", "id")
            if not pid:
                continue

            # Club identification — accept EITHER id or url
            club_url = _get(row, "current_club_url", "Current Club URL",
                            "Current club URL", "club_url")
            club_id  = _get(row, "current_club_id", "Current Club ID",
                            "Current club ID", "club_id")

            if not club_url and not club_id:
                stats["skipped_no_club"] += 1
                continue

            # Skip retired / without club when URL is present
            if club_url:
                low = club_url.lower()
                if "retired" in low:
                    stats["skipped_retired"] += 1
                    continue
                if "vereinslos" in low:
                    stats["skipped_no_club"] += 1
                    continue
                if _is_youth(club_url, ""):
                    stats["skipped_youth"] += 1
                    continue

            # Resolve canonical club ID
            canonical = None
            if club_id:
                canonical = tm_to_canonical.get(str(club_id))
            if not canonical and club_url:
                cid_from_url = _club_id_from_url(club_url)
                if cid_from_url:
                    canonical = tm_to_canonical.get(str(cid_from_url))
            if not canonical:
                ref = club_id or _club_id_from_url(club_url) or "unknown"
                canonical = f"tm:{ref}"
                stats["unmapped"] += 1
            else:
                stats["mapped"] += 1

            # ── Ensure the club row exists (FK safety) ──
            if canonical not in known_clubs:
                # Upsert a stub club so the FK is satisfied
                club_name = _get(row, "current_club_name", "Current Club Name",
                                 "Current club name", "club_name") or canonical
                upsert_club(db, {
                    "id": canonical,
                    "tournament_id": canonical.split(":")[0],
                    "name": club_name,
                    "country": "",
                    "col": 0,
                })
                known_clubs.add(canonical)
                # Only count as a stub if it's a tm: fallback, not a registry match
                if canonical.startswith("tm:"):
                    stats["stub_clubs"] += 1

            pos = _get(row, "player_main_position", "Player Main Position",
                       "position", "Position", "player_position")

            upsert_player(db, {
                "id": f"tm:{pid}",
                "name": _get(row, "player_name", "Player Name", "name"),
                "position": _normalize_pos(pos),
                "club_id": canonical,
                "tournament_id": canonical.split(":")[0],
                "number": None,
                "nationality": _get(row, "citizenship", "Citizenship",
                                    "nationality"),
                "market_value": None,
                "photo_url": _get(row, "player_image_url", "Player Image URL",
                                  "image_url"),
            })
            stats["written"] += 1
            if stats["written"] % 2000 == 0:
                db.commit()
                known_clubs = set()   # reset after commit; next player rechecks
                print(f"[tm] players committed: {stats['written']}", flush=True)
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"players write: {e}")
    finally:
        db.close()

    print(f"[tm] players: {stats['written']} written, "
          f"{stats['mapped']} mapped, {stats['unmapped']} unmapped, "
          f"{stats['stub_clubs']} stub clubs created", flush=True)
    return stats


def import_all() -> dict:
    init_db()
    clubs = import_clubs()
    players = import_players(clubs.pop("tm_to_canonical", {}))

    db = SessionLocal()
    try:
        log_sync(db, "tm:import",
                 "ok" if not (clubs["errors"] or players["errors"]) else "partial",
                 players["written"],
                 f"clubs={clubs['written']} mapped={clubs['mapped']} "
                 f"players={players['written']} p_mapped={players['mapped']}")
    finally:
        db.close()

    return {
    "ok": not (clubs["errors"] or players["errors"]),
    "clubs": clubs["written"],
    "clubs_skipped_youth": clubs["skipped_youth"],
    "clubs_mapped": clubs["mapped"],
    "clubs_unmapped": clubs["unmapped"],
    "players": players["written"],
    "players_mapped": players["mapped"],
    "players_unmapped": players["unmapped"],
    "players_skipped_retired": players["skipped_retired"],
    "players_skipped_no_club": players["skipped_no_club"],
    "players_stub_clubs": players.get("stub_clubs", 0),
    "errors": clubs["errors"] + players["errors"],
}