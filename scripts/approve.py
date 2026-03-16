#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approval Helper - Move files from Pending_Approval to Approved or Rejected.

Usage:
    py scripts/approve.py --vault AI_Employee_Vault --approve FILENAME.md
    py scripts/approve.py --vault AI_Employee_Vault --reject FILENAME.md
    py scripts/approve.py --vault AI_Employee_Vault --list
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path


class ApprovalHelper:
    """Helper for managing approvals."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure folders exist
        for folder in [self.approved, self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

    def list_pending(self):
        """List all pending approvals."""
        if not self.pending_approval.exists():
            print("No pending approvals.")
            return

        files = [f for f in self.pending_approval.iterdir() if f.is_file() and f.suffix == '.md']
        
        if not files:
            print("✅ No pending approvals!")
            return

        print(f"\n📋 Pending Approvals ({len(files)} items):\n")
        for f in sorted(files):
            stat = f.stat()
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  📄 {f.name}")
            print(f"     Modified: {modified}")
            print()

    def approve(self, filename: str):
        """Approve a file and move to Done."""
        source = self.pending_approval / filename
        if not source.exists():
            print(f"❌ File not found: {filename}")
            return

        # Move to Approved first, then to Done
        approved_path = self.approved / filename
        shutil.move(str(source), str(approved_path))
        
        # Then move to Done
        done_path = self.done / filename
        shutil.move(str(approved_path), str(done_path))

        # Log the approval
        self._log_approval(filename, 'approved')

        print(f"✅ Approved: {filename}")
        print(f"   Moved to: Done/{filename}")

    def reject(self, filename: str):
        """Reject a file and move to Rejected."""
        source = self.pending_approval / filename
        if not source.exists():
            print(f"❌ File not found: {filename}")
            return

        dest = self.rejected / filename
        shutil.move(str(source), str(dest))

        # Log the rejection
        self._log_approval(filename, 'rejected')

        print(f"❌ Rejected: {filename}")
        print(f"   Moved to: Rejected/{filename}")

    def _log_approval(self, filename: str, action: str):
        """Log approval/rejection action."""
        import json
        log_file = self.logs / f"actions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': f'approval_{action}',
            'file': filename,
            'status': action
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Approval Helper for AI Employee')
    parser.add_argument('--vault', '-v', required=True, help='Path to Obsidian vault')
    parser.add_argument('--list', '-l', action='store_true', help='List pending approvals')
    parser.add_argument('--approve', '-a', help='Approve a file (provide filename)')
    parser.add_argument('--reject', '-r', help='Reject a file (provide filename)')

    args = parser.parse_args()

    helper = ApprovalHelper(args.vault)

    if args.list:
        helper.list_pending()
    elif args.approve:
        helper.approve(args.approve)
    elif args.reject:
        helper.reject(args.reject)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
