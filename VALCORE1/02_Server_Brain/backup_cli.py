#!/usr/bin/env python3
"""
VALCORE1 Backup CLI Tool
Command-line interface for manual backup management
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.backup_manager import BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_backup(args):
    """Create a new backup"""
    backup_manager = BackupManager(args.source, args.backup_dir)

    backup_path = backup_manager.create_backup(tag=args.tag)

    if backup_path:
        print(f"✓ Backup created successfully: {backup_path}")
        return 0
    else:
        print("✗ Backup failed")
        return 1


def list_backups(args):
    """List all backups"""
    backup_manager = BackupManager(args.source, args.backup_dir)

    backups = backup_manager.list_backups()

    if not backups:
        print("No backups found")
        return 0

    print(f"\n{'Backup Name':<40} {'Timestamp':<25} {'Files':<10} {'Size (MB)':<15}")
    print("=" * 90)

    for backup in backups:
        name = backup.get('backup_name', 'N/A')
        timestamp = backup.get('timestamp', 'N/A')
        files = backup.get('files_backed_up', backup.get('files', 'N/A'))

        # Calculate size
        backup_dir = Path(args.backup_dir or (Path(args.source).parent / "Backups"))
        backup_path = backup_dir / name
        size_mb = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file()) / (1024 * 1024)

        # Format timestamp
        if timestamp != 'N/A':
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass

        print(f"{name:<40} {timestamp:<25} {files:<10} {size_mb:<15.2f}")

    print()
    return 0


def restore_backup(args):
    """Restore from a backup"""
    backup_manager = BackupManager(args.source, args.backup_dir)

    # Confirm if clear_existing is set
    if args.clear_existing:
        print(f"⚠️  WARNING: This will DELETE all existing data in {args.source}")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Restore cancelled")
            return 0

    success = backup_manager.restore_backup(args.backup_name, clear_existing=args.clear_existing)

    if success:
        print(f"✓ Restore completed successfully from: {args.backup_name}")
        return 0
    else:
        print("✗ Restore failed")
        return 1


def get_stats(args):
    """Display backup statistics"""
    backup_manager = BackupManager(args.source, args.backup_dir)

    stats = backup_manager.get_stats()

    print("\n=== Backup Statistics ===")
    print(f"Source directory:     {stats['source_dir']}")
    print(f"Backup directory:     {stats['backup_dir']}")
    print(f"Total backups:        {stats['total_backups']}")
    print(f"Total size:           {stats['total_size_mb']:.2f} MB")
    print(f"Max backups kept:     {stats['max_backups']}")
    print(f"Backup interval:      {stats['backup_interval_hours']} hours")
    print(f"Scheduler running:    {stats['scheduler_running']}")
    print()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="VALCORE1 Backup Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a backup with a tag
  python backup_cli.py create --tag manual

  # List all backups
  python backup_cli.py list

  # Restore from a specific backup
  python backup_cli.py restore backup_20250114_120000

  # Restore and clear existing data
  python backup_cli.py restore backup_20250114_120000 --clear-existing

  # Show backup statistics
  python backup_cli.py stats
        """
    )

    # Global arguments
    parser.add_argument(
        '--source',
        default='/home/user/ValCore1/Library',
        help='Source directory to backup (default: /home/user/ValCore1/Library)'
    )

    parser.add_argument(
        '--backup-dir',
        default=None,
        help='Backup directory (default: source/../Backups)'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create backup
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument(
        '--tag',
        default=None,
        help='Optional tag for the backup (e.g., manual, pre-update)'
    )

    # List backups
    list_parser = subparsers.add_parser('list', help='List all backups')

    # Restore backup
    restore_parser = subparsers.add_parser('restore', help='Restore from a backup')
    restore_parser.add_argument(
        'backup_name',
        help='Name of the backup to restore (e.g., backup_20250114_120000)'
    )
    restore_parser.add_argument(
        '--clear-existing',
        action='store_true',
        help='Delete existing data before restoring (DANGEROUS!)'
    )

    # Statistics
    stats_parser = subparsers.add_parser('stats', help='Show backup statistics')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        if args.command == 'create':
            return create_backup(args)
        elif args.command == 'list':
            return list_backups(args)
        elif args.command == 'restore':
            return restore_backup(args)
        elif args.command == 'stats':
            return get_stats(args)
        else:
            parser.print_help()
            return 1

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
