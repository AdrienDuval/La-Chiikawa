from chiikawa.collect import parse_news_sitemap

XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url>
    <loc>https://www.site.fr/article-1.html</loc>
    <news:news>
      <news:publication_date>2026-10-20T08:00:00+02:00</news:publication_date>
      <news:title>Premier article</news:title>
    </news:news>
  </url>
</urlset>"""


def test_reads_title_link_and_date():
    items = parse_news_sitemap(XML)
    assert items == [
        {
            "title": "Premier article",
            "excerpt": "",
            "link": "https://www.site.fr/article-1.html",
            "published": "2026-10-20T08:00:00+02:00",
        }
    ]
