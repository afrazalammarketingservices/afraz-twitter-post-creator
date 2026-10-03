# Automated Mon-Fri X (Twitter) posting (Modal)

Unattended cloud automation, added 2026-09-08 by explicit user decision -
see `CLAUDE.md`'s "Autonomous Daily Posting" section and
`memory/learnings.md`'s 2026-09-08 entry for the full context on why the
Step 5 approval gate is bypassed here specifically (nowhere else).

Runs Mon-Fri, 7:30 PM IST (14:00 UTC): live-trend research (Firecrawl
search + a scrape of your own site and `inputs/competitors/urls.txt`) ->
one Claude-written single tweet, following the same rules as the
interactive `/twitter-post` skill (`CLAUDE.md`, `SKILL.md`,
`memory/learnings.md`, `inputs/brand/`) -> a Gemini-generated image, palette
and layout rotating through 5 patterns so posts don't all look the same ->
published straight to X via the same tweepy/OAuth 1.0a flow as
`publish_twitter.py`.

## One-time setup

1. **Add your Anthropic API key to this project's `.env`** (get one at
   console.anthropic.com if you don't already have one handy - this is
   separate from your Claude Code session auth, the Modal container needs
   its own key to call the API directly):
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   Optional, for an FYI email after every automated publish (skipped
   gracefully if you don't add these):
   ```
   BREVO_API_KEY=...
   NOTIFICATION_EMAIL=you@example.com
   ```

2. **Create the Modal secret bundle** (run from this project's root):
   ```
   modal secret create twitter-post-secrets --from-dotenv .env
   ```
   This pulls `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`,
   `X_ACCESS_TOKEN_SECRET`, `FIRECRAWL_API_KEY`, `GOOGLE_AI_STUDIO_API_KEY`,
   `ANTHROPIC_API_KEY` (and, if you added them, `BREVO_API_KEY` /
   `NOTIFICATION_EMAIL`) straight out of `.env` - nothing needs to be typed
   or pasted anywhere else. A few unrelated keys already in `.env`
   (`APIFY_TOKEN`, `MODAL_API_KEY`, `TAVILY_API_KEY`) get pulled in too;
   harmless, `pipeline.py` just ignores them.

3. **Test before trusting the schedule:**
   ```
   modal run automation/modal_app.py::pipeline_entrypoint
   ```
   This actually publishes a real tweet to your live profile (there's no
   approval gate here, that's the point) - watch the output, then check
   x.com/afrazdigital to confirm it looks right before moving to step 4.

4. **Deploy ordering - read this before running `modal deploy`.** This
   app's scheduled function would be a 6th scheduled function on a Modal
   workspace whose plan caps it at 5 (LinkedIn x2, Instagram x2, Facebook
   x1 already use all 5, as of 2026-09-08). Before deploying this app, the
   LinkedIn consolidation (see the diff Claude gave you for
   `AAMS_linkedin-automation-basic/infra/modal/deploy.py`, merging its two
   same-time schedules into one dispatcher) needs to be deployed first,
   freeing a slot. Once that's live:
   ```
   modal deploy automation/modal_app.py
   ```
   If you skip step 4's ordering, this deploy will fail against the
   workspace's schedule-count limit.

## Redeploying after edits

Editing `inputs/brand/`, `.claude/skills/twitter-post/SKILL.md`,
`CLAUDE.md`, or `memory/learnings.md` only takes effect after
`modal deploy automation/modal_app.py` again - the container bundles these
files at deploy time (`Image.add_local_dir`/`add_local_file` in
`modal_app.py`), it doesn't read your live local files at run time.

## Turning it off

Ask Claude to cancel the scheduled job, or run:
```
modal app stop twitter-post-automation
```
Reverting to manual-only (Step 5 approval gate back in force for every
run) is also just an ask - see `CLAUDE.md`'s "Autonomous Daily Posting"
section, "To pause or stop."

## Files

- `modal_app.py` - Modal app definition: container image, bundled files,
  the `twitter-post-secrets` bundle reference, the Mon-Fri 14:00 UTC
  schedule, and the manual test entrypoint.
- `pipeline.py` - the actual research -> copy -> image -> publish logic,
  the headless equivalent of the interactive skill's Steps 1-6.
