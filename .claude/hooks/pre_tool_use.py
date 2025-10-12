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


def is_dangerous_chained_command(command):
    """
    Detect dangerous commands that use chaining to bypass protections.
    Looks for command separators (&&, ||, ;, |) combined with rm.
    """
    normalized = ' '.join(command.lower().split())

    # Check for chained commands with rm
    chain_patterns = [
        r'&&\s*rm\s+.*-[a-z]*r',  # && rm -r
        r'\|\|\s*rm\s+.*-[a-z]*r',  # || rm -r
        r';\s*rm\s+.*-[a-z]*r',  # ; rm -r
    ]

    for pattern in chain_patterns:
        if re.search(pattern, normalized):
            return True

    return False


def is_alternative_deletion_method(command):
    """
    Detect alternative file deletion methods that bypass rm checks.
    """
    normalized = ' '.join(command.lower().split())

    # Alternative deletion patterns
    alt_patterns = [
        r'\bfind\b.*-delete',  # find . -delete
        r'\bfind\b.*-exec\s+rm',  # find . -exec rm
        r'\bxargs\s+rm',  # ... | xargs rm
        r'\bperl\s+-e.*rm\s+.*-r',  # perl -e 'system("rm -rf")'
        r'\bpython\s+-c.*rm\s+.*-r',  # python -c with rm
        r'\bruby\s+-e.*rm\s+.*-r',  # ruby -e with rm
        r'\bnode\s+-e.*rm\s+.*-r',  # node -e with rm
        r'\beval.*rm\s+.*-r',  # eval "rm -rf"
    ]

    for pattern in alt_patterns:
        if re.search(pattern, normalized):
            return True

    return False


def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    Enhanced to catch all .env variants (.env.local, .env.production, etc.)
    and additional access methods (editors, encoding tools, streaming, scripting).
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            # Block all .env variants except .env.sample and .env.example
            if re.search(r'\.env(?!\.sample|\.example)', file_path):
                return True

        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')

            # Enhanced patterns to catch all .env variants and access methods
            env_patterns = [
                # Basic .env access (all variants except .sample/.example)
                r'\.env[^\s/]*(?!\.sample|\.example)\b',

                # Read commands
                r'(cat|less|more|head|tail|grep|awk|sed)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Editor commands
                r'(vim|vi|nano|emacs|code|subl|atom)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Encoding/streaming commands
                r'(base64|xxd|od|strings|hexdump)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Write/modify commands
                r'(echo|printf|tee)\s+.*>\s*[^\s]*\.env(?!\.sample|\.example)',
                r'(touch|cp|mv)\s+.*\.env(?!\.sample|\.example)',

                # Scripting languages
                r'(python|ruby|perl|node|php)\s+.*["\'].*\.env(?!\.sample|\.example)',

                # Other access methods
                r'(curl|wget)\s+.*-o\s+[^\s]*\.env(?!\.sample|\.example)',
                r'(zip|tar|gzip)\s+.*\.env(?!\.sample|\.example)',
            ]

            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True

    return False


def main():
    """
    Hook logic with safety protections.

    Protections:
    - Block dangerous rm -rf commands (direct, chained, and alternative methods)
    - Block .env file access (all variants except .env.sample/.env.example)
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Protection 1: Block .env file access (enhanced for all variants)
        if is_env_file_access(tool_name, tool_input):
            print("BLOCKED: Access to .env files is prohibited", file=sys.stderr)
            print("Use .env.sample or .env.example for template files.", file=sys.stderr)
            sys.exit(2)

        # Protection 2: Block dangerous deletion commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")

            # Check direct rm commands
            if is_dangerous_rm_command(command):
                print("BLOCKED: Dangerous rm command detected", file=sys.stderr)
                print("This command could delete critical system files or directories.", file=sys.stderr)
                sys.exit(2)

            # Check chained commands
            if is_dangerous_chained_command(command):
                print("BLOCKED: Dangerous chained command detected", file=sys.stderr)
                print("Command chaining with rm -r is not allowed.", file=sys.stderr)
                sys.exit(2)

            # Check alternative deletion methods
            if is_alternative_deletion_method(command):
                print("BLOCKED: Alternative deletion method detected", file=sys.stderr)
                print("Using find -delete, xargs rm, or embedded rm commands is not allowed.", file=sys.stderr)
                sys.exit(2)

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
