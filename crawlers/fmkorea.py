import re
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

FMKOREA_MOBILE_URL = "https://m.fmkorea.com/index.php?mid=hotdeal&order_type=desc&sort_index=pop"
BASE_URL = "https://m.fmkorea.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Referer": "https://m.fmkorea.com/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Connection": "keep-alive",
}

session = requests.Session()
session.headers.update(HEADERS)


def extract_document_srl(href: str):
    match = re.search(r"[?&]document_srl=(\d+)", href)
    return match.group(1) if match else None


def is_notice_title(text: str) -> bool:
    notice_keywords = [
        "통합공지",
        "게시판 통합공지",
        "금지",
        "공지",
    ]
    return any(keyword in text for keyword in notice_keywords)


def is_valid_post_link(href: str, text: str) -> bool:
    text = text.strip()

    if not href or not text:
        return False

    if "document_srl=" not in href:
        return False

    if "search_target=title" in href:
        return False

    if is_notice_title(text):
        return False

    return True


def fetch_page():
    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.5))
            response = session.get(FMKOREA_MOBILE_URL, timeout=10)

            if response.status_code in (429, 430):
                print(f"[WARN] FM코리아 차단 응답: {response.status_code}")
                time.sleep(3 + attempt * 2)
                continue

            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            print(f"[WARN] FM코리아 요청 실패 (시도 {attempt + 1}/3): {e}")
            time.sleep(3 + attempt * 2)

    return None


def get_fmkorea_posts(limit=10):
    html = fetch_page()
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    posts = []
    seen_ids = set()

    candidate_links = soup.select("a[href*='document_srl=']")

    for a_tag in candidate_links:
        href = a_tag.get("href", "").strip()
        text = a_tag.get_text(" ", strip=True)

        if not is_valid_post_link(href, text):
            continue

        post_id = extract_document_srl(href)
        if not post_id:
            continue

        if post_id in seen_ids:
            continue

        url = urljoin(BASE_URL, href)

        seen_ids.add(post_id)
        posts.append({
            "id": post_id,
            "title": text,
            "url": url,
        })

        if len(posts) >= limit:
            break

    return posts
