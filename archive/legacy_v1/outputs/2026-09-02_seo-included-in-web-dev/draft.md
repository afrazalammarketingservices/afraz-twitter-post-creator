# Draft — 2026-09-02 (automated draft-only run)

## Status
DRAFT ONLY. Not published. Image generation and publishing are pending human
action (no image API key or X publish permitted in this automated run).

## Format
Single tweet. Today is Wednesday, not Tuesday/Thursday, and the angle is a
sharp single point, not a step-by-step framework, so it doesn't earn thread
room per the kit's own rule.

## Template
"Hard truth." Per `memory/learnings.md`, no rotation-list template
(contrarian take, hard truth, before/after, data-driven insight, stop/start,
unpopular opinion, curiosity question) had been used yet as of the last
entry, and yesterday's run used the separate "framework breakdown" thread
shape, not a rotation template. This is the first rotation-template pick;
"hard truth" is used today.

## Angle and why
AAMS's own strongest documented differentiator: SEO is included free in
every website build, not sold as a post-launch upsell like most developers
do it. This is grounded in:
- `afrazalam.com/blog/the-role-of-seo-friendly-website-development-in-digital-marketing/`
  — a live, current post on afrazalam.com's own blog (confirmed indexed via
  Firecrawl search of the domain), arguing web development and SEO have to
  be built together, not bolted on after.
- `inputs/brand/Differentiators and Competitive Angle.md` (itself sourced
  from afrazalam.com/services, /about, /contact), which names this as "the
  strongest single offer differentiator in the portfolio": "Most developers
  charge extra to make a site SEO-friendly. AAMS bakes titles, meta, schema,
  structure, speed and analytics into every build at no extra cost."

This is a real, standing business practice, not an invented statistic or
trend, and it's specific (five named concrete deliverables: meta titles,
schema, structure, speed, analytics) rather than a generic platitude.

## Sources checked this run
- `afrazalam.com` — Firecrawl search confirmed the blog post above plus
  general site content (case studies, policy pages). Used as the angle
  source.
- `inputs/competitors/urls.txt` domains checked via Firecrawl search:
  `jijojosephseo.in` (search misfired, returned unrelated Google Pixel/YouTube
  results, skipped), `pankajkumarseo.com` (category/tag pages only, no
  usable single-post angle), `jagdishprajapat.com` (city-listicle and
  service-page content, nothing thread/tweet-worthy), `seofirststep.in`
  (UX-for-SEO and URL-structure posts, not distinctive enough to lead with),
  `amittiwari.net` (technical SEO and image-loading posts, generic), `
  soravjain.com` (a genuinely fresh post, "How to Find Viral Reels on
  Instagram," posted ~5 days ago per the snippet, but a second search to
  pull real detail out of it hit a Firecrawl 429 rate limit and didn't
  return, so there wasn't a verified specific number/detail to build a post
  on; skipped rather than fabricate one), `pranavjha.com` (SEO/franchise and
  lead-gen posts, generic), `varunsurana.in` (SME digital marketing
  generalist content, generic).
- Own-site follow-up search for more direct quotes from the SEO-friendly-dev
  blog post also hit repeated Firecrawl 429s after the first successful
  search; proceeded on the confirmed post existing plus the already-verified
  detail in the brand's own Differentiators file rather than guessing at
  additional specifics.

## Full tweet text (exactly as drafted, 280 characters)

Hard truth: most web developers charge extra to make your site SEO-friendly after launch.

I don't. Meta titles, schema, structure, speed, analytics ship built in, no upsell.

If your developer treats SEO as an add-on, that's the red flag.

Agree, or did it work out fine for you?

## Copy rules check
- No em dashes. ✓
- First person "I", never "we". ✓
- 0 hashtags (within 0-2 max). ✓
- No external link in the body. ✓
- Ends with a genuine question / invite to disagree. ✓
- Concrete detail, not a platitude: five named deliverables (meta titles,
  schema, structure, speed, analytics). ✓
- No guaranteed-results claim. ✓

## Pending before this can go live
1. Generate an image (`scripts/generate_image.py`) — skipped this run, no
   image API key available in this environment.
2. Human review and the Step 5 approval gate.
3. Publish via `scripts/publish_twitter.py` — never run automatically by
   this scheduled task.
