#!/usr/bin/env python3
"""
shotkit — Output Validator
Checks all generated screenshots against App Store Connect requirements.

Usage:
  python3 validate_output.py --dir ./screenshots-output
"""

import argparse
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow not installed. Run: bash scripts/install_deps.sh")
    import sys; sys.exit(1)

REQUIRED_SIZES = {
    "iphone-6.9":  (1320, 2868),
    "iphone-6.7":  (1290, 2796),
    "iphone-6.5":  (1242, 2688),
    "iphone-6.1":  (1179, 2556),
    "ipad-13":     (2064, 2752),
    "ipad-12.9":   (2048, 2732),
    "ipad-11":     (1668, 2388),
}

def validate(output_dir):
    base = Path(output_dir)
    if not base.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return
    errors = []
    warnings = []
    passed = 0
    total = 0
    for locale_dir in sorted(base.iterdir()):
        if locale_dir.name.startswith("_") or not locale_dir.is_dir():
            continue
        for device_dir in sorted(locale_dir.iterdir()):
            if not device_dir.is_dir():
                continue
            device_key = device_dir.name
            expected_size = REQUIRED_SIZES.get(device_key)
            files = sorted([f for f in device_dir.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg"}])
            total += len(files)
            if not files:
                warnings.append(f"[{locale_dir.name}/{device_key}] No screenshots found")
                continue
            if len(files) > 10:
                warnings.append(f"[{locale_dir.name}/{device_key}] {len(files)} files (App Store max is 10)")
            for f in files:
                try:
                    with Image.open(f) as img:
                        w, h = img.size
                except Exception as e:
                    errors.append(f"[{f.name}] Cannot open: {e}")
                    continue
                if expected_size and (w, h) != expected_size and (h, w) != expected_size:
                    errors.append(f"[{locale_dir.name}/{device_key}/{f.name}] Wrong size: {w}×{h}px (expected {expected_size[0]}×{expected_size[1]}px)")
                else:
                    passed += 1
    print(f"\n{'─'*50}")
    print(f"Shotkit — Validation Report")
    print(f"{'─'*50}")
    print(f"Total checked : {total}")
    print(f"Passed        : {passed}")
    print(f"Errors        : {len(errors)}")
    print(f"Warnings      : {len(warnings)}")
    print(f"{'─'*50}")
    if errors:
        print(f"\n❌ ERRORS:")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"   • {w}")
    if not errors:
        print(f"\n✅ No critical errors. Ready to upload.")
    else:
        print(f"\n❌ Fix errors before uploading.")
    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="./screenshots-output")
    args = parser.parse_args()
    validate(args.dir)

if __name__ == "__main__":
    main()
