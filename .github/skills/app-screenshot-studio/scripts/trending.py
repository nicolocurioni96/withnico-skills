#!/usr/bin/env python3
"""
shotkit — Trending Styles Engine

Data-driven renderer that generates App Store screenshots following
current top-charting visual trends. Supports:

  - Curated seasonal palettes (trending_palettes.json)
  - Auto-palette from app icon color extraction
  - Custom brand color input
  - Multiple layout variants

Usage via generate_screenshots.py:
  --template trending                          # random trending palette
  --template trending --palette aurora         # specific palette
  --template trending --icon ./icon.png        # auto from app icon
  --template trending --brand-color "#1E90FF"  # custom brand color
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from color_utils import (
    extract_dominant_colors,
    generate_gradient_from_colors,
    ensure_text_contrast,
    darken_color,
)

SCRIPT_DIR = Path(__file__).resolve().parent
PALETTES_FILE = SCRIPT_DIR / "trending_palettes.json"


def _load_palettes():
    """Load trending palettes data."""
    with open(PALETTES_FILE) as f:
        return json.load(f)


def _get_font(size, bold=True):
    """Import font loader from generate_screenshots."""
    # Import here to avoid circular dependency
    from generate_screenshots import _get_font as gf
    return gf(size, bold)


def _get_text_dims(draw, text, font):
    """Get width and height of text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _create_gradient(size, color_top, color_bottom):
    """Fast vertical gradient."""
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


def _round_corners(img, radius):
    """Apply rounded corners."""
    from generate_screenshots import _round_corners as rc
    return rc(img, radius)


def _fit_screenshot(screenshot, target_w, target_h):
    """Resize screenshot to fit."""
    img = screenshot.copy()
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    return img


def resolve_palette(palette_name=None, icon_path=None, brand_color=None):
    """
    Resolve which palette/colors to use.

    Priority:
      1. brand_color (hex string) → generate gradient from it
      2. icon_path → extract colors from icon
      3. palette_name → look up in trending_palettes.json
      4. None → random trending palette
    """
    data = _load_palettes()
    palettes = data.get("palettes", [])
    typography = data.get("typography", {})
    layouts = data.get("layouts", [])

    if brand_color:
        # Parse hex color
        hex_str = brand_color.lstrip("#")
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        base_color = (r, g, b)
        dark = darken_color(base_color, 0.4)
        text_color = ensure_text_contrast((255, 255, 255), dark)
        sub_color = ensure_text_contrast((200, 200, 220), dark)
        return {
            "name": "custom-brand",
            "gradient_top": dark,
            "gradient_bottom": base_color,
            "text_color": text_color,
            "sub_color": sub_color,
            "typography": typography,
            "layout": layouts[0] if layouts else None,
        }

    if icon_path and Path(icon_path).exists():
        colors = extract_dominant_colors(icon_path)
        if len(colors) >= 2:
            top, bottom = generate_gradient_from_colors(colors)
            text_color = ensure_text_contrast((255, 255, 255), top)
            sub_color = ensure_text_contrast((200, 200, 220), top)
            return {
                "name": "icon-auto",
                "gradient_top": top,
                "gradient_bottom": bottom,
                "text_color": text_color,
                "sub_color": sub_color,
                "typography": typography,
                "layout": layouts[0] if layouts else None,
            }

    if palette_name:
        for p in palettes:
            if p["name"] == palette_name:
                return {
                    "name": p["name"],
                    "gradient_top": tuple(p["gradient_top"]),
                    "gradient_bottom": tuple(p["gradient_bottom"]),
                    "text_color": tuple(p["text_color"]),
                    "sub_color": tuple(p["sub_color"]),
                    "typography": typography,
                    "layout": layouts[0] if layouts else None,
                }
        print(f"  Warning: Palette '{palette_name}' not found. Using random.")

    # Random palette
    p = random.choice(palettes)
    layout = random.choice(layouts) if layouts else None
    return {
        "name": p["name"],
        "gradient_top": tuple(p["gradient_top"]),
        "gradient_bottom": tuple(p["gradient_bottom"]),
        "text_color": tuple(p["text_color"]),
        "sub_color": tuple(p["sub_color"]),
        "typography": typography,
        "layout": layout,
    }


def render_trending(canvas_size, screenshot, headline, subline,
                    palette_name=None, icon_path=None, brand_color=None):
    """
    Trending meta-renderer. Produces screenshots following current
    App Store visual trends using curated palettes or auto-extracted colors.
    """
    w, h = canvas_size
    palette = resolve_palette(palette_name, icon_path, brand_color)
    layout = palette.get("layout") or {}
    typo = palette.get("typography") or {}

    grad_top = palette["gradient_top"]
    grad_bottom = palette["gradient_bottom"]
    text_color = palette["text_color"]
    sub_color = palette["sub_color"]

    # Layout params
    text_pos = layout.get("text_position", "top")
    text_y_ratio = layout.get("text_y_ratio", 0.06)
    ui_y_start = layout.get("ui_y_start_ratio", 0.30)
    ui_scale = layout.get("ui_scale", 0.65)

    # Typography
    hl_scale = typo.get("headline_scale", 0.08)
    sl_scale = typo.get("subline_scale", 0.042)

    # Create gradient background
    canvas = _create_gradient(canvas_size, grad_top, grad_bottom)
    draw = ImageDraw.Draw(canvas)

    margin = int(w * 0.07)
    headline_font = _get_font(int(w * hl_scale), bold=True)
    sub_font = _get_font(int(w * sl_scale), bold=False)

    # Prepare screenshot
    ui_max_w = w - margin * 2
    ui_max_h = int(h * ui_scale)
    ui = _fit_screenshot(screenshot, ui_max_w, ui_max_h)
    ui = _round_corners(ui, 30)

    if text_pos == "top":
        # Text at top, UI at bottom
        text_y = int(h * text_y_ratio)
        draw.text((margin, text_y), headline, fill=text_color, font=headline_font)
        hl_w, hl_h = _get_text_dims(draw, headline, headline_font)
        sub_y = text_y + hl_h + int(h * 0.015)
        draw.text((margin, sub_y), subline, fill=sub_color, font=sub_font)

        ui_x = (w - ui.size[0]) // 2
        ui_y = int(h * ui_y_start)
        # If UI would overlap text, push it down
        text_bottom = sub_y + _get_text_dims(draw, subline, sub_font)[1] + int(h * 0.03)
        if ui_y < text_bottom:
            ui_y = text_bottom

        # Clip UI to canvas bottom
        if ui_y + ui.size[1] > h:
            ui_y = h - ui.size[1]

        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.paste(ui, (ui_x, max(0, ui_y)), ui)
        canvas = canvas_rgba.convert("RGB")

    else:
        # Text at bottom, UI at center-top
        ui_x = (w - ui.size[0]) // 2
        ui_y = int(h * ui_y_start)
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.paste(ui, (ui_x, ui_y), ui)
        canvas = canvas_rgba.convert("RGB")
        draw = ImageDraw.Draw(canvas)

        text_y = int(h * text_y_ratio)
        hl_w, hl_h = _get_text_dims(draw, headline, headline_font)
        draw.text(((w - hl_w) // 2, text_y), headline, fill=text_color, font=headline_font)
        sl_w, sl_h = _get_text_dims(draw, subline, sub_font)
        sub_y = text_y + hl_h + int(h * 0.015)
        draw.text(((w - sl_w) // 2, sub_y), subline, fill=sub_color, font=sub_font)

    return canvas


def list_palettes():
    """Print all available palette names."""
    data = _load_palettes()
    print(f"\nShotkit Trending Palettes (v{data.get('version', 'unknown')})")
    print("=" * 50)
    for p in data.get("palettes", []):
        cats = ", ".join(p.get("categories", []))
        print(f"  {p['name']:15s}  {p['vibe']:15s}  {cats}")
    print("")
