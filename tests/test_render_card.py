import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

import render_card
from samples import get

REF = Path(__file__).resolve().parents[1] / "inputs" / "references" / "v2_approved"


def mean_diff(a: Path, b: Path) -> float:
    d = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB"))
    return sum(ImageStat.Stat(d).mean) / 3


def render(name: str, tmp_path: Path, draft: dict | None = None) -> tuple[dict, Path]:
    folder = tmp_path / name
    folder.mkdir()
    (folder / "draft.json").write_text(json.dumps(draft or get(name)), encoding="utf-8")
    return render_card.render(folder / "draft.json"), folder


def test_tuesday_card_matches_reference(tmp_path):
    m, folder = render("tue", tmp_path)
    assert m["ok"], m["errors"]
    assert Image.open(folder / "image.png").size == (1080, 1350)
    assert Image.open(folder / "preview_540.png").size == (540, 675)
    assert mean_diff(folder / "image.png", REF / "X_Sample_Tuesday_Image_Post.jpg") < 3


def test_friday_cover_matches_reference(tmp_path):
    m, folder = render("fri", tmp_path)
    assert m["ok"], m["errors"]
    assert mean_diff(folder / "image.png", REF / "X_Sample_Friday_Thread_Cover.jpg") < 3


def test_limits():
    img = get("tue")["image"]
    assert render_card.check_limits(img) == []
    bad = dict(img, headline="One two three four five six seven eight nine [[ten]]")
    assert any("words" in e for e in render_card.check_limits(bad))
    bad = dict(img, headline="No highlight here at all")
    assert any("highlight" in e for e in render_card.check_limits(bad))
    bad = dict(img, cards=[dict(img["cards"][0], text="x" * 61)])
    assert any("over 60" in e for e in render_card.check_limits(bad))
    bad = dict(img, sub="y" * 91)
    assert any("over 90" in e for e in render_card.check_limits(bad))
    bad = {k: v for k, v in img.items() if k != "source"}
    assert any("source is required" in e for e in render_card.check_limits(bad))


def test_card_words_must_be_in_post():
    d = get("tue")
    assert render_card.copy_match_errors(d["image"], d["parts"][0]) == []
    img = dict(d["image"], headline="Is your [[store]] fast for Bing?")
    assert any("bing" in e for e in render_card.copy_match_errors(img, d["parts"][0]))
    img = dict(d["image"], cards=[dict(d["image"]["cards"][0], value="3.5 s or less")])
    assert any("3.5" in e for e in render_card.copy_match_errors(img, d["parts"][0]))


def test_qa_rejects_text_outside_the_safe_area(tmp_path):
    d = get("tue")
    d["image"]["cards"][0]["value"] = "WWWWWWWWWWWWWWWW"
    d["parts"][0] = d["parts"][0].replace("LCP 2.5", "LCP WWWWWWWWWWWWWWWW 2.5")
    m, _ = render("wide", tmp_path, d)
    assert not m["ok"]
    assert any("outside x 70 to 1010" in e or "overflows" in e for e in m["errors"]), m["errors"]
