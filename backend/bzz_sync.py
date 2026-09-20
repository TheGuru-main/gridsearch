"""
Bzzoiro sync — single league OR all leagues, with registry mapping.
Progress persists to DB so the sync survives Render restarts.

API reference: https://sports.bzzoiro.com/docs/football/teams-players/
"""
import os
import time
import json
import threading
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync
from registry_map import match_tournament, match_club, canonical_club_id
from models import SyncState
from sqlalchemy import text

BASE = "https://sports.bzzoiro.com/api/v2"

SKIP_TOKENS = [
    "qualification", "qualifier",
    "women", "womens", "ladies",
    "under", "u18", "u19", "u20", "u21", "u23",
    "youth", "academy", "primavera", "junioren", "jugend",
    "friendly", "friendlies",
    "reserve", " ii ", " b team",
]


# ═══════════════════════════════════════════════════════
#  STATE HELPERS (persisted to DB)
# ═══════════════════════════════════════════════════════
def _load_state(db) -> SyncState:
    s = db.get(SyncState, "bzz_all")
    if not s:
        s = SyncState(
            id="bzz_all", running=0, current_index=0, total_leagues=0,
            candidate_ids="[]", completed_ids="[]",
            clubs_written=0, players_written=0, mapped_clubs=0,
            unmapped_clubs=0, errors="[]",
            started_at=0, updated_at=time.time(),
        )
        db.add(s)
        db.commit()
    return s


def _is_running() -> bool:
    db = SessionLocal()
    try:
        s = _load_state(db)
        return bool(s.running)
    finally:
        db.close()


def get_state() -> dict:
    """Read current sync status from DB."""
    db = SessionLocal()
    try:
        s = _load_state(db)
        completed = json.loads(s.completed_ids or "[]")
        errors = json.loads(s.errors or "[]")

        # Build a name map from candidates
        candidates = json.loads(s.candidate_ids or "[]")
        name_map = {c["id"]: c.get("name", "") for c in candidates}

        return {
            "running": bool(s.running),
            "started_at": s.started_at or 0,
            "finished_at": 0,
            "current_index": s.current_index or 0,
            "total_leagues": s.total_leagues or 0,
            "current_league_id": None,
            "current_league_name": None,
            "current_registry_match": None,
            "leagues_completed": [
                {"id": i, "name": name_map.get(i, "")} for i in completed
            ],
            "leagues_skipped": [],
            "clubs_written": s.clubs_written or 0,
            "players_written": s.players_written or 0,
            "mapped_clubs": s.mapped_clubs or 0,
            "unmapped_clubs": s.unmapped_clubs or 0,
            "errors": errors,
            "mode": "all" if s.running else "idle",
        }
    finally:
        db.close()


def stop_sync():
    db = SessionLocal()
    try:
        s = _load_state(db)
        s.running = 0
        s.updated_at = time.time()
        db.commit()
        return {"ok": True, "message": "Stop requested."}
    finally:
        db.close()


# ═══════════════════════════════════════════════════════
#  HTTP + UTILS
# ═══════════════════════════════════════════════════════
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
    """GET /api/v2/leagues/ — paginated."""
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
    """GET /api/v2/leagues/{id}/ — returns name or ''."""
    try:
        r = client.get(f"{BASE}/leagues/{league_id}/")
        if r.status_code == 200:
            return (r.json() or {}).get("name") or ""
    except Exception:
        pass
    return ""


def _dedup_old_club_membership(db, player_name):
    """
    If a TM-sourced player with this name exists, delete it.
    Prevents the same player showing in old and new clubs after a transfer.
    """
    if not player_name:
        return
    db.execute(text("""
        DELETE FROM players
        WHERE name = :n AND id LIKE 'tm:%'
    """), {"n": player_name})


# ═══════════════════════════════════════════════════════
#  SYNC ONE LEAGUE
# ═══════════════════════════════════════════════════════
def sync_league(league_id: int, league_name: str = None,
                silent: bool = False) -> dict:
    """
    Sync one Bzzoiro league:
    1. GET /api/v2/teams/?league_id=N   → club rows
    2. GET /api/v2/teams/{id}/squad/    → player rows
    """
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set"}

    stats = {"league_id": league_id, "league_name": league_name,
             "registry_match": None,
             "clubs": 0, "players": 0,
             "mapped": 0, "unmapped": 0,
             "errors": [], "teams": []}

    # Fetch league name if not provided
    if not league_name:
        with httpx.Client(timeout=15, headers=h) as probe:
            league_name = _fetch_league_name(probe, league_id)
            stats["league_name"] = league_name

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

        # ── Clubs ──
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
                        pname = p.get("name") or ""
                        # Prevent old-club duplicates after transfers
                        _dedup_old_club_membership(db, pname)

                        upsert_player(db, {
                            "id": f"{canonical}:{pid}",
                            "name": pname,
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


# ═══════════════════════════════════════════════════════
#  SYNC ALL — resumable, DB-persisted
# ═══════════════════════════════════════════════════════
def _run_sync_all(resume: bool = False):
    """
    Walk every active Bzzoiro league.
    Progress is written to sync_state after each league, so a Render restart
    does not lose ground. On boot, app.py calls this with resume=True.
    """
    db = SessionLocal()
    try:
        s = _load_state(db)

        if s.running and not resume:
            return {"ok": False, "error": "Already running. Stop it first."}

        s.running = 1
        if not resume or not s.started_at:
            s.started_at = time.time()
            s.completed_ids = "[]"
            s.candidate_ids = "[]"
            s.clubs_written = 0
            s.players_written = 0
            s.mapped_clubs = 0
            s.unmapped_clubs = 0
            s.errors = "[]"
            s.current_index = 0
        s.updated_at = time.time()
        db.commit()

        # ── Build candidate list (only on fresh run) ──
        candidates = json.loads(s.candidate_ids or "[]")
        if not candidates:
            h = _h()
            if not h:
                s.running = 0
                s.errors = json.dumps(["BZZOIRO_TOKEN not set"])
                db.commit()
                return {"ok": False, "error": "BZZOIRO_TOKEN not set"}

            with httpx.Client(timeout=30, headers=h) as c:
                all_leagues = _fetch_all_leagues(c)

            for lg in all_leagues:
                if not lg.get("is_active") or not lg.get("current_season"):
                    continue
                name = lg.get("name") or ""
                if _should_skip_league(name):
                    continue
                candidates.append({"id": lg["id"], "name": name})

            s.candidate_ids = json.dumps(candidates)
            s.total_leagues = len(candidates)
            db.commit()

        completed = set(json.loads(s.completed_ids or "[]"))
        db.close()

        # ── Iterate ──
        for idx, lg in enumerate(candidates):
            if lg["id"] in completed:
                continue

            # Re-read state (allows external stop)
            check = SessionLocal()
            try:
                st = check.get(SyncState, "bzz_all")
                if not st or st.running == 0:
                    check.close()
                    return {"ok": True, "stopped": True}
                st.current_index = idx + 1
                st.updated_at = time.time()
                check.commit()
            finally:
                check.close()

            try:
                stats = sync_league(lg["id"], lg.get("name"), silent=True)
                completed.add(lg["id"])

                upd = SessionLocal()
                try:
                    st = upd.get(SyncState, "bzz_all")
                    st.completed_ids = json.dumps(list(completed))
                    st.clubs_written = (st.clubs_written or 0) + stats.get("clubs", 0)
                    st.players_written = (st.players_written or 0) + stats.get("players", 0)
                    st.mapped_clubs = (st.mapped_clubs or 0) + stats.get("mapped", 0)
                    st.unmapped_clubs = (st.unmapped_clubs or 0) + stats.get("unmapped", 0)
                    if stats.get("errors"):
                        errs = json.loads(st.errors or "[]")
                        errs.extend(stats["errors"][:2])
                        st.errors = json.dumps(errs[-50:])
                    st.updated_at = time.time()
                    upd.commit()
                finally:
                    upd.close()
            except Exception as e:
                upd = SessionLocal()
                try:
                    st = upd.get(SyncState, "bzz_all")
                    errs = json.loads(st.errors or "[]")
                    errs.append(f"{lg.get('name')}: {e}")
                    st.errors = json.dumps(errs[-50:])
                    st.updated_at = time.time()
                    upd.commit()
                finally:
                    upd.close()

        # ── All done ──
        fin = SessionLocal()
        try:
            st = fin.get(SyncState, "bzz_all")
            st.running = 0
            st.current_index = st.total_leagues
            st.updated_at = time.time()
            fin.commit()
            log_sync(fin, "bzz:sync_all", "ok", st.players_written,
                     f"leagues={len(completed)} clubs={st.clubs_written} "
                     f"players={st.players_written}")
        finally:
            fin.close()

        return {"ok": True, "completed": len(completed)}

    finally:
        try:
            db.close()
        except Exception:
            pass


def start_sync_all():
    if _is_running():
        return {"ok": False, "error": "Already running. Stop first."}
    t = threading.Thread(target=_run_sync_all, daemon=True)
    t.start()
    return {"ok": True, "message": "Sync started in background. Poll /api/admin/bzz-progress for status."}