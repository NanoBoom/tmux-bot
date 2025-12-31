# tmux-bot

An intelligent tmux plugin that translates natural language into bash commands using AI (OpenAI GPT or compatible APIs).

## Features

- 🤖 Natural language to bash command translation
- 🔒 Security checks (dangerous operation denial, ambiguous request clarification)
- ⚡ Fast response with loading animation
- 🎨 Command preview (inserted but not executed)
- 🔧 Compatible with OpenAI-compatible API endpoints

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

# Custom keybinding (default: v)
set -g @tmux_bot_key "V"  # Use capital V instead
```

## Usage

1. Press `prefix + v` (or your custom key)
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

- Check existing bindings: `tmux list-keys | grep "bind-key.*v"`
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
