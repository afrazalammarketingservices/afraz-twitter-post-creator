#!/usr/bin/env python3
"""
Renders an X post image with HTML + headless Chromium (no Gemini, no image
API), per docs/X-ROUTINE-MIGRATION.md section 5.

- 1200 x 1200 opaque PNG, plus a 400 x 400 mobile preview.
- 5 layouts: comparison, stat_grid, before_after, checklist, single_stat.
- dark variant -> inputs/brand/logo_white.png, light -> logo_primary_color_transparent.png.
  The ORIGINAL logo file bytes are embedded unchanged; only CSS crops away its
  transparent padding. Nothing is redrawn.
- Only the approved headline and labels are drawn. Text auto-shrinks to fit;
  anything still clipped or outside the safe area is reported in the manifest.

Usage:
    python automation/routine/render_image.py outputs/<date>_<slug>/draft.json
Writes image.png, preview_mobile.png and render_manifest.json next to the draft
and sets draft["image"]["manifest"].
"""
import base64
import hashlib
import html
import json
import re
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
LOGOS = {
    "dark": REPO / "inputs" / "brand" / "logo_white.png",
    "light": REPO / "inputs" / "brand" / "logo_primary_color_transparent.png",
}
SIZE = 1200
SAFE = 48

THEMES = {
    "dark": {"bg": "#0B1220", "panel": "#111B2E", "border": "#1F2E48", "text": "#FFFFFF",
             "muted": "#9AA8BF", "accent": "#1BAE7D", "accent2": "#2DD4BF"},
    "light": {"bg": "#FFFFFF", "panel": "#F3F6F8", "border": "#DCE3EA", "text": "#111827",
              "muted": "#4B5563", "accent": "#0F9D7A", "accent2": "#14B8A6"},
}

NUM_LEAD = re.compile(r"^([$₹]?\d[\d,]*(?:\.\d+)?[%kKmMxX]?)(\s+.*)?$")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def num_split(label: str) -> str:
    m = NUM_LEAD.match(label.strip())
    if m and m.group(2):
        return f'<span class="acc">{esc(m.group(1))}</span>{esc(m.group(2))}'
    return esc(label)


def logo_html(variant: str) -> tuple[str, str]:
    path = LOGOS[variant]
    raw = path.read_bytes()
    with Image.open(path) as im:
        w, h = im.size
        bbox = im.convert("RGBA").getchannel("A").getbbox() or (0, 0, w, h)
    bx0, by0, bx1, by1 = bbox
    target_w = 440
    scale = target_w / (bx1 - bx0)
    box_h = round((by1 - by0) * scale)
    b64 = base64.b64encode(raw).decode("ascii")
    tag = (
        f'<div class="logo" style="width:{target_w}px;height:{box_h}px;">'
        f'<img src="data:image/png;base64,{b64}" style="width:{round(w * scale)}px;height:{round(h * scale)}px;'
        f'margin-left:{-round(bx0 * scale)}px;margin-top:{-round(by0 * scale)}px;" alt=""></div>'
    )
    return tag, hashlib.sha256(raw).hexdigest()


def body_for(layout: str, headline: str, labels: list[str]) -> str:
    h = f'<div class="t fit headline" data-min="56">{esc(headline)}</div>'
    L = labels + [""] * (3 - len(labels))
    if layout == "stat_grid":
        rows = "".join(
            f'<div class="row"><div class="bar"></div><div class="t fit rowtext" data-min="40">{num_split(x)}</div></div>'
            for x in labels
        )
        return h + f'<div class="stack">{rows}</div>'
    if layout == "checklist":
        rows = "".join(
            f'<div class="row"><div class="bullet">{i + 1}</div><div class="t fit rowtext" data-min="40">{num_split(x)}</div></div>'
            for i, x in enumerate(labels)
        )
        return h + f'<div class="stack">{rows}</div>'
    if layout in ("comparison", "before_after"):
        cls_l = "card muted-card" if layout == "before_after" else "card"
        foot = f'<div class="t fit footline" data-min="38">{num_split(L[2])}</div>' if L[2] else ""
        return h + (
            '<div class="pair">'
            f'<div class="{cls_l}"><div class="t fit cardtext" data-min="40">{num_split(L[0])}</div></div>'
            '<div class="arrow">&#8594;</div>'
            f'<div class="card hot"><div class="t fit cardtext" data-min="40">{num_split(L[1])}</div></div>'
            "</div>" + foot
        )
    if layout == "single_stat":
        sub = f'<div class="t fit sub" data-min="38">{esc(L[1])}</div>' if L[1] else ""
        return h + f'<div class="t fit bignum" data-min="120">{esc(L[0])}</div>' + sub
    raise ValueError(f"unknown layout {layout}")


def page(layout: str, variant: str, headline: str, labels: list[str]) -> tuple[str, str]:
    c = THEMES[variant]
    logo, logo_sha = logo_html(variant)
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&display=block');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ width: {SIZE}px; height: {SIZE}px; background: {c['bg']}; }}
    body {{ font-family: 'Poppins', 'Segoe UI', Arial, sans-serif; color: {c['text']};
            display: flex; flex-direction: column; padding: 96px 88px 64px; overflow: hidden; }}
    .main {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 56px; min-height: 0; }}
    .acc {{ color: {c['accent']}; }}
    .headline {{ font-size: 92px; font-weight: 800; line-height: 1.12; letter-spacing: -1px; max-height: 320px; text-wrap: balance; overflow: hidden; }}
    .stack {{ display: flex; flex-direction: column; gap: 30px; }}
    .row {{ display: flex; align-items: center; gap: 30px; height: 110px; }}
    .bar {{ width: 14px; height: 92px; border-radius: 7px; background: {c['accent']}; flex: none; }}
    .bullet {{ width: 92px; height: 92px; border-radius: 50%; border: 5px solid {c['accent']}; color: {c['accent']};
               font-size: 44px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex: none; }}
    .rowtext {{ font-size: 58px; font-weight: 700; line-height: 1.1; flex: 1; height: 110px; overflow: hidden;
                display: flex; align-items: center; }}
    .pair {{ display: flex; align-items: stretch; gap: 28px; height: 340px; }}
    .card {{ flex: 1; border-radius: 28px; background: {c['panel']}; border: 3px solid {c['border']};
             display: flex; align-items: center; justify-content: center; padding: 34px; min-width: 0; }}
    .muted-card {{ opacity: 0.75; }}
    .hot {{ border-color: {c['accent']}; }}
    .cardtext {{ font-size: 62px; font-weight: 700; line-height: 1.12; text-align: center; width: 100%;
                 max-height: 272px; overflow: hidden; }}
    .arrow {{ font-size: 80px; color: {c['accent']}; display: flex; align-items: center; flex: none; }}
    .footline {{ font-size: 50px; font-weight: 600; color: {c['muted']}; text-align: center; max-height: 130px; overflow: hidden; }}
    .bignum {{ font-size: 300px; font-weight: 800; line-height: 1; color: {c['accent']}; max-height: 330px; overflow: hidden; white-space: nowrap; }}
    .sub {{ font-size: 60px; font-weight: 600; color: {c['muted']}; line-height: 1.15; max-height: 150px; overflow: hidden; }}
    .footer {{ height: 170px; display: flex; align-items: flex-end; justify-content: center; flex: none; }}
    .logo {{ overflow: hidden; }}
    .logo img {{ display: block; }}
    """
    body = body_for(layout, headline, labels)
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head>"
           f"<body><div class='main'>{body}</div><div class='footer'>{logo}</div></body></html>")
    return doc, logo_sha


FIT_JS = """
async () => {
  await document.fonts.ready;
  const issues = [];
  let minFont = 9999;
  for (const el of document.querySelectorAll('.fit')) {
    let size = parseFloat(getComputedStyle(el).fontSize);
    const min = parseFloat(el.dataset.min || '34');
    // Tolerance absorbs glyph ascender/descender overhang, which is not clipping.
    const over = () => el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + Math.max(10, size * 0.25);
    while (over() && size > min) { size -= 2; el.style.fontSize = size + 'px'; }
    if (over()) issues.push('overflow: ' + el.textContent.slice(0, 40));
    minFont = Math.min(minFont, size);
  }
  for (const el of document.querySelectorAll('.t, .logo')) {
    const r = el.getBoundingClientRect();
    if (r.left < %(safe)d || r.top < %(safe)d || r.right > %(size)d - %(safe)d || r.bottom > %(size)d - %(safe)d)
      issues.push('outside safe area: ' + (el.textContent || 'logo').slice(0, 40));
  }
  return {issues, minFont};
}
""" % {"safe": SAFE, "size": SIZE}


def render(draft_path: Path) -> dict:
    from playwright.sync_api import sync_playwright

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    img = draft["image"]
    out_dir = draft_path.parent
    doc, logo_sha = page(img["layout"], img["variant"], img["headline"], img["labels"])
    (out_dir / "image.html").write_text(doc, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": SIZE, "height": SIZE}, device_scale_factor=1)
        pg.set_content(doc, wait_until="networkidle")
        fit = pg.evaluate(FIT_JS)
        png_path = out_dir / "image.png"
        pg.screenshot(path=str(png_path), full_page=False, omit_background=False)
        browser.close()

    with Image.open(png_path) as im:
        rgb = im.convert("RGB")
        rgb.save(png_path)
        rgb.resize((400, 400), Image.LANCZOS).save(out_dir / "preview_mobile.png")

    rel = lambda p: str(p.relative_to(REPO)).replace("\\", "/")
    manifest = {
        "image": rel(png_path),
        "mobile_preview": rel(out_dir / "preview_mobile.png"),
        "layout": img["layout"], "variant": img["variant"],
        "headline": img["headline"], "labels": img["labels"],
        "logo_file": rel(LOGOS[img["variant"]]), "logo_sha256": logo_sha,
        "fit_ok": not fit["issues"], "fit_issues": fit["issues"], "min_font_px": fit["minFont"],
    }
    man_path = out_dir / "render_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    draft["image"]["manifest"] = rel(man_path)
    draft_path.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: render_image.py <draft.json>", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(render(Path(sys.argv[1]).resolve()), indent=2, ensure_ascii=False))
