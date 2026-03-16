---
name: shotkit
description: Autonomously generate, design, and organize App Store screenshots for iOS and iPadOS apps. Use this skill whenever a developer asks to create App Store screenshots, generate screenshot assets, design screenshot templates, capture simulator screens, produce localized screenshots, or organize screenshots by device size. Triggers on phrases like "create my App Store screenshots", "generate screenshots for my app", "make screenshot assets", "design screenshot templates", "capture simulator screenshots", "build my App Store creatives". This skill handles the FULL pipeline end-to-end: capturing raw UI from the Xcode Simulator → generating styled composites with text overlays → organizing output into ASC-ready folder structure. Always use this skill when any part of the App Store screenshot workflow is mentioned.
compatibility:
  platform: macOS only
  requires:
    - Xcode + Simulator (for capture mode)
    - Python 3.8+ with Pillow, PyJWT, cryptography (auto-installed by skill)
    - xcrun (bundled with Xcode)
    - App Store Connect API key (for upload/download)
---

# Shotkit

End-to-end App Store screenshot pipeline for indie iOS developers. From raw Simulator capture to upload-ready assets, with native App Store Connect integration.

**This skill is fully automated.** When triggered, the agent handles the entire pipeline — booting simulators, capturing screenshots, compositing with trending styles, and uploading to App Store Connect — without requiring manual interaction.

---

## What This Skill Does

**Stage 1 — Auto-Capture** (optional): Boots Xcode Simulator devices, launches the app via bundle ID, navigates screens via deep links, sets a clean status bar (9:41, full battery), and captures raw UI screenshots — all without user interaction.

**Stage 2 — Generate Copy**: Produces locale-aware headlines (max 30 chars) + sublines (max 60 chars) for each screenshot frame. If no copy.json is provided, the agent generates one based on the app's features and target audience.

**Stage 3 — Composite**: Renders styled screenshot images using Pillow — background, device UI area, app screenshot, and text overlay — with 5 template styles.

**Stage 4 — Organize & Validate**: Outputs an ASC-ready folder structure (`{locale}/{device}/`), validates dimensions against App Store requirements, and generates an upload checklist.

**Stage 5 — Upload** (optional): Uploads screenshots directly to App Store Connect via native API integration. Supports uploading new screenshots and replacing existing ones.

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
- A) **Automated capture** from Simulator → ask for app Bundle ID and deep link URLs per screen
- B) **Existing screenshots** folder → ask for path to folder of PNG/JPG files
- C) **No UI screenshots yet** → generate placeholder-based composites with colored UI mockups

If the developer chooses option A, also ask:
- Deep link URL scheme (e.g. `myapp://`) and paths for each screen to capture
- Which Simulator devices to boot (default: iPhone 16 Pro Max)
- If no deep links are available, the agent will capture the app's launch screen only

**Template style (choose one, or generate previews for all):**
- `minimal` — white/light background, small device frame, centered text, clean typography
- `bold` — full-bleed gradient background, large text, high contrast, punchy
- `dark` — dark/black background, device glow effect, premium feel
- `editorial` — magazine-style layout, split composition, text beside device
- `flat` — no device frame, full-bleed app UI with text overlay bar at bottom

**Device targets (default: iPhone 6.9" + iPad 13"):**
- iPhone 6.9" — 1320 × 2868 px (mandatory as of 2025)
- iPhone 6.7" — 1290 × 2796 px (legacy, still widely used)
- iPhone 6.5" — 1242 × 2688 px
- iPad 13" — 2064 × 2752 px (mandatory if app supports iPad)
- iPad 12.9" — 2048 × 2732 px

> Read `references/device_specs.md` for the full device dimensions table.

---

### Step 2 — Install Dependencies

Run the dependency installer:
```bash
bash skills/shotkit/scripts/install_deps.sh
```

This checks for Python 3, installs Pillow, and verifies xcrun is available.

---

### Step 3 — Capture Screenshots (Automated)

**Option A — Fully automated capture with deep links:**
```bash
bash skills/shotkit/scripts/auto_capture.sh \
  --bundle-id com.yourapp.bundleid \
  --devices "iPhone 16 Pro Max,iPad Pro 13-inch (M4)" \
  --screens "home,detail,settings,profile,onboarding" \
  --deeplinks "myapp://home,myapp://detail/1,myapp://settings,myapp://profile,myapp://onboarding" \
  --output ./raw-captures
```

**Option A (with config file):**
Create a `capture_config.json`:
```json
{
  "bundle_id": "com.yourapp.bundleid",
  "devices": ["iPhone 16 Pro Max", "iPad Pro 13-inch (M4)"],
  "screens": [
    {"name": "home", "deeplink": "myapp://home"},
    {"name": "detail", "deeplink": "myapp://detail/1"},
    {"name": "settings", "deeplink": "myapp://settings"},
    {"name": "profile", "deeplink": "myapp://profile"},
    {"name": "onboarding", "deeplink": "myapp://onboarding"}
  ]
}
```
Then run:
```bash
bash skills/shotkit/scripts/auto_capture.sh --config capture_config.json --output ./raw-captures
```

The auto-capture script will:
1. Boot each Simulator device automatically
2. Set a clean status bar (9:41, full battery, full signal)
3. Launch the app
4. Navigate to each screen via deep link
5. Wait for the screen to settle, then capture
6. Save organized by device subfolder
7. Shut down each device when done

**Option B — Interactive capture (fallback):**
```bash
bash skills/shotkit/scripts/capture_simulator.sh com.yourapp.bundleid ./raw-captures
```
This is the legacy interactive mode where the developer navigates manually and presses ENTER to capture.

**Option C — Existing screenshots:**
Skip this step. Point `--captures` at the existing folder in Step 4.

---

### Step 4 — Generate Copy (if needed)

If the developer has not provided a `copy.json`, generate one based on the app's features and target audience. Follow the format in `references/copy_example.json`:

```json
{
  "en-US": {
    "screenshots": [
      {"headline": "Max 30 chars", "subline": "Max 60 chars for the subline text", "scene": "Screen name"}
    ]
  }
}
```

Rules:
- Headlines: max 30 characters, action-oriented
- Sublines: max 60 characters, benefit-focused
- Adapt tone per locale (formal for de/ja, casual for en-US)
- One entry per screenshot, matched by index to the capture files

Save as `copy.json` in the project root or a path the developer specifies.

---

### Step 5 — Composite Screenshots

Run the compositing engine:
```bash
python3 skills/shotkit/scripts/generate_screenshots.py \
  --app-name "YourApp" \
  --captures ./raw-captures \
  --copy ./copy.json \
  --template bold \
  --devices iphone-6.9 ipad-13 \
  --locales en-US it \
  --output ./screenshots-output
```

This will:
1. Load raw captures from the captures directory
2. Load copy data for each locale
3. Render each screenshot through the chosen template
4. Resize and position the UI within the device-specific canvas
5. Add text overlays (headline + subline)
6. Save as PNG in the ASC-ready folder structure: `{output}/{locale}/{device}/01_screen.png`

Available templates: `minimal`, `bold`, `dark`, `editorial`, `flat`, `trending`

> Read `references/template_guide.md` for detailed template descriptions and customization.

**Trending template** (recommended):
```bash
shotkit generate --app-name "YourApp" --captures ./raw --template trending --icon ./icon.png
shotkit generate --app-name "YourApp" --captures ./raw --template trending --palette aurora
shotkit generate --app-name "YourApp" --captures ./raw --template trending --brand-color "#1E90FF"
```

The trending template uses curated color palettes and layouts based on top-charting App Store apps. It can also auto-extract brand colors from your app icon. Run `shotkit palettes` to see all available palettes.

---

### Step 6 — Validate Output

```bash
shotkit validate --dir ./screenshots-output
```

Checks:
- All screenshots match required device dimensions
- Max 10 per device per locale
- Files are valid PNG/JPEG
- Generates a pass/fail report

---

### Step 7 — App Store Connect Integration

**First-time setup:**
```bash
shotkit init
```
This connects to App Store Connect, verifies credentials, and saves config to `.shotkit.json`.

**Download existing screenshots (backup):**
```bash
shotkit download --output ./backup
```

**Upload new screenshots:**
```bash
shotkit upload --dir ./screenshots-output
```

**Replace existing screenshots:**
```bash
shotkit update --dir ./screenshots-output
```

The upload command validates screenshots automatically before uploading.

> Read `references/app_store_connect.md` for full ASC integration details.

---

### Full Pipeline (One Command)

```bash
shotkit screenshots \
  --bundle-id com.yourapp.id \
  --app-name "YourApp" \
  --template trending \
  --icon ./icon.png \
  --deeplinks "myapp://home,myapp://detail,myapp://settings" \
  --screens "home,detail,settings" \
  --devices iphone-6.9 \
  --locales en-US
```

This runs capture + generate + validate in sequence.

---

## Automation Best Practices

### Deep Link Setup
For fully automated capture, the app must support URL schemes or Universal Links. Common patterns:
- `myapp://home` — main screen
- `myapp://feature/detail?id=1` — specific content
- `myapp://settings` — settings screen
- `myapp://onboarding` — onboarding flow

Add URL schemes in Xcode: Target → Info → URL Types.

### Demo Data
For best results, ensure the app has realistic demo data loaded before capture. Options:
- Use a debug build with seeded data
- Set up a launch argument (e.g. `--demo-mode`) that loads sample content
- Use `xcrun simctl` to push notifications or set defaults before capture

### Multi-Device Workflow
The automated capture handles multiple devices sequentially — it boots each device, captures all screens, then shuts it down before moving to the next. This keeps resource usage low.

### Status Bar
The auto-capture script automatically sets the status bar to the Apple-standard "marketing" look: 9:41 AM, full battery, full signal, no carrier name. Use `--no-clean-status` to skip this.
