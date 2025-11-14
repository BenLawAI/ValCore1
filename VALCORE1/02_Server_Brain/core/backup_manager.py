"""
VALCORE1 Backup Manager
Automated backup system for Library data (FAISS index, metadata, etc.)
"""

import os
import logging
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import threading
import time
import schedule

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages automated backups of VALCORE1 data"""

    def __init__(self, source_dir: str, backup_dir: Optional[str] = None):
        """
        Initialize backup manager

        Args:
            source_dir: Directory to backup (e.g., Library/)
            backup_dir: Directory to store backups (defaults to source_dir/../Backups)
        """
        self.source_dir = Path(source_dir)

        if not self.source_dir.exists():
            logger.warning(f"Source directory does not exist: {self.source_dir}")
            self.source_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created source directory: {self.source_dir}")

        # Set backup directory
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            # Default: Backups/ directory next to Library/
            self.backup_dir = self.source_dir.parent / "Backups"

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration from environment
        self.max_backups = int(os.getenv('MAX_BACKUPS', '7'))  # Keep last 7 backups
        self.backup_interval_hours = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))  # Backup every 24 hours

        # Scheduler
        self.scheduler_running = False
        self.scheduler_thread = None

        logger.info(f"Backup manager initialized")
        logger.info(f"Source: {self.source_dir}")
        logger.info(f"Backup: {self.backup_dir}")
        logger.info(f"Max backups: {self.max_backups}, Interval: {self.backup_interval_hours}h")

    def create_backup(self, tag: Optional[str] = None) -> Optional[Path]:
        """
        Create a backup of the source directory

        Args:
            tag: Optional tag to add to backup name (e.g., 'manual', 'pre-update')

        Returns:
            Path to backup directory, or None if backup failed
        """
        try:
            # Generate backup name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"

            if tag:
                backup_name += f"_{tag}"

            backup_path = self.backup_dir / backup_name

            logger.info(f"Creating backup: {backup_name}")

            # Check if source directory is empty
            if not any(self.source_dir.iterdir()):
                logger.warning("Source directory is empty, skipping backup")
                return None

            # Copy entire directory
            shutil.copytree(self.source_dir, backup_path)

            # Create backup metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "source": str(self.source_dir),
                "backup_path": str(backup_path),
                "tag": tag,
                "files_backed_up": self._count_files(backup_path)
            }

            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Backup created successfully: {backup_path}")
            logger.info(f"Files backed up: {metadata['files_backed_up']}")

            # Cleanup old backups
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return None

    def restore_backup(self, backup_name: str, clear_existing: bool = False) -> bool:
        """
        Restore from a backup

        Args:
            backup_name: Name of backup to restore (e.g., 'backup_20250114_120000')
            clear_existing: If True, delete existing data before restore (default: False)

        Returns:
            True if restore successful
        """
        try:
            backup_path = self.backup_dir / backup_name

            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False

            logger.info(f"Restoring from backup: {backup_name}")

            # Clear existing data if requested
            if clear_existing:
                logger.warning("Clearing existing data before restore")
                if self.source_dir.exists():
                    shutil.rmtree(self.source_dir)
                self.source_dir.mkdir(parents=True, exist_ok=True)

            # Copy files from backup (skip backup_metadata.json)
            for item in backup_path.iterdir():
                if item.name == "backup_metadata.json":
                    continue

                dest = self.source_dir / item.name

                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

            logger.info(f"Restore completed successfully from: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return False

    def list_backups(self) -> List[dict]:
        """
        List all available backups

        Returns:
            List of backup info dictionaries
        """
        backups = []

        try:
            for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
                if not backup_dir.is_dir():
                    continue

                # Read metadata if available
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                else:
                    # Create basic metadata from directory
                    metadata = {
                        "backup_name": backup_dir.name,
                        "path": str(backup_dir),
                        "size_mb": self._get_dir_size(backup_dir) / (1024 * 1024),
                        "files": self._count_files(backup_dir)
                    }

                metadata["backup_name"] = backup_dir.name
                backups.append(metadata)

        except Exception as e:
            logger.error(f"Error listing backups: {e}")

        return backups

    def _cleanup_old_backups(self):
        """Delete old backups beyond max_backups limit"""
        try:
            backups = sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True  # Newest first
            )

            if len(backups) > self.max_backups:
                for old_backup in backups[self.max_backups:]:
                    logger.info(f"Deleting old backup: {old_backup.name}")
                    shutil.rmtree(old_backup)

        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")

    def _count_files(self, directory: Path) -> int:
        """Count files in directory recursively"""
        return sum(1 for _ in directory.rglob('*') if _.is_file())

    def _get_dir_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        return sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())

    def start_scheduled_backups(self):
        """Start automated backup scheduler"""
        if self.scheduler_running:
            logger.warning("Scheduler already running")
            return

        logger.info(f"Starting backup scheduler (interval: {self.backup_interval_hours}h)")

        # Schedule backup
        schedule.every(self.backup_interval_hours).hours.do(
            lambda: self.create_backup(tag="scheduled")
        )

        # Run scheduler in background thread
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info("Backup scheduler started")

    def _run_scheduler(self):
        """Run scheduler loop (runs in background thread)"""
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop_scheduled_backups(self):
        """Stop automated backup scheduler"""
        if not self.scheduler_running:
            return

        logger.info("Stopping backup scheduler")
        self.scheduler_running = False

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        schedule.clear()
        logger.info("Backup scheduler stopped")

    def get_stats(self) -> dict:
        """
        Get backup statistics

        Returns:
            Statistics dictionary
        """
        backups = self.list_backups()

        total_size = sum(
            self._get_dir_size(self.backup_dir / b['backup_name'])
            for b in backups
        )

        return {
            "total_backups": len(backups),
            "total_size_mb": total_size / (1024 * 1024),
            "max_backups": self.max_backups,
            "backup_interval_hours": self.backup_interval_hours,
            "source_dir": str(self.source_dir),
            "backup_dir": str(self.backup_dir),
            "scheduler_running": self.scheduler_running
        }
