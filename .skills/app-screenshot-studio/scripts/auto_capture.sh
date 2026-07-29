#!/bin/bash
# shotkit — Automated Simulator Capture
# Boots simulators, launches app, navigates via deep links, and captures
# screenshots without any manual interaction.
#
# Usage:
#   bash auto_capture.sh --bundle-id com.app.id --devices "iPhone 16 Pro Max" --screens "home,detail,settings"
#   bash auto_capture.sh --bundle-id com.app.id --deeplinks "myapp://home,myapp://detail" --devices "iPhone 16 Pro Max,iPad Pro 13-inch (M4)"
#   bash auto_capture.sh --config capture_config.json

set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────
BUNDLE_ID=""
OUTPUT_DIR="./raw-captures"
DEVICES=""
SCREENS=""
DEEPLINKS=""
CONFIG_FILE=""
CLEAN_STATUS_BAR=true
WAIT_AFTER_LAUNCH=3
WAIT_AFTER_NAVIGATE=2

# ─── Parse Arguments ─────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bundle-id)   BUNDLE_ID="$2"; shift 2 ;;
    --output)      OUTPUT_DIR="$2"; shift 2 ;;
    --devices)     DEVICES="$2"; shift 2 ;;
    --screens)     SCREENS="$2"; shift 2 ;;
    --deeplinks)   DEEPLINKS="$2"; shift 2 ;;
    --config)      CONFIG_FILE="$2"; shift 2 ;;
    --wait-launch) WAIT_AFTER_LAUNCH="$2"; shift 2 ;;
    --wait-nav)    WAIT_AFTER_NAVIGATE="$2"; shift 2 ;;
    --no-clean-status) CLEAN_STATUS_BAR=false; shift ;;
    --help|-h)
      echo "Usage: auto_capture.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --bundle-id ID        App bundle identifier (required)"
      echo "  --output DIR          Output directory (default: ./raw-captures)"
      echo "  --devices LIST        Comma-separated simulator names"
      echo "                        (default: iPhone 16 Pro Max)"
      echo "  --screens LIST        Comma-separated screen names for naming files"
      echo "                        (e.g. home,detail,settings)"
      echo "  --deeplinks LIST      Comma-separated deep link URLs to navigate"
      echo "                        (e.g. myapp://home,myapp://detail)"
      echo "  --config FILE         JSON config file (overrides other flags)"
      echo "  --wait-launch SECS    Seconds to wait after app launch (default: 3)"
      echo "  --wait-nav SECS       Seconds to wait after navigation (default: 2)"
      echo "  --no-clean-status     Skip status bar override"
      echo ""
      echo "Config JSON format:"
      echo '  {'
      echo '    "bundle_id": "com.app.id",'
      echo '    "devices": ["iPhone 16 Pro Max"],'
      echo '    "screens": ['
      echo '      {"name": "home", "deeplink": "myapp://home"},'
      echo '      {"name": "detail", "deeplink": "myapp://detail/1"}'
      echo '    ]'
      echo '  }'
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# ─── Dependency Check ────────────────────────────────────────────────
if ! command -v xcrun &>/dev/null; then
  echo "Error: xcrun not found. Install Xcode from the Mac App Store."
  exit 1
fi

# ─── Load Config File ───────────────────────────────────────────────
if [ -n "$CONFIG_FILE" ]; then
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
  fi
  if command -v python3 &>/dev/null; then
    BUNDLE_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('bundle_id',''))")
    DEVICES=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(','.join(c.get('devices',[])))")
    # Extract screens and deeplinks from config
    SCREENS=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(','.join(s['name'] for s in c.get('screens',[])))")
    DEEPLINKS=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(','.join(s.get('deeplink','') for s in c.get('screens',[])))")
  else
    echo "Error: python3 required for JSON config parsing."
    exit 1
  fi
fi

# ─── Validation ──────────────────────────────────────────────────────
if [ -z "$BUNDLE_ID" ]; then
  echo "Error: --bundle-id is required."
  echo "Run with --help for usage."
  exit 1
fi

# Default devices
if [ -z "$DEVICES" ]; then
  DEVICES="iPhone 16 Pro Max"
fi

# ─── Helper Functions ────────────────────────────────────────────────

get_device_udid() {
  local device_name="$1"
  xcrun simctl list devices available -j \
    | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data.get('devices', {}).items():
    if 'iOS' not in runtime:
        continue
    for d in devices:
        if d['name'] == '$device_name' and d['isAvailable']:
            print(d['udid'])
            sys.exit(0)
sys.exit(1)
" 2>/dev/null
}

boot_device() {
  local udid="$1"
  local name="$2"
  local state
  state=$(xcrun simctl list devices -j | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data.get('devices', {}).items():
    for d in devices:
        if d['udid'] == '$udid':
            print(d['state'])
            sys.exit(0)
" 2>/dev/null)

  if [ "$state" = "Booted" ]; then
    echo "  Already booted: $name"
    return 0
  fi

  echo "  Booting: $name..."
  xcrun simctl boot "$udid" 2>/dev/null || true
  # Wait for boot to complete
  local retries=0
  while [ $retries -lt 30 ]; do
    state=$(xcrun simctl list devices -j | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data.get('devices', {}).items():
    for d in devices:
        if d['udid'] == '$udid':
            print(d['state'])
            sys.exit(0)
" 2>/dev/null)
    if [ "$state" = "Booted" ]; then
      return 0
    fi
    sleep 1
    retries=$((retries + 1))
  done
  echo "  Warning: Device may not have fully booted."
}

clean_status_bar() {
  local udid="$1"
  # Set a clean status bar: 9:41 AM, full battery, full signal
  xcrun simctl status_bar "$udid" override \
    --time "9:41" \
    --batteryState charged \
    --batteryLevel 100 \
    --cellularMode active \
    --cellularBars 4 \
    --wifiBars 3 \
    --operatorName "" 2>/dev/null || true
}

capture_screenshot() {
  local udid="$1"
  local output_path="$2"
  xcrun simctl io "$udid" screenshot --type=png "$output_path" 2>/dev/null
}

navigate_deeplink() {
  local udid="$1"
  local deeplink="$2"
  xcrun simctl openurl "$udid" "$deeplink" 2>/dev/null
}

# ─── Main Pipeline ───────────────────────────────────────────────────

echo ""
echo "Shotkit — Automated Capture"
echo "Bundle ID : $BUNDLE_ID"
echo "Devices   : $DEVICES"
echo "Output    : $OUTPUT_DIR"
echo ""

mkdir -p "$OUTPUT_DIR"

# Open Simulator.app (needed for rendering)
open -a Simulator 2>/dev/null || true
sleep 2

# Split comma-separated values into arrays
IFS=',' read -ra DEVICE_LIST <<< "$DEVICES"
IFS=',' read -ra SCREEN_LIST <<< "$SCREENS"
IFS=',' read -ra DEEPLINK_LIST <<< "$DEEPLINKS"

TOTAL_CAPTURES=0

for device_name in "${DEVICE_LIST[@]}"; do
  device_name=$(echo "$device_name" | xargs)  # trim whitespace
  echo "--- Device: $device_name ---"

  # Resolve UDID
  UDID=$(get_device_udid "$device_name")
  if [ -z "$UDID" ]; then
    echo "  Error: Simulator '$device_name' not found. Skipping."
    echo "  Available devices:"
    xcrun simctl list devices available | grep -E "iPhone|iPad" | head -5
    continue
  fi
  echo "  UDID: $UDID"

  # Boot
  boot_device "$UDID" "$device_name"
  sleep 1

  # Clean status bar
  if [ "$CLEAN_STATUS_BAR" = true ]; then
    echo "  Setting clean status bar..."
    clean_status_bar "$UDID"
  fi

  # Normalize device name for folder
  DEVICE_FOLDER=$(echo "$device_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[()]//g')
  DEVICE_OUTPUT="$OUTPUT_DIR/$DEVICE_FOLDER"
  mkdir -p "$DEVICE_OUTPUT"

  # Launch app
  echo "  Launching $BUNDLE_ID..."
  xcrun simctl launch "$UDID" "$BUNDLE_ID" 2>/dev/null || {
    echo "  Error: Could not launch $BUNDLE_ID. Is it installed on this simulator?"
    continue
  }
  sleep "$WAIT_AFTER_LAUNCH"

  # If no deeplinks provided, just capture the current screen
  if [ ${#DEEPLINK_LIST[@]} -eq 0 ] || [ -z "${DEEPLINK_LIST[0]}" ]; then
    if [ ${#SCREEN_LIST[@]} -eq 0 ] || [ -z "${SCREEN_LIST[0]}" ]; then
      # Single capture of current state
      FILENAME="01_home.png"
      echo "  Capturing: $FILENAME"
      capture_screenshot "$UDID" "$DEVICE_OUTPUT/$FILENAME"
      TOTAL_CAPTURES=$((TOTAL_CAPTURES + 1))
    else
      # Multiple screen names but no deeplinks — capture with delay between
      COUNTER=1
      for screen_name in "${SCREEN_LIST[@]}"; do
        screen_name=$(echo "$screen_name" | xargs | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
        FILENAME=$(printf "%02d_%s.png" "$COUNTER" "$screen_name")
        echo "  Capturing: $FILENAME (waiting for manual navigation...)"
        capture_screenshot "$UDID" "$DEVICE_OUTPUT/$FILENAME"
        TOTAL_CAPTURES=$((TOTAL_CAPTURES + 1))
        COUNTER=$((COUNTER + 1))
        sleep "$WAIT_AFTER_NAVIGATE"
      done
    fi
  else
    # Navigate via deep links and capture each
    COUNTER=1
    for i in "${!DEEPLINK_LIST[@]}"; do
      deeplink=$(echo "${DEEPLINK_LIST[$i]}" | xargs)
      if [ -z "$deeplink" ]; then continue; fi

      # Get screen name
      if [ $i -lt ${#SCREEN_LIST[@]} ]; then
        screen_name=$(echo "${SCREEN_LIST[$i]}" | xargs | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
      else
        screen_name="screen_$COUNTER"
      fi

      FILENAME=$(printf "%02d_%s.png" "$COUNTER" "$screen_name")
      echo "  Navigating: $deeplink"
      navigate_deeplink "$UDID" "$deeplink"
      sleep "$WAIT_AFTER_NAVIGATE"

      echo "  Capturing: $FILENAME"
      capture_screenshot "$UDID" "$DEVICE_OUTPUT/$FILENAME"
      TOTAL_CAPTURES=$((TOTAL_CAPTURES + 1))
      COUNTER=$((COUNTER + 1))
    done
  fi

  # Shutdown device to free resources (unless it's the only one)
  if [ ${#DEVICE_LIST[@]} -gt 1 ]; then
    echo "  Shutting down $device_name..."
    xcrun simctl shutdown "$UDID" 2>/dev/null || true
    sleep 1
  fi

  echo ""
done

echo "Done. Captured $TOTAL_CAPTURES screenshot(s) in $OUTPUT_DIR"
echo ""
ls -la "$OUTPUT_DIR"/*/ 2>/dev/null || ls -la "$OUTPUT_DIR"/ 2>/dev/null
