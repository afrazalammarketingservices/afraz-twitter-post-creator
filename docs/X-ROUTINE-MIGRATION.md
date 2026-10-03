# X agent: move from Modal to a Claude Code routine (October 2026)

Owner: Md Afraz Alam. Read this whole file, `CLAUDE.md`, `AAMS-X-Agent-Operating-Guide.md` and `memory/learnings.md` before changing anything. Same pattern as the AAMS LinkedIn, Facebook and Instagram routines: cloud routine, own environment, no Modal, no Anthropic API credits, no laptop needed.

This file is the owner's explicit instruction (given 2026-10-03) to replace the paused Modal app `twitter-post-automation` with a Claude Code routine. It does NOT authorize redeploying or resuming the Modal app. The Modal app stays stopped.

## 0. Hard rules

- Never print, log, echo or commit any key or token. Never commit `.env`.
- FIND N FORM is a separate business. Do not touch its routines, environments, repos or Modal apps.
- Do not touch the AAMS LinkedIn, Facebook or Instagram routines, or the "Daily X Reply Picks" scheduled task.
- Do not run `modal deploy` or `modal run` for `twitter-post-automation`. Do not delete the Modal app either.
- Never delete anything in `inputs/`. Never overwrite an existing `outputs/` folder.
- No em dashes anywhere. Never invent a number, client result or platform claim.
- The routine publishes only: the day's post (or thread) and ONE first reply on its own post. Never like, follow, repost, quote, DM or reply to anyone else.

## 1. Repo and environment

1. The local folder has many uncommitted changes (`automation/`, `AAMS-X-Agent-Operating-Guide.md`, new logo files, edited `CLAUDE.md`, `SKILL.md`, `memory/learnings.md`). Commit them first and push to the existing private repo `afrazalammarketingservices/afraz-twitter-post-creator`. Respect `.gitignore` (no `.env`, no `outputs/*/`).
2. Create a Claude Code cloud environment called **AAMS X**. Network access: **Full** (Trusted can block api.x.com and upload.twitter.com).
3. Environment variables (values from local `.env`, typed by the owner or set by you without displaying them). Keep the existing names so `publish_twitter.py` works unchanged:
   - `X_API_KEY`
   - `X_API_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_TOKEN_SECRET`
4. Not needed in the cloud: `ANTHROPIC_API_KEY` (the routine's own Claude writes), `GOOGLE_AI_STUDIO_API_KEY` (no Gemini, see section 5), `BREVO_API_KEY` (routine notifications replace the FYI email), Firecrawl/Apify keys (the routine does its own web research). Keep them in local `.env` only.

## 2. Schedule

- One routine: **AAMS X Post**, `CRON_TZ=Asia/Kolkata 50 19 * * 1-5` (starts 7:50 PM IST, Monday to Friday).
- Publish at **8:30 PM IST** (11:00 AM New York until 1 Nov, 10:00 AM after). If ready early, wait until 8:30 PM IST. Hard stop 9:30 PM IST: if not ready or not verified, publish nothing and log NEEDS_AFRAZ.
- One publication per weekday: one post OR one thread, never both.
- Idempotency: before publishing, check `memory/x-post-log.md` for a row with today's IST date and status PUBLISHED. If found, exit. If a publish call errors or times out, read the account's recent posts via the API before any retry. Never retry blind.

## 3. What to post each day

Readers: owners of home-service businesses (HVAC, plumbing, electrical, roofing) and founders of D2C / e-commerce / Shopify brands. US first in examples, platforms and spelling. Coaches and other segments are not readers.

| Day | Reader | Angle | Default format |
|---|---|---|---|
| Mon | Home-service | Local SEO or Google Business Profile check an owner can run in 10 minutes | Single post, text only |
| Tue | D2C / Shopify | Meta Ads or tracking lesson (CAPI, Advantage+, creative, what to measure) | Single post + image |
| Wed | Both | What changed this week in Google, Meta or AI search, and what to do about it. Thread (4 to 6 parts) only when depth is real, max 1 per week | Thread or single post |
| Thu | Home-service | Google Ads / LSA math: cost per booked job, not cost per click | Single post + image |
| Fri | D2C or both | Store conversion lesson, or an honest lesson from running the consultancy | Single post, text only |

Mix target per week: 2 to 3 image posts, 2 to 3 text-only, at most 1 thread. Never repeat a topic used on X in the last 30 days (check `memory/x-post-log.md`).

## 4. Writing rules

Keep everything in `CLAUDE.md` "X Copy Rules" and the operating guide. Additions and overrides:

- First line under 100 characters: a number with a source, a specific mistake, or a cost. No "Just a thought", "Hear me out", "Interesting thread", no leading hashtag.
- Single post target 230 to 250 characters, hard max 280 (X weighted count). Thread parts each under 280; part 1 must stand alone.
- One idea per sentence. Active voice. Numerals. At least one concrete example (a job, a store, a campaign setting).
- 0 hashtags by default, 1 at most.
- No link in the post body, ever. The first reply (within 2 minutes of publishing) carries the source link if there is one, then one line from `CTA_REPLY_VARIANTS` in `automation/pipeline.py` (rotate, never the same one 2 days running).
- Every number needs a named primary source, logged with its URL and date. Platform news only from official sources (Google Search Central, Google Ads, Meta, GA4, X), with the announced date checked.
- Read `inputs/brand/Voice and Messaging Bank.md`, `inputs/brand/ICP and Target Industries.md` and `memory/learnings.md` before drafting.

## 5. Images (no Gemini)

- Render images with HTML + headless Chromium (same approach as the Instagram carousel renderer), 1200 x 1200 PNG. Use the operating guide's image standard and the 5 rotating layouts (comparison, stat grid, before/after, checklist, single stat).
- Overlay the ORIGINAL logo file, never redrawn: `inputs/brand/logo_white.png` on dark backgrounds, `inputs/brand/logo_primary_color_transparent.png` on light ones.
- Max 1 headline and 3 short labels on the image. Every word on the image must match the approved copy exactly. No fake charts, no platform icons, no AI face, no portrait unless asked.
- Write alt text for every image. If `publish_twitter.py` cannot set alt text yet, add an `--alt-text` argument using tweepy `create_media_metadata`, test it in the dry run.

## 6. QA before publishing

- Validator script: no em dashes, no banned hooks, no link in body, hashtag count 0 or 1, X weighted character count in range (use the `twitter-text-parser` package or an equivalent implementation of X's counting), a logged source for every number.
- Image check: 1200 x 1200, correct logo file by hash, nothing clipped at mobile preview size.
- Fix and retry up to 2 times using surgical edits of the failing part (see the 2026-09-24 learning). After 2 failures publish nothing, log NEEDS_AFRAZ and open a GitHub issue "NEEDS_AFRAZ: <date> <reason>".

## 7. After every run

- Verify the post exists via the API. Log to `memory/x-post-log.md`: IST date, day, reader, format, image layout, topic, sources with dates, post ID, permalink, CTA variant, status. Commit and push. This file replaces the Modal Dict state.
- On failure, open a GitHub issue. Routine notifications (push) are the success signal.

## 8. Cut-over steps

1. Build everything above. Create the routine **disabled**.
2. Dry run, publish nothing: one Monday text post, one Tuesday image post (dark logo), one Thursday image post (light logo), one Wednesday thread. Save copy, images, alt text and character counts to `outputs/<date>_dry-run-routine/` (new folder) and to a `dry-run-preview` branch.
3. Owner reviews. After approval: confirm with `modal app list` that `twitter-post-automation` is still stopped (do not touch any other app), delete the preview branch, enable the routine.
4. Update `CLAUDE.md`: replace the "PAUSED since 2026-10-01" Modal note with "Publishing moved to Claude Code routine AAMS X Post on <date>; Modal app twitter-post-automation retired, keep stopped." Add a dated entry to `memory/learnings.md`.
5. Report: cron, enabled status, Network Full, env var names only, next 5 run dates with reader and format, Modal app still stopped, FIND N FORM untouched.
