from urllib.parse import urlsplit
from xml.etree import ElementTree

import feedparser
import httpx
from protego import Protego

NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
}

USER_AGENT = "chiikawa_efrei/1.0 (+https://github.com/AdrienDuval/La-Chiikawa)"


BOT_NAME = "Chiikawa_efrei"


class NotAllowedError(Exception):
    """robots.txt forbids our bot to read this URL."""


def parse_news_sitemap(xml: bytes) -> list[dict]:
    """Read a news sitemap and keep only the allowed fields."""
    root = ElementTree.fromstring(xml)
    items = []
    for url in root.findall("sm:url", NS):
        items.append(
            {
                "title": url.findtext("news:news/news:title", "", NS),
                "excerpt": "",
                "link": url.findtext("sm:loc", "", NS),
                "published": url.findtext("news:news/news:publication_date", "", NS),
            }
        )
    return items


def robots_url(url: str) -> str:
    """robots.txt always lives at the root of the site."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/robots.txt"


def is_allowed(url: str, robots_txt: str) -> bool:
    """Does this robots.txt allow our bot to read this URL?"""
    return Protego.parse(robots_txt).can_fetch(url, BOT_NAME)


def fetch_rss(url: str) -> list[dict]:
    """Download one RSS feed (politely) and keep only the allowed fields."""
    feed = feedparser.parse(polite_get(url))
    return [
        {
            "title": entry.get("title", ""),
            "excerpt": entry.get("summary", "")[:500],
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        }
        for entry in feed.entries
    ]


def polite_get(url: str) -> bytes:
    """Check robots.txt, then download the URL. Raise NotAllowedError if forbidden."""
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, timeout=20, follow_redirects=True
    ) as client:
        robots = client.get(robots_url(url))
        if robots.status_code >= 500:
            robots.raise_for_status()
        robots_txt = robots.text if robots.status_code == 200 else ""

        if not is_allowed(url, robots_txt):
            raise NotAllowedError(f"robots.txt forbids reading {url}")

        response = client.get(url)
        response.raise_for_status()
        return response.content


def fetch_sitemap(url: str) -> list[dict]:
    """Download one news sitemap (politely) and keep only the allowed fields."""
    return parse_news_sitemap(polite_get(url))
