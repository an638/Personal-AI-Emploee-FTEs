# 📊 AI Employee Dashboard Guide

## Dashboard Features

The Dashboard has been updated to show comprehensive task tracking with the following sections:

### 1. Task Summary Table

| Location | Count | Description |
|----------|-------|-------------|
| 📥 Inbox | Auto | Files waiting to be picked up |
| ⚠️ Needs Action | Auto | Items requiring processing |
| 🔄 In Progress | Auto | Items being processed by Qwen |
| ⏳ Pending Approval | Auto | Items awaiting your approval |
| ✅ Done Today | Auto | Tasks completed today |
| ✅ Done This Week | Auto | Tasks completed this week |

### 2. Weekly Metrics

Shows tasks completed:
- **Today** - Tasks completed in last 24 hours
- **This Week** - Tasks completed since Monday
- **This Month** - Tasks completed this calendar month

### 3. AI Assistant Status

Real-time status of system components:
- 🟢 Running - Process is active
- 🔴 Not running - Process is stopped

### 4. Recent Activity

Last 5 completed tasks with timestamps.

### 5. Pending Approval List

Shows files waiting for your approval (up to 5 items).

---

## How Dashboard Updates

The dashboard automatically updates every time the Orchestrator runs:

1. **Counts files** in each folder (Inbox, Needs_Action, In_Progress, Pending_Approval, Done)
2. **Calculates metrics** (today/week/month completions)
3. **Reads recent activity** from Done folder
4. **Checks process status** (watcher/orchestrator running?)
5. **Rebuilds entire dashboard** with fresh data

---

## Example Dashboard View

```markdown
## 📊 Task Summary

| Location | Count | Description |
|----------|-------|-------------|
| 📥 Inbox | 1 | Files waiting to be picked up |
| ⚠️ Needs Action | 2 | Items requiring processing |
| 🔄 In Progress | 1 | Items being processed by Qwen |
| ⏳ Pending Approval | 3 | Items awaiting your approval |
| ✅ Done Today | 5 | Tasks completed today |
| ✅ Done This Week | 12 | Tasks completed this week |

## 📈 Weekly Metrics

| Period | Tasks | Status |
|--------|-------|--------|
| Today | 5 | ✅ Active |
| This Week | 12 | ✅ On Track |
| This Month | 45 | ✅ Productive |

## 🤖 AI Assistant Status

| Component | Status |
|-----------|--------|
| File Watcher | 🟢 Running |
| Orchestrator | 🟢 Running |
| Qwen Code | 🟢 Ready |
```

---

## Commands

### View Dashboard
Open in Obsidian: `AI_Employee_Vault/Dashboard.md`

### Manual Refresh
```bash
py scripts/orchestrator.py -v AI_Employee_Vault --once
```

### Start Auto-Update
```bash
py scripts/orchestrator.py -v AI_Employee_Vault --interval 30
```

---

## Folder Counts Explained

| Folder | What It Means |
|--------|---------------|
| **Inbox** | Files dropped but not yet processed by watcher |
| **Needs_Action** | Action files ready for orchestrator |
| **In_Progress** | Files currently being processed |
| **Pending_Approval** | Plans created, waiting for your approval |
| **Done** | Completed and approved tasks |

---

## Status Icons

| Icon | Meaning |
|------|---------|
| 📥 | Inbox |
| ⚠️ | Needs attention |
| 🔄 | Processing |
| ⏳ | Waiting |
| ✅ | Complete |
| 🟢 | Active/Running |
| 🔴 | Stopped/Offline |
| ⚪ | Inactive |

---

*Created: 2026-03-16*
*AI Employee v0.1 - Dashboard Guide*
