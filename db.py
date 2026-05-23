import sqlite3
from contextlib import closing
from config import BASE_DIR

DB_PATH = f"{BASE_DIR}/posts.db"


def connect_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_db():
    with closing(connect_db()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    site_name TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (site_name, post_id)
                )
            """)


def has_post(site_name, post_id):
    with closing(connect_db()) as conn:
        cursor = conn.execute("""
            SELECT 1
            FROM posts
            WHERE site_name = ? AND post_id = ?
            LIMIT 1
        """, (site_name, post_id))
        return cursor.fetchone() is not None


def save_post(site_name, post):
    with closing(connect_db()) as conn:
        with conn:
            conn.execute("""
                INSERT OR IGNORE INTO posts (site_name, post_id, title, url)
                VALUES (?, ?, ?, ?)
            """, (site_name, post["id"], post["title"], post["url"]))


def save_posts(site_name, posts):
    with closing(connect_db()) as conn:
        with conn:
            conn.executemany("""
                INSERT OR IGNORE INTO posts (site_name, post_id, title, url)
                VALUES (?, ?, ?, ?)
            """, [
                (site_name, post["id"], post["title"], post["url"])
                for post in posts
            ])
