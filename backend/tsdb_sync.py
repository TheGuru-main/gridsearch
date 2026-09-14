"""
TheSportsDB sync. Free key '3'. No signup.
Two requests per team: search_all_teams, then lookup_all_players.
"""
import time
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

BASE = "https://www.thesportsdb.com/api/v1/json/3"


def sync_league(league_name: str) -> dict:
    stats = {"league": league_name, "clubs": 0, "players": 0, "errors": [], "teams": []}
    init_db()

    with httpx.Client(timeout=25) as c:
        # 1. Teams in league
        r = c.get(f"{BASE}/search_all_teams.php", params={"l": league_name})
        teams = (r.json().get("teams") or []) if r.status_code == 200 else []
        if not teams:
            stats["errors"].append(f"no teams for '{league_name}' (HTTP {r.status_code})")
            return stats

        # 2. Write clubs
        db = SessionLocal()
        try:
            league_key = league_name.lower().replace(" ", "_")[:20]
            for i, t in enumerate(teams):
                upsert_club(db, {
                    "id": f"{league_key}:{t['idTeam']}",
                    "tournament_id": league_key,
                    "name": t.get("strTeam") or "",
                    "country": t.get("strCountry") or "",
                    "col": i,
                })
                stats["clubs"] += 1
            db.commit()
        finally:
            db.close()

        # 3. Players per team
        for i, t in enumerate(teams):
            team_name = t.get("strTeam") or f"team-{t['idTeam']}"
            try:
                time.sleep(2.1)  # TheSportsDB: 30 req/min free
                r = c.get(f"{BASE}/lookup_all_players.php", params={"id": t["idTeam"]})
                if r.status_code != 200:
                    stats["teams"].append({"team": team_name, "status": r.status_code})
                    continue
                players = r.json().get("player") or []
                db = SessionLocal()
                try:
                    for p in players:
                        pid = p.get("idPlayer")
                        if not pid: continue
                        upsert_player(db, {
                            "id": f"{league_key}:{t['idTeam']}:{pid}",
                            "name": p.get("strPlayer") or "",
                            "position": p.get("strPosition"),
                            "club_id": f"{league_key}:{t['idTeam']}",
                            "tournament_id": league_key,
                            "number": None,
                            "nationality": p.get("strNationality"),
                            "market_value": None,
                            "photo_url": p.get("strThumb"),
                        })
                    db.commit()
                    stats["players"] += len(players)
                    stats["teams"].append({"team": team_name, "players": len(players)})
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{team_name}: {e}")

    db = SessionLocal()
    try:
        log_sync(db, f"tsdb:{league_name}", "ok" if not stats["errors"] else "partial",
                 stats["players"], "; ".join(stats["errors"][:2]))
    finally:
        db.close()
    stats["ok"] = not stats["errors"]
    return stats