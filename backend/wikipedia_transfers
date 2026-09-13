"""
Wikipedia fallback. Pages like:
  https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2026
  https://en.wikipedia.org/wiki/List_of_Spanish_football_transfers_summer_2026
  ... etc.

These pages are well-formatted HTML tables. We parse and store.
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from storage import insert_transfer, log_sync

WIKI_PAGES = {
    "epl":       "List_of_English_football_transfers_summer_2026",
    "laliga":    "List_of_Spanish_football_transfers_summer_2026",
    "seriea":    "List_of_Italian_football_transfers_summer_2026",
    "bundes":    "List_of_German_football_transfers_summer_2026",
    "ligue1":    "List_of_French_football_transfers_summer_2026",
    "portugal":  "List_of_Portuguese_football_transfers_summer_2026",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OpenBoxBot/1.0)"}


def parse_wiki_tables(html: str, tournament: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for table in soup.select("table.wikitable"):
        for row in table.select("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 4:
                continue
            # Common format: Player | From | To | Fee
            player, from_club, to_club, fee = cells[0], cells[1], cells[2], cells[3]
            if not player or len(player) > 80:
                continue
            out.append({
                "player_name": player,
                "from_club": from_club,
                "to_club": to_club,
                "fee": fee,
                "transfer_type": "permanent",
                "date": datetime.utcnow().date().isoformat(),
                "source": "wikipedia",
                "source_url": f"https://en.wikipedia.org/wiki/{WIKI_PAGES[tournament]}",
                "tournament_hint": tournament,
            })
    return out


def run(conn):
    total = 0
    for tournament, page in WIKI_PAGES.items():
        url = f"https://en.wikipedia.org/wiki/{page}"
        try:
            r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
            if r.status_code != 200:
                print(f"[wikipedia] {tournament}: HTTP {r.status_code}")
                continue
            rows = parse_wiki_tables(r.text, tournament)
            added = sum(1 for row in rows if insert_transfer(conn, row))
            total += added
            print(f"[wikipedia] {tournament}: +{added} new")
        except Exception as e:
            print(f"[wikipedia] {tournament} failed: {e}")
    log_sync(conn, "wikipedia:transfers", "ok", total)