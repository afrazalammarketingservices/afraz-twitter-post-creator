import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "routine"))
from site_new import build, parse_index, parse_urlset  # noqa: E402

INDEX = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://afrazalam.com/post-sitemap.xml</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></sitemap>
  <sitemap><loc>https://afrazalam.com/page-sitemap.xml</loc><lastmod>2026-11-05T03:24:48+00:00</lastmod></sitemap>
</sitemapindex>"""

POSTS = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://afrazalam.com/blog/</loc><lastmod>2026-11-05T03:24:48+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/blog/new-post/</loc><lastmod>2026-11-03T10:00:00+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/blog/old-a/</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/blog/old-b/</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/blog/old-c/</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/blog/really-old/</loc><lastmod>2026-09-01T10:00:00+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/tag/seo/</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></url>
</urlset>"""

PAGES = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://afrazalam.com/shopify-seo-checklist/</loc><lastmod>2026-11-04T15:36:37+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/tools/roas-calculator/</loc><lastmod>2026-11-05T03:00:13+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/privacy-policy/</loc><lastmod>2026-11-05T03:00:12+00:00</lastmod></url>
  <url><loc>https://afrazalam.com/author/afraz/</loc><lastmod>2026-11-05T03:00:12+00:00</lastmod></url>
</urlset>"""

META = {
    "https://afrazalam.com/blog/new-post/": {"published": "2026-11-03", "title": "New post"},
    "https://afrazalam.com/blog/old-a/": {"published": "2026-09-20", "title": "Old A"},
    "https://afrazalam.com/blog/old-b/": {"published": "2026-09-21", "title": "Old B"},
    "https://afrazalam.com/blog/old-c/": {"published": "2026-09-22", "title": "Old C"},
    "https://afrazalam.com/shopify-seo-checklist/": {"published": "2026-11-04", "title": "Shopify SEO Quick-Fix Checklist"},
    "https://afrazalam.com/tools/roas-calculator/": {"published": "2026-10-21", "title": "ROAS Calculator"},
}


def entries():
    out = []
    sitemaps = parse_index(INDEX)
    assert sitemaps == ["https://afrazalam.com/post-sitemap.xml", "https://afrazalam.com/page-sitemap.xml"]
    for sm, xml in zip(sitemaps, [POSTS, PAGES]):
        out += [dict(e, sitemap=sm) for e in parse_urlset(xml)]
    return out


def test_parse_urlset():
    e = parse_urlset(POSTS)
    assert e[1] == {"url": "https://afrazalam.com/blog/new-post/", "lastmod": "2026-11-03T10:00:00+00:00"}


def test_build_filters_and_flags():
    items = build(entries(), META, date(2026, 11, 6), 7)
    urls = [i["url"] for i in items]
    # skipped: blog index, tag and author archives, legal pages, anything older than 7 days
    for skipped in ("/blog/", "/tag/seo/", "/author/afraz/", "/privacy-policy/", "/blog/really-old/"):
        assert "https://afrazalam.com" + skipped not in urls
    # genuinely new pieces come first
    assert urls[:2] == ["https://afrazalam.com/shopify-seo-checklist/", "https://afrazalam.com/blog/new-post/"]
    by = {i["url"]: i for i in items}
    assert by["https://afrazalam.com/shopify-seo-checklist/"]["type"] == "page"
    assert by["https://afrazalam.com/shopify-seo-checklist/"]["new"] is True
    assert by["https://afrazalam.com/blog/new-post/"]["type"] == "post"
    assert by["https://afrazalam.com/tools/roas-calculator/"]["type"] == "tool"
    # 5 URLs share the 03:00:13 re-save stamp: flagged, not new
    assert by["https://afrazalam.com/blog/old-a/"]["bulk_resave"] is True
    assert by["https://afrazalam.com/blog/old-a/"]["new"] is False
