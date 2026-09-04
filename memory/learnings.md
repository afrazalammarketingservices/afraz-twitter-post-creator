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
