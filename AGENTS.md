# AGENTS.md — X (Twitter) Post Creator

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
python .Codex/skills/twitter-post/scripts/scrape.py [--urls-file PATH]
python .Codex/skills/twitter-post/scripts/generate_image.py --prompt "..." --slug "my-post" --index 1
python .Codex/skills/twitter-post/scripts/publish_twitter.py --text "..." --images outputs/2026-08-27_x/image.png --slug "my-post"
python .Codex/skills/twitter-post/scripts/publish_twitter.py --thread-file outputs/2026-08-27_x/thread.json --slug "my-post"
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

## Autonomous Daily Posting (enabled 2026-09-08)

The user explicitly overrode the Step 5 approval gate for the **scheduled
Monday-Friday cron job only**, after being shown the tradeoff (see
`memory/learnings.md` entry dated 2026-09-08 for the full context: only 8
days and 2 published drafts into the originally planned ~1-month manual
review window, and the note below about X's automation policy). This is a
real, informed, explicit decision, not a default.

- **Schedule:** Monday-Friday, 7:30 PM IST (14:00 UTC), run entirely in
  Modal's cloud (not a local cron/Task Scheduler job) so it works even when
  the user's machine is off. See `automation/README.md` for the full setup
  and `automation/modal_app.py` + `automation/pipeline.py` for the
  implementation.
- **Scope of the override:** the scheduled Modal run only. It researches a
  fresh angle (Firecrawl search for live trends + a scrape of the user's
  own site and competitors), drafts a single tweet via a direct Anthropic
  API call using the same rules as this file + `SKILL.md` +
  `memory/learnings.md` + `inputs/brand/`, generates an image (palette and
  layout rotate through 5 patterns, not locked to one house style, see
  `pipeline.py`'s `IMAGE_PATTERNS`), and publishes straight to the live
  profile with no chat approval step.
- **Single tweet only, no threads, in the automated path.** A deliberate
  scope decision, 2026-09-08: an unattended thread compounds failure risk
  across every chained tweet. Threads stay an interactive, human-judgment
  call.
- **Every automated post gets an afrazalam.com CTA as an automatic first
  reply, added 2026-09-08 by explicit user request** (see
  `memory/learnings.md`'s 2026-09-08 "Website CTA" entry). This reverses
  the earlier 2026-08-31 "no CTA in the body" deferral, but not the reason
  behind it: the CTA still never goes in the tweet body itself, since a
  link there cuts reach roughly 50% (confirmed by the same day's research,
  see "X Copy Rules" below). `pipeline.py`'s `publish_cta_reply()` posts it
  as a reply right after the main tweet instead, rotating through a few
  short variants (`CTA_REPLY_VARIANTS`) so every post doesn't read
  identically. A failed CTA reply never blocks or undoes the main publish.
  Research is also explicitly scoped to the user's actual service lines
  (SEO, Google Ads, Meta Ads, performance marketing, AI automation/AI
  marketing) rather than generic "digital marketing" - see `pipeline.py`'s
  `TREND_QUERIES`.
- **Ad-hoc runs stay gated.** When the user asks in a live conversation
  ("make a tweet", "post this", `/twitter-post`), Step 5 still applies and
  Codex still stops for explicit yes/no before publishing. The override
  is not a blanket removal of the approval gate, only the scheduled path.
- **X policy check (done 2026-09-08):** scheduling and publishing original
  posts through an OAuth-authorized tool, which this kit already uses, is
  within X's automation rules. No bot-account labeling is required for a
  named individual's own account posting their own original content; that
  labeling requirement applies to purely automated/feed-driven bot
  accounts, not this use case. Re-verify this if X's policy changes.
- **Deploy dependency:** Modal's plan caps scheduled functions at 5
  workspace-wide; LinkedIn/Instagram/Facebook's automations already used
  all 5 as of 2026-09-08, so this app's schedule only works after the
  LinkedIn kit's two same-time schedules are consolidated into one
  dispatcher (frees a slot). See `automation/README.md` step 4.
- **To pause or stop:** tell Codex to cancel the scheduled job, or run
  `modal app stop twitter-post-automation` directly. Reverting to
  manual-only is a one-line ask, not a re-negotiation.

## The 7-Step Flow

1. **Research** — `scripts/scrape.py` pulls fresh content from the user's
   own site and the URLs in `inputs/competitors/urls.txt` via Firecrawl, so
   the post is grounded in something real, not a generic AI topic or a made
   up statistic.
2. **Angle + format decision** — Codex reads the scraped material and
   proposes ONE sharp angle, plus whether it earns a single tweet or a
   thread (5-7 body tweets). Most tips are a single tweet with an image.
   Save a thread for something that genuinely needs the room: a framework,
   a breakdown, a step-by-step. User approves or redirects before any copy
   gets written.
3. **Copy** — Codex drafts the post text in the brand voice from
   `inputs/brand/`, following the platform rules in "X Copy Rules" below.
   No em dashes. Simple, human, SEO-aware language. Render any
   user-provided copy verbatim, never reword it.
4. **Creative** — `scripts/generate_image.py` renders the image via Gemini
   image generation (default 1200x675, 16:9), following any style
   references in `inputs/references/`. Every post gets an image or a thread
   graphic unless the user explicitly says text-only.
5. **Approval gate** — Codex shows the copy + image (and the full thread
   if applicable) and asks: publish now, or hold as a draft? Nothing goes
   live without an explicit yes. This is the same hard rule as the Facebook
   kit, non-negotiable here too, since a bad post is public immediately and
   this is the user's personal, named profile.
6. **Publish** — `scripts/publish_twitter.py` posts to X via the X API v1.1
   (media upload) + v2 (create tweet) endpoints. For a thread, each tweet
   chains to the previous via `in_reply_to_tweet_id`. The API response
   (tweet ID(s), URL) gets logged in `outputs/<date>_<slug>/publish_log.json`.
7. **First-hour follow-up reminder** — After publishing, Codex tells the
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
  it goes in the first reply, and Codex should say so explicitly at the
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
├── AGENTS.md              # You're reading this
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
└── .Codex/
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
  hardcode. Never upload the real `.env` anywhere, including to Codex.
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
