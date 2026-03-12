#!/bin/bash
set -e
echo "📦 Installing shotkit dependencies..."
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Install via: brew install python3"
  exit 1
fi
echo "✅ Python $(python3 --version) found"
pip3 install Pillow --quiet --break-system-packages 2>/dev/null \
  || pip3 install Pillow --quiet 2>/dev/null \
  || { echo "❌ Pillow install failed. Try: pip3 install Pillow"; exit 1; }
echo "✅ Pillow installed"
if command -v xcrun &>/dev/null; then
  echo "✅ xcrun found (Xcode present)"
else
  echo "⚠️  xcrun not found. Install Xcode to enable Simulator capture."
fi
echo ""
echo "✅ Dependencies ready."
