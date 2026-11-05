"""
Headless research -> angle -> copy -> image -> publish pipeline for the
automated X (Twitter) posting flow. Rebuilt 2026-09-24 against
AAMS-X-Agent-Operating-Guide.md (see CLAUDE.md's "Autonomous Daily
Posting" section for the full history of decisions this reflects).

Runs inside a Modal container. All CONTAINER_ROOT paths point at files
bundled into the container image by modal_app.py's Image.add_local_dir/
file calls at `modal deploy` time - you must redeploy to pick up brand/
skill/competitor/logo edits made after the last deploy.

Key architectural facts worth knowing before editing this file:
- No thread-of-tools access here. The interactive Claude Code session has
  WebSearch, MCP connectors (Ubersuggest included), and a human at the
  approval gate. This script has none of that - it is a standalone Python
  process with only what's imported below. Ubersuggest specifically is
  NOT reachable from here (it's an MCP tool scoped to the chat session,
  not a server-side API this container can call) - the operating guide
  explicitly allows skipping an unavailable tool and logging the
  limitation, so that's what research() does.
- Links/CTAs never go in the post body, only as a follow-up reply - a
  link in the body measurably cuts reach (see memory/learnings.md's
  2026-09-08 research entries). This was re-confirmed by explicit user
  decision on 2026-09-24 when the new operating guide's looser phrasing
  ("add a link when it fits") would otherwise have suggested putting it
  in the body.
- Weekly state (image/text mix, thread cadence, post history, same-day
  idempotency) lives in a Modal Dict ("twitter-post-state"), not in any
  bundled file, since it has to persist and mutate across scheduled runs.
"""
import json
import os
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

CONTAINER_ROOT = Path("/bundled")
SKILL_MD_PATH = CONTAINER_ROOT / "SKILL.md"
CLAUDE_MD_PATH = CONTAINER_ROOT / "CLAUDE.md"
LEARNINGS_PATH = CONTAINER_ROOT / "learnings.md"
BRAND_DIR = CONTAINER_ROOT / "brand"
COMPETITORS_FILE = CONTAINER_ROOT / "urls.txt"
LOGO_WHITE_PATH = BRAND_DIR / "logo_white.png"        # for dark-background posts
LOGO_COLOR_PATH = BRAND_DIR / "logo_primary_color_transparent.png"  # for light-background posts

IMAGE_MODEL = "gemini-2.5-flash-image"
TEXT_MODEL = "claude-sonnet-5"
IMAGE_SIZE = 1200  # 1200x1200, 1:1 - per AAMS-X-Agent-Operating-Guide.md

IST = ZoneInfo("Asia/Kolkata")


def ist_now() -> datetime:
    return datetime.now(IST)


# --- Weekly topic balance (flexible coverage, never force a weak topic -
# see the operating guide's own caveat). Monday=0 .. Friday=4. ---
WEEKDAY_TOPIC_HINTS = {
    0: "SEO or local SEO diagnostic - what an owner should check or fix",
    1: "Google Ads or Meta Ads lesson - a practical account-level check",
    2: "A verified, dated platform update (Google/Meta/X/GA) if one is genuinely current and confirmed; otherwise an evergreen diagnostic. Wednesday is also the day a thread is most appropriate, if the topic genuinely needs 4-6 steps.",
    3: "Website conversion or measurement - what happens after the click",
    4: "Business growth lesson, a practical AI marketing workflow, or an evergreen insight",
}

# Live-news research queries, rotated by weekday hint plus a general pool.
TREND_QUERIES = [
    "SEO services Google ranking algorithm news this week",
    "Google Search Console Analytics news this week",
    "Meta Ads Facebook Instagram advertising news this week",
    "Google Ads performance marketing news this week",
    "AI Overviews AI search SEO news this week",
    "AI marketing automation workflow news this week",
    "performance marketing paid ads trends this week",
    "AI automation tools for marketing agencies news this week",
    "Google Search Central official announcement this week",
    "website conversion rate optimization measurement news this week",
]

# Website CTA, added as an automatic first reply (never in the tweet/thread
# body - see module docstring). Rotated so every post doesn't read
# identically.
CTA_REPLY_VARIANTS = [
    "More on how I approach this: afrazalam.com",
    "I write more on this at afrazalam.com",
    "More breakdowns like this: afrazalam.com",
    "I go deeper on this at afrazalam.com",
]

MAX_TWEET_CHARS = 280


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_brand_notes() -> str:
    notes = []
    priority = BRAND_DIR / "brand.md"
    if priority.exists():
        notes.append(_read(priority))
    for f in sorted(BRAND_DIR.glob("*.md")):
        if f != priority:
            notes.append(_read(f))
    return "\n".join(notes)[:4000]


# --- Persistent state (Modal Dict) ---------------------------------------
#
# _DRY_RUN_MODE is set at the top of run() and read by _state() so that
# dry-run test calls (character limits, thread cadence, image quota, logo
# variants) NEVER mutate the production counters/rotation/history the real
# scheduled pipeline depends on. A bug caught 2026-09-24: the first version
# of the dry-run acceptance check shared the real "twitter-post-state"
# Dict, so running the 5 test cases actually consumed this week's real
# image/thread quota before any live post had happened. Dry runs get their
# own isolated Dict instead.

_DRY_RUN_MODE = False


def _state():
    import modal
    name = "twitter-post-state-dryrun" if _DRY_RUN_MODE else "twitter-post-state"
    return modal.Dict.from_name(name, create_if_missing=True)


def _week_key(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


def get_week_counters() -> dict:
    """Returns this ISO week's {image, text, thread_used} counters, reset
    automatically when the week rolls over (target per the operating
    guide: 2-3 image posts and 2-3 text-only posts per week, threads at
    most about once a week)."""
    state = _state()
    wk = _week_key(ist_now())
    counters = state.get("week_counters")
    if not counters or counters.get("week") != wk:
        counters = {"week": wk, "image": 0, "text": 0, "thread_used": False}
        state["week_counters"] = counters
    return counters


def record_week_counters(used_image: bool, used_thread: bool) -> None:
    state = _state()
    counters = get_week_counters()
    if used_image:
        counters["image"] += 1
    else:
        counters["text"] += 1
    if used_thread:
        counters["thread_used"] = True
    state["week_counters"] = counters


def already_published_today() -> bool:
    """Same-day idempotency guard - a manual re-trigger or an overlapping
    schedule fire must never double-post."""
    state = _state()
    return state.get("last_published_date") == ist_now().date().isoformat()


def mark_published_today() -> None:
    _state()["last_published_date"] = ist_now().date().isoformat()


def load_post_history(limit: int = 15) -> list[dict]:
    return _state().get("post_log", [])[-limit:]


def append_post_history(entry: dict) -> None:
    state = _state()
    log = state.get("post_log", [])
    log.append(entry)
    state["post_log"] = log[-30:]  # cap so the Dict value stays small


# --- Research --------------------------------------------------------------

def research(weekday_hint: str) -> dict:
    """Live trend search (Firecrawl search, standing in for the interactive
    skill's WebSearch tool and, per the operating guide, a proxy for
    'search current X posts and questions' - there's no server-side X
    search API access here) plus a scrape of the user's own site and
    competitor sites. Ubersuggest demand-checking is explicitly skipped -
    not reachable from this container - and that limitation is logged
    into the returned dict rather than silently ignored, per the
    operating guide's own "log the limitation, never fabricate" rule."""
    from firecrawl import FirecrawlApp

    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

    weekday_queries = [q for q in TREND_QUERIES if any(
        w in q.lower() for w in weekday_hint.lower().split() if len(w) > 4
    )]
    query = random.choice(weekday_queries or TREND_QUERIES)
    search_results = app.search(query, limit=6)
    trend_hits = [
        {"title": r.title, "description": r.description, "url": r.url}
        for r in (search_results.web or [])
    ]

    urls = [
        line.strip()
        for line in _read(COMPETITORS_FILE).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    scraped = []
    for url in urls:
        try:
            doc = app.scrape(url, formats=["markdown"])
            scraped.append({
                "url": url,
                "title": doc.metadata.title if doc.metadata else "",
                "markdown": (doc.markdown or "")[:3000],
            })
        except Exception as e:  # noqa: BLE001
            scraped.append({"url": url, "error": str(e)})

    return {
        "query": query,
        "weekday_hint": weekday_hint,
        "trend_hits": trend_hits,
        "scraped_sites": scraped,
        "limitations": [
            "Ubersuggest demand-check not available from this automated "
            "container (MCP-tool only, not a server-callable API) - "
            "skipped per the operating guide's own allowance."
        ],
    }


# --- Copy -------------------------------------------------------------------

def pick_angle_and_write_post(
    research_results: dict, weekday_hint: str, recent_history: list[dict],
    week_counters: dict, force_format: str | None = None,
) -> dict:
    """One Anthropic Messages API call, forced into a tool call. System
    prompt bundles the full (untruncated) CLAUDE.md, SKILL.md and
    learnings.md so this stays in sync with the interactive skill's rules
    - see the 2026-09-08 bug note in memory/learnings.md about why these
    are no longer aggressively truncated."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    claude_md = _read(CLAUDE_MD_PATH)
    skill_md = _read(SKILL_MD_PATH)
    learnings = _read(LEARNINGS_PATH)
    learnings_tail = learnings[-12000:] if len(learnings) > 12000 else learnings

    history_lines = "\n".join(
        f"- {h.get('date', '?')} ({h.get('weekday', '?')}): {h.get('angle', '?')} "
        f"[{h.get('format', '?')}, {h.get('image_type', 'text-only')}]"
        for h in recent_history
    ) or "none yet"

    thread_allowed = not week_counters.get("thread_used", False)
    if force_format == "thread":
        format_instruction = (
            "TEST OVERRIDE: you MUST use format='thread' with 4-6 real, "
            "connected thread parts (not a single post relabeled) - this "
            "run exists specifically to exercise the thread code path."
        )
    elif force_format == "single":
        format_instruction = "TEST OVERRIDE: you MUST use format='single' for this run."
    else:
        format_instruction = (
            "A thread is allowed today if the topic genuinely needs 4-6 "
            "connected steps - not a quota, use it only when it's clearly "
            "better than one post."
            if thread_allowed else
            "A thread was already used this week - default to a single "
            "post unless there is an exceptionally strong reason not to."
        )

    system_prompt = f"""You are drafting one day's X (Twitter) publication for Afraz Alam's
profile, representing him as a digital marketing consultant. Follow the
project's own rules exactly.

--- CLAUDE.md (project rules, including "X Copy Rules") ---
{claude_md}

--- .claude/skills/twitter-post/SKILL.md ---
{skill_md}

--- memory/learnings.md (accumulated rules, most recent entries kept if truncated) ---
{learnings_tail}

--- Brand voice notes ---
{load_brand_notes()}

--- Today's weekday topic hint (flexible coverage, never force a weak topic
just to fill this category - pick the strongest real angle available) ---
{weekday_hint}

--- Recent posts (avoid near-duplicate topics, repeat hooks, or a streak
of the exact same template) ---
{history_lines}

Hard rules for this automated run:
- Exactly ONE publication today: either a single post, or a thread that
  REPLACES the single post (never both). {format_instruction}
- Every part (single post, or each thread part) must be under 280
  characters, counted as plain characters (no link will be in the body).
  X's hard limit is 280 - target 230-250 characters instead, as real
  working margin. Models reliably misjudge their own character count when
  aiming right at a ceiling, so treat 250 as the actual target and 280 as
  a limit you should never even approach. Count before finalizing: if a
  part is close to 250, cut a clause rather than push closer to 280.
- No external link or CTA in the body, ever - a link there measurably
  cuts reach. A website CTA is added automatically as a separate reply
  after publishing, so do not mention afrazalam.com or invite a site
  visit yourself. If today's angle is a verified, dated platform update
  with a real primary-source URL, name that source in
  `source_citation` (never invent one) so it can be added as a separate
  reply too - do not put the URL in the post itself.
- Recommend (in `wants_image`) whether an image would genuinely clarify
  this specific post - a comparison, checklist, process, or example.
  Text-only is valid and should stay part of the normal mix; don't
  default to "yes" out of habit. The final image/text decision is made
  in code against this week's target mix, your recommendation is input,
  not final.
- Never invent a case study, screenshot, metric, "10X" claim, or
  guarantee. Label a platform statement as fact only when it's grounded
  in the research below; if you're offering a lesson or interpretation
  rather than a confirmed fact, the post should read that way, not as an
  asserted announcement.
- A question or invitation to disagree is a strong, proven engagement
  pattern (see the 2026-09-08 research in memory/learnings.md) - use one
  when it fits naturally, but don't force a bolted-on question onto a
  post that already stands complete on its own.
- 0-1 hashtags max, only if genuinely relevant.
- Ground the post in something real from the research below - if the
  research is thin, use a researched evergreen diagnostic or lesson
  rather than manufacturing urgency around weak news.
- Rotate templates/angles rather than repeating the most recent post's
  shape (see the recent posts list above).
"""

    user_prompt = (
        "Here is today's grounding research (a live trend search plus a "
        "scrape of the user's own site and competitor sites). Note any "
        "logged limitations (e.g. an unavailable research tool) and work "
        "around them rather than fabricating what they would have shown. "
        "Pick exactly ONE sharp, specific angle tied to something real in "
        "this research, then write the full publication.\n\n"
        + json.dumps(research_results, indent=2)[:12000]
    )

    tool_schema = {
        "name": "submit_post",
        "description": "Submit the finished X publication for today",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "string", "description": "One sentence describing the chosen angle"},
                "format": {"type": "string", "enum": ["single", "thread"]},
                "copy": {"type": "string", "description": "Full text if format is 'single'"},
                "thread": {
                    "type": "array", "items": {"type": "string"},
                    "description": "4-6 parts, in order, if format is 'thread'; each targeting 230-250 chars (280 is the hard limit, don't aim near it), part 1 understandable alone",
                },
                "wants_image": {"type": "boolean"},
                "image_prompt_core_idea": {
                    "type": "string",
                    "description": "Short description of the visual concept, used only if an image is included",
                },
                "source_citation": {
                    "type": ["object", "null"],
                    "properties": {
                        "url": {"type": "string"},
                        "title": {"type": "string"},
                    },
                    "description": "A real primary-source URL from the research, only for a verified dated platform update; null otherwise",
                },
                "is_verified_news": {
                    "type": "boolean",
                    "description": "True only if this post asserts a specific dated platform change grounded in the research; false for an evergreen lesson/diagnostic/opinion",
                },
            },
            "required": ["angle", "format", "wants_image", "image_prompt_core_idea", "is_verified_news"],
        },
    }

    response = client.messages.create(
        model=TEXT_MODEL,
        max_tokens=2000,
        system=system_prompt,
        tools=[tool_schema],
        tool_choice={"type": "tool", "name": "submit_post"},
        messages=[{"role": "user", "content": user_prompt}],
    )

    for block in response.content:
        if block.type == "tool_use":
            post = block.input
            if post["format"] == "single" and not post.get("copy"):
                raise RuntimeError("submit_post returned format=single with no copy")
            if post["format"] == "thread" and not post.get("thread"):
                raise RuntimeError("submit_post returned format=thread with no thread parts")
            return post

    raise RuntimeError("Claude did not return a submit_post tool call")


def shorten_part(client, original: str, target_max: int = 250) -> str:
    """Focused edit call: shorten ONE specific over-limit part, preserving
    meaning, rather than regenerating the whole post and risking a
    different part drifting over the limit instead. Empirically more
    reliable than asking for a full regeneration (2026-09-24 dry-run
    testing: full-post retries still overshot ~40% of the time even with
    explicit guidance; this targeted approach edits the actual offending
    text down instead of writing something new from scratch)."""
    response = client.messages.create(
        model=TEXT_MODEL,
        max_tokens=300,
        system=(
            "You edit text to fit under a strict character limit while "
            "keeping the same meaning, tone, and voice. Output ONLY the "
            "edited text, nothing else - no preamble, no quotes around it."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"This text is {len(original)} characters. It must be under "
                f"{target_max} characters (a hard platform limit is 280, "
                f"but target {target_max} for real margin). Cut clauses or "
                "tighten phrasing, don't just truncate mid-sentence. Keep "
                f"the same point and voice.\n\nTEXT:\n{original}"
            ),
        }],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def shorten_violating_parts(post: dict) -> dict:
    """Runs shorten_part() on just the parts that are over the limit,
    leaving everything else in `post` untouched."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if post["format"] == "thread":
        parts = list(post["thread"])
        for i, part in enumerate(parts):
            if len(part) > MAX_TWEET_CHARS:
                parts[i] = shorten_part(client, part)
        post["thread"] = parts
    else:
        if len(post["copy"]) > MAX_TWEET_CHARS:
            post["copy"] = shorten_part(client, post["copy"])
    return post


def decide_image(post: dict, week_counters: dict) -> bool:
    """Deterministic weekly-quota enforcement (target 2-3 image / 2-3
    text-only per week) rather than leaving the mix entirely to the
    model's per-post judgment call."""
    if week_counters["image"] >= 3:
        return False
    if week_counters["text"] >= 3:
        return True
    return bool(post.get("wants_image"))


# --- Images (1200x1200, deterministic real-logo overlay) -------------------

IMAGE_PATTERNS = [
    {
        "name": "comparison_diagram",
        "structure": """
Pattern: COMPARISON DIAGRAM (e.g. a two-circle Venn diagram, or a clean
split comparison chart) - a real functioning diagram doing the
explaining, not decoration.
1. Bold question or contrast headline at the top (a few words)
2. The diagram itself, with 2-3 short labeled items per side/zone
3. Minimal extra decoration - the diagram is the visual""",
    },
    {
        "name": "stat_grid",
        "structure": """
Pattern: STAT/PROOF GRID.
1. Bold large headline - the value prop or a number-led claim, a few words
2. A grid of 2-4 icon-badge stat callouts (a number + a short label each)
3. One visual motif tied to the post's actual topic""",
    },
    {
        "name": "before_after_split",
        "structure": """
Pattern: BEFORE/AFTER SPLIT.
1. Bold headline posing the problem or the shift (a few words)
2. A clear split-screen: "before"/"old" state (muted, 1-2 short
   pain-point labels) vs "after"/"new" state (vivid, 1-2 benefit labels)""",
    },
    {
        "name": "checklist_hook",
        "structure": """
Pattern: QUESTION-HOOK CHECKLIST.
1. A punchy question or pain-point headline at the top (max 6-8 words)
2. A checklist of 3-4 short reason/fix rows, each with a DISTINCT small
   icon matched to its meaning (not a repeated plain checkmark)""",
    },
    {
        "name": "single_stat_hero",
        "structure": """
Pattern: SINGLE BOLD STAT (use when the core idea is genuinely one number).
1. One very large number or percentage as the dominant focal point
2. A short 1-2 line label under it explaining what the number means
3. A simple supporting visual (a small chart line, an icon, an arrow)""",
    },
    {
        "name": "flow_steps",
        "structure": """
Pattern: FLOW / PROCESS STEPS (e.g. search -> call -> booking).
1. Bold headline (a few words)
2. 3 connected step icons in circles, joined by arrows, one short label
   under each
3. One short closing line under the flow""",
    },
]


def get_next_image_pattern() -> dict:
    state = _state()
    idx = state.get("image_pattern_index", 0) % len(IMAGE_PATTERNS)
    state["image_pattern_index"] = (idx + 1) % len(IMAGE_PATTERNS)
    return IMAGE_PATTERNS[idx]


def get_next_variant() -> str:
    """Alternates dark/light so the feed doesn't read as one palette."""
    state = _state()
    idx = state.get("variant_index", 0)
    state["variant_index"] = 1 - idx
    return "dark" if idx == 0 else "light"


def generate_image(core_idea: str, pattern: dict, variant: str) -> bytes:
    """Gemini generates the background/design only - explicitly told not
    to draw any logo or wordmark, since that gets composited in
    deterministically afterward (composite_logo) per the operating
    guide's "never let a model redraw the logo" rule."""
    from google import genai

    client = genai.Client(api_key=os.environ.get("GOOGLE_AI_STUDIO_API_KEY") or os.environ["GEMINI_API_KEY"])

    if variant == "dark":
        palette_line = (
            "Deep navy/near-black background, a restrained teal/emerald "
            "accent color, readable white/light text."
        )
    else:
        palette_line = (
            "Opaque white or very light neutral background, charcoal/dark "
            "navy text, a restrained teal accent color."
        )

    prompt = (
        f"Create a {IMAGE_SIZE}x{IMAGE_SIZE} (1:1 square) image for an X "
        "(Twitter) post by a digital marketing consultant.\n"
        f"Core idea: {core_idea}\n"
        f"{palette_line}\n"
        f"{pattern['structure']}\n"
        "Clean bold sans-serif text, confident and modern, minimal clutter, "
        "generous safe margins. Leave the bottom ~15% of the canvas visually "
        "clear/uncluttered (a plain background band) - a logo will be "
        "composited into that space afterward, so do NOT draw any logo, "
        "wordmark, 'Afraz Alam' text, or brand mark yourself anywhere in "
        "the image. Every on-image text label must be short (a few words), "
        "never a full sentence or a fake paragraph - longer text reliably "
        "garbles in image generation. Do not draw fake charts, platform "
        "icons, or a decorative button. No spelling errors, no duplicated "
        "text, no people."
    )

    MAX_ATTEMPTS = 3
    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.models.generate_content(model=IMAGE_MODEL, contents=[prompt])
        candidate = response.candidates[0] if response.candidates else None
        parts = candidate.content.parts if (candidate is not None and candidate.content is not None) else None
        if parts:
            for part in parts:
                if getattr(part, "inline_data", None) is not None:
                    return _force_square_size(part.inline_data.data)
    raise RuntimeError(f"Gemini returned no image after {MAX_ATTEMPTS} attempts")


def _force_square_size(image_bytes: bytes) -> bytes:
    """Gemini doesn't reliably honor an exact pixel size from a text
    prompt (observed 2026-09-24: asked for 1200x1200, got 1024x1024
    consistently) - resize deterministically afterward so the final
    export always matches the operating guide's 1200x1200 spec exactly,
    rather than trusting the model's literal output dimensions."""
    import io
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if img.size != (IMAGE_SIZE, IMAGE_SIZE):
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def composite_logo(image_bytes: bytes, variant: str) -> bytes:
    """Deterministic overlay of the real logo file bytes - never an AI
    approximation. White wordmark on dark-variant images, the original
    colorful wordmark on light-variant images. Preserves aspect ratio,
    placed bottom-left with a safe margin."""
    import io
    from PIL import Image

    logo_path = LOGO_WHITE_PATH if variant == "dark" else LOGO_COLOR_PATH
    if not logo_path.exists():
        raise RuntimeError(f"Logo asset missing: {logo_path} - stopping image creation rather than publishing without it")

    base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    target_w = int(base.width * 0.30)
    scale = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * scale)), Image.LANCZOS)

    margin = int(base.width * 0.045)
    pos = (margin, base.height - logo.height - margin)
    base.alpha_composite(logo, pos)

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG")
    return out.getvalue()


# --- Publish -----------------------------------------------------------------

def _tweepy_clients():
    import tweepy
    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    return api_v1, client_v2


def post_parts(post: dict) -> list[str]:
    return post["thread"] if post["format"] == "thread" else [post["copy"]]


def check_char_limits(post: dict) -> list[str]:
    """Plain-character count against X's 280 limit. Since links/CTAs never
    go in the body (see module docstring), there's no t.co-shortening or
    surrogate-pair edge case to model - a simple len() check is accurate
    here. Returns a list of violation strings, empty if everything's within
    limits."""
    violations = []
    for i, part in enumerate(post_parts(post)):
        if len(part) > MAX_TWEET_CHARS:
            over_by = len(part) - MAX_TWEET_CHARS
            violations.append(
                f"part {i + 1}/{len(post_parts(post))} is {len(part)} chars, "
                f"{over_by} OVER the {MAX_TWEET_CHARS} limit - cut at least "
                f"{over_by + 15} characters (not just {over_by}, leave margin): {part!r}"
            )
    return violations


def publish(post: dict, image_bytes: bytes | None) -> dict:
    """Publishes a single post or a thread. Image (if any) attaches to the
    first part only. Returns {tweet_id (last part's, for reply-chaining),
    first_url, all_urls}."""
    import io

    api_v1, client_v2 = _tweepy_clients()
    media_ids = None
    if image_bytes is not None:
        media = api_v1.media_upload(filename="image.png", file=io.BytesIO(image_bytes))
        media_ids = [media.media_id]

    parts = post_parts(post)
    violations = check_char_limits(post)
    if violations:
        raise RuntimeError(f"Character limit violations, refusing to publish: {violations}")

    urls = []
    previous_id = None
    for i, text in enumerate(parts):
        kwargs = {"text": text}
        if i == 0 and media_ids:
            kwargs["media_ids"] = media_ids
        if previous_id:
            kwargs["in_reply_to_tweet_id"] = previous_id
        response = client_v2.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        urls.append(f"https://x.com/i/web/status/{tweet_id}")
        previous_id = tweet_id

    return {"tweet_id": previous_id, "first_url": urls[0], "all_urls": urls}


def publish_reply(tweet_id: str, text: str) -> dict:
    _, client_v2 = _tweepy_clients()
    response = client_v2.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
    reply_id = response.data["id"]
    return {"tweet_id": reply_id, "text": text, "url": f"https://x.com/i/web/status/{reply_id}"}


# --- Notifications -----------------------------------------------------------

def send_email(subject: str, html: str, image_bytes: bytes | None = None, image_filename: str = "post_image.png") -> None:
    import base64
    payload = {
        "sender": {"name": "AAMS Post Bot", "email": "hello@afrazalam.com"},
        "to": [{"email": os.environ["NOTIFICATION_EMAIL"]}],
        "subject": subject,
        "htmlContent": html,
    }
    if image_bytes is not None:
        payload["attachment"] = [{"content": base64.b64encode(image_bytes).decode("ascii"), "name": image_filename}]
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"accept": "application/json", "api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json"},
        json=payload,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"Brevo email failed ({resp.status_code}): {resp.text}")


def notify(subject: str, html: str, image_bytes: bytes | None = None) -> None:
    if not (os.environ.get("BREVO_API_KEY") and os.environ.get("NOTIFICATION_EMAIL")):
        print(f"[notify] BREVO_API_KEY / NOTIFICATION_EMAIL not set, skipping: {subject}")
        return
    try:
        send_email(subject, html, image_bytes)
    except Exception as e:  # noqa: BLE001
        print(f"[notify] email failed: {e}")


# --- Orchestration -----------------------------------------------------------

def run(dry_run: bool = False, force_case: dict | None = None) -> dict:
    """force_case lets the dry-run entrypoint pin specific fields (format,
    wants_image/variant) to exercise the operating guide's five
    acceptance cases deterministically instead of whatever the model
    would pick today."""
    global _DRY_RUN_MODE
    _DRY_RUN_MODE = dry_run

    now = ist_now()
    weekday = now.weekday()

    if not dry_run and already_published_today():
        msg = f"Already published today ({now.date().isoformat()} IST) - skipping to avoid a duplicate."
        print(f"[run] {msg}")
        return {"status": "skipped_duplicate", "message": msg}

    weekday_hint = WEEKDAY_TOPIC_HINTS.get(weekday, WEEKDAY_TOPIC_HINTS[4])
    week_counters = get_week_counters()
    recent_history = load_post_history()

    if force_case and force_case.get("skip_research"):
        research_results = force_case["research_override"]
    else:
        research_results = research(weekday_hint)

    force_format = (force_case or {}).get("format")
    post = pick_angle_and_write_post(
        research_results, weekday_hint, recent_history, week_counters,
        force_format=force_format,
    )

    # Self-correction retry: the model doesn't always reliably honor the
    # 280-char instruction on its own (caught empirically 2026-09-24 during
    # dry-run testing). A full-post regeneration retry converged only
    # ~60% of the time - the more reliable fix is a focused edit pass that
    # shortens just the specific over-limit part(s), via shorten_part().
    violations = check_char_limits(post)
    for attempt in range(3):
        if not violations:
            break
        print(f"[run] character limit violations (targeted-shorten attempt {attempt + 1}/3): {violations}")
        post = shorten_violating_parts(post)
        violations = check_char_limits(post)
    if violations:
        raise RuntimeError(f"Character limit violations persisted after retries, refusing to publish: {violations}")

    if force_case and "wants_image" in force_case:
        post["wants_image"] = force_case["wants_image"]

    use_thread = post["format"] == "thread"
    use_image = decide_image(post, week_counters)

    variant = force_case.get("variant") if force_case and force_case.get("variant") else get_next_variant()
    image_bytes = None
    pattern_name = None
    if use_image:
        pattern = get_next_image_pattern()
        pattern_name = pattern["name"]
        raw_image = generate_image(post["image_prompt_core_idea"], pattern, variant)
        image_bytes = composite_logo(raw_image, variant)

    log_entry = {
        "date": now.date().isoformat(),
        "time_ist": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
        "angle": post["angle"],
        "format": post["format"],
        "image_type": pattern_name or "text-only",
        "variant": variant if use_image else None,
        "is_verified_news": post.get("is_verified_news", False),
        "source_citation": post.get("source_citation"),
        "limitations": research_results.get("limitations", []),
    }

    if dry_run:
        char_violations = check_char_limits(post)
        log_entry["status"] = "dry_run"
        log_entry["char_limit_ok"] = not char_violations
        print(f"[dry-run] {json.dumps(log_entry, indent=2)}")
        print(f"[dry-run] COPY:\n{post.get('copy') or json.dumps(post.get('thread'), indent=2)}")
        if char_violations:
            print(f"[dry-run] CHARACTER LIMIT VIOLATIONS: {char_violations}")
        else:
            print(f"[dry-run] character limits: OK (all {len(post_parts(post))} part(s) under {MAX_TWEET_CHARS})")
        return {
            "status": "dry_run", "post": post, "log_entry": log_entry,
            "char_violations": char_violations,
            "image_bytes_len": len(image_bytes) if image_bytes else 0, "_image_bytes": image_bytes,
        }

    result = publish(post, image_bytes)
    print(f"Published: {result}, format={post['format']}, image={pattern_name or 'text-only'}")
    mark_published_today()
    record_week_counters(used_image=use_image, used_thread=use_thread)
    log_entry["status"] = "published"
    log_entry["url"] = result["first_url"]
    append_post_history(log_entry)

    try:
        if post.get("source_citation") and post["source_citation"].get("url"):
            src = post["source_citation"]
            src_result = publish_reply(result["tweet_id"], f"Source: {src.get('title', '')[:100]} - {src['url']}")
            print(f"Source reply published: {src_result}")
    except Exception as e:  # noqa: BLE001
        print(f"publish_reply (source) failed (main publish still stands): {e}")

    try:
        cta_result = publish_reply(result["tweet_id"], random.choice(CTA_REPLY_VARIANTS))
        print(f"CTA reply published: {cta_result}")
    except Exception as e:  # noqa: BLE001
        print(f"publish_reply (CTA) failed (main publish still stands): {e}")

    notify(
        subject=f"Published to X: {post['angle'][:60]}",
        html=f"""
            <p><b>Published automatically.</b> <a href="{result['first_url']}">{result['first_url']}</a></p>
            <p><b>Format:</b> {post['format']} | <b>Image:</b> {pattern_name or 'text-only'}</p>
            <p><b>Angle:</b> {post['angle']}</p>
            <pre style="white-space:pre-wrap;font-family:sans-serif">{post.get('copy') or chr(10).join(post.get('thread', []))}</pre>
        """,
        image_bytes=image_bytes,
    )

    return {"status": "published", "result": result, "log_entry": log_entry}
