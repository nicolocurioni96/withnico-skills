# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] — Unreleased

### Added
- **Native App Store Connect integration** — `shotkit init`, `shotkit apps`, `shotkit download`, `shotkit upload`, `shotkit update`. Direct REST API integration using JWT authentication (PyJWT + cryptography). No third-party CLI tools required.
- **Trending styles engine** — data-driven renderer with 10 curated palettes (aurora, sunset-pop, midnight, ocean, coral, forest, neon, slate, peach, electric) based on top-charting App Store apps.
- **Auto-palette from app icon** — extracts dominant colors from your app icon and generates brand-aware gradients automatically (`--icon ./icon.png`).
- **Custom brand color support** — `--brand-color "#1E90FF"` for consistent brand identity.
- **`shotkit screenshots`** — full pipeline command that runs capture + generate + validate in one step.
- **`shotkit palettes`** — list all available trending palettes with categories and vibes.
- New scripts: `asc_api.py`, `asc_init.py`, `asc_upload.py`, `asc_download.py`, `trending.py`, `color_utils.py`, `trending_palettes.json`.
- Reference doc: `references/app_store_connect.md` — native ASC integration guide.

### Changed
- **CLI wrapper** — bumped to v2.0.0 with new subcommands: `init`, `apps`, `download`, `upload`, `update`, `screenshots`, `palettes`.
- **generate_screenshots.py** — added `trending` template with `--icon`, `--brand-color`, `--palette` flags.
- **install_deps.sh** — now installs PyJWT and cryptography alongside Pillow.
- **Formula/shotkit.rb** — bumped to v2.0.0, added PyJWT and cryptography to venv.
- **SKILL.md** — added Stage 5 (Upload), trending template docs, ASC integration workflow, full pipeline command.
- **README.md** — updated with ASC integration, trending palettes, streamlined quick start.
- **template_guide.md** — added trending template section.

### Removed
- **references/asc_upload.md** — replaced by native `references/app_store_connect.md`. Shotkit no longer references third-party `asc` CLI tools.

## [1.0.0]

### Added
- **Homebrew support** — `brew tap nicolocurioni96/tools && brew install shotkit`.
- **`shotkit` CLI wrapper** — unified command with subcommands: `capture`, `generate`, `validate`, `install-deps`.
- **auto_capture.sh** — fully automated Simulator capture with deep link navigation, clean status bar, multi-device support.
- **generate_screenshots.py** — compositing engine with 5 template styles: minimal, bold, dark, editorial, flat.
- **validate_output.py** — App Store dimension validation.
- **Homebrew formula** (`Formula/shotkit.rb`).
- Reference docs: device_specs.md, template_guide.md, capture_guide.md, copy_example.json.
