#!/bin/bash
# shotkit — Dependency installer
#
# By default this creates an isolated virtualenv at ~/.shotkit/venv and
# installs Pillow, PyJWT, and cryptography there. The shotkit CLI auto-
# detects that venv and uses it, so the user's system Python stays clean.
#
# Set SHOTKIT_LEGACY_INSTALL=1 to fall back to the pre-2.1 behaviour of
# installing into the system Python (with --break-system-packages).

set -e

SHOTKIT_HOME="${SHOTKIT_HOME:-$HOME/.shotkit}"
VENV_DIR="$SHOTKIT_HOME/venv"
PACKAGES=(Pillow PyJWT cryptography)

echo "Installing shotkit dependencies..."

if ! command -v python3 &>/dev/null; then
  echo "Error: Python 3 not found. Install via: brew install python3"
  exit 1
fi
echo "Python $(python3 --version) found"

if [ "${SHOTKIT_LEGACY_INSTALL:-0}" = "1" ]; then
  echo "SHOTKIT_LEGACY_INSTALL=1 — installing into system Python (legacy path)"
  pip3 install "${PACKAGES[@]}" --quiet --break-system-packages 2>/dev/null \
    || pip3 install "${PACKAGES[@]}" --quiet 2>/dev/null \
    || { echo "Error: pip install failed. Try: pip3 install ${PACKAGES[*]}"; exit 1; }
else
  mkdir -p "$SHOTKIT_HOME"
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv at $VENV_DIR"
    python3 -m venv "$VENV_DIR" \
      || { echo "Error: could not create venv. On Debian/Ubuntu install python3-venv."; exit 1; }
  else
    echo "Reusing existing virtualenv at $VENV_DIR"
  fi
  "$VENV_DIR/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
  "$VENV_DIR/bin/pip" install --quiet "${PACKAGES[@]}" \
    || { echo "Error: pip install failed inside venv at $VENV_DIR."; exit 1; }
fi

echo "Pillow, PyJWT, cryptography installed"

if command -v xcrun &>/dev/null; then
  echo "xcrun found (Xcode present)"
else
  echo "Warning: xcrun not found. Install Xcode to enable Simulator capture."
fi

echo ""
echo "Dependencies ready."
if [ "${SHOTKIT_LEGACY_INSTALL:-0}" != "1" ]; then
  echo "Shotkit will auto-detect the venv at $VENV_DIR."
fi
