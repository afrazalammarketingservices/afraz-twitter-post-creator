from datetime import date

from x_today import plan


def test_week():
    got = {plan(date(2026, 11, d))["weekday"]: plan(date(2026, 11, d)) for d in range(9, 16)}
    assert got["Monday"]["pillar"] == "seo_fix" and got["Monday"]["format"] == "text"
    assert got["Tuesday"]["pillar"] == "image_card" and got["Tuesday"]["image"].startswith("stat_cards")
    assert got["Wednesday"]["pillar"] == "what_changed" and got["Wednesday"]["parts"] == [1, 3, 4]
    assert got["Thursday"]["pillar"] == "myth_or_mistake"
    assert got["Friday"]["pillar"] == "website_thread" and got["Friday"]["parts"] == [5, 6, 7]
    assert got["Friday"]["image"] == "thread_cover"
    assert got["Saturday"]["pillar"] is None and got["Sunday"]["format"] is None
    assert got["Monday"]["theme"] == "crawling, indexing and BFCM readiness"
    assert plan(date(2026, 12, 7))["theme"] == "product page SEO"
