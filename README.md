# tmux-bot

An intelligent tmux plugin that translates natural language into bash commands using AI (OpenAI GPT or compatible APIs).

> ⚠️ **v3.0 Breaking Change**: Chat mode requires manual setup. [See Migration Guide](#️-breaking-change-in-v30)

## Features

- 🤖 Natural language to bash command translation
- 🔒 Security checks (dangerous operation denial, ambiguous request clarification)
- ⚡ Fast response with loading animation
- 🎨 Command preview (inserted but not executed)
- 🔧 Compatible with OpenAI-compatible API endpoints

## ⚠️ Breaking Change in v3.0

Chat mode (prefix + b) no longer auto-configured by plugin.

**To enable chat mode**, copy-paste ONE of these to `~/.tmux.conf` (no modification needed):

```tmux
# Option 1: Popup mode (requires tmux-toggle-popup plugin)
# Enable global singleton mode (one chat instance across all directories)
set -gF @popup-id-format "{popup_name}"
# Configure popup-specific keybinding (Ctrl+Q to hide popup)
set -g @popup-on-init 'set status off ; bind -n C-q detach-client'
# Bind the chat command to Alt+t (no prefix needed)
bind -n M-t run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat}'"

# Option 2: New window (no extra plugins)
bind b new-window -n "AI Chat" "#{@tmux-bot-chat}"

# Option 3: Split window (no extra plugins)
bind b split-window -v -l 30% "#{@tmux-bot-chat}"
```

**Note**: `#{@tmux-bot-chat}` is auto-configured by the plugin - no hardcoded paths needed.

**To use old auto-config behavior**, downgrade to v2.x:
```tmux
set -g @plugin 'doodle-es/tmux-bot@v2.0'
```

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

### Quick Start (Copy-Paste Ready)

**Minimal setup** (command mode only):
```tmux
# Add to ~/.tmux.conf
set -g @plugin 'doodle-es/tmux-bot'
set -g @openai_api_key "sk-your-api-key-here"
```

**Full setup** (command + popup chat mode):
```tmux
# Add to ~/.tmux.conf

# === Plugins ===
set -g @plugin 'doodle-es/tmux-bot'
set -g @plugin 'loichyan/tmux-toggle-popup'

# === API Configuration ===
set -g @openai_api_key "sk-your-api-key-here"

# === Chat Mode (Popup) ===
set -gF @popup-id-format "{popup_name}"  # Global singleton mode
set -g @popup-on-init 'set status off ; bind -n C-q detach-client'
bind -n M-t run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat}'"
```

Then reload: `tmux source ~/.tmux.conf` and press `prefix + I` to install plugins.

---

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

# Custom keybinding for command mode (default: a)
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

**New in v2.0**: Persistent AI chat mode with aichat.

### Prerequisites

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

### Setup Chat Mode

Chat mode requires **manual configuration** in your `~/.tmux.conf`. Choose one of the following options:

#### Option 1: Popup Mode (Recommended)

**Requirements**:
- tmux >= 3.2 (for popup support)
- [tmux-toggle-popup](https://github.com/loichyan/tmux-toggle-popup) plugin

**Configuration** (copy-paste ready):
```tmux
# 1. Add tmux-toggle-popup to your plugins
set -g @plugin 'loichyan/tmux-toggle-popup'

# 2. Enable global singleton mode (IMPORTANT: prevents multiple chat instances)
set -gF @popup-id-format "{popup_name}"

# 3. Configure popup-specific keybinding (Ctrl+Q to hide)
# `-n` flag makes tmux intercept key before aichat receives it
set -g @popup-on-init 'set status off ; bind -n C-q detach-client'

# 4. Bind chat command to Alt+t (no prefix needed)
bind -n M-t run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat}'"
```

**Optional: Prevent conflicts with other popups**
If you use multiple popups (e.g., lazygit, htop), add `--name=aichat` to avoid session collision:
```tmux
bind -n M-t run "#{@popup-toggle} -w85% -h85% -E --name=aichat '#{@tmux-bot-chat}'"
```

**Usage**:
- Press `Alt+t` to open popup (from any directory, no prefix needed)
- Press `Ctrl+Q` to hide popup (keeps aichat running in background)
  - **Why no prefix needed**: `-n` flag intercepts key before aichat captures it
- Press `Alt+t` again to resume the same session
- **Global singleton**: All directories share one chat instance (conversation history preserved)

#### Option 2: New Window Mode

**Requirements**: None (uses tmux built-in)

**Configuration** (copy-paste ready):
```tmux
# Add to ~/.tmux.conf - no modification needed
bind b new-window -n "AI Chat" "#{@tmux-bot-chat}"
```

**Usage**:
- Press `prefix + b` to open chat in new window
- Press `Ctrl+D` or type `.exit` to close
- Use `prefix + [window number]` to switch back to work

#### Option 3: Split Window Mode

**Requirements**: None (uses tmux built-in)

**Configuration** (copy-paste ready):
```tmux
# Add to ~/.tmux.conf - no modification needed
bind b split-window -v -l 30% "#{@tmux-bot-chat}"
```

**Usage**:
- Press `prefix + b` to open chat in bottom split (30% height)
- Press `Ctrl+D` or type `.exit` to close split
- Use `prefix + arrow keys` to switch panes

### Chat Mode Features

### Chat Mode vs Command Mode

| Feature | Command Mode (`prefix + a`) | Chat Mode (`Alt+t`) |
|---------|----------------------------|---------------------|
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

**Using custom roles** (after creating the role file above):
```tmux
# Option 1: Via keybinding argument
bind -n M-r run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} -r tmux-bot-assistant'"

# Option 2: Via aichat config (set as default)
# Edit ~/.config/aichat/config.yaml and add: role: tmux-bot-assistant
```

### Chat Mode Configuration

**Customize keybinding**:
The default popup binding is `Alt+t`. To use a different key, modify the binding in your `~/.tmux.conf`:
```tmux
# Example: Use Alt+g instead of Alt+t
bind -n M-g run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat}'"

# Example: Use prefix + c (requires prefix)
bind c run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat}'"
```

**Note**: `@tmux_bot_chat_key` option was removed in v3.0. Manually configure the binding instead.

### Advanced: Custom Arguments

Pass arguments to aichat for advanced customization:

**Use custom AI model**:
```tmux
bind -n M-4 run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} -m gpt-4o'"
bind -n M-3 run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} -m claude-sonnet-4.5'"
```

**Use specific role**:
```tmux
# Assuming you created ~/.config/aichat/roles/code-reviewer.md
bind -n M-r run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} -r code-reviewer'"
```

**Start empty session (no history)**:
```tmux
bind -n M-n run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} --empty-session'"
```

**Combine multiple arguments**:
```tmux
bind -n M-c run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} -m gpt-4o -r shell-expert'"
```

### Chat Mode Troubleshooting

**"aichat not installed" message**:
- Install aichat: https://github.com/sigoden/aichat#installation
- Verify: `which aichat`

**Session doesn't persist**:
- By default, chat uses temporary session (no history saved)
- To enable persistence, use `--session` flag in your binding:
  ```tmux
  bind -n M-t run "#{@popup-toggle} -w85% -h85% -E '#{@tmux-bot-chat} --session my-chat'"
  ```
- Check active sessions: `aichat --list-sessions`
- Delete session: `aichat` → `.delete session <name>`

**Role not found**:
- Custom roles are optional
- aichat uses default behavior if role missing
- Create role: `mkdir -p ~/.config/aichat/roles/`

**Q: I pressed `Ctrl+Q` but the popup didn't hide**

A: Check if the keybinding is configured:
```bash
tmux show -g @popup-on-init
# Should show: set status off ; bind -n C-q detach-client
```
If not, reload tmux config: `tmux source-file ~/.tmux.conf`

**Q: What's the difference between `Ctrl+Q` and `Ctrl+D`?**

A:
- `Ctrl+Q`: Hide popup (aichat keeps running, instant resume)
- `Ctrl+D`: Exit aichat (terminate process, fresh start next time)

**Q: The popup doesn't resume my previous conversation**

A: This is expected if you used `Ctrl+D` (exit). Use `Ctrl+Q` (hide) instead. aichat's `--session` flag persists history across restarts, but there's a slight delay.

**Q: Multiple aichat instances are created in different directories**

A: This happens when `@popup-id-format` is not configured. By default, tmux-toggle-popup uses directory path in the session ID, creating separate instances per directory.

**Fix** (add to `~/.tmux.conf`):
```tmux
set -gF @popup-id-format "{popup_name}"
```

Then cleanup old sessions:
```bash
# Kill all old popup sessions
tmux -L popup kill-server

# Or use the automated fix script
./scripts/fix-multi-instance.sh
```

Verify only one session exists:
```bash
tmux -L popup list-sessions
# Should show: aichat: 1 windows (created ...)
```

See `FIX_MULTI_INSTANCE.md` for detailed diagnosis.

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
