# Capture Guide — Getting Clean Simulator Screenshots

## Before Capturing
1. Boot the correct Simulator device (iPhone 16 Pro Max for 6.9", iPad Pro 13" for iPad)
2. Set window to Physical Size: Simulator menu → Window → Physical Size
3. Use realistic demo data — no empty states, no test banners
4. Hide debug overlays

## Key Commands
```bash
# Capture current screen
xcrun simctl io booted screenshot ./raw/01_home.png

# List all simulators
xcrun simctl list devices

# Boot a simulator
xcrun simctl boot "iPhone 16 Pro Max"

# Open Simulator app
open -a Simulator
```

## The 6-Screenshot Formula
1. Hero/Home — main value prop
2. Key Feature 1 — primary feature
3. Key Feature 2 — second feature
4. Key Feature 3 — detail or settings
5. Data/Stats — completed state, streaks
6. Onboarding — shows ease of getting started
