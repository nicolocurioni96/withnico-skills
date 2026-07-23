# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.1] — Unreleased

### Changed
- Bump the `shotkit` CLI internal version marker to `2.0.1`.
- Sync the `.skills/app-screenshot-studio`, `.cursor/skills/app-screenshot-studio`, and `.github/skills/app-screenshot-studio` distribution mirrors so their `SKILL.md`, `scripts/`, and `references/` match the current primary skill in `skills/shotkit/` (previously frozen at the v1.0.0 snapshot).
- Document how `.shotkit.json` stores App Store Connect key metadata and where the `.p8` private key lives in `SECURITY.md`.

### Fixed
- Remove the stray `assets/.!34093!shotkit-logo.png` Finder lock file that had been committed by accident.
- Add macOS Finder metadata patterns (`.DS_Store`, `._*`, `.!*`, `.AppleDouble`, `.LSOverride`) to `.gitignore` so lock files can't reappear.

### Notes
- The Homebrew formula (`Formula/shotkit.rb`) still installs the `v2.0.0` tarball. It will be bumped to `v2.0.1` only when a real `v2.0.1` GitHub release exists so its `sha256` can be recomputed against the published tarball.

## [2.0.0] — 2026-03-16

### Added
- **Realistic device frames** — `--frame device` renders iPhone/iPad bezels with Dynamic Island, notch, side buttons, and rounded corners. Supports 6 frame colors: `black-titanium`, `natural-titanium`, `white-titanium`, `desert-titanium`, `space-black`, `silver`. Run `shotkit frame-colors` to list all options.
- **Native App Store Connect integration** — `shotkit init`, `shotkit apps`, `shotkit download`, `shotkit upload`, `shotkit update`. Direct REST API integration using JWT authentication (PyJWT + cryptography). No third-party CLI tools required.
- **Trending styles engine** — data-driven renderer with 10 curated palettes (aurora, sunset-pop, midnight, ocean, coral, forest, neon, slate, peach, electric) based on top-charting App Store apps.
- **Auto-palette from app icon** — extracts dominant colors from your app icon and generates brand-aware gradients automatically (`--icon ./icon.png`).
- **Custom brand color support** — `--brand-color "#1E90FF"` for consistent brand identity.
- **`shotkit screenshots`** — full pipeline command that runs capture + generate + validate in one step.
- **`shotkit palettes`** — list all available trending palettes with categories and vibes.
- New scripts: `device_frames.py`, `asc_api.py`, `asc_init.py`, `asc_upload.py`, `asc_download.py`, `trending.py`, `color_utils.py`, `trending_palettes.json`.
- Reference doc: `references/app_store_connect.md` — native ASC integration guide.

### Changed
- **CLI wrapper** — bumped to v2.0.0 with new subcommands: `init`, `apps`, `download`, `upload`, `update`, `screenshots`, `palettes`.
- **generate_screenshots.py** — added `trending` template with `--icon`, `--brand-color`, `--palette` flags. Added `--frame` and `--frame-color` for device frame rendering.
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
