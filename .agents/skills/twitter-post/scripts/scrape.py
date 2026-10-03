#!/usr/bin/env python3
"""
Scrapes the user's own site and any competitor/niche URLs listed in
inputs/competitors/urls.txt via Firecrawl, so post angles are grounded in
something real rather than invented.

Usage:
    python scrape.py [--urls-file PATH] [--out PATH]

Writes a research.json file with one entry per URL: {url, title, content,
scraped_at}. Skips URLs that fail to scrape (logs a warning, doesn't crash
the whole run over one bad site).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_URLS_FILE = REPO_ROOT / "inputs" / "competitors" / "urls.txt"


def read_urls(urls_file: Path) -> list[str]:
    if not urls_file.exists():
        return []
    urls = []
    for line in urls_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def scrape_url(app, url: str) -> dict | None:
    try:
        result = app.scrape(url, formats=["markdown"])
        content = result.markdown or ""
        title = (result.metadata.title if result.metadata else "") or ""
        return {
            "url": url,
            "title": title,
            "content": (content or "")[:6000],  # cap so downstream prompts stay reasonable
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:  # noqa: BLE001
        print(f"[scrape] WARNING: failed to scrape {url}: {exc}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls-file", type=Path, default=DEFAULT_URLS_FILE)
    parser.add_argument("--out", type=Path, default=None, help="Where to write research.json")
    args = parser.parse_args()

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("[scrape] ERROR: FIRECRAWL_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    urls = read_urls(args.urls_file)
    if not urls:
        print(
            f"[scrape] No URLs found in {args.urls_file}. "
            "Add your own site plus 1-3 competitor/niche URLs, one per line, then re-run.",
            file=sys.stderr,
        )
        sys.exit(1)

    from firecrawl import FirecrawlApp  # imported here so --help works without the dep installed

    app = FirecrawlApp(api_key=api_key)

    results = []
    for url in urls:
        print(f"[scrape] scraping {url} ...")
        entry = scrape_url(app, url)
        if entry:
            results.append(entry)

    if not results:
        print("[scrape] ERROR: every URL failed to scrape, nothing to work with.", file=sys.stderr)
        sys.exit(1)

    out_path = args.out
    if out_path is None:
        date_slug = datetime.now().strftime("%Y-%m-%d")
        out_dir = REPO_ROOT / "outputs" / f"{date_slug}_draft"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "research.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[scrape] wrote {len(results)} entries to {out_path}")


if __name__ == "__main__":
    main()
