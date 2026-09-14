"""
Bzzoiro sync — free token, no rate limits.
Register: sports.bzzoiro.com/register
Set env var BZZOIRO_TOKEN on Render.
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


def sync_league(league_id: int) -> dict:
    h = _h()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set on Render"}

    stats = {"league_id": league_id, "clubs": 0, "players": 0,
             "errors": [], "teams": []}
    init_db()
    key = f"bzz_{league_id}"

    with httpx.Client(timeout=30, headers=h) as c:
        # Teams in league — paginate
        url = f"{BASE}/teams/"
        params = {"league_id": league_id, "limit": 100}
        teams = []
        while url and len(teams) < 500:
            r = c.get(url, params=params)
            if r.status_code != 200:
                stats["errors"].append(f"teams HTTP {r.status_code}: {r.text[:200]}")
                break
            body = r.json()
            teams.extend(body.get("results") or [])
            url = body.get("next")
            params = None  # next already has params
            time.sleep(0.2)

        if not teams:
            stats["errors"].append(f"no teams returned for league {league_id}")
            return stats

        # Write clubs
        db = SessionLocal()
        try:
            for i, t in enumerate(teams):
                upsert_club(db, {
                    "id": f"{key}:{t['id']}",
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
            try:
                time.sleep(0.15)
                r = c.get(f"{BASE}/teams/{t['id']}/squad/")
                if r.status_code != 200:
                    stats["teams"].append({"team": t.get("name"),
                                           "status": r.status_code})
                    continue
                squad = r.json() or []
                db = SessionLocal()
                try:
                    for p in squad:
                        pid = p.get("id")
                        if not pid:
                            continue
                        upsert_player(db, {
                            "id": f"{key}:{t['id']}:{pid}",
                            "name": p.get("name") or "",
                            "position": _pos(p.get("position")),
                            "club_id": f"{key}:{t['id']}",
                            "tournament_id": key,
                            "number": p.get("shirt_number"),
                            "nationality": p.get("nationality"),
                            "market_value": p.get("market_value"),
                            "photo_url": p.get("image_url"),
                        })
                    db.commit()
                    stats["players"] += len(squad)
                    stats["teams"].append({"team": t.get("name"),
                                           "players": len(squad)})
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{t.get('name')}: {e}")

    db = SessionLocal()
    try:
        log_sync(db, f"bzz:{league_id}",
                 "ok" if not stats["errors"] else "partial",
                 stats["players"], "; ".join(stats["errors"][:2]))
    finally:
        db.close()
    stats["ok"] = not stats["errors"]
    return stats