#!/usr/bin/env python3
"""
X API clients for the AAMS X routine, on the x.com hosts.

Since 19 Nov 2026 api.twitter.com serves a Cloudflare challenge (cf-mitigated:
challenge, HTTP 403) to the cloud runner, while api.x.com answers normally
(memory/x-post-log.md, 2026-11-19 and 2026-11-20). So every call goes to:

    v2 API (posts, users, timelines)   https://api.x.com/2/...
    v1.1 media upload and alt text     https://upload.x.com/1.1/media/...
                                       (api.x.com answers 404 for media upload)

Auth stays OAuth 1.0a user context, exactly as before. Nothing here prints or
logs a credential.

    python automation/routine/x_api.py --check
        read-only: GET /2/users/me on api.x.com, prints the host, status and username
"""
import argparse
import json
import os
import sys

API_HOST = "api.x.com"
UPLOAD_HOST = "upload.x.com"
LEGACY_V2_PREFIX = "https://api.twitter.com"  # hardcoded in tweepy.Client.request (tweepy 4.x)

REQUIRED_ENV = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]


def missing_env() -> list[str]:
    return [k for k in REQUIRED_ENV if not os.environ.get(k)]


def v2_client():
    """tweepy.Client (OAuth 1.0a user context) whose requests go to api.x.com instead of api.twitter.com.

    tweepy builds every v2 URL from a hardcoded "https://api.twitter.com"; this rewrites only that host
    on the client's own session before the request is signed and sent, so the OAuth signature covers the
    final api.x.com URL.
    """
    import tweepy

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    original = client.session.request

    def request(method, url, *args, **kwargs):
        if isinstance(url, str) and url.startswith(LEGACY_V2_PREFIX):
            url = "https://" + API_HOST + url[len(LEGACY_V2_PREFIX):]
        return original(method, url, *args, **kwargs)

    client.session.request = request
    return client


def v1_api():
    """tweepy.API (OAuth 1.0a) for the v1.1 media upload and alt text, on api.x.com / upload.x.com."""
    import tweepy

    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    return tweepy.API(auth, host=API_HOST, upload_host=UPLOAD_HOST)


def check() -> int:
    """Read-only: GET /2/users/me on the new host. Prints host, HTTP status and username only."""
    import requests
    from requests_oauthlib import OAuth1

    url = f"https://{API_HOST}/2/users/me"
    auth = OAuth1(os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
                  os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])
    r = requests.get(url, auth=auth, timeout=30)
    body = {}
    try:
        body = r.json()
    except ValueError:
        pass
    result = {
        "ok": r.status_code == 200 and "data" in body,
        "host": API_HOST,
        "status": r.status_code,
        "cf_mitigated": r.headers.get("cf-mitigated"),
        "username": (body.get("data") or {}).get("username"),
    }
    print(json.dumps(result))
    if not result["ok"]:
        return 1
    # The tweepy client used by the routine must reach the same host.
    me = v2_client().get_me(user_auth=True).data
    print(json.dumps({"ok": me is not None, "via": "tweepy v2_client", "host": API_HOST,
                      "username": getattr(me, "username", None)}))
    return 0 if me is not None else 1


def main() -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="read-only GET /2/users/me on api.x.com")
    a = ap.parse_args()
    if missing_env():
        print(json.dumps({"ok": False, "error": "missing env vars", "names": missing_env()}))
        return 1
    if a.check:
        return check()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
