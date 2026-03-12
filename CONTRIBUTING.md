# Contributing to withnico-skills

Thanks for your interest in contributing! This repo follows the [Agent Skills open standard](https://agentskills.io).

---

## Ways to Contribute

- **New skill** — add a skill nobody has built yet
- **Improve existing skill** — better instructions, more locales, bug fixes
- **Fix a bug** — scripts not working, wrong dimensions, etc.
- **Improve docs** — clearer reference files, better examples

---

## Adding a New Skill

Each skill lives in `skills/<skill-name>/` and must follow this structure:
```
skills/my-skill/
├── SKILL.md              # required — YAML frontmatter + instructions
├── scripts/              # optional — executable scripts
└── references/           # optional — docs loaded on demand
```

**SKILL.md frontmatter must include:**
```yaml
---
name: skill-name
description: Clear description of what the skill does and when to trigger it.
---
```

**Rules:**
- Test your skill in Claude Code before submitting
- No hard-coded absolute paths (use `$HOME`, relative paths)
- Shell scripts must be POSIX-compatible
- Python scripts must work with Python 3.8+
- No external API keys baked into files
- macOS-only skills must clearly state `platform: macOS only` in frontmatter

---

## Pull Request Process

1. Fork the repo
2. Create a branch: `git checkout -b feat/my-skill-name`
3. Add your skill in `skills/`
4. Test it works
5. Open a PR against `master` with a clear description
6. Fill in the PR template

PRs that add skills without a working test will not be merged.

---

## Commit Convention

Use conventional commits:
```
feat: add transcript-recycler skill
fix: correct iPhone 6.9 dimensions in device_specs
docs: improve capture_guide with simulator tips
chore: update marketplace.json
```

---

## Code of Conduct

Be kind and constructive. This is a small indie open source project.
Issues and PRs with disrespectful language will be closed.

---

## Community & Support

Join the Discord for questions, skill ideas, and feedback:

👉 **https://discord.gg/JXgrVwqa8b**

Channels:
- `#skills-general` — questions and help
- `#skill-ideas` — suggest new skills
- `#bug-reports` — report non-security bugs
- `#security-reports` — private security disclosures
