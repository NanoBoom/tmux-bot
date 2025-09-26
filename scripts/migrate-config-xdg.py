#!/usr/bin/env python3
"""
Standalone script for migrating TmuxBot configuration to XDG Base Directory.

This script migrates configuration from legacy ./config.yaml to XDG-compliant
~/.config/tmuxbot/config.yaml location following the XDG Base Directory specification.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add the project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from tmuxbot.utils.config_migration import (
        migration_status,
        migrate_config,
        check_migration_needed,
        get_migration_paths
    )
    from tmuxbot.config.settings import load_config, get_config_file_path
except ImportError as e:
    print(f"❌ Error importing TmuxBot modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        stream=sys.stdout
    )


def print_banner() -> None:
    """Print script banner."""
    print("🔧 TmuxBot XDG Configuration Migration Tool")
    print("=" * 50)


def print_status_report() -> None:
    """Print current migration status."""
    print("\n📊 Current Configuration Status")
    print("-" * 30)

    status = migration_status()

    print(f"Legacy config exists: {'✅ Yes' if status['legacy_exists'] else '❌ No'}")
    if status['legacy_path']:
        print(f"Legacy path: {status['legacy_path']}")

    print(f"XDG config exists: {'✅ Yes' if status['xdg_exists'] else '❌ No'}")
    print(f"XDG path: {status['xdg_path']}")

    print(f"Migration needed: {'✅ Yes' if status['needs_migration'] else '❌ No'}")
    print(f"Recommendation: {status['recommendation']}")


def dry_run() -> bool:
    """
    Show what would be done without executing migration.

    Returns:
        bool: True if migration would be needed, False otherwise
    """
    print("\n🔍 Dry Run - Migration Plan")
    print("-" * 30)

    needs_migration, legacy_path, xdg_path = check_migration_needed()

    if not needs_migration:
        if not legacy_path:
            print("🟢 No legacy configuration found - no migration needed")
        elif xdg_path.exists():
            print("🟠 Both legacy and XDG configs exist")
            print(f"   Legacy: {legacy_path}")
            print(f"   XDG:    {xdg_path}")
            print("   XDG config takes priority - consider removing legacy manually")
        return False

    print("📋 Migration Plan:")
    print(f"   1. ✅ Create directory: {xdg_path.parent}")
    print(f"   2. 📄 Copy file: {legacy_path} → {xdg_path}")
    print(f"   3. 🔍 Preserve permissions and timestamps")
    print(f"   4. 📦 Create backup: {legacy_path}.backup")
    print(f"   5. ✅ Validate migrated configuration")

    return True


def validate_migrated_config(xdg_path: Path) -> bool:
    """
    Validate the migrated configuration can be loaded successfully.

    Args:
        xdg_path: Path to the XDG config file

    Returns:
        bool: True if validation passes, False otherwise
    """
    print("\n🔍 Validating migrated configuration...")

    try:
        # Check file exists
        if not xdg_path.exists():
            print("❌ Configuration file not found at XDG location")
            return False

        # Try loading the configuration
        config = load_config()
        if config is None:
            print("❌ Configuration could not be loaded")
            return False

        print("✅ Configuration validation successful")
        print(f"   📄 File: {xdg_path}")
        print(f"   👥 Profiles: {len(config.profiles)}")
        print(f"   🤖 Agents: {len(config.agents)}")
        print(f"   📚 Max history: {config.max_history}")
        print(f"   ⏱️  Timeout: {config.conversation_timeout}s")

        return True

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def interactive_migration() -> bool:
    """
    Run interactive migration with user prompts.

    Returns:
        bool: True if migration successful, False otherwise
    """
    print("\n🚀 Starting Interactive Migration")
    print("-" * 35)

    # Check if migration is needed
    needs_migration, legacy_path, xdg_path = check_migration_needed()

    if not needs_migration:
        print("ℹ️  Migration not needed")
        return True

    # Run migration
    success = migrate_config(interactive=True, backup=True)

    if success:
        # Validate the migrated configuration
        if validate_migrated_config(xdg_path):
            print("\n🎉 Migration completed successfully!")
            print(f"Configuration is now available at: {xdg_path}")
            print(f"You can remove the legacy config: {legacy_path}")
        else:
            print("\n⚠️  Migration completed but validation failed")
            print("Please check the configuration manually")
            return False
    else:
        print("\n❌ Migration failed")
        return False

    return True


def non_interactive_migration() -> bool:
    """
    Run non-interactive migration (for scripts/automation).

    Returns:
        bool: True if migration successful, False otherwise
    """
    print("\n🤖 Running Non-Interactive Migration")
    print("-" * 38)

    success = migrate_config(interactive=False, backup=True)

    if success:
        xdg_path = get_config_file_path()
        if validate_migrated_config(xdg_path):
            print("✅ Non-interactive migration completed successfully")
        else:
            print("❌ Migration completed but validation failed")
            return False
    else:
        print("❌ Non-interactive migration failed")
        return False

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate TmuxBot configuration to XDG Base Directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate-config-xdg.py --status    # Show current status
  python migrate-config-xdg.py --dry-run   # Show migration plan
  python migrate-config-xdg.py             # Run interactive migration
  python migrate-config-xdg.py --yes       # Run non-interactive migration
        """
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current configuration status'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without executing'
    )

    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Run migration without interactive prompts'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Print banner
    print_banner()

    try:
        # Handle different modes
        if args.status:
            print_status_report()
            return 0

        if args.dry_run:
            print_status_report()
            migration_needed = dry_run()
            return 0 if not migration_needed else 1

        # Run migration
        print_status_report()

        if args.yes:
            success = non_interactive_migration()
        else:
            success = interactive_migration()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())