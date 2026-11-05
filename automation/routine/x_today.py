#!/usr/bin/env python3
"""What the AAMS X agent v2 posts today, in Asia/Kolkata (inputs/X-STANDARD-v2.md section 3).

    python automation/routine/x_today.py [--date YYYY-MM-DD]

Prints JSON: {date, weekday, pillar, format, image, parts, theme}.
Saturday and Sunday: pillar and format are null, the routine stops.
"""
import argparse
import json
from datetime import date, datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))  # India has no daylight saving

# weekday -> pillar, format, image, allowed part counts
DAYS = {
    0: {"pillar": "seo_fix", "format": "text", "image": None, "parts": [1]},
    1: {"pillar": "image_card", "format": "image", "image": "stat_cards|checklist|before_after|steps", "parts": [1]},
    2: {"pillar": "what_changed", "format": "text", "image": None, "parts": [1, 3, 4]},
    3: {"pillar": "myth_or_mistake", "format": "text", "image": None, "parts": [1]},
    4: {"pillar": "website_thread", "format": "thread", "image": "thread_cover", "parts": [5, 6, 7]},
}
THEMES = {
    11: "crawling, indexing and BFCM readiness",
    12: "product page SEO",
    1: "collection pages and internal links",
    2: "speed, Core Web Vitals, variants and filters",
    3: "schema, Merchant Center free listings, reviews",
    4: "content, links and AI search",
    5: "migrations and reporting",
}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def today_ist() -> date:
    return datetime.now(IST).date()


def plan(d: date) -> dict:
    day = DAYS.get(d.weekday(), {"pillar": None, "format": None, "image": None, "parts": []})
    return {"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()], **day, "theme": THEMES.get(d.month)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD, default today in Asia/Kolkata")
    a = ap.parse_args()
    print(json.dumps(plan(date.fromisoformat(a.date) if a.date else today_ist())))


if __name__ == "__main__":
    main()
