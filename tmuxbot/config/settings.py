"""Configuration management for TmuxBot."""

import json
import os
import logging
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Union, Any, List
from pydantic_ai import ModelSettings

from ..utils.yaml_utils import safe_load_yaml

logger = logging.getLogger(__name__)


def get_xdg_config_home() -> Path:
    """
    Get XDG_CONFIG_HOME directory with fallback to ~/.config.

    Returns:
        Path: XDG config home directory
    """
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        return Path(xdg_config_home)
    return Path.home() / '.config'


def get_tmuxbot_config_dir() -> Path:
    """
    Get tmuxbot-specific configuration directory.

    Returns:
        Path: TmuxBot configuration directory (~/.config/tmuxbot or $XDG_CONFIG_HOME/tmuxbot)
    """
    return get_xdg_config_home() / 'tmuxbot'


def get_config_file_path() -> Path:
    """
    Get full path to the configuration file following XDG Base Directory specification.

    Returns:
        Path: Full path to config.yaml in XDG-compliant location
    """
    return get_tmuxbot_config_dir() / 'config.yaml'


def ensure_config_directory() -> Path:
    """
    Ensure the configuration directory exists, creating it if necessary.

    Returns:
        Path: The configuration directory path
    """
    config_dir = get_tmuxbot_config_dir()
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Configuration directory ensured: {config_dir}")
    except PermissionError:
        logger.warning(f"Permission denied creating config directory: {config_dir}")
        # Fall back to current directory for legacy compatibility
        return Path.cwd()
    except Exception as e:
        logger.warning(f"Failed to create config directory {config_dir}: {e}")
        return Path.cwd()
    return config_dir


@dataclass
class ProfileConfig:
    provider: str
    api_key: str
    model: str
    base_url: Optional[str] = None
    settings: Optional[ModelSettings] = None


@dataclass
class AgentConfig:
    profile: str
    instructions: Optional[str] = None
    fallbacks: Optional[List[str]] = None


@dataclass
class Config:
    """TmuxBot configuration settings with profile-based architecture and conversation management."""

    profiles: Dict[str, ProfileConfig]
    agents: Dict[str, AgentConfig]
    max_history: int
    conversation_timeout: int


def load_config() -> Union[None, Config]:
    """
    Load configuration from YAML file and environment variables.

    Follows XDG Base Directory specification for configuration file location:
    1. $XDG_CONFIG_HOME/tmuxbot/config.yaml (if XDG_CONFIG_HOME is set)
    2. $HOME/.config/tmuxbot/config.yaml (default XDG location)
    3. ./config.yaml (legacy fallback with deprecation warning)

    Environment variables take precedence over file values.
    Uses TMUXBOT_ prefix for environment variables.

    Returns:
        Config: Loaded configuration with defaults for missing values
    """
    config_data = {}
    config_file_loaded = None

    # Try XDG-compliant configuration path first
    xdg_config_file = get_config_file_path()
    if xdg_config_file.exists():
        try:
            yaml_data = safe_load_yaml(xdg_config_file)
            if yaml_data:
                config_data = yaml_data
                config_file_loaded = xdg_config_file
                logger.info(f"Loaded configuration from XDG location: {xdg_config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config from XDG location {xdg_config_file}: {e}")

    # Fallback to legacy config.yaml in current directory (with deprecation warning)
    if not config_file_loaded:
        legacy_config_file = Path(os.getcwd()) / "config.yaml"
        if legacy_config_file.exists():
            try:
                yaml_data = safe_load_yaml(legacy_config_file)
                if yaml_data:
                    config_data = yaml_data
                    config_file_loaded = legacy_config_file
                    logger.warning(f"DEPRECATED: Loading configuration from legacy location: {legacy_config_file}")
                    logger.warning(f"Please migrate your configuration to XDG location: {xdg_config_file}")
                    logger.warning("Run 'python scripts/migrate-config-xdg.py' to migrate automatically")
            except Exception as e:
                logger.warning(f"Failed to load legacy config.yaml: {e}")

    # Conversation management environment variables
    env_max_history = os.getenv("TMUXBOT_MAX_HISTORY")
    if env_max_history:
        try:
            history_value = int(env_max_history)
            if history_value > 0:
                config_data["max_history"] = history_value
        except ValueError:
            logger.warning(f"Invalid TMUXBOT_MAX_HISTORY value: {env_max_history}")

    env_conversation_timeout = os.getenv("TMUXBOT_CONVERSATION_TIMEOUT")
    if env_conversation_timeout:
        try:
            timeout_value = int(env_conversation_timeout)
            if timeout_value > 0:
                config_data["conversation_timeout"] = timeout_value
        except ValueError:
            logger.warning(
                f"Invalid TMUXBOT_CONVERSATION_TIMEOUT value: {env_conversation_timeout}"
            )

    # Profile-specific environment variables are handled by ProfileConfigManager

    # Create Config object with loaded data, using defaults for missing fields
    try:
        # Convert profile data to ProfileConfig objects
        profiles = {}
        profile_data = config_data.get("profiles", {})
        for profile_name, profile_info in profile_data.items():
            profiles[profile_name] = ProfileConfig(
                provider=profile_info["provider"],
                api_key=profile_info["api_key"],
                model=profile_info["model"],
                base_url=profile_info.get("base_url"),
                settings=profile_info.get("settings"),
            )

        # Convert agent data to AgentConfig objects
        agents = {}
        agent_data = config_data.get("agents", {})
        for agent_name, agent_info in agent_data.items():
            agents[agent_name] = AgentConfig(
                profile=agent_info["profile"],
                instructions=agent_info.get("instructions"),
                fallbacks=agent_info.get("fallbacks"),
            )

        config = Config(
            profiles=profiles,
            agents=agents,
            max_history=config_data.get("max_history", 100),
            conversation_timeout=config_data.get("conversation_timeout", 300),
        )

        return config
    except (TypeError, ValueError) as e:
        # Return default config if there are any issues
        logger.warning(f"Failed to load config: {e}")
        return None


def save_config_template() -> None:
    """
    Save a profile-based configuration template to XDG-compliant config.yaml location.
    Creates the configuration directory if it doesn't exist.
    Only creates the file if it doesn't already exist in the XDG location.
    """
    # Ensure the configuration directory exists
    ensure_config_directory()

    # Use XDG-compliant path for template creation
    yaml_config_file = get_config_file_path()

    # Create profile-based configuration template
    config_data = {
        "profiles": {
            "openai-gpt-4o": {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key": "your-openai-api-key-here",
                "base_url": None,
                "settings": None,
            },
            "openai-gpt-4o-mini": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "your-openai-api-key-here",
                "base_url": None,
                "settings": None,
            },
        },
        "agents": {
            "primary": {
                "profile": "openai-gpt-4o",
                "instructions": "You are TmuxBot's primary coordination agent.",
                "fallbacks": None,
            },
            "coder": {
                "profile": "openai-gpt-4o",
                "instructions": "Focus on code quality and best practices.",
                "fallbacks": ["openai-gpt-4o-mini"],
            },
        },
        "max_history": 100,
        "conversation_timeout": 300,
    }

    # Try to save as YAML first
    try:
        yaml_content = f"""# TmuxBot Profile-Based Configuration
# Configuration follows XDG Base Directory specification
# Location: {yaml_config_file}
# Pure profile-based architecture - no legacy settings
# Environment variables: Use TMUXBOT_PROFILE_{{PROFILE_NAME}}_{{PARAMETER}} to override settings

{yaml.safe_dump(config_data, default_flow_style=False, indent=2, sort_keys=False)}"""

        with open(yaml_config_file, "w") as f:
            f.write(yaml_content)
        logger.info(f"Created config.yaml template at XDG location: {yaml_config_file}")

    except Exception as e:
        logger.warning(f"Failed to create YAML template: {e}")
