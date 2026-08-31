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
   user: X's own reach testing happens in the first 30-60 minutes, and
   replying to any early comments in that window matters more than almost
   anything else for how far the post travels. This kit does not
   auto-reply on the user's behalf (see "What This Kit Does Not Do"), it
   just flags the window so the user can jump in.

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
generic "best practices":

- **No external links in the post body.** Reach drops sharply for
  non-Premium accounts when a link is in the tweet itself. If a link to the
  site or a case study belongs with this post, it goes in the first reply,
  and Claude should say so explicitly at the approval gate rather than
  silently dropping it.
- **0-2 hashtags max**, only when genuinely relevant. 5+ reads as spam to
  the ranking system.
- **End tactical/opinion posts with a genuine question or an explicit
  invite to disagree.** Replies are the single highest-value engagement
  signal on X, this isn't manipulation, it's writing the way the platform
  actually rewards real conversation.
- **Every tip needs a specific number, name, or concrete detail.** Generic
  marketing platitudes get treated as filler by X's negative-signal system
  and by every human reading it.
- **Threads: 5-7 body tweets, one idea per tweet**, under ~250 characters
  each. Tweet 1 is the hook (bold statement + reader's pain point +
  counterintuitive angle + a hint of proof). Last tweet is the CTA.
- **Never promise guaranteed results.** This profile represents a real
  consulting business. Emphasize proven strategies and continuous
  optimization, same standard as any client-facing content.
- Rotate through templates (contrarian take, hard truth, before/after with
  a real number, data-driven insight, stop/start, unpopular opinion,
  curiosity question). Never the same template twice in a row.

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
- **It does not run as a fully autonomous, unattended bot.** Every publish
  goes through the Step 5 approval gate. This keeps the account squarely in
  "a person using a tool to draft and post their own content" territory,
  not X's "automated account" category, which carries its own labeling and
  prior-approval requirements. Do not remove the approval gate without
  re-reading X's current Automation Rules first.
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
- Never publish without the explicit approval gate in Step 5. No silent
  auto-publish, ever, unless the user has explicitly turned it on for this
  account after reviewing at least 2-3 weeks of drafts, same standard as
  the Facebook kit.

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
