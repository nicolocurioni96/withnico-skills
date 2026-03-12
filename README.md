# 🏥 Project Clinic AI

> AI-powered clinic management system built on Mac Mini + OpenClaw + GoHighLevel.  
> Automates lead tracking, performance monitoring, and content strategy for aesthetic medicine clinics — with real-time alerts via Telegram and Discord.

---

## 📚 Documentation Index

| Section | File | Description |
|---------|------|-------------|
| **Hardware** | [01-hardware/specs.md](./01-hardware/specs.md) | Mac Mini vs Mac Studio, RAM guide, remote access |
| **Setup** | [02-setup/macos-setup.md](./02-setup/macos-setup.md) | macOS base config, Homebrew, system dependencies |
| | [02-setup/exo-setup.md](./02-setup/exo-setup.md) | Exo — local LLM inference engine |
| | [02-setup/openclaw-setup.md](./02-setup/openclaw-setup.md) | OpenClaw — install and configure |
| **AI Config** | [03-ai-config/claude-api.md](./03-ai-config/claude-api.md) | Claude API on OpenClaw — setup and tuning |
| | [03-ai-config/local-llm.md](./03-ai-config/local-llm.md) | ⭐ Local LLMs — zero cost setup, models, routing |
| **Integrations** | [04-integrations/gohighlevel.md](./04-integrations/gohighlevel.md) | GoHighLevel CRM — API, webhooks, data |
| | [04-integrations/telegram-bot.md](./04-integrations/telegram-bot.md) | Telegram — alerts, notifications, commands |
| | [04-integrations/imessage-setup.md](./04-integrations/imessage-setup.md) | iMessage — setup and use cases |
| | [04-integrations/discord-setup.md](./04-integrations/discord-setup.md) | Discord — channel structure, webhooks, team |
| **CRM** | [05-crm/leads-management.md](./05-crm/leads-management.md) | Leads — pipeline, tagging, scoring |
| | [05-crm/automation-flows.md](./05-crm/automation-flows.md) | Automations — triggers, actions, sequences |
| | [05-crm/calls-management.md](./05-crm/calls-management.md) | Calls — log, follow-up, analysis |
| **Skills** | [06-skills/skills-overview.md](./06-skills/skills-overview.md) | All OpenClaw skills map |
| | [06-skills/ghl-monitor.md](./06-skills/ghl-monitor.md) | Skill: daily CRM monitor |
| | [06-skills/performance-alert.md](./06-skills/performance-alert.md) | Skill: performance drop alerts |
| | [06-skills/content-strategy.md](./06-skills/content-strategy.md) | Skill: editorial plan and Reels scripts |
| | [06-skills/ads-review.md](./06-skills/ads-review.md) | Skill: ad campaigns review |
| **Notifications** | [07-notifications/alerts-system.md](./07-notifications/alerts-system.md) | Alert system — thresholds, priority, channels |
| | [07-notifications/report-templates.md](./07-notifications/report-templates.md) | Message templates for Telegram and Discord |
| **Scaling** | [08-scaling/scaling-guide.md](./08-scaling/scaling-guide.md) | When and how to scale — future scenarios |
| **Troubleshooting** | [09-troubleshooting/common-issues.md](./09-troubleshooting/common-issues.md) | Common problems and fixes |

📋 **Quick Reference:** [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            PROJECT CLINIC AI                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  EXTERNAL DATA SOURCES
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │ GoHighLevel  │     │  Meta Ads    │     │  Google Ads  │
  │  CRM/Leads   │     │  Campaigns   │     │  Campaigns   │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │ API                │ API                 │ API
         └────────────────────┴─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MAC MINI M4 Pro (24/7)                                │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           OPENCLAW                                   │    │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐    │    │
│  │   │   Skills    │    │   Memory    │    │  Scheduler (cron)   │    │    │
│  │   │   Layer     │    │   Context   │    │  08:00 · 12:00      │    │    │
│  │   │             │    │             │    │  18:00 · Mon 09:00  │    │    │
│  │   └─────────────┘    └─────────────┘    └─────────────────────┘    │    │
│  └──────────────────────────────┬──────────────────────────────────────┘    │
│                                  │                                            │
│              ┌───────────────────┼───────────────────┐                       │
│              │                   │                   │                       │
│              ▼                   ▼                   ▼                       │
│  ┌───────────────────┐  ┌────────────────┐  ┌──────────────────────────┐   │
│  │   AI ROUTING      │  │  EXO (local)   │  │     File System          │   │
│  │   LAYER           │  │                │  │                          │   │
│  │                   │  │ Llama 3.3 70B  │  │  ~/openclaw-workspace/   │   │
│  │  Task leggero? ───┼─►│ Mistral 22B    │  │  /data    /skills        │   │
│  │       │           │  │ Llama 3.1 8B   │  │  /reports /content       │   │
│  │  Task complesso?  │  │                │  │  /config                 │   │
│  │       │           │  │ GRATIS ✅      │  │                          │   │
│  │       ▼           │  └────────────────┘  └──────────────────────────┘   │
│  │  ┌────────────┐   │                                                       │
│  │  │ Claude API │   │  ← usato solo come fallback o per web search         │
│  │  │  (cloud)   │   │                                                       │
│  │  │ ~€2-5/mese │   │                                                       │
│  │  └────────────┘   │                                                       │
│  └───────────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │   Telegram   │   │   iMessage   │   │   Discord    │
  │  (primary)   │   │  (secondary) │   │ (team/logs)  │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         └───────────────────┴───────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │     YOU      │
                    │  (iPhone /   │
                    │  anywhere)   │
                    └──────────────┘
```

---

## 🧠 AI Routing — Zero Cost Strategy

The system uses a **3-level routing logic** to minimize API costs while maintaining quality:

```
TASK ARRIVES
     │
     ├─► Simple task (classify, tag, count, extract)
     │         └─► Llama 3.1 8B  — local, instant, FREE
     │
     ├─► Standard task (analyze, report, write, review)
     │         └─► Llama 3.3 70B — local, ~8 tok/s, FREE
     │
     ├─► Local offline / slow response
     │         └─► Claude Sonnet  — cloud fallback, ~€0.003/1k tokens
     │
     └─► Extraordinary task (annual strategy, full audit)
               └─► Claude Opus   — cloud, ~€0.015/1k tokens (1x/month)
```

| Model | Where | RAM | Quality (IT) | Cost |
|-------|-------|-----|-------------|------|
| Llama 3.3 70B Q4 | Local | 40 GB | ⭐⭐⭐⭐⭐ | **Free** |
| Qwen 2.5 72B Q4 | Local | 40 GB | ⭐⭐⭐⭐⭐ | **Free** |
| Mistral 22B | Local | 14 GB | ⭐⭐⭐⭐ | **Free** |
| Llama 3.1 8B | Local | 6 GB | ⭐⭐⭐ | **Free** |
| Claude Sonnet | Cloud | — | ⭐⭐⭐⭐⭐ | ~€20–50/mo |
| Claude Opus | Cloud | — | ⭐⭐⭐⭐⭐ | ~€60–100/mo |

→ Full setup guide: [03-ai-config/local-llm.md](./03-ai-config/local-llm.md)

---

## 💰 Stack and Costs

### Standard Setup (24GB RAM — Claude API primary)

| Service | Purpose | Cost |
|---------|---------|------|
| **Mac Mini M4 Pro 24GB** | AI worker hardware | ~€1,400 one-time |
| **OpenClaw** | AI agent framework | Free |
| **Exo + Llama 3.1 8B** | Local LLM for light tasks | Free |
| **Claude API** | AI brain for complex tasks | ~€20–50/month |
| **GoHighLevel** | CRM + automations | ~€97/month |
| **Telegram Bot** | Primary notifications | Free |
| **Discord** | Team + logs | Free |
| **Google Workspace** | Docs + Drive | ~€6/month |

**Monthly: ~€130–160/month**

---

### Zero-Cost Setup (48GB RAM — Local LLM primary)

| Service | Purpose | Cost |
|---------|---------|------|
| **Mac Mini M4 Pro 48GB** | AI worker hardware | ~€1,800 one-time |
| **OpenClaw** | AI agent framework | Free |
| **Exo + Llama 3.3 70B** | Local LLM for ALL tasks | **Free** |
| **Claude API** | Fallback only (~5% of tasks) | ~€2–5/month |
| **GoHighLevel** | CRM + automations | ~€97/month |
| **Telegram Bot** | Primary notifications | Free |
| **Discord** | Team + logs | Free |
| **Google Workspace** | Docs + Drive | ~€6/month |

**Monthly: ~€108–115/month** — save ~€40/month vs standard, payback in ~10 months on RAM upgrade

---

## 🔄 Daily Operational Flow

```
08:00           →  GHL Monitor       →  Morning report on Telegram
12:00           →  Silent check      →  Notify only if anomaly
18:00           →  Silent check      →  Notify only if anomaly
Real-time       →  New lead in GHL   →  Instant notify + auto-tag + score
Monday 09:00    →  Weekly report     →  PDF on Google Drive + Telegram link
Wednesday 09:00 →  Content          →  Reels scripts draft for review
```

---

## 🗂️ Repository Structure

```
project-clinic-ai/
│
├── README.md                        ← You are here
├── QUICK-REFERENCE.md               ← Quick commands and shortcuts
├── .gitignore
│
├── 01-hardware/
│   └── specs.md
│
├── 02-setup/
│   ├── macos-setup.md
│   ├── exo-setup.md
│   └── openclaw-setup.md
│
├── 03-ai-config/
│   ├── claude-api.md                ← Cloud AI setup
│   └── local-llm.md                 ← ⭐ Zero-cost local AI setup
│
├── 04-integrations/
│   ├── gohighlevel.md
│   ├── telegram-bot.md
│   ├── imessage-setup.md
│   └── discord-setup.md
│
├── 05-crm/
│   ├── leads-management.md
│   ├── automation-flows.md
│   └── calls-management.md
│
├── 06-skills/
│   ├── skills-overview.md
│   ├── ghl-monitor.md
│   ├── performance-alert.md
│   ├── content-strategy.md
│   └── ads-review.md
│
├── 07-notifications/
│   ├── alerts-system.md
│   └── report-templates.md
│
├── 08-scaling/
│   └── scaling-guide.md
│
├── 09-troubleshooting/
│   └── common-issues.md
│
├── 10-config/
│   ├── integrations.example.json
│   └── thresholds.example.json
│
└── 11-scripts/
    ├── setup.sh
    └── healthcheck.sh
```

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/project-clinic-ai.git
cd project-clinic-ai

# 2. Copy config templates
cp 10-config/integrations.example.json ~/openclaw-workspace/config/integrations.json
cp 10-config/thresholds.example.json ~/openclaw-workspace/config/thresholds.json

# 3. Fill in your API keys
nano ~/openclaw-workspace/config/integrations.json

# 4. Run Mac Mini setup
chmod +x 11-scripts/setup.sh && ./11-scripts/setup.sh

# 5. Health check
./11-scripts/healthcheck.sh
```

---

## 📅 Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-02-19 | v1.2 | Added zero-cost local AI architecture and routing layer |
| 2026-02-19 | v1.1 | Added department structure and node architecture |
| 2026-02-19 | v1.0 | Initial release |

---

*Project Clinic AI — WithNico / Nicolò Curioni © 2026*
