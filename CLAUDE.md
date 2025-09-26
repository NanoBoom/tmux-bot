# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing

- `pytest` - Run all tests
- `pytest tests/model/` - Run specific test directory
- `pytest tests/providers/test_openai.py` - Run specific test file

### Code Quality

- `ruff` - Run linting
- `mypy` - Run type checking

### Running the Application

- `python main.py` - Start TmuxBot
- `python -m tmuxbot` - Alternative way to start

### Configuration Management

- `python scripts/setup-config.py --create-template` - Create XDG config template
- `python scripts/setup-config.py --validate` - Validate configuration
- `python scripts/migrate-config-xdg.py` - Migrate legacy config to XDG

## Architecture Overview

### Configuration System

TmuxBot uses an XDG Base Directory compliant configuration system with profile-based architecture:

- **Config Location**: `~/.config/tmuxbot/config.yaml` (XDG-compliant)
- **Legacy Support**: `./config.yaml` (deprecated with warnings)
- **Profile-Based**: Separate AI provider profiles for different agents
- **Environment Override**: Use `TMUXBOT_*` environment variables

Key configuration modules:

- `tmuxbot/config/settings.py` - Main configuration loading and XDG compliance
- `tmuxbot/utils/config_migration.py` - Migration utilities

### Agent System

Multi-agent architecture using PydanticAI:

- **Primary Agent** (`tmuxbot/agents/primary.py`) - Main coordination
- **Specialized Agents**: Coder, DevOps, SysAdmin agents in `tmuxbot/agents/`
- **Shared Dependencies** (`TmuxBotDeps`) - Conversation history, context
- **Agent Factory Pattern** - Configuration-driven agent creation with fallback support

### Provider System

AI provider abstraction supporting multiple backends:

- **OpenAI Provider** (`tmuxbot/providers/openai.py`) - Direct OpenAI integration
- **OpenRouter Support** - Alternative provider with cost optimization
- **Fallback Mechanism** - Automatic failover between providers/models
- **Model Factory** (`tmuxbot/model/factory.py`) - Provider instance creation

### Core Components

- **App Entry Point** (`tmuxbot/app.py`) - Main application with error handling
- **Context Management** (`tmuxbot/core/context.py`) - Conversation state
- **YAML Utilities** (`tmuxbot/utils/yaml_utils.py`) - Safe YAML parsing

### Technology Stack

- **PydanticAI** - Primary agent framework
- **Rich** - Terminal UI and formatting
- **PyYAML** - Configuration file parsing
- **pytest** - Testing framework

## Development Guidelines

### Profile-Based Configuration

- All AI providers are configured through profiles in `config.yaml`
- Each agent references a profile and can have fallbacks
- Environment variables use `TMUXBOT_PROFILE_{PROFILE_NAME}_{PARAMETER}` format

### Agent Development

- Use PydanticAI data models (avoid custom types where possible)
- Implement fallback mechanisms for reliability
- Follow dependency injection pattern with `TmuxBotDeps`

### Configuration Migration

- XDG Base Directory specification compliance is enforced
- Legacy `config.yaml` support maintained with deprecation warnings
- Migration scripts handle automatic upgrades

### Error Handling

- Rich console output for user-friendly error messages
- Graceful degradation for configuration/provider failures
- Comprehensive logging throughout the application

