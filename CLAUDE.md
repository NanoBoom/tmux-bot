# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a tmux plugin that provides AI-assisted command suggestions. The plugin binds a key (prefix + v) to open a command prompt that queries an AI assistant (OpenAI GPT) for bash command suggestions and types them directly into the terminal.

## Architecture

The plugin follows a modular architecture with clear separation of concerns:

### Core Components
- **bot.tmux**: Main tmux plugin entry point - handles key binding setup and configuration initialization
- **scripts/suggest.sh**: AI integration layer - processes user prompts, makes API calls, and inserts commands
- **scripts/helpers.sh**: Utility library - provides configuration management and error handling
- **scripts/variables.sh**: Configuration defaults - contains API parameters and system prompts

### Key Technical Implementation
- Uses tmux's `command-prompt` feature to capture natural language input
- Makes HTTP requests to OpenAI-compatible APIs using curl
- Parses JSON responses with jq to extract command content
- Supports dual configuration sources: tmux options and environment variables
- Includes comprehensive error handling for dependencies and API failures

### Configuration Management
Configuration is loaded in this priority order:
1. Tmux options (`@openai_api_key`, `@openai_base_url`, `@openai_model`)
2. Environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`)
3. Default values from variables.sh

### API Integration Pattern
1. User input → tmux command-prompt → suggest.sh
2. System prompt + user prompt → OpenAI API request
3. API response → jq parsing → command extraction
4. Extracted command → tmux send-keys → terminal input

## Development Workflow

### Testing the Plugin
```bash
# Install the plugin (from project root)
cp bot.tmux ~/.config/tmux/plugins/tmux-bot/

# Add to tmux configuration
echo 'run-shell "~/.config/tmux/plugins/tmux-bot/bot.tmux"' >> ~/.tmux.conf

# Reload tmux configuration
tmux source-file ~/.tmux.conf

# Test the binding (prefix + v)
# Type natural language request in the prompt
```

### Debugging and Development
```bash
# Test the suggest script directly
./scripts/suggest.sh "list all files in current directory"

# Check script syntax
bash -n scripts/suggest.sh
bash -n scripts/helpers.sh

# Verify dependencies are available
command -v curl && command -v jq
```

### Configuration Options
Available tmux options (set in ~/.tmux.conf):
- `@openai_api_key`: API key for authentication (required)
- `@openai_base_url`: Base URL for API endpoint (default: https://api.openai.com/v1)
- `@openai_model`: Model name to use (default: gpt-5)

Environment variable alternatives:
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`

## File Structure Details

### bot.tmux (Main Entry Point)
- Sets default configuration options
- Binds key to command-prompt with suggest.sh integration
- Sources helper scripts for shared functionality

### scripts/suggest.sh (Core Logic)
- Processes user prompt from command line argument
- Validates dependencies (curl, jq)
- Constructs API request payload with system prompt
- Handles API response parsing and error checking
- Inserts command into current tmux pane

### scripts/helpers.sh (Utilities)
- `get_tmux_option()`: Retrieves tmux options with fallback defaults
- `check_dependencies()`: Validates required command availability
- `check_api_key()`: Ensures API authentication is configured
- `get_api_config()`: Unified configuration loading with priority handling

### scripts/variables.sh (Defaults)
- API endpoint and model defaults
- System prompt for command generation
- API request parameters (temperature, tokens, etc.)

## Common Development Tasks

### Adding New Configuration Options
1. Add option to variables.sh with default value
2. Update get_api_config() in helpers.sh to handle the new option
3. Add corresponding tmux option handling in bot.tmux
4. Update documentation in README.md

### Modifying API Behavior
- Change system prompt in variables.sh for different command styles
- Adjust API parameters (temperature, max_tokens) in variables.sh
- Update error handling in suggest.sh for different API responses

### Extending Functionality
- Add new script modules in scripts/ directory
- Create additional tmux key bindings in bot.tmux
- Implement new helper functions for shared functionality