import json
import os
from datetime import datetime, timezone

from config import BASE_DIR

STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "seen_posts.json")
STATE_VERSION = 1


def empty_state():
    return {
        "version": STATE_VERSION,
        "sites": {},
    }


def load_state():
    if not os.path.exists(STATE_PATH):
        return empty_state()

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    state.setdefault("version", STATE_VERSION)
    state.setdefault("sites", {})
    return state


def has_seen_ids(state, site_name):
    return bool(state.get("sites", {}).get(site_name, {}).get("seen_ids", {}))


def has_post(state, site_name, post_id):
    seen_ids = state.get("sites", {}).get(site_name, {}).get("seen_ids", {})
    return str(post_id) in seen_ids


def save_post(state, site_name, post):
    site_state = state.setdefault("sites", {}).setdefault(site_name, {})
    seen_ids = site_state.setdefault("seen_ids", {})
    post_id = str(post["id"])

    if post_id in seen_ids:
        return False

    seen_ids[post_id] = {
        "title": post["title"],
        "url": post["url"],
        "first_seen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    return True


def save_posts(state, site_name, posts):
    changed = False
    for post in posts:
        if save_post(state, site_name, post):
            changed = True
    return changed


def write_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp_path = f"{STATE_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp_path, STATE_PATH)
