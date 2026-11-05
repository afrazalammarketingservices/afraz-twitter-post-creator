"""The 5 approved v2 samples (inputs/references/v2_approved/approved_samples.md) as draft.json dicts."""
import copy

EMPTY_STATE = {"published_today": False, "last_cta_type": None, "last_image_layout": None,
               "questions_this_week": 0, "wed_thread_last_2_weeks": False, "topic_keys_60d": []}

MON = {
    "date_ist": "2026-11-09", "day": "Mon", "pillar": "seo_fix", "format": "single", "keyword": "sitemap",
    "topic": "A sitemap is a hint, not an order", "topic_key": "sitemap-is-a-hint",
    "parts": ["Your sitemap is a hint, not an order.\n\nGoogle's own docs call a sitemap \"merely a hint\". "
              "Submitting one does not force Google to index your new products.\n\nWhat helps more: link each new "
              "product from a live collection page, then run it through URL Inspection in Search Console."],
    "sources": [{"id": "s1", "name": "Google Search Central, Build and submit a sitemap",
                 "url": "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap",
                 "date": "2026-11-05", "quote": "Submitting a sitemap is merely a hint and doesn't guarantee that Google will download the sitemap or use the sitemap for crawling URLs on the site."}],
    "numbers": {}, "source_article": None, "image": None,
    "first_reply": {"cta_type": "checklist", "source_id": "s1"},
}

TUE = {
    "date_ist": "2026-11-10", "day": "Tue", "pillar": "image_card", "format": "single", "keyword": "Core Web Vitals",
    "topic": "Google's 3 Core Web Vitals targets for product pages", "topic_key": "core-web-vitals-targets",
    "parts": ["Is your product page fast enough for Google?\n\nGoogle's 3 Core Web Vitals targets: LCP 2.5 s or less, "
              "INP under 200 ms, CLS under 0.1.\n\nOpen Search Console > Core Web Vitals, mobile first. Fix the URLs "
              "marked Poor before anything else.\n\nWhich one is worst on your store?"],
    "sources": [{"id": "s1", "name": "Google Search Central, Understanding Core Web Vitals and Google search results",
                 "url": "https://developers.google.com/search/docs/appearance/core-web-vitals", "date": "2026-11-05",
                 "quote": "LCP: 2.5 seconds or less. INP: under 200 milliseconds. CLS: under 0.1."}],
    "numbers": {"3": {"kind": "count", "note": "the 3 Core Web Vitals metrics on the page"}, "2.5": "s1", "200": "s1", "0.1": "s1"},
    "source_article": None,
    "image": {"layout": "stat_cards", "label": "PAGE SPEED", "headline": "Is your product page [[fast enough]] for Google?",
              "sub": "Google's 3 targets, checked on a phone:",
              "cards": [{"k": "LCP", "value": "2.5 s or less", "text": "Your main product image and content show up fast"},
                        {"k": "INP", "value": "under 200 ms", "text": "The page reacts as soon as a shopper taps"},
                        {"k": "CLS", "value": "under 0.1", "text": "Nothing jumps while the page loads"}],
              "source": "Google Search Central, Understanding Core Web Vitals and Google search results",
              "alt_text": "Card listing Google's 3 Core Web Vitals targets for a product page: LCP 2.5 s or less, INP under 200 ms and CLS under 0.1."},
    "first_reply": {"cta_type": "call", "source_id": "s1"},
}

WED = {
    "date_ist": "2026-11-11", "day": "Wed", "pillar": "what_changed", "format": "single", "keyword": "AI search",
    "topic": "No special schema for Google's AI search", "topic_key": "no-special-ai-schema",
    "parts": ["There is no special \"AI schema\" for Google's AI search.\n\nGoogle says you don't need to add any special "
              "structured data to appear in AI Overviews or AI Mode.\n\nThe same basics decide it: pages Google can crawl, "
              "index and understand.\n\nSold an AI SEO fix lately?"],
    "sources": [{"id": "s1", "name": "Google Search Central, AI features and your website",
                 "url": "https://developers.google.com/search/docs/appearance/ai-features", "date": "2026-11-05",
                 "quote": "There's no special schema.org structured data that you need to add."}],
    "numbers": {}, "source_article": None, "image": None,
    "first_reply": {"cta_type": "checklist", "source_id": "s1"},
}

THU = {
    "date_ist": "2026-11-12", "day": "Thu", "pillar": "myth_or_mistake", "format": "single", "keyword": "canonical tag",
    "topic": "One Shopify product, two URLs", "topic_key": "shopify-collection-product-urls",
    "parts": ["On Shopify, one product can live at two URLs:\n\n/collections/shoes/products/red-sneaker\n/products/red-sneaker\n\n"
              "Shopify's canonical tag points Google to the short one, so it's usually fine.\n\nThe waste starts when "
              "themes link the long one everywhere. Which does your menu use?"],
    "sources": [{"id": "s1", "name": "Google Search Central, How to specify a canonical URL",
                 "url": "https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls",
                 "date": "2026-11-05", "quote": "Use the rel=\"canonical\" link annotation to indicate the canonical URL."}],
    "numbers": {}, "source_article": None, "image": None,
    "first_reply": {"cta_type": "call", "source_id": "s1"},
}

FRI = {
    "date_ist": "2026-11-13", "day": "Fri", "pillar": "website_thread", "format": "thread", "keyword": "store SEO",
    "topic": "20 store SEO checks from the Shopify SEO checklist", "topic_key": "shopify-seo-checklist-20-checks",
    "parts": ["20 store SEO checks you can run in about an hour, with no paid tools.\n\nI grouped my Shopify SEO checklist "
              "into 5 areas. Here is what each one covers:",
              "Can Google find your store?\nStore password off, sitemap submitted, no stray noindex tags, one main domain.",
              "Duplicate and broken pages\nCheck your product links, old pages that used to get traffic, and products you renamed.",
              "Pages worth ranking\nUnique titles and descriptions, real text on collection pages, product details buyers actually search for.",
              "Speed\nCompress images, remove apps you no longer use, and watch the Core Web Vitals that matter.",
              "Trust and measurement\nProduct data that passes Google's test, and sales from Google tracked in GA4.\n\n"
              "Which area would your store fail first?"],
    "sources": [{"id": "s1", "name": "Afraz Alam Marketing Services, Shopify SEO Quick-Fix Checklist",
                 "url": "https://afrazalam.com/shopify-seo-checklist/", "date": "2026-11-04",
                 "quote": "Shopify SEO Quick-Fix Checklist: 20 fixes in 5 areas you can check in about an hour, with no paid tools."}],
    "numbers": {"20": "s1", "5": "s1"}, "source_article": "https://afrazalam.com/shopify-seo-checklist/",
    "image": {"layout": "thread_cover", "label": "NEW GUIDE", "headline": "20 store SEO checks in [[about an hour]]",
              "sub": "No paid tools. Shopify, WooCommerce and custom stores.",
              "sections": ["Can Google find your store?", "Duplicate and broken pages", "Pages worth ranking", "Speed",
                           "Trust and measurement"],
              "alt_text": "Thread cover for a guide to 20 store SEO checks a Shopify or WooCommerce owner can run in about an hour."},
    "first_reply": {"cta_type": "article", "source_id": None},
}

ALL = {"mon": MON, "tue": TUE, "wed": WED, "thu": THU, "fri": FRI}


def get(name: str) -> dict:
    return copy.deepcopy(ALL[name])
