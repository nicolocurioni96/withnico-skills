# withnico-skills

Open source Claude Code agent skills for iOS developers and content creators on Mac.

Built by [Nicolò Curioni](https://withnico.com) — [@nicolocurioni96](https://github.com/nicolocurioni96)

---

## Install

Install all skills at once:
```bash
npx ai-agent-skills install nicolocurioni96/withnico-skills
```

Install a single skill:
```bash
npx ai-agent-skills install nicolocurioni96/withnico-skills --skill app-screenshot-studio
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
| [app-screenshot-studio](./skills/app-screenshot-studio/) | End-to-end App Store screenshot pipeline: Simulator capture → 5 templates → multi-locale compositing → ASC-ready output | macOS | ✅ Ready |

More skills coming — see [Roadmap](#roadmap).

---

## app-screenshot-studio

The full App Store screenshot workflow in one Claude Code skill.

**Trigger phrases:**
- "create my App Store screenshots"
- "generate screenshots for my app"
- "design screenshot templates"
- "capture simulator screenshots"
- "build my App Store creatives"

**What it does:**

1. **Capture** — pulls raw UI from Xcode Simulator via `xcrun simctl`, interactively screen by screen
2. **Copy** — generates locale-aware headlines (max 30 chars) + sublines (max 60 chars) per screenshot
3. **Composite** — renders styled images using Pillow with 5 template styles
4. **Organize** — outputs an ASC-ready folder structure, validates dimensions, generates upload checklist

**5 Template Styles:**

| Template | Best For | Style |
|----------|---------|-------|
| `minimal` | Productivity, utilities, finance | White bg, shadow device, clean text below |
| `bold` | Games, lifestyle, fitness | Full-bleed gradient, large text at top |
| `dark` | Pro tools, music, photography | Black bg, colored glow, premium feel |
| `editorial` | Creative, travel, shopping | Split layout, magazine composition |
| `flat` | Photo/video, maps, AR | Full-bleed UI, semi-transparent text bar |

**Device support (2025/2026):**
- iPhone 6.9" — 1320 × 2868 px ✅ mandatory
- iPhone 6.7" — 1290 × 2796 px
- iPhone 6.5" — 1242 × 2688 px
- iPad 13" — 2064 × 2752 px ✅ mandatory (if iPad)
- iPad 12.9" — 2048 × 2732 px

**Locale support:**
en-US, it, de, ja, fr, es, pt-BR, ko — tone-adapted per market.

**Requirements:**
- macOS only
- Xcode installed (for Simulator capture)
- Python 3.8+ (auto-detected)
- Pillow (auto-installed by skill)

**Quick start:**
```bash
# 1. Install deps
bash skills/app-screenshot-studio/scripts/install_deps.sh

# 2. Capture from Simulator
bash skills/app-screenshot-studio/scripts/capture_simulator.sh com.yourapp.bundleid ./raw

# 3. Generate screenshots
python3 skills/app-screenshot-studio/scripts/generate_screenshots.py \
  --app-name "YourApp" \
  --captures ./raw \
  --copy ./skills/app-screenshot-studio/references/copy_example.json \
  --template bold \
  --devices iphone-6.9 ipad-13 \
  --locales en-US it \
  --output ./screenshots-output

# 4. Validate
python3 skills/app-screenshot-studio/scripts/validate_output.py --dir ./screenshots-output
```

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
