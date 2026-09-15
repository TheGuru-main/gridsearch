"""
Bzzoiro sync — single league OR all leagues, with registry mapping.
Free token: sports.bzzoiro.com/register
"""
import os
import time
import threading
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync
from registry_map import match_tournament, match_club, canonical_club_id

BASE = "https://sports.bzzoiro.com/api/v2"

# Leagues whose names match these tokens are skipped during sync-all
SKIP_TOKENS = [
    "qualification", "qualifier",
    "women", "womens", "ladies",
    "under", "u18", "u19", "u20", "u21", "u23",
    "youth", "academy", "primavera", "junioren", "jugend",
    "friendly", "friendlies",
    "reserve", " ii ", " b team",
]

_SYNC_STATE = {
    "running": False, "stop_requested": False,
    "started_at": 0, "finished_at": 0,
    "total_leagues": 0, "current_index": 0,
    "current_league_id": None, "current_league_name": None,
    "current_registry_match": None,
    "leagues_completed": [], "leagues_skipped": [],
    "clubs_written": 0, "players_written": 0,
    "mapped_clubs": 0, "unmapped_clubs": 0,
    "errors": [], "mode": "idle",
}


def get_state():
    return dict(_SYNC_STATE)


def stop_sync():
    _SYNC_STATE["stop_requested"] = True
    return {"ok": True, "message": "Stop requested. Finishing current team."}


def _h():
    tok = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {tok}"} if tok else {}


def _pos(code):
    c = (code or "").upper()[:1]
    return {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}.get(c, "MID")


def _extract_list(payload):
    """Handle both raw lists and paginated {count, results} objects."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("results"), list):
            return payload["results"]
        for v in payload.values():
            if isinstance(v, list):
                return v
    return []


def _should_skip_league(name: str) -> bool:
    low = (name or "").lower()
    return any(tok in low for tok in SKIP_TOKENS)


def _fetch_all_leagues(client):
    leagues = []
    url = f"{BASE}/leagues/"
    params = {"limit": 100}
    while url and len(leagues) < 500:
        r = client.get(url, params=params)
        if r.status_code != 200:
            break
        body = r.json()
        leagues.extend(body.get("results") or [])
        url = body.get("next")
        params = None
        time.sleep(0.2)
    return leagues


def _fetch_league_name(client, league_id: int) -> str:
    """Fetch the league's name from Bzzoiro. Returns '' on failure."""
    try:
        r = client.get(f"{BASE}/leagues/{league_id}/")
        if r.status_code == 200:
            return (r.json() or {}).get("name") or ""
    except Exception:
        pass
    return ""


def sync_league(league_id: int, league_name: str = None,
                silent: bool = False) -> dict:
    """
    Sync one Bzzoiro league.
    If league_name is None, fetches it from the API so registry matching works.
    """
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set"}

    stats = {"league_id": league_id, "league_name": league_name,
             "registry_match": None,
             "clubs": 0, "players": 0,
             "mapped": 0, "unmapped": 0,
             "errors": [], "teams": []}

    # ── Fetch league name if not provided ──
    if not league_name:
        with httpx.Client(timeout=15, headers=h) as probe:
            league_name = _fetch_league_name(probe, league_id)
            stats["league_name"] = league_name

    # ── Match to registry tournament ──
    registry_tid = match_tournament(league_name) if league_name else None
    stats["registry_match"] = registry_tid
    source_key = f"bzz_{league_id}"

    with httpx.Client(timeout=30, headers=h) as c:
        # ── Teams (paginated) ──
        url = f"{BASE}/teams/"
        params = {"league_id": league_id, "limit": 100}
        teams = []
        while url and len(teams) < 500:
            r = c.get(url, params=params)
            if r.status_code != 200:
                stats["errors"].append(f"teams HTTP {r.status_code}: {r.text[:150]}")
                break
            body = r.json()
            teams.extend(_extract_list(body))
            url = body.get("next") if isinstance(body, dict) else None
            params = None
            time.sleep(0.15)

        if not teams:
            stats["errors"].append("no teams returned")
            return stats

        # ── Clubs with mapping ──
        db = SessionLocal()
        try:
            for i, t in enumerate(teams):
                team_name = t.get("name") or ""
                canonical = canonical_club_id(
                    registry_tid, team_name, source_key, t.get("id")
                )
                tid_for_db = canonical.split(":")[0]

                upsert_club(db, {
                    "id": canonical,
                    "tournament_id": tid_for_db,
                    "name": team_name,
                    "country": t.get("country") or "",
                    "col": i,
                })
                stats["clubs"] += 1
                if registry_tid and canonical.startswith(f"{registry_tid}:"):
                    stats["mapped"] += 1
                else:
                    stats["unmapped"] += 1
            db.commit()
        except Exception as e:
            db.rollback()
            stats["errors"].append(f"clubs write: {e}")
        finally:
            db.close()

        # ── Squads ──
        for t in teams:
            if _SYNC_STATE["stop_requested"]:
                break
            tid = t.get("id")
            tname = t.get("name") or f"team-{tid}"
            if not tid:
                continue
            canonical = canonical_club_id(registry_tid, tname, source_key, tid)
            try:
                time.sleep(0.15)
                r = c.get(f"{BASE}/teams/{tid}/squad/")
                if r.status_code != 200:
                    continue
                squad = _extract_list(r.json())
                db = SessionLocal()
                try:
                    for p in squad:
                        if not isinstance(p, dict):
                            continue
                        pid = p.get("id")
                        if not pid:
                            continue
                        upsert_player(db, {
                            "id": f"{canonical}:{pid}",
                            "name": p.get("name") or "",
                            "position": _pos(p.get("position")),
                            "club_id": canonical,
                            "tournament_id": canonical.split(":")[0],
                            "number": p.get("shirt_number"),
                            "nationality": p.get("nationality") or p.get("nationality_code"),
                            "market_value": p.get("market_value"),
                            "photo_url": p.get("image_url"),
                        })
                    db.commit()
                    stats["players"] += len(squad)
                    stats["teams"].append({"team": tname, "players": len(squad)})
                except Exception as e:
                    db.rollback()
                    stats["errors"].append(f"{tname} DB: {e}")
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{tname}: {e}")

    if not silent:
        db = SessionLocal()
        try:
            log_sync(db, f"bzz:{league_id}",
                     "ok" if not stats["errors"] else "partial",
                     stats["players"],
                     f"name={stats['league_name']} match={stats['registry_match']} "
                     f"mapped={stats['mapped']} unmapped={stats['unmapped']}")
        finally:
            db.close()

    stats["ok"] = not stats["errors"]
    return stats


def _run_sync_all():
    _SYNC_STATE.update({
        "running": True, "stop_requested": False,
        "started_at": time.time(), "finished_at": 0,
        "leagues_completed": [], "leagues_skipped": [],
        "clubs_written": 0, "players_written": 0,
        "mapped_clubs": 0, "unmapped_clubs": 0,
        "errors": [], "mode": "all",
        "current_registry_match": None,
    })
    init_db()

    h = _h()
    if not h:
        _SYNC_STATE["errors"].append("BZZOIRO_TOKEN not set")
        _SYNC_STATE["running"] = False
        _SYNC_STATE["finished_at"] = time.time()
        return

    try:
        with httpx.Client(timeout=30, headers=h) as c:
            all_leagues = _fetch_all_leagues(c)

        candidates = []
        for lg in all_leagues:
            if not lg.get("is_active") or not lg.get("current_season"):
                continue
            name = lg.get("name") or ""
            if _should_skip_league(name):
                _SYNC_STATE["leagues_skipped"].append(
                    {"id": lg.get("id"), "name": name, "reason": "filtered"})
                continue
            candidates.append(lg)

        _SYNC_STATE["total_leagues"] = len(candidates)

        for idx, lg in enumerate(candidates):
            if _SYNC_STATE["stop_requested"]:
                break
            _SYNC_STATE["current_index"] = idx + 1
            _SYNC_STATE["current_league_id"] = lg.get("id")
            _SYNC_STATE["current_league_name"] = lg.get("name")

            try:
                stats = sync_league(lg["id"], lg.get("name"), silent=True)
                _SYNC_STATE["current_registry_match"] = stats.get("registry_match")
                _SYNC_STATE["clubs_written"] += stats.get("clubs", 0)
                _SYNC_STATE["players_written"] += stats.get("players", 0)
                _SYNC_STATE["mapped_clubs"] += stats.get("mapped", 0)
                _SYNC_STATE["unmapped_clubs"] += stats.get("unmapped", 0)
                _SYNC_STATE["leagues_completed"].append({
                    "id": lg["id"],
                    "name": lg.get("name"),
                    "registry": stats.get("registry_match"),
                    "clubs": stats.get("clubs", 0),
                    "players": stats.get("players", 0),
                    "mapped": stats.get("mapped", 0),
                })
                if stats.get("errors"):
                    _SYNC_STATE["errors"].extend(stats["errors"][:2])
            except Exception as e:
                _SYNC_STATE["errors"].append(f"league {lg.get('id')}: {e}")
    except Exception as e:
        _SYNC_STATE["errors"].append(f"outer: {e}")
    finally:
        _SYNC_STATE["running"] = False
        _SYNC_STATE["finished_at"] = time.time()
        _SYNC_STATE["mode"] = "idle"

        db = SessionLocal()
        try:
            log_sync(db, "bzz:sync_all",
                     "ok" if not _SYNC_STATE["errors"] else "partial",
                     _SYNC_STATE["players_written"],
                     f"clubs={_SYNC_STATE['clubs_written']} "
                     f"mapped={_SYNC_STATE['mapped_clubs']} "
                     f"players={_SYNC_STATE['players_written']}")
        finally:
            db.close()


def start_sync_all():
    if _SYNC_STATE["running"]:
        return {"ok": False, "error": "Already running. Stop first."}
    t = threading.Thread(target=_run_sync_all, daemon=True)
    t.start()
    return {"ok": True, "message": "Sync started in background. Poll /api/admin/bzz-progress for status."}