import re
import requests
from bs4 import BeautifulSoup

PPOMPPU_URL = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu&hotlist_flag=999"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.ppomppu.co.kr/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def extract_post_id(url: str):
    match = re.search(r"[?&]no=(\d+)", url)
    return match.group(1) if match else None


def is_notice_title(title: str) -> bool:
    keywords = [
        "이용규칙",
        "이용 규칙",
        "키워드 알림",
        "공지",
    ]
    return any(keyword in title for keyword in keywords)


def get_ppomppu_posts(limit=10):
    response = requests.get(PPOMPPU_URL, headers=HEADERS, timeout=10)
    response.encoding = "euc-kr"
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    posts = []
    seen_ids = set()

    for a_tag in soup.select("a"):
        href = a_tag.get("href", "").strip()
        title = a_tag.get_text(" ", strip=True)

        if not href or not title:
            continue

        # 실제 게시글만 통과
        if "view.php" not in href:
            continue

        if "id=ppomppu" not in href:
            continue

        if "no=" not in href:
            continue

        # 규칙/공지 게시판 제외
        if "id=regulation" in href or "id=notice" in href:
            continue

        if is_notice_title(title):
            continue

        if href.startswith("http"):
            url = href
        elif href.startswith("/"):
            url = "https://www.ppomppu.co.kr" + href
        else:
            url = "https://www.ppomppu.co.kr/zboard/" + href

        post_id = extract_post_id(url)
        if not post_id:
            continue

        if post_id in seen_ids:
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