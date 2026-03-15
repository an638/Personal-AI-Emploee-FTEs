# Personal AI Employee (Digital FTE)

A comprehensive hackathon project for building autonomous AI employees ("Digital FTEs") that manage personal and business affairs 24/7. This is a local-first, agent-driven system with human-in-the-loop controls.

## Project Overview

This project implements a **Digital Full-Time Equivalent (FTE)** - an AI agent built with Claude Code and Obsidian that proactively manages:
- **Personal Affairs**: Gmail, WhatsApp, Bank transactions
- **Business Operations**: Social Media, Payments, Project Tasks, Accounting

### Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian | Local Markdown dashboard and knowledge base |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |

### Key Features

- **Watcher Architecture**: Lightweight Python scripts monitor inputs and create actionable `.md` files in `/Needs_Action`
- **Ralph Wiggum Loop**: Stop hook pattern keeping Claude iterating until tasks complete
- **Human-in-the-Loop**: Sensitive actions require file-based approval workflow
- **Monday Morning CEO Briefing**: Autonomous weekly business audit with revenue/bottleneck reports

## Directory Structure

```
Personal-AI-Emploee-FTEs/
├── .claude/skills/           # Claude skill configurations
├── .qwen/skills/             # Qwen skill configurations
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Playwright MCP documentation
│       ├── references/
│       │   └── playwright-tools.md
│       └── scripts/
│           ├── mcp-client.py # Universal MCP client (HTTP/stdio)
│           ├── start-server.sh
│           ├── stop-server.sh
│           └── verify.py
├── skills-lock.json          # Installed skills registry
└── Personal AI Employee Hackathon 0_...md  # Full architectural blueprint
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Playwright MCP Setup

The project includes a browser automation skill using Playwright MCP:

```bash
# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python mcp-client.py list -u http://localhost:8808

# Call a tool
python mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take page snapshot
python mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'
```

## Development Conventions

### Skill-Based Architecture

All AI functionality is implemented as **Agent Skills** - modular, reusable components with:
- `SKILL.md`: Documentation and usage examples
- `scripts/`: Helper scripts for server lifecycle
- `references/`: Tool schema documentation

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending messages):

1. Claude creates approval request in `/Pending_Approval/`
2. User reviews and moves file to `/Approved/` or `/Rejected/`
3. Orchestrator triggers actual MCP action on approval

### Ralph Wiggum Persistence Loop

Keep Claude working autonomously until task completion:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 watcher, basic folder structure |
| **Silver** | 20-30 hrs | Multiple watchers, MCP server, approval workflow |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, Ralph loop, audit logging |
| **Platinum** | 60+ hrs | Cloud deployment, work-zone specialization, A2A upgrade |

## Key Resources

- **Full Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **MCP Client**: `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py`

## Weekly Meetings

Research and Showcase meetings every **Wednesday at 10:00 PM PKT** on Zoom.
