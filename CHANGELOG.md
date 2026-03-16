# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- **auto_capture.sh** — Fully automated Simulator capture script. Boots devices, launches apps by bundle ID, navigates screens via deep links, sets a clean status bar (9:41 AM, full battery), and captures screenshots without any manual interaction. Supports multiple devices sequentially and JSON config files for repeatable setups.
- **generate_screenshots.py** — Compositing engine that renders styled App Store screenshots using Pillow. Combines raw UI captures with text overlays across 5 template styles: `minimal`, `bold`, `dark`, `editorial`, `flat`. Outputs ASC-ready folder structure (`{locale}/{device}/`).

### Changed
- **SKILL.md** — Rewritten with an automation-first workflow. Documents deep link capture, JSON config format, multi-device pipelines, and the full compositing engine usage.
- **README.md** — Updated quick start to use `auto_capture.sh` instead of the interactive capture script. Added auto-capture feature highlights.

### Notes
- The interactive `capture_simulator.sh` is preserved as a fallback for apps without deep link support.
- Apps must support URL schemes (Xcode → Target → Info → URL Types) for fully automated capture.
