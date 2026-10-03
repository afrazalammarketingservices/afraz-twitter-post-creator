#!/usr/bin/env python3
"""
IST clock helper for the AAMS X Post routine. Uses a fixed UTC+05:30 offset
(India has no DST), so it never depends on the server timezone.

    python automation/routine/ist_clock.py now
        -> {"date": "2026-10-05", "day": "Mon", "time": "19:51", "weekday": true}
    python automation/routine/ist_clock.py wait --until 20:30 --deadline 21:30
        exit 0: target time reached, publish now
        exit 3: still early, slept ~9 minutes, run the same command again
        exit 4: past the deadline, do NOT publish, log NEEDS_AFRAZ
"""
import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
MAX_SLEEP = 540


def now() -> datetime:
    return datetime.now(IST)


def at(hhmm: str) -> datetime:
    h, m = map(int, hhmm.split(":"))
    return now().replace(hour=h, minute=m, second=0, microsecond=0)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("now")
    w = sub.add_parser("wait")
    w.add_argument("--until", required=True)
    w.add_argument("--deadline", required=True)
    args = ap.parse_args()

    n = now()
    if args.cmd == "now":
        print(json.dumps({"date": n.date().isoformat(), "day": n.strftime("%a"),
                          "time": n.strftime("%H:%M"), "weekday": n.weekday() < 5}))
        return
    if n >= at(args.deadline):
        print(json.dumps({"status": "past_deadline", "time": n.strftime("%H:%M")}))
        sys.exit(4)
    remaining = (at(args.until) - n).total_seconds()
    if remaining <= 0:
        print(json.dumps({"status": "go", "time": n.strftime("%H:%M")}))
        return
    time.sleep(min(remaining, MAX_SLEEP))
    if now() >= at(args.until):
        print(json.dumps({"status": "go", "time": now().strftime("%H:%M")}))
        return
    print(json.dumps({"status": "waiting", "time": now().strftime("%H:%M")}))
    sys.exit(3)


if __name__ == "__main__":
    main()
