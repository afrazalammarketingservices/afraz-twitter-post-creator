#!/usr/bin/env python3
"""
Generates a post image with Gemini image generation, sized for X.

Usage:
    python generate_image.py --prompt "..." --slug "my-post" --index 1 [--ratio 16:9]

Ratios supported (matches X's own spec):
    16:9  -> 1200x675   (default, standard single/multi image post)
    1:1   -> 1080x1080  (square)
    4:5   -> 1080x1350  (portrait, better mobile real estate)
    9:16  -> 1080x1920  (vertical, mainly for video-style graphics)

Writes outputs/<date>_<slug>/image_<index>.png and prints the path.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[4]

RATIOS = {
    "16:9": (1200, 675),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "9:16": (1080, 1920),
}


def load_brand_notes() -> str:
    brand_dir = REPO_ROOT / "inputs" / "brand"
    if not brand_dir.exists():
        return ""
    notes = []
    for f in sorted(brand_dir.glob("*.md")):
        try:
            notes.append(f.read_text())
        except Exception:  # noqa: BLE001
            continue
    return "\n\n".join(notes)


def load_reference_note() -> str:
    ref_dir = REPO_ROOT / "inputs" / "references"
    if not ref_dir.exists():
        return ""
    images = list(ref_dir.glob("*.png")) + list(ref_dir.glob("*.jpg")) + list(ref_dir.glob("*.jpeg"))
    if images:
        return f"Match the visual style of the reference image(s) in inputs/references/: {[i.name for i in images]}."
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="What the image should show")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--index", type=int, default=1)
    parser.add_argument("--ratio", default="16:9", choices=list(RATIOS.keys()))
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_AI_STUDIO_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[generate_image] ERROR: GOOGLE_AI_STUDIO_API_KEY / GEMINI_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    width, height = RATIOS[args.ratio]
    brand_notes = load_brand_notes()
    reference_note = load_reference_note()

    full_prompt = (
        f"{args.prompt}\n\n"
        f"Image for a personal digital marketing consultant's X (Twitter) post. "
        f"Clean, professional, readable at small size on a phone screen. "
        f"Target dimensions {width}x{height} ({args.ratio}). "
        f"{('Brand notes: ' + brand_notes) if brand_notes else ''} "
        f"{reference_note}"
    ).strip()

    from google import genai  # imported here so --help works without the dep installed
    from PIL import Image
    import io

    client = genai.Client(api_key=api_key)

    print("[generate_image] generating...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[full_prompt],
    )

    image_bytes = None
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) is not None:
            image_bytes = part.inline_data.data
            break

    if image_bytes is None:
        print("[generate_image] ERROR: no image returned. Try again or adjust the prompt.", file=sys.stderr)
        sys.exit(1)

    img = Image.open(io.BytesIO(image_bytes))
    if img.size != (width, height):
        img = img.resize((width, height))

    out_dir = args.out_dir
    if out_dir is None:
        date_slug = datetime.now().strftime("%Y-%m-%d")
        out_dir = REPO_ROOT / "outputs" / f"{date_slug}_{args.slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"image_{args.index}.png"
    img.save(out_path)
    print(f"[generate_image] wrote {out_path} ({width}x{height})")


if __name__ == "__main__":
    main()
