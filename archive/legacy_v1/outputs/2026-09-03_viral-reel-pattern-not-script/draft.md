# Draft — 2026-09-03 (automated draft-only run)

## Status
DRAFT ONLY. Image generation and publishing are still pending human action.
No Firecrawl API key or image API key was available in this environment,
so `scripts/scrape.py` and `scripts/generate_image.py` were not run (per
the automation's own instructions). Research below was pulled live via the
connected Firecrawl MCP tools (`firecrawl_search`) and `tavily_extract`
instead.

## Angle chosen
**"Copy the pattern, not the script."** Sorav Jain (founder of echoVME
Digital / Digital Scholar) published a post this week
(`soravjain.com/how-to-find-viral-reels-on-instagram/`, indexed as "6 days
ago" at research time) walking through how he actually uses viral Reels he
finds: he does not recreate them, he breaks each one into its hook, its
promise, and its payoff, then rebuilds that same three-part structure for
a different niche or topic. His own line: "The pattern travels, the topic
does not need to."

## Why this angle, and why single tweet not thread
- It is a real, current, specific technique from a named person's post
  published this week, not an invented trend or generic "content tips"
  platitude — satisfies the "real number, name, or concrete detail"
  requirement in CLAUDE.md's X Copy Rules.
- It connects naturally to AAMS's own positioning (strategy over
  guesswork, honest about what actually works, "AI does the heavy
  lifting, I make the decisions") without needing to force a plug.
- Today is Thursday, which the automation's format rule allows leaning
  thread-ward on, but this angle is one sharp, self-contained insight, not
  a multi-step framework or breakdown that needs 5-7 tweets of room. Per
  CLAUDE.md ("Most tips are a single tweet... Save a thread for something
  that genuinely needs the room"), this stays a single tweet.
- Template used: **stop/start**. Checked `memory/learnings.md` first —
  prior automated runs used "framework breakdown" (2026-09-01, not on the
  CLAUDE.md rotation list) and "hard truth" (2026-09-02, on the rotation
  list). "Stop/start" has not been used yet in either prior run, so it is
  a fresh template, not a repeat of the last-used one.

## Sources / facts this is grounded in
- https://soravjain.com/how-to-find-viral-reels-on-instagram/ — the core
  technique and the "pattern travels, the topic does not" framing (primary
  source for this post).
- https://afrazalam.com/ and https://afrazalam.com/blog/ — checked for a
  fresher own-site angle first; no new blog post since
  `technical-seo-audit-checklist` (already used 2026-09-01). No usable
  hard numbers surfaced on https://afrazalam.com/case-studies/seo/ beyond
  the niche list (crypto, health/wellness, fashion/beauty, community
  platform), so it was skipped as too generic for this post's "specific
  detail" requirement.
- Other competitor sites checked via `firecrawl_search`
  (jijojosephseo.in, pankajkumarseo.com, jagdishprajapat.com,
  seofirststep.in, amittiwari.net, pranavjha.com, varunsurana.in): mostly
  evergreen/generic SEO-tips content (entity-based SEO, NAP consistency,
  "top SEO strategies" listicles) with no fresh, dated, specific angle as
  strong as the Sorav Jain piece. Noted, not used, nothing fabricated to
  fill the gap.

## Tweet text (exactly as drafted, ready for approval)

```
Stop copying the viral script. Start copying the structure.

Sorav Jain's move: pull the hook, promise, and payoff from a Reel that's working, rebuild those three in your own niche. The words don't transfer. The pattern does.

What's one pattern you keep reusing across formats?
```

(278 characters, single tweet, 0 hashtags, no external link, ends with a
genuine question per X Copy Rules.)

## Pending before this can go live
1. **Image** — needs `scripts/generate_image.py` (or a manual creative)
   once a Gemini image API key is available. Every post is supposed to
   ship with an image or thread graphic unless the user explicitly says
   text-only; this draft has neither yet.
2. **Human approval** — Step 5 approval gate has not happened. This run
   never called `publish_twitter.py` and nothing has been posted to X.
