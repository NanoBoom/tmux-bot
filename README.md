# Tmux AI Assistant

This is a tmux plugin that uses an AI model (like OpenAI's GPT series) to translate your natural language into bash commands and types them directly into your terminal.

<https://github.com/doodle-es/tmux-bot/assets/889295/0391d1e6-b620-4286-8a39-5095d38b0066>

## Features

- **Natural Language to Command**: Simply describe what you want to do (e.g., "find all markdown files in my home directory") and the AI will generate the command for you.
- **Seamless Integration**: Binds to a tmux key of your choice (`prefix + b` by default) for quick access.
- **Direct Input**: The suggested command is typed directly into your command prompt, ready for you to review and execute.

## Requirements

- **tmux**: The terminal multiplexer.
- **curl**: A command-line tool for transferring data with URLs.
- **jq**: A lightweight and flexible command-line JSON processor.
- **OpenAI API Key**: You need an API key from OpenAI to use the model.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/doodle-es/tmux-bot.git ~/.config/tmux/plugins/tmux-bot
    ```

2. **Set up your OpenAI API Key:**

    You can configure the API key in two ways:

    **Option A: Environment variable** (add to `~/.bashrc`, `~/.zshrc`):

    ```bash
    export OPENAI_API_KEY="your_openai_api_key_here"
    ```

    Reload your shell configuration for the changes to take effect (e.g., `source ~/.zshrc`).

    **Option B: Tmux configuration** (add to `~/.tmux.conf`):

    ```tmux
    set-option -g @openai_api_key "your_openai_api_key_here"
    # Optional: Set custom API URL (defaults to OpenAI)
    set-option -g @openai_base_url "https://api.openai.com/v1/chat/completions"
    ```

3. **Add the plugin to your `tmux.conf`:**

    Add this line to your `~/.tmux.conf` file:

    ```tmux
    run-shell "~/.config/tmux/plugins/tmux-bot/bot.tmux"
    ```

4. **Reload your tmux configuration:**

    ```bash
    tmux source-file ~/.tmux.conf
    ```

## Usage

1. Press `prefix + b` (your tmux prefix, then the letter 'b').
2. A command prompt will appear at the bottom of your tmux window.
3. Type your request in natural language (e.g., "list all running docker containers").
4. Press `Enter`.
5. The AI-generated command will be typed into your current tmux pane.

## Customization

### Key Binding

You can change the key binding in the `bot.tmux` file. For example, to change it to `prefix + a`:

```tmux
# In bot.tmux
tmux bind-key a command-prompt -p "Ask AI assistant:" \
  "run-shell '"$CURRENT_DIR/scripts/suggest.sh" "%1"'"
```

### API Configuration

You can configure the API endpoint, key, and model in your `~/.tmux.conf`:

```tmux
# Set OpenAI API key
set-option -g @openai_api_key "your_openai_api_key_here"

# Optional: Set custom API URL (for other OpenAI-compatible APIs)
set-option -g @openai_base_url "https://api.openai.com/v1"

# Optional: Set custom model (default: gpt-5)
set-option -g @openai_model "gpt-4-turbo"
```

## License

This project is licensed under the MIT License.

