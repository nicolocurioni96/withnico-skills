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

---

## Local Configuration Files

Some skills store per-machine configuration on disk. These files may reference
credentials or resource identifiers and must **never** be committed.

### `.shotkit.json` (created by `shotkit init`)

Written to the current working directory when you connect Shotkit to App Store
Connect. It contains:

- Your ASC **Key ID** and **Issuer ID**
- The **path** to your `.p8` private key (the key file itself stays where it is)
- Your selected app's ID and display name

The `.p8` private key is never copied or transmitted — Shotkit reads it from
the path you provide, signs a short-lived JWT locally, and uses that JWT for
each App Store Connect API call.

`.shotkit.json` is already listed in this repo's `.gitignore`. If you fork
Shotkit or vendor its scripts into another project, add `.shotkit.json` to
that project's `.gitignore` too, and store your `.p8` outside the repository
(for example under `~/.appstoreconnect/`).
