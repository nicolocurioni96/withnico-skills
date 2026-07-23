#!/usr/bin/env python3
"""
shotkit upload / update — Upload screenshots to App Store Connect.

Reads the ASC-ready folder structure ({locale}/{device}/*.png) and
uploads each screenshot via the App Store Connect API.

Upload flow per Apple's API:
  1. Reserve upload slot (POST /v1/appScreenshots)
  2. Upload binary to Apple CDN (PUT to uploadOperations URLs)
  3. Commit upload (PATCH /v1/appScreenshots/{id})
"""

import argparse
import hashlib
import sys
from pathlib import Path

from asc_api import (
    AppStoreConnectClient,
    DISPLAY_TYPE_MAP,
    load_config,
)


def _md5_checksum(file_path):
    """Compute MD5 checksum of a file."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_or_create_set(client, localization_id, display_type, existing_sets):
    """Find an existing screenshot set or create a new one."""
    for ss_set in existing_sets:
        if ss_set["attributes"]["screenshotDisplayType"] == display_type:
            return ss_set["id"]

    # Create new set
    return client.create_screenshot_set(localization_id, display_type)


def _delete_existing_screenshots(client, set_id):
    """Delete all screenshots in a set."""
    try:
        resp = client._get(f"/v1/appScreenshotSets/{set_id}/appScreenshots")
        screenshots = resp.get("data", [])
        for ss in screenshots:
            print(f"    Deleting: {ss['attributes'].get('fileName', ss['id'])}")
            client.delete_screenshot(ss["id"])
        return len(screenshots)
    except Exception as e:
        print(f"    Warning: Could not clean set — {e}")
        return 0


def upload_screenshot(client, set_id, file_path):
    """Upload a single screenshot file through the 3-step ASC flow."""
    path = Path(file_path)
    file_size = path.stat().st_size
    file_data = path.read_bytes()
    filename = path.name

    # Step 1: Reserve
    screenshot_id, upload_ops = client.reserve_screenshot(set_id, filename, file_size)

    # Step 2: Upload parts to CDN
    for op in upload_ops:
        client.upload_screenshot_part(op, file_data)

    # Step 3: Commit
    checksum = _md5_checksum(file_path)
    client.commit_screenshot(screenshot_id, checksum)

    return screenshot_id


def run_upload(args, replace=False):
    """Main upload/update logic."""
    config = load_config(args.config)
    if not config:
        print("Error: No .shotkit.json found. Run: shotkit init")
        sys.exit(1)

    app_id = args.app_id or config.get("app_id")
    if not app_id:
        print("Error: No app ID. Run: shotkit init")
        sys.exit(1)

    screenshots_dir = Path(args.dir)
    if not screenshots_dir.exists():
        print(f"Error: Directory not found: {screenshots_dir}")
        sys.exit(1)

    action = "Update" if replace else "Upload"
    print("")
    print(f"Shotkit — {action} Screenshots")
    print(f"App    : {config.get('app_name', app_id)}")
    print(f"Source : {screenshots_dir}")
    if replace:
        print("Mode   : Replace (existing screenshots will be deleted)")
    print("")

    # Validate first
    print("Validating screenshots...")
    from validate_output import validate
    validate(str(screenshots_dir))

    confirm = input(f"\nProceed with {action.lower()}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    client = AppStoreConnectClient(
        config["key_id"],
        config["issuer_id"],
        config["private_key_path"],
    )

    # Get editable version
    version = client.get_edit_version(app_id)
    if not version:
        print("Error: No editable app version found.")
        print("Create a new version in App Store Connect first.")
        sys.exit(1)

    version_id = version["id"]

    # Get existing localizations
    localizations = client.get_version_localizations(version_id)
    loc_map = {loc["attributes"]["locale"]: loc["id"] for loc in localizations}

    total_uploaded = 0
    total_errors = 0

    # Walk the output directory: {locale}/{device}/*.png
    for locale_dir in sorted(screenshots_dir.iterdir()):
        if not locale_dir.is_dir() or locale_dir.name.startswith("_"):
            continue

        locale = locale_dir.name
        loc_id = loc_map.get(locale)
        if not loc_id:
            print(f"  Warning: Locale '{locale}' not found in ASC version. Skipping.")
            continue

        for device_dir in sorted(locale_dir.iterdir()):
            if not device_dir.is_dir():
                continue

            device_key = device_dir.name
            display_type = DISPLAY_TYPE_MAP.get(device_key)
            if not display_type:
                print(f"  Warning: Unknown device '{device_key}'. Skipping.")
                continue

            files = sorted(
                f for f in device_dir.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            )
            if not files:
                continue

            print(f"  [{locale}/{device_key}] {len(files)} file(s)")

            # Get existing screenshot sets for this localization
            existing_sets, _ = client.get_screenshot_sets(loc_id)

            # Find or create the set
            set_id = _find_or_create_set(client, loc_id, display_type, existing_sets)

            # Delete existing screenshots if replacing
            if replace:
                deleted = _delete_existing_screenshots(client, set_id)
                if deleted:
                    print(f"    Deleted {deleted} existing screenshot(s)")

            # Upload each file
            for f in files:
                try:
                    print(f"    Uploading: {f.name}")
                    upload_screenshot(client, set_id, str(f))
                    total_uploaded += 1
                except Exception as e:
                    print(f"    Error uploading {f.name}: {e}")
                    total_errors += 1

    print("")
    print(f"Done. Uploaded: {total_uploaded}, Errors: {total_errors}")
    if total_errors == 0:
        print("All screenshots uploaded successfully.")
    else:
        print("Some uploads failed. Check errors above and retry.")


def main_upload():
    parser = argparse.ArgumentParser(description="Shotkit — Upload Screenshots to ASC")
    parser.add_argument("--dir", default="./screenshots-output", help="Screenshots directory")
    parser.add_argument("--app-id", help="App Store app ID (default: from .shotkit.json)")
    parser.add_argument("--config", help="Path to .shotkit.json")
    args = parser.parse_args()
    run_upload(args, replace=False)


def main_update():
    parser = argparse.ArgumentParser(description="Shotkit — Update Screenshots on ASC")
    parser.add_argument("--dir", default="./screenshots-output", help="Screenshots directory")
    parser.add_argument("--app-id", help="App Store app ID (default: from .shotkit.json)")
    parser.add_argument("--config", help="Path to .shotkit.json")
    parser.add_argument("--replace", action="store_true", default=True,
                        help="Replace existing screenshots (default: true)")
    args = parser.parse_args()
    run_upload(args, replace=True)


if __name__ == "__main__":
    main_upload()
