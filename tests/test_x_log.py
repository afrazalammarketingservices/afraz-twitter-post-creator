from datetime import date

import pytest

import x_log


def row(**kw):
    base = {c: "x" for c in x_log.V2_COLUMNS}
    base.update({"IST date": "2026-11-09", "Day": "Mon", "Pillar": "seo_fix", "Format": "single", "Layout": "text",
                 "Topic key": "sitemap-is-a-hint", "CTA type": "checklist", "Question": "no", "Status": "PUBLISHED",
                 "Notes": ""})
    base.update(kw)
    return base


def test_state_and_add(temp_log):
    st = x_log.state(date(2026, 11, 9))
    assert st["published_today"] is False and st["last_cta_type"] is None
    assert "shipping-cost-before-checkout" in st["topic_keys_60d"]  # v1 rows still count for 60 days
    x_log.add(row())
    x_log.add(row(**{"IST date": "2026-11-10", "Day": "Tue", "Pillar": "image_card", "Layout": "stat_cards",
                     "Topic key": "cwv", "CTA type": "call", "Question": "yes"}))
    st = x_log.state(date(2026, 11, 11))
    assert st["last_cta_type"] == "call" and st["last_image_layout"] == "stat_cards"
    assert st["questions_this_week"] == 1
    assert {"sitemap-is-a-hint", "cwv"} <= set(st["topic_keys_60d"])
    assert x_log.state(date(2026, 11, 10))["published_today"] is True


def test_manual_rows_do_not_count_for_the_week(temp_log):
    x_log.add(row(Question="yes", Notes="manual test"))
    assert x_log.state(date(2026, 11, 10))["questions_this_week"] == 0


def test_wed_thread_window(temp_log):
    x_log.add(row(**{"IST date": "2026-11-11", "Day": "Wed", "Pillar": "what_changed", "Format": "thread"}))
    assert x_log.state(date(2026, 11, 18))["wed_thread_last_2_weeks"] is True
    assert x_log.state(date(2026, 11, 26))["wed_thread_last_2_weeks"] is False


def test_add_rejects_missing_columns(temp_log):
    with pytest.raises(ValueError):
        x_log.add({"IST date": "2026-11-09"})


def test_pipes_are_escaped(temp_log):
    assert "a / b" in x_log.add(row(Topic="a | b"))
