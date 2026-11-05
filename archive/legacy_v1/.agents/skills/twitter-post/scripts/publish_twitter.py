#!/usr/bin/env python3
"""
Publishes a single tweet or a thread to X (Twitter), with an optional
image on the first tweet.

This hits the LIVE X API and posts to the real, authenticated profile.
Only run it after the Step 5 approval gate in the twitter-post skill has
already been satisfied by the user.

Usage:
    # single tweet, no image
    python publish_twitter.py --text "..." --slug "my-post"

    # single tweet with image
    python publish_twitter.py --text "..." --images outputs/2026-08-27_my-post/image_1.png --slug "my-post"

    # thread (JSON array of strings, one per tweet, in order), image on tweet 1 only
    python publish_twitter.py --thread-file outputs/2026-08-27_my-post/thread.json --images outputs/2026-08-27_my-post/image_1.png --slug "my-post"

    # a follow-up reply (e.g. to carry a link that shouldn't be in the body)
    python publish_twitter.py --text "Details here: https://afrazalam.com" --in-reply-to 1234567890 --slug "my-post"

Auth: uses OAuth 1.0a user-context credentials (API key/secret + access
token/secret) for both the v1.1 media upload endpoint and the v2 tweet
creation endpoint. All four must have Read and Write permission, see
README.md if you get a 403.

Logs every call to outputs/<date>_<slug>/publish_log.json.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[4]

REQUIRED_ENV = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]


def get_clients():
    import tweepy

    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        print(f"[publish] ERROR: missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    api_v1 = tweepy.API(auth)  # media upload only lives on v1.1

    client_v2 = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    return api_v1, client_v2


def upload_media(api_v1, image_paths: list[str], alt_texts: list[str] | None = None) -> list[str]:
    alt_texts = alt_texts or []
    media_ids = []
    for i, path in enumerate(image_paths):
        if not Path(path).exists():
            print(f"[publish] ERROR: image not found: {path}", file=sys.stderr)
            sys.exit(1)
        media = api_v1.media_upload(filename=path)
        media_ids.append(media.media_id)
        print(f"[publish] uploaded {path} -> media_id {media.media_id}")
        if i < len(alt_texts) and alt_texts[i]:
            # Alt text must never block the post: on failure, publish without it.
            try:
                api_v1.create_media_metadata(media.media_id, alt_texts[i][:1000])
                print(f"[publish] alt text set on media_id {media.media_id}")
            except Exception as e:  # noqa: BLE001
                ALT_TEXT_FAILURES.append(f"media_id {media.media_id}: {type(e).__name__}")
                print(f"[publish] ALT_TEXT_FAILED on media_id {media.media_id} ({type(e).__name__}), publishing without alt text")
    return media_ids


ALT_TEXT_FAILURES: list[str] = []


def post_tweet(client_v2, text: str, media_ids: list[str] | None = None, in_reply_to: str | None = None) -> dict:
    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    if in_reply_to:
        kwargs["in_reply_to_tweet_id"] = in_reply_to

    response = client_v2.create_tweet(**kwargs)
    tweet_id = response.data["id"]
    return {
        "tweet_id": tweet_id,
        "text": text,
        "url": f"https://x.com/i/web/status/{tweet_id}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Single tweet text")
    parser.add_argument("--thread-file", type=Path, help="JSON file: array of tweet texts, in order")
    parser.add_argument("--images", nargs="*", default=[], help="Image path(s) to attach to the first tweet only")
    parser.add_argument("--alt-text", nargs="*", default=[], help="Alt text per image, same order as --images (max 1000 chars each)")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print what would be posted; no API calls")
    parser.add_argument("--in-reply-to", help="Tweet ID to reply to (e.g. for a follow-up link reply)")
    parser.add_argument("--slug", required=True)
    args = parser.parse_args()

    if not args.text and not args.thread_file:
        print("[publish] ERROR: pass either --text or --thread-file", file=sys.stderr)
        sys.exit(1)

    if args.thread_file:
        tweets = json.loads(Path(args.thread_file).read_text())
        if not isinstance(tweets, list) or not tweets:
            print("[publish] ERROR: --thread-file must be a non-empty JSON array of strings", file=sys.stderr)
            sys.exit(1)
    else:
        tweets = [args.text]

    if args.alt_text and len(args.alt_text) != len(args.images):
        print("[publish] ERROR: --alt-text count must match --images count", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        for path in args.images:
            if not Path(path).exists():
                print(f"[publish] ERROR: image not found: {path}", file=sys.stderr)
                sys.exit(1)
        print(json.dumps({"dry_run": True, "tweets": tweets, "images": args.images,
                          "alt_text": args.alt_text, "in_reply_to": args.in_reply_to}, indent=2, ensure_ascii=False))
        return

    api_v1, client_v2 = get_clients()

    media_ids = upload_media(api_v1, args.images, args.alt_text) if args.images else None

    results = []
    previous_id = args.in_reply_to
    for i, text in enumerate(tweets):
        result = post_tweet(
            client_v2,
            text,
            media_ids=media_ids if i == 0 else None,  # image only on the first tweet
            in_reply_to=previous_id,
        )
        results.append(result)
        print(f"[publish] posted tweet {i + 1}/{len(tweets)}: {result['url']}")
        previous_id = result["tweet_id"]
        if i < len(tweets) - 1:
            time.sleep(2)  # small, human-like gap between chained thread tweets

    date_slug = datetime.now().strftime("%Y-%m-%d")
    out_dir = REPO_ROOT / "outputs" / f"{date_slug}_{args.slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "publish_log.json"

    log_entry = {
        "published_at": datetime.now().isoformat(),
        "slug": args.slug,
        "tweets": results,
        "alt_text_failed": ALT_TEXT_FAILURES,
    }
    existing = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
            if not isinstance(existing, list):
                existing = [existing]
        except Exception:  # noqa: BLE001
            existing = []
    existing.append(log_entry)
    log_path.write_text(json.dumps(existing, indent=2))

    print(f"[publish] logged to {log_path}")
    print(f"[publish] live: {results[0]['url']}")
    if ALT_TEXT_FAILURES:
        print(f"[publish] ALT_TEXT_FAILED: post is live without alt text ({'; '.join(ALT_TEXT_FAILURES)})")


if __name__ == "__main__":
    main()
