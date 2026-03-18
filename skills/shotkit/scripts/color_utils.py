#!/usr/bin/env python3
"""
shotkit — Color Utilities

Extract dominant colors from app icons, generate brand-aware gradients,
and check contrast ratios for text readability.
"""

import colorsys
import math
from collections import Counter

from PIL import Image


def extract_dominant_colors(image_path, num_colors=5, sample_size=1000):
    """
    Extract dominant colors from an image using pixel sampling and clustering.
    Returns a list of (r, g, b) tuples sorted by frequency.
    """
    img = Image.open(image_path).convert("RGB")

    # Resize for faster sampling
    img.thumbnail((150, 150), Image.LANCZOS)
    pixels = list(img.getdata())

    # Quantize colors to reduce noise (group similar colors)
    quantized = []
    for r, g, b in pixels:
        qr = (r // 24) * 24
        qg = (g // 24) * 24
        qb = (b // 24) * 24
        quantized.append((qr, qg, qb))

    # Count and sort by frequency
    counts = Counter(quantized)

    # Filter out near-white, near-black, and very desaturated colors
    filtered = {}
    for color, count in counts.items():
        r, g, b = color
        brightness = (r + g + b) / 3
        if brightness < 20 or brightness > 240:
            continue
        # Check saturation
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.1:
            continue
        filtered[color] = count

    if not filtered:
        # Fall back to unfiltered if everything was filtered
        filtered = dict(counts.most_common(num_colors * 2))

    # Get top colors
    sorted_colors = sorted(filtered.items(), key=lambda x: -x[1])

    # Merge similar colors
    result = []
    for color, count in sorted_colors:
        is_duplicate = False
        for existing in result:
            if _color_distance(color, existing) < 50:
                is_duplicate = True
                break
        if not is_duplicate:
            result.append(color)
        if len(result) >= num_colors:
            break

    return result


def _color_distance(c1, c2):
    """Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def generate_gradient_from_colors(colors):
    """
    Generate a gradient pair from extracted colors.
    Picks two colors with good contrast that work as a gradient.
    """
    if len(colors) < 2:
        # Default gradient if not enough colors
        return colors[0] if colors else (30, 30, 120), (128, 0, 128)

    # Find the pair with the best visual separation
    best_pair = None
    best_distance = 0

    for i, c1 in enumerate(colors):
        for c2 in colors[i + 1:]:
            dist = _color_distance(c1, c2)
            if dist > best_distance:
                best_distance = dist
                best_pair = (c1, c2)

    if not best_pair:
        return colors[0], colors[1]

    # Ensure darker color is on top
    b1 = sum(best_pair[0]) / 3
    b2 = sum(best_pair[1]) / 3
    if b1 > b2:
        return best_pair[1], best_pair[0]
    return best_pair


def darken_color(color, factor=0.6):
    """Darken a color by a factor."""
    return tuple(int(c * factor) for c in color)


def lighten_color(color, factor=1.4):
    """Lighten a color by a factor, capped at 255."""
    return tuple(min(255, int(c * factor)) for c in color)


def contrast_ratio(fg, bg):
    """
    Calculate WCAG contrast ratio between two colors.
    Returns a value between 1 and 21.
    """
    def relative_luminance(rgb):
        srgb = [c / 255.0 for c in rgb]
        linear = []
        for c in srgb:
            if c <= 0.03928:
                linear.append(c / 12.92)
            else:
                linear.append(((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def ensure_text_contrast(text_color, bg_color, min_ratio=4.5):
    """
    Adjust text color to ensure sufficient contrast against background.
    Returns adjusted text color.
    """
    ratio = contrast_ratio(text_color, bg_color)
    if ratio >= min_ratio:
        return text_color

    # Try white
    if contrast_ratio((255, 255, 255), bg_color) >= min_ratio:
        return (255, 255, 255)

    # Try near-white
    if contrast_ratio((240, 240, 245), bg_color) >= min_ratio:
        return (240, 240, 245)

    # Try black
    if contrast_ratio((0, 0, 0), bg_color) >= min_ratio:
        return (20, 20, 20)

    # Return white as safest default
    return (255, 255, 255)
