#!/usr/bin/env python3
"""
shotkit — App Store Connect REST API Client

Handles JWT authentication and all ASC API operations:
app listing, screenshot sets, upload, download, delete.

Uses only stdlib (urllib) + PyJWT + cryptography for signing.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed. Run: shotkit install-deps")
    import sys; sys.exit(1)


BASE_URL = "https://api.appstoreconnect.apple.com"

# Maps shotkit device keys to ASC screenshotDisplayType values
DISPLAY_TYPE_MAP = {
    "iphone-6.9": "APP_IPHONE_69",
    "iphone-6.7": "APP_IPHONE_67",
    "iphone-6.5": "APP_IPHONE_65",
    "iphone-6.1": "APP_IPHONE_61",
    "ipad-13":    "APP_IPAD_PRO_3GEN_129",
    "ipad-12.9":  "APP_IPAD_PRO_129",
    "ipad-11":    "APP_IPAD_PRO_3GEN_11",
}

# Reverse map for download
DISPLAY_TYPE_REVERSE = {v: k for k, v in DISPLAY_TYPE_MAP.items()}


class AppStoreConnectClient:
    """Client for the App Store Connect API v1."""

    def __init__(self, key_id, issuer_id, private_key_path):
        self.key_id = key_id
        self.issuer_id = issuer_id
        self.private_key_path = Path(private_key_path)
        self._token = None
        self._token_exp = 0

        if not self.private_key_path.exists():
            raise FileNotFoundError(f"Private key not found: {self.private_key_path}")

        self._private_key = self.private_key_path.read_text()

    def _generate_token(self):
        """Generate a signed JWT for ASC API authentication."""
        now = int(time.time())
        exp = now + 20 * 60  # 20 minutes

        payload = {
            "iss": self.issuer_id,
            "iat": now,
            "exp": exp,
            "aud": "appstoreconnect-v1",
        }

        token = jwt.encode(
            payload,
            self._private_key,
            algorithm="ES256",
            headers={"kid": self.key_id},
        )

        self._token = token
        self._token_exp = exp
        return token

    def _get_token(self):
        """Get a valid token, refreshing if needed."""
        if self._token and time.time() < self._token_exp - 300:
            return self._token
        return self._generate_token()

    def _request(self, method, path, data=None, retries=3):
        """Make an authenticated API request with retry logic."""
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req) as resp:
                    if resp.status == 204:
                        return None
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries - 1:
                    wait = 2 ** (attempt + 1)
                    print(f"  Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                    continue
                error_body = e.read().decode() if e.fp else ""
                try:
                    error_json = json.loads(error_body)
                    errors = error_json.get("errors", [])
                    if errors:
                        msg = errors[0].get("detail", errors[0].get("title", str(e)))
                        raise RuntimeError(f"ASC API error ({e.code}): {msg}")
                except (json.JSONDecodeError, RuntimeError):
                    if isinstance(e, RuntimeError):
                        raise
                raise RuntimeError(f"ASC API error ({e.code}): {error_body or str(e)}")

    def _get(self, path):
        return self._request("GET", path)

    def _post(self, path, data):
        return self._request("POST", path, data)

    def _patch(self, path, data):
        return self._request("PATCH", path, data)

    def _delete(self, path):
        return self._request("DELETE", path)

    # ─── Apps ────────────────────────────────────────────────────────

    def list_apps(self):
        """List all apps. Returns list of app dicts."""
        resp = self._get("/v1/apps?limit=200")
        apps = []
        for item in resp.get("data", []):
            attrs = item.get("attributes", {})
            apps.append({
                "id": item["id"],
                "name": attrs.get("name", ""),
                "bundle_id": attrs.get("bundleId", ""),
                "sku": attrs.get("sku", ""),
                "platform": attrs.get("primaryLocale", ""),
            })
        return apps

    def get_app(self, app_id):
        """Get a single app by ID."""
        resp = self._get(f"/v1/apps/{app_id}")
        item = resp.get("data", {})
        attrs = item.get("attributes", {})
        return {
            "id": item["id"],
            "name": attrs.get("name", ""),
            "bundle_id": attrs.get("bundleId", ""),
            "sku": attrs.get("sku", ""),
            "primary_locale": attrs.get("primaryLocale", ""),
        }

    # ─── Versions & Localizations ────────────────────────────────────

    def get_edit_version(self, app_id):
        """Get the editable (not yet live) app store version."""
        resp = self._get(
            f"/v1/apps/{app_id}/appStoreVersions"
            "?filter[appStoreState]=PREPARE_FOR_SUBMISSION,DEVELOPER_ACTION_NEEDED,WAITING_FOR_REVIEW,IN_REVIEW,DEVELOPER_REJECTED"
            "&limit=1"
        )
        data = resp.get("data", [])
        if not data:
            # Try getting the latest version
            resp = self._get(f"/v1/apps/{app_id}/appStoreVersions?limit=1")
            data = resp.get("data", [])
        if not data:
            return None
        return data[0]

    def get_version_localizations(self, version_id):
        """Get all localizations for a version."""
        resp = self._get(
            f"/v1/appStoreVersions/{version_id}/appStoreVersionLocalizations"
        )
        return resp.get("data", [])

    def get_screenshot_sets(self, localization_id):
        """Get screenshot sets for a localization."""
        resp = self._get(
            f"/v1/appStoreVersionLocalizations/{localization_id}/appScreenshotSets"
            "?include=appScreenshots"
        )
        return resp.get("data", []), resp.get("included", [])

    # ─── Screenshot CRUD ─────────────────────────────────────────────

    def create_screenshot_set(self, localization_id, display_type):
        """Create a new screenshot set for a display type."""
        data = {
            "data": {
                "type": "appScreenshotSets",
                "attributes": {
                    "screenshotDisplayType": display_type,
                },
                "relationships": {
                    "appStoreVersionLocalization": {
                        "data": {
                            "type": "appStoreVersionLocalizations",
                            "id": localization_id,
                        }
                    }
                },
            }
        }
        resp = self._post("/v1/appScreenshotSets", data)
        return resp["data"]["id"]

    def reserve_screenshot(self, set_id, filename, file_size):
        """Reserve a screenshot upload slot. Returns screenshot ID and upload operations."""
        data = {
            "data": {
                "type": "appScreenshots",
                "attributes": {
                    "fileName": filename,
                    "fileSize": file_size,
                },
                "relationships": {
                    "appScreenshotSet": {
                        "data": {
                            "type": "appScreenshotSets",
                            "id": set_id,
                        }
                    }
                },
            }
        }
        resp = self._post("/v1/appScreenshots", data)
        screenshot_id = resp["data"]["id"]
        upload_ops = resp["data"]["attributes"].get("uploadOperations", [])
        return screenshot_id, upload_ops

    def upload_screenshot_part(self, upload_op, file_data):
        """Upload a single part of a screenshot to Apple's CDN."""
        url = upload_op["url"]
        headers = {h["name"]: h["value"] for h in upload_op.get("requestHeaders", [])}
        offset = upload_op.get("offset", 0)
        length = upload_op.get("length", len(file_data))
        chunk = file_data[offset:offset + length]

        req = urllib.request.Request(url, data=chunk, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as resp:
            return resp.status

    def commit_screenshot(self, screenshot_id, checksum=None):
        """Mark a screenshot upload as complete."""
        attrs = {"uploaded": True, "sourceFileChecksum": checksum} if checksum else {"uploaded": True}
        data = {
            "data": {
                "type": "appScreenshots",
                "id": screenshot_id,
                "attributes": attrs,
            }
        }
        return self._patch(f"/v1/appScreenshots/{screenshot_id}", data)

    def delete_screenshot(self, screenshot_id):
        """Delete a single screenshot."""
        return self._delete(f"/v1/appScreenshots/{screenshot_id}")

    def delete_screenshot_set(self, set_id):
        """Delete an entire screenshot set."""
        return self._delete(f"/v1/appScreenshotSets/{set_id}")

    # ─── Download ────────────────────────────────────────────────────

    def download_image(self, url, output_path):
        """Download an image from a URL to a local file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            output.write_bytes(resp.read())


def load_config(config_path=None):
    """Load .shotkit.json config file. Returns dict or None."""
    if config_path:
        p = Path(config_path)
    else:
        p = Path.cwd() / ".shotkit.json"

    if not p.exists():
        return None

    with open(p) as f:
        return json.load(f)


def save_config(config, config_path=None):
    """Save config to .shotkit.json."""
    if config_path:
        p = Path(config_path)
    else:
        p = Path.cwd() / ".shotkit.json"

    with open(p, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Config saved: {p}")
