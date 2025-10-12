# Taming Claude YOLO: Safety Hooks for --dangerously-skip-permissions

## Hook (Opening)
- "YOLO mode" = Claude Code's slang for `--dangerously-skip-permissions`
- Removes manual approval, enables fast iteration
- Problem: AI can accidentally `cat .env`, `rm -rf`, `git push --force`
- Solution: Pre-tool-use hooks that intercept EVERY operation

## The YOLO Dilemma
**Without --dangerously-skip-permissions:**
- 100+ approval prompts per session
- Unusable for real work

**With --dangerously-skip-permissions:**
- Fast, productive workflow
- Risk of accidental credential leaks
- Risk of destructive commands

**We need both: Speed AND safety**

## Solution: Pre-Tool-Use Hooks

### How It Works
```
User → Claude → Pre-Tool-Use Hook → [Block/Allow] → Tool Execution
```

**Configuration in `.claude/settings.json`:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use.py"
          }
        ]
      }
    ]
  }
}
```

**Hook script**: `.claude/hooks/pre_tool_use.py`
- Input: JSON via stdin with tool name + parameters
- Output: Exit code 0 (allow) or 2 (block with error message)
- Intercepts: Read, Write, Edit, Bash, etc.
- Runs before EVERY tool call (100% coverage)

**Official Documentation**: https://docs.claude.com/en/docs/claude-code/hooks

## Security Principles

### 1. Credential Protection
**Block access to:**
- `.env*` (except `.env.sample`, `.env.example`)
- `client_secret.json`, `.credentials.json`, `token.pickle`

**Catches all methods:**
- Direct: `Read(.env)`, `Edit(.env.local)`
- Bash: `cat .env`, `vim .env`, `base64 .env`
- Bypasses: `.ENV` (case), `.env*` (glob), `source .env`

**Code snippet:** (from pre_tool_use.py:205-305)

### 2. Dangerous Commands
**Blocks:**
- `rm -rf` (all variations + chained)
- `git push --force`, `git reset --hard`, `git config --global`
- `chmod 777`, `chmod u+s` (setuid)
- `brew install` (unauthorized packages)

**Allows:**
- `chmod +x` (make executable)
- Normal git ops, safe file operations

**Code snippet:** (from pre_tool_use.py:25-145)

### 3. Pattern Matching
- Case-insensitive (catches `.ENV`, `.Env`)
- Normalized whitespace (handles weird spacing)
- Regex-based (flexible, comprehensive)
- Detects chaining (`&&`, `||`, `;`)

## Environment Variable Convention

### The .env.mcp Pattern
Separate credentials by purpose:

```
.env.local      # App credentials (Blogger, Cloudinary, OpenAI)
.env.mcp        # MCP server credentials (Perplexity, Firecrawl, YouTube)
.env.sample     # Safe template (commit to git)
```

**Why separate files?**
- Different rotation schedules (MCP keys vs app keys)
- Different access patterns (Claude Code loads MCP, app uses local)
- Explicit about what loads where
- Easier to audit and manage
- Better than one giant .env

**Real example from this project:**

`.env.local` has:
```bash
BLOGGER_CLIENT_ID=xxx
BLOGGER_CLIENT_SECRET=xxx
BLOGGER_REFRESH_TOKEN=xxx
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
OPENAI_API_KEY=xxx
```

`.env.mcp` would have:
```bash
PERPLEXITY_API_KEY=xxx
FIRECRAWL_API_KEY=xxx
YOUTUBE_API_KEY=xxx
```

**How MCP uses these:**
`.mcp.json` references environment variables:
```json
{
  "mcpServers": {
    "perplexity-ask": {
      "command": "npx",
      "args": ["-y", "server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    }
  }
}
```

When you run `claudey`, the alias loads the MCP credentials, making them available to Claude Code.

**Note on MCP Servers**: This post focuses on safety hooks, but MCP servers deserve their own deep dive. Perplexity's MCP server is particularly amazing for real-time web search and research (no sponsorship, just genuinely impressed). MCP integrations are game-changers for AI workflows—more on those later.

## The Alias Pattern

### Setup (.zshrc / .bashrc)
```bash
# Claude Code with auto-loaded MCP credentials
alias claudey='env $(grep -v "^#" .env.mcp | grep -v "^$" | xargs) claude --dangerously-skip-permissions'
```

**Breakdown:**
1. `grep -v "^#"` - Skip comments
2. `grep -v "^$"` - Skip empty lines
3. `xargs` - Convert to KEY=VALUE pairs
4. `env` - Inject into environment
5. `--dangerously-skip-permissions` - YOLO mode

### Usage
```bash
cd /project
claudey  # Start Claude with MCP creds + safety hooks active
```

## Code Walkthrough

### Hook Structure
```python
def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input")

    # Check credential access
    if is_credential_file_access(tool_name, tool_input):
        print("BLOCKED: Access to credential files", file=sys.stderr)
        sys.exit(2)  # Block

    # Check dangerous commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_dangerous_rm_command(command):
            print("BLOCKED: Dangerous rm command", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)  # Allow
```

### Key Detection Function
```python
def is_credential_file_access(tool_name, tool_input):
    # File-based tools
    file_path = tool_input.get('file_path', '').lower()  # Case-insensitive!
    if re.search(r'\.env(?!\.sample|\.example)', file_path):
        return True

    # Bash commands
    command = tool_input.get('command', '').lower()
    if re.search(r'(cat|vim|base64).*\.env', command):
        return True

    return False
```

## Real-World Impact

**Before hooks:**
- Accidentally ran `cat .env` → Claude saw credentials
- `rm -rf` typo deleted work
- Manual approval fatigue

**After hooks:**
- Zero credential leaks
- Destructive commands blocked
- YOLO mode safe for daily use
- Productivity 10x

## Claude Code Settings Structure

`.claude/settings.json` configures:

1. **Hook Registration** (7 hook types available)
   - `PreToolUse` - Intercept before execution (our security layer)
   - `PostToolUse`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`, `UserPromptSubmit`

2. **Permissions** (allow/deny lists for --dangerously-skip-permissions)
   - Pre-approved tools: `Write`, `Edit`, `Bash(mkdir:*)`, etc.

3. **MCP Server Configuration**
   - Enabled servers: perplexity-ask, firecrawl-mcp, youtube-data, reddit

**Why This Matters:**
- Hooks run for EVERY session automatically
- `$CLAUDE_PROJECT_DIR` environment variable points to project root
- Exit code 2 from PreToolUse blocks the operation

**Other Hook Types**: https://docs.claude.com/en/docs/claude-code/hooks

## Example Session
```bash
$ claudey
Claude Code started with safety hooks active

You: Read the .env file
Claude: [attempts Read tool]
Hook: BLOCKED - Access to credential files prohibited

You: Read .env.sample
Claude: [attempts Read tool]
Hook: ALLOWED
[Shows .env.sample contents]

You: chmod +x deploy.sh
Hook: ALLOWED
✅ Made deploy.sh executable

You: rm -rf node_modules
Hook: BLOCKED - Dangerous rm command detected
```

## Project Structure

```
.claude/
├── settings.json              # Hook registration + permissions
├── hooks/
│   ├── pre_tool_use.py       # Security layer (main focus)
│   ├── post_tool_use.py      # Placeholder for logging
│   ├── notification.py        # Placeholder for alerts
│   ├── stop.py               # Cleanup on exit
│   ├── subagent_stop.py      # Subagent cleanup
│   ├── pre_compact.py        # Context management
│   └── user_prompt_submit.py # Input preprocessing
└── commands/
    ├── create-post.md        # Slash command definitions
    ├── build.md
    ├── publish.md
    └── ...

.env.local                     # App credentials (protected by hook)
.env.mcp                       # MCP credentials (protected by hook)
.env.sample                    # Safe template (OK to read)
.mcp.json                      # MCP server configuration
```

**Key insight:** The `.claude/` directory is your control panel for AI behavior.

## Resources
- **Hook Documentation**: https://docs.claude.com/en/docs/claude-code/hooks
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code
- **Pre-Tool-Use Hook Gist**: https://gist.github.com/Mandalorian007/3dcafac5b8e97458bdc8816ce0d4f55d
- **This Project's Hook**: `.claude/hooks/pre_tool_use.py`

## Key Takeaways

1. **YOLO mode + hooks = safe automation** - No more approval fatigue
2. **Settings.json registers hooks** - Hooks enforce policies automatically
3. **Separate .env files** - .env.local for app, .env.mcp for MCP
4. **Alias pattern simplifies workflow** - One command to start safely
5. **Exit code 2 blocks operations** - Simple, effective contract

## Conclusion

Simple pattern, massive productivity boost. Share your hook, improve the community.
