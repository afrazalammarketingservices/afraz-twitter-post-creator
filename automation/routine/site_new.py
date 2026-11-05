#!/usr/bin/env python3
"""New or updated afrazalam.com posts, pages and tools in the last N days.

  python automation/routine/site_new.py [--days 7]

Discovery: https://afrazalam.com/sitemap_index.xml and its child sitemaps.
Real publish dates and titles come from the WordPress REST API, because a
sitewide re-save gives dozens of URLs the same lastmod. Those are flagged
"bulk_resave": true and are not new content.

Prints a JSON list, newest first. Each item: url, title, lastmod, type
(post, page, tool), published, new (published inside the window),
bulk_resave. Legal pages, tag, author and category archives are skipped.
"""
import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import unescape
from urllib.parse import urlparse

SITE = "https://afrazalam.com"
UA = {"User-Agent": "Mozilla/5.0 (AAMS X agent)"}
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
IST = timezone(timedelta(hours=5, minutes=30))
SKIP = re.compile(
    r"/(terms|privacy|disclaimer|data-protection|cookie|refund)[^/]*/?$|/(tag|author|category)/|^/blog/?$|/confirmed/?$",
    re.I,
)
BULK_MIN = 5


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def parse_index(xml: str) -> list:
    root = ET.fromstring(xml.strip())
    return [e.text.strip() for e in root.findall("s:sitemap/s:loc", NS)]


def parse_urlset(xml: str) -> list:
    root = ET.fromstring(xml.strip())
    out = []
    for u in root.findall("s:url", NS):
        loc = u.find("s:loc", NS)
        lm = u.find("s:lastmod", NS)
        if loc is not None and loc.text:
            out.append({"url": loc.text.strip(), "lastmod": lm.text.strip() if lm is not None and lm.text else ""})
    return out


def kind(url: str, sitemap: str) -> str:
    path = urlparse(url).path
    if path.startswith("/tools/") and path.strip("/") != "tools":
        return "tool"
    return "post" if "post-sitemap" in sitemap else "page"


def to_date(s: str):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def rest_dates() -> dict:
    """url -> {published, title} from the WordPress REST API. Empty dict if unavailable."""
    out = {}
    for t in ("posts", "pages"):
        page = 1
        while page <= 10:
            try:
                data = json.loads(fetch(f"{SITE}/wp-json/wp/v2/{t}?per_page=100&page={page}&_fields=link,date,title"))
            except Exception:
                break
            if not isinstance(data, list) or not data:
                break
            for d in data:
                out[d["link"].rstrip("/") + "/"] = {
                    "published": (d.get("date") or "")[:10],
                    "title": unescape(re.sub("<[^>]+>", "", (d.get("title") or {}).get("rendered", ""))),
                }
            if len(data) < 100:
                break
            page += 1
    return out


def build(entries: list, meta: dict, today: date, days: int) -> list:
    """entries: [{url, lastmod, sitemap}] -> filtered, enriched, newest first."""
    since = today - timedelta(days=days)
    stamps = Counter(e["lastmod"] for e in entries if e["lastmod"])
    items = []
    for e in entries:
        path = urlparse(e["url"]).path or "/"
        if SKIP.search(path):
            continue
        m = meta.get(e["url"].rstrip("/") + "/", {})
        pub = to_date(m.get("published", ""))
        lm = to_date(e["lastmod"])
        is_new = bool(pub and pub >= since)
        if not is_new and not (lm and lm >= since):
            continue
        items.append({
            "url": e["url"],
            "title": m.get("title", ""),
            "lastmod": e["lastmod"],
            "type": kind(e["url"], e["sitemap"]),
            "published": pub.isoformat() if pub else None,
            "new": is_new,
            "bulk_resave": stamps[e["lastmod"]] >= BULK_MIN and not is_new,
        })
    items.sort(key=lambda i: (i["new"], not i["bulk_resave"], i["published"] or "", i["lastmod"]), reverse=True)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--date", help="YYYY-MM-DD, default today in Asia/Kolkata")
    a = ap.parse_args()
    today = date.fromisoformat(a.date) if a.date else datetime.now(IST).date()
    try:
        entries = []
        for sm in parse_index(fetch(SITE + "/sitemap_index.xml")):
            entries += [dict(e, sitemap=sm) for e in parse_urlset(fetch(sm))]
    except Exception as e:
        sys.exit("could not read the afrazalam.com sitemaps: %s" % e)
    meta = rest_dates()
    missing = [e["url"] for e in entries if e["url"].rstrip("/") + "/" not in meta]
    for u in missing:  # fall back to the page <title>
        try:
            t = re.search(r"<title>(.*?)</title>", fetch(u), re.S)
            meta[u.rstrip("/") + "/"] = {"published": "", "title": unescape(t.group(1).strip()) if t else ""}
        except Exception:
            pass
    print(json.dumps(build(entries, meta, today, a.days), indent=2))


if __name__ == "__main__":
    main()
