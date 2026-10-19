from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Query parameters that only track where a click came from

TRACKING_PREFIXES = ("utm_", "xtor", "at_")


def canonical_url(url: str) -> str:
    """return a clean url, so the same article always gets the same key."""
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query)
        if not key.lower().startswith(TRACKING_PREFIXES)
    ]

    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path, urlencode(query), "")
    )
