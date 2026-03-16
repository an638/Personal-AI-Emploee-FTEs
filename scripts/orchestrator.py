#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for AI Employee.

The Orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending items
3. Manages the approval workflow
4. Updates the Dashboard.md
5. Handles scheduled tasks (daily briefings, weekly audits)

Usage:
    python orchestrator.py --vault /path/to/vault
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List


class Orchestrator:
    """Main orchestrator for AI Employee operations."""

    def __init__(self, vault_path: str, qwen_cmd: str = "qwen"):
        """
        Initialize the Orchestrator.

        Args:
            vault_path: Path to Obsidian vault
            qwen_cmd: Command to invoke Qwen Code
        """
        self.vault_path = Path(vault_path)
        self.qwen_cmd = qwen_cmd
        # Always use 'qwen' directly since it's in PATH (verified by user)
        # Windows npm commands work better without full path in subprocess

        # Define folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.in_progress = self.vault_path / 'In_Progress'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure all folders exist
        for folder in [self.needs_action, self.in_progress, self.plans,
                       self.pending_approval, self.approved, self.rejected,
                       self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Track current processing
        self.current_item: Optional[Path] = None

    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')

    def check_needs_action(self) -> List[Path]:
        """
        Check for items in Needs_Action folder.

        Returns:
            List of files needing action
        """
        if not self.needs_action.exists():
            return []

        files = [f for f in self.needs_action.iterdir() if f.is_file() and f.suffix == '.md']
        return sorted(files, key=lambda f: f.stat().st_mtime)

    def check_pending_approval(self) -> List[Path]:
        """
        Check for items awaiting approval.

        Returns:
            List of files pending approval
        """
        if not self.pending_approval.exists():
            return []

        return [f for f in self.pending_approval.iterdir() if f.is_file() and f.suffix == '.md']

    def check_approved(self) -> List[Path]:
        """
        Check for approved items ready for action.

        Returns:
            List of approved files
        """
        if not self.approved.exists():
            return []

        return [f for f in self.approved.iterdir() if f.is_file() and f.suffix == '.md']

    def process_item(self, file_path: Path) -> bool:
        """
        Process a single item using Qwen Code.

        Args:
            file_path: Path to the action file

        Returns:
            True if processing succeeded
        """
        self.current_item = file_path
        self.logger.info(f"Processing: {file_path.name}")

        try:
            # Move to In_Progress
            in_progress_path = self.in_progress / file_path.name
            shutil.move(str(file_path), str(in_progress_path))

            # Read the file content
            content = in_progress_path.read_text(encoding='utf-8')

            # Create prompt for Qwen
            prompt = self._create_processing_prompt(in_progress_path, content)

            # Invoke Qwen Code
            result = self._invoke_qwen(prompt)

            # Check if Qwen created a plan
            plan_created = self._check_for_plan(in_progress_path.stem)

            if plan_created:
                self.logger.info(f"Plan created for {in_progress_path.name}")
                # Move to Pending_Approval instead of Done
                pending_path = self.pending_approval / file_path.name
                shutil.move(str(in_progress_path), str(pending_path))
                self.logger.info(f"Moved to Pending_Approval: {file_path.name}")
            else:
                self.logger.warning(f"No plan created for {in_progress_path.name}")
                # Move back to Needs_Action if no plan
                shutil.move(str(in_progress_path), str(file_path))

            return True

        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            # Move back to Needs_Action on error
            if self.current_item and self.current_item.exists():
                pass  # Already there or handled
            return False

    def _create_processing_prompt(self, file_path: Path, content: str) -> str:
        """Create a prompt for Qwen Code."""
        return f"""You are processing an action item from the AI Employee system.

**File:** {file_path.name}
**Location:** {file_path.parent}

**Content:**
{content}

---

**Your Task:**
1. Read and understand the action item
2. Check the Company_Handbook.md for relevant rules
3. Create a Plan.md file in the /Plans folder with:
   - Clear objective
   - Step-by-step approach
   - Any approvals needed
   - Checklist of tasks
4. If approval is required, create a file in /Pending_Approval
5. If the task is complete, move the original file to /Done

**Remember:**
- Always follow the Company Handbook rules
- When in doubt, request approval
- Log all actions taken
- Update the Dashboard.md with progress

Start by analyzing the request and creating your plan.
"""

    def _invoke_qwen(self, prompt: str) -> str:
        """
        Invoke Qwen Code with a prompt.

        Args:
            prompt: The prompt to send to Qwen

        Returns:
            Qwen's response
        """
        try:
            # Write prompt to a temp file for debugging
            self.logs.mkdir(parents=True, exist_ok=True)
            debug_prompt = self.logs / 'last_prompt.txt'
            debug_prompt.write_text(prompt, encoding='utf-8')

            # Change to vault directory
            original_dir = os.getcwd()
            os.chdir(self.vault_path)

            # Run Qwen Code using node directly with full path
            self.logger.info(f"Invoking Qwen using node with full path...")
            
            # Full path to qwen cli
            qwen_cli_path = r"C:\Users\DELL\AppData\Roaming\npm\node_modules\@qwen-code\qwen-code\cli.js"
            
            # Write prompt to temp file and pass via stdin redirection
            # This avoids encoding and special character issues
            import tempfile
            temp_file = Path(tempfile.gettempdir()) / f"qwen_prompt_{os.getpid()}.txt"
            temp_file.write_text(prompt, encoding='utf-8')
            
            # Use type command to pipe file content to qwen
            cmd = f'type "{temp_file}" | node "{qwen_cli_path}" -y'
            self.logger.info(f"Running Qwen with file input...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                shell=True,
                env={**os.environ, 'FORCE_COLOR': '0'},
                encoding='utf-8',
                errors='replace'
            )
            
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass

            os.chdir(original_dir)

            # Log output for debugging
            self.logger.info(f"Qwen return code: {result.returncode}")
            if result.stdout:
                self.logger.info(f"Qwen output: {result.stdout[:500]}...")
            if result.stderr:
                self.logger.error(f"Qwen stderr: {result.stderr[:500]}...")

            if result.returncode != 0:
                self.logger.error(f"Qwen error: {result.stderr}")
                return ""

            return result.stdout

        except subprocess.TimeoutExpired:
            self.logger.error("Qwen Code timed out")
            return ""
        except Exception as e:
            self.logger.error(f"Error invoking Qwen: {e}")
            return ""

    def _check_for_plan(self, item_name: str) -> bool:
        """Check if a plan was created for an item."""
        plan_pattern = f"PLAN_{item_name}"
        plans = list(self.plans.glob(f"*{plan_pattern}*.md"))
        return len(plans) > 0

    def process_approved_items(self) -> bool:
        """
        Process items that have been approved.

        Returns:
            True if any items were processed
        """
        approved = self.check_approved()
        if not approved:
            return False

        for item in approved:
            self.logger.info(f"Processing approved item: {item.name}")
            # In full implementation, this would trigger MCP actions
            # For Bronze tier, we just move to Done and log
            self._complete_approved_item(item)

        return True

    def _complete_approved_item(self, item: Path):
        """Mark an approved item as complete."""
        try:
            # Log the completion
            log_entry = {
                'timestamp': self.get_timestamp(),
                'action': 'approved_item_completed',
                'item': item.name,
                'status': 'completed'
            }
            self._log_action(log_entry)

            # Move to Done
            dest = self.done / item.name
            shutil.move(str(item), str(dest))

            self.logger.info(f"Completed: {item.name}")

        except Exception as e:
            self.logger.error(f"Error completing {item.name}: {e}")

    def _get_recent_activities(self, limit: int = 5) -> list:
        """Get recent activities from done folder."""
        done_files = list(self.done.glob('*.md'))
        # Sort by modification time, newest first
        done_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        activities = []
        for f in done_files[:limit]:
            timestamp = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            activities.append({
                'date': timestamp,
                'action': f'Completed: {f.name}',
                'status': '✅'
            })
        return activities

    def _build_dashboard(self, inbox: int, needs: int, in_prog: int, pending: int,
                         pending_items: list, done_today: int, done_week: int,
                         done_month: int, activities: list) -> str:
        """Build complete dashboard from scratch."""
        
        # Build pending items list
        if pending_items:
            pending_list = '\n'.join([f'- [ ] `{item}`' for item in pending_items[:5]])
            pending_section = f"""### Pending Approval
*{pending} items awaiting approval*

{pending_list}"""
        else:
            pending_section = """### Pending Approval
*No items awaiting approval*"""

        # Build activity rows
        if activities:
            activity_rows = '\n'.join([
                f"| {a['date']} | {a['action']} | {a['status']} |"
                for a in activities
            ])
        else:
            activity_rows = "| — | System initialized | ✅ |"

        # Build status
        watcher_status = '🟢 Running' if self._is_process_running('filesystem_watcher') else '🔴 Not running'
        orchestrator_status = '🟢 Running' if self._is_process_running('orchestrator') else '🔴 Not running'

        dashboard = f"""---
last_updated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}
status: active
---

# 📊 AI Employee Dashboard

*Real-time overview of personal and business operations*

---

## 📬 Communication Queue

| Channel | Unread | Urgent | Action Required |
|---------|--------|--------|-----------------|
| Gmail | 0 | 0 | 0 |
| WhatsApp | 0 | 0 | 0 |

---

## 📊 Task Summary

| Location | Count | Description |
|----------|-------|-------------|
| 📥 Inbox | {inbox} | Files waiting to be picked up |
| ⚠️ Needs Action | {needs} | Items requiring processing |
| 🔄 In Progress | {in_prog} | Items being processed by Qwen |
| ⏳ Pending Approval | {pending} | Items awaiting your approval |
| ✅ Done Today | {done_today} | Tasks completed today |
| ✅ Done This Week | {done_week} | Tasks completed this week |

---

## ✅ Active Tasks

### In Progress
*{in_prog} items being processed*

{pending_section}

---

## 📈 Weekly Metrics

| Period | Tasks Completed | Status |
|--------|-----------------|--------|
| **Today** | {done_today} | {'✅ Active' if done_today > 0 else '⚪ No tasks'} |
| **This Week** | {done_week} | {'✅ On Track' if done_week > 0 else '⚪ No tasks'} |
| **This Month** | {done_month} | {'✅ Productive' if done_month > 0 else '⚪ No tasks'} |

---

## 📋 Recent Activity

| Date | Action | Status |
|------|--------|--------|
{activity_rows}

---

## 🤖 AI Assistant Status

| Component | Status | Last Check |
|-----------|--------|------------|
| File Watcher | {watcher_status} | Now |
| Orchestrator | {orchestrator_status} | Now |
| Qwen Code | 🟢 Ready | Available |

---

## 📅 Today's Schedule

*No scheduled items*

---

## ⚡ Quick Actions

- [ ] Sync bank transactions
- [ ] Check email inbox
- [ ] Review pending approvals ({pending} items)
- [ ] Generate weekly briefing

---

*Last generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}*
*AI Employee v0.1 (Bronze Tier)*
"""
        return dashboard

    def update_dashboard(self):
        """Update the Dashboard.md with current status - complete rewrite approach."""
        try:
            # Count files in each folder
            inbox_count = len(list(self.inbox.glob('**/*'))) - len(list(self.inbox.glob('**/Drop/*')))
            needs_action_count = len(self.check_needs_action())
            in_progress_count = len(list(self.in_progress.glob('*.md')))
            pending_approval_count = len(self.check_pending_approval())
            done_today = len([
                f for f in self.done.glob('*.md')
                if datetime.fromtimestamp(f.stat().st_mtime).date() == datetime.now().date()
            ])
            done_this_week = len([
                f for f in self.done.glob('*.md')
                if self._is_this_week(f.stat().st_mtime)
            ])
            done_this_month = len([
                f for f in self.done.glob('*.md')
                if self._is_this_month(f.stat().st_mtime)
            ])

            # Get pending items for display
            pending_items = [f.name for f in self.pending_approval.glob('*.md')]
            
            # Get recent activity from logs
            recent_activities = self._get_recent_activities()

            # Build complete dashboard
            content = self._build_dashboard(
                inbox_count,
                needs_action_count,
                in_progress_count,
                pending_approval_count,
                pending_items,
                done_today,
                done_this_week,
                done_this_month,
                recent_activities
            )

            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info("Dashboard updated (full rewrite)")

        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")

    def _is_this_week(self, timestamp: float) -> bool:
        """Check if timestamp is in current week (Monday-Sunday)."""
        from datetime import date
        dt = datetime.fromtimestamp(timestamp)
        today = date.today()
        # Get Monday of this week
        monday = today - timedelta(days=today.weekday())
        return dt.date() >= monday

    def _is_this_month(self, timestamp: float) -> bool:
        """Check if timestamp is in current month."""
        from datetime import date
        dt = datetime.fromtimestamp(timestamp)
        return dt.month == date.today().month and dt.year == date.today().year

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            result = subprocess.run(
                ['tasklist'],
                capture_output=True,
                text=True,
                shell=True
            )
            return process_name in result.stdout
        except:
            return False

    def _log_action(self, entry: dict):
        """Log an action to the logs folder."""
        log_file = self.logs / f"actions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        import json
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def run_once(self):
        """Run a single processing cycle."""
        self.logger.info("Starting processing cycle")

        # Process needs action
        items = self.check_needs_action()
        for item in items[:5]:  # Limit to 5 items per cycle
            self.process_item(item)

        # Process approved items
        self.process_approved_items()

        # Update dashboard
        self.update_dashboard()

        self.logger.info("Processing cycle complete")

    def run_continuous(self, interval: int = 60):
        """
        Run continuous processing loop.

        Args:
            interval: Seconds between cycles
        """
        import time

        self.logger.info(f"Starting continuous mode (interval: {interval}s)")

        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault', '-v',
        required=True,
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--qwen', '-q',
        default='qwen',
        help='Qwen Code command (default: qwen)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Processing interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )

    args = parser.parse_args()

    try:
        orchestrator = Orchestrator(
            vault_path=args.vault,
            qwen_cmd=args.qwen
        )

        if args.once:
            orchestrator.run_once()
        else:
            orchestrator.run_continuous(interval=args.interval)

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
