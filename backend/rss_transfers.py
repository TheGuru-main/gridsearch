"""
RSS fallback for late-breaking transfers. BBC + Sky.
"""
import feedparser
from datetime import datetime
from storage import insert_transfer, log_sync

FEEDS = [
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",  # football news
]

KEYWORDS = ["signs", "joins", "loan", "transfer", "move to", "completed"]


def run(conn):
    total = 0
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:80]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                text = f"{title} {summary}".lower()
                if not any(k in text for k in KEYWORDS):
                    continue
                # Very light extraction; real parsing is fuzzy here
                if insert_transfer(conn, {
                    "player_name": title[:120],
                    "from_club": None,
                    "to_club": None,
                    "fee": None,
                    "transfer_type": "rumor",
                    "date": datetime.utcnow().date().isoformat(),
                    "source": "rss",
                    "source_url": entry.get("link"),
                    "tournament_hint": None,
                }):
                    total += 1
            log_sync(conn, f"rss:{url}", "ok", total)
        except Exception as e:
            print(f"[rss] {url} failed: {e}")
    return total