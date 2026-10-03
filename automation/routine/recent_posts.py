#!/usr/bin/env python3
"""
Read-only X API checks for the AAMS X Post routine. Never posts, never
prints a credential.

    python automation/routine/recent_posts.py --recent 10   # account's latest posts
    python automation/routine/recent_posts.py --id 123456   # does this post exist?

Use --recent before ANY retry after a publish error or timeout (never retry
blind), and --id after publishing to verify the post exists.
"""
import argparse
import json
import os
import sys

REQUIRED = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]


def client():
    import tweepy
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        print(json.dumps({"error": "missing env vars", "names": missing}))
        sys.exit(1)
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--recent", type=int)
    g.add_argument("--id")
    args = ap.parse_args()
    c = client()
    fields = ["created_at", "conversation_id", "in_reply_to_user_id"]
    if args.id:
        r = c.get_tweet(args.id, tweet_fields=fields, user_auth=True)
        if r.data is None:
            print(json.dumps({"exists": False, "id": args.id, "errors": [str(e) for e in (r.errors or [])]}))
            sys.exit(1)
        print(json.dumps({"exists": True, "id": str(r.data.id), "text": r.data.text,
                          "created_at": str(r.data.created_at),
                          "url": f"https://x.com/i/web/status/{r.data.id}"}, ensure_ascii=False))
        return
    me = c.get_me(user_auth=True).data
    r = c.get_users_tweets(me.id, max_results=max(5, min(args.recent, 100)), tweet_fields=fields, user_auth=True)
    out = [{"id": str(t.id), "created_at": str(t.created_at), "text": t.text,
            "is_reply": t.in_reply_to_user_id is not None} for t in (r.data or [])]
    print(json.dumps({"username": me.username, "posts": out}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
