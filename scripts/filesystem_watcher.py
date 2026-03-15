#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files requiring action.

This watcher uses the watchdog library to monitor a folder for new files.
When a file is dropped, it creates an action file in the Obsidian vault
and optionally copies the original file for processing.

Usage:
    python filesystem_watcher.py --vault /path/to/vault --watch /path/to/drop
"""

import argparse
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from base_watcher import BaseWatcher


# Try to import watchdog, provide helpful error if missing
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Watchdog library not installed. Run: pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """Handler for file system events in the drop folder."""

    def __init__(self, watcher):
        """
        Initialize the handler.

        Args:
            watcher: Parent FilesystemWatcher instance
        """
        self.watcher = watcher
        self.logger = watcher.logger

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        source_path = Path(event.src_path)

        # Skip temporary files
        if source_path.name.startswith('~') or source_path.suffix == '.tmp':
            return

        self.logger.info(f"New file detected: {source_path.name}")

        try:
            # Wait a moment for file to be fully written
            import time
            time.sleep(0.5)

            # Process the file
            self.watcher.process_dropped_file(source_path)

        except Exception as e:
            self.logger.error(f"Error processing dropped file: {e}")


class FilesystemWatcher(BaseWatcher):
    """Watcher for files dropped into a monitored folder."""

    # File types that need action
    ACTION_EXTENSIONS = {
        '.txt', '.md', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.csv', '.json', '.xml'
    }

    def __init__(self, vault_path: str, watch_path: str = None,
                 check_interval: int = 60):
        """
        Initialize Filesystem Watcher.

        Args:
            vault_path: Path to Obsidian vault
            watch_path: Path to folder to monitor (default: vault/Inbox/Drop)
            check_interval: Check frequency in seconds
        """
        super().__init__(vault_path, check_interval)

        # Set up watch folder
        if watch_path:
            self.watch_path = Path(watch_path)
        else:
            self.watch_path = self.inbox / 'Drop'

        self.watch_path.mkdir(parents=True, exist_ok=True)

        # Track processed files by hash
        self.processed_hashes: set = set()

        # Set up observer if watchdog is available
        if WATCHDOG_AVAILABLE:
            self.observer = Observer()
            self.handler = DropFolderHandler(self)
            self.observer.schedule(self.handler, str(self.watch_path), recursive=False)
        else:
            self.observer = None
            self.handler = None

    def check_for_updates(self) -> list:
        """
        Check for files in watch folder (fallback if watchdog not available).

        Returns:
            List of file paths to process
        """
        if not self.watch_path.exists():
            return []

        files = []
        for file_path in self.watch_path.iterdir():
            if file_path.is_file() and file_path not in self.processed_ids:
                files.append(file_path)

        return files

    def process_dropped_file(self, file_path: Path):
        """
        Process a file that was dropped into the watch folder.

        Args:
            file_path: Path to the dropped file
        """
        # Calculate file hash to track processing
        file_hash = self._calculate_hash(file_path)

        if file_hash in self.processed_hashes:
            self.logger.info(f"File already processed: {file_path.name}")
            return

        # Create action file
        action_file = self.create_action_file(file_path)

        # Mark as processed
        self.processed_hashes.add(file_hash)
        self.processed_ids.add(file_path)

        self.logger.info(f"Processed file: {file_path.name} -> {action_file.name}")

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_action_file(self, file_path: Path) -> Path:
        """
        Create action file for dropped file.

        Args:
            file_path: Path to the dropped file

        Returns:
            Path to created action file
        """
        # Generate filename
        filename = self.sanitize_filename(file_path.name)
        action_filename = f"FILE_{filename}.md"

        filepath = self.needs_action / action_filename

        # Get file info
        stat = file_path.stat()
        size_kb = stat.st_size / 1024

        # Copy file to vault for reference
        files_dir = self.vault_path / 'Files'
        files_dir.mkdir(parents=True, exist_ok=True)
        dest_path = files_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        shutil.copy2(file_path, dest_path)

        # Determine file type and suggested actions
        suggested_actions = self._get_suggested_actions(file_path.suffix)

        # Create action file content
        content = f"""---
type: file_drop
original_name: {filename}
original_path: {str(file_path)}
vault_path: {str(dest_path)}
size_kb: {size_kb:.1f}
extension: {file_path.suffix}
received: {self.get_timestamp()}
status: pending
---

# File Dropped for Processing

**Original File:** `{filename}`
**Size:** {size_kb:.1f} KB
**Received:** {self.get_timestamp()}

**Vault Copy:** `{dest_path.name}`

---

## File Type Analysis

{self._analyze_file_type(file_path.suffix)}

---

## Suggested Actions

{suggested_actions}

---

## Notes

*Add any context or instructions for processing this file*

---

*Processed by File System Watcher*
"""

        filepath.write_text(content, encoding='utf-8')
        return filepath

    def _analyze_file_type(self, extension: str) -> str:
        """Provide analysis based on file type."""
        analyses = {
            '.pdf': 'PDF document - may contain invoices, contracts, or reports',
            '.doc': 'Word document - likely a letter, contract, or document',
            '.docx': 'Word document - likely a letter, contract, or document',
            '.xls': 'Excel spreadsheet - likely contains financial data or lists',
            '.xlsx': 'Excel spreadsheet - likely contains financial data or lists',
            '.csv': 'CSV data file - likely contains structured data for import',
            '.txt': 'Plain text file - may contain notes, data, or instructions',
            '.md': 'Markdown file - may contain notes or documentation',
            '.json': 'JSON data file - likely contains structured data',
            '.xml': 'XML data file - likely contains structured data',
        }
        return analyses.get(extension.lower(), 'Unknown file type - manual review required')

    def _get_suggested_actions(self, extension: str) -> str:
        """Get suggested actions based on file type."""
        actions = {
            '.pdf': [
                '- [ ] Review document content',
                '- [ ] Extract key information',
                '- [ ] Archive to appropriate folder',
                '- [ ] Create follow-up tasks if needed',
            ],
            '.doc': [
                '- [ ] Review document content',
                '- [ ] Extract action items',
                '- [ ] Respond if response required',
            ],
            '.docx': [
                '- [ ] Review document content',
                '- [ ] Extract action items',
                '- [ ] Respond if response required',
            ],
            '.xls': [
                '- [ ] Review spreadsheet data',
                '- [ ] Import to accounting system if financial',
                '- [ ] Archive after processing',
            ],
            '.xlsx': [
                '- [ ] Review spreadsheet data',
                '- [ ] Import to accounting system if financial',
                '- [ ] Archive after processing',
            ],
            '.csv': [
                '- [ ] Review data structure',
                '- [ ] Import to relevant system',
                '- [ ] Archive after processing',
            ],
            '.txt': [
                '- [ ] Read and understand content',
                '- [ ] Take appropriate action',
            ],
            '.md': [
                '- [ ] Read and understand content',
                '- [ ] Integrate with vault if relevant',
            ],
            '.json': [
                '- [ ] Parse and review data',
                '- [ ] Import or process as needed',
            ],
            '.xml': [
                '- [ ] Parse and review data',
                '- [ ] Import or process as needed',
            ],
        }

        default_actions = [
            '- [ ] Review file content',
            '- [ ] Determine required action',
            '- [ ] Process and archive',
        ]

        action_list = actions.get(extension.lower(), default_actions)
        return '\n'.join(action_list)

    def run(self):
        """Main watcher loop with watchdog support."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Watch path: {self.watch_path}')

        if WATCHDOG_AVAILABLE and self.observer:
            self.logger.info('Using watchdog for real-time monitoring')
            self.observer.start()
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                self.observer.stop()
                self.logger.info('File System Watcher stopped by user')
            self.observer.join()
        else:
            self.logger.info('Watchdog not available, using polling mode')
            super().run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        required=True,
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--watch', '-w',
        help='Path to folder to monitor (default: vault/Inbox/Drop)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    try:
        watcher = FilesystemWatcher(
            vault_path=args.vault,
            watch_path=args.watch,
            check_interval=args.interval
        )
        watcher.run()
    except KeyboardInterrupt:
        print("\nFile System Watcher stopped")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == '__main__':
    main()
