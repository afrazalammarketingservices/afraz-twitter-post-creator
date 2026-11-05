#!/usr/bin/env python3
"""
First reply text for the AAMS X agent v2 (inputs/X-STANDARD-v2.md section 6).
Exactly one reply, on the last part. Links live here, never in the post body.

    With a source:    "Source: <Publisher>, <page title>\\n<url>\\n\\n<CTA>"
    Without a source: "<CTA>"
"""
CTA_TYPES = ("checklist", "article", "call")
CHECKLIST_URL = "https://afrazalam.com/shopify-seo-checklist/"
CALL_URL = "https://afrazalam.com/contact/"


def utm(url: str, pillar: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=x&utm_medium=social&utm_campaign={pillar}"


def cta_text(cta_type: str, pillar: str, article_url: str | None = None) -> str:
    if cta_type == "checklist":
        return f"Free Shopify SEO checklist, 20 quick fixes: {utm(CHECKLIST_URL, pillar)}"
    if cta_type == "article":
        if not article_url:
            raise ValueError("article CTA needs source_article")
        return f"Full guide: {utm(article_url, pillar)}"
    if cta_type == "call":
        return f"Want me to look at your store? Free 30-minute Store Call: {utm(CALL_URL, pillar)}"
    raise ValueError(f"cta_type must be one of {CTA_TYPES}, got {cta_type!r}")


def build(draft: dict) -> str:
    fr = draft.get("first_reply") or {}
    cta = cta_text(fr.get("cta_type"), draft.get("pillar", ""), draft.get("source_article"))
    sid = fr.get("source_id")
    if not sid:
        return cta
    src = next((s for s in draft.get("sources", []) if s.get("id") == sid), None)
    if src is None:
        raise ValueError(f"first_reply.source_id {sid!r} is not in sources")
    return f"Source: {src['name']}\n{src['url']}\n\n{cta}"
