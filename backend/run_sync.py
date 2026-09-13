"""
Full sync: SportMonks (primary) → Wikipedia (fallback) → RSS (rumors).
Run every 6 hours via cron / Render cron job.
"""
import asyncio
from storage import init_db
from sportmonks_sync import run as sm_run
from wikipedia_transfers import run as wiki_run
from rss_transfers import run as rss_run


async def main():
    conn = init_db()
    print("=== SportMonks ===")
    await sm_run(conn)
    print("=== Wikipedia ===")
    wiki_run(conn)
    print("=== RSS ===")
    rss_run(conn)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())