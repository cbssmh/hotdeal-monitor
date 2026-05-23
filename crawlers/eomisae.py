import re
import requests
from bs4 import BeautifulSoup

EOMISAE_URL = "https://eomisae.co.kr/fs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Referer": "https://eomisae.co.kr/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def extract_post_id(url: str):
    match = re.search(r"/(\d+)$", url.rstrip("/"))
    return match.group(1) if match else None


def is_notice_or_ad(title: str) -> bool:
    keywords = ["공지", "광고", "AD", "이벤트", "이용 규정", "게시판 이용 규정"]
    return any(keyword in title for keyword in keywords)


def get_eomisae_posts(limit=10):
    response = requests.get(EOMISAE_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    posts = []
    seen_ids = set()

    for a_tag in soup.select("a"):
        href = a_tag.get("href", "").strip()
        title = a_tag.get_text(" ", strip=True)

        if not href or not title:
            continue

        if "/fs/" not in href:
            continue

        # 카테고리 링크 제외
        if "/fs/category/" in href:
            continue

        if href.startswith("/"):
            url = "https://eomisae.co.kr" + href
        elif href.startswith("http"):
            url = href
        else:
            continue

        post_id = extract_post_id(url)
        if not post_id:
            continue

        if post_id in seen_ids:
            continue

        if is_notice_or_ad(title):
            continue

        seen_ids.add(post_id)
        posts.append({
            "id": post_id,
            "title": title,
            "url": url,
        })

        if len(posts) >= limit:
            break

    return posts