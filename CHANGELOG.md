# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- **Homebrew support** — `brew tap nicolocurioni96/tools && brew install shotkit`. Installs the `shotkit` CLI with all dependencies (Python venv + Pillow) managed automatically.
- **`shotkit` CLI wrapper** — Unified command-line interface with subcommands: `shotkit capture`, `shotkit generate`, `shotkit validate`, `shotkit install-deps`.
- **Homebrew formula** (`Formula/shotkit.rb`) — Homebrew tap formula for distribution.
- **auto_capture.sh** — Fully automated Simulator capture script. Boots devices, launches apps by bundle ID, navigates screens via deep links, sets a clean status bar (9:41 AM, full battery), and captures screenshots without any manual interaction. Supports multiple devices sequentially and JSON config files for repeatable setups.
- **generate_screenshots.py** — Compositing engine that renders styled App Store screenshots using Pillow. Combines raw UI captures with text overlays across 5 template styles: `minimal`, `bold`, `dark`, `editorial`, `flat`. Outputs ASC-ready folder structure (`{locale}/{device}/`).

### Changed
- **SKILL.md** — Rewritten with an automation-first workflow. Documents deep link capture, JSON config format, multi-device pipelines, and the full compositing engine usage.
- **README.md** — Added Homebrew install as the recommended method. Updated quick start with both `shotkit` CLI and direct script usage.

### Notes
- The interactive `capture_simulator.sh` is preserved as a fallback for apps without deep link support.
- Apps must support URL schemes (Xcode → Target → Info → URL Types) for fully automated capture.
- Homebrew tap requires creating a separate `nicolocurioni96/homebrew-tools` repo on GitHub (see Formula/shotkit.rb).
