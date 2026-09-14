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
    "epl":       8,     # English Premier League
    "laliga":    564,   # La Liga
    "seriea":    384,   # Serie A
    "bundes":    82,    # Bundesliga
    "ligue1":    301,   # Ligue 1
    "eredivisie":72,    # Eredivisie
    "portugal":  462,   # Primeira Liga
    "turkey":    600,   # Süper Lig
    "brasileirao_a": 648,
    "argentina_primera": 636,
    "mls":       779,
    "saudi_pl":  944,
    "j1":        968,

    # NPFL, CAF, Egyptian, South African etc. may not be on SportMonks.
    # Run /api/admin/sp-find?q=nigeria to check.
}

USER_AGENT = "Mozilla/5.0 (compatible; OpenBoxBot/1.0)"