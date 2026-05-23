import time
from config import load_sites
from notifier import send_discord_message, format_post_message
from state_store import has_post, has_seen_ids, load_state, save_post, save_posts, write_state
from crawlers.fmkorea import get_fmkorea_posts
from crawlers.ruliweb import get_ruliweb_posts
from crawlers.eomisae import get_eomisae_posts
from crawlers.ppomppu import get_ppomppu_posts

CRAWLER_MAP = {
    "fmkorea": get_fmkorea_posts,
    "ruliweb": get_ruliweb_posts,
    "eomisae": get_eomisae_posts,
    "ppomppu": get_ppomppu_posts,
}


def deduplicate_posts(posts):
    deduped_posts = []
    seen_ids = set()

    for post in posts:
        post_id = str(post["id"])
        if post_id in seen_ids:
            continue

        seen_ids.add(post_id)
        deduped_posts.append(post)

    return deduped_posts


def main():
    state = load_state()
    state_changed = False
    sites = load_sites()

    print("[CHECK] 사이트 점검 시작")

    for site in sites:
        if not site.get("enabled", True):
            continue

        site_name = site["name"]
        site_label = site["label"]
        check_limit = site.get("check_limit", 10)

        crawler = CRAWLER_MAP.get(site_name)
        if not crawler:
            print(f"[SKIP] 크롤러 없음: {site_name}")
            time.sleep(1)
            continue

        print(f"\n===== {site_label} =====")

        try:
            posts = deduplicate_posts(crawler(limit=check_limit))
            print(f"수집 결과: {len(posts)}개")

            if not posts:
                print("[INFO] 수집 결과 없음")
                time.sleep(1)
                continue

            if not has_seen_ids(state, site_name):
                print("[INIT] 첫 실행으로 판단, 상태 저장만 진행")
                if save_posts(state, site_name, posts):
                    state_changed = True
                time.sleep(1)
                continue

            new_posts = []
            for post in posts:
                if not has_post(state, site_name, post["id"]):
                    new_posts.append(post)

            if not new_posts:
                print("[INFO] 새 글 없음")
            else:
                print(f"[NEW] 새 글 {len(new_posts)}개 발견")

                for post in reversed(new_posts):
                    print(post)
                    message = format_post_message(site_label, post)
                    try:
                        send_discord_message(message)
                        if save_post(state, site_name, post):
                            state_changed = True
                    except Exception as e:
                        print(f"[ERROR] Discord 알림 실패: {site_label} {post['id']}: {e}")

        except Exception as e:
            print(f"[ERROR] {site_label}: {e}")

        time.sleep(1)

    if state_changed:
        write_state(state)


if __name__ == "__main__":
    main()
