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


def is_dangerous_git_command(command):
    """
    Protect against dangerous git operations that could cause data loss or
    break collaboration workflows.
    """
    normalized = ' '.join(command.lower().split())

    # Dangerous git patterns
    git_patterns = [
        r'\bgit\s+push\s+.*--force',            # Force push (breaks others' work)
        r'\bgit\s+push\s+.*-f\b',               # Force push shorthand
        r'\bgit\s+reset\s+.*--hard',            # Hard reset (loses work)
        r'\bgit\s+clean\s+.*-[dfx]',            # Clean with force (deletes files)
        r'\bgit\s+branch\s+.*-D',               # Force delete branch
        r'\bgit\s+config\s+--global',           # Global config changes (system-wide)
        r'\bgit\s+config\s+--system',           # System config changes
        r'\bgit\s+filter-branch',               # Rewrite history (dangerous)
        r'\bgit\s+filter-repo',                 # Rewrite history (modern)
        r'\bgit\s+rebase\s+.*-i',               # Interactive rebase (requires terminal input)
        r'\bgit\s+reflog\s+expire',             # Expire reflog (loses recovery points)
        r'\bgit\s+gc\s+.*--prune=now',          # Aggressive garbage collection
        r'\bgit\s+remote\s+remove\s+origin',    # Remove origin remote
        r'\bgit\s+remote\s+rm\s+origin',        # Remove origin remote (alias)
    ]

    for pattern in git_patterns:
        if re.search(pattern, normalized):
            return True

    return False


def is_dangerous_permission_change(command):
    """
    Detect dangerous permission changes.
    Allows chmod +x for making scripts executable (common development need).
    Blocks other dangerous permission patterns including setuid/setgid.
    """
    normalized = ' '.join(command.lower().split())

    # Allow chmod +x for making scripts executable (common and safe)
    if re.search(r'\bchmod\s+\+x\b', normalized):
        return False

    # Block dangerous permission patterns
    perm_patterns = [
        r'\bchmod\s+777',                       # World-writable (major security risk)
        r'\bchmod\s+.*-R\s+777',                # Recursive 777
        r'\bchmod\s+.*a\+rwx',                  # All read/write/execute
        r'\bchmod\s+.*o\+w',                    # Others can write
        r'\bchmod\s+.*-R.*[67][67][67]',        # Recursive permissive modes
        r'\bchmod\s+[0-7]*[4567][0-7]{3}\b',    # Setuid/setgid bit (4000, 6755, etc.)
        r'\bchmod\s+.*[ug]\+s',                 # Setuid/setgid symbolic (u+s, g+s)
        r'\bchown\s+.*-R\s+root',               # Recursive root ownership
        r'\bchown\s+.*-R\s+.*:.*',              # Recursive ownership change (risky)
        r'\bsudo\s+chmod\s+(?!\+x)',            # Sudo chmod (except +x)
        r'\bsudo\s+chown',                      # Sudo chown (system changes)
    ]

    for pattern in perm_patterns:
        if re.search(pattern, normalized):
            return True

    return False


def is_unauthorized_brew_command(command):
    """
    Block Homebrew commands to prevent unauthorized system-level package installation.
    """
    normalized = ' '.join(command.lower().split())

    brew_patterns = [
        r'\bbrew\s+install',                    # Install packages
        r'\bbrew\s+uninstall',                  # Uninstall packages
        r'\bbrew\s+reinstall',                  # Reinstall packages
        r'\bbrew\s+upgrade',                    # Upgrade packages
        r'\bbrew\s+tap',                        # Add repositories
        r'\bbrew\s+untap',                      # Remove repositories
        r'\bbrew\s+link',                       # Link packages
        r'\bbrew\s+unlink',                     # Unlink packages
    ]

    for pattern in brew_patterns:
        if re.search(pattern, normalized):
            return True

    return False


def is_credential_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access credential files containing sensitive data.

    Protected files:
    - .env* files (all variants except .env.sample/.env.example)
    - client_secret.json (Google OAuth credentials)
    - .credentials.json (alternative credential storage)
    - token.pickle (pickled authentication tokens)

    Enhanced to catch all access methods (editors, encoding tools, streaming, scripting).
    Case-insensitive matching to prevent bypasses.
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '').lower()

            # Block all .env variants except .env.sample and .env.example (case-insensitive)
            if re.search(r'\.env(?!\.sample|\.example)', file_path):
                return True

            # Block JSON and pickle credential files (case-insensitive)
            credential_files = [
                r'client_secret\.json',
                r'\.credentials\.json',
                r'token\.pickle',
            ]

            for pattern in credential_files:
                if re.search(pattern, file_path):
                    return True

        # Check bash commands for credential file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '').lower()

            # Only block actual file access commands, not mentions in strings
            # Enhanced patterns to catch .env file access
            env_patterns = [
                # Read commands - must have command + path pattern
                # Note: grep can have args before filename, so handle separately
                r'(cat|less|more|head|tail|awk|sed)\s+[^\s]*\.env(?!\.sample|\.example)',
                r'\bgrep\s+.*\.env(?!\.sample|\.example)',  # grep with any args

                # Editor commands - must be followed by filename
                r'(vim|vi|nano|emacs|code|subl|atom)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Encoding/streaming commands - must be followed by filename
                r'(base64|xxd|od|strings|hexdump)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Write/modify commands - must be targeting .env file
                r'(echo|printf|tee)\s+.*>\s*[^\s]*\.env(?!\.sample|\.example)',
                r'(touch|cp|mv)\s+[^\s]+\s+[^\s]*\.env(?!\.sample|\.example)',

                # Source command - loads env vars
                r'\bsource\s+[^\s]*\.env(?!\.sample|\.example)',
                r'\.\s+[^\s]*\.env(?!\.sample|\.example)',  # . command (source alias)

                # Scripting languages accessing file
                r'(python|ruby|perl|node|php)\s+[^\s]*\.env(?!\.sample|\.example)',

                # Other file operations
                r'(curl|wget)\s+.*-o\s*[^\s]*\.env(?!\.sample|\.example)',
                r'(zip|tar|gzip|bzip2)\s+[^\s]+\s+[^\s]*\.env(?!\.sample|\.example)',
            ]

            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True

            # Patterns for JSON/pickle credential files (case-insensitive)
            credential_file_patterns = [
                # Direct access
                r'client_secret\.json',
                r'\.credentials\.json',
                r'token\.pickle',

                # With commands
                r'(cat|less|more|head|tail|grep|jq|json_pp)\s+.*client_secret\.json',
                r'(cat|less|more|head|tail|grep)\s+.*\.credentials\.json',
                r'(cat|less|more|head|tail|grep)\s+.*token\.pickle',

                # Editors
                r'(vim|vi|nano|emacs|code)\s+.*client_secret\.json',
                r'(vim|vi|nano|emacs|code)\s+.*\.credentials\.json',

                # Modifications
                r'>\s*client_secret\.json',
                r'>\s*\.credentials\.json',
                r'>\s*token\.pickle',
                r'(rm|mv|cp)\s+.*client_secret\.json',
                r'(rm|mv|cp)\s+.*\.credentials\.json',
                r'(rm|mv|cp)\s+.*token\.pickle',
            ]

            for pattern in credential_file_patterns:
                if re.search(pattern, command):
                    return True

    return False


def main():
    """
    Hook logic with safety protections.

    Protections:
    - Block credential file access (.env*, client_secret.json, .credentials.json, token.pickle)
    - Block dangerous rm -rf commands (direct, chained, and alternative methods)
    - Block dangerous git operations (force push, config changes, history rewriting)
    - Block dangerous permission changes (allow chmod +x, block chmod 777 etc)
    - Block unauthorized brew commands (install, uninstall, upgrade, tap)
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Protection 1: Block credential file access
        if is_credential_file_access(tool_name, tool_input):
            print("BLOCKED: Access to credential files is prohibited", file=sys.stderr)
            print("Protected files: .env*, client_secret.json, .credentials.json, token.pickle", file=sys.stderr)
            print("Use .env.sample or .env.example for template files.", file=sys.stderr)
            sys.exit(2)

        # Protection 2-6: Block dangerous bash commands
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

            # Check git operations
            if is_dangerous_git_command(command):
                print("BLOCKED: Dangerous git operation detected", file=sys.stderr)
                print("Operations like force push, hard reset, and global config changes are not allowed.", file=sys.stderr)
                print("If you need to perform this operation, run it manually outside of Claude Code.", file=sys.stderr)
                sys.exit(2)

            # Check permission changes
            if is_dangerous_permission_change(command):
                print("BLOCKED: Dangerous permission change detected", file=sys.stderr)
                print("Commands like chmod 777, setuid/setgid, and recursive chown are not allowed.", file=sys.stderr)
                print("Note: chmod +x is allowed for making scripts executable.", file=sys.stderr)
                sys.exit(2)

            # Check brew commands
            if is_unauthorized_brew_command(command):
                print("BLOCKED: Unauthorized brew command detected", file=sys.stderr)
                print("Package installation and system changes via brew are not allowed.", file=sys.stderr)
                print("Please install packages manually or add them to your project dependencies.", file=sys.stderr)
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
