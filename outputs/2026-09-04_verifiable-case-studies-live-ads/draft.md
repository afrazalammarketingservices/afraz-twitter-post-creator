# Draft — 2026-09-04 (automated draft-only run)

## Status
DRAFT ONLY. Image generation and publishing are still pending human action.
No Firecrawl API key or image API key was available in this environment,
so `scripts/scrape.py` and `scripts/generate_image.py` were not run (per
the automation's own instructions). Research below was pulled live via the
connected Firecrawl MCP tools (`firecrawl_search`) and `tavily_extract`
instead.

## Angle chosen
**"A case study screenshot proves nothing, so I stopped relying on them."**
Afraz's own live Google Ads case studies page
(`afrazalam.com/case-studies/google-ads/`) states plainly that his Google
Ads experience so far is freelance client work (via Fiverr) where client
confidentiality means he can't share names or specific results publicly.
Rather than paper over that gap with vague claims, the page says he is now
running new Google Ads campaigns on his own live properties (named:
**USA Tech Deals**, **Busiqueens**, and `afrazalam.com` itself) specifically
so results are visible and trackable by anyone, no NDA required. That's a
real, current, specific detail (named sites, named constraint) rather than
an invented trend or statistic.

## Why this angle, and why single tweet not thread
- It's grounded in a real, dated statement on Afraz's own site, not a
  generic "case studies matter" platitude — satisfies the "real number,
  name, or concrete detail" rule in CLAUDE.md's X Copy Rules (named sites:
  USA Tech Deals; named constraint: Fiverr client confidentiality).
- It ties directly to AAMS's core voice ("Honest numbers, not inflated
  claims," anti-vanity-metric framing, "the person actually doing the
  work") without forcing a plug or a link.
- Today is Friday, outside the Tue/Thu thread-leaning window, and the
  angle is one sharp, self-contained point, not a multi-step framework —
  per CLAUDE.md ("Most tips are a single tweet... Save a thread for
  something that genuinely needs the room"), this stays a single tweet.
- Template used: **unpopular opinion**. Checked `memory/learnings.md`
  first — prior automated runs used "framework breakdown" (2026-09-01, not
  on the CLAUDE.md rotation list), "hard truth" (2026-09-02), and
  "stop/start" (2026-09-03). "Unpopular opinion" has not been used in any
  prior run, so this is a fresh rotation slot, not a repeat of stop/start.

## Sources / facts this is grounded in
- https://afrazalam.com/case-studies/google-ads/ — primary source: the
  freelance-client-confidentiality note, and the named live properties
  (USA Tech Deals, Busiqueens, afrazalam.com) where new, trackable Google
  Ads campaigns are now being set up.
- https://afrazalam.com/ and https://afrazalam.com/blog/ — checked first
  for a fresher own-site angle. No new blog post since
  `technical-seo-audit-checklist` (Aug 21, 2026, already used 2026-09-01);
  the blog page itself says "Next Article Coming Soon."
- https://afrazalam.com/case-studies/ and
  https://afrazalam.com/case-studies/website-development/ — checked for
  additional hard numbers; both stayed at the "honest, early-stage,
  building my track record" framing with no new figures beyond what's
  already used in this angle.
- Other competitor/niche sites checked via `firecrawl_search`
  (jijojosephseo.in, pankajkumarseo.com, jagdishprajapat.com,
  seofirststep.in, amittiwari.net, soravjain.com, pranavjha.com,
  varunsurana.in): all surfaced only evergreen/generic listicle content
  (old "top SEO tips," "best SEO company in [city]" pages) with no fresh,
  dated, specific angle. Nothing usable found, nothing fabricated to fill
  the gap.

## Tweet text (exactly as drafted, ready for approval)

```
Unpopular opinion: a case study screenshot proves nothing.

I can't share results from freelance Ads work, client confidentiality. So I'm running live Google Ads on my own site, USA Tech Deals. No NDA. Fully trackable.

Screenshot or a live campaign, which do you trust more?
```

(275 characters, single tweet, 0 hashtags, no external link, ends with a
genuine question per X Copy Rules.)

## Pending before this can go live
1. **Image** — needs `scripts/generate_image.py` (or a manual creative)
   once a Gemini image API key is available. Every post is supposed to
   ship with an image or thread graphic unless the user explicitly says
   text-only; this draft has neither yet.
2. **Human approval** — Step 5 approval gate has not happened. This run
   never called `publish_twitter.py` and nothing has been posted to X.
