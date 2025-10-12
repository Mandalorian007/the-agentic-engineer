#!/usr/bin/env python3
"""
PreToolUse Hook

Executed before Claude Code uses any tool.

Input: JSON via stdin with structure:
{
  "tool_name": "Bash",
  "tool_input": { "command": "ls -la" },
  "message_id": "msg_123",
  ...
}

Return codes:
- 0: Continue with tool execution
- 2: Block tool execution (shows error to Claude)
"""

import sys
import json
import re


def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())

    # Pattern 1: Standard rm -rf variations
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',  # rm --recursive --force
        r'\brm\s+--force\s+--recursive',  # rm --force --recursive
        r'\brm\s+-r\s+.*-f',  # rm -r ... -f
        r'\brm\s+-f\s+.*-r',  # rm -f ... -r
    ]

    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True

    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*',       # Current directory at end of command
    ]

    if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True

    return False


def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            if '.env' in file_path and not file_path.endswith('.env.sample'):
                return True

        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Pattern to detect .env file access (but allow .env.sample)
            env_patterns = [
                r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
                r'cat\s+.*\.env\b(?!\.sample)',  # cat .env
                r'echo\s+.*>\s*\.env\b(?!\.sample)',  # echo > .env
                r'touch\s+.*\.env\b(?!\.sample)',  # touch .env
                r'cp\s+.*\.env\b(?!\.sample)',  # cp .env
                r'mv\s+.*\.env\b(?!\.sample)',  # mv .env
            ]

            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True

    return False


def main():
    """
    Hook logic with safety protections.

    Protections:
    - Block dangerous rm -rf commands
    - Block .env file access (allows .env.sample)
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Protection 1: Block .env file access
        if is_env_file_access(tool_name, tool_input):
            print("BLOCKED: Access to .env files is prohibited", file=sys.stderr)
            print("Use .env.sample for template files.", file=sys.stderr)
            sys.exit(2)

        # Protection 2: Block dangerous rm commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_rm_command(command):
                print("BLOCKED: Dangerous rm command detected", file=sys.stderr)
                print("This command could delete critical system files or directories.", file=sys.stderr)
                sys.exit(2)

        # Placeholder: Add additional custom validation logic here
        # Example:
        # if some_custom_check(tool_name, tool_input):
        #     print("BLOCKED: Custom validation failed", file=sys.stderr)
        #     sys.exit(2)

        # Allow tool execution
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
