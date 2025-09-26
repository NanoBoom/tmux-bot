"""Configuration migration utilities for XDG Base Directory compliance."""

import logging
import shutil
from pathlib import Path
from typing import Tuple, Optional
import os

logger = logging.getLogger(__name__)


def detect_legacy_config() -> Optional[Path]:
    """
    Detect if a legacy config.yaml file exists in the current directory.

    Returns:
        Path: Path to legacy config if found, None otherwise
    """
    legacy_config = Path.cwd() / "config.yaml"
    return legacy_config if legacy_config.exists() else None


def get_migration_paths() -> Tuple[Path, Path]:
    """
    Get source and destination paths for config migration.

    Returns:
        Tuple[Path, Path]: (legacy_path, xdg_path)
    """
    from ..config.settings import get_config_file_path

    legacy_path = Path.cwd() / "config.yaml"
    xdg_path = get_config_file_path()
    return legacy_path, xdg_path


def check_migration_needed() -> Tuple[bool, Optional[Path], Path]:
    """
    Check if migration is needed and return relevant paths.

    Returns:
        Tuple[bool, Optional[Path], Path]: (needs_migration, legacy_path, xdg_path)
    """
    legacy_path, xdg_path = get_migration_paths()

    # Migration needed if legacy exists and XDG doesn't
    needs_migration = legacy_path.exists() and not xdg_path.exists()

    return needs_migration, legacy_path if legacy_path.exists() else None, xdg_path


def migrate_config(interactive: bool = True, backup: bool = True) -> bool:
    """
    Migrate configuration from legacy location to XDG-compliant location.

    Args:
        interactive: If True, prompt user for confirmation
        backup: If True, create backup of legacy config after migration

    Returns:
        bool: True if migration successful, False otherwise
    """
    from ..config.settings import ensure_config_directory

    needs_migration, legacy_path, xdg_path = check_migration_needed()

    if not needs_migration:
        if not legacy_path:
            logger.info("No legacy configuration found - migration not needed")
            return True
        if xdg_path.exists():
            logger.info("XDG configuration already exists - migration not needed")
            logger.info(f"Legacy config: {legacy_path}")
            logger.info(f"XDG config: {xdg_path}")
            if interactive:
                print(f"Both legacy ({legacy_path}) and XDG ({xdg_path}) configs exist.")
                print("XDG config takes priority. Consider removing legacy config manually.")
            return True

    logger.info(f"Migration needed: {legacy_path} -> {xdg_path}")

    # Interactive confirmation
    if interactive:
        print(f"\nConfiguration Migration Required")
        print(f"From: {legacy_path}")
        print(f"To:   {xdg_path}")
        print(f"\nThis will:")
        print(f"  1. Create XDG config directory if needed")
        print(f"  2. Copy configuration to XDG location")
        print(f"  3. Preserve file permissions and timestamps")
        if backup:
            print(f"  4. Create backup: {legacy_path}.backup")

        response = input("\nProceed with migration? [y/N]: ").lower().strip()
        if response not in ['y', 'yes']:
            logger.info("Migration cancelled by user")
            return False

    try:
        # Ensure XDG config directory exists
        config_dir = ensure_config_directory()
        logger.info(f"Configuration directory ensured: {config_dir}")

        # Copy file with metadata preservation
        shutil.copy2(legacy_path, xdg_path)
        logger.info(f"Configuration copied: {legacy_path} -> {xdg_path}")

        # Verify the copy was successful
        if not xdg_path.exists():
            raise RuntimeError("Configuration file was not created at destination")

        # Create backup if requested
        if backup:
            backup_path = legacy_path.with_suffix('.yaml.backup')
            shutil.copy2(legacy_path, backup_path)
            logger.info(f"Backup created: {backup_path}")

        # Success message
        success_msg = f"✅ Configuration successfully migrated to XDG location: {xdg_path}"
        logger.info(success_msg)
        if interactive:
            print(f"\n{success_msg}")
            if backup:
                print(f"📦 Backup created: {legacy_path}.backup")
            print(f"\nYou can now remove the legacy config file: {legacy_path}")

        return True

    except PermissionError as e:
        error_msg = f"Permission denied during migration: {e}"
        logger.error(error_msg)
        if interactive:
            print(f"❌ {error_msg}")
        return False

    except Exception as e:
        error_msg = f"Migration failed: {e}"
        logger.error(error_msg)
        if interactive:
            print(f"❌ {error_msg}")
        return False


def migration_status() -> dict:
    """
    Get current migration status information.

    Returns:
        dict: Status information including paths and migration state
    """
    needs_migration, legacy_path, xdg_path = check_migration_needed()

    return {
        'needs_migration': needs_migration,
        'legacy_exists': legacy_path is not None,
        'legacy_path': str(legacy_path) if legacy_path else None,
        'xdg_exists': xdg_path.exists(),
        'xdg_path': str(xdg_path),
        'recommendation': _get_migration_recommendation(needs_migration, legacy_path, xdg_path)
    }


def _get_migration_recommendation(needs_migration: bool, legacy_path: Optional[Path], xdg_path: Path) -> str:
    """Get migration recommendation based on current state."""
    if needs_migration:
        return f"Run migration to move {legacy_path} to {xdg_path}"
    elif legacy_path and xdg_path.exists():
        return f"Consider removing legacy config {legacy_path} (XDG config takes priority)"
    elif xdg_path.exists():
        return "Configuration is XDG-compliant - no action needed"
    else:
        return "No configuration found - run save_config_template() to create template"