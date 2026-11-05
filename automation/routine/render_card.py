#!/usr/bin/env python3
"""
AAMS X v2 image renderer (inputs/X-STANDARD-v2.md section 2).

Ports the two approved templates (X_Tuesday_Image_Card.html and
X_Friday_Thread_Cover.html) to five layouts on the same brand system as
the Instagram v2 renderer: 1080 x 1350, teal radial gradient, white dot
grid, AAMS logo top left, afrazalam.com bottom left.

    python automation/routine/render_card.py outputs/<folder>/draft.json

Reads draft["image"] and the post copy (draft["parts"]), writes next to
draft.json: card.html, image.png (1080 x 1350), preview_540.png and
render_manifest.json. Exit 0 only when every limit and QA check passes.
The routine must never edit this file during a run.

draft["image"] shape (headline marks the highlighted words with [[...]]):
  stat_cards:   {"layout", "label", "headline", "sub", "cards": [{"k", "value", "text"}] (1 to 3)}
  checklist:    {"layout", "label", "headline", "sub", "rows": ["..."] (1 to 5)}
  before_after: {"layout", "label", "headline", "sub", "before", "now", "do"}
  steps:        {"layout", "label", "headline", "sub", "steps": ["..."] (exactly 3)}
  thread_cover: {"layout", "label" (default "NEW GUIDE"), "headline", "sub",
                 "sections": ["..."] (3 to 5 short titles, the thread's parts),
                 "sections_label": "areas" | "steps" (default "areas")}
  every layout: "source": "Publisher, page" (required when the card states a
  number or a platform rule: "rule": true), "alt_text": "One sentence."
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FONTS = REPO / "inputs" / "brand" / "fonts"
LOGO = REPO / "inputs" / "brand" / "AAMS_Logo_Horizontal_OnDark.png"
W, H = 1080, 1350
LAYOUTS = ("stat_cards", "checklist", "before_after", "steps", "thread_cover")
IMAGE_LAYOUTS = ("stat_cards", "checklist", "before_after", "steps")  # Tuesday rotation

LIMITS = {"headline_words": 9, "hl_min": 1, "hl_max": 3, "card": 60, "row": 60, "sub": 90,
          "label": 24, "k": 12, "section": 32, "value": 18, "source": 110}
SAFE_LEFT, SAFE_RIGHT, CONTENT_BOTTOM = 70, 1010, 1230
MIN_FONT, SOURCE_FONT = 26, 22
FIXED_GLYPHS = {"↓"}  # the cover's "Read the thread" arrow, drawn by a fallback font as in the approved sample
HL = re.compile(r"\[\[(.+?)\]\]")
ARROW = "Read the thread ↓"

CSS = (
    "@font-face{font-family:'P';font-weight:700;src:url('{F}/Poppins-Bold.ttf')}"
    "@font-face{font-family:'P';font-weight:600;src:url('{F}/Poppins-SemiBold.ttf')}"
    "@font-face{font-family:'P';font-weight:500;src:url('{F}/Poppins-Medium.ttf')}"
    "@font-face{font-family:'I';font-weight:400;src:url('{F}/Inter-Regular.ttf')}"
    "*{box-sizing:border-box}body{margin:0}"
    ".c{position:relative;overflow:hidden;background:radial-gradient(circle at 78% 35%,#0D6B60 0%,#063831 55%,#04271F 100%);color:#fff;font-family:P}\n"
    ".dots{position:absolute;inset:0;background-image:radial-gradient(#fff 1.6px,transparent 1.9px);background-size:28px 28px;opacity:.07}\n"
    ".abs{position:absolute}.h{font-weight:700;line-height:1.08;letter-spacing:-.02em}"
    ".mk{display:inline-block;background:#15B5B0;color:#063831;border-radius:.16em;padding:0 .18em;margin:.06em 0}\n"
    ".sub{font-weight:500;color:#8FDCD9}"
    ".box{display:flex;align-items:center;background:rgba(255,255,255,.08);border:2px solid rgba(143,220,217,.35);border-radius:22px;padding:24px 30px;margin-top:20px}"
    ".btn{display:inline-block;background:#15B5B0;color:#063831;font-weight:600;border-radius:12px}"
    ".pill{display:inline-block;background:#FFD60A;color:#1F2937;font-weight:600;border-radius:40px;padding:10px 26px}"
    ".tick{flex:none;width:46px;height:46px;border-radius:50%;background:#15B5B0;position:relative;margin-right:26px}"
    ".tick:after{content:'';position:absolute;left:16px;top:9px;width:11px;height:21px;border:solid #063831;border-width:0 5px 5px 0;transform:rotate(45deg)}"
    ".num{flex:none;width:58px;height:58px;border-radius:50%;background:#15B5B0;color:#063831;font-weight:700;font-size:32px;display:flex;align-items:center;justify-content:center;margin-right:26px}"
)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def headline_html(h: str) -> str:
    parts, last = [], 0
    for m in HL.finditer(h):
        parts.append(esc(h[last:m.start()]))
        parts.append('<span class="mk">%s</span>' % esc(m.group(1)))
        last = m.end()
    parts.append(esc(h[last:]))
    return "".join(parts)


def plain_headline(h: str) -> str:
    return HL.sub(r"\1", h)


def box_title(img: dict) -> str:
    return f"THE {len(img.get('sections', []))} {(img.get('sections_label') or 'areas').upper()}"


def card_texts(img: dict) -> list[tuple[str, str]]:
    """(kind, text) for every text on the card except logo, footer and source."""
    out = [("label", img.get("label") or ("NEW GUIDE" if img.get("layout") == "thread_cover" else "")),
           ("headline", plain_headline(img.get("headline", ""))), ("sub", img.get("sub", ""))]
    lay = img.get("layout")
    if lay == "stat_cards":
        for c in img.get("cards", []):
            out += [("k", c.get("k", "")), ("value", c.get("value", "")), ("card", c.get("text", ""))]
    elif lay == "checklist":
        out += [("row", r) for r in img.get("rows", [])]
    elif lay == "steps":
        out += [("row", r) for r in img.get("steps", [])]
    elif lay == "before_after":
        out += [("row", img.get(k, "")) for k in ("before", "now", "do")]
    elif lay == "thread_cover":
        out += [("boxtitle", box_title(img))] + [("section", t) for t in img.get("sections", [])]
    return [(k, t) for k, t in out if t]


def check_limits(img: dict) -> list[str]:
    errs = []
    lay = img.get("layout")
    if lay not in LAYOUTS:
        return [f"image.layout must be one of {LAYOUTS}, got {lay!r}"]
    h = img.get("headline", "")
    if not h:
        errs.append("image.headline missing")
    words = plain_headline(h).split()
    if len(words) > LIMITS["headline_words"]:
        errs.append(f"headline has {len(words)} words, max {LIMITS['headline_words']}")
    hl_words = sum(len(m.split()) for m in HL.findall(h))
    if not LIMITS["hl_min"] <= hl_words <= LIMITS["hl_max"]:
        errs.append(f"headline must highlight 1 to 3 words with [[...]], has {hl_words}")
    for kind, text in card_texts(img):
        lim = LIMITS.get(kind)
        if lim and len(text) > lim:
            errs.append(f"{kind} over {lim} chars ({len(text)}): {text!r}")
    if lay == "stat_cards" and not 1 <= len(img.get("cards", [])) <= 3:
        errs.append("stat_cards needs 1 to 3 cards")
    if lay == "checklist" and not 1 <= len(img.get("rows", [])) <= 5:
        errs.append("checklist needs 1 to 5 rows")
    if lay == "steps" and len(img.get("steps", [])) != 3:
        errs.append("steps needs exactly 3 rows")
    if lay == "thread_cover":
        if not 3 <= len(img.get("sections", [])) <= 5:
            errs.append("thread_cover needs 3 to 5 sections")
        if (img.get("sections_label") or "areas") not in ("areas", "steps"):
            errs.append("sections_label must be 'areas' or 'steps'")
    if lay == "before_after" and not all(img.get(k) for k in ("before", "now", "do")):
        errs.append("before_after needs before, now and do")
    has_number = any(re.search(r"\d", t) for k, t in card_texts(img) if k != "label")
    # The thread cover carries the guide's own title (the first reply links that page), as in the approved sample.
    if lay != "thread_cover" and (has_number or img.get("rule")) and not img.get("source"):
        errs.append("card states a number or a platform rule: image.source is required")
    if img.get("source") and len(img["source"]) > LIMITS["source"]:
        errs.append(f"source over {LIMITS['source']} chars")
    return errs


def norm_words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9.']*[a-z0-9]|[a-z0-9]", s.lower().replace("’", "'"))


def copy_match_errors(img: dict, post_copy: str) -> list[str]:
    """Card words must come from the post: the whole headline, every number and every card key."""
    post = set(norm_words(post_copy))
    errs = []
    for w in norm_words(plain_headline(img.get("headline", ""))):
        if w not in post:
            errs.append(f"headline word {w!r} is not in the post copy")
    for kind, text in card_texts(img):
        if kind == "label":
            continue
        for n in re.findall(r"\d+(?:[.,]\d+)*%?", text):
            if n.rstrip("%") not in post and n not in post:
                errs.append(f"number {n!r} on the card is not in the post copy")
        if kind == "k":
            for w in norm_words(text):
                if w not in post:
                    errs.append(f"card key {text!r} is not in the post copy")
    return sorted(set(errs))


def glyph_errors(img: dict) -> list[str]:
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return []
    cmap = set(TTFont(str(FONTS / "Poppins-Bold.ttf")).getBestCmap())
    bad = set()
    for _, t in card_texts(img) + [("source", img.get("source", ""))]:
        bad |= {c for c in t if ord(c) not in cmap and not c.isspace()}
    return [f"character {c!r} (U+{ord(c):04X}) is not in the brand fonts" for c in sorted(bad)]


def body(img: dict) -> str:
    lay = img["layout"]
    if lay == "thread_cover":
        rows = "".join(
            f'<div style="display:flex;align-items:center;margin-top:{0 if i == 1 else 14}px">'
            f'<span class="t" style="display:inline-flex;width:50px;height:50px;border-radius:14px;background:#15B5B0;color:#063831;align-items:center;justify-content:center;font-weight:700;font-size:30px;margin-right:24px;flex:none">{i}</span>'
            f'<span class="t" style="font-size:33px;font-weight:600">{esc(t)}</span></div>'
            for i, t in enumerate(img["sections"], 1))
        return (
            '<div class="abs" style="left:70px;top:160px;width:940px;height:1040px;display:flex;flex-direction:column;justify-content:center">'
            f'<div><span class="t" style="display:inline-block;background:#FFD60A;color:#1F2937;font-weight:600;font-size:30px;border-radius:40px;padding:10px 28px">{esc(img.get("label") or "NEW GUIDE")}</span></div>'
            f'<div class="h t" style="font-size:90px;margin-top:26px">{headline_html(img["headline"])}</div>'
            f'<div class="sub t" style="font-size:34px;margin-top:20px;line-height:1.35">{esc(img.get("sub", ""))}</div>'
            '<div class="box2" style="margin-top:32px;background:rgba(255,255,255,.08);border:2px solid rgba(143,220,217,.35);border-radius:22px;padding:26px 32px">'
            f'<div class="t" style="font-size:26px;font-weight:600;color:#8FDCD9;letter-spacing:.08em;margin-bottom:16px">{esc(box_title(img))}</div>'
            f"{rows}</div>"
            f'<div style="margin-top:32px"><span class="btn t" style="font-size:32px;padding:18px 34px">{esc(ARROW)}</span></div></div>'
        )
    rows = ""
    if lay == "stat_cards":
        for c in img["cards"]:
            rows += (
                '<div class="box"><div style="min-width:330px;white-space:nowrap;margin-right:20px">'
                f'<div class="t" style="font-size:30px;font-weight:600;color:#8FDCD9">{esc(c["k"])}</div>'
                f'<div class="t" style="font-size:46px;font-weight:700;color:#15B5B0;line-height:1.1">{esc(c["value"])}</div></div>'
                f'<div class="t" style="font-size:30px;font-weight:500;line-height:1.3">{esc(c["text"])}</div></div>'
            )
    elif lay == "checklist":
        for r in img["rows"]:
            rows += f'<div class="box"><div class="tick"></div><div class="t" style="font-size:32px;font-weight:500;line-height:1.3">{esc(r)}</div></div>'
    elif lay == "steps":
        for i, r in enumerate(img["steps"], 1):
            rows += f'<div class="box"><div class="num t">{i}</div><div class="t" style="font-size:32px;font-weight:500;line-height:1.3">{esc(r)}</div></div>'
    elif lay == "before_after":
        for key, name, color in (("before", "Before", "#8FDCD9"), ("now", "Now", "#8FDCD9"), ("do", "Do this", "#FFD60A")):
            rows += (
                '<div class="box" style="display:block">'
                f'<div class="t" style="font-size:30px;font-weight:600;color:{color}">{name}</div>'
                f'<div class="t" style="font-size:34px;font-weight:500;line-height:1.3;margin-top:6px">{esc(img[key])}</div></div>'
            )
    return (
        '<div class="abs" id="content" style="left:70px;top:180px;width:940px">'
        f'<div class="pill t" style="font-size:26px">{esc(img.get("label", ""))}</div>'
        f'<div class="h t" style="font-size:%(hs)spx;margin-top:28px">{headline_html(img["headline"])}</div>'
        f'<div class="sub t" style="font-size:32px;margin-top:22px">{esc(img.get("sub", ""))}</div>'
        f"{rows}</div>"
    )


def page(img: dict, headline_px: int = 70) -> str:
    fonts = FONTS.resolve().as_uri()
    src = ""
    if img.get("source"):
        publisher, _, rest = img["source"].partition(",")
        src = (
            '<div class="abs src" style="left:70px;right:70px;bottom:120px;font-size:22px;color:#8FDCD9;font-family:I">'
            f'<b style="color:#fff;font-family:P">Source:</b> {esc(publisher)}{"," + esc(rest) if rest else ""}</div>'
        )
    inner = body(img).replace("%(hs)s", str(headline_px))
    return (
        "<html><head><meta charset='utf-8'><style>" + CSS.replace("{F}", fonts) + "</style></head><body>"
        f"<div class='c' style='width:{W}px;height:{H}px'><div class='dots'></div>"
        f'<div class="abs" style="left:70px;top:70px"><img id="logo" src="{LOGO.resolve().as_uri()}" style="height:64px"></div>'
        f"{inner}{src}"
        '<div class="abs foot" style="left:70px;bottom:62px;font-size:26px;font-weight:500;color:#8FDCD9">afrazalam.com</div>'
        "</div></body></html>"
    )


MEASURE_JS = """() => {
  const r = e => e.getBoundingClientRect();
  const out = {texts: [], logo: null, fontsOk: document.fonts.check('700 40px P')};
  const lg = document.getElementById('logo'); const b = r(lg);
  out.logo = {left: b.left, top: b.top, height: b.height, loaded: lg.complete && lg.naturalWidth > 0};
  document.querySelectorAll('.t, .src, .foot').forEach(e => {
    const k = r(e); const range = document.createRange(); range.selectNodeContents(e);
    const tr = range.getBoundingClientRect();
    out.texts.push({cls: e.className, text: e.innerText, size: parseFloat(getComputedStyle(e).fontSize),
      left: Math.min(k.left, tr.left), right: Math.max(k.right, tr.right), top: k.top, bottom: Math.max(k.bottom, tr.bottom),
      overflow: e.scrollWidth > e.clientWidth + 1});
  });
  document.querySelectorAll('.box, .box2').forEach(e => { const k = r(e);
    out.texts.push({cls: 'box', text: '', size: 99, left: k.left, right: k.right, top: k.top, bottom: k.bottom,
      overflow: e.scrollWidth > e.clientWidth + 1}); });
  return out;
}"""


def qa(m: dict) -> list[str]:
    errs = []
    if not m["fontsOk"]:
        errs.append("brand font P did not load")
    if not m["logo"]["loaded"]:
        errs.append("logo did not load")
    elif (round(m["logo"]["left"]), round(m["logo"]["top"]), round(m["logo"]["height"])) != (70, 70, 64):
        errs.append(f"logo not at (70, 70, height 64): {m['logo']}")
    src_top = min((t["top"] for t in m["texts"] if "src" in t["cls"]), default=None)
    limit = min(CONTENT_BOTTOM, src_top - 16) if src_top is not None else CONTENT_BOTTOM
    for t in m["texts"]:
        is_src, is_foot = "src" in t["cls"], "foot" in t["cls"]
        if t["left"] < SAFE_LEFT - 0.5 or t["right"] > SAFE_RIGHT + 0.5:
            errs.append(f"outside x 70 to 1010: {t['text'][:40]!r} ({t['left']:.0f} to {t['right']:.0f})")
        if t["overflow"]:
            errs.append(f"text overflows its box: {t['text'][:40]!r}")
        if not (is_src or is_foot) and t["bottom"] > limit + 0.5:
            errs.append(f"content below y {limit:.0f}: {t['text'][:40]!r} (bottom {t['bottom']:.0f})")
        if not is_src and t["size"] < MIN_FONT:
            errs.append(f"text under {MIN_FONT}px: {t['text'][:40]!r}")
        if is_src and t["size"] < SOURCE_FONT:
            errs.append("source line under 22px")
    return errs


def render(draft_path: Path) -> dict:
    from playwright.sync_api import sync_playwright

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    img = draft.get("image") or {}
    out = draft_path.parent
    post_copy = "\n".join(draft.get("parts", []))
    errors = check_limits(img)
    if not errors:
        errors += copy_match_errors(img, post_copy) + glyph_errors(img)
    manifest = {"layout": img.get("layout"), "size": [W, H], "ok": False, "errors": errors,
                "logo_sha256": hashlib.sha256(LOGO.read_bytes()).hexdigest(),
                "card_text": [t for _, t in card_texts(img)], "source_line": img.get("source")}
    if errors:
        (out / "render_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest
    html_path, png, prev = out / "card.html", out / "image.png", out / "preview_540.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--allow-file-access-from-files"])
        qa_errs, used = [], None
        for hs in ((90,) if img["layout"] == "thread_cover" else (70, 64, 58)):
            html_path.write_text(page(img, hs), encoding="utf-8")
            pg = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pg.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            qa_errs = qa(pg.evaluate(MEASURE_JS))
            if not qa_errs:
                pg.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": W, "height": H})
                pg.close()
                used = hs
                break
            pg.close()
        if used is not None:
            small = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=0.5)
            small.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            small.evaluate("document.fonts.ready")
            small.screenshot(path=str(prev), clip={"x": 0, "y": 0, "width": W, "height": H})
            small.close()
        browser.close()
    manifest["errors"] = qa_errs
    if used is not None:
        from PIL import Image
        with Image.open(png) as im:
            manifest["size"] = list(im.size)
            if im.size != (W, H):
                manifest["errors"].append(f"image is {im.size}, expected {(W, H)}")
        with Image.open(prev) as im:
            manifest["preview_size"] = list(im.size)
            if im.size != (540, 675):
                manifest["errors"].append(f"preview is {im.size}, expected (540, 675)")
        manifest.update({"headline_px": used, "image": str(png), "preview": str(prev),
                         "min_text_px_at_540": (MIN_FONT / 2, SOURCE_FONT / 2)})
    manifest["ok"] = not manifest["errors"]
    (out / "render_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    m = render(Path(sys.argv[1]))
    print(json.dumps({k: m.get(k) for k in ("ok", "layout", "errors", "image", "preview", "headline_px")}, indent=2, ensure_ascii=False))
    return 0 if m["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
