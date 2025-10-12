#!/usr/bin/env python3
"""
SubagentStop Hook

Executed when a Claude Code subagent stops (after using Task tool).

Input: JSON via stdin with structure:
{
  "subagent_type": "general-purpose",
  "subagent_result": "...",
  "message_id": "msg_123",
  ...
}

Return codes:
- 0: Success
- non-zero: Error (logged but doesn't affect subagent behavior)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Log subagent execution results
    - Aggregate subagent metrics
    - Track subagent performance
    - Notify on subagent completion
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        subagent_type = input_data.get("subagent_type", "unknown")
        subagent_result = input_data.get("subagent_result", "")
        message_id = input_data.get("message_id", "")

        # Placeholder: Add your subagent stop logic here
        # Example:
        # if subagent_type == "code-reviewer":
        #     log_review_results(subagent_result)

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
