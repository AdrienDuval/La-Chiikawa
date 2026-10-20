from chiikawa.collect import is_allowed, robots_url

ROBOTS = """
User-agent: *
Disallow: */feed
Disallow: /private/
"""


def test_robots_is_at_site_root():
    url = "https://www.site.fr/a/b/rss.xml"
    assert robots_url(url) == "https://www.site.fr/robots.txt"


def test_allowed_url():
    assert is_allowed("https://www.site.fr/rss.xml", ROBOTS)


def test_wildcard_rule_blocks_feed():
    # the rule that Python's built in robotparser get wrong
    assert not is_allowed("https://www.site.fr/news/feed", ROBOTS)


def test_blocked_folder():
    assert not is_allowed("https://www.site.fr/private/x", ROBOTS)
