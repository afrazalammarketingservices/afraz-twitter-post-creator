# CLAUDE.md — X (Twitter) Post Creator

> Read this before every task.

## What This Is

An agent that researches, writes, designs, and publishes posts (single tweets
or threads) to one X account (your personal profile, representing you as a
digital marketing consultant), end to end. Same shape as your Facebook Post
Creator kit, adapted for how X actually ranks and rewards content. The user
supplies:
1. **Brand kit** — colors, fonts, voice notes (in `inputs/brand/`, can point
   back at the same brand kit your Facebook/Instagram/LinkedIn kits use)
2. **Competitor / niche sites** — a list of URLs to scan for angles (in
   `inputs/competitors/urls.txt`)
3. **References** — post styles to match (in `inputs/references/`)
4. **Copy** — optional, a topic or a full draft (in `inputs/copy/`)

It scrapes for a real, current angle first (never invents trends or fake
data points), drafts the post copy (single tweet or thread), generates the
image with Gemini image generation, gets the user's approval, then publishes
directly to X via the X API. Output and a publish record land in
`outputs/<date>_<slug>/`.

## Commands

Setup (one-time):
```
pip install -r requirements.txt
cp .env.example .env   # then fill in the keys, never commit this file
```

There is no build, lint, or test suite in this repo; the only "run" surface
is the skill's three scripts, normally invoked by the skill itself, not
directly. To run a step in isolation for debugging:
```
python .claude/skills/twitter-post/scripts/scrape.py [--urls-file PATH]
python .claude/skills/twitter-post/scripts/generate_image.py --prompt "..." --slug "my-post" --index 1
python .claude/skills/twitter-post/scripts/publish_twitter.py --text "..." --images outputs/2026-08-27_x/image.png --slug "my-post"
python .claude/skills/twitter-post/scripts/publish_twitter.py --thread-file outputs/2026-08-27_x/thread.json --slug "my-post"
```
`publish_twitter.py` hits the live X API and posts to your real profile, so
only run it manually after the Step 5 approval gate has already been
satisfied, same as the Facebook kit would.

Note: `inputs/brand/`, `inputs/references/`, `inputs/photos/`, and
`inputs/copy/` are referenced throughout the skill but don't exist populated
on disk yet, only `inputs/competitors/urls.txt` does. Create them (or ask
the user for their content) the first time a step needs them; the fastest
path is pointing this kit at the same `inputs/brand/` folder your Facebook
kit already uses, so voice and colors stay consistent across every channel.

## How To Operate

When the user says "make a tweet", "post to X", "tweet this", "make a
thread", or `/twitter-post`:
- **Invoke the `twitter-post` skill immediately via the Skill tool.** Do not
  start a freeform conversation. The skill walks the 7-step flow below.

The skill is self-learning. It reads `memory/learnings.md` at the start of
every run and applies past learnings. It appends new ones after every run.

## Autonomous Daily Posting (enabled 2026-09-08, rebuilt 2026-09-24, moved to a Claude Code routine 2026-10-03)

> As of 2026-10-03 the scheduled path is the Claude Code routine **AAMS X
> Post**, not Modal. See the last bullet of this section and
> `docs/X-ROUTINE-MIGRATION.md`. The Modal notes below are history.

The user explicitly overrode the Step 5 approval gate for the **scheduled
Monday-Friday job only** (2026-09-08), then handed Claude a detailed
written operating guide - `AAMS-X-Agent-Operating-Guide.md` at the repo
root - and asked for the automation to be rebuilt against it (2026-09-24).
Both are real, informed, explicit decisions, not defaults. Read
`AAMS-X-Agent-Operating-Guide.md` for the full source spec; this section
tracks how each rule maps to code and what had to be adapted.

- **Schedule:** Monday-Friday, 8:30 PM IST (15:00 UTC) - changed from 7:30
  PM on 2026-09-24 per the operating guide's locked schedule. Runs
  entirely in Modal's cloud (not local cron/Task Scheduler) so it works
  with the user's machine off. See `automation/README.md`,
  `automation/modal_app.py`, `automation/pipeline.py`.
- **Format:** one publication a day - a single post, or a thread that
  REPLACES it (never both), roughly once a week when a topic genuinely
  needs 4-6 connected steps, not a quota. Reversed 2026-09-24 from the
  earlier "single tweet only, no threads" rule - the operating guide
  explicitly wants occasional threads; the unattended-risk concern that
  drove the original single-tweet-only decision is now handled by real
  validation instead (character-limit checking with a targeted-shorten
  retry, see below) rather than by avoiding threads altogether.
- **Weekday topic balance** (`pipeline.py`'s `WEEKDAY_TOPIC_HINTS`):
  Monday SEO/local SEO, Tuesday Google/Meta Ads lesson, Wednesday a
  verified platform update (or a thread if warranted), Thursday website
  conversion/measurement, Friday growth lesson/AI workflow/evergreen -
  flexible coverage, never forced onto a weak topic.
- **Image cadence: target 2-3 image posts and 2-3 text-only posts per
  week**, enforced in code (`decide_image()`) against a weekly counter in
  Modal Dict state, not left purely to the model's per-post judgment.
  Images are **1200x1200 (1:1)**, alternating dark/light variant, and the
  real logo file is composited on deterministically after generation
  (`composite_logo()`) - the image model is explicitly told never to draw
  a logo itself, matching the operating guide's "never let a model redraw
  the logo" rule. `logo_white.png` (dark backgrounds) and
  `logo_primary_color_transparent.png` (light backgrounds) are derived,
  pixel-perfect recolors of the original brand files in `inputs/brand/`,
  generated via direct image manipulation (not AI), since neither a
  pre-made white variant nor a truly-transparent color version existed
  before 2026-09-24 (the original "PRIMARY LOGO... Transparent version"
  file turned out to have no real alpha channel - white background baked
  into the RGB pixels - alpha was derived from a white-chroma-key). Gemini
  also doesn't reliably honor an exact pixel size from a text prompt
  (observed: asked for 1200x1200, consistently got 1024x1024) - resized
  deterministically afterward (`_force_square_size()`) rather than trusted.
- **Character-limit reliability (added 2026-09-24, load-bearing):** the
  model does not reliably self-count characters against X's 280 limit -
  empirically observed during dry-run testing at roughly a 40% first-pass
  violation rate, occasionally still over after a full-post regeneration
  retry. `pipeline.py` now targets 230-250 chars in the prompt (real
  margin below the 280 ceiling, not aiming at it) and, if a part still
  comes back over, runs up to 3 rounds of `shorten_violating_parts()` - a
  focused edit call that shortens only the specific offending part(s)
  rather than regenerating the whole post from scratch (more reliable:
  editing existing text down converged consistently in testing where full
  regeneration did not). If limits still aren't met after retries, `run()`
  raises rather than publishing something broken - a day with no post is
  an acceptable, honest outcome; a garbled or truncated one is not.
- **Same-day idempotency:** `already_published_today()` checks a Modal
  Dict before doing any work, so a manual re-trigger or an overlapping
  fire can never double-post.
- **Structured post history:** every real publish appends to a capped
  post-log in Modal Dict state (date, weekday, angle, format, image type,
  source citation, URL) - this is what `load_post_history()` feeds back
  into the next day's prompt to avoid near-duplicate topics or a streak of
  the same template, replacing the old learnings.md-heading-parsing
  approach.
- **Dry-run acceptance testing:** `modal run
  automation/modal_app.py::dry_run_acceptance` runs the operating guide's
  five named cases (verified update, evergreen fallback, thread, dark
  image, light image) against the real Anthropic/Gemini APIs but never
  calls the X publish endpoints, saving each case's copy + image to a
  `twitter-post-dryrun` Modal Volume for review. **Dry runs use a
  completely separate state Dict (`twitter-post-state-dryrun`) from the
  real pipeline** - a bug caught the same day: the first version of this
  shared the production Dict, so test runs were silently consuming real
  weekly image/thread quota before any live post had happened.
- **Ubersuggest is not reachable from the automated path.** It's an MCP
  tool scoped to an interactive Claude session, not a server-callable API
  the standalone Modal container can reach. `research()` explicitly skips
  it and logs that limitation into the research context every run, per the
  operating guide's own "if a tool is unavailable, continue with other
  evidence and log the limitation" allowance - this is a real, permanent
  architectural gap, not an oversight to revisit casually.
- **Every automated post gets an afrazalam.com CTA as an automatic first
  reply** (added 2026-09-08, reconfirmed 2026-09-24 when the operating
  guide's looser "add a link when it fits" phrasing could have been read
  as putting it in the body - explicit user decision was to keep the
  existing first-reply-only pattern instead). The CTA never goes in the
  post/thread body itself - a link there measurably cuts reach (see "X
  Copy Rules" below). If today's angle is a verified, dated platform
  update with a real primary source, a source-citation reply is added too
  (also never in the body). Both wrapped so a failed reply never blocks or
  undoes the main publish.
- **Research is scoped to the user's actual service lines** (SEO, Google
  Ads, Meta Ads, performance marketing, AI automation/AI marketing)
  rather than generic "digital marketing" - see `pipeline.py`'s
  `TREND_QUERIES`.
- **Ad-hoc runs stay gated.** When the user asks in a live conversation
  ("make a tweet", "post this", `/twitter-post`), Step 5 still applies and
  Claude still stops for explicit yes/no before publishing. The override
  is not a blanket removal of the approval gate, only the scheduled path.
- **X policy check (done 2026-09-08):** scheduling and publishing original
  posts through an OAuth-authorized tool, which this kit already uses, is
  within X's automation rules. No bot-account labeling is required for a
  named individual's own account posting their own original content; that
  labeling requirement applies to purely automated/feed-driven bot
  accounts, not this use case. Re-verify this if X's policy changes.
- **Reliability caveat, found 2026-09-24:** on this Modal plan tier, a
  scheduled function can go silently inactive for an extended period with
  no error and no notification - discovered when the schedule turned out
  to have fired only once in the two weeks after its original 2026-09-08
  deploy. A fresh `modal deploy` re-arms it. There is no automated
  detection of this yet; periodically check `modal app logs
  twitter-post-automation --since 7d` or the Modal dashboard's Logs tab
  rather than assuming silence means success. Setting up the optional FYI
  email (`BREVO_API_KEY` + `NOTIFICATION_EMAIL` in the secret bundle,
  still not configured as of 2026-09-24) would make a normal
  publish-failure far more visible, though it would not by itself catch
  this specific "schedule never fired at all" failure mode.
- **To pause or stop:** tell Claude to cancel the scheduled job, or run
  `modal app stop twitter-post-automation` directly. Reverting to
  manual-only is a one-line ask, not a re-negotiation.
- **Publishing moved to Claude Code routine AAMS X Post on 2026-10-03;
  Modal app twitter-post-automation retired, keep stopped.** Never run
  `modal deploy` or `modal run` for it and never delete it. The routine
  (`trig_01PDuGZaH72RJ8kCcZL2RNxH`, `CRON_TZ=Asia/Kolkata 50 19 * * 1-5`,
  publishes 8:30 PM IST, hard stop 9:30 PM IST) runs in the environment
  "AAMS Twitter (X)" (Network Full, only the 4 `X_*` variables). It was
  created disabled and is enabled only by Afraz after dry-run approval.
  Never attach it to the FIND N FORM environment or any other business's
  environment. Everything above this bullet describes the retired Modal
  pipeline and is kept for history; the live spec is
  `docs/X-ROUTINE-MIGRATION.md` and `automation/routine/ROUTINE-PROMPT.md`,
  with state in `memory/x-post-log.md`.

## The 7-Step Flow

1. **Research** — `scripts/scrape.py` pulls fresh content from the user's
   own site and the URLs in `inputs/competitors/urls.txt` via Firecrawl, so
   the post is grounded in something real, not a generic AI topic or a made
   up statistic.
2. **Angle + format decision** — Claude reads the scraped material and
   proposes ONE sharp angle, plus whether it earns a single tweet or a
   thread (5-7 body tweets). Most tips are a single tweet with an image.
   Save a thread for something that genuinely needs the room: a framework,
   a breakdown, a step-by-step. User approves or redirects before any copy
   gets written.
3. **Copy** — Claude drafts the post text in the brand voice from
   `inputs/brand/`, following the platform rules in "X Copy Rules" below.
   No em dashes. Simple, human, SEO-aware language. Render any
   user-provided copy verbatim, never reword it.
4. **Creative** — `scripts/generate_image.py` renders the image via Gemini
   image generation (default 1200x675, 16:9), following any style
   references in `inputs/references/`. Every post gets an image or a thread
   graphic unless the user explicitly says text-only.
5. **Approval gate** — Claude shows the copy + image (and the full thread
   if applicable) and asks: publish now, or hold as a draft? Nothing goes
   live without an explicit yes. This is the same hard rule as the Facebook
   kit, non-negotiable here too, since a bad post is public immediately and
   this is the user's personal, named profile.
6. **Publish** — `scripts/publish_twitter.py` posts to X via the X API v1.1
   (media upload) + v2 (create tweet) endpoints. For a thread, each tweet
   chains to the previous via `in_reply_to_tweet_id`. The API response
   (tweet ID(s), URL) gets logged in `outputs/<date>_<slug>/publish_log.json`.
7. **First-hour follow-up reminder** — After publishing, Claude tells the
   user: 10+ engagements in the first 15 minutes is the actual trigger for
   wider, out-of-network distribution on X (confirmed 2026-09-08 research,
   tighter than the earlier "30-60 minute" framing), and replying to any
   early comments in that window matters more than almost anything else
   for how far the post travels. Staying active through the first hour
   still helps, but the first 15 minutes is where the algorithm decides.
   This kit does not auto-reply on the user's behalf (see "What This Kit
   Does Not Do"), it just flags the window so the user can jump in.

## Architecture Notes

Details that only show up by reading the three scripts, not by reading the
flow above:

- **`scrape.py`'s output path is a trap if called before a slug exists.**
  Without `--out`, it writes to `outputs/<date>_draft/research.json`, not
  `outputs/<date>_<slug>/`, because the slug isn't decided until Step 2
  (angle + format), which runs *after* research. Either pass `--out
  outputs/<date>_<slug>/research.json` once the slug is known, or read from
  the `_draft` folder and let the real per-post folder get created fresh by
  `generate_image.py`/`publish_twitter.py` in Step 4/6.
- **`generate_image.py` uses `gemini-2.5-flash-image`** and accepts either
  `GOOGLE_AI_STUDIO_API_KEY` or `GEMINI_API_KEY` (checks the first, falls
  back to the second). It also supports `--ratio 1:1|4:5|9:16` and
  `--out-dir` beyond the 16:9 default shown in the Commands section above.
- **`publish_twitter.py` uses two X API surfaces under one OAuth 1.0a
  user-context auth**: `tweepy.API` (v1.1) for media upload only — v2 has no
  upload endpoint — and `tweepy.Client` (v2) for `create_tweet`. All four
  `X_*` credentials must carry Read+Write, checked once in `get_clients()`.
  It also accepts `--in-reply-to <tweet_id>` for the Step 6 follow-up-link
  reply pattern, and appends (not overwrites) each run's result to
  `publish_log.json` as a JSON array.

## X Copy Rules

These come directly from how X's ranking system actually behaves, not
generic "best practices". Updated 2026-09-08 after a deep research pass
(see `memory/learnings.md`'s 2026-09-08 "Viral content research" entry for
sources and full findings) on what actually drives virality on X in 2026
specifically in the SEO/paid-ads/AI-marketing niche.

- **No external links in the post body.** Confirmed by 2026 research: a
  link in the first tweet cuts reach by roughly 50% for non-Premium
  accounts. If a link to the site or a case study belongs with this post,
  it goes in the first reply, and Claude should say so explicitly at the
  approval gate rather than silently dropping it.
- **0-1 hashtags max**, only when genuinely relevant. Research update
  2026-09-08: more than one hashtag provides no additional reach benefit,
  and 3+ actively triggers spam filters. When in doubt, use zero.
- **The first line has to earn the second.** X gives a scrolling reader
  a fraction of a second. Open with one of: a specific number ("we
  analyzed 10,000 tweets..."), a contrarian/bold claim, a direct
  contradiction of common wisdom, a before/after result, or a story-opener
  that creates an open loop. Never open with a hedge or a label - these
  measurably kill engagement: "Just a thought...", "Interesting thread
  🧵", "Hear me out...", or leading with a hashtag.
- **End tactical/opinion posts with a genuine question or an explicit
  invite to disagree.** Confirmed 2026-09-08: X's algorithm weights
  replies above retweets/quotes, above bookmarks, above likes - this isn't
  manipulation, it's writing the way the platform actually rewards real
  conversation. A post that earns 10+ engagements in its first 15 minutes
  (not 30-60, see the Step 7 update below) is what triggers wider,
  out-of-network distribution.
- **Every tip needs a specific number, name, or concrete detail.** Generic
  marketing platitudes get treated as filler by X's negative-signal system
  and by every human reading it.
- **Visual content roughly doubles engagement** - a real chart, a
  before/after, or a genuine comparison diagram (not decorative stock
  imagery). This is why image generation rotates through varied,
  topic-specific patterns and palettes instead of one fixed house style -
  see `pipeline.py`'s `IMAGE_PATTERNS` and `memory/learnings.md`'s
  2026-09-08 "Image variety" entry.
- **Threads: 5-7 body tweets, one idea per tweet**, under ~250 characters
  each. Tweet 1 is the hook (bold statement + reader's pain point +
  counterintuitive angle + a hint of proof). Last tweet is the CTA. Threads
  outperform single tweets for reach and X-search ranking (X treats a
  thread as a topical-authority cluster) - lean toward a thread when the
  angle has real room to develop, not just to hit a length quota.
- **Never promise guaranteed results.** This profile represents a real
  consulting business. Emphasize proven strategies and continuous
  optimization, same standard as any client-facing content.
- Rotate through templates (contrarian take, hard truth, before/after with
  a real number, data-driven insight, stop/start, unpopular opinion,
  curiosity question, **personal lesson or failure story** - added
  2026-09-08, e.g. "I lost a client's budget before learning this one
  thing" - vulnerability plus a specific, honest takeaway is a validated
  2026 pattern and fits this brand's existing "honest numbers, not
  inflated claims" positioning). Never the same template twice in a row.

## What This Kit Does Not Do

On purpose, not as an oversight:

- **It does not auto-reply to other people's posts, or to comments on your
  posts.** X's own automation guidance is explicit that AI-generated reply
  spam is one of the fastest ways to get an account suppressed or
  restricted, and that replies specifically should stay human-written.
  Growing on X leans heavily on replying to bigger accounts in your niche
  (roughly 70% of your active time, per the research this kit was built
  from) but that has to be you, in your own words, not this kit acting on
  your behalf. If you want, a future version can draft reply *suggestions*
  for your review, never auto-send them.
- **Ad-hoc runs never publish as a fully autonomous, unattended bot.**
  Every in-conversation publish goes through the Step 5 approval gate.
  **Exception:** the Monday-Friday scheduled cron job (see "Autonomous
  Daily Posting" above) does run unattended by explicit user decision,
  2026-09-08. Do not extend unattended publishing to any other trigger
  without the same explicit, informed confirmation, and re-read X's
  current Automation Rules before changing the scope of this exception.
- **It does not follow, unfollow, like, or retweet anything.** Out of
  scope, and follow/unfollow cycling in particular is one of the fastest
  ways to get an account flagged.

## Folder Structure

```
twitter-post-creator/
├── CLAUDE.md              # You're reading this
├── README.md              # Setup guide
├── .env                   # API keys (NEVER commit, NEVER upload, NEVER paste in chat)
├── .env.example
├── .gitignore
├── requirements.txt
├── inputs/
│   ├── brand/             # Brand kit + voice notes (can mirror the FB kit's)
│   ├── competitors/       # urls.txt — sites to scan for angles
│   ├── references/        # Post styles to match (JPG/PNG)
│   ├── photos/            # Optional founder/team photos
│   └── copy/              # Optional topic or draft copy
├── outputs/               # Generated posts (dated folders, incl. publish_log.json)
├── memory/
│   └── learnings.md       # Self-learning log
└── .claude/
    └── skills/
        └── twitter-post/
            ├── SKILL.md
            └── scripts/
                ├── scrape.py
                ├── generate_image.py
                └── publish_twitter.py
```

## Security Rules

- API keys and tokens live in `.env` only. Never paste keys into chat. Never
  hardcode. Never upload the real `.env` anywhere, including to Claude.
- If a key or token is ever exposed (pasted in chat, committed, uploaded),
  rotate it immediately in the provider's dashboard before using this kit
  again.
- Never delete files in `inputs/`.
- Never overwrite folders in `outputs/` — every run gets a new dated folder.
- For any ad-hoc, in-conversation run: never publish without the explicit
  approval gate in Step 5. No silent auto-publish there.
- The one exception is the scheduled Monday-Friday cron job, where the
  user explicitly turned the gate off for that path only, 2026-09-08 — see
  "Autonomous Daily Posting" above. Do not extend that override to any
  other trigger (chat requests, other schedules) without the same explicit,
  informed confirmation.

## Voice Defaults

- No em dashes (—). Use commas, periods, or hyphens.
- Short, direct sentences. One idea per sentence.
- Never promise guaranteed results. Emphasize proven strategies and
  continuous optimization.
- Render any user-provided copy verbatim, never reword it.
- This is a personal profile representing a named individual consultant,
  not a faceless brand account. It's fine, and good, for posts to sound
  like a person with opinions, not a company newsletter.

## When to Step Outside the Skill

Only when the user explicitly says:
- "Skip the wizard"
- "Just publish this exact text with this exact image"
- "Edit `inputs/copy/draft.md` directly"

Otherwise, always go through the skill so the memory loop and the approval
gate keep working.
