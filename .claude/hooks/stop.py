#!/usr/bin/env python3
"""
Stop Hook

Executed when Claude Code stops (chat ends, user cancels, error occurs).

Input: JSON via stdin with structure:
{
  "stop_reason": "user_stop",
  "message_id": "msg_123",
  ...
}

Return codes:
- 0: Success
- non-zero: Error (logged but doesn't affect stop behavior)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Save session state
    - Cleanup resources
    - Log session end
    - Send completion notifications
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        stop_reason = input_data.get("stop_reason", "unknown")
        message_id = input_data.get("message_id", "")

        # Placeholder: Add your stop logic here
        # Example:
        # save_session_state(message_id)
        # announce_completion()
        # cleanup_resources()

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
