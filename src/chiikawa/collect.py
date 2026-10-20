from urllib.parse import urlsplit

import feedparser
import httpx
from protego import Protego

USER_AGENT = "chiikawa_efrei/1.0 (+https://github.com/AdrienDuval/La-Chiikawa)"


BOT_NAME = "Chiikawa_efrei"


def robots_url(url: str) -> str:
    """robots.txt always lives at the root of the site."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/robots.txt"


def is_allowed(url: str, robots_txt: str) -> bool:
    """Does this robots.txt allow our bot to read this URL?"""
    return Protego.parse(robots_txt).can_fetch(url, BOT_NAME)


def fetch_rss(url: str) -> list[dict]:
    """download one rss feed and keep only the allowed fields"""

    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    return [
        {
            "title": entry.get("title", ""),
            "excerpt": entry.get("summary", "")[:500],
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        }
        for entry in feed.entries
    ]
