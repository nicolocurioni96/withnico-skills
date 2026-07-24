<img src="assets/shotkit-banner.png" width="100%" alt="Shotkit banner" />

# Shotkit

[![Release](https://img.shields.io/github/v/release/nicolocurioni96/withnico-skills?style=flat-square&label=Release&color=E8530E)](https://github.com/nicolocurioni96/withnico-skills/releases)
[![Stars](https://img.shields.io/github/stars/nicolocurioni96/withnico-skills?style=flat-square&label=Stars&color=F5A623)](https://github.com/nicolocurioni96/withnico-skills/stargazers)
[![License](https://img.shields.io/github/license/nicolocurioni96/withnico-skills?style=flat-square&label=License&color=D4A017)](https://github.com/nicolocurioni96/withnico-skills/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Homebrew](https://img.shields.io/badge/Homebrew-Ready-FBB040?style=flat-square&logo=homebrew&logoColor=white)](https://github.com/nicolocurioni96/homebrew-tools)
[![Platform](https://img.shields.io/badge/Platform-macOS-E8530E?style=flat-square&logo=apple&logoColor=white)](https://github.com/nicolocurioni96/withnico-skills)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-F5A623?style=flat-square&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/nicolocurioni96)

Open source Claude Code agent skills for iOS developers and content creators on Mac.

Built by [Nicolò Curioni](https://withnico.com) 🔸 — [@nicolocurioni96](https://github.com/nicolocurioni96)

---

## Install

### Homebrew (recommended)

```bash
brew tap nicolocurioni96/tools
brew install shotkit
```

Then use the `shotkit` CLI directly:
```bash
shotkit doctor                                            # verify environment before you start
shotkit init                                              # connect to App Store Connect
shotkit capture --bundle-id com.app.id --deeplinks "..."  # auto-capture from Simulator
shotkit generate --app-name "MyApp" --template trending   # generate with trending styles
shotkit upload --dir ./screenshots-output                  # upload to App Store Connect
```

### As an Agent Skill

Install all skills at once:
```bash
npx ai-agent-skills install nicolocurioni96/withnico-skills
```

Install a single skill:
```bash
npx ai-agent-skills install nicolocurioni96/withnico-skills --skill shotkit
```

Or register as a Claude Code plugin:
```
/plugin install withnico-skills@nicolocurioni96
```

Works with **Claude Code**, **Cursor**, **Codex**, **Gemini CLI**, **OpenCode**, and any agent following the [Agent Skills open standard](https://agentskills.io).

---

## Skills

| Skill | What it does | Platform | Status |
|-------|-------------|----------|--------|
| [shotkit](./skills/shotkit/) | End-to-end App Store screenshot pipeline: auto-capture → trending styles → App Store Connect upload | macOS | ✅ Ready |

More skills coming — see [Roadmap](#roadmap).

---

## shotkit

The full App Store screenshot workflow in one Claude Code skill.

**Trigger phrases:**
- "create my App Store screenshots"
- "generate screenshots for my app"
- "design screenshot templates"
- "capture simulator screenshots"
- "build my App Store creatives"

**What it does:**

1. **Auto-Capture** — boots Simulator devices, launches your app, navigates via deep links, sets a clean status bar, and captures screenshots — fully automated, zero manual interaction
2. **Copy** — generates locale-aware headlines (max 30 chars) + sublines (max 60 chars) per screenshot
3. **Composite** — renders styled images using Pillow with 6 template styles including trending auto-styles
4. **Organize & Validate** — outputs an ASC-ready folder structure, validates dimensions
5. **App Store Connect** — native integration to upload, update, and download screenshots directly

**6 Template Styles:**

| Template | Best For | Style |
|----------|---------|-------|
| `trending` | Any app | Auto-styled with curated palettes from top-charting apps |
| `minimal` | Productivity, utilities, finance | White bg, shadow device, clean text below |
| `bold` | Games, lifestyle, fitness | Full-bleed gradient, large text at top |
| `dark` | Pro tools, music, photography | Black bg, colored glow, premium feel |
| `editorial` | Creative, travel, shopping | Split layout, magazine composition |
| `flat` | Photo/video, maps, AR | Full-bleed UI, semi-transparent text bar |

**Trending palettes:** aurora, sunset-pop, midnight, ocean, coral, forest, neon, slate, peach, electric — or auto-extract from your app icon.

**Device frames:**
Add realistic Apple device bezels with `--frame device`:
```bash
shotkit generate --app-name "MyApp" --captures ./raw --template bold --frame device --frame-color natural-titanium
```

| Frame Color | Device |
|-------------|--------|
| `black-titanium` | iPhone 16 Pro/Max |
| `natural-titanium` | iPhone 16 Pro/Max |
| `white-titanium` | iPhone 16 Pro/Max |
| `desert-titanium` | iPhone 16 Pro/Max |
| `space-black` | iPad Pro |
| `silver` | iPad Pro |

Frames include Dynamic Island, side buttons, and accurate corner radii. Run `shotkit frame-colors` to list all options.

> **Note on device likenesses.** Shotkit renders stylised bezels programmatically — it does not embed real Apple product photography. When shipping to the App Store, follow Apple's [Marketing Resources & Identity Guidelines](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html) on how iPhone, iPad, and other Apple product silhouettes may be used in your creatives.

**Device support (2025/2026):**
- iPhone 6.9" — 1320 × 2868 px ✅ mandatory
- iPhone 6.7" — 1290 × 2796 px
- iPhone 6.5" — 1242 × 2688 px
- iPad 13" — 2064 × 2752 px ✅ mandatory (if iPad)
- iPad 12.9" — 2048 × 2732 px

**Locale support:**
en-US, it, de, ja, fr, es, pt-BR, ko — tone-adapted per market.

**App Store Connect integration:**
```bash
shotkit init                           # connect with your API key
shotkit apps                           # list your apps
shotkit download --output ./backup     # download existing screenshots
shotkit upload --dir ./screenshots-output   # upload new screenshots
shotkit update --dir ./screenshots-output   # replace existing screenshots
```

**Requirements:**
- macOS only
- Xcode installed (for Simulator capture)
- Python 3.8+ (auto-detected)
- Pillow, PyJWT, cryptography — auto-installed into an isolated venv at `~/.shotkit/venv`. Set `SHOTKIT_LEGACY_INSTALL=1` before `shotkit install-deps` to keep the pre-2.1 behaviour of installing into system Python.
- App Store Connect API key (for upload/download — [create one here](https://appstoreconnect.apple.com/access/integrations/api))

**Quick start:**
```bash
# 1. Connect to App Store Connect
shotkit init

# 2. Full pipeline in one command
shotkit screenshots \
  --bundle-id com.yourapp.bundleid \
  --app-name "YourApp" \
  --template trending \
  --icon ./icon.png \
  --deeplinks "myapp://home,myapp://detail,myapp://settings" \
  --screens "home,detail,settings"

# 3. Upload to App Store Connect
shotkit upload --dir ./screenshots-output
```

**Or step by step:**
```bash
shotkit capture --bundle-id com.app.id --deeplinks "myapp://home,myapp://detail"
shotkit generate --app-name "MyApp" --captures ./raw --template trending --palette aurora
shotkit validate --dir ./screenshots-output
shotkit upload --dir ./screenshots-output
```

**Key features:**
- Fully automated Simulator capture — zero manual interaction
- 10 curated trending palettes + auto-extract from app icon
- Native App Store Connect integration — upload, download, update
- Multi-device, multi-locale support
- ASC-ready folder structure with validation

---

## Troubleshooting

**`shotkit doctor` first.** It reports which of Python, Pillow, PyJWT, cryptography, xcrun, a booted Simulator, and `.shotkit.json` are present, and prints a targeted hint for each miss.

**Simulator won't boot.** Verify the device name matches an installed runtime:
```bash
xcrun simctl list devices available
```
Pass the exact name to `--devices-sim`, e.g. `--devices-sim "iPhone 16 Pro Max"`. If the runtime is missing, install it in Xcode → Settings → Platforms.

**Deep link isn't recognised.** Confirm the URL scheme is registered in your app's Info.plist (`CFBundleURLTypes`) and that the app is already installed and launched at least once on the target Simulator. Test the deep link manually first:
```bash
xcrun simctl openurl booted "myapp://home"
```

**Upload fails with 403.** The API key needs the **Developer** or **App Manager** role in App Store Connect → Users and Access → Keys. The key you generated must have access to the app you selected during `shotkit init`.

**Upload fails with "alpha channel not permitted".** App Store Connect rejects PNGs with transparency. Run `shotkit validate --dir ./screenshots-output` — v2.1 flags this as a warning; flatten the offending PNGs (open in Preview, export as PNG without alpha) and re-upload.

**Python packages not found.** If Homebrew isn't managing shotkit for you, run:
```bash
shotkit install-deps
```
That creates `~/.shotkit/venv` and installs Pillow, PyJWT, and cryptography there. To force the pre-2.1 behaviour of installing into system Python, prefix with `SHOTKIT_LEGACY_INSTALL=1`.

---

## Roadmap

| Skill | What it will do |
|-------|----------------|
| `xcode-release-notes` | git log → App Store What's New copy in multiple languages |
| `ios-localization` | Localize App Store metadata for 28+ territories intelligently |
| `transcript-recycler` | YouTube URL → full content repurposing pack |
| `youtube-package` | One brief → complete bilingual YouTube video content package |
| `apple-notes-agent` | Create, search, and manage Apple Notes from Claude Code |
| `swift-review` | SwiftUI and iOS-specific code review: architecture, App Store compliance |

---

## Contributing

PRs welcome. Each skill lives in `skills/<skill-name>/` with:
```
skills/my-skill/
├── SKILL.md
├── scripts/
└── references/
```

Follow the [Agent Skills open standard](https://agentskills.io) for `SKILL.md` format.

---

## License

MIT — see [LICENSE](./LICENSE)

---

## Author

Nicolò Curioni — [withnico.com](https://withnico.com) · [@nicolocurioni96](https://github.com/nicolocurioni96)

iOS Engineer · AI Evangelist · Indie Developer · Content Creator

Discord: https://discord.gg/JXgrVwqa8b
