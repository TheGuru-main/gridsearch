"""
Bzzoiro sync. Free token from sports.bzzoiro.com/register.
"""
import os, time
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

BASE = "https://sports.bzzoiro.com/api/v2"


def _headers():
    tok = os.environ.get("BZZOIRO_TOKEN", "")
    return {"Authorization": f"Token {tok}"} if tok else {}


def sync_league(league_id: int) -> dict:
    h = _headers()
    if not h:
        return {"ok": False, "error": "BZZOIRO_TOKEN not set on Render"}

    stats = {"league_id": league_id, "clubs": 0, "players": 0, "errors": [], "teams": []}
    init_db()

    with httpx.Client(timeout=25, headers=h) as c:
        # 1. Teams in league
        r = c.get(f"{BASE}/teams/", params={"league_id": league_id})
        teams = (r.json().get("results") or []) if r.status_code == 200 else []
        if not teams:
            stats["errors"].append(f"no teams (HTTP {r.status_code}): {r.text[:150]}")
            return stats

        league_key = f"bzz_{league_id}"

        # 2. Write clubs
        db = SessionLocal()
        try:
            for i, t in enumerate(teams):
                upsert_club(db, {
                    "id": f"{league_key}:{t['id']}",
                    "tournament_id": league_key,
                    "name": t.get("name") or "",
                    "country": t.get("country") or "",
                    "col": i,
                })
                stats["clubs"] += 1
            db.commit()
        finally:
            db.close()

        # 3. Squad per team
        for i, t in enumerate(teams):
            try:
                time.sleep(0.3)  # generous headroom
                r = c.get(f"{BASE}/teams/{t['id']}/squad/")
                if r.status_code != 200:
                    stats["teams"].append({"team": t.get("name"), "status": r.status_code})
                    continue
                squad = r.json().get("results") or r.json() or []
                db = SessionLocal()
                try:
                    for p in squad:
                        pid = p.get("id")
                        if not pid: continue
                        pos_code = (p.get("position") or "").upper()
                        pos_map = {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}
                        upsert_player(db, {
                            "id": f"{league_key}:{t['id']}:{pid}",
                            "name": p.get("name") or "",
                            "position": pos_map.get(pos_code, pos_code) or "MID",
                            "club_id": f"{league_key}:{t['id']}",
                            "tournament_id": league_key,
                            "number": p.get("shirt_number"),
                            "nationality": p.get("nationality"),
                            "market_value": p.get("market_value"),
                            "photo_url": p.get("image_url"),
                        })
                    db.commit()
                    stats["players"] += len(squad)
                    stats["teams"].append({"team": t.get("name"), "players": len(squad)})
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{t.get('name')}: {e}")

    db = SessionLocal()
    try:
        log_sync(db, f"bzz:{league_id}", "ok" if not stats["errors"] else "partial",
                 stats["players"], "; ".join(stats["errors"][:2]))
    finally:
        db.close()
    stats["ok"] = not stats["errors"]
    return stats