#!/usr/bin/env python3
"""
VALCORE1 Log Cleanup Script
Manually clean up old log files
"""

import sys
import logging
from pathlib import Path

# Add VALCORE1 to path
valcore_path = Path(__file__).parent.parent / "VALCORE1" / "03_Shared"
sys.path.insert(0, str(valcore_path))

from logging_config import cleanup_old_logs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run log cleanup"""
    logger.info("="*60)
    logger.info("VALCORE1 LOG CLEANUP")
    logger.info("="*60)

    # Default: keep logs for 90 days
    max_age_days = 90

    if len(sys.argv) > 1:
        try:
            max_age_days = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid days value: {sys.argv[1]}")
            sys.exit(1)

    logger.info(f"Cleaning up logs older than {max_age_days} days")

    try:
        cleanup_old_logs(log_dir="logs", max_age_days=max_age_days)
        logger.info("Log cleanup complete")

    except Exception as e:
        logger.error(f"Log cleanup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
