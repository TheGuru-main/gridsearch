"""
Pull squads and transfers from SportMonks into Postgres.
"""
import asyncio
import httpx
from typing import Dict
from database import SessionLocal, init_db
from config import SPORTMONKS_KEY, SPORTMONKS_BASE, LEAGUES
from storage import upsert_club, upsert_player, insert_transfer, log_sync


async def fetch_json(client: httpx.AsyncClient, url: str) -> Dict:
    r = await client.get(url, timeout=20)
    if r.status_code != 200:
        return {}
    return r.json()


async def sync_league(league_id: str, sm_id: int):
    print(f"[sportmonks] syncing {league_id}...")
    async with httpx.AsyncClient() as client:
        url = f"{SPORTMONKS_BASE}/teams/seasons/{sm_id}?api_token={SPORTMONKS_KEY}"
        data = await fetch_json(client, url)
        teams = data.get("data", [])
        print(f"  {len(teams)} teams")

        # Each league gets its own session so a failure mid-league doesn't corrupt others
        db = SessionLocal()
        try:
            for idx, team in enumerate(teams):
                club_id = f"{league_id}:{team['id']}"
                upsert_club(db, {
                    "id": club_id,
                    "tournament_id": league_id,
                    "name": team.get("name"),
                    "country": str(team.get("country_id") or ""),
                    "col": idx,
                })

                squad_url = (
                    f"{SPORTMONKS_BASE}/squads/teams/{team['id']}"
                    f"?api_token={SPORTMONKS_KEY}&include=player;position"
                )
                squad_data = await fetch_json(client, squad_url)
                squad = squad_data.get("data", [])
                for entry in squad:
                    p = entry.get("player") or {}
                    if not p:
                        continue
                    upsert_player(db, {
                        "id": f"{league_id}:{team['id']}:{p['id']}",
                        "name": p.get("display_name") or p.get("name"),
                        "position": (entry.get("position") or {}).get("name"),
                        "club_id": club_id,
                        "tournament_id": league_id,
                        "number": entry.get("jersey_number"),
                        "nationality": str(p.get("nationality_id") or ""),
                        "market_value": None,
                        "photo_url": p.get("image_path"),
                    })
                print(f"  {team['name']}: {len(squad)} players")
                await asyncio.sleep(0.2)

            db.commit()
            log_sync(db, f"sportmonks:{league_id}", "ok", len(teams))
        except Exception as e:
            db.rollback()
            print(f"[sportmonks] {league_id} DB error: {e}")
            log_sync(db, f"sportmonks:{league_id}", "error", 0, str(e))
        finally:
            db.close()


async def sync_transfers():
    print("[sportmonks] syncing transfers...")
    async with httpx.AsyncClient() as client:
        db = SessionLocal()
        try:
            total_added = 0
            for league_id, sm_id in LEAGUES.items():
                url = (
                    f"{SPORTMONKS_BASE}/transfers/seasons/{sm_id}"
                    f"?api_token={SPORTMONKS_KEY}"
                    f"&include=player;fromTeam;toTeam"
                )
                data = await fetch_json(client, url)
                transfers = data.get("data", [])
                added = 0
                for t in transfers:
                    player = t.get("player") or {}
                    from_team = t.get("fromteam") or {}
                    to_team = t.get("toteam") or {}
                    if not player.get("name"):
                        continue
                    ok = insert_transfer(db, {
                        "player_name": player["name"],
                        "from_club": from_team.get("name"),
                        "to_club": to_team.get("name"),
                        "fee": str(t.get("amount") or ""),
                        "transfer_type": t.get("type"),
                        "date": t.get("date"),
                        "source": "sportmonks",
                        "source_url": None,
                        "tournament_hint": league_id,
                    })
                    if ok:
                        added += 1
                db.commit()
                total_added += added
                print(f"  {league_id}: +{added} new transfers")
                await asyncio.sleep(0.3)
            log_sync(db, "sportmonks:transfers", "ok", total_added)
        except Exception as e:
            db.rollback()
            print(f"[sportmonks] transfers DB error: {e}")
            log_sync(db, "sportmonks:transfers", "error", 0, str(e))
        finally:
            db.close()


async def run():
    init_db()
    for league_id, sm_id in LEAGUES.items():
        try:
            await sync_league(league_id, sm_id)
        except Exception as e:
            print(f"[sportmonks] {league_id} failed: {e}")
    await sync_transfers()