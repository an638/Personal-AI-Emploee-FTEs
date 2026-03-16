# AI Employee - Approval Workflow Guide

## Updated Workflow

```
File Dropped → Needs_Action → Orchestrator → Qwen Creates Plan → Pending_Approval → (You Decide) → Approved/Done or Rejected
```

## Commands

### Start the System

**Terminal 1 - File Watcher:**
```bash
py scripts/filesystem_watcher.py --vault AI_Employee_Vault --interval 30
```

**Terminal 2 - Orchestrator:**
```bash
py scripts/orchestrator.py --vault AI_Employee_Vault --interval 30
```

### Manage Approvals

**List pending approvals:**
```bash
py scripts/approve.py -v AI_Employee_Vault --list
```

**Approve a file:**
```bash
py scripts/approve.py -v AI_Employee_Vault --approve FILENAME.md
```

**Reject a file:**
```bash
py scripts/approve.py -v AI_Employee_Vault --reject FILENAME.md
```

---

## Dashboard Features

### Active Tasks Section
- **In Progress:** Shows items being processed
- **Pending Approval:** Shows items awaiting your approval

### Weekly Metrics
| Period | Shows | Status |
|--------|-------|--------|
| Today | Tasks completed today | ✅ Active / ⚪ No tasks |
| This Week | Tasks completed this week (Mon-Sun) | ✅ On Track / ⚪ No tasks |
| This Month | Tasks completed this month | ✅ Productive / ⚪ No tasks |

### Recent Activity
- Last 10 actions logged
- Auto-update timestamps
- Task completion tracking

---

## File Lifecycle

1. **File Dropped** → `Inbox/Drop/`
2. **Watcher Creates** → `Needs_Action/FILE_*.md`
3. **Orchestrator Processes** → Moves to `In_Progress/`
4. **Qwen Creates Plan** → `Plans/Plan_*.md`
5. **File Moves to** → `Pending_Approval/` ⏳
6. **You Review** → Check plan and details
7. **You Approve** → File moves to `Done/` ✅
8. **Or You Reject** → File moves to `Rejected/` ❌

---

## Example Session

### 1. Start System
```bash
# Terminal 1
py scripts/filesystem_watcher.py -v AI_Employee_Vault -i 30

# Terminal 2
py scripts/orchestrator.py -v AI_Employee_Vault -i 30
```

### 2. Drop a File
```bash
echo "Process this invoice" > AI_Employee_Vault\Inbox\Drop\invoice.txt
```

### 3. Wait for Processing
- Watcher detects file (30 seconds)
- Orchestrator processes file (30 seconds)
- Qwen creates plan (~30-60 seconds)
- File moves to `Pending_Approval/`

### 4. Check Pending
```bash
py scripts/approve.py -v AI_Employee_Vault --list
```

### 5. Review in Obsidian
- Open `AI_Employee_Vault/Pending_Approval/FILE_*.md`
- Read the plan in `Plans/`
- Check Dashboard for metrics

### 6. Approve or Reject
```bash
# Approve
py scripts/approve.py -v AI_Employee_Vault --approve FILE_invoice.txt.md

# Or reject
py scripts/approve.py -v AI_Employee_Vault --reject FILE_invoice.txt.md
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `py scripts/filesystem_watcher.py -v AI_Employee_Vault -i 30` | Start file watcher |
| `py scripts/orchestrator.py -v AI_Employee_Vault -i 30` | Start orchestrator |
| `py scripts/approve.py -v AI_Employee_Vault --list` | List pending |
| `py scripts/approve.py -v AI_Employee_Vault --approve FILE.md` | Approve file |
| `py scripts/approve.py -v AI_Employee_Vault --reject FILE.md` | Reject file |

---

## Folders

| Folder | Purpose |
|--------|---------|
| `Inbox/Drop/` | Drop files here |
| `Needs_Action/` | Waiting to be processed |
| `In_Progress/` | Currently being processed |
| `Plans/` | Qwen's created plans |
| `Pending_Approval/` | Awaiting your decision |
| `Approved/` | Approved (temp) |
| `Done/` | Completed tasks |
| `Rejected/` | Rejected tasks |
| `Logs/` | System logs |

---

## Dashboard Updates

The Dashboard automatically updates every processing cycle with:
- ✅ Pending approval count
- ✅ Weekly metrics (today/week/month)
- ✅ Recent activity (last 10 items)
- ✅ System status (watcher/orchestrator running)

---

*Created: 2026-03-16*
*AI Employee v0.1 - Approval Workflow*
