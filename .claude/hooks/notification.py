#!/usr/bin/env python3
"""
Notification Hook

Executed when Claude Code wants to send a notification.

Input: JSON via stdin with structure:
{
  "title": "Notification Title",
  "message": "Notification body",
  "level": "info",
  ...
}

Return codes:
- 0: Success
- non-zero: Error (notification won't be sent)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Send to Slack/Discord
    - System notifications
    - Text-to-speech
    - Custom notification services
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        title = input_data.get("title", "")
        message = input_data.get("message", "")
        level = input_data.get("level", "info")

        # Placeholder: Add your notification logic here
        # Example:
        # send_slack_notification(title, message)
        # send_desktop_notification(title, message)

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
