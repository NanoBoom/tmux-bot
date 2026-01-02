# tmux-bot

An intelligent tmux plugin that translates natural language into bash commands using AI (OpenAI GPT or compatible APIs).

## Features

- 🤖 Natural language to bash command translation
- 🔒 Security checks (dangerous operation denial, ambiguous request clarification)
- ⚡ Fast response with loading animation
- 🎨 Command preview (inserted but not executed)
- 🔧 Compatible with OpenAI-compatible API endpoints

## ⚠️ Breaking Change in v2.0

Default keybindings changed:
- Command mode: `prefix + v` → `prefix + a`
- Chat mode: `prefix + V` → `prefix + b`

**To use old keys**, add to `~/.tmux.conf`:
```tmux
set -g @tmux_bot_key "v"
set -g @tmux_bot_chat_key "V"
```

## Requirements

- **tmux** >= 1.9 (uses `command-prompt -p` feature)
- **bash** >= 4.0
- **curl** (HTTP client)
- **jq** (JSON processor)
- **OpenAI API key** or compatible API endpoint

## Installation

### Via TPM (Recommended)

Add to your `~/.tmux.conf`:

```tmux
set -g @plugin 'doodle-es/tmux-bot'
```

Press `prefix + I` to install.

### Manual Installation

```bash
git clone https://github.com/doodle-es/tmux-bot ~/.tmux/plugins/tmux-bot
echo 'run-shell "~/.tmux/plugins/tmux-bot/bot.tmux"' >> ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

## Configuration

### Required Settings

```tmux
# Set your OpenAI API key (required)
set -g @openai_api_key "sk-your-api-key-here"
```

Or use environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Optional Settings

```tmux
# Custom API endpoint (default: https://api.openai.com/v1)
set -g @openai_base_url "https://api.openai.com/v1"

# Model selection (default: gpt-4)
set -g @openai_model "gpt-4"

# Custom keybinding (default: a)
set -g @tmux_bot_key "c"  # Use 'c' instead of default 'a'
```

## Usage

1. Press `prefix + a` (or your custom key)
2. Type your natural language request (e.g., "show disk usage")
3. Wait for AI to generate the command
4. Command is inserted into your terminal (not auto-executed)
5. Review and press Enter to execute

### Example Requests

- "list all markdown files"
- "show current directory size"
- "compress all png files to archive.zip"
- "find files modified in last 7 days"

### Safety Features

**Dangerous Operation Denial**: Commands like `rm -rf /`, `dd`, `mkfs` are automatically denied.

**Ambiguous Request Clarification**: If your request lacks key information, the AI will ask for clarification.

**Command Preview**: Commands are inserted but not executed, allowing you to review before running.

## AI Chat Assistant (Multi-turn Conversations)

**New in v2.0**: Persistent AI chat mode with `prefix + b`.

### Quick Start

1. **Install aichat**:
   ```bash
   # macOS
   brew install aichat

   # Linux
   cargo install aichat

   # Or download binary from https://github.com/sigoden/aichat/releases
   ```

2. **Configure API Key** (if not already done):
   ```bash
   # aichat will prompt for API key on first run
   aichat

   # Or set environment variable
   export OPENAI_API_KEY="sk-..."
   ```

3. **Install tmux-toggle-popup** (optional, for popup UI):
   ```tmux
   # Add to ~/.tmux.conf
   set -g @plugin 'loichyan/tmux-toggle-popup'

   # Then install via TPM (prefix + I)
   ```

4. **Use Chat Mode**:
   - Press `prefix + b`
   - Popup appears with aichat REPL
   - Ask questions, get responses, refine iteratively
   - Close popup: session persists, reopens with full history

### Chat Mode vs Command Mode

| Feature | Command Mode (`prefix + a`) | Chat Mode (`prefix + b`) |
|---------|----------------------------|--------------------------|
| **Use Case** | Quick one-shot commands | Multi-turn conversations |
| **UI** | Inline prompt | Popup window |
| **History** | None | Full session persistence |
| **Output** | Inserts command to terminal | Interactive chat |
| **Best For** | "Find all .md files" | "Explain tmux sessions, then show me how to rename one" |

### Custom Role (Optional)

Create `~/.config/aichat/roles/tmux-bot-assistant.md`:

```yaml
---
model: openai:gpt-4
temperature: 0.3
---
You are a tmux and shell command expert.

When user describes a task:
1. Provide executable command (single-line preferred)
2. Brief explanation
3. Warn if destructive (rm, dd, mkfs, etc.)

Consider OS and shell context. Be concise.
```

See `examples/aichat-role-tmux-bot-assistant.md` for a complete example.

### Chat Mode Configuration

```tmux
# Customize chat keybinding (default: b)
set -g @tmux_bot_chat_key "B"  # Use capital 'B' instead of default 'b'
```

### Chat Mode Troubleshooting

**"aichat not installed" message**:
- Install aichat: https://github.com/sigoden/aichat#installation
- Verify: `which aichat`

**Popup doesn't appear**:
- Option 1: Install tmux-toggle-popup (see Quick Start)
- Option 2: Use fallback (opens new tmux window instead)
- Check: `tmux show -g @popup-toggle` should show script path

**Session doesn't persist**:
- aichat sessions auto-save by default
- Check: `aichat --list-sessions` should show "tmux-bot"
- Delete session: `aichat` → `.delete session tmux-bot`

**Role not found**:
- Custom roles are optional
- aichat uses default behavior if role missing
- Create role: `mkdir -p ~/.config/aichat/roles/`

## Troubleshooting

### Plugin Not Loading

- Check tmux version: `tmux -V` (must be >= 1.9)
- Reload config: `tmux source-file ~/.tmux.conf`
- Check for errors: `tmux display-message "Plugin loaded"`

### API Key Not Working

- Verify key is set: `tmux show-option -gv @openai_api_key`
- Check environment variable: `echo $OPENAI_API_KEY`
- Test connectivity: `curl -I https://api.openai.com/v1/models`

### Key Binding Conflict

- Check existing bindings: `tmux list-keys | grep "bind-key.*a"`
- Use custom key: `set -g @tmux_bot_key "your-key"`
- Plugin will warn if key is already bound

### Missing Dependencies

```bash
# macOS
brew install jq curl

# Ubuntu/Debian
sudo apt-get install jq curl

# Verify installation
command -v jq && command -v curl && echo "✅ Dependencies OK"
```

## Development

### Running Tests

```bash
# Run full test suite
./tests/run_tests

# Run specific test file
bash tests/test_helpers.sh

# Run shellcheck
shellcheck -x bot.tmux scripts/*.sh
```

### Project Structure

```
tmux-bot/
├── bot.tmux              # Plugin entry point
├── scripts/
│   ├── suggest.sh        # Main logic (API calls)
│   ├── helpers.sh        # Utility functions
│   └── variables.sh      # Configuration constants
├── tests/                # Test suite
└── PRPs/                 # Implementation plans
```

## License

MIT License - see LICENSE file for details

## Credits

Inspired by tmux plugin ecosystem best practices from:
- [tmux-plugins/tpm](https://github.com/tmux-plugins/tpm)
- [tmux-plugins/tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect)
- [tmux-plugins/tmux-yank](https://github.com/tmux-plugins/tmux-yank)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
