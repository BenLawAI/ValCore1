#!/usr/bin/env python3
"""
VALCORE1 Manual Backup Script
Run this script to create a manual backup of all critical data
"""

import sys
import logging
from pathlib import Path

# Add VALCORE1 to path
valcore_path = Path(__file__).parent.parent / "VALCORE1" / "03_Shared"
sys.path.insert(0, str(valcore_path))

from backup_manager import create_system_backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run manual backup"""
    logger.info("="*60)
    logger.info("VALCORE1 MANUAL BACKUP")
    logger.info("="*60)

    try:
        backup_paths = create_system_backup()

        logger.info("")
        logger.info("="*60)
        logger.info(f"BACKUP COMPLETE: {len(backup_paths)} archives created")
        logger.info("="*60)

        for path in backup_paths:
            logger.info(f"  - {path}")

        logger.info("")
        logger.info("Backups saved to: backups/")
        logger.info("To restore, use the BackupManager.restore_backup() method")

    except Exception as e:
        logger.error(f"Backup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
