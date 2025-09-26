#!/usr/bin/env python3
"""
TmuxBot Configuration Setup and Validation Script

This script helps set up, validate, and test TmuxBot configuration.
Configuration follows XDG Base Directory specification (~/.config/tmuxbot/config.yaml).

Usage:
    python scripts/setup-config.py --validate         # Validate XDG configuration
    python scripts/setup-config.py --create-template  # Create XDG config template
    python scripts/setup-config.py --check-migration  # Check if migration is needed
    python scripts/setup-config.py --full-check       # Complete configuration check
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tmuxbot.config.settings import (
        load_config,
        save_config_template,
        get_config_file_path,
        get_tmuxbot_config_dir,
        ensure_config_directory
    )
    from tmuxbot.utils.config_migration import migration_status, migrate_config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


class ConfigSetup:
    """Configuration setup and validation utility."""

    def __init__(self):
        self.project_root = project_root
        self.xdg_config_dir = get_tmuxbot_config_dir()
        self.xdg_config_file = get_config_file_path()

    def validate_main_config(self) -> bool:
        """Validate the main XDG configuration."""
        print("🔍 Validating XDG configuration...")

        try:
            config = load_config()

            if config is None:
                print("❌ No configuration found")
                print(f"   Expected location: {self.xdg_config_file}")
                print("   Run --create-template to create a configuration template")
                return False

            print("✅ XDG configuration loaded successfully")
            print(f"   Configuration file: {self.xdg_config_file}")
            print(f"   Profiles configured: {len(config.profiles)}")
            print(f"   Agents configured: {len(config.agents)}")
            print(f"   Max history: {config.max_history}")
            print(f"   Conversation timeout: {config.conversation_timeout}s")

            # Validate profile structure
            if not config.profiles:
                print("⚠️  No profiles configured")
                return False

            # Validate agent structure
            if not config.agents:
                print("⚠️  No agents configured")
                return False

            print("✅ Configuration structure is valid")
            return True

        except Exception as e:
            print(f"❌ Error validating main configuration: {e}")
            return False

    def check_migration_status(self) -> bool:
        """Check if migration from legacy config is needed."""
        print("🔍 Checking configuration migration status...")

        try:
            status = migration_status()

            print(f"   XDG config exists: {'✅ Yes' if status['xdg_exists'] else '❌ No'}")
            print(f"   XDG config path: {status['xdg_path']}")

            if status['legacy_exists']:
                print(f"   Legacy config found: {status['legacy_path']}")

                if status['needs_migration']:
                    print("⚠️  Migration needed!")
                    print("   Run 'python scripts/migrate-config-xdg.py' to migrate your configuration")
                    return False
                else:
                    print("⚠️  Legacy config exists but XDG config takes priority")
                    print("   Consider removing legacy config manually")

            print(f"📝 Recommendation: {status['recommendation']}")
            return not status['needs_migration']

        except Exception as e:
            print(f"❌ Error checking migration status: {e}")
            return False

    def validate_xdg_directory(self) -> bool:
        """Validate XDG directory structure."""
        print("🔍 Validating XDG directory structure...")

        try:
            # Check if config directory exists
            if self.xdg_config_dir.exists():
                print(f"✅ XDG config directory exists: {self.xdg_config_dir}")
            else:
                print(f"⚠️  XDG config directory does not exist: {self.xdg_config_dir}")
                print("   Will be created automatically when needed")

            # Check if config file exists
            if self.xdg_config_file.exists():
                print(f"✅ XDG config file exists: {self.xdg_config_file}")
            else:
                print(f"⚠️  XDG config file does not exist: {self.xdg_config_file}")
                print("   Run --create-template to create configuration template")

            # Check directory permissions
            try:
                ensure_config_directory()
                print("✅ XDG directory permissions are valid")
                return True
            except PermissionError:
                print("❌ Permission denied accessing XDG config directory")
                return False

        except Exception as e:
            print(f"❌ Error validating XDG directory: {e}")
            return False

    def create_config_template(self) -> bool:
        """Create XDG configuration template."""
        print("🔧 Creating XDG configuration template...")

        try:
            if self.xdg_config_file.exists():
                response = input(f"⚠️  Configuration already exists at {self.xdg_config_file}. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print("📋 Keeping existing configuration")
                    return True

            save_config_template()
            print(f"✅ Configuration template created at: {self.xdg_config_file}")
            print("📝 Please edit the configuration and add your API keys")
            return True

        except Exception as e:
            print(f"❌ Error creating configuration template: {e}")
            return False

    def validate_profile_configs(self) -> bool:
        """Validate profile configurations in the XDG config."""
        print("🔍 Validating profile configurations...")

        try:
            config = load_config()
            if config is None:
                print("❌ No configuration loaded")
                return False

            if not config.profiles:
                print("❌ No profiles configured")
                return False

            print(f"✅ Found {len(config.profiles)} profiles:")

            for profile_name, profile_config in config.profiles.items():
                print(f"   📋 {profile_name}:")
                print(f"      Provider: {profile_config.provider}")
                print(f"      Model: {profile_config.model}")
                print(f"      API Key: {'✅ Set' if profile_config.api_key else '❌ Missing'}")
                if profile_config.base_url:
                    print(f"      Base URL: {profile_config.base_url}")

            return True

        except Exception as e:
            print(f"❌ Error validating profile configurations: {e}")
            return False

    def validate_agent_configs(self) -> bool:
        """Validate agent configurations in the XDG config."""
        print("🔍 Validating agent configurations...")

        try:
            config = load_config()
            if config is None:
                print("❌ No configuration loaded")
                return False

            if not config.agents:
                print("❌ No agents configured")
                return False

            print(f"✅ Found {len(config.agents)} agents:")

            for agent_name, agent_config in config.agents.items():
                print(f"   🤖 {agent_name}:")
                print(f"      Profile: {agent_config.profile}")
                if agent_config.instructions:
                    print(f"      Instructions: {agent_config.instructions[:50]}...")
                if agent_config.fallbacks:
                    print(f"      Fallbacks: {', '.join(agent_config.fallbacks)}")

                # Validate that the referenced profile exists
                if agent_config.profile not in config.profiles:
                    print(f"      ❌ Profile '{agent_config.profile}' not found")
                    return False

            return True

        except Exception as e:
            print(f"❌ Error validating agent configurations: {e}")
            return False

    def check_environment_variables(self) -> bool:
        """Check required environment variables."""
        print("🔍 Checking environment variables...")

        required_vars = {
            "OPENAI_API_KEY": "OpenAI API access",
            "OPENROUTER_API_KEY": "OpenRouter API access (optional)",
            "ANTHROPIC_API_KEY": "Anthropic API access (optional)"
        }

        found_vars = {}
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            found_vars[var_name] = value is not None

            if value:
                # Show masked version for security
                if len(value) > 8:
                    masked = value[:6] + "..." + value[-4:]
                else:
                    masked = "***"
                print(f"   ✅ {var_name}: {masked}")
            else:
                print(f"   ⚠️  {var_name}: Not set ({description})")

        # Check if at least one provider key is available
        has_provider_key = found_vars["OPENAI_API_KEY"] or found_vars["OPENROUTER_API_KEY"]

        if has_provider_key:
            print("✅ At least one provider API key is configured")
            return True
        else:
            print("❌ No provider API keys found - set OPENAI_API_KEY or OPENROUTER_API_KEY")
            return False

    def check_config_files(self) -> bool:
        """Check XDG configuration file structure."""
        print("🔍 Checking XDG configuration files...")

        # Check main XDG config file
        if self.xdg_config_file.exists():
            print(f"   ✅ XDG config file: {self.xdg_config_file}")
            return True
        else:
            print(f"   ❌ XDG config file missing: {self.xdg_config_file}")
            print("   Run --create-template to create configuration")
            return False

    def create_env_template(self) -> bool:
        """Create .env file from template."""
        print("🔧 Creating .env file from template...")

        env_template = self.project_root / ".env.template"
        env_file = self.project_root / ".env"

        if not env_template.exists():
            print("❌ .env.template not found")
            return False

        if env_file.exists():
            response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("📋 Keeping existing .env file")
                return True

        try:
            # Copy template to .env
            with open(env_template, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())

            print("✅ Created .env file from template")
            print("📝 Please edit .env and add your API keys")
            return True

        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False

def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(
        description="TmuxBot XDG Configuration Setup and Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup-config.py --validate         # Validate XDG configuration
  python scripts/setup-config.py --create-template  # Create XDG config template
  python scripts/setup-config.py --check-migration  # Check migration status
  python scripts/setup-config.py --full-check       # Complete configuration check
        """
    )

    parser.add_argument("--validate", action="store_true", help="Validate XDG configuration")
    parser.add_argument("--create-template", action="store_true", help="Create XDG configuration template")
    parser.add_argument("--check-migration", action="store_true", help="Check if migration from legacy config is needed")
    parser.add_argument("--full-check", action="store_true", help="Run complete configuration validation")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    setup = ConfigSetup()

    print("🚀 TmuxBot XDG Configuration Setup and Validation")
    print("=" * 60)

    success = True

    if args.create_template:
        success &= setup.create_config_template()

    if args.check_migration or args.full_check:
        success &= setup.check_migration_status()

    if args.validate or args.full_check:
        success &= setup.validate_xdg_directory()
        success &= setup.check_config_files()
        success &= setup.validate_main_config()
        success &= setup.validate_profile_configs()
        success &= setup.validate_agent_configs()

    print("\n" + "=" * 60)

    if success:
        print("🎉 Configuration validation completed successfully!")
        print("Your TmuxBot XDG configuration is ready to use.")
        print(f"📁 Configuration location: {setup.xdg_config_file}")
    else:
        print("❌ Configuration validation found issues.")
        print("Please review the errors above and fix them.")
        if args.check_migration:
            print("💡 Consider running: python scripts/migrate-config-xdg.py")
        sys.exit(1)


if __name__ == "__main__":
    main()