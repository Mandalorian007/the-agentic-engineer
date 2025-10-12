#!/usr/bin/env python3
"""
PostToolUse Hook

Executed after Claude Code uses any tool.

Input: JSON via stdin with structure:
{
  "tool_name": "Bash",
  "tool_input": { "command": "ls -la" },
  "tool_result": { "output": "..." },
  "message_id": "msg_123",
  ...
}

Return codes:
- 0: Success
- non-zero: Error (logged but doesn't affect tool execution)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Log tool results
    - Update metrics
    - Trigger notifications
    - Analyze tool outputs
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        tool_result = input_data.get("tool_result", {})
        message_id = input_data.get("message_id", "")

        # Placeholder: Add your post-tool logic here
        # Example:
        # if tool_name == "Bash":
        #     log_bash_command(tool_input.get("command"), tool_result)

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
