import os
import time
import threading
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync
from registry_map import match_tournament, match_club, canonical_club_id

BASE = "https://sports.bzzoiro.com/api/v2"

SKIP_TOKENS = ["qualification", "women", "under", "u18", "u19", "u20",
               "u21", "u23", "youth", "academy", "friendly", "friendlies"]

_SYNC_STATE = {
    "running": False, "stop_requested": False,
    "started_at": 0, "finished_at": 0,
    "total_leagues": 0, "current_index": 0,
    "current_league_id": None, "current_league_name": None,
    "leagues_completed": [], "leagues_skipped": [],
    "clubs_written": 0, "players_written": 0,
    "mapped_clubs": 0, "unmapped_clubs": 0,
    "errors": [], "mode": "idle",
}


def get_state():
    return dict(_SYNC_STATE)


def stop_sync():
    _SYNC_STATE["stop_requested"] = True
    return {"ok": True, "message": "Stop requested."}


def _h():
    tok = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {tok}"} if tok else {}


def _pos(code):
    c = (code or "").upper()[:1]
    return {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}.get(c, "MID")


def _extract_list(payload):
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


def sync_league(league_id: int, league_name: str = None, silent: bool = False) -> dict:
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set"}

    stats = {"league_id": league_id, "league_name": league_name,
             "clubs": 0, "players": 0, "mapped": 0, "unmapped": 0,
             "errors": [], "teams": []}

    # Resolve tournament key from name
    registry_tid = match_tournament(league_name) if league_name else None
    source_key = f"bzz_{league_id}"

    with httpx.Client(timeout=30, headers=h) as c:
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
            stats["errors"].append("no teams")
            return stats

        # Clubs — with mapping
        db = SessionLocal()
        try:
            for i, t in enumerate(teams):
                team_name = t.get("name") or ""
                # Resolve canonical club ID
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
        finally:
            db.close()

        # Squads — write players under the canonical club ID
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
                     f"mapped={stats['mapped']} unmapped={stats['unmapped']} "
                     f"players={stats['players']}")
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
                _SYNC_STATE["clubs_written"] += stats.get("clubs", 0)
                _SYNC_STATE["players_written"] += stats.get("players", 0)
                _SYNC_STATE["mapped_clubs"] += stats.get("mapped", 0)
                _SYNC_STATE["unmapped_clubs"] += stats.get("unmapped", 0)
                _SYNC_STATE["leagues_completed"].append({
                    "id": lg["id"], "name": lg.get("name"),
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
        return {"ok": False, "error": "Already running"}
    t = threading.Thread(target=_run_sync_all, daemon=True)
    t.start()
    return {"ok": True, "message": "Sync started"}