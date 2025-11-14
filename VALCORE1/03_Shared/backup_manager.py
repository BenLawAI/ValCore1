"""
VALCORE1 Backup Manager
Automated backup system for FAISS indices, configs, and critical data
"""

import os
import logging
import shutil
import tarfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import threading
import time

logger = logging.getLogger(__name__)


class BackupManager:
    """Automated backup system"""

    def __init__(self, backup_root: str = "backups", retention_days: int = 30):
        """
        Initialize backup manager

        Args:
            backup_root: Root directory for backups
            retention_days: Days to keep backups before deletion
        """
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days

        self.scheduler_running = False
        self.scheduler_thread = None

        logger.info(f"Backup manager initialized: {self.backup_root}")
        logger.info(f"Retention policy: {retention_days} days")

    def create_backup(
        self,
        name: str,
        paths: List[str],
        description: str = ""
    ) -> Optional[str]:
        """
        Create a backup archive

        Args:
            name: Backup name (e.g., 'faiss_index', 'config')
            paths: List of files/directories to backup
            description: Optional description

        Returns:
            Path to backup file or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_{timestamp}.tar.gz"
            backup_path = self.backup_root / backup_name

            logger.info(f"Creating backup: {backup_name}")

            # Create tarball
            with tarfile.open(backup_path, "w:gz") as tar:
                for path_str in paths:
                    path = Path(path_str)

                    if not path.exists():
                        logger.warning(f"Path not found, skipping: {path}")
                        continue

                    # Add to archive with relative path
                    arcname = path.name if path.is_file() else path.name
                    tar.add(path, arcname=arcname)

                    logger.debug(f"Added to backup: {path}")

            # Create metadata file
            metadata = {
                "name": name,
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "description": description,
                "paths": [str(p) for p in paths],
                "size_bytes": backup_path.stat().st_size
            }

            metadata_path = self.backup_root / f"{name}_{timestamp}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            size_mb = metadata["size_bytes"] / (1024 * 1024)
            logger.info(f"Backup created: {backup_path} ({size_mb:.2f} MB)")

            return str(backup_path)

        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return None

    def restore_backup(
        self,
        backup_path: str,
        restore_root: str = "."
    ) -> bool:
        """
        Restore from backup archive

        Args:
            backup_path: Path to backup file
            restore_root: Directory to restore to

        Returns:
            True if successful
        """
        try:
            backup_file = Path(backup_path)

            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False

            restore_dir = Path(restore_root)
            restore_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Restoring backup: {backup_file}")

            # Extract tarball
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(restore_dir)

            logger.info(f"Backup restored to: {restore_dir}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return False

    def list_backups(self, name_filter: Optional[str] = None) -> List[dict]:
        """
        List available backups

        Args:
            name_filter: Filter by backup name

        Returns:
            List of backup metadata
        """
        backups = []

        for metadata_file in self.backup_root.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Apply filter
                if name_filter and not metadata['name'].startswith(name_filter):
                    continue

                backups.append(metadata)

            except Exception as e:
                logger.warning(f"Error reading metadata {metadata_file}: {e}")

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)

        return backups

    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period

        Returns:
            Number of backups deleted
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0

        logger.info(f"Cleaning up backups older than {cutoff_date.date()}")

        for metadata_file in self.backup_root.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Parse timestamp
                backup_date = datetime.fromisoformat(metadata['datetime'])

                if backup_date < cutoff_date:
                    # Delete backup file and metadata
                    backup_name = metadata_file.stem  # Remove .json
                    backup_file = self.backup_root / f"{backup_name}.tar.gz"

                    if backup_file.exists():
                        backup_file.unlink()
                        logger.info(f"Deleted old backup: {backup_file.name}")

                    metadata_file.unlink()
                    deleted_count += 1

            except Exception as e:
                logger.warning(f"Error processing {metadata_file}: {e}")

        logger.info(f"Cleanup complete: {deleted_count} backups deleted")
        return deleted_count

    def backup_faiss_index(self, index_path: str) -> Optional[str]:
        """
        Backup FAISS index

        Args:
            index_path: Path to FAISS index file or directory

        Returns:
            Path to backup file
        """
        return self.create_backup(
            name="faiss_index",
            paths=[index_path],
            description="FAISS vector index backup"
        )

    def backup_configs(self, config_dirs: List[str]) -> Optional[str]:
        """
        Backup configuration files

        Args:
            config_dirs: List of config directories

        Returns:
            Path to backup file
        """
        return self.create_backup(
            name="config",
            paths=config_dirs,
            description="Configuration files backup"
        )

    def backup_library(self, library_path: str) -> Optional[str]:
        """
        Backup library data

        Args:
            library_path: Path to library directory

        Returns:
            Path to backup file
        """
        return self.create_backup(
            name="library",
            paths=[library_path],
            description="Library data backup"
        )

    def start_scheduler(
        self,
        interval_hours: int = 24,
        backup_config: Optional[dict] = None
    ):
        """
        Start automated backup scheduler

        Args:
            interval_hours: Hours between backups
            backup_config: Configuration for what to backup
        """
        if self.scheduler_running:
            logger.warning("Backup scheduler already running")
            return

        if backup_config is None:
            backup_config = {
                'faiss_index': None,
                'configs': [],
                'library': None
            }

        self.scheduler_running = True

        def scheduler_loop():
            logger.info(f"Backup scheduler started (interval: {interval_hours}h)")

            while self.scheduler_running:
                try:
                    # Perform backups
                    if backup_config.get('faiss_index'):
                        self.backup_faiss_index(backup_config['faiss_index'])

                    if backup_config.get('configs'):
                        self.backup_configs(backup_config['configs'])

                    if backup_config.get('library'):
                        self.backup_library(backup_config['library'])

                    # Cleanup old backups
                    self.cleanup_old_backups()

                except Exception as e:
                    logger.error(f"Backup scheduler error: {e}", exc_info=True)

                # Sleep until next backup
                for _ in range(interval_hours * 3600):
                    if not self.scheduler_running:
                        break
                    time.sleep(1)

            logger.info("Backup scheduler stopped")

        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """Stop automated backup scheduler"""
        if self.scheduler_running:
            logger.info("Stopping backup scheduler...")
            self.scheduler_running = False

            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)


def create_system_backup(backup_root: str = "backups") -> List[str]:
    """
    Create a full system backup (convenience function)

    Args:
        backup_root: Root directory for backups

    Returns:
        List of backup file paths
    """
    manager = BackupManager(backup_root)
    backup_paths = []

    # Backup configurations
    config_dirs = [
        "VALCORE1/01_Client_Brain/config",
        "VALCORE1/02_Server_Brain/config"
    ]

    existing_configs = [d for d in config_dirs if Path(d).exists()]
    if existing_configs:
        backup_path = manager.backup_configs(existing_configs)
        if backup_path:
            backup_paths.append(backup_path)

    # Backup library
    library_path = Path("/home/user/ValCore1/Library")
    if library_path.exists():
        backup_path = manager.backup_library(str(library_path))
        if backup_path:
            backup_paths.append(backup_path)

    # Backup FAISS indices (if they exist)
    faiss_paths = list(library_path.glob("*.faiss")) if library_path.exists() else []
    for faiss_path in faiss_paths:
        backup_path = manager.backup_faiss_index(str(faiss_path))
        if backup_path:
            backup_paths.append(backup_path)

    logger.info(f"System backup complete: {len(backup_paths)} archives created")
    return backup_paths
