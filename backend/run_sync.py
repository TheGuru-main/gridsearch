"""
Full sync entry point. Run from Render Cron Job every 6 hours.
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import init_db
from sportmonks_sync import run as sm_run
from wikipedia_transfers import run as wiki_run
from rss_transfers import run as rss_run


async def main():
    print("=== init DB ===")
    init_db()
    print("=== SportMonks ===")
    await sm_run()
    print("=== Wikipedia ===")
    wiki_run()
    print("=== RSS ===")
    rss_run()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())