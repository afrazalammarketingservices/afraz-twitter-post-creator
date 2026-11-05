# Draft — 2026-09-01 — crawl-framework-technical-seo-audit

**Status:** DRAFT ONLY. Not published. Image generation and publishing are
both still pending human action (see notes at the bottom).

## Format

Thread (8 tweets: hook, roadmap, 5 layers, CTA). Today is Tuesday, and the
angle is a genuine step-by-step framework, so it earns the extra room per
the kit's own rule (most tips are a single tweet, threads are for something
that needs it — a framework, a breakdown, a step-by-step).

## Angle

Afraz published a real, dated post on his own blog three weeks ago
("Technical SEO Audit Checklist: The CRAWL Framework," dated Aug 21, 2026)
laying out the exact 5-layer order he runs technical SEO audits in for
clients. That's a concrete, current, ownable asset: a real methodology with
a name, in a specific order, not a generic "SEO tips" listicle. Turning it
into a thread lets him claim the framework publicly and invites people to
argue about which layer actually trips up most sites, which is a strong
reply-bait question per the kit's engagement rule.

Template used: framework/step-by-step breakdown (this shape is explicitly
called out in CLAUDE.md/SKILL.md as the one that earns a thread; it isn't
one of the rotation list's named templates like "contrarian take" or
"before/after," so there's nothing to check against memory/learnings.md for
repeat-avoidance here — the rotation list applies to single-tweet
templates. Noted in memory so a future run doesn't default back to a
single-tweet template just because "framework" doesn't appear in that
list).

## Sources / facts this is grounded in

- `https://afrazalam.com/blog/technical-seo-audit-checklist/` — "Technical
  SEO Audit Checklist: The CRAWL Framework." Confirmed via Firecrawl search
  snippets (no direct scrape tool was available in this environment, so the
  framework's structure was reconstructed from multiple overlapping search
  snippets against afrazalam.com, not invented):
  - Page states: "Note: This checklist reflects the process Afraz Alam
    Marketing Services runs for clients as of August 2026."
  - Dated **Aug 21, 2026** per a matched snippet.
  - "Using the CRAWL framework above, it includes 5 layers: crawlability
    and indexing, rendering and speed, site architecture, website trust
    signals, [links]" — the 5th layer ("Links," matching the L in CRAWL)
    was confirmed via a separate snippet: "This layer checks how your
    pages connect to each other... internal links pointing to it."
  - Layer 2 detail confirmed verbatim from a snippet: "Speed, and Core Web
    Vitals. This layer checks whether the page loads fast enough, and
    renders correctly, on the device most visitors actually [use]."
  - A separate afrazalam.com blog snippet (same domain, different page)
    confirms Afraz runs this process "for clients across the US, UK, UAE"
    in addition to Kolkata — used in the CTA tweet as a real, sourced
    detail rather than an invented one.
- `https://afrazalam.com/` (homepage) — reconfirmed core positioning used
  for voice only (not quoted in the copy): "digital marketing consultant
  ... SEO, Google Ads, Meta Ads, and AI," "not vanity metrics," Kolkata
  base serving clients worldwide.
- Competitor/niche sites checked for a possible sharper or conflicting
  angle: jijojosephseo.in, pankajkumarseo.com, jagdishprajapat.com,
  seofirststep.in, amittiwari.net, soravjain.com, pranavjha.com,
  varunsurana.in. Nothing from them carried a specific number, name, or
  claim strong enough to beat Afraz's own dated, named framework, so the
  angle comes entirely from his own site, which is the strongest source
  anyway (nothing to fabricate, nothing to attribute to a competitor).
  Sorav Jain's "Top 20 SEO Trends for 2026" was the closest competing
  angle but is a generic trends listicle with no single ownable hook.

## Full thread text (exact, as drafted)

1/8
Most technical SEO audits start in the wrong place. I check crawlability before I ever open PageSpeed Insights. Here's the exact 5-layer order I run on every client audit, updated this month for how Google actually crawls sites in 2026:

2/8
I call it the CRAWL framework. 5 layers, checked in this order: Crawlability and Indexing, Rendering and Speed, Architecture, Website trust signals, Links. Skip a layer or do them out of order and you end up fixing symptoms, not causes.

3/8
1. Crawlability and Indexing. If Google can't crawl or index a page, nothing else on this list matters. I check robots.txt, sitemap coverage, and the actual index status of every important page before touching anything else.

4/8
2. Rendering and Speed. This is where Core Web Vitals live. I check if a page loads fast and renders correctly on the device most of your visitors actually use, not desktop Chrome on a fast connection.

5/8
3. Architecture. How the site is structured, how many clicks deep a page sits from the homepage, and whether your most important pages are 1-2 clicks away or buried 5 levels down.

6/8
4. Website trust signals. Schema, HTTPS, author info, real contact details. The things that tell Google, and a human, this is a real business, not a thin content farm.

7/8
5. Links. How your pages connect to each other. A great page with zero internal links pointing to it might as well not exist to Google.

8/8
That's the order I run for every client audit, from Kolkata to the US, UK and UAE. Which layer do you think most sites get wrong first? Curious what you're actually seeing out there.

## Copy rule check

- No em dashes anywhere. ✓
- First person "I," never "we." ✓
- 0 hashtags (none needed, framework speaks for itself). ✓
- No external link in the body. ✓ (the blog post itself could go in a
  first-reply if desired at publish time, human's call)
- Ends on a genuine question inviting disagreement/reply. ✓
- No guaranteed-results language. ✓
- All 8 tweets under 250 characters (max was 236). ✓
- Every tweet has a specific, concrete detail (not generic filler). ✓

## Pending human action

- **Image generation was skipped** (no Gemini/image API key available in
  this environment). A hook-tweet graphic (16:9, brand colors emerald
  #1BAE7D on deep navy #0B1220) still needs to be generated via
  `scripts/generate_image.py` before this can go through the Step 5
  approval gate.
- **Publishing was not attempted and must not be attempted from this
  automated run.** This is a draft-only research run. A human must run the
  full approval gate (Step 5) and manually invoke
  `scripts/publish_twitter.py` after reviewing copy + image.
