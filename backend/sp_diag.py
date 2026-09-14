"""
SportMonks v3 sync — one league at a time.
Rate-limited to 1 request/second to stay under free-tier limits.
Returns rich stats so we can see exactly what happened.
"""
import time
import httpx
from database import SessionLocal, init_db
from storage import upsert_club, upsert_player, log_sync

SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"


def _token():
    import os
    return os.environ.get("SPORTMONKS_KEY", "")


def sp_raw_league(league_id: int):
    """Diagnostic: fetch one league and return the raw JSON."""
    tok = _token()
    if not tok:
        return {"error": "SPORTMONKS_KEY not set"}
    with httpx.Client(timeout=25) as c:
        r = c.get(
            f"{SPORTMONKS_BASE}/leagues/{league_id}",
            params={"api_token": tok, "include": "currentSeason;country"},
        )
    try:
        body = r.json()
    except Exception:
        body = {"_raw": r.text[:500]}
    return {"status": r.status_code, "body": body}


def sp_find_league(query: str):
    """Search SportMonks for a league by name. Useful to find correct IDs."""
    tok = _token()
    if not tok:
        return {"error": "SPORTMONKS_KEY not set"}
    with httpx.Client(timeout=25) as c:
        r = c.get(
            f"{SPORTMONKS_BASE}/leagues",
            params={"api_token": tok, "search": query, "per_page": 15},
        )
    try:
        data = r.json().get("data") or []
    except Exception:
        return {"status": r.status_code, "raw": r.text[:500]}
    return {
        "status": r.status_code,
        "results": [
            {"id": x.get("id"), "name": x.get("name"),
             "country": (x.get("country") or {}).get("name"),
             "type": x.get("type")}
            for x in data
        ],
    }


def sync_one_league(league_key: str, league_id: int):
    """
    Pull clubs + players for one league.
    Returns stats and a per-team log.
    """
    tok = _token()
    if not tok:
        return {"ok": False, "error": "SPORTMONKS_KEY not set"}

    init_db()
    stats = {
        "league": league_key,
        "league_id": league_id,
        "clubs_written": 0,
        "players_written": 0,
        "teams": [],
        "errors": [],
    }

    with httpx.Client(timeout=30) as c:
        # ─── 1. League + current season ───
        r = c.get(
            f"{SPORTMONKS_BASE}/leagues/{league_id}",
            params={"api_token": tok, "include": "currentSeason;country"},
        )
        if r.status_code != 200:
            stats["errors"].append(f"league fetch HTTP {r.status_code}: {r.text[:200]}")
            return stats

        league = r.json().get("data") or {}
        season = league.get("currentseason") or {}
        season_id = season.get("id")
        season_name = season.get("name")
        stats["season_id"] = season_id
        stats["season_name"] = season_name

        if not season_id:
            stats["errors"].append("no current season for this league")
            return stats

        # ─── 2. Teams in season ───
        r = c.get(
            f"{SPORTMONKS_BASE}/teams/seasons/{season_id}",
            params={"api_token": tok},
        )
        if r.status_code != 200:
            stats["errors"].append(f"teams fetch HTTP {r.status_code}: {r.text[:200]}")
            return stats

        teams = r.json().get("data") or []
        stats["team_count"] = len(teams)

        # Write clubs first
        db = SessionLocal()
        try:
            for i, team in enumerate(teams):
                upsert_club(db, {
                    "id": f"{league_key}:{team['id']}",
                    "tournament_id": league_key,
                    "name": team.get("name") or "",
                    "country": str(team.get("country_id") or ""),
                    "col": i,
                })
                stats["clubs_written"] += 1
            db.commit()
        except Exception as e:
            db.rollback()
            stats["errors"].append(f"club write: {e}")
        finally:
            db.close()

        # ─── 3. Squad per team (rate-limited) ───
        for i, team in enumerate(teams):
            team_name = team.get("name") or f"team-{team['id']}"
            try:
                time.sleep(1.1)  # ~54 req/min — safe under SportMonks free tier
                r = c.get(
                    f"{SPORTMONKS_BASE}/squads/teams/{team['id']}",
                    params={"api_token": tok, "include": "player;position"},
                )
                if r.status_code == 429:
                    stats["errors"].append(f"RATE LIMIT hit at team {i+1}/{len(teams)}")
                    break
                if r.status_code != 200:
                    stats["teams"].append({"team": team_name, "status": r.status_code})
                    continue

                squad = r.json().get("data") or []
                written = 0
                db = SessionLocal()
                try:
                    for entry in squad:
                        p = entry.get("player") or {}
                        pid = p.get("id")
                        if not pid:
                            continue
                        upsert_player(db, {
                            "id": f"{league_key}:{team['id']}:{pid}",
                            "name": p.get("display_name") or p.get("name") or "",
                            "position": (entry.get("position") or {}).get("name"),
                            "club_id": f"{league_key}:{team['id']}",
                            "tournament_id": league_key,
                            "number": entry.get("jersey_number"),
                            "nationality": str(p.get("nationality_id") or ""),
                            "market_value": None,
                            "photo_url": p.get("image_path"),
                        })
                        written += 1
                    db.commit()
                    stats["players_written"] += written
                    stats["teams"].append({"team": team_name, "players": written})
                except Exception as e:
                    db.rollback()
                    stats["teams"].append({"team": team_name, "error": str(e)})
                finally:
                    db.close()
            except Exception as e:
                stats["errors"].append(f"{team_name}: {e}")

    # Log the run
    db = SessionLocal()
    try:
        log_sync(
            db,
            f"sp:{league_key}",
            "ok" if not stats["errors"] else "partial",
            stats["players_written"],
            "; ".join(stats["errors"][:3]) or "clean",
        )
    finally:
        db.close()

    stats["ok"] = not stats["errors"]
    return stats