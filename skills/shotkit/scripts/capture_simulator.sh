#!/bin/bash
BUNDLE_ID="${1:-}"
OUTPUT_DIR="${2:-./raw-captures}"
COUNTER=1

if ! command -v xcrun &>/dev/null; then
  echo "❌ xcrun not found. Install Xcode from the Mac App Store."
  exit 1
fi

BOOTED=$(xcrun simctl list devices | grep "Booted" | head -1)
if [ -z "$BOOTED" ]; then
  echo "❌ No booted Simulator found."
  echo "   Open Simulator.app and boot a device, then re-run."
  exit 1
fi

DEVICE_NAME=$(xcrun simctl list devices | grep "Booted" | head -1 | sed 's/ (.*)//')
echo "✅ Booted Simulator: $DEVICE_NAME"

mkdir -p "$OUTPUT_DIR"

if [ -n "$BUNDLE_ID" ]; then
  echo "🚀 Launching $BUNDLE_ID..."
  xcrun simctl launch booted "$BUNDLE_ID" &>/dev/null || echo "⚠️  Could not auto-launch. Launch manually."
  sleep 3
fi

echo ""
echo "📸 Screenshot Capture Mode"
echo "Navigate to each screen. Press ENTER to capture. Type 'done' to finish."
echo ""

while true; do
  read -r -p "Screen $COUNTER — Press ENTER to capture (or type 'done'): " INPUT
  if [[ "$INPUT" == "done" || "$INPUT" == "q" ]]; then break; fi
  read -r -p "  Name this screen (e.g. 'home', 'detail'): " SCREEN_NAME
  SCREEN_NAME="${SCREEN_NAME:-screen}"
  SCREEN_NAME=$(echo "$SCREEN_NAME" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
  FILENAME=$(printf "%02d_%s.png" "$COUNTER" "$SCREEN_NAME")
  xcrun simctl io booted screenshot "$OUTPUT_DIR/$FILENAME"
  [ $? -eq 0 ] && echo "  ✅ Saved: $OUTPUT_DIR/$FILENAME" || echo "  ❌ Capture failed."
  COUNTER=$((COUNTER + 1))
done

echo ""
echo "✅ Captured $((COUNTER - 1)) screenshot(s) → $OUTPUT_DIR"
