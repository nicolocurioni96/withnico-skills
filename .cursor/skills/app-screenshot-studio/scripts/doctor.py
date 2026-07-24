#!/usr/bin/env python3
"""
shotkit — Doctor

Preflight environment check. Verifies that everything shotkit needs is
installed and reachable: Python packages, Xcode command line tools,
booted Simulators, and (if present) the App Store Connect config.

Exits 0 when the environment is ready for the full pipeline. Exits 1 if
a required check fails. Optional checks (booted simulator, .shotkit.json)
never cause a non-zero exit.

Usage:
  python3 doctor.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED = "required"
OPTIONAL = "optional"


class Doctor:
    def __init__(self):
        self.results = []
        self.required_failures = 0

    def check(self, label, ok, kind=REQUIRED, hint="", detail=""):
        status = "OK" if ok else ("MISSING" if kind == REQUIRED else "not present")
        symbol = "✓" if ok else ("✗" if kind == REQUIRED else "•")
        detail_str = f" — {detail}" if detail else ""
        print(f"  {symbol} {label:38s} {status}{detail_str}")
        if not ok and hint:
            print(f"      → {hint}")
        self.results.append({"label": label, "ok": ok, "kind": kind, "detail": detail})
        if not ok and kind == REQUIRED:
            self.required_failures += 1


def _python_version():
    return ".".join(str(v) for v in sys.version_info[:3])


def _try_import(name):
    try:
        mod = __import__(name)
        return True, getattr(mod, "__version__", "?")
    except ImportError:
        return False, None


def _booted_simulators():
    """Return the number of currently booted Simulator devices, or None if xcrun is missing."""
    if not shutil.which("xcrun"):
        return None
    try:
        out = subprocess.check_output(
            ["xcrun", "simctl", "list", "devices", "booted", "--json"],
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        data = json.loads(out)
        return sum(
            1
            for runtime_devices in data.get("devices", {}).values()
            for d in runtime_devices
            if d.get("state") == "Booted"
        )
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return None


def _shotkit_config_report(doc):
    """Inspect .shotkit.json if it exists."""
    cfg = Path(".shotkit.json")
    if not cfg.exists():
        doc.check(".shotkit.json (ASC config)", True, kind=OPTIONAL,
                  detail="not present — run 'shotkit init' to enable App Store Connect commands")
        return
    try:
        data = json.loads(cfg.read_text())
    except json.JSONDecodeError as e:
        doc.check(".shotkit.json (ASC config)", False, kind=REQUIRED,
                  hint="fix the JSON syntax", detail=f"invalid JSON: {e}")
        return

    required_keys = {"app_id", "key_id", "issuer_id", "private_key_path"}
    missing = sorted(required_keys - set(data))
    if missing:
        doc.check(".shotkit.json (ASC config)", False, kind=REQUIRED,
                  hint="re-run 'shotkit init'",
                  detail=f"missing fields: {', '.join(missing)}")
        return

    doc.check(".shotkit.json (ASC config)", True, kind=OPTIONAL,
              detail=f"app '{data.get('app_name', data['app_id'])}'")
    pk = Path(str(data["private_key_path"])).expanduser()
    doc.check(f"  .p8 private key at {pk}", pk.exists(),
              kind=REQUIRED,
              hint="update private_key_path in .shotkit.json" if not pk.exists() else "")


def main():
    doc = Doctor()

    print("\nShotkit — Doctor")
    print("=" * 55)

    # Python
    doc.check(f"python3 ({_python_version()})", True)

    # Required Python packages
    for pkg in ("PIL", "jwt", "cryptography"):
        ok, ver = _try_import(pkg)
        display = {"PIL": "Pillow", "jwt": "PyJWT", "cryptography": "cryptography"}[pkg]
        doc.check(f"{display} package", ok,
                  hint="run: shotkit install-deps" if not ok else "",
                  detail=f"v{ver}" if ok else "")

    # Isolated venv (optional but recommended)
    venv = Path.home() / ".shotkit" / "venv" / "bin" / "python3"
    doc.check("~/.shotkit/venv (isolated deps)", venv.exists(), kind=OPTIONAL,
              detail="run 'shotkit install-deps' to create one" if not venv.exists() else "")

    # Xcode / xcrun
    xcrun = shutil.which("xcrun")
    doc.check("xcrun (Xcode command line tools)", bool(xcrun),
              hint="install Xcode from the App Store" if not xcrun else "")

    # Booted simulators
    booted = _booted_simulators()
    if booted is None:
        doc.check("booted Simulator", False, kind=OPTIONAL,
                  detail="skipped (xcrun not available)")
    else:
        doc.check("booted Simulator", booted > 0, kind=OPTIONAL,
                  detail=f"{booted} device(s) booted" if booted else "none booted — open Simulator or 'xcrun simctl boot <name>'")

    # ASC config
    _shotkit_config_report(doc)

    print()
    if doc.required_failures == 0:
        print("All required checks passed.")
        sys.exit(0)
    print(f"{doc.required_failures} required check(s) failed. See hints above.")
    sys.exit(1)


if __name__ == "__main__":
    main()
