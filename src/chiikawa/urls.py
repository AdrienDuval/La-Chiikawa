from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Query parameters that only track where a click came from

TRACKING_PREFIXES = ("utm_", "xtor", "at_")

def canonical_url(url: str) -> str:
    """ return a clean url, so the same article always gets the same key."""
    parts = urlsplit(url.strip())
    print(f"splitted part: {parts} \n")
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query)
        if not key.lower().startswith(TRACKING_PREFIXES)
    ]

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path,
            urlencode(query),
            ""
        )
    )

# uv run python -c "from chiikawa.urls import canonical_url; print(canonical_url('https://WWW.LeMonde.fr/a.html?utm_source=rss&id=7#top'))"
