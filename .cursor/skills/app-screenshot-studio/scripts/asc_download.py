#!/usr/bin/env python3
"""
shotkit download — Download existing screenshots from App Store Connect.

Fetches all screenshot assets for the current editable version and saves
them in the standard Shotkit folder structure: {output}/{locale}/{device}/
"""

import argparse
import sys
from pathlib import Path

from asc_api import (
    AppStoreConnectClient,
    DISPLAY_TYPE_REVERSE,
    load_config,
)


def download(args):
    """Download existing screenshots from ASC."""
    config = load_config(args.config)
    if not config:
        print("Error: No .shotkit.json found. Run: shotkit init")
        sys.exit(1)

    app_id = args.app_id or config.get("app_id")
    if not app_id:
        print("Error: No app ID. Run: shotkit init")
        sys.exit(1)

    output_dir = Path(args.output)
    print("")
    print("Shotkit — Download Screenshots")
    print(f"App    : {config.get('app_name', app_id)}")
    print(f"Output : {output_dir}")
    print("")

    client = AppStoreConnectClient(
        config["key_id"],
        config["issuer_id"],
        config["private_key_path"],
    )

    # Get editable version
    version = client.get_edit_version(app_id)
    if not version:
        print("Error: No editable app version found.")
        sys.exit(1)

    version_id = version["id"]
    version_str = version.get("attributes", {}).get("versionString", "unknown")
    print(f"Version: {version_str}")

    # Get localizations
    localizations = client.get_version_localizations(version_id)
    if not localizations:
        print("No localizations found.")
        return

    total = 0
    for loc in localizations:
        locale = loc["attributes"]["locale"]
        loc_id = loc["id"]

        # Get screenshot sets
        sets, included = client.get_screenshot_sets(loc_id)
        if not sets:
            continue

        for ss_set in sets:
            display_type = ss_set["attributes"]["screenshotDisplayType"]
            device_key = DISPLAY_TYPE_REVERSE.get(display_type, display_type.lower())
            set_id = ss_set["id"]

            # Find screenshots in this set from included data
            screenshots = [
                item for item in included
                if item["type"] == "appScreenshots"
                and item.get("relationships", {})
                    .get("appScreenshotSet", {})
                    .get("data", {})
                    .get("id") == set_id
            ]

            if not screenshots:
                # Try fetching directly
                try:
                    resp = client._get(f"/v1/appScreenshotSets/{set_id}/appScreenshots")
                    screenshots = resp.get("data", [])
                except Exception:
                    continue

            for idx, ss in enumerate(screenshots):
                attrs = ss.get("attributes", {})
                image_url = attrs.get("imageAsset", {}).get("templateUrl", "")
                if not image_url:
                    continue

                # Build download URL (replace template placeholders)
                width = attrs.get("imageAsset", {}).get("width", 0)
                height = attrs.get("imageAsset", {}).get("height", 0)
                image_url = image_url.replace("{w}", str(width))
                image_url = image_url.replace("{h}", str(height))
                image_url = image_url.replace("{f}", "png")

                filename = attrs.get("fileName", f"{idx + 1:02d}_screenshot.png")
                out_path = output_dir / locale / device_key / filename
                out_path.parent.mkdir(parents=True, exist_ok=True)

                print(f"  [{locale}/{device_key}] {filename}")
                try:
                    client.download_image(image_url, str(out_path))
                    total += 1
                except Exception as e:
                    print(f"    Error: {e}")

    print(f"\nDownloaded {total} screenshot(s) to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Shotkit — Download Screenshots from ASC")
    parser.add_argument("--app-id", help="App Store app ID (default: from .shotkit.json)")
    parser.add_argument("--output", default="./existing-screenshots", help="Output directory")
    parser.add_argument("--config", help="Path to .shotkit.json")
    args = parser.parse_args()
    download(args)


if __name__ == "__main__":
    main()
