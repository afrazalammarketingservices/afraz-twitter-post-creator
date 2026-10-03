# Learnings — X (Twitter) Post Creator

This file is read at the start of every run and appended to after every
run. It's how the skill improves over time from your feedback.

Format for each entry: date, what happened, what to do differently next
time.

---

<!-- Entries get added below this line. Leave it empty until the first run. -->

## 2026-08-31 — Long-form reflective post approved as a standing format

**Approved template — use this pattern going forward, keep improvising within it:**

- **Copy shape:** long-form single post (not a short ~250-char tweet, not a
  numbered thread). Personal-observation opening line ("I've spent years
  doing X...") → short "old model" bullet list (one short phrase per line)
  → a pivot line → short "new model" bullet list mirroring the old one
  point-for-point → 1-2 reflective closing lines. No question at the end
  for this format specifically (that rule still applies to the short
  tactical/opinion single-tweet format, not this one). Still first person,
  no em dashes, no external link in body, no invented stats, still grounded
  in real research (this run used the "AI Overviews / AI chatbots" language
  already on afrazalam.com).
- **Image shape:** a real comparison table/chart that mirrors the post's
  own bullet points line-for-line (not a generic abstract graphic), navy
  background with emerald + soft cyan glow accents, two-column "OLD MODEL /
  NEW MODEL" layout with a divider line and bullet dots per row.
- **Image generation method — important:** `generate_image.py` (Gemini)
  reliably garbles multi-row/multi-line on-image text — duplicated rows,
  dropped rows, misspelled words (failed 3x in a row on a 5-row table even
  with explicit spelling call-outs). For any image with more than ~2 short
  text labels, especially a table or multi-item list, generate the layout
  with a local PIL script instead (same approach as the profile banner) so
  every word is guaranteed correct. Reserve `generate_image.py` for images
  with little or no on-image text, or a single short headline + 1-2 stat
  numbers.
- **No CTA in the post body for now** — explicitly deferred by the user,
  revisit later, don't add "visit afrazalam.com" or similar without asking
  first.
- **Cadence for the next ~1 month:** stay fully manual. Do not auto-publish
  and do not suggest the cloud routine's drafts get auto-approved. The user
  will explicitly ask for each research → draft → image cycle by name; do
  the work when asked, stop at the approval gate every time, same as
  always.
- Note: the cloud routine's own learnings-file entry from earlier today
  (2026-08-31) never made it into this file — its git push failed (see
  GitHub write-access issue) so the sandbox's edit was lost when the
  session closed. This file is the durable copy until that's fixed.

## 2026-08-31 — Confirmed posting window and daily workflow (manual month)

- **Target publish window: Monday–Friday, 7:00–8:30 PM IST.** Chosen
  deliberately to land in the ~9-11 AM Eastern Time morning-scroll window
  for the US Tier-1 audience (IST is ~9.5h ahead of EDT while US daylight
  saving is in effect, through early Nov 2026; shift ~30 min earlier in IST
  once US clocks fall back to EST).
- **Daily workflow for the next ~1 month:** the user initiates each day
  with a topic or direction. Run real research against that topic within
  the digital marketing / SEO / ads / performance marketing niche (own
  site + inputs/competitors/urls.txt + relevant current context), draft
  the post and image in the approved long-form/table pattern above, then
  stop at the approval gate. No standing auto-publish, no auto-scheduling
  yet — that stays a live topic for after this manual month, not something
  to bring up again unprompted.
- Keep using the same copy/image pattern by default. Only change the
  pattern (format, image style, etc.) if the user explicitly asks for a
  change.

## 2026-09-01 — Trending-news research is a valid Step 1 alternative

- When the user explicitly asks for "what's trending" or "going viral"
  instead of the default own-site/competitor scrape, real-time web search
  (WebSearch / Tavily) for current SEO/marketing news is a legitimate
  research source, not a substitute for `scrape.py`'s job. Still hold to
  the same rule: only use what real search results actually surface, never
  invent a stat or a trend. Present 2-3 real found options and let the user
  pick before drafting copy, same as the standard Step 2 angle-approval
  gate.
- Mock-dashboard / data-visual image concepts (a glowing flatlined graph
  inside a card, an alert dot) outperform plain headline-and-stat text on
  navy for scroll-stopping, engagement-bait posts. Reserve the plain
  stat-headline style for straightforward proof-point posts; reach for the
  visual-metaphor style when the goal is maximum stop-the-scroll and
  shares/comments.
- Rotating between the standing long-form reflective format and a punchy
  single-tweet/thread pulled from live news both work; keep alternating
  based on what the research actually supports that day rather than
  defaulting to one shape every time.

## 2026-09-08 — Approval gate overridden for scheduled posts only, timing reconfirmed

- **User explicitly ended the "manual month" early** (8 days in, 2 posts
  published) and asked to fully automate Monday-Friday posting with no
  chat approval step. This was flagged clearly first (conflicts with the
  original 2-3-week/1-month plan and with X's automated-account policy
  territory) and the user confirmed they wanted to proceed anyway. See
  [[project_twitter_kit_live]] and `CLAUDE.md`'s new "Autonomous Daily
  Posting" section for the full scope: **the override applies only to the
  scheduled cron job**, not to ad-hoc in-conversation requests, which still
  stop at the Step 5 approval gate by default.
- **X automation policy check (2026-09-08):** scheduling/publishing your
  own original posts through an OAuth-authorized tool is within X's rules
  and does not require bot-account labeling; that labeling requirement is
  for purely automated feed/bot accounts, not a named individual's own
  voice. Re-check this if X's policy changes before extending automation
  further.
- **Posting-time research reconfirmed the existing window is correct.**
  Fresh 2026 data (Buffer's 8M-post analysis, HubSpot's 20K-tweet study,
  RecurPost, Distribution.ai) converges on weekday mornings 9-11 AM ET,
  Tuesday-Thursday strongest, Friday and weekends measurably weaker for B2B
  content. The standing window of 7:00-8:30 PM IST lands at 9:30-11 AM ET,
  right in that peak — no change needed. New nuance worth revisiting later:
  Friday specifically underperforms for B2B; the user asked for Mon-Fri
  automation anyway, so this wasn't acted on, just noted for a future
  conversation about whether Friday's slot should carry lighter/different
  content.
- Scheduled job: Mon-Fri, 7:30 PM IST (14:00 UTC), built in Modal (not a
  local cron/Task Scheduler job, so it runs even with the user's machine
  off) - see `automation/README.md`. Single tweet only in the automated
  path, no threads (compounds failure risk unattended). Deploying it
  required consolidating the LinkedIn kit's two same-time schedules into
  one dispatcher first, since Modal's workspace-wide 5-scheduled-function
  cap was already fully used by LinkedIn/Instagram/Facebook's automations.
- **Image variety > fixed brand template, confirmed 2026-09-08.** The user
  pointed at a real high-performing @semrush post (a genuine "SEO vs GEO"
  Venn-diagram comparison graphic, 7.9K views) as the bar to match, and
  explicitly said not to stay locked into brand navy/emerald every time -
  vary the palette per topic and build real diagrams when the angle calls
  for one. `automation/pipeline.py` now rotates through 5 image patterns
  (comparison_diagram, stat_grid, before_after_split, checklist_hook,
  single_stat_hero) with free per-topic palette choice, tracked via a
  Modal Dict so consecutive posts don't repeat. This should also inform
  interactive-session image generation going forward, not just the
  automated path - don't default to the same navy/emerald look on every
  manually-run post either unless the topic specifically calls for it.
- **Bug fixed same day:** `pipeline.py`'s system prompt sliced CLAUDE.md to
  `[:6000]` chars, which cut off before ever reaching the "X Copy Rules"
  section (CLAUDE.md is ~17K chars). The automated path was silently
  drafting copy with none of the X-specific rules applied. Fixed by
  bundling full files (or last-12K-chars for learnings.md, so recent
  entries survive over old ones) instead of truncating from the start -
  see `pipeline.py`'s `pick_angle_and_write_copy()`. Worth remembering as
  a bug class: any time a bundled file grows, re-check truncation limits
  don't silently cut the part that actually matters.

## 2026-09-08 — Viral content research (SEO / paid ads / AI marketing niche)

User asked for a deep research pass on what actually goes viral on X in
2026, specifically in the SEO/Google Ads/Meta Ads/AI-marketing niche.
Findings applied directly to `CLAUDE.md`'s X Copy Rules, `SKILL.md`, and
`pipeline.py`'s system prompt - see those files for the rules themselves.
Sources: multiple 2026 X-algorithm/growth guides (Teract AI, FS Poster,
Unfollr, Metadata Reactor, Shopify), Seer Interactive's AI-Overview CTR
study (3,119 queries), and general-marketing sources on Google
Performance Max / Meta Advantage+ 2026 changes.

- **Algorithm hierarchy confirmed:** replies > retweets/quotes > bookmarks
  > likes. The real trigger for wider distribution is **10+ engagements in
  the first 15 minutes** - tighter than the "30-60 minute" framing this
  kit used before. Updated Step 7 in both `CLAUDE.md` and `SKILL.md`.
- **Hashtags: 0-1 max, not 0-2.** More than one hashtag gives no reach
  benefit; 3+ actively triggers spam filters. Tightened from the previous
  0-2 rule.
- **Hook formulas that work:** specific number, contrarian/bold claim,
  direct contradiction of common wisdom, before/after result, story-opener
  with an open loop. **Hooks that measurably kill engagement:** "Just a
  thought...", "Interesting thread 🧵", "Hear me out...", leading with a
  hashtag. Added an explicit blacklist to the copy rules.
- **New template added to the rotation: personal lesson / failure story**
  (e.g. "I lost a client's budget before learning this one thing").
  Vulnerability + a specific, honest takeaway is a validated 2026 pattern
  and fits this brand's existing "honest numbers, not inflated claims"
  positioning well - not a tonal stretch.
- **Visual content roughly doubles engagement** (real charts, before/after,
  genuine comparison diagrams) - confirms the 2026-09-08 image-variety
  change above was the right call, not just a one-off preference.
- **Threads outperform single tweets for reach and X-search ranking** (X
  treats a thread as a topical-authority cluster) - worth leaning toward a
  thread more readily in interactive sessions when an angle has real room,
  not just defaulting to single tweets. Automated path stays single-tweet
  only regardless (unattended-risk decision, unrelated to this finding).
- **Niche-specific angle bank:** GEO (being cited by AI, not just ranked)
  is the dominant live SEO conversation right now. Seer Interactive found
  organic CTR on AI-Overview queries fell 61% (1.76%→0.61%) - an
  independently-sourced number close to the 58% Ahrefs figure already used
  in the 2026-09-01 post; good to have both in the angle bank. Paid-ads
  angle bank: Google Performance Max and Meta Advantage+ have both made AI
  automation the *default* in 2026, shifting the real value-add from
  manual bid-tuning to clean conversion data and creative - this is what
  the 2026-09-08 test tweet used ("I still set manual guardrails") and
  it's confirmed as a live, current narrative, not a stretch.

## 2026-09-08 — Website CTA added (reverses the 2026-08-31 "no CTA" deferral), research scoped to service lines

- **User explicitly asked for a CTA to afrazalam.com "in the very end" of
  every automated post.** This reverses the 2026-08-31 learnings entry
  that said "no CTA in the post body for now, explicitly deferred... don't
  add 'visit afrazalam.com' without asking first" - the user has now
  asked, so it's no longer deferred. What did NOT change: the reasoning
  behind that original deferral (a link in the tweet body itself cuts
  reach ~50%) is still true, reconfirmed by the same day's viral-content
  research above. So the CTA goes in an **automatic first reply**, never
  the body - `pipeline.py`'s `publish_cta_reply()`, called from `run()`
  right after the main tweet publishes, wrapped in try/except so a failed
  CTA reply never blocks or undoes the main post. Rotates through 4 short
  variants (`CTA_REPLY_VARIANTS`) so it doesn't read identically every
  time. This is automated-path only for now; ad-hoc interactive runs
  should ask the user at the Step 5 approval gate whether they want the
  same CTA-reply pattern, same as the existing "link goes in first reply"
  rule already does.
- **Research explicitly re-scoped to the user's actual service lines**
  (SEO, Google Ads, Meta Ads, performance marketing, AI automation/AI
  marketing workflows), not generic "digital marketing" - `pipeline.py`'s
  `TREND_QUERIES` now names each service line directly rather than one
  broad catch-all query.
- **User re-confirmed the image-variety direction** (free palette, "go
  beyond brand colors," engaging/unique/creative) already built earlier
  today - no code change needed, just confirms `IMAGE_PATTERNS` was the
  right call, not a one-off ask.
- **Bug note:** all of these prompt/rule changes only reach the automated
  path once `automation/modal_app.py` is actually redeployed (`modal
  deploy`) - editing `pipeline.py`, `CLAUDE.md`, `SKILL.md`, or
  `memory/learnings.md` locally does nothing to the live schedule until
  that happens, since the container bundles these files at deploy time.
  As of this entry, the Twitter automation has only been through an
  ephemeral `modal run` test, not yet a real `modal deploy` - the next
  deploy will be the first one to carry all of today's changes (image
  variety, the CLAUDE.md truncation fix, the CTA reply, and the
  re-scoped research queries) at once.

## 2026-09-24 — Automation rebuilt against AAMS-X-Agent-Operating-Guide.md

User handed over a detailed written operating guide (saved at repo root,
`AAMS-X-Agent-Operating-Guide.md`) plus 6 reference layout images (saved
to `inputs/references/`) and asked for a full rebuild. This entry is the
"what actually happened" log; `CLAUDE.md`'s "Autonomous Daily Posting"
section is the living reference for the current rules.

**Audit finding before touching anything:** the Mon-Fri schedule deployed
2026-09-08 had gone silently inactive - `modal app logs
twitter-post-automation --since 21d` showed exactly ONE fire in two weeks
(2026-09-23), not the ~11 expected. This matches a documented Modal
plan-tier quirk (the LinkedIn kit's own deploy.py already had a comment
about this exact failure mode from an earlier incident). A fresh
`modal deploy` re-arms it, but there's no detection for it happening
again short of manually checking logs periodically - flagged to the user
as a real, unresolved reliability gap, not silently accepted.

**Real conflict surfaced and resolved before building:** the new guide's
"add a relevant source link... when it fits" reads as putting a link in
the post body sometimes, which contradicts the 2026-09-08 finding that a
body link cuts reach ~50%. Asked the user explicitly rather than picking
silently - **decision: keep links out of the body always**, first-reply
pattern stays for both the afrazalam.com CTA and any source citation.

**Logo assets fixed.** Neither a white (dark-background) nor a genuinely
transparent (light-background) version of the primary wordmark logo
existed. Investigated and found "PRIMARY LOGO (Main) - Transparent
version (PNG).png" was mislabeled - mode RGB, no alpha channel at all,
white background baked into the pixels. Derived real alpha via a
white-chroma-key (soft-threshold distance-from-white, not a hard cutoff,
for clean anti-aliased edges) and produced two new files:
`logo_white.png` and `logo_primary_color_transparent.png`. Both are
deterministic pixel operations, never an AI model redrawing the logo -
matches the operating guide's explicit requirement. **Caught by the
harness's own safety classifier mid-task:** a first attempt at this
accidentally overwrote the original source logo file in place - correctly
blocked as an irreversible destructive overwrite. Lesson: derived brand
assets always go to new filenames, never overwrite the original file even
when "fixing" it.

**Ubersuggest architecturally unavailable to the automated path.** The
MCP tool is scoped to an interactive Claude Code session; the Modal
container is a standalone Python process with no such access. The
operating guide's own "if unavailable, log the limitation" clause covers
this - implemented as an explicit limitations list threaded into every
research() call and the LLM's context, not silently dropped.

**Character-limit reliability was the biggest real engineering problem,
not a footnote.** Empirically, during dry-run acceptance testing:
- Asking for "under 280 characters" in the original prompt produced a
  ~40% first-pass violation rate (one case came back at 341 chars).
- A full-post regeneration retry (rewrite the whole thing, told it
  violated the limit) converged only ~60% of the time - sometimes a
  *different* part would drift over on the retry.
- The fix that actually worked: (1) target 230-250 chars in the prompt,
  not 280 - never aim at the ceiling; (2) on violation, don't regenerate
  the whole post, run a focused edit call that shortens only the specific
  offending part(s) with the exact original text and exact overage count
  (`shorten_violating_parts()` / `shorten_part()`); (3) up to 3 rounds of
  that; (4) if still over, raise and refuse to publish rather than post
  something broken. This converged reliably (11/11 across the final two
  full acceptance-test passes) where blind full-regeneration retries had
  not. **Takeaway for future LLM-generated-content-with-a-hard-limit
  work: target well below the limit, and make retries surgical edits of
  the specific violation, not full regenerations.**
- Separately, Gemini does not reliably honor an exact pixel size from a
  text prompt either - asked for 1200x1200, consistently got 1024x1024.
  Fixed the same way: stopped trusting the model's literal output and
  added a deterministic resize step (`_force_square_size()`) after
  generation. General pattern worth remembering: don't trust an
  image/text model's literal compliance with an exact numeric
  constraint (size, character count) from the prompt alone - verify
  programmatically and correct deterministically, every time, not just
  when something looks off.

**Threads re-enabled in the automated path**, reversing the 2026-09-08
"single tweet only" decision - the operating guide explicitly wants
occasional threads (~1/week, only with real depth) and the character-
limit validation above now provides the reliability guardrail that
decision was originally protecting against, so the tradeoff changed.

**A real bug caught in the test harness itself, not the pipeline:** the
first version of the dry-run acceptance check shared the SAME Modal Dict
("twitter-post-state") as the real production pipeline. Running the 5
test cases was silently consuming real weekly image/thread quota before
any live post had happened that week. Fixed by giving dry runs a fully
separate Dict ("twitter-post-state-dryrun"), gated by a module-level
`_DRY_RUN_MODE` flag set at the top of `run()`. Worth remembering
generally: a test/dry-run path that reads real persistent state is fine;
one that can *write* to the same state as production needs its own
isolated storage, always, not just "probably won't matter."

**Final verification before deploy:** ran the operating guide's own 5
acceptance cases (verified update, evergreen fallback, thread, dark logo
image, light logo image) against real Anthropic/Gemini API calls but with
no X publish calls, pulled the actual generated images back locally
(`modal volume get twitter-post-dryrun <case>/image.png ...` - note: `/`
as a bare REMOTE_PATH failed oddly on Windows Git Bash even though it
matches Modal's own documented example; downloading a specific file path
worked reliably, `MSYS_NO_PATHCONV=1` was needed once to stop Git Bash
mangling a leading `/` into a Windows path) and inspected them directly.
Both variants (dark/light) came back clean: correct 1200x1200, crisp
logo compositing, no spelling errors, no garbled text, real numbers in
the diagrams, no fake platform icons.

**Schedule changed:** 7:30 PM IST -> 8:30 PM IST (15:00 UTC), per the
operating guide's locked schedule, superseding the 2026-09-08 timing
research. Not re-litigated - the guide is an explicit, deliberate new
instruction.

**Brevo FYI email enabled same day**, `BREVO_API_KEY` + `NOTIFICATION_EMAIL`
added to the `twitter-post-secrets` bundle (reusing the same Brevo account
the Facebook kit already uses, sender `hello@afrazalam.com`). Note: the
API key was pasted directly into chat when the user supplied it - flagged
immediately per this project's own security rule, user asked to proceed
now and rotate the key in Brevo's dashboard afterward. Live end-to-end
test confirmed working: a real publish (`modal run
automation/modal_app.py::pipeline_entrypoint`) both posted successfully
AND the FYI email arrived - user confirmed receiving it.

**That live test run also validated the character-limit retry mechanism
for real, not just in dry-run:** the first draft came back at 364 chars
(84 over), `shorten_violating_parts()` caught it and corrected it before
publishing. First real-world confirmation the fix actually works outside
the dry-run harness.

**User gave final explicit go-ahead 2026-09-24** after reviewing the live
test tweet/image and confirming the email arrived. No further action
needed - `twitter-post-automation` was already deployed with the Mon-Fri
8:30 PM IST schedule from earlier in the session; this was a confirmation
checkpoint, not a new deploy. First real scheduled (non-manual) fire under
the rebuilt pipeline: tonight, 2026-09-24 8:30 PM IST.

## 2026-10-01 — Automation paused by explicit user instruction

User said to stop publishing entirely "until my next command," no reason
given, none needed. Ran `modal app stop twitter-post-automation --yes`,
confirmed stopped via `modal app list`. This is a full stop, not a
deploy-in-place change - resuming requires `modal deploy
automation/modal_app.py` again (re-registers the Mon-Fri 8:30 PM IST
schedule) when the user explicitly asks, not proactively.

**Noted in passing, not acted on:** at the same check, `linkedin-basic-agent`,
`facebook-post-automation`, and `instagram-carousel-agent` were also all
showing `stopped` - none of that was this session's doing, and there was
evidence of other active work on the Facebook kit earlier the same day
(multiple ephemeral `facebook-po...` / `aams-adhoc-...` app runs around
13:00-13:35 IST). Flagged to the user rather than assumed to be related
or silently ignored.
**2026-09-01 (automated draft-only run):** First run. Angle used: the
"CRAWL framework" 5-layer technical SEO audit checklist Afraz published on
his own blog on Aug 21, 2026 (Crawlability/Indexing, Rendering/Speed,
Architecture, Website trust signals, Links). Format: thread (8 tweets),
justified because it's a genuine step-by-step framework, not because it
was a Tuesday. Template shape: "framework/step-by-step breakdown" — this
isn't one of the CLAUDE.md rotation-list template names (contrarian take,
hard truth, before/after, data-driven insight, stop/start, unpopular
opinion, curiosity question), it's the separate thread-worthy shape called
out in the "Angle + format decision" step. Next automated run: don't reuse
the CRAWL-framework thread; for the *next single-tweet* post, none of the
rotation templates have been used yet either, so any of them is fair game,
just don't reach for "framework breakdown" again unless a new genuinely
step-by-step angle turns up. No Firecrawl `scrape.py`/API key was
available this run — research came from `firecrawl_search` (web search +
snippets) scoped to each domain via `includeDomains`, not a full-page
scrape, so facts had to be pieced together from overlapping snippets
rather than one clean pull. If a real Firecrawl API key gets added later,
`scripts/scrape.py` will likely surface fuller page content in one pass.

**2026-09-02 (automated draft-only run):** Angle used: AAMS's own
strongest documented differentiator, SEO (meta titles, schema, structure,
speed, analytics) is included free in every website build instead of sold
as a post-launch upsell, grounded in the live blog post
`afrazalam.com/blog/the-role-of-seo-friendly-website-development-in-digital-marketing/`
plus `inputs/brand/Differentiators and Competitive Angle.md`. Format:
single tweet (Wednesday, not Tue/Thu, and the angle is a sharp single
point, not a step-by-step framework). Template: **"hard truth"** — this is
the first automated run to actually use one of the CLAUDE.md rotation-list
templates (contrarian take, hard truth, before/after with a real number,
data-driven insight, stop/start, unpopular opinion, curiosity question);
2026-09-01 used the separate "framework breakdown" thread shape, which
isn't on that list. Next automated run: don't reuse "hard truth"; five of
the seven rotation templates are still untried (contrarian take,
before/after, data-driven insight, stop/start, unpopular opinion,
curiosity question) plus the always-available framework-breakdown thread
shape for a genuinely step-by-step angle.
`firecrawl_search` hit repeated HTTP 429 rate-limit errors mid-run on two
follow-up queries (a deeper pull on Sorav Jain's fresh "viral Reels" post,
and a deeper pull on Afraz's own SEO-friendly-web-dev post) — both were
skipped rather than fabricating detail to fill the gap; the first-pass
domain-scoped searches that already succeeded were used instead. If this
recurs, spacing out competitor-domain searches (or reducing the number of
parallel `firecrawl_search` calls in one batch) may help; this run fired 8
`firecrawl_search` calls in parallel in one batch, which likely triggered
it.

**2026-09-03 (automated draft-only run):** Angle used: Sorav Jain's fresh
(published ~6 days prior) post on how he actually uses viral Reels he
finds, breaking each into hook/promise/payoff and rebuilding that
structure in a different niche rather than recreating it verbatim
("the pattern travels, the topic does not"), sourced from
`soravjain.com/how-to-find-viral-reels-on-instagram/` — this is the same
post that hit 429 errors on 2026-09-02 and got skipped that run; this run
successfully pulled it via `tavily_extract` instead of a follow-up
`firecrawl_search` call, which avoided the rate limit entirely. Format:
single tweet (Thursday, so a thread was allowed by the day-of-week rule,
but the angle is one self-contained insight, not a multi-step framework,
so it stayed a single tweet per CLAUDE.md's own "most tips are a single
tweet" guidance). Template: **stop/start** — first automated run to use
this one; two of the seven CLAUDE.md rotation-list templates are now used
(hard truth 2026-09-02, stop/start 2026-09-03); still untried: contrarian
take, before/after with a real number, data-driven insight, unpopular
opinion, curiosity question, plus the separate framework-breakdown thread
shape (used 2026-09-01) for a genuinely step-by-step angle. Next automated
run: don't reuse stop/start; reach for one of the five untried rotation
templates first.
Own-site check first: no new blog post since the CRAWL-framework one
(already used 2026-09-01); `afrazalam.com/case-studies/seo/` was pulled
via `tavily_extract` and had no hard numbers, only a niche list (crypto,
health/wellness, fashion/beauty, community platform) — too generic to
anchor a "specific number/name/detail" post, so it was skipped rather than
stretched into a claim it doesn't support.
`tavily_extract` (full-page content) worked well as a fallback/complement
to `firecrawl_search` (search snippets only) this run for pulling full
article content from a known URL without hitting Firecrawl's rate limit —
worth using directly for known target URLs rather than only for
`firecrawl_search` follow-ups.

**2026-09-04 (automated draft-only run):** Angle used: Afraz's own
`afrazalam.com/case-studies/google-ads/` page states his Google Ads
experience so far is freelance client work with confidential results (per
standard Fiverr client agreements), so instead of leaning on unverifiable
claims, he's now running new, publicly trackable Google Ads campaigns on
his own live properties (named: USA Tech Deals, Busiqueens, afrazalam.com
itself). Format: single tweet (Friday, outside the Tue/Thu thread-leaning
window; the angle is one sharp point, not a multi-step framework).
Template: **unpopular opinion** — first automated run to use this one;
four of the seven CLAUDE.md rotation-list templates are now used (hard
truth 2026-09-02, stop/start 2026-09-03, unpopular opinion 2026-09-04);
still untried: contrarian take, before/after with a real number,
data-driven insight, curiosity question, plus the framework-breakdown
thread shape (used 2026-09-01, not on the official rotation list) for a
genuinely step-by-step angle. Next automated run: don't reuse unpopular
opinion; reach for one of the three untried rotation templates first
(contrarian take, before/after with a real number, data-driven insight,
curiosity question).
No new blog post since the CRAWL-framework one (still Aug 21, 2026; the
blog page itself now explicitly says "Next Article Coming Soon"). All 8
competitor/niche URLs in `inputs/competitors/urls.txt` were checked via
`firecrawl_search` again this run (jijojosephseo.in, pankajkumarseo.com,
jagdishprajapat.com, seofirststep.in, amittiwari.net, soravjain.com,
pranavjha.com, varunsurana.in) and every one surfaced only old, generic,
evergreen listicle content with no dated/fresh angle strong enough to use
— own-site content ended up being the strongest real, current, specific
source this run. No Firecrawl rate-limit (429) issues this run; searches
were spaced out in batches of 2-3 rather than fired 8-at-once, consistent
with the 2026-09-02 learning about avoiding large parallel batches.


## 2026-10-03 - Publishing moved from Modal to the Claude Code routine AAMS X Post

Per docs/X-ROUTINE-MIGRATION.md (owner instruction, 2026-10-03). The Modal
app twitter-post-automation is retired and stays stopped; confirmed via
`modal app history` (last deploy v2 on 2026-09-24, no redeploy after the
2026-10-01 stop) and an empty `modal app list`.

- Routine: AAMS X Post, `trig_01PDuGZaH72RJ8kCcZL2RNxH`,
  `CRON_TZ=Asia/Kolkata 50 19 * * 1-5`, publishes 8:30 PM IST, hard stop
  9:30 PM IST. Created disabled; Afraz enables it after reviewing the dry run.
- Environment: "AAMS Twitter (X)", Network Full, only X_API_KEY,
  X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET. **Mistake to never
  repeat:** at creation Claude attached the routine to env_018CctV7k4y3PMrdnNvWdHXP
  believing it was "Default" from an old listing label; it was the FIND N
  FORM environment. Afraz caught it and moved it. Never pick an environment
  by an old or generic label; confirm which business it belongs to, and
  never touch a routine's environment once Afraz has set it (a partial
  update to job_config can overwrite environment_id).
- State moved from the Modal Dict to memory/x-post-log.md (idempotency,
  30-day topic check, CTA rotation, weekly mix). Notes column carries
  non-blocking flags such as ALT_TEXT_FAILED.
- No Gemini. Images are HTML + headless Chromium (automation/routine/
  render_image.py), 1200x1200, original logo bytes embedded and checked by
  SHA-256. Its text auto-fit check first flagged Poppins glyph overhang as
  clipping and shrank every headline to minimum size; the tolerance now
  scales with font size. Always look at the rendered PNG, not just the
  fit report.
- Validator (automation/routine/validate_post.py) uses X's weighted count
  (twitter-text-parser, which needs setuptools<81 for pkg_resources). It
  was proven against 9 deliberately broken drafts, not just passing ones.
- Owner fixes after the dry run review (2026-10-03):
  1. Any worked-example number means the image must carry an "Example"
     label; the renderer adds it and the validator enforces it.
  2. Posts land at 11 AM ET, so never write "tonight" in copy; say "today".
  3. Alt text never blocks a post: publish_twitter.py publishes without
     it if create_media_metadata fails, prints ALT_TEXT_FAILED, and the
     routine logs it and opens a GitHub issue.
- Platform news needs an announced date from an official dated source.
  The Wednesday dry-run thread (Local Services Ads moving into Performance
  Max) had an undated official help page, so it was framed as an ongoing
  rollout rather than "this week's news".
- Git: the auto-mode classifier blocked commit/push once in this session;
  when that happens, hand Afraz the exact commands instead of retrying.
