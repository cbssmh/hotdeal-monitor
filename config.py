import json
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITES_FILE = os.path.join(BASE_DIR, "sites.json")

def load_sites():
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)