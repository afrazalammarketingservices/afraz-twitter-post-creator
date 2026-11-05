# AAMS X agent v2 (afraz-twitter-post-creator)

Publishes SEO-only posts to Afraz Alam's X account @afrazdigital, Monday to Friday at 8:30 PM IST, from the Claude Code cloud routine "AAMS Twitter (X) Post" (`trig_01PDuGZaH72RJ8kCcZL2RNxH`, environment "AAMS Twitter (X)", starts 7:50 PM IST). v2 starts 9 Nov 2026.

## Read first

- `inputs/X-STANDARD-v2.md`: the rules (reader, images, week, research, gate, first reply).
- `automation/routine/ROUTINE-PROMPT.md`: what the routine does, step by step.
- `inputs/brand/AAMS_Brand_Voice_Signature_v2.md` and `inputs/references/v2_approved/`: voice and approved looks.
- `memory/x-post-log.md` (state, v2 rows under "## v2 log"), `memory/x-learnings.md`, `memory/afraz-ideas.md`.

## Code (automation/routine/)

| File | Job |
|---|---|
| `x_today.py` | today's pillar and format in Asia/Kolkata |
| `site_new.py` | new afrazalam.com pages in the last 7 days (Friday) |
| `render_card.py` | 1080 x 1350 brand image card + 540px preview + QA |
| `validate_post.py` | the copy gate |
| `x_reply.py` | first reply text and UTM CTA |
| `x_flow.py` | render, gate, publish, one first reply (`--dry-run` stops before publishing) |
| `publish_twitter.py` | X API publish (single, thread, image, alt text) |
| `recent_posts.py` | read-only checks: recent posts, does a post exist |
| `x_log.py` | log state and adding a v2 row |
| `ist_clock.py` | IST time and the 8:30 PM wait / 9:30 PM hard stop |

Tests: `python -m pytest` (no live calls; tests never touch the real log).

## Hard rules

- SEO only. Never ads, ROAS, Pixel, CAPI, PPC, Meta Ads, Google Ads, home services, local services or coaches.
- One post or one thread a day, Monday to Friday, plus one first reply on its last part. Never like, follow, repost, quote, DM or reply to anyone else.
- Never publish, reply, like or follow on X while testing. Only read-only calls (`recent_posts.py`) and `--dry-run`.
- Never print, log or commit a key, token or `.env`.
- No em dashes or en dashes in any file or post.
- Never invent a number, client, result, quote or screenshot.
- Never delete files: retired files go to `archive/legacy_v1/` with `git mv`. Nothing in `archive/legacy_v1/` is used by the agent.
- The routine never edits `render_card.py` or `validate_post.py` during a run.
- Pull before editing (`git pull --rebase origin main`): the routine pushes log rows to main.
- Do not touch the Facebook, Instagram, LinkedIn or FIND N FORM repos or routines, the "Daily X Reply Picks" task, or any Modal app (the old Modal app `twitter-post-automation` stays stopped).
- In-conversation publishing needs Afraz's explicit yes for that post. Only the scheduled routine publishes unattended.

## Setup

```
pip install -r requirements.txt
python -m playwright install chromium
```
`.env` holds `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` (never commit it).

## History

v1 (home-service and D2C topics, Gemini images, Modal pipeline, Claude Code skill) is in `archive/legacy_v1/` for reference only.
