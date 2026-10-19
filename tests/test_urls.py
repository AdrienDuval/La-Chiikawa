from chiikawa.urls import canonical_url

def test_removes_tracking_parameters():
    print(canonical_url("https://www.lemonde.fr/article.html?utm_source=rss&xtor=RSS-3208"))
    url = "https://www.lemonde.fr/article.html?utm_source=rss&xtor=RSS-3208"
    assert canonical_url(url) == "https://www.lemonde.fr/article.html"

def test_keeps_usefull_parameters():
    print(canonical_url("https://site.fr/a?id=42"))
    assert canonical_url("https://site.fr/a?id=42") == "https://site.fr/a?id=42"

def test_lowercases_domain_and_drops_anchor():
    print(f"Test result: {canonical_url('https://WWW.Site.fr/a#comments')} should give https://www.site.fr/a")
    assert canonical_url("https://WWW.Site.fr/a#comments") == "https://www.site.fr/a"
