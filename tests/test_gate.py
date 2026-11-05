import json
from pathlib import Path

import pytest

import render_card
import validate_post
from samples import EMPTY_STATE, get

STATE = dict(EMPTY_STATE)


def prepared(name: str, tmp_path: Path) -> tuple[dict, Path]:
    """Draft in its own folder, rendered when it has an image (as the routine does)."""
    d = get(name)
    folder = tmp_path / name
    folder.mkdir()
    (folder / "draft.json").write_text(json.dumps(d), encoding="utf-8")
    if d.get("image"):
        assert render_card.render(folder / "draft.json")["ok"]
    return d, folder


def run(d: dict, folder: Path, **state) -> dict:
    return validate_post.validate(d, folder, {**STATE, **state})


@pytest.mark.parametrize("name", ["mon", "tue", "fri"])
def test_approved_samples_pass(name, tmp_path):
    d, folder = prepared(name, tmp_path)
    r = run(d, folder)
    assert r["ok"], r["errors"]


def test_approved_wednesday_sample_only_trips_on_schema_org(tmp_path):
    # X turns "schema.org" into a link (23 weighted chars), so the approved Wednesday text
    # counts 291 and carries a link in the body. Without the domain it passes.
    d, folder = prepared("wed", tmp_path)
    r = run(d, folder)
    assert r["errors"] == ["part 1 is 291 weighted chars, must be 200 to 280",
                           "part 1: URL in the post body (links go in the first reply)"]
    d["parts"][0] = d["parts"][0].replace("schema.org structured data", "structured data")
    assert run(d, folder)["ok"]


def test_approved_thursday_sample_only_misses_the_question(tmp_path):
    # The approved Thursday sample ends "Check one menu link." while the standard says
    # Thursday always ends with a question. Everything else in it passes.
    d, folder = prepared("thu", tmp_path)
    r = run(d, folder, questions_this_week=2)
    assert r["errors"] == ["Thursday must end with a question"]
    d["parts"][0] = d["parts"][0].replace("Check one menu link.", "Which does yours use?")
    r = run(d, folder, questions_this_week=2)
    assert r["ok"], r["errors"]


def fails_with(d: dict, folder: Path, needle: str, **state):
    r = run(d, folder, **state)
    assert not r["ok"]
    assert any(needle in e for e in r["errors"]), r["errors"]


BAD_CASES = [
    ("over_280", lambda d: d["parts"].__setitem__(0, d["parts"][0] + " Then do it again on every collection page you have." * 2), "weighted chars"),
    ("url_in_body", lambda d: d["parts"].__setitem__(0, d["parts"][0] + " See afrazalam.com"), "URL in the post body"),
    ("two_hashtags", lambda d: d["parts"].__setitem__(0, d["parts"][0] + " #ShopifySEO #EcommerceSEO"), "2 hashtags"),
    ("roas", lambda d: d["parts"].__setitem__(0, d["parts"][0].replace("new products", "ROAS products")), "not SEO-only"),
    ("em_dash", lambda d: d["parts"].__setitem__(0, d["parts"][0].replace(", then", " " + chr(0x2014) + " then")), "em or en dash"),
    ("emoji", lambda d: d["parts"].__setitem__(0, d["parts"][0] + " \U0001F680"), "emoji"),
    ("first_line_100", lambda d: d["parts"].__setitem__(0, "Your sitemap is a hint, not an order, and this first line keeps going well past the limit for a hook line on X.\n\n" + d["parts"][0].split("\n\n", 1)[1]), "first line"),
    ("exclamation", lambda d: d["parts"].__setitem__(0, d["parts"][0].replace("not an order.", "not an order!")), "exclamation"),
    ("banned_phrase", lambda d: d["parts"].__setitem__(0, d["parts"][0].replace("What helps more", "Unlock this")), "banned phrase"),
    ("counter", lambda d: d["parts"].__setitem__(0, "1/6 " + d["parts"][0]), "counter"),
    ("bad_hashtag", lambda d: d["parts"].__setitem__(0, d["parts"][0] + " #SEO"), "not allowed"),
    ("unsourced_number", lambda d: d["parts"].__setitem__(0, d["parts"][0].replace("new products", "40 new products")), "no entry in numbers"),
    ("repeat_topic", lambda d: None, "last 60 days"),
]


@pytest.mark.parametrize("name,mutate,needle", BAD_CASES, ids=[c[0] for c in BAD_CASES])
def test_bad_cases_fail(name, mutate, needle, tmp_path):
    d, folder = prepared("mon", tmp_path)
    mutate(d)
    extra = {"topic_keys_60d": ["sitemap-is-a-hint"]} if name == "repeat_topic" else {}
    fails_with(d, folder, needle, **extra)


def test_thursday_without_question_fails(tmp_path):
    d, folder = prepared("thu", tmp_path)
    fails_with(d, folder, "Thursday must end with a question", questions_this_week=2)


def test_weekly_question_quota(tmp_path):
    d, folder = prepared("mon", tmp_path)  # Monday sample has no question
    d.update(date_ist="2026-11-11", day="Wed", pillar="what_changed")
    fails_with(d, folder, "must end with a question", questions_this_week=0)
    assert not any("question" in e for e in run(d, folder, questions_this_week=1)["errors"])


def test_thread_word_and_cta_rotation(tmp_path):
    d, folder = prepared("wed", tmp_path)
    d["parts"][0] = d["parts"][0].replace("schema.org structured data", "structured data").replace(
        "for Google's AI search", "for Google's AI search, a thread")
    fails_with(d, folder, "'thread' in part 1")
    fails_with(get("wed"), folder, "rotate", last_cta_type="checklist")


def test_wednesday_thread_limits(tmp_path):
    d, folder = prepared("wed", tmp_path)
    d["parts"] = [d["parts"][0].replace("schema.org structured data", "structured data"), "Second part with enough words to be a real thread part for this test case today.",
                  "Third part with enough words to be a real thread part for this test case today too?"]
    d["format"] = "thread"
    assert run(d, folder)["ok"]
    fails_with(d, folder, "Wednesday thread already ran", wed_thread_last_2_weeks=True)


def test_image_rules(tmp_path):
    d, folder = prepared("tue", tmp_path)
    fails_with(d, folder, "last image layout", last_image_layout="stat_cards")
    d["image"]["alt_text"] = "A card about page speed."
    fails_with(d, folder, "keyword")
    d2, folder2 = prepared("mon", tmp_path)
    d2["image"] = get("tue")["image"]
    fails_with(d2, folder2, "text only")


def test_friday_needs_article_cta(tmp_path):
    d, folder = prepared("fri", tmp_path)
    d["first_reply"]["cta_type"] = "call"
    fails_with(d, folder, "Friday CTA must be 'article'")
