from urllib.parse import urlsplit

import feedparser
import httpx
from protego import Protego

USER_AGENT = "chiikawa_efrei/1.0 (+https://github.com/AdrienDuval/La-Chiikawa)"


BOT_NAME = "Chiikawa_efrei"

class NotAllowedError(Exception):
    """robots.txt forbids our bot to read this URL."""

def robots_url(url: str) -> str:
    """robots.txt always lives at the root of the site."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/robots.txt"


def is_allowed(url: str, robots_txt: str) -> bool:
    """Does this robots.txt allow our bot to read this URL?"""
    return Protego.parse(robots_txt).can_fetch(url, BOT_NAME)


def fetch_rss(url: str) -> list[dict]:
    """Check robots.txt, download on rss feedm, keep only the allowed fields."""

    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=10
    ) as client:
        robots = client.get(robots_url(url))
        if robots.status_code >= 500:
            robots.raise_for_status()
        robots_txt = robots.text if robots.status_code == 200 else ""

        if not is_allowed(url, robots_txt):
            raise NotAllowedError(f"robots.txt forbids reading {url}")

        response = client.get(url)
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