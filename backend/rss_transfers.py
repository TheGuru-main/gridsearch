import feedparser
from datetime import datetime
from database import SessionLocal, init_db
from storage import insert_transfer, log_sync

FEEDS = [
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
]

KEYWORDS = ["signs", "joins", "loan", "transfer", "move to", "completed"]


def run():
    init_db()
    db = SessionLocal()
    try:
        total = 0
        for url in FEEDS:
            try:
                feed = feedparser.parse(url)
                added = 0
                for entry in feed.entries[:80]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    text = f"{title} {summary}".lower()
                    if not any(k in text for k in KEYWORDS):
                        continue
                    if insert_transfer(db, {
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
                        added += 1
                db.commit()
                total += added
                log_sync(db, f"rss:{url}", "ok", added)
            except Exception as e:
                db.rollback()
                print(f"[rss] {url} failed: {e}")
        return total
    finally:
        db.close()