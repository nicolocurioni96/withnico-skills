# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.2.0] — 2026-07-24

### Added
- **`shotkit doctor`** — new preflight command. Verifies Python, Pillow, PyJWT, cryptography, xcrun, booted Simulators, the isolated venv at `~/.shotkit/venv`, and the shape of `.shotkit.json` (including the `.p8` private key path). Exits non-zero on required-check failure; optional checks (booted sim, ASC config) never fail the run.
- **Isolated venv installer** — `shotkit install-deps` now creates `~/.shotkit/venv` and installs Pillow, PyJWT, and cryptography there. The CLI auto-detects the venv and uses it. Set `SHOTKIT_LEGACY_INSTALL=1` to restore the pre-2.2 system-Python behaviour for one release cycle.
- **`--json` and `--report FILE`** on `shotkit validate` — emit a structured JSON report of every checked file (dimensions, mode, issues), plus totals and the current Apple spec version marker.
- **`--report FILE`** on `shotkit screenshots` — writes the validation JSON report to disk at the end of the full pipeline.
- **Alpha-channel check** in the validator — App Store Connect rejects transparent PNGs; the check surfaces them before upload. Warning in this release, will become an error in v2.3.
- **PNG/JPEG magic-byte check** in the validator — catches files whose extension doesn't match their real format. Warning in this release, error in v2.3.
- **Unknown-device-folder warning** in the validator — flags device sub-folders not in the current Apple spec.
- **Copy-length overflow warnings** in `generate` — headline > 30 chars or subline > 60 chars prints a warning to stderr (per locale, per screenshot) and is included in the run report.
- **Optional `review: true` flag** on any entry in `copy.json` — surfaces marketing/legal-sensitive copy in generate output and the run report so it doesn't reach production unreviewed.
- **`.github/workflows/ci.yml`** — GitHub Actions workflow. Runs shellcheck on all shell scripts and executes `shotkit --version`, `--help`, `palettes`, `frame-colors`, `doctor`, and an invalid-palette rejection test on `macos-latest`.
- **`SPEC_VERSION`** constant in the validator (`2025-mandatory-iphone-6.9-ipad-13`) — printed in the report so the reader can tell which Apple spec revision the run was validated against.

### Changed
- **Bump the shotkit CLI internal version marker** to `2.2.0`.
- **`--palette` and `--frame-color` are now validated** against the loaded palette and frame-color tables. Unknown values fail with a listing of valid options instead of silently falling back.
- **`shotkit generate`** now returns a summary dict `{total, overflow_warnings, review_flags}` instead of an integer, so callers can act on the extra signals. Direct CLI use is unaffected.
- **`shotkit` CLI wrapper** picks Python in this order: `~/.shotkit/venv/bin/python3` if present, else `python3` on `$PATH` (which is how the Homebrew wrapper already reaches its own venv). Set `SHOTKIT_HOME` to override the venv location.
- **`references/copy_example.json`** — annotates the new `review` field and adds it to one entry per locale so users can see it in context.
- **`README.md`** — adds a Troubleshooting section (Simulator, deep links, ASC 403, alpha PNGs, python deps), a note about Apple's device likeness guidelines, and mentions `shotkit doctor` in the quick start.

### Deprecated
- The system-Python install path in `install_deps.sh` (`pip3 install --break-system-packages`). Available in v2.2.x behind `SHOTKIT_LEGACY_INSTALL=1`; slated for removal in v3.0.0.

## [2.1.0] — 2026-03-18

### Added
- **GitHub Sponsors** — added `FUNDING.yml` for the GitHub Sponsors sidebar widget.
- **Shields.io badges** — release, stars, license, Python, Homebrew, platform, and sponsor badges in README.

### Changed
- **README banner** — replaced banner image and removed standalone logo icon for a cleaner header.

### Fixed
- **Bash argument passing** — use bash arrays for argument passing in `shotkit screenshots` command to prevent word-splitting issues.
- **Homebrew formula** — handle empty `assets/fonts` directory; updated release tarball sha256 for v2.0.0.

### Infrastructure
- **`.gitignore`** — added Python and Shotkit-specific entries.

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

## [2.0.0] — 2026-03-18

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
