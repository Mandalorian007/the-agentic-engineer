#!/usr/bin/env python3
"""
UserPromptSubmit Hook

Executed when user submits a prompt to Claude Code.

Input: JSON via stdin with structure:
{
  "session_id": "sess_123",
  "prompt": "User's prompt text",
  ...
}

Return codes:
- 0: Continue with prompt
- 2: Block prompt (shows error to user)
"""

import sys
import json


def main():
    """
    Hook logic goes here.

    Example use cases:
    - Log prompts
    - Validate input
    - Add context
    - Filter content
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "unknown")
        prompt = input_data.get("prompt", "")

        # Placeholder: Add your user prompt submit logic here
        # Example:
        # log_prompt(session_id, prompt)
        # validate_prompt(prompt)

        # You can print additional context that will be added to the prompt
        # Example: print(f"Current time: {datetime.now()}")

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
