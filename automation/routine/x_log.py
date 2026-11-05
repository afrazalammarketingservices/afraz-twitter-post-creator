#!/usr/bin/env python3
"""
memory/x-post-log.md reader and writer for the AAMS X agent v2.

The file holds the v1 table (kept unchanged, read for the 60-day topic check
and once-a-day check) and, under "## v2 log (from 2026-11-09)", the v2 table.

    python automation/routine/x_log.py state [--date YYYY-MM-DD]
        JSON: published_today, last_cta_type, last_image_layout,
        questions_this_week, wed_thread_last_2_weeks, topic_keys_60d
    python automation/routine/x_log.py add --row outputs/<folder>/log_row.json
        appends one v2 row (keys = V2_COLUMNS) under the v2 heading

Set X_LOG_PATH to point at another file (tests use a temp copy, never the real log).
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IST = timezone(timedelta(hours=5, minutes=30))
V2_HEADING = "## v2 log (from 2026-11-09)"
V2_COLUMNS = ["IST date", "Day", "Pillar", "Format", "Layout", "Topic", "Topic key", "Sources (with dates)",
              "Post ID", "Permalink", "CTA type", "UTM campaign", "Source article", "Question", "Status", "Notes"]
MANUAL = ("manual test", "manual live test")


def log_path() -> Path:
    return Path(os.environ.get("X_LOG_PATH") or REPO / "memory" / "x-post-log.md")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read(path: Path | None = None) -> tuple[list[dict], list[dict]]:
    """(v1_rows, v2_rows), each row a dict keyed by lower-case column name."""
    path = path or log_path()
    if not path.exists():
        return [], []
    v1, v2, header, in_v2 = [], [], None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == V2_HEADING:
            in_v2, header = True, None
            continue
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-", " ", ":"}:
            continue
        cells = _cells(line)
        if header is None:
            header = [c.lower() for c in cells]
            continue
        (v2 if in_v2 else v1).append(dict(zip(header, cells)))
    return v1, v2


def _d(r: dict):
    try:
        return date.fromisoformat(r.get("ist date", ""))
    except ValueError:
        return None


def _published(rows):
    return [r for r in rows if r.get("status", "").upper() == "PUBLISHED"]


def _manual(r: dict) -> bool:
    return any(m in r.get("notes", "").lower() for m in MANUAL)


def state(today: date, path: Path | None = None) -> dict:
    v1, v2 = read(path)
    pub_all, pub2 = _published(v1 + v2), _published(v2)
    monday = today - timedelta(days=today.weekday())
    real2 = [r for r in pub2 if not _manual(r)]
    images = [r for r in real2 if r.get("layout", "text") not in ("", "text", "none")
              and r.get("pillar") == "image_card"]
    return {
        "date": today.isoformat(),
        "published_today": any(_d(r) == today for r in pub_all),
        "last_cta_type": real2[-1].get("cta type") if real2 else None,
        "last_image_layout": images[-1].get("layout") if images else None,
        "questions_this_week": sum(1 for r in real2 if _d(r) and monday <= _d(r) < today
                                   and r.get("question", "").lower() == "yes"),
        "wed_thread_last_2_weeks": any(r.get("pillar") == "what_changed" and r.get("format") == "thread"
                                       and _d(r) and today - timedelta(days=14) <= _d(r) < today for r in real2),
        "topic_keys_60d": sorted({r.get("topic key", "") for r in pub_all
                                  if _d(r) and _d(r) >= today - timedelta(days=60)} - {""}),
    }


def _fmt(v) -> str:
    return str(v if v not in (None, "") else "none").replace("|", "/").replace("\n", " ").strip()


def add(row: dict, path: Path | None = None) -> str:
    path = path or log_path()
    missing = [c for c in V2_COLUMNS if c not in row]
    if missing:
        raise ValueError(f"log row is missing columns: {missing}")
    text = path.read_text(encoding="utf-8")
    if V2_HEADING not in text:
        raise ValueError(f"{path} has no '{V2_HEADING}' section")
    line = "| " + " | ".join(_fmt(row[c]) for c in V2_COLUMNS) + " |"
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")
    return line


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("state")
    s.add_argument("--date")
    a = sub.add_parser("add")
    a.add_argument("--row", required=True, type=Path)
    args = ap.parse_args()
    if args.cmd == "state":
        today = date.fromisoformat(args.date) if args.date else datetime.now(IST).date()
        print(json.dumps(state(today), indent=2))
        return 0
    try:
        print(add(json.loads(args.row.read_text(encoding="utf-8"))))
    except ValueError as e:
        print(f"x_log: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
