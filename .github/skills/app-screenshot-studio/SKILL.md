---
name: shotkit
description: Autonomously generate, design, and organize App Store screenshots for iOS and iPadOS apps. Use this skill whenever a developer asks to create App Store screenshots, generate screenshot assets, design screenshot templates, capture simulator screens, produce localized screenshots, or organize screenshots by device size. Triggers on phrases like "create my App Store screenshots", "generate screenshots for my app", "make screenshot assets", "design screenshot templates", "capture simulator screenshots", "build my App Store creatives". This skill handles the FULL pipeline end-to-end: capturing raw UI from the Xcode Simulator → generating styled composites with text overlays → organizing output into ASC-ready folder structure. Always use this skill when any part of the App Store screenshot workflow is mentioned.
compatibility:
  platform: macOS only
  requires:
    - Xcode + Simulator (for capture mode)
    - Python 3.8+ with Pillow (auto-installed by skill)
    - xcrun (bundled with Xcode)
---

# Shotkit

End-to-end App Store screenshot pipeline for indie iOS developers. From raw Simulator capture to upload-ready assets organized by device, locale, and template style.

---

## What This Skill Does

**Stage 1 — Capture** (optional): Takes raw UI screenshots from the Xcode Simulator using `xcrun simctl`.

**Stage 2 — Generate Copy**: Produces locale-aware headlines + sublines for each screenshot frame.

**Stage 3 — Composite**: Renders styled screenshot images using Pillow — background, device mockup area, app UI screenshot, and text overlay.

**Stage 4 — Organize**: Outputs a folder structure compatible with `asc` CLI and App Store Connect upload.

---

## Workflow

### Step 1 — Collect Inputs

Ask the developer for the following (or infer from context if already provided):

**Required:**
- App name
- Core features to highlight (3–8 bullet points)
- Target audience (one sentence)
- Primary language (default: English)
- Additional locales (optional, e.g. Italian, German, Japanese)

**Screenshot source (choose one):**
- A) Auto-capture from booted Simulator → ask for app Bundle ID
- B) Existing screenshots folder → ask for path to folder of PNG/JPG files
- C) No UI screenshots yet → generate placeholder-based composites with colored UI mockups

**Template style (choose one, or generate previews for all):**
- `minimal` — white/light background, small device frame, centered text, clean typography
- `bold` — full-bleed gradient background, large text, high contrast, punchy
- `dark` — dark/black background, device glow effect, premium feel
- `editorial` — magazine-style layout, diagonal composition, text beside device
- `flat` — no device frame, full-bleed app UI with text overlay bar at top or bottom

**Device targets (default: iPhone 6.9" + iPad 13"):**
- iPhone 6.9" — 1320 × 2868 px (mandatory as of 2025)
- iPhone 6.7" — 1290 × 2796 px (legacy, still widely used)
- iPhone 6.5" — 1242 × 2688 px
- iPad 13" — 2064 × 2752 px (mandatory if app supports iPad)
- iPad 12.9" — 2048 × 2732 px

> Read `references/device_specs.md` for the full device dimensions table.

---

### Step 2 — Install Dependencies
```bash
cat > "$REPO/skills/shotkit/scripts/install_deps.sh" << 'EOF'
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
  echo "⚠️  xcrun not found. Simulator capture will not work."
fi
echo ""
echo "✅ Dependencies ready."
