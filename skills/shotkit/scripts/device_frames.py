#!/usr/bin/env python3
"""
shotkit — Device Frame Renderer

Draws realistic Apple device frames (bezels) programmatically with Pillow.
Supports iPhone 16 Pro Max, iPhone 15 Pro Max, iPad Pro 13", iPad Pro 12.9",
with multiple frame colors (titanium variants, space black, silver).

Usage:
  from device_frames import render_device_frame
  framed = render_device_frame(screenshot, "iphone-6.9", color="natural-titanium")
"""

from PIL import Image, ImageDraw, ImageFilter

# ─── Device Frame Specifications ─────────────────────────────────────
#
# All values are in pixels at the device's native resolution.
# Bezel widths are calculated from screen-to-body ratios and
# physical measurements from Apple specs.

FRAME_SPECS = {
    "iphone-6.9": {
        "screen": (1320, 2868),
        "bezel_top": 120,
        "bezel_bottom": 120,
        "bezel_side": 48,
        "outer_radius": 165,
        "inner_radius": 132,
        "has_dynamic_island": True,
        "dynamic_island": {
            "width": 370,
            "height": 108,
            "radius": 54,
            "top_offset": 48,
        },
        "type": "phone",
    },
    "iphone-6.7": {
        "screen": (1290, 2796),
        "bezel_top": 115,
        "bezel_bottom": 115,
        "bezel_side": 46,
        "outer_radius": 158,
        "inner_radius": 126,
        "has_dynamic_island": True,
        "dynamic_island": {
            "width": 360,
            "height": 105,
            "radius": 52,
            "top_offset": 45,
        },
        "type": "phone",
    },
    "iphone-6.5": {
        "screen": (1242, 2688),
        "bezel_top": 110,
        "bezel_bottom": 110,
        "bezel_side": 44,
        "outer_radius": 145,
        "inner_radius": 115,
        "has_dynamic_island": False,
        "notch": {
            "width": 640,
            "height": 90,
            "radius": 45,
        },
        "type": "phone",
    },
    "iphone-6.1": {
        "screen": (1179, 2556),
        "bezel_top": 105,
        "bezel_bottom": 105,
        "bezel_side": 42,
        "outer_radius": 138,
        "inner_radius": 110,
        "has_dynamic_island": True,
        "dynamic_island": {
            "width": 340,
            "height": 100,
            "radius": 50,
            "top_offset": 42,
        },
        "type": "phone",
    },
    "ipad-13": {
        "screen": (2064, 2752),
        "bezel_top": 80,
        "bezel_bottom": 80,
        "bezel_side": 80,
        "outer_radius": 72,
        "inner_radius": 48,
        "has_dynamic_island": False,
        "type": "tablet",
    },
    "ipad-12.9": {
        "screen": (2048, 2732),
        "bezel_top": 85,
        "bezel_bottom": 85,
        "bezel_side": 85,
        "outer_radius": 68,
        "inner_radius": 44,
        "has_dynamic_island": False,
        "type": "tablet",
    },
    "ipad-11": {
        "screen": (1668, 2388),
        "bezel_top": 70,
        "bezel_bottom": 70,
        "bezel_side": 70,
        "outer_radius": 58,
        "inner_radius": 38,
        "has_dynamic_island": False,
        "type": "tablet",
    },
}

# ─── Frame Colors ────────────────────────────────────────────────────

FRAME_COLORS = {
    # iPhone 16 Pro / Pro Max
    "black-titanium":   {"frame": (60, 60, 61),    "highlight": (85, 85, 86),    "shadow": (35, 35, 36)},
    "natural-titanium": {"frame": (194, 188, 178),  "highlight": (215, 210, 200), "shadow": (160, 155, 145)},
    "white-titanium":   {"frame": (242, 241, 237),  "highlight": (250, 250, 248), "shadow": (210, 208, 204)},
    "desert-titanium":  {"frame": (191, 164, 143),  "highlight": (215, 192, 172), "shadow": (155, 132, 115)},
    # iPad
    "space-black":      {"frame": (45, 45, 47),     "highlight": (70, 70, 72),    "shadow": (25, 25, 27)},
    "silver":           {"frame": (210, 211, 213),   "highlight": (230, 231, 233), "shadow": (180, 181, 183)},
}

# Default colors per device type
DEFAULT_COLORS = {
    "phone": "natural-titanium",
    "tablet": "space-black",
}


def _rounded_rect_mask(size, radius):
    """Create a rounded rectangle mask."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    # Draw the rounded rectangle
    draw.rectangle([radius, 0, w - radius, h], fill=255)
    draw.rectangle([0, radius, w, h - radius], fill=255)
    draw.pieslice([0, 0, radius * 2, radius * 2], 180, 270, fill=255)
    draw.pieslice([w - radius * 2, 0, w, radius * 2], 270, 360, fill=255)
    draw.pieslice([0, h - radius * 2, radius * 2, h], 90, 180, fill=255)
    draw.pieslice([w - radius * 2, h - radius * 2, w, h], 0, 90, fill=255)
    return mask


def _draw_dynamic_island(draw, screen_x, screen_y, screen_w, di_spec):
    """Draw the Dynamic Island pill shape."""
    di_w = di_spec["width"]
    di_h = di_spec["height"]
    di_r = di_spec["radius"]
    di_top = di_spec["top_offset"]

    # Center horizontally on screen
    di_x = screen_x + (screen_w - di_w) // 2
    di_y = screen_y + di_top

    # Draw pill shape (rounded rectangle)
    draw.rounded_rectangle(
        [di_x, di_y, di_x + di_w, di_y + di_h],
        radius=di_r,
        fill=(0, 0, 0),
    )


def _draw_notch(draw, screen_x, screen_y, screen_w, notch_spec):
    """Draw a notch (for older iPhones like 6.5")."""
    n_w = notch_spec["width"]
    n_h = notch_spec["height"]
    n_r = notch_spec["radius"]

    n_x = screen_x + (screen_w - n_w) // 2
    n_y = screen_y

    # Notch shape: rectangle with rounded bottom corners
    draw.rectangle([n_x, n_y, n_x + n_w, n_y + n_h - n_r], fill=(0, 0, 0))
    draw.rectangle([n_x + n_r, n_y, n_x + n_w - n_r, n_y + n_h], fill=(0, 0, 0))
    draw.pieslice([n_x, n_y + n_h - n_r * 2, n_x + n_r * 2, n_y + n_h], 90, 180, fill=(0, 0, 0))
    draw.pieslice([n_x + n_w - n_r * 2, n_y + n_h - n_r * 2, n_x + n_w, n_y + n_h], 0, 90, fill=(0, 0, 0))


def render_device_frame(screenshot, device_key, color=None, show_buttons=True):
    """
    Render a device frame around a screenshot.

    Args:
        screenshot: PIL Image of the app UI (will be resized to fit)
        device_key: e.g. "iphone-6.9", "ipad-13"
        color: frame color name (e.g. "natural-titanium", "space-black")
               or None for default
        show_buttons: whether to draw side buttons

    Returns:
        PIL Image (RGBA) of the device with frame, ready to composite
    """
    spec = FRAME_SPECS.get(device_key)
    if not spec:
        # No frame spec — return screenshot as-is
        return screenshot.convert("RGBA")

    screen_w, screen_h = spec["screen"]
    bezel_t = spec["bezel_top"]
    bezel_b = spec["bezel_bottom"]
    bezel_s = spec["bezel_side"]
    outer_r = spec["outer_radius"]
    inner_r = spec["inner_radius"]

    # Resolve frame color
    if color is None:
        color = DEFAULT_COLORS.get(spec["type"], "natural-titanium")
    colors = FRAME_COLORS.get(color, FRAME_COLORS["natural-titanium"])

    frame_color = colors["frame"]
    highlight_color = colors["highlight"]
    shadow_color = colors["shadow"]

    # Total device size
    device_w = screen_w + bezel_s * 2
    device_h = screen_h + bezel_t + bezel_b

    # Create device image with transparency
    device = Image.new("RGBA", (device_w, device_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(device)

    # 1. Draw outer frame (device body)
    draw.rounded_rectangle(
        [0, 0, device_w, device_h],
        radius=outer_r,
        fill=frame_color,
    )

    # 2. Draw subtle frame edge highlights (top-left light, bottom-right shadow)
    # Top edge highlight
    draw.rounded_rectangle(
        [1, 1, device_w - 1, device_h // 3],
        radius=outer_r,
        fill=highlight_color,
    )
    # Redraw main body on top, slightly inset, to create edge effect
    draw.rounded_rectangle(
        [3, 3, device_w - 3, device_h - 3],
        radius=outer_r - 2,
        fill=frame_color,
    )

    # 3. Draw screen cutout (black underneath for screen area)
    screen_x = bezel_s
    screen_y = bezel_t

    draw.rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=inner_r,
        fill=(0, 0, 0),
    )

    # 4. Place screenshot into screen area
    ui = screenshot.convert("RGBA")
    ui = ui.resize((screen_w, screen_h), Image.LANCZOS)

    # Apply inner rounded corners to screenshot
    screen_mask = _rounded_rect_mask((screen_w, screen_h), inner_r)
    ui.putalpha(screen_mask)

    device.paste(ui, (screen_x, screen_y), ui)

    # 5. Draw Dynamic Island or notch
    if spec.get("has_dynamic_island") and "dynamic_island" in spec:
        _draw_dynamic_island(draw, screen_x, screen_y, screen_w, spec["dynamic_island"])
    elif "notch" in spec:
        _draw_notch(draw, screen_x, screen_y, screen_w, spec["notch"])

    # 6. Draw side buttons (optional)
    if show_buttons and spec["type"] == "phone":
        _draw_phone_buttons(draw, device_w, device_h, bezel_t, shadow_color, highlight_color)
    elif show_buttons and spec["type"] == "tablet":
        _draw_tablet_buttons(draw, device_w, device_h, bezel_t, shadow_color, highlight_color)

    return device


def _draw_phone_buttons(draw, device_w, device_h, bezel_t, shadow_color, highlight_color):
    """Draw power button and volume buttons on phone frame."""
    btn_w = 6
    btn_r = 3

    # Power button — right side, upper third
    power_y = bezel_t + 300
    power_h = 200
    draw.rounded_rectangle(
        [device_w - 1, power_y, device_w + btn_w, power_y + power_h],
        radius=btn_r,
        fill=shadow_color,
    )

    # Volume up — left side
    vol_up_y = bezel_t + 280
    vol_h = 160
    draw.rounded_rectangle(
        [-btn_w, vol_up_y, 1, vol_up_y + vol_h],
        radius=btn_r,
        fill=shadow_color,
    )

    # Volume down — left side, below volume up
    vol_down_y = vol_up_y + vol_h + 40
    draw.rounded_rectangle(
        [-btn_w, vol_down_y, 1, vol_down_y + vol_h],
        radius=btn_r,
        fill=shadow_color,
    )

    # Action button — left side, above volume
    action_y = bezel_t + 160
    action_h = 80
    draw.rounded_rectangle(
        [-btn_w, action_y, 1, action_y + action_h],
        radius=btn_r,
        fill=shadow_color,
    )


def _draw_tablet_buttons(draw, device_w, device_h, bezel_t, shadow_color, highlight_color):
    """Draw power button on tablet frame."""
    btn_w = 5
    btn_r = 2

    # Power button — top edge, right side
    power_x = device_w - 300
    power_w = 120
    draw.rounded_rectangle(
        [power_x, -btn_w, power_x + power_w, 1],
        radius=btn_r,
        fill=shadow_color,
    )


def get_framed_size(device_key):
    """Get the total size of a device with frame."""
    spec = FRAME_SPECS.get(device_key)
    if not spec:
        return None
    screen_w, screen_h = spec["screen"]
    return (
        screen_w + spec["bezel_side"] * 2,
        screen_h + spec["bezel_top"] + spec["bezel_bottom"],
    )


def list_frame_colors():
    """Print available frame colors."""
    print("\nShotkit — Device Frame Colors")
    print("=" * 45)
    print("\n  iPhone:")
    for name in ["black-titanium", "natural-titanium", "white-titanium", "desert-titanium"]:
        c = FRAME_COLORS[name]["frame"]
        print(f"    {name:22s}  RGB({c[0]:3d}, {c[1]:3d}, {c[2]:3d})")
    print("\n  iPad:")
    for name in ["space-black", "silver"]:
        c = FRAME_COLORS[name]["frame"]
        print(f"    {name:22s}  RGB({c[0]:3d}, {c[1]:3d}, {c[2]:3d})")
    print("")
