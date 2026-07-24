#!/usr/bin/env python3
"""
shotkit — Output Validator

Checks generated screenshots against App Store Connect requirements:

  * Recognised device folder keys (see references/device_specs.md)
  * Portrait or landscape dimensions match the spec
  * File is readable
  * File's magic bytes match the extension (.png vs .jpg/.jpeg)
  * No alpha channel (ASC rejects transparent PNGs)
  * No empty per-device folders
  * At most 10 files per device per locale (App Store limit)

Emits warnings for the alpha and magic-byte checks in v2.1.x; these are
scheduled to become errors in v2.2.0.

Usage:
  python3 validate_output.py --dir ./screenshots-output
  python3 validate_output.py --dir ./screenshots-output --json
  python3 validate_output.py --dir ./screenshots-output --report ./run.json
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: bash scripts/install_deps.sh")
    sys.exit(1)

# Apple's currently-accepted screenshot dimensions. Bump SPEC_VERSION
# whenever you refresh this table against Apple's specification page.
SPEC_VERSION = "2025-mandatory-iphone-6.9-ipad-13"

REQUIRED_SIZES = {
    "iphone-6.9":  (1320, 2868),
    "iphone-6.7":  (1290, 2796),
    "iphone-6.5":  (1242, 2688),
    "iphone-6.1":  (1179, 2556),
    "ipad-13":     (2064, 2752),
    "ipad-12.9":   (2048, 2732),
    "ipad-11":     (1668, 2388),
}

# Magic bytes → file kind. Used to catch mislabeled files (e.g. a JPEG saved as .png).
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def _detect_kind(path):
    """Return 'png', 'jpeg', or None based on the first few bytes."""
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError:
        return None
    if head.startswith(PNG_MAGIC):
        return "png"
    if head.startswith(JPEG_MAGIC):
        return "jpeg"
    return None


def _has_alpha(img):
    """True if the image mode carries a transparency channel."""
    if img.mode in ("RGBA", "LA"):
        return True
    if img.mode == "P" and "transparency" in img.info:
        return True
    return False


def validate(output_dir):
    """Walk the output directory and return a structured result."""
    base = Path(output_dir)
    result = {
        "spec_version": SPEC_VERSION,
        "output_dir": str(base),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_files": 0,
        "passed": 0,
        "errors": [],
        "warnings": [],
        "files": [],
    }

    if not base.exists():
        result["errors"].append({"kind": "missing-output-dir", "path": str(base)})
        return result

    for locale_dir in sorted(base.iterdir()):
        if locale_dir.name.startswith("_") or not locale_dir.is_dir():
            continue
        for device_dir in sorted(locale_dir.iterdir()):
            if not device_dir.is_dir():
                continue
            device_key = device_dir.name
            expected_size = REQUIRED_SIZES.get(device_key)

            if expected_size is None:
                result["warnings"].append({
                    "kind": "unknown-device-folder",
                    "path": f"{locale_dir.name}/{device_key}",
                    "hint": "not in Apple's currently-accepted device set — see references/device_specs.md",
                })

            files = sorted(
                f for f in device_dir.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            )
            result["total_files"] += len(files)

            if not files:
                result["warnings"].append({
                    "kind": "empty-folder",
                    "path": f"{locale_dir.name}/{device_key}",
                })
                continue

            if len(files) > 10:
                result["warnings"].append({
                    "kind": "over-limit",
                    "path": f"{locale_dir.name}/{device_key}",
                    "count": len(files),
                    "limit": 10,
                })

            for f in files:
                entry = {
                    "path": str(f.relative_to(base)),
                    "issues": [],
                }

                # Magic-byte check
                expected_kind = "png" if f.suffix.lower() == ".png" else "jpeg"
                detected = _detect_kind(f)
                if detected is None:
                    result["errors"].append({
                        "kind": "unreadable",
                        "path": entry["path"],
                    })
                    entry["issues"].append("unreadable")
                    result["files"].append(entry)
                    continue
                if detected != expected_kind:
                    # Warning in v2.1.x; will become an error in v2.2.0.
                    result["warnings"].append({
                        "kind": "magic-byte-mismatch",
                        "path": entry["path"],
                        "declared": expected_kind,
                        "actual": detected,
                    })
                    entry["issues"].append(f"declared {expected_kind}, is {detected}")

                # Open and inspect the image
                try:
                    with Image.open(f) as img:
                        w, h = img.size
                        mode = img.mode
                        alpha = _has_alpha(img)
                except Exception as exc:
                    result["errors"].append({
                        "kind": "unreadable",
                        "path": entry["path"],
                        "reason": str(exc),
                    })
                    entry["issues"].append("cannot open")
                    result["files"].append(entry)
                    continue

                entry["size"] = [w, h]
                entry["mode"] = mode

                if expected_size and (w, h) != expected_size and (h, w) != expected_size:
                    result["errors"].append({
                        "kind": "wrong-size",
                        "path": entry["path"],
                        "actual": [w, h],
                        "expected": list(expected_size),
                    })
                    entry["issues"].append(f"size {w}x{h} != expected {expected_size[0]}x{expected_size[1]}")

                if alpha:
                    # Warning in v2.1.x; ASC will reject on upload but the file itself is not corrupt.
                    result["warnings"].append({
                        "kind": "alpha-channel",
                        "path": entry["path"],
                        "mode": mode,
                        "hint": "App Store Connect rejects PNGs with transparency; flatten before upload",
                    })
                    entry["issues"].append(f"alpha channel ({mode})")

                if not entry["issues"]:
                    result["passed"] += 1

                result["files"].append(entry)

    return result


def _print_text_report(result):
    """Render the human-readable summary."""
    print(f"\n{'─'*55}")
    print("Shotkit — Validation Report")
    print(f"{'─'*55}")
    print(f"Output dir    : {result['output_dir']}")
    print(f"Spec version  : {result['spec_version']}")
    print(f"Total checked : {result['total_files']}")
    print(f"Passed        : {result['passed']}")
    print(f"Errors        : {len(result['errors'])}")
    print(f"Warnings      : {len(result['warnings'])}")
    print(f"{'─'*55}")

    if result["errors"]:
        print("\nERRORS:")
        for e in result["errors"]:
            path = e.get("path", "")
            extra = " ".join(f"{k}={v}" for k, v in e.items() if k not in ("kind", "path"))
            print(f"   • [{e['kind']}] {path} {extra}".rstrip())

    if result["warnings"]:
        print("\nWARNINGS:")
        for w in result["warnings"]:
            path = w.get("path", "")
            extra_bits = [f"{k}={v}" for k, v in w.items() if k not in ("kind", "path", "hint")]
            hint = w.get("hint", "")
            print(f"   • [{w['kind']}] {path} {' '.join(extra_bits)}".rstrip())
            if hint:
                print(f"       hint: {hint}")

    print()
    if not result["errors"]:
        print("No critical errors. Ready to upload.")
    else:
        print("Fix errors before uploading.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Shotkit — validate App Store screenshot output")
    parser.add_argument("--dir", default="./screenshots-output", help="Output directory to check")
    parser.add_argument("--json", action="store_true",
                        help="Print the report as JSON to stdout instead of the human-readable summary")
    parser.add_argument("--report", metavar="FILE", default=None,
                        help="Also write the JSON report to FILE")
    args = parser.parse_args()

    result = validate(args.dir)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, indent=2) + "\n")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_text_report(result)

    sys.exit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
