# AI Employee Vault - Bronze Tier

A local-first, agent-driven personal AI employee system built with Qwen Code and Obsidian.

## Quick Start

### Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | AI reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers (optional) |

### Installation

1. **Clone or download** this vault to your local machine

2. **Install Python dependencies:**
   ```bash
   pip install watchdog google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Verify Qwen Code installation:**
   ```bash
   qwen --version
   ```

4. **Open the vault in Obsidian:**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select the `AI_Employee_Vault` folder

### Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Main dashboard (open in Obsidian)
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 objectives and tracking
├── Templates/                # Action file templates
│   ├── Email_Action_Template.md
│   ├── Approval_Request_Template.md
│   ├── Plan_Template.md
│   ├── WhatsApp_Action_Template.md
│   └── File_Drop_Template.md
├── Inbox/                    # Incoming items
│   └── Drop/                 # Drop folder for files
├── Needs_Action/             # Items awaiting processing
├── In_Progress/              # Items being processed
├── Plans/                    # Claude's action plans
├── Pending_Approval/         # Awaiting your approval
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed items
├── Logs/                     # System logs
├── Accounting/               # Financial records
├── Invoices/                 # Generated invoices
└── Files/                    # Processed file copies
```

## Running the System

### Option 1: Run Individual Watchers

**Gmail Watcher** (requires Gmail API setup):
```bash
cd scripts
python gmail_watcher.py --vault /path/to/AI_Employee_Vault --interval 120
```

**File System Watcher:**
```bash
cd scripts
python filesystem_watcher.py --vault /path/to/AI_Employee_Vault --interval 60
```

**Orchestrator:**
```bash
cd scripts
python orchestrator.py --vault /path/to/AI_Employee_Vault --interval 60
```

### Option 2: Run All Together (Recommended)

Create a startup script or use separate terminal windows:

**Terminal 1 - Gmail Watcher:**
```bash
python scripts/gmail_watcher.py -v AI_Employee_Vault -i 120
```

**Terminal 2 - File Watcher:**
```bash
python scripts/filesystem_watcher.py -v AI_Employee_Vault -i 60
```

**Terminal 3 - Orchestrator:**
```bash
python scripts/orchestrator.py -v AI_Employee_Vault -i 60
```

## Gmail API Setup (Optional)

To enable Gmail watching:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**

2. **Create a new project** or select existing

3. **Enable Gmail API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Other"
   - Download the JSON file

5. **Save credentials:**
   - Rename to `credentials.json`
   - Place in `scripts/` folder

6. **First-time authorization:**
   ```bash
   python scripts/gmail_watcher.py -v AI_Employee_Vault
   ```
   - Follow the browser prompt to authorize
   - A `token.pickle` file will be created

## How It Works

### 1. Perception (Watchers)

Watchers monitor external sources and create action files:

- **Gmail Watcher**: Checks for unread emails every 2 minutes
- **File Watcher**: Monitors the `Inbox/Drop` folder for new files
- **WhatsApp Watcher**: (Coming in Silver tier) Uses Playwright for WhatsApp Web

### 2. Reasoning (Qwen Code)

The Orchestrator triggers Qwen Code to:
- Read action files in `Needs_Action/`
- Check `Company_Handbook.md` for rules
- Create plans in `Plans/`
- Request approvals when needed

### 3. Action (Human-in-the-Loop)

For sensitive actions:
1. Claude creates approval request in `Pending_Approval/`
2. You review and move to `Approved/` or `Rejected/`
3. If approved, action is executed

### 4. Memory (Obsidian)

All state is stored in Markdown files:
- Dashboard shows real-time status
- Logs track all actions
- Completed items archived in `Done/`

## Usage Examples

### Example 1: Process an Email

1. Gmail Watcher detects new email with "invoice request"
2. Creates `EMAIL_client_invoice_abc123.md` in `Needs_Action/`
3. Orchestrator triggers Qwen to process
4. Qwen creates plan and draft invoice
5. Qwen creates approval request for sending
6. You review and approve
7. Email sent, files moved to `Done/`

### Example 2: Drop a File

1. Save a PDF to `AI_Employee_Vault/Inbox/Drop/`
2. File Watcher detects new file
3. Creates `FILE_document.pdf.md` in `Needs_Action/`
4. Qwen reads and categorizes the document
5. Appropriate action taken based on content

### Example 3: Manual Task

1. Create a new `.md` file in `Needs_Action/`
2. Describe what you need done
3. Orchestrator will process it
4. Qwen creates plan and executes

## Configuration

### Watcher Intervals

| Watcher | Default | Recommended |
|---------|---------|-------------|
| Gmail | 120s | 60-300s |
| File System | 60s | 30-60s |
| Orchestrator | 60s | 30-120s |

### Company Handbook Rules

Edit `Company_Handbook.md` to customize:
- Email response templates
- Payment approval thresholds
- Priority keywords
- Auto-action rules

## Troubleshooting

### "Qwen Code not found"
Make sure Qwen Code is installed and in your PATH.

### "Gmail API credentials not found"
- Ensure `credentials.json` is in `scripts/` folder
- Run Gmail watcher interactively first to authorize

### "Watcher keeps crashing"
- Check logs in `Logs/` folder
- Ensure Python dependencies are installed
- Verify vault path is correct

### "Files not being processed"
- Ensure Orchestrator is running
- Check that files have `.md` extension
- Verify folder permissions

## Bronze Tier Deliverables Checklist

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] Business_Goals.md with objectives
- [x] Gmail Watcher script
- [x] File System Watcher script
- [x] Orchestrator script
- [x] Folder structure (/Inbox, /Needs_Action, /Done, etc.)
- [x] Templates for action files
- [ ] Qwen Code integration (requires Qwen setup)
- [ ] Gmail API authorization (optional)

## Next Steps (Silver Tier)

To upgrade to Silver tier, add:
- [ ] WhatsApp Watcher using Playwright
- [ ] MCP server for sending emails
- [ ] Scheduled tasks (cron/Task Scheduler)
- [ ] Weekly CEO Briefing generation
- [ ] Enhanced approval workflow

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit credentials** - Add `.env`, `credentials.json`, `token.pickle` to `.gitignore`
2. **Use environment variables** for API keys
3. **Review all approvals** before moving to Approved folder
4. **Regular log reviews** to audit AI actions
5. **Start with dry-run mode** when testing new features

## Support

- **Documentation**: See `Company_Handbook.md` for rules
- **Logs**: Check `Logs/` folder for errors
- **Hackathon Guide**: See main `Personal AI Employee Hackathon 0_...md` document

---

*AI Employee v0.1 - Bronze Tier*
*Built with Qwen Code + Obsidian*
