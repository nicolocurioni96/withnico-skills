# Security Policy

## Reporting a Vulnerability

If you find a security issue in any skill (e.g. a script that could expose
credentials, exfiltrate data, or execute unsafe commands), please
**do not open a public GitHub issue**.

Report it privately via Discord:

👉 **https://discord.gg/JXgrVwqa8b**

Join the server and open a private thread in **#security-reports**
or send a direct message to **@withnico**.

Include:
- Which skill is affected
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
