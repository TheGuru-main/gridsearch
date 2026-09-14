"""
Bzzoiro sync — single league OR all leagues, with progress tracking.
Free token: sports.bzzoiro.com/register
"""
import os
import time
import threading
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

BASE = "https://sports.bzzoiro.com/api/v2"

# Skip leagues whose names match these
SKIP_TOKENS = [
    "qualification", "cup", "women", "under", "u18", "u19", "u20",
    "u21", "u23", "youth", "academy", "playoff", "play-off",
    "friendly", "friendlies",
]

# Module-level state for background sync
_SYNC_STATE = {
    "running": False,
    "stop_requested": False,
    "started_at": 0,
    "finished_at": 0,
    "total_leagues": 0,
    "current_index": 0,
    "current_league_id": None,
    "current_league_name": None,
    "leagues_completed": [],
    "leagues_skipped": [],
    "clubs_written": 0,
    "players_written": 0,
    "errors": [],
    "mode": "idle",  # "idle" | "all" | "one"
}


def get_state() -> dict:
    return dict(_SYNC_STATE)


def stop_sync():
    _SYNC_STATE["stop_requested"] = True
    return {"ok": True, "message": "Stop requested. Finishing current team..."}


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


def _fetch_all_leagues(client: httpx.Client) -> list:
    """Paginate through /api/v2/leagues/ and return all."""
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


def sync_league(league_id: int, silent: bool = False) -> dict:
    """Sync one league. Returns stats. Used by both single and all-sync."""
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set on Render"}

    stats = {"league_id": league_id, "clubs": 0, "players": 0,
             "errors": [], "teams": []}
    key = f"bzz_{league_id}"

    with httpx.Client(timeout=30, headers=h) as c:
        # Teams
        url = f"{BASE}/teams/"
        params = {"league_id": league_id, "limit": 100}
        teams = []
        while url and len(teams) < 500:
            r = c.get(url, params=params)
            if r.status_code != 200:
                stats["errors"].append(f"teams HTTP {r.status_code}")
                break
            body = r.json()
            teams.extend(_extract_list(body))
            url = body.get("next") if isinstance(body, dict) else None
            params = None
            time.sleep(0.15)

        if not teams:
            stats["errors"].append("no teams returned")
            return stats

        # Clubs
        db = SessionLocal()
        try:
            for i, t in enumerate(teams):
                upsert_club(db, {
                    "id": f"{key}:{t.get('id')}",
                    "tournament_id": key,
                    "name": t.get("name") or "",
                    "country": t.get("country") or "",
                    "col": i,
                })
                stats["clubs"] += 1
            db.commit()
        finally:
            db.close()

        # Squads
        for t in teams:
            if _SYNC_STATE["stop_requested"]:
                break
            tid = t.get("id")
            tname = t.get("name") or f"team-{tid}"
            if not tid:
                continue
            try:
                time.sleep(0.15)
                r = c.get(f"{BASE}/teams/{tid}/squad/")
                if r.status_code != 200:
                    stats["teams"].append({"team": tname, "status": r.status_code})
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
                            "id": f"{key}:{tid}:{pid}",
                            "name": p.get("name") or "",
                            "position": _pos(p.get("position")),
                            "club_id": f"{key}:{tid}",
                            "tournament_id": key,
                            "number": p.get("shirt_number"),
                            "nationality": p.get("nationality") or p.get("nationality_code"),
                            "market_value": p.get("market_value"),
                            "photo_url": p.get("image_url"),
                        })
                    db.commit()
                    stats["players"] += len(squad)
                    stats["teams"].append({"team": tname, "players": len(squad)})
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{tname}: {e}")

    if not silent:
        db = SessionLocal()
        try:
            log_sync(db, f"bzz:{league_id}",
                     "ok" if not stats["errors"] else "partial",
                     stats["players"], "; ".join(stats["errors"][:2]))
        finally:
            db.close()

    stats["ok"] = not stats["errors"]
    return stats


def _run_sync_all():
    """Background thread: sync every league one by one."""
    _SYNC_STATE["running"] = True
    _SYNC_STATE["stop_requested"] = False
    _SYNC_STATE["started_at"] = time.time()
    _SYNC_STATE["finished_at"] = 0
    _SYNC_STATE["leagues_completed"] = []
    _SYNC_STATE["leagues_skipped"] = []
    _SYNC_STATE["clubs_written"] = 0
    _SYNC_STATE["players_written"] = 0
    _SYNC_STATE["errors"] = []
    _SYNC_STATE["mode"] = "all"

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

        # Filter: keep domestic leagues with a current season
        candidates = []
        for lg in all_leagues:
            if not lg.get("is_active"):
                continue
            if not lg.get("current_season"):
                continue
            name = lg.get("name") or ""
            if _should_skip_league(name):
                _SYNC_STATE["leagues_skipped"].append(
                    {"id": lg.get("id"), "name": name, "reason": "filtered"}
                )
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
                stats = sync_league(lg["id"], silent=True)
                _SYNC_STATE["clubs_written"] += stats.get("clubs", 0)
                _SYNC_STATE["players_written"] += stats.get("players", 0)
                _SYNC_STATE["leagues_completed"].append({
                    "id": lg["id"],
                    "name": lg.get("name"),
                    "clubs": stats.get("clubs", 0),
                    "players": stats.get("players", 0),
                    "errors": stats.get("errors", [])[:3],
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
                     f"leagues={len(_SYNC_STATE['leagues_completed'])} "
                     f"clubs={_SYNC_STATE['clubs_written']} "
                     f"players={_SYNC_STATE['players_written']}")
        finally:
            db.close()


def start_sync_all() -> dict:
    """Launch background sync. Returns immediately."""
    if _SYNC_STATE["running"]:
        return {"ok": False, "error": "Already running. Stop it first."}
    t = threading.Thread(target=_run_sync_all, daemon=True)
    t.start()
    return {"ok": True, "message": "Sync started in background. Poll /api/admin/bzz-progress for status."}