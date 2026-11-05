#!/usr/bin/env python3
"""
AAMS X agent v2 copy gate (inputs/X-STANDARD-v2.md section 5). Reads one
draft.json, prints a JSON report, exits 0 only when there are zero errors.
On a failure the routine rewrites only the failing part, max 2 rounds, then
logs NEEDS_AFRAZ. The routine must never edit this file during a run.

    python automation/routine/validate_post.py outputs/<folder>/draft.json

draft.json (v2):
{
  "date_ist": "2026-11-09", "day": "Mon", "pillar": "seo_fix",
  "format": "single" | "thread", "keyword": "XML sitemap",
  "topic": "...", "topic_key": "sitemap-is-a-hint",
  "parts": ["post text"],                      (thread: one string per part)
  "sources": [{"id": "s1", "name": "Publisher, page title", "url": "https://...",
               "date": "YYYY-MM-DD", "quote": "the page's own words"}],
  "numbers": {"2.5": "s1", "3": {"kind": "count", "note": "3 metrics listed"}},
  "source_article": null | "https://afrazalam.com/...",
  "image": null | {... see render_card.py ..., "alt_text": "One sentence."},
  "first_reply": {"cta_type": "checklist" | "article" | "call", "source_id": "s1" | null}
}
The image must be rendered (render_card.py) before this gate runs.
"""
import hashlib
import json
import re
import sys
import unicodedata
import warnings
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_card  # noqa: E402
import x_log  # noqa: E402
import x_reply  # noqa: E402
import x_today  # noqa: E402

warnings.filterwarnings("ignore")

DASHES = (chr(0x2014), chr(0x2013))
BANNED = ["game-changer", "game changer", "in today's", "let's dive", "unlock", "supercharge", "skyrocket",
          "follow for more", "like and repost", "comment below"]
OFF_TOPIC = [r"\bROAS\b", r"\bMeta Ads\b", r"\bFacebook Ads\b", r"\bGoogle Ads\b", r"\bPPC\b", r"\bCAPI\b",
             r"\bPixel\b", r"\bad spend\b", r"\bCPC\b", r"\bCPA\b", r"Advantage\+", r"\bHVAC\b",
             r"\bplumb(?:ing|ers?)\b", r"\broof(?:ing|ers?)\b", r"\bhome[- ]services?\b",
             r"\blocal[- ]services?\b", r"\bcoach(?:es|ing)?\b"]
HASHTAGS_OK = {"#shopifyseo", "#ecommerceseo", "#woocommerce"}
URL_RE = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|io|co|in|shop|store|ai|dev|app|uk|us)\b", re.I)
COUNTER_RE = re.compile(r"^\s*\(?\d+\s*/\s*\d+\)?|(?<![\d.])\b\d{1,2}/\d{1,2}\b(?![\d/])|^\s*\d+[.)]\s")
NUM_RE = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?")
SINGLE_MIN, MAX_CHARS, THREAD_PART_MIN = 200, 280, 80


def weighted(text: str) -> int:
    from twitter_text import parse_tweet
    return parse_tweet(text).weightedLength


def is_emoji(c: str) -> bool:
    o = ord(c)
    return unicodedata.category(c) == "So" or 0x1F000 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)


def text_checks(label: str, text: str) -> list[str]:
    errs = []
    if any(d in text for d in DASHES):
        errs.append(f"{label}: em or en dash")
    if any(is_emoji(c) for c in text):
        errs.append(f"{label}: emoji")
    if "!" in text:
        errs.append(f"{label}: exclamation mark")
    low = text.lower().replace("’", "'")
    for b in BANNED:
        if b in low:
            errs.append(f"{label}: banned phrase {b!r}")
    for pat in OFF_TOPIC:
        m = re.search(pat, text, re.I)
        if m:
            errs.append(f"{label}: not SEO-only, found {m.group(0)!r}")
    return errs


def ends_with_question(parts: list[str]) -> bool:
    return bool(parts) and parts[-1].rstrip().endswith("?")


def validate(draft: dict, draft_dir: Path, st: dict) -> dict:
    errors, warns, info = [], [], {}
    try:
        d = date.fromisoformat(draft.get("date_ist", ""))
    except ValueError:
        return {"ok": False, "errors": ["date_ist missing or not YYYY-MM-DD"], "warnings": [], "info": {}}
    plan = x_today.plan(d)
    pillar, parts = draft.get("pillar"), draft.get("parts") or []
    if plan["pillar"] is None:
        errors.append(f"{d} is a {plan['weekday']}: no post on weekends")
    elif pillar != plan["pillar"]:
        errors.append(f"pillar must be {plan['pillar']!r} on {plan['weekday']}, got {pillar!r}")
    if draft.get("day") != plan["weekday"][:3]:
        errors.append(f"day must be {plan['weekday'][:3]!r}")

    # Format and length
    n = len(parts)
    if n == 0 or not all(isinstance(p, str) and p.strip() for p in parts):
        errors.append("parts must be a non-empty list of non-empty strings")
        parts = [p for p in parts if isinstance(p, str)]
    if plan["parts"] and n not in plan["parts"]:
        errors.append(f"{plan['weekday']} allows {plan['parts']} part(s), got {n}")
    if pillar == "what_changed" and n > 1 and st.get("wed_thread_last_2_weeks"):
        errors.append("a Wednesday thread already ran in the last 2 weeks: post a single")
    fmt = "single" if n == 1 else "thread"
    if draft.get("format") != fmt:
        errors.append(f"format must be {fmt!r} for {n} part(s)")
    counts = [weighted(p) for p in parts]
    info["weighted_counts"] = counts
    for i, c in enumerate(counts):
        lo = SINGLE_MIN if n == 1 else THREAD_PART_MIN
        if not lo <= c <= MAX_CHARS:
            errors.append(f"part {i + 1} is {c} weighted chars, must be {lo} to {MAX_CHARS}")

    # Part 1 rules
    if parts:
        first = parts[0].strip().splitlines()[0] if parts[0].strip() else ""
        info["first_line_chars"] = len(first)
        if len(first) >= 100:
            errors.append(f"first line is {len(first)} chars, must be under 100")
        if first.startswith("#"):
            errors.append("part 1 starts with a hashtag")
        if re.search(r"\bthread\b", parts[0], re.I):
            errors.append("the word 'thread' in part 1 (only the Friday cover image may say it)")
    for i, p in enumerate(parts):
        if COUNTER_RE.search(p):
            errors.append(f"part {i + 1}: '1/6' style counter or list number")
        if URL_RE.search(p):
            errors.append(f"part {i + 1}: URL in the post body (links go in the first reply)")
        errors += text_checks(f"part {i + 1}", p)
    tags = [t.lower() for p in parts for t in re.findall(r"(?<![\w#])#\w+", p)]
    if len(tags) > 1:
        errors.append(f"{len(tags)} hashtags, max 1")
    for t in tags:
        if t not in HASHTAGS_OK:
            errors.append(f"hashtag {t} not allowed (only #ShopifySEO #EcommerceSEO #WooCommerce)")
    for k in ("topic", "keyword"):
        if not draft.get(k):
            errors.append(f"{k} missing")
        else:
            errors += text_checks(k, draft[k])
    kw = (draft.get("keyword") or "").lower()
    if kw and kw not in " ".join(parts).lower():
        errors.append(f"keyword {draft['keyword']!r} is not in the post copy")

    # Questions
    q = ends_with_question(parts)
    info["question"] = "yes" if q else "no"
    if pillar == "myth_or_mistake" and not q:
        errors.append("Thursday must end with a question")
    if plan["pillar"]:
        need = 3 - st.get("questions_this_week", 0)
        left = 5 - d.weekday()
        if need >= left and not q:
            errors.append(f"only {st.get('questions_this_week', 0)} question post(s) so far this week, this one must end with a question")

    # Topic repeat
    tk = draft.get("topic_key")
    if not tk:
        errors.append("topic_key missing")
    elif tk in st.get("topic_keys_60d", []):
        errors.append(f"topic_key {tk!r} was used in the last 60 days")

    # Sources and numbers
    sources = {s.get("id"): s for s in draft.get("sources", [])}
    if not sources:
        errors.append("at least one source opened in this run is required")
    for sid, s in sources.items():
        for k in ("id", "name", "url", "date", "quote"):
            if not s.get(k):
                errors.append(f"source {sid}: {k} missing")
        if s.get("name") and ", " not in s["name"]:
            errors.append(f"source {sid}: name must be 'Publisher, page title'")
        if s.get("url") and not str(s["url"]).startswith("http"):
            errors.append(f"source {sid}: url must be a full URL")
        try:
            date.fromisoformat(s.get("date", ""))
        except ValueError:
            errors.append(f"source {sid}: date must be YYYY-MM-DD")
    numbers = draft.get("numbers") or {}
    for tok in sorted({t for p in parts for t in NUM_RE.findall(p)}):
        entry = numbers.get(tok, numbers.get(tok.rstrip("%")))
        if entry is None:
            errors.append(f"number {tok!r} has no entry in numbers")
        elif isinstance(entry, dict):
            if entry.get("kind") != "count" or not entry.get("note"):
                errors.append(f"number {tok!r}: use a source id, or kind 'count' with a note")
        elif entry not in sources:
            errors.append(f"number {tok!r} points to unknown source {entry!r}")
        elif tok.rstrip("%") not in sources[entry].get("quote", ""):
            errors.append(f"number {tok!r} is not in the quote of {entry} (use the page's own words)")

    # First reply
    fr = draft.get("first_reply") or {}
    ct = fr.get("cta_type")
    art = draft.get("source_article")
    if pillar == "website_thread":
        want = "article" if art else "checklist"
        if ct != want:
            errors.append(f"Friday CTA must be {want!r}")
    elif ct and ct == st.get("last_cta_type"):
        errors.append(f"cta_type {ct!r} was used last time, rotate")
    if art and not str(art).startswith("https://afrazalam.com/"):
        errors.append("source_article must be an https://afrazalam.com/ page")
    try:
        reply = x_reply.build(draft)
        info["reply_text"] = reply
        info["reply_weighted"] = weighted(reply)
        if info["reply_weighted"] > MAX_CHARS:
            errors.append("first reply is over 280 weighted chars")
        if any(dd in reply for dd in DASHES):
            errors.append("first reply: em or en dash")
    except ValueError as e:
        errors.append(f"first reply: {e}")
    info["cta_type"], info["utm_campaign"] = ct, pillar

    # Image
    img = draft.get("image")
    want_img = plan.get("image")
    if not want_img and img:
        errors.append(f"{plan['weekday']} is text only, image must be null")
    if want_img and not img:
        errors.append(f"{plan['weekday']} needs an image ({want_img})")
    if img and want_img:
        lay = img.get("layout")
        if lay not in want_img.split("|"):
            errors.append(f"image.layout must be one of {want_img}, got {lay!r}")
        if pillar == "image_card" and lay and lay == st.get("last_image_layout"):
            errors.append(f"image.layout {lay!r} was the last image layout, rotate")
        alt = (img.get("alt_text") or "").strip()
        sentences = [s for s in re.split(r"(?<=[.?])\s+", alt) if s]
        if not alt:
            errors.append("image.alt_text missing")
        else:
            if len(sentences) != 1 or not alt.endswith("."):
                errors.append("alt text must be one sentence ending with a full stop")
            if kw and kw not in alt.lower():
                errors.append(f"alt text must contain the keyword {draft.get('keyword')!r}")
            if len(alt) > 1000:
                errors.append("alt text over 1000 chars")
            errors += text_checks("alt text", alt)
        for _, t in render_card.card_texts(img):
            errors += text_checks("image text", t)
        mpath = draft_dir / "render_manifest.json"
        if not mpath.exists():
            errors.append("no render_manifest.json: run render_card.py first")
        else:
            m = json.loads(mpath.read_text(encoding="utf-8"))
            if not m.get("ok"):
                errors.append(f"render QA failed: {m.get('errors')}")
            if m.get("layout") != lay:
                errors.append("render_manifest layout does not match draft.json: render again")
            if m.get("logo_sha256") != hashlib.sha256(render_card.LOGO.read_bytes()).hexdigest():
                errors.append("logo hash does not match inputs/brand/AAMS_Logo_Horizontal_OnDark.png")
            if m.get("size") != [render_card.W, render_card.H]:
                errors.append(f"image size {m.get('size')}, expected 1080 x 1350")
            for k in ("image", "preview"):
                if not m.get(k) or not Path(m[k]).exists():
                    errors.append(f"rendered {k} file missing")
            if m.get("card_text") != [t for _, t in render_card.card_texts(img)]:
                errors.append("card text changed since the render: render again")
    return {"ok": not errors, "errors": errors, "warnings": warns, "info": info}


def main(path: str) -> int:
    p = Path(path)
    draft = json.loads(p.read_text(encoding="utf-8"))
    try:
        st = x_log.state(date.fromisoformat(draft.get("date_ist", "")))
    except ValueError:
        st = {}
    report = validate(draft, p.parent, st)
    out = json.dumps(report, indent=2, ensure_ascii=False)
    sys.stdout.buffer.write((out + "\n").encode("utf-8"))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
