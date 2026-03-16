# Personal AI Employee - Bronze Tier

A local-first, agent-driven personal AI employee system built with **Qwen Code** and **Obsidian**.

## Features

- **File Watcher**: Monitors `Inbox/Drop/` for new files
- **Orchestrator**: Processes action files with Qwen Code
- **Approval Workflow**: Files wait in `Pending_Approval/` until you approve
- **Dashboard**: Real-time metrics in Obsidian

## Quick Start

### Prerequisites

- Python 3.13+
- Qwen Code (`npm install -g @qwen-code/qwen-code`)
- Obsidian (optional, for viewing Dashboard)

### Installation

```bash
pip install -r scripts/requirements.txt
```

### Run the System

**Terminal 1 - File Watcher:**
```bash
py scripts/filesystem_watcher.py --vault AI_Employee_Vault --interval 30
```

**Terminal 2 - Orchestrator:**
```bash
py scripts/orchestrator.py --vault AI_Employee_Vault --interval 30
```

### Manage Approvals

```bash
# List pending
py scripts/approve.py -v AI_Employee_Vault --list

# Approve a file
py scripts/approve.py -v AI_Employee_Vault --approve FILENAME.md

# Reject a file
py scripts/approve.py -v AI_Employee_Vault --reject FILENAME.md
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status (open in Obsidian)
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 objectives
├── Inbox/Drop/               # Drop files here
├── Needs_Action/             # Waiting to process
├── In_Progress/              # Currently processing
├── Plans/                    # Qwen's created plans
├── Pending_Approval/         # Awaiting your approval
├── Approved/                 # Approved (temp)
├── Done/                     # Completed tasks
├── Rejected/                 # Rejected tasks
└── Logs/                     # System logs
```

## How It Works

1. **Drop a file** in `AI_Employee_Vault/Inbox/Drop/`
2. **Watcher detects** it and creates action file in `Needs_Action/`
3. **Orchestrator processes** it with Qwen Code
4. **Qwen creates plan** in `Plans/`
5. **File moves to** `Pending_Approval/` (waits for you)
6. **You approve** via command → moves to `Done/`

## Dashboard Features

- **Task Summary**: Counts for each folder
- **Weekly Metrics**: Tasks completed Today/Week/Month
- **AI Assistant Status**: Watcher/Orchestrator running status
- **Recent Activity**: Last 5 completed tasks

## Documentation

- [APPROVAL_WORKFLOW_GUIDE.md](APPROVAL_WORKFLOW_GUIDE.md) - Approval workflow guide
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Dashboard features guide

## Hackathon Tier

**Bronze Tier Complete:**
- ✅ Obsidian vault with Dashboard
- ✅ Company Handbook
- ✅ Business Goals
- ✅ File System Watcher
- ✅ Orchestrator with Qwen Code
- ✅ Approval workflow
- ✅ Auto-updating Dashboard

## Security Notes

- Never commit `credentials.json` or `.env` files
- Review all approvals before executing
- Check logs regularly for audit trail

---

*AI Employee v0.1 - Bronze Tier*
*Built with Qwen Code + Obsidian*
