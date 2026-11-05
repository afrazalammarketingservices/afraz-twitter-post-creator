import pytest

import x_reply
from samples import get

UTM = "?utm_source=x&utm_medium=social&utm_campaign="


def test_with_source():
    r = x_reply.build(get("mon"))
    assert r.startswith("Source: Google Search Central, Build and submit a sitemap\nhttps://developers.google.com/")
    assert r.endswith("\n\nFree Shopify SEO checklist, 20 quick fixes: https://afrazalam.com/shopify-seo-checklist/" + UTM + "seo_fix")


def test_article_and_call():
    assert x_reply.build(get("fri")) == "Full guide: https://afrazalam.com/shopify-seo-checklist/" + UTM + "website_thread"
    assert "Want me to look at your store? Free 30-minute Store Call: https://afrazalam.com/contact/" + UTM + "image_card" in x_reply.build(get("tue"))


def test_errors():
    d = get("mon")
    d["first_reply"]["source_id"] = "s9"
    with pytest.raises(ValueError):
        x_reply.build(d)
    with pytest.raises(ValueError):
        x_reply.cta_text("article", "seo_fix", None)
