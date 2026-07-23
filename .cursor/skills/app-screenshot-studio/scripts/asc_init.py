#!/usr/bin/env python3
"""
shotkit init — Connect to App Store Connect and configure your project.

Interactive setup that collects API credentials, verifies the connection,
lets you pick your app, and saves everything to .shotkit.json.
"""

import argparse
import getpass
import sys
from pathlib import Path

from asc_api import AppStoreConnectClient, save_config, load_config


def prompt_input(label, default=None, secret=False):
    """Prompt for user input with optional default."""
    suffix = f" [{default}]" if default else ""
    prompt_text = f"  {label}{suffix}: "
    if secret:
        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text)
    return value.strip() or default


def init(args):
    """Run the interactive init flow."""
    print("")
    print("Shotkit — App Store Connect Setup")
    print("=" * 45)
    print("")

    # Load existing config if present
    existing = load_config()
    if existing and not args.force:
        print("Found existing .shotkit.json")
        print(f"  App: {existing.get('app_name', 'unknown')}")
        print(f"  ID:  {existing.get('app_id', 'unknown')}")
        print("")
        answer = input("  Overwrite? (y/N): ").strip().lower()
        if answer != "y":
            print("  Keeping existing config.")
            return

    print("You need an App Store Connect API key.")
    print("Create one at: https://appstoreconnect.apple.com/access/integrations/api")
    print("")

    # Collect credentials
    key_id = args.key_id or prompt_input("Key ID")
    issuer_id = args.issuer_id or prompt_input("Issuer ID")
    private_key = args.private_key or prompt_input("Path to .p8 private key file")

    if not key_id or not issuer_id or not private_key:
        print("Error: All three fields are required.")
        sys.exit(1)

    # Expand and validate key path
    key_path = Path(private_key).expanduser().resolve()
    if not key_path.exists():
        print(f"Error: Private key not found: {key_path}")
        sys.exit(1)

    if not key_path.suffix == ".p8":
        print(f"Warning: Expected a .p8 file, got: {key_path.name}")

    print("")
    print("Connecting to App Store Connect...")

    # Test connection
    try:
        client = AppStoreConnectClient(key_id, issuer_id, str(key_path))
        apps = client.list_apps()
    except Exception as e:
        print(f"Error: Could not connect — {e}")
        print("")
        print("Check your credentials and try again.")
        sys.exit(1)

    if not apps:
        print("Connected, but no apps found in this account.")
        sys.exit(1)

    print(f"Connected. Found {len(apps)} app(s):")
    print("")

    # Display apps
    for i, app in enumerate(apps, 1):
        print(f"  {i}. {app['name']} ({app['bundle_id']})")

    print("")

    # Select app
    if len(apps) == 1:
        selected = apps[0]
        print(f"  Auto-selected: {selected['name']}")
    else:
        while True:
            choice = input(f"  Select app (1-{len(apps)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(apps):
                    selected = apps[idx]
                    break
            except ValueError:
                pass
            print("  Invalid choice. Try again.")

    # Save config
    config = {
        "key_id": key_id,
        "issuer_id": issuer_id,
        "private_key_path": str(key_path),
        "app_id": selected["id"],
        "app_name": selected["name"],
        "bundle_id": selected["bundle_id"],
    }

    save_config(config)

    print("")
    print(f"Setup complete for: {selected['name']}")
    print("")
    print("Next steps:")
    print("  shotkit apps          — list your apps")
    print("  shotkit download      — download existing screenshots")
    print("  shotkit screenshots   — generate new screenshots")
    print("  shotkit upload        — upload to App Store Connect")
    print("")
    print("Important: Add .shotkit.json to your .gitignore")
    print("  echo '.shotkit.json' >> .gitignore")
    print("")


def main():
    parser = argparse.ArgumentParser(description="Shotkit — App Store Connect Setup")
    parser.add_argument("--key-id", help="ASC API Key ID")
    parser.add_argument("--issuer-id", help="ASC Issuer ID")
    parser.add_argument("--private-key", help="Path to .p8 private key file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    args = parser.parse_args()
    init(args)


if __name__ == "__main__":
    main()
