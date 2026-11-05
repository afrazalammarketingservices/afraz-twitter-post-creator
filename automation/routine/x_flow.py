#!/usr/bin/env python3
"""
One-shot flow for a finished draft.json (AAMS X agent v2):
render the card (Tue, Fri) -> run the gate -> build the first reply ->
publish the post or thread -> publish exactly one first reply on the last part.

    python automation/routine/x_flow.py outputs/<folder>/draft.json --dry-run
        stops before publish_twitter.py: prints the post, the reply and the image path
    python automation/routine/x_flow.py outputs/<folder>/draft.json
        publishes (the routine runs this only after ist_clock.py wait says go)

Exit codes: 0 done (or dry run ok), 1 render or gate failed (nothing published),
3 already published today (nothing published), 5 publish result unclear
(run recent_posts.py --recent 10 before any retry), 6 post is live but the
first reply failed (check recent_posts.py before retrying the reply only).
"""
import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_card  # noqa: E402
import validate_post  # noqa: E402
import x_log  # noqa: E402

PUBLISH = HERE / "publish_twitter.py"


def out(obj: dict) -> None:
    sys.stdout.buffer.write((json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def prepare(draft_path: Path) -> tuple[dict | None, dict]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    folder = draft_path.parent
    if draft.get("image"):
        m = render_card.render(draft_path)
        if not m["ok"]:
            return None, {"stage": "render", "errors": m["errors"]}
    st = x_log.state(date.fromisoformat(draft["date_ist"]))
    report = validate_post.validate(draft, folder, st)
    if not report["ok"]:
        return None, {"stage": "gate", "errors": report["errors"]}
    parts = draft["parts"]
    thread_file = None
    if len(parts) > 1:
        thread_file = folder / "thread.json"
        thread_file.write_text(json.dumps(parts, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / "reply.txt").write_text(report["info"]["reply_text"], encoding="utf-8")
    img = draft.get("image")
    plan = {
        "slug": folder.name.split("_", 1)[-1],
        "parts": parts,
        "thread_file": str(thread_file) if thread_file else None,
        "image": str(folder / "image.png") if img else None,
        "preview": str(folder / "preview_540.png") if img else None,
        "alt_text": img.get("alt_text") if img else None,
        "reply_text": report["info"]["reply_text"],
        "reply_on": "the last part",
        "question": report["info"]["question"],
        "cta_type": report["info"]["cta_type"],
        "utm_campaign": report["info"]["utm_campaign"],
        "weighted_counts": report["info"]["weighted_counts"],
        "state": st,
    }
    return plan, {}


def run_publish(args: list[str], result: Path) -> dict | None:
    if result.exists():
        result.unlink()
    p = subprocess.run([sys.executable, str(PUBLISH), *args, "--result-json", str(result)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    sys.stderr.write(p.stdout + p.stderr)
    if p.returncode != 0 or not result.exists():
        return None
    return json.loads(result.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", type=Path)
    ap.add_argument("--dry-run", action="store_true", help="stop before publish_twitter.py")
    a = ap.parse_args()
    plan, fail = prepare(a.draft)
    if plan is None:
        out({"ok": False, "published": False, **fail})
        return 1
    if a.dry_run:
        out({"ok": True, "dry_run": True, "published": False,
             "note": "DRY RUN: stopped before publish_twitter.py", **plan})
        return 0
    if plan["state"]["published_today"]:
        out({"ok": False, "published": False, "stage": "idempotency", "errors": ["already published today"]})
        return 3
    folder = a.draft.parent
    post_args = ["--thread-file", plan["thread_file"]] if plan["thread_file"] else ["--text", plan["parts"][0]]
    if plan["image"]:
        post_args += ["--images", plan["image"], "--alt-text", plan["alt_text"]]
    post = run_publish(post_args + ["--slug", plan["slug"]], folder / "publish_result.json")
    if post is None:
        out({"ok": False, "published": "unclear", "stage": "publish",
             "errors": ["PUBLISH_UNCLEAR: run recent_posts.py --recent 10 before any retry, never retry blind"]})
        return 5
    tweets = post["tweets"]
    result = {"ok": True, "published": True, "post_ids": [t["tweet_id"] for t in tweets],
              "permalink": tweets[0]["url"], "last_id": tweets[-1]["tweet_id"],
              "alt_text_failed": post.get("alt_text_failed", []), "reply_id": None}
    reply = run_publish(["--text", plan["reply_text"], "--in-reply-to", tweets[-1]["tweet_id"], "--slug", plan["slug"]],
                        folder / "reply_result.json")
    if reply is None:
        result.update(ok=False, errors=["REPLY_FAILED: the post is live; check recent_posts.py --recent 10 before retrying the reply only"])
        out(result)
        return 6
    result["reply_id"] = reply["tweets"][0]["tweet_id"]
    result["reply_url"] = reply["tweets"][0]["url"]
    (folder / "flow_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    out(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
