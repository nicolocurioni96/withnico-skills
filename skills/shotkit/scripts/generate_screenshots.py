#!/usr/bin/env python3
"""
shotkit — Screenshot Compositing Engine

Renders styled App Store screenshots by combining raw UI captures with
text overlays and template styles. Outputs ASC-ready folder structure.

Usage:
  python3 generate_screenshots.py \
    --app-name "YourApp" \
    --captures ./raw-captures \
    --copy ./copy.json \
    --template bold \
    --devices iphone-6.9 ipad-13 \
    --locales en-US it \
    --output ./screenshots-output

Templates: minimal, bold, dark, editorial, flat
"""

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: bash scripts/install_deps.sh")
    sys.exit(1)

# ─── Device Specs ────────────────────────────────────────────────────

DEVICE_SPECS = {
    "iphone-6.9":  {"size": (1320, 2868), "corner_radius": 120, "type": "phone"},
    "iphone-6.7":  {"size": (1290, 2796), "corner_radius": 110, "type": "phone"},
    "iphone-6.5":  {"size": (1242, 2688), "corner_radius": 100, "type": "phone"},
    "iphone-6.1":  {"size": (1179, 2556), "corner_radius": 95,  "type": "phone"},
    "ipad-13":     {"size": (2064, 2752), "corner_radius": 60,  "type": "tablet"},
    "ipad-12.9":   {"size": (2048, 2732), "corner_radius": 60,  "type": "tablet"},
    "ipad-11":     {"size": (1668, 2388), "corner_radius": 50,  "type": "tablet"},
}

# ─── Font Helpers ────────────────────────────────────────────────────

SKILL_ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = SKILL_ROOT / "assets" / "fonts"


def _find_system_font():
    """Find a usable system font on macOS."""
    candidates = [
        "/System/Library/Fonts/SFProDisplay-Bold.otf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay-Bold.otf",
        "/Library/Fonts/SF-Pro-Display-Bold.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _get_font(size, bold=True):
    """Load a font at the given size. Checks custom fonts first, then system."""
    # Check custom fonts in assets/fonts/
    if FONT_DIR.exists():
        ttf_files = sorted(FONT_DIR.glob("*.ttf")) + sorted(FONT_DIR.glob("*.otf"))
        bold_fonts = [f for f in ttf_files if "bold" in f.stem.lower()]
        regular_fonts = [f for f in ttf_files if "bold" not in f.stem.lower()]
        target = bold_fonts if bold else (regular_fonts or bold_fonts)
        if target:
            return ImageFont.truetype(str(target[0]), size)

    # Fall back to system font
    sys_font = _find_system_font()
    if sys_font:
        try:
            return ImageFont.truetype(sys_font, size)
        except Exception:
            pass

    # Last resort: default bitmap font
    return ImageFont.load_default()


def _get_text_height(draw, text, font):
    """Get the height of rendered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def _get_text_width(draw, text, font):
    """Get the width of rendered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


# ─── Drawing Helpers ─────────────────────────────────────────────────

def _rounded_rectangle(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def _create_gradient(size, color_top, color_bottom):
    """Create a vertical gradient image."""
    w, h = size
    img = Image.new("RGB", size)
    for y in range(h):
        ratio = y / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img


def _create_gradient_fast(size, color_top, color_bottom):
    """Create a vertical gradient using line drawing (much faster)."""
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _fit_screenshot(screenshot, target_w, target_h):
    """Resize screenshot to fit within target dimensions, maintaining aspect ratio."""
    img = screenshot.copy()
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    return img


def _round_corners(img, radius):
    """Apply rounded corners to an image."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    _rounded_rectangle(draw, (0, 0, img.size[0], img.size[1]), radius, fill=255)
    result = img.copy()
    result.putalpha(mask)
    return result


def _add_shadow(img, offset=20, blur_radius=40, opacity=80):
    """Add a drop shadow behind an image."""
    shadow_size = (
        img.size[0] + blur_radius * 4,
        img.size[1] + blur_radius * 4,
    )
    shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    sx = blur_radius * 2 + offset
    sy = blur_radius * 2 + offset
    shadow_draw.rectangle(
        [sx, sy, sx + img.size[0], sy + img.size[1]],
        fill=(0, 0, 0, opacity),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    # Paste original on top
    paste_x = blur_radius * 2
    paste_y = blur_radius * 2
    shadow.paste(img, (paste_x, paste_y), img if img.mode == "RGBA" else None)
    return shadow, paste_x, paste_y


# ─── Template Renderers ─────────────────────────────────────────────

def render_minimal(canvas_size, screenshot, headline, subline):
    """
    minimal — White background, device with shadow, text below.
    Clean and professional.
    """
    w, h = canvas_size
    bg_color = (248, 248, 248)
    text_color = (30, 30, 30)
    sub_color = (100, 100, 100)

    canvas = Image.new("RGB", canvas_size, bg_color)
    draw = ImageDraw.Draw(canvas)

    # Layout: UI takes top 65%, text in bottom 25%, margins 5%
    margin = int(w * 0.08)
    ui_max_w = w - margin * 2
    ui_max_h = int(h * 0.62)
    text_y_start = int(h * 0.70)

    # Resize and round corners on screenshot
    ui = _fit_screenshot(screenshot, ui_max_w, ui_max_h)
    ui = _round_corners(ui, 30)

    # Add shadow
    shadowed, sx, sy = _add_shadow(ui, offset=15, blur_radius=30, opacity=60)

    # Center the shadowed image
    ui_x = (w - shadowed.size[0]) // 2
    ui_y = int(h * 0.05)
    canvas.paste(shadowed, (ui_x, ui_y), shadowed)

    # Draw headline
    headline_font = _get_font(int(w * 0.065), bold=True)
    sub_font = _get_font(int(w * 0.04), bold=False)

    hw = _get_text_width(draw, headline, headline_font)
    draw.text(((w - hw) // 2, text_y_start), headline, fill=text_color, font=headline_font)

    # Draw subline
    sw = _get_text_width(draw, subline, sub_font)
    sub_y = text_y_start + _get_text_height(draw, headline, headline_font) + int(h * 0.02)
    draw.text(((w - sw) // 2, sub_y), subline, fill=sub_color, font=sub_font)

    return canvas


def render_bold(canvas_size, screenshot, headline, subline):
    """
    bold — Full-bleed gradient, large text at top, UI at bottom.
    High energy, punchy.
    """
    w, h = canvas_size
    color_top = (25, 25, 112)      # deep blue
    color_bottom = (128, 0, 128)   # purple

    canvas = _create_gradient_fast(canvas_size, color_top, color_bottom)
    draw = ImageDraw.Draw(canvas)

    text_color = (255, 255, 255)
    margin = int(w * 0.08)

    # Headline at top
    headline_font = _get_font(int(w * 0.085), bold=True)
    sub_font = _get_font(int(w * 0.045), bold=False)

    text_y = int(h * 0.06)
    draw.text((margin, text_y), headline, fill=text_color, font=headline_font)

    sub_y = text_y + _get_text_height(draw, headline, headline_font) + int(h * 0.015)
    draw.text((margin, sub_y), subline, fill=(220, 220, 255), font=sub_font)

    # UI at bottom 62%
    ui_max_w = w - margin * 2
    ui_max_h = int(h * 0.60)
    ui = _fit_screenshot(screenshot, ui_max_w, ui_max_h)
    corner_r = 30
    ui = _round_corners(ui, corner_r)

    ui_x = (w - ui.size[0]) // 2
    ui_y = h - ui.size[1] - int(h * 0.02)
    canvas.paste(ui, (ui_x, ui_y), ui)

    return canvas


def render_dark(canvas_size, screenshot, headline, subline):
    """
    dark — Near-black background with colored glow halo. Premium feel.
    """
    w, h = canvas_size
    bg_color = (10, 10, 14)
    glow_color = (40, 80, 200)
    text_color = (240, 240, 245)
    sub_color = (150, 150, 170)

    canvas = Image.new("RGB", canvas_size, bg_color)

    # Create glow effect behind device area
    glow_size = (int(w * 0.7), int(h * 0.5))
    glow = Image.new("RGB", glow_size, glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=min(glow_size) // 3))
    glow_x = (w - glow_size[0]) // 2
    glow_y = int(h * 0.10)

    # Blend glow onto canvas
    glow_rgba = glow.convert("RGBA")
    # Reduce opacity
    alpha = glow_rgba.split()[3] if glow_rgba.mode == "RGBA" else Image.new("L", glow.size, 60)
    alpha = Image.new("L", glow.size, 60)
    glow_rgba.putalpha(alpha)
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(glow_rgba, (glow_x, glow_y), glow_rgba)
    canvas = canvas_rgba.convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # Screenshot in center-top
    margin = int(w * 0.10)
    ui_max_w = w - margin * 2
    ui_max_h = int(h * 0.58)
    ui = _fit_screenshot(screenshot, ui_max_w, ui_max_h)
    ui = _round_corners(ui, 30)

    ui_x = (w - ui.size[0]) // 2
    ui_y = int(h * 0.08)
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(ui, (ui_x, ui_y), ui)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Text below
    text_y = int(h * 0.72)
    headline_font = _get_font(int(w * 0.065), bold=True)
    sub_font = _get_font(int(w * 0.04), bold=False)

    hw = _get_text_width(draw, headline, headline_font)
    draw.text(((w - hw) // 2, text_y), headline, fill=text_color, font=headline_font)

    sw = _get_text_width(draw, subline, sub_font)
    sub_y = text_y + _get_text_height(draw, headline, headline_font) + int(h * 0.02)
    draw.text(((w - sw) // 2, sub_y), subline, fill=sub_color, font=sub_font)

    return canvas


def render_editorial(canvas_size, screenshot, headline, subline):
    """
    editorial — Magazine layout. Text on left, UI on right, accent strip.
    """
    w, h = canvas_size
    bg_color = (245, 242, 238)     # warm paper
    accent_color = (255, 80, 64)   # red accent
    text_color = (30, 30, 30)
    sub_color = (80, 80, 80)

    canvas = Image.new("RGB", canvas_size, bg_color)
    draw = ImageDraw.Draw(canvas)

    # Left accent strip
    strip_w = int(w * 0.015)
    draw.rectangle([0, 0, strip_w, h], fill=accent_color)

    # Text on left side (left 40%)
    text_margin_left = int(w * 0.06)
    text_max_w = int(w * 0.35)
    text_y = int(h * 0.35)

    headline_font = _get_font(int(w * 0.06), bold=True)
    sub_font = _get_font(int(w * 0.035), bold=False)

    # Word-wrap headline
    words = headline.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        if _get_text_width(draw, test, headline_font) <= text_max_w:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y = text_y
    for line in lines:
        draw.text((text_margin_left, y), line, fill=text_color, font=headline_font)
        y += _get_text_height(draw, line, headline_font) + int(h * 0.008)

    y += int(h * 0.02)
    # Word-wrap subline
    words = subline.split()
    sub_lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        if _get_text_width(draw, test, sub_font) <= text_max_w:
            current_line = test
        else:
            if current_line:
                sub_lines.append(current_line)
            current_line = word
    if current_line:
        sub_lines.append(current_line)

    for line in sub_lines:
        draw.text((text_margin_left, y), line, fill=sub_color, font=sub_font)
        y += _get_text_height(draw, line, sub_font) + int(h * 0.005)

    # UI on right side
    ui_margin = int(w * 0.44)
    ui_max_w = w - ui_margin - int(w * 0.04)
    ui_max_h = int(h * 0.75)
    ui = _fit_screenshot(screenshot, ui_max_w, ui_max_h)
    ui = _round_corners(ui, 25)

    ui_x = ui_margin
    ui_y = (h - ui.size[1]) // 2

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(ui, (ui_x, ui_y), ui)
    canvas = canvas_rgba.convert("RGB")

    return canvas


def render_flat(canvas_size, screenshot, headline, subline):
    """
    flat — Full-bleed UI with semi-transparent text bar at bottom.
    Immersive, UI-first.
    """
    w, h = canvas_size

    # Resize screenshot to fill entire canvas
    ui = screenshot.resize(canvas_size, Image.LANCZOS)
    canvas = ui.convert("RGBA")

    # Semi-transparent dark bar at bottom
    bar_h = int(h * 0.18)
    bar = Image.new("RGBA", (w, bar_h), (0, 0, 0, 180))
    canvas.paste(bar, (0, h - bar_h), bar)

    draw = ImageDraw.Draw(canvas)
    text_color = (255, 255, 255)
    sub_color = (200, 200, 210)

    margin = int(w * 0.06)
    headline_font = _get_font(int(w * 0.06), bold=True)
    sub_font = _get_font(int(w * 0.035), bold=False)

    hl_y = h - bar_h + int(bar_h * 0.2)
    draw.text((margin, hl_y), headline, fill=text_color, font=headline_font)

    sub_y = hl_y + _get_text_height(draw, headline, headline_font) + int(h * 0.01)
    draw.text((margin, sub_y), subline, fill=sub_color, font=sub_font)

    return canvas.convert("RGB")


RENDERERS = {
    "minimal": render_minimal,
    "bold": render_bold,
    "dark": render_dark,
    "editorial": render_editorial,
    "flat": render_flat,
}

# ─── Screenshot Matching ────────────────────────────────────────────

def _find_captures(captures_dir):
    """Find and sort raw capture files."""
    captures_path = Path(captures_dir)
    if not captures_path.exists():
        return []

    files = []
    # Check for device subdirectories (from auto_capture.sh)
    subdirs = [d for d in captures_path.iterdir() if d.is_dir()]
    if subdirs:
        # Use first device subdir as source
        for subdir in subdirs:
            subfiles = sorted(
                f for f in subdir.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            )
            if subfiles:
                files = subfiles
                break

    if not files:
        # Flat directory
        files = sorted(
            f for f in captures_path.iterdir()
            if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
        )

    return files


def _load_copy(copy_path, locale):
    """Load copy data for a locale."""
    with open(copy_path, "r") as f:
        data = json.load(f)

    # Remove comment keys
    data = {k: v for k, v in data.items() if not k.startswith("_")}

    if locale in data:
        return data[locale].get("screenshots", [])

    # Try language code without region
    lang = locale.split("-")[0]
    for key in data:
        if key.startswith(lang):
            return data[key].get("screenshots", [])

    # Fall back to first locale
    first_key = next(iter(data), None)
    if first_key:
        print(f"  Warning: locale '{locale}' not in copy file, using '{first_key}'")
        return data[first_key].get("screenshots", [])

    return []


# ─── Main Pipeline ──────────────────────────────────────────────────

def generate(
    app_name,
    captures_dir,
    copy_path,
    template,
    devices,
    locales,
    output_dir,
):
    """Run the full compositing pipeline."""
    renderer = RENDERERS.get(template)
    if not renderer:
        print(f"Error: Unknown template '{template}'. Choose from: {', '.join(RENDERERS.keys())}")
        sys.exit(1)

    captures = _find_captures(captures_dir)
    if not captures:
        print(f"Error: No screenshots found in {captures_dir}")
        print("  Supported formats: .png, .jpg, .jpeg")
        sys.exit(1)

    print(f"\nShotkit — Compositing Engine")
    print(f"App        : {app_name}")
    print(f"Template   : {template}")
    print(f"Captures   : {len(captures)} files")
    print(f"Devices    : {', '.join(devices)}")
    print(f"Locales    : {', '.join(locales)}")
    print(f"Output     : {output_dir}\n")

    output_base = Path(output_dir)
    total = 0

    for locale in locales:
        copy_data = _load_copy(copy_path, locale) if copy_path else []

        for device_key in devices:
            spec = DEVICE_SPECS.get(device_key)
            if not spec:
                print(f"  Warning: Unknown device '{device_key}', skipping.")
                continue

            canvas_size = spec["size"]
            device_dir = output_base / locale / device_key
            device_dir.mkdir(parents=True, exist_ok=True)

            for idx, capture_file in enumerate(captures):
                # Get copy for this screenshot
                if idx < len(copy_data):
                    headline = copy_data[idx].get("headline", app_name)
                    subline = copy_data[idx].get("subline", "")
                else:
                    headline = app_name
                    subline = ""

                # Load raw screenshot
                try:
                    raw = Image.open(capture_file).convert("RGB")
                except Exception as e:
                    print(f"  Error loading {capture_file}: {e}")
                    continue

                # Render composite
                result = renderer(canvas_size, raw, headline, subline)

                # Save
                out_name = f"{idx + 1:02d}_{capture_file.stem.split('_', 1)[-1] if '_' in capture_file.stem else capture_file.stem}.png"
                out_path = device_dir / out_name
                result.save(str(out_path), "PNG", optimize=True)
                total += 1

                print(f"  [{locale}/{device_key}] {out_name}")

    print(f"\nDone. Generated {total} screenshot(s) in {output_dir}")
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Shotkit — App Store Screenshot Compositing Engine"
    )
    parser.add_argument("--app-name", required=True, help="App display name")
    parser.add_argument("--captures", required=True, help="Path to raw captures directory")
    parser.add_argument("--copy", default=None, help="Path to copy.json with headlines/sublines")
    parser.add_argument(
        "--template",
        default="minimal",
        choices=list(RENDERERS.keys()),
        help="Template style (default: minimal)",
    )
    parser.add_argument(
        "--devices",
        nargs="+",
        default=["iphone-6.9"],
        help="Device keys (default: iphone-6.9)",
    )
    parser.add_argument(
        "--locales",
        nargs="+",
        default=["en-US"],
        help="Locale codes (default: en-US)",
    )
    parser.add_argument("--output", default="./screenshots-output", help="Output directory")

    args = parser.parse_args()

    generate(
        app_name=args.app_name,
        captures_dir=args.captures,
        copy_path=args.copy,
        template=args.template,
        devices=args.devices,
        locales=args.locales,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
