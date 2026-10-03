#!/usr/bin/env python3
"""
Pre-publish validator for the AAMS X Post routine (docs/X-ROUTINE-MIGRATION.md
section 6). Reads one draft.json, prints a JSON report, exits 0 only when
there are zero errors. Warnings never block.

Usage:
    python automation/routine/validate_post.py outputs/<date>_<slug>/draft.json

draft.json shape:
{
  "date_ist": "2026-10-05", "day": "Mon", "reader": "home-service",
  "format": "single" | "thread",
  "topic": "Free-text topic", "topic_key": "gbp-primary-category",
  "parts": ["post text"]  (thread: 4-6 parts),
  "sources": [{"id": "s1", "name": "...", "url": "https://...",
               "date": "YYYY-MM-DD", "quote": "source's own wording"}],
  "numbers": {"25": {"source": "s1"}, "10": {"kind": "example", "note": "..."}},
  "first_reply": {"source_url": "https://..." | null, "cta": "<one CTA_REPLY_VARIANTS line>"},
  "image": null | {"layout": "...", "variant": "dark" | "light",
                   "headline": "...", "labels": ["...", ...], "alt_text": "...",
                   "manifest": "outputs/<date>_<slug>/render_manifest.json"}
}
"""
import ast
import hashlib
import json
import re
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")
from twitter_text import parse_tweet  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LOG_PATH = REPO / "memory" / "x-post-log.md"
PIPELINE_PATH = REPO / "automation" / "pipeline.py"
LOGOS = {
    "dark": REPO / "inputs" / "brand" / "logo_white.png",
    "light": REPO / "inputs" / "brand" / "logo_primary_color_transparent.png",
}
LAYOUTS = {"comparison", "stat_grid", "before_after", "checklist", "single_stat"}

DASHES = {chr(0x2014): "em dash", chr(0x2013): "en dash"}
BANNED_OPENERS = ["just a thought", "hear me out", "interesting thread", "thread:", "a thread", "\U0001f9f5"]
LINK_RE = re.compile(
    r"(https?://|www\.)|\b[a-z0-9-]+\.(com|net|org|io|co|ai|in|us|app|dev|ly|me|biz|info)\b",
    re.IGNORECASE,
)
HASHTAG_RE = re.compile(r"(?<!\w)#\w+")
NUMBER_RE = re.compile(r"(?<![\w/])[$₹]?\d[\d,]*(?:\.\d+)?[%kKmMxX]?")
THREAD_MARKER_RE = re.compile(r"^\s*\d+\s*/\s*\d+")


def weighted(text: str) -> int:
    return parse_tweet(text).weightedLength


def norm_number(tok: str) -> str:
    tok = tok.strip().rstrip(".,")
    return tok.lstrip("$₹").replace(",", "").lower()


def cta_variants() -> list[str]:
    tree = ast.parse(PIPELINE_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CTA_REPLY_VARIANTS" for t in node.targets
        ):
            return list(ast.literal_eval(node.value))
    raise RuntimeError("CTA_REPLY_VARIANTS not found in automation/pipeline.py")


def log_rows() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    rows, header = [], None
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def main(path: str) -> int:
    draft = json.loads(Path(path).read_text(encoding="utf-8"))
    errors, warns, info = [], [], {}

    parts = draft.get("parts") or []
    fmt = draft.get("format")
    if fmt not in ("single", "thread"):
        errors.append(f"format must be single or thread, got {fmt!r}")
    if fmt == "single" and len(parts) != 1:
        errors.append(f"single post must have exactly 1 part, got {len(parts)}")
    if fmt == "thread" and not 4 <= len(parts) <= 6:
        errors.append(f"thread must have 4 to 6 parts, got {len(parts)}")
    if not parts:
        print(json.dumps({"ok": False, "errors": ["no parts"]}, indent=2))
        return 1

    reply = draft.get("first_reply") or {}
    image = draft.get("image")
    all_text = {f"part {i + 1}": p for i, p in enumerate(parts)}
    all_text["first_reply.cta"] = reply.get("cta") or ""
    if image:
        all_text["image.headline"] = image.get("headline", "")
        for i, lab in enumerate(image.get("labels", [])):
            all_text[f"image.label {i + 1}"] = lab
        all_text["image.alt_text"] = image.get("alt_text", "")
    all_text["topic"] = draft.get("topic", "")

    # 1. No em or en dashes anywhere.
    for where, text in all_text.items():
        for ch, name in DASHES.items():
            if ch in text:
                errors.append(f"{name} in {where}")

    # 2. Hook rules on part 1.
    first_line = parts[0].strip().splitlines()[0] if parts[0].strip() else ""
    info["first_line_chars"] = len(first_line)
    if len(first_line) >= 100:
        errors.append(f"first line is {len(first_line)} chars, must be under 100")
    low = parts[0].strip().lower()
    for b in BANNED_OPENERS:
        if low.startswith(b):
            errors.append(f"banned opener: {b!r}")
    if parts[0].strip().startswith("#"):
        errors.append("part 1 starts with a hashtag")

    # 3. No link in the body. Hashtags 0 or 1 across the whole publication.
    hashtags = 0
    for i, p in enumerate(parts):
        if LINK_RE.search(p):
            errors.append(f"link or domain in part {i + 1}: {LINK_RE.search(p).group(0)!r}")
        hashtags += len(HASHTAG_RE.findall(p))
    info["hashtags"] = hashtags
    if hashtags > 1:
        errors.append(f"{hashtags} hashtags, max 1")

    # 4. X weighted character counts.
    counts = [weighted(p) for p in parts]
    info["weighted_counts"] = counts
    for i, c in enumerate(counts):
        if c > 280:
            errors.append(f"part {i + 1} is {c} weighted chars, hard max 280")
    if fmt == "single":
        if counts[0] < 200:
            errors.append(f"single post is {counts[0]} weighted chars, below the 200 floor (target 230 to 250)")
        elif not 230 <= counts[0] <= 250:
            warns.append(f"single post is {counts[0]} weighted chars, target is 230 to 250")
    if fmt == "thread":
        for i, c in enumerate(counts):
            if c < 60:
                warns.append(f"thread part {i + 1} is only {c} chars")

    # 5. Every number has a logged source (or is a labelled worked example).
    sources = {s.get("id"): s for s in draft.get("sources", [])}
    for sid, s in sources.items():
        if not str(s.get("url", "")).startswith("http"):
            errors.append(f"source {sid} has no URL")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(s.get("date", ""))):
            errors.append(f"source {sid} has no YYYY-MM-DD date")
    numbers = {norm_number(k): v for k, v in (draft.get("numbers") or {}).items()}
    texts_with_numbers = list(parts)
    if image:
        texts_with_numbers += [image.get("headline", "")] + list(image.get("labels", []))
    seen = set()
    for text in texts_with_numbers:
        body = "\n".join(THREAD_MARKER_RE.sub("", ln) for ln in text.splitlines())
        for tok in NUMBER_RE.findall(body):
            key = norm_number(tok)
            if not key or key in seen:
                continue
            seen.add(key)
            entry = numbers.get(key)
            if entry is None:
                errors.append(f"number {tok!r} has no entry in 'numbers'")
            elif entry.get("source"):
                if entry["source"] not in sources:
                    errors.append(f"number {tok!r} points to unknown source {entry['source']!r}")
            elif entry.get("kind") == "example":
                if not entry.get("note"):
                    errors.append(f"number {tok!r} is a worked example but has no note")
            else:
                errors.append(f"number {tok!r} needs a source id or kind=example with a note")
    info["numbers_checked"] = sorted(seen)

    # 6. First reply: one reply, CTA from the rotation, not the same as the last published post.
    variants = cta_variants()
    cta = reply.get("cta")
    if cta not in variants:
        errors.append(f"first_reply.cta must be one of CTA_REPLY_VARIANTS, got {cta!r}")
    src_url = reply.get("source_url")
    if src_url and not str(src_url).startswith("http"):
        errors.append("first_reply.source_url must be a full URL or null")
    reply_text = (f"Source: {src_url}\n\n{cta}" if src_url else (cta or ""))
    info["first_reply_weighted"] = weighted(reply_text)
    if weighted(reply_text) > 280:
        errors.append("first reply exceeds 280 weighted chars")
    rows = log_rows()
    published = [r for r in rows if r.get("status", "").upper() == "PUBLISHED"]
    if published and published[-1].get("cta variant") == cta:
        errors.append("same CTA variant as the last published post, rotate")

    # 7. No repeat topic in the last 30 days.
    tk = draft.get("topic_key")
    if not tk:
        errors.append("topic_key missing")
    else:
        try:
            today = date.fromisoformat(draft.get("date_ist", ""))
        except ValueError:
            today = date.today()
            errors.append("date_ist missing or not YYYY-MM-DD")
        cutoff = today - timedelta(days=30)
        for r in published:
            try:
                d = date.fromisoformat(r.get("ist date", ""))
            except ValueError:
                continue
            if d >= cutoff and r.get("topic key") == tk:
                errors.append(f"topic_key {tk!r} already published on {d}")

    # 8. Day-of-week defaults (warnings only, the doc calls these defaults).
    day = draft.get("day")
    expected = {"Mon": "text", "Tue": "image", "Thu": "image", "Fri": "text"}
    if day in expected:
        has_img = bool(image)
        if expected[day] == "image" and not has_img:
            warns.append(f"{day} default is single post + image")
        if expected[day] == "text" and has_img:
            warns.append(f"{day} default is text only")
    if fmt == "thread" and day != "Wed":
        warns.append("threads are planned for Wednesday")
    if fmt == "thread":
        week_threads = 0
        try:
            today = date.fromisoformat(draft.get("date_ist", ""))
            monday = today - timedelta(days=today.weekday())
            for r in published:
                try:
                    d = date.fromisoformat(r.get("ist date", ""))
                except ValueError:
                    continue
                if monday <= d <= today and r.get("format") == "thread":
                    week_threads += 1
        except ValueError:
            pass
        if week_threads >= 1:
            errors.append("a thread was already published this week, max 1")

    # 9. Image checks.
    if image:
        if image.get("layout") not in LAYOUTS:
            errors.append(f"image.layout must be one of {sorted(LAYOUTS)}")
        if image.get("variant") not in LOGOS:
            errors.append("image.variant must be dark or light")
        labels = image.get("labels") or []
        if len(labels) > 3:
            errors.append(f"{len(labels)} image labels, max 3")
        if len(image.get("headline", "")) > 48:
            errors.append("image headline over 48 chars")
        for i, lab in enumerate(labels):
            if len(lab) > 32:
                errors.append(f"image label {i + 1} over 32 chars")
        alt = image.get("alt_text", "")
        if not 20 <= len(alt) <= 1000:
            errors.append("alt_text must be 20 to 1000 chars")
        man_path = image.get("manifest")
        if not man_path or not (REPO / man_path).exists():
            errors.append("render manifest missing, render the image first")
        else:
            man = json.loads((REPO / man_path).read_text(encoding="utf-8"))
            from PIL import Image as PILImage
            png = REPO / man["image"]
            with PILImage.open(png) as im:
                info["image_size"] = list(im.size)
                if im.size != (1200, 1200):
                    errors.append(f"image is {im.size}, must be 1200x1200")
                if im.mode not in ("RGB",):
                    errors.append(f"image mode {im.mode}, must be opaque RGB")
            expected_hash = hashlib.sha256(LOGOS[image["variant"]].read_bytes()).hexdigest()
            if man.get("logo_sha256") != expected_hash:
                errors.append("logo bytes do not match the original logo file for this variant")
            if man.get("variant") != image.get("variant") or man.get("layout") != image.get("layout"):
                errors.append("manifest variant/layout does not match draft")
            if man.get("headline") != image.get("headline") or man.get("labels") != labels:
                errors.append("rendered image text does not match the approved image text")
            if not man.get("fit_ok"):
                errors.append(f"text clipped or out of safe area: {man.get('fit_issues')}")
            if man.get("min_font_px", 0) < 34:
                errors.append(f"smallest text is {man.get('min_font_px')}px, unreadable at mobile size")
            if not (REPO / man.get("mobile_preview", "")).exists():
                errors.append("mobile preview missing")

    report = {"ok": not errors, "errors": errors, "warnings": warns, "info": info}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_post.py <draft.json>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
