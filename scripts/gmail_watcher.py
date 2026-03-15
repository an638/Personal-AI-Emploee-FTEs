#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new messages requiring action.

This watcher uses the Gmail API to check for unread messages and creates
action files in the Obsidian vault for Claude Code to process.

Setup Requirements:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json to this scripts directory
4. Run once interactively to authorize

Usage:
    python gmail_watcher.py --vault /path/to/vault --interval 120
"""

import argparse
import os
import pickle
from datetime import datetime
from pathlib import Path
from base_watcher import BaseWatcher
from email import message_from_string
from email.header import decode_header


# Try to import Google libraries, provide helpful error if missing
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """Watcher for Gmail messages requiring action."""

    # Scopes required for Gmail API access
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    # Keywords that indicate a message needs action
    ACTION_KEYWORDS = [
        'urgent', 'asap', 'invoice', 'payment', 'help',
        'request', 'question', 'reply', 'respond',
        'action required', 'please', 'important'
    ]

    def __init__(self, vault_path: str, credentials_path: str = None,
                 check_interval: int = 120):
        """
        Initialize Gmail Watcher.

        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail OAuth credentials JSON
            check_interval: Check frequency in seconds
        """
        super().__init__(vault_path, check_interval)

        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries required but not installed")

        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), 'credentials.json'
        )
        self.token_path = os.path.join(
            os.path.dirname(__file__), 'token.pickle'
        )
        self.service = None
        self._connect()

    def _connect(self):
        """Establish connection to Gmail API."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Connected to Gmail API")

    def check_for_updates(self) -> list:
        """
        Check for new unread messages.

        Returns:
            List of message dictionaries
        """
        if not self.service:
            self._connect()

        try:
            # Fetch unread messages from last check
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    message_data = self._get_message_details(msg['id'])
                    if message_data and self._needs_action(message_data):
                        new_messages.append(message_data)
                        self.processed_ids.add(msg['id'])

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            # Try to reconnect on next iteration
            self.service = None
            return []

    def _get_message_details(self, message_id: str) -> dict:
        """Get full message details."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            payload = message.get('payload', {})
            headers = payload.get('headers', [])

            # Extract headers
            email_data = {
                'id': message_id,
                'threadId': message.get('threadId'),
                'from': self._get_header(headers, 'From'),
                'to': self._get_header(headers, 'To'),
                'subject': self._get_header(headers, 'Subject'),
                'date': self._get_header(headers, 'Date'),
                'snippet': message.get('snippet', ''),
            }

            # Get body content
            email_data['body'] = self._get_body(payload)

            # Check for attachments
            email_data['has_attachments'] = self._has_attachments(payload)

            return email_data

        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return None

    def _get_header(self, headers: list, name: str) -> str:
        """Extract a specific header from the message."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''

    def _get_body(self, payload: dict) -> str:
        """Extract the email body from payload."""
        body = ""

        # Try to get body from parts
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'body' in part:
                    data = part['body'].get('data', '')
                    if data:
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break

        # Fallback to main body
        if not body and 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                import base64
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        return body

    def _has_attachments(self, payload: dict) -> bool:
        """Check if message has attachments."""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] not in ['text/plain', 'text/html']:
                    if 'attachmentId' in part.get('body', {}):
                        return True
        return False

    def _needs_action(self, message: dict) -> bool:
        """
        Determine if a message needs action.

        Args:
            message: Message dictionary

        Returns:
            True if message needs action
        """
        # Check subject and snippet for action keywords
        text_to_check = (
            message.get('subject', '').lower() +
            ' ' +
            message.get('snippet', '').lower()
        )

        for keyword in self.ACTION_KEYWORDS:
            if keyword in text_to_check:
                return True

        # Default: all unread messages need action
        return True

    def create_action_file(self, item: dict) -> Path:
        """
        Create action file for Gmail message.

        Args:
            item: Message dictionary

        Returns:
            Path to created file
        """
        # Generate filename
        subject = self.sanitize_filename(item.get('subject', 'No Subject')[:50])
        from_addr = self.sanitize_filename(item.get('from', '').split('<')[-1].strip('>'))
        filename = f"EMAIL_{from_addr}_{subject}_{item['id']}.md"

        filepath = self.needs_action / filename

        # Parse date for display
        try:
            date_obj = datetime.strptime(item['date'][:25], '%a, %d %b %Y %H:%M:%S')
            date_display = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            date_display = item.get('date', 'Unknown')

        # Create action file content
        content = f"""---
type: email
from: {item.get('from', 'Unknown')}
to: {item.get('to', '')}
subject: {item.get('subject', 'No Subject')}
received: {self.get_timestamp()}
original_date: {date_display}
message_id: {item['id']}
thread_id: {item.get('threadId', '')}
priority: normal
status: pending
has_attachments: {str(item.get('has_attachments', False)).lower()}
---

# Email: {item.get('subject', 'No Subject')}

**From:** {item.get('from', 'Unknown')}
**To:** {item.get('to', '')}
**Date:** {date_display}

---

## Message Content

{item.get('body', 'No content available')}

---

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Create follow-up task

---

## Notes

*Processed by Gmail Watcher*
"""

        filepath.write_text(content, encoding='utf-8')
        return filepath


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        required=True,
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )
    parser.add_argument(
        '--credentials', '-c',
        help='Path to Gmail credentials JSON (default: ./credentials.json)'
    )

    args = parser.parse_args()

    try:
        watcher = GmailWatcher(
            vault_path=args.vault,
            credentials_path=args.credentials,
            check_interval=args.interval
        )
        watcher.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTo fix this:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Gmail API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download credentials.json to the scripts directory")
    except ImportError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nGmail Watcher stopped")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == '__main__':
    main()
