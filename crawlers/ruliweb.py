import re
import requests
from bs4 import BeautifulSoup

RULIWEB_URL = "https://bbs.ruliweb.com/market/board/1020?view_best=1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Referer": "https://bbs.ruliweb.com/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def extract_post_id(url: str):
    match = re.search(r"/read/(\d+)", url)
    return match.group(1) if match else None


def get_ruliweb_posts(limit=10):
    response = requests.get(RULIWEB_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    posts = []
    seen_ids = set()

    # 루리웹 게시글 제목 링크
    for a_tag in soup.select("a.deco"):
        href = a_tag.get("href", "").strip()
        title = a_tag.get_text(" ", strip=True)

        if not href or not title:
            continue

        if "/market/board/1020/read/" not in href:
            continue

        if href.startswith("/"):
            url = "https://bbs.ruliweb.com" + href
        elif href.startswith("http"):
            url = href
        else:
            continue

        post_id = extract_post_id(url)
        if not post_id:
            continue

        if post_id in seen_ids:
            continue

        # 공지/베스트성 텍스트 제거용 최소 필터
        if "공지" in title:
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