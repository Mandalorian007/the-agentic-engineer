#!/usr/bin/env python3
"""
PreCompact Hook

Executed before Claude Code compacts the conversation history (when context limit approached).

Input: JSON via stdin with structure:
{
  "compact_size": 10,
  "message_id": "msg_123",
  ...
}

Return codes:
- 0: Continue with compaction
- 1: Block compaction (use with caution - may cause context errors)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Backup conversation history before compaction
    - Save important messages to external storage
    - Log compaction events
    - Alert when context limit is approached
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        compact_size = input_data.get("compact_size", 0)
        message_id = input_data.get("message_id", "")

        # Placeholder: Add your pre-compact logic here
        # Example:
        # if compact_size > 50:
        #     backup_conversation_history()

        # Allow compaction
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
