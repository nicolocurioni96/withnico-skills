# Security Policy

## Reporting a Vulnerability

If you find a security issue in any skill (e.g. a script that could expose credentials, exfiltrate data, or execute unsafe commands), please **do not open a public issue**.

Email: nicolo@withnico.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

I will respond within 72 hours and credit you in the fix if you'd like.

---

## Skill Safety Rules

All skills in this repo must follow these rules:

- No hard-coded API keys, tokens, or passwords
- No network calls without explicit user knowledge
- No file deletion without user confirmation
- No data exfiltration of any kind
- Scripts must be readable and auditable

Skills that violate these rules will be removed immediately.
