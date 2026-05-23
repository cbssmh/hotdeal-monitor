import re
import time
import requests
from config import DISCORD_WEBHOOK_URL

MAX_DISCORD_CONTENT_LENGTH = 1900
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_discord_text(value: str) -> str:
    value = str(value or "")
    value = CONTROL_CHARS_RE.sub("", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def truncate_discord_content(content: str) -> str:
    if len(content) <= MAX_DISCORD_CONTENT_LENGTH:
        return content
    return content[: MAX_DISCORD_CONTENT_LENGTH - 15] + "\n...(truncated)"


def send_discord_message(content: str):
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")

    content = truncate_discord_content(sanitize_discord_text(content))

    payload = {
        "content": content,
        "allowed_mentions": {"parse": []},
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

    if response.status_code == 429:
        try:
            retry_after = min(float(response.json().get("retry_after", 1)), 5)
        except (ValueError, TypeError):
            retry_after = 1

        time.sleep(retry_after)
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

    response.raise_for_status()


def format_post_message(site_label: str, post: dict) -> str:
    return (
        f"{sanitize_discord_text(site_label)}\n"
        f"{sanitize_discord_text(post['title'])}\n"
        f"{sanitize_discord_text(post['url'])}"
    )