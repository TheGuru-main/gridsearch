"""
Bzzoiro sync — free token, no rate limits.
Squad endpoint returns {count, results:[...]} — paginated object.
"""
import os
import time
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

BASE = "https://sports.bzzoiro.com/api/v2"


def _h():
    tok = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {tok}"} if tok else {}


def _pos(code):
    c = (code or "").upper()[:1]
    return {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}.get(c, "MID")


def _extract_list(payload):
    """Squad endpoint returns {count, results}. Team list also {count, results}.
       Handle both a raw list and a paginated object defensively."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("results"), list):
            return payload["results"]
        # fallback: any list value
        for v in payload.values():
            if isinstance(v, list):
                return v
    return []


def sync_league(league_id: int) -> dict:
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set on Render"}

    stats = {"league_id": league_id, "clubs": 0, "players": 0,
             "errors": [], "teams": []}
    init_db()
    key = f"bzz_{league_id}"

    with httpx.Client(timeout=30, headers=h) as c:
        # ─── Teams in league (paginated) ───
        url = f"{BASE}/teams/"
        params = {"league_id": league_id, "limit": 100}
        teams = []
        while url and len(teams) < 500:
            r = c.get(url, params=params)
            if r.status_code != 200:
                stats["errors"].append(f"teams HTTP {r.status_code}: {r.text[:200]}")
                break
            teams.extend(_extract_list(r.json()))
            next_url = (r.json() or {}).get("next") if isinstance(r.json(), dict) else None
            url = next_url
            params = None
            time.sleep(0.2)

        if not teams:
            stats["errors"].append(f"no teams returned for league {league_id}")
            return stats

        # ─── Write clubs ───
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

        # ─── Squads (one call per team) ───
        for t in teams:
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

    db = SessionLocal()
    try:
        log_sync(db, f"bzz:{league_id}",
                 "ok" if not stats["errors"] else "partial",
                 stats["players"], "; ".join(stats["errors"][:2]))
    finally:
        db.close()
    stats["ok"] = not stats["errors"]
    return stats