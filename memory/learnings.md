# Learnings — X (Twitter) Post Creator

This file is read at the start of every run and appended to after every
run. It's how the skill improves over time from your feedback.

Format for each entry: date, what happened, what to do differently next
time.

---

<!-- Entries get added below this line. Leave it empty until the first run. -->

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
