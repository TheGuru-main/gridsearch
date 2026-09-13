import os
from dotenv import load_dotenv

load_dotenv()

SPORTMONKS_KEY = os.getenv("SPORTMONKS_KEY", "")
SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")  # optional Transfermarkt fallback

DB_PATH = "storage/transfers.db"
CACHE_DIR = "storage/cache"

# Leagues we track (SportMonks IDs)
LEAGUES = {
    "epl":     8,
    "laliga":  564,
    "seriea":  384,
    "bundes":  82,
    "ligue1":  301,
    "eredivisie": 72,
    "portugal": 462,
    "turkey":   600,
    "brasileirao_a": 648,
    "argentina_primera": 636,
    "mls":      779,
    "saudi_pl": 944,
    "npfl":     1005,   # verify against SportMonks
    "j1":       968,
}

USER_AGENT = "Mozilla/5.0 (compatible; OpenBoxBot/1.0)"