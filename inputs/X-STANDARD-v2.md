# AAMS X standard v2 (from 9 Nov 2026)

The rules the X agent follows, in plain words. The code enforces them: `automation/routine/render_card.py` (images), `x_today.py` (days), `validate_post.py` (the gate), `x_reply.py` (first reply), `x_log.py` (log). Account: @afrazdigital. Publishes Monday to Friday at 8:30 PM IST.

## 1. Who we write for

SEO only: SEO, AEO and GEO for Shopify, WooCommerce and custom-built stores. Readers are US store owners and founders first (UK, UAE, Australia and Singapore second), plus in-house ecommerce marketers. Never ads, ROAS, Pixel, CAPI, PPC, Meta Ads, Google Ads, home services, local services or coaches.

## 2. Images

- One brand system, the same as Instagram v2: 1080 x 1350, deep teal radial gradient, faint white dot grid, AAMS logo top left (70, 70, 64px high), "afrazalam.com" bottom left.
- Yellow label pill, a bold white Poppins headline with 1 to 3 key words in a teal highlight, a short teal subline, rounded glass boxes.
- Fonts come from `inputs/brand/fonts/` (Poppins, Inter), never Google Fonts. The logo is the original file, never redrawn.
- Five layouts: `stat_cards` (up to 3 cards: key, value, text), `checklist` (up to 5 ticked rows), `before_after` (Before, Now, Do this), `steps` (3 numbered rows) and `thread_cover` (Friday: "NEW GUIDE", headline, subline, a "THE n AREAS" or "THE n STEPS" box listing the thread's 3 to 5 sections (each up to 32 characters) as numbered rows, then a teal "Read the thread" button; the block sits centred between the logo and the footer).
- A source line ("Source: Publisher, page") sits above the footer whenever the card states a number or a platform rule.
- Limits: headline up to 9 words with 1 to 3 highlighted; card and row text up to 60 characters; subline up to 90.
- QA: everything between x 70 and 1010, content above y 1230, no text under 26px except the source line, the headline, every number and every card key also appear in the post, and a 540px preview is rendered and checked.
- Approved looks: `inputs/references/v2_approved/` (Tuesday card, Friday cover).

## 3. The week

| Day | Pillar | Format |
|---|---|---|
| Mon | seo_fix | text |
| Tue | image_card | single post with an image card (layout rotates: stat_cards, checklist, before_after, steps; never the same as the last image) |
| Wed | what_changed | text; a 3 to 4 part thread only when the news needs it and there was no Wednesday thread in the last 2 weeks |
| Thu | myth_or_mistake | text, always ends with a question |
| Fri | website_thread | thread of 5 to 7 parts, part 1 has the thread cover image |
| Sat, Sun | none | no post |

## 4. Topics and research

- Mon: one problem a store owner can fix this week: where to check, what to look for, the fix. One line per platform when it differs.
- Tue: numbers or a checklist worth saving, from an official source.
- Wed: news under 14 days old from Google Search Central, the Search Status Dashboard, Merchant Center, Shopify or WooCommerce / WordPress. No strong news: an AEO or GEO tip on how AI search reads store pages.
- Thu: a common belief or setup mistake, fixed in plain words, ending with a question owners can answer.
- Fri: anything new on afrazalam.com in the last 7 days (`site_new.py`: sitemaps plus WordPress publish dates, sitewide re-saves ignored) becomes the thread, using only that page and the sources it cites. Nothing new: a thread on the month's theme that ends with the free checklist.
- Monthly themes: Nov crawling, indexing and BFCM readiness; Dec product page SEO; Jan collection pages and internal links; Feb speed, Core Web Vitals, variants and filters; Mar schema, Merchant Center free listings, reviews; Apr content, links and AI search; May migrations and reporting.
- Research order: (1) Google Search Central docs and blog, Search Status Dashboard, Merchant Center Help, Shopify changelog and Help Center, WooCommerce developer blog, WordPress.org news; (2) Search Engine Roundtable, Search Engine Land, Search Engine Journal, Ahrefs, Semrush, Moz, Baymard; (3) afrazalam.com; (4) for demand only, never as a source: r/shopify, r/ecommerce, r/SEO, r/woocommerce, X search.
- Facts: every number and platform rule comes from a page opened in that run, in its own words, logged with URL and date. No topic repeats within 60 days. Never invent a client, result, test, quote or screenshot. If a fact cannot be confirmed, pick another topic; if none works, publish nothing and log NEEDS_AFRAZ.
- `memory/afraz-ideas.md` ideas are used on X only when they fit the SEO-only reader.

## 5. Copy gate

Voice: `inputs/brand/AAMS_Brand_Voice_Signature_v2.md` and the approved samples. First person "I", plain words, short lines, calm and honest. Match their voice, length and structure, never their topics or wording.

The gate rejects a draft when:
- the first line of part 1 is 100 characters or more, or part 1 starts with a hashtag;
- a single post is outside 200 to 280 weighted characters, or a thread part is outside 80 to 280;
- a part has a "1/6" counter or list number, or part 1 says "thread";
- there is more than 1 hashtag, or a hashtag other than #ShopifySEO, #EcommerceSEO, #WooCommerce;
- the body has a URL or a domain;
- there is an em or en dash, an emoji or an exclamation mark;
- it uses "game-changer", "in today's", "let's dive", "unlock", "supercharge", "skyrocket", "follow for more", "like and repost" or "comment below";
- it mentions ROAS, Meta Ads, Facebook Ads, Google Ads, PPC, CAPI, Pixel, ad spend, CPC, CPA, Advantage+, HVAC, plumbing, roofing, home service, local service or coach;
- Thursday does not end with a question, or the week would end with fewer than 3 question posts;
- a number is not backed by a source quote (or marked as a count of items in the post);
- the topic was used in the last 60 days;
- an image post lacks one-sentence alt text with the keyword, or the image failed QA.
A failed draft is rewritten only where it failed, at most 2 times; then nothing is published and the log says NEEDS_AFRAZ.

## 6. First reply

Exactly one reply, on the last part. Links only go here.
- With a source: "Source: Publisher, page title", the URL, a blank line, then the CTA.
- Without a source: the CTA only.

CTAs rotate and never repeat back to back:
- checklist: "Free Shopify SEO checklist, 20 quick fixes: https://afrazalam.com/shopify-seo-checklist/" plus UTM
- article: "Full guide: <article URL>" plus UTM (Friday always when a new page was found, and any day with a matching afrazalam.com article)
- call: "Want me to look at your store? Free 30-minute Store Call: https://afrazalam.com/contact/" plus UTM

UTM: `utm_source=x&utm_medium=social&utm_campaign=<pillar>`.
