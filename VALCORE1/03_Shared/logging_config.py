"""
VALCORE1 Logging Configuration
Centralized logging setup with rotation, formatting, and filtering
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs"""

    SENSITIVE_PATTERNS = [
        'password',
        'token',
        'api_key',
        'secret',
        'authorization',
        'bearer',
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact sensitive data

        Args:
            record: Log record

        Returns:
            True (always pass, but may modify message)
        """
        message = record.getMessage().lower()

        # Check if message contains sensitive keywords
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                # Redact the message
                record.msg = f"[REDACTED: Message contains '{pattern}']"
                record.args = ()
                break

        return True


def setup_logging(
    name: str = "VALCORE1",
    log_dir: str = "logs",
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 10,
    console_output: bool = True,
    filter_sensitive: bool = True
) -> logging.Logger:
    """
    Setup logging with rotation and formatting

    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of backup files to keep
        console_output: Also log to console
        filter_sensitive: Filter sensitive data from logs

    Returns:
        Configured logger
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create sensitive data filter if enabled
    sensitive_filter = SensitiveDataFilter() if filter_sensitive else None

    # File Handler with Rotation (detailed logs)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{name.lower()}.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    if sensitive_filter:
        file_handler.addFilter(sensitive_filter)

    logger.addHandler(file_handler)

    # Error File Handler (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{name.lower()}_errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    if sensitive_filter:
        error_handler.addFilter(sensitive_filter)

    logger.addHandler(error_handler)

    # Console Handler (if enabled)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        if sensitive_filter:
            console_handler.addFilter(sensitive_filter)

        logger.addHandler(console_handler)

    # Time-based rotation handler (daily rotation)
    timed_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_path / f"{name.lower()}_daily.log",
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding='utf-8'
    )
    timed_handler.setLevel(logging.INFO)
    timed_handler.setFormatter(simple_formatter)
    timed_handler.suffix = "%Y%m%d"  # Append date to rotated files

    if sensitive_filter:
        timed_handler.addFilter(sensitive_filter)

    logger.addHandler(timed_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    logger.info(f"Logging initialized: {name}")
    logger.info(f"Log directory: {log_path.absolute()}")
    logger.info(f"Log level: {level}")
    logger.info(f"Max file size: {max_bytes / (1024*1024):.1f} MB")
    logger.info(f"Backup count: {backup_count}")
    logger.info(f"Sensitive data filtering: {filter_sensitive}")

    return logger


def setup_component_logging(
    component: str,
    parent_logger: str = "VALCORE1",
    level: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging for a specific component

    Args:
        component: Component name (e.g., "client_brain", "server_brain")
        parent_logger: Parent logger name
        level: Log level (inherits from parent if None)

    Returns:
        Component logger
    """
    logger_name = f"{parent_logger}.{component}"
    logger = logging.getLogger(logger_name)

    if level:
        logger.setLevel(getattr(logging, level.upper()))

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def cleanup_old_logs(log_dir: str = "logs", max_age_days: int = 90):
    """
    Clean up old log files

    Args:
        log_dir: Log directory
        max_age_days: Maximum age of log files to keep
    """
    import time

    log_path = Path(log_dir)

    if not log_path.exists():
        return

    current_time = time.time()
    cutoff_time = current_time - (max_age_days * 24 * 3600)
    deleted_count = 0

    for log_file in log_path.glob("*.log*"):
        # Skip current log files (without date suffix)
        if not any(char.isdigit() for char in log_file.suffix):
            continue

        # Check file age
        file_mtime = log_file.stat().st_mtime

        if file_mtime < cutoff_time:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                logging.warning(f"Failed to delete old log {log_file}: {e}")

    if deleted_count > 0:
        logging.info(f"Cleaned up {deleted_count} old log files")


# Example usage configuration
def configure_valcore_logging():
    """Configure logging for the entire VALCORE1 system"""

    # Main system logger
    main_logger = setup_logging(
        name="VALCORE1",
        log_dir="logs",
        level=os.getenv("LOG_LEVEL", "INFO"),
        max_bytes=10 * 1024 * 1024,  # 10 MB
        backup_count=10,
        console_output=True,
        filter_sensitive=True
    )

    # Component loggers
    client_logger = setup_component_logging("client_brain", level="INFO")
    server_logger = setup_component_logging("server_brain", level="INFO")
    librarian_logger = setup_component_logging("librarian", level="INFO")
    llm_logger = setup_component_logging("llm", level="INFO")

    # Cleanup old logs
    cleanup_old_logs(max_age_days=90)

    return main_logger
