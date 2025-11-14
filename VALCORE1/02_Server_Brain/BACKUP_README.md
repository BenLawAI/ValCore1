# VALCORE1 Backup System

## Overview

The VALCORE1 backup system provides automated and manual backup capabilities for the Library directory (FAISS index, metadata, and conversation history). This ensures your data is protected against accidental loss or corruption.

## Features

- **Automated Backups**: Schedule regular backups (default: every 24 hours)
- **Manual Backups**: Create backups on-demand via CLI
- **Startup Backups**: Automatically backup on server startup
- **Automatic Cleanup**: Old backups are automatically deleted (keeps last 7 by default)
- **Easy Restore**: Simple CLI commands to restore from any backup
- **Backup Metadata**: Each backup includes metadata (timestamp, file count, etc.)

## Configuration

Configure backup behavior via environment variables in `.env`:

```bash
# Maximum number of backups to keep (default: 7)
MAX_BACKUPS=7

# Backup interval in hours (default: 24)
BACKUP_INTERVAL_HOURS=24

# Create backup on server startup (default: true)
BACKUP_ON_STARTUP=true

# Custom backup directory (optional)
BACKUP_DIR=/path/to/custom/backup/directory
```

## Automated Backups

Automated backups run in the background when the server is running:

1. **Startup Backup**: Created when server starts (if `BACKUP_ON_STARTUP=true`)
2. **Scheduled Backups**: Created every `BACKUP_INTERVAL_HOURS` hours
3. **Automatic Cleanup**: Old backups beyond `MAX_BACKUPS` limit are deleted

Automated backups are tagged with `startup` or `scheduled` for easy identification.

## Manual Backup Management

Use the `backup_cli.py` tool for manual backup operations:

### Create a Backup

```bash
# Create a backup with default settings
python backup_cli.py create

# Create a backup with a custom tag
python backup_cli.py create --tag manual
python backup_cli.py create --tag pre-update
python backup_cli.py create --tag "before-migration"
```

### List All Backups

```bash
python backup_cli.py list
```

Output example:
```
Backup Name                              Timestamp                 Files      Size (MB)
==========================================================================================
backup_20250114_120000_startup           2025-01-14 12:00:00      42         125.43
backup_20250113_120000_scheduled         2025-01-13 12:00:00      38         118.92
backup_20250112_150000_manual            2025-01-12 15:00:00      35         112.34
```

### Show Backup Statistics

```bash
python backup_cli.py stats
```

Output example:
```
=== Backup Statistics ===
Source directory:     /home/user/ValCore1/Library
Backup directory:     /home/user/ValCore1/Backups
Total backups:        7
Total size:           856.21 MB
Max backups kept:     7
Backup interval:      24 hours
Scheduler running:    True
```

### Restore from a Backup

⚠️ **IMPORTANT**: Always stop the server before restoring to avoid data corruption.

```bash
# Stop the server first!
# Then restore from a specific backup (merges with existing data)
python backup_cli.py restore backup_20250114_120000_startup

# Restore and CLEAR all existing data first (DANGEROUS!)
python backup_cli.py restore backup_20250114_120000_startup --clear-existing
```

**Restore Options**:
- **Default behavior**: Restores backup files, existing files are overwritten
- **`--clear-existing` flag**: DELETES all existing data before restore (use with caution!)

### Custom Source/Backup Directories

```bash
# Specify custom directories
python backup_cli.py create --source /path/to/library --backup-dir /path/to/backups
python backup_cli.py list --source /path/to/library --backup-dir /path/to/backups
```

## Backup Structure

Backups are stored in the `Backups/` directory (default location: next to `Library/`):

```
Backups/
├── backup_20250114_120000_startup/
│   ├── backup_metadata.json       # Backup metadata
│   ├── faiss_index.bin           # FAISS vector index
│   ├── metadata.json             # Conversation metadata
│   └── [other library files]
├── backup_20250113_120000_scheduled/
│   └── ...
└── backup_20250112_150000_manual/
    └── ...
```

Each backup directory contains:
- **backup_metadata.json**: Metadata about the backup (timestamp, file count, etc.)
- **All Library files**: Complete copy of Library directory contents

## Best Practices

### Regular Backups
- Keep automated backups enabled (default: every 24 hours)
- Adjust `BACKUP_INTERVAL_HOURS` based on data change frequency
- More frequent conversations = more frequent backups

### Manual Backups
Create manual backups before:
- Major system updates
- Configuration changes
- Experimental features
- Database migrations

```bash
python backup_cli.py create --tag pre-update
```

### Backup Retention
- Default: 7 backups (1 week with daily backups)
- Adjust `MAX_BACKUPS` based on available disk space
- Calculate storage: ~150MB per backup (varies with data size)

### Disaster Recovery
1. Stop the server
2. List available backups: `python backup_cli.py list`
3. Restore from most recent good backup
4. Restart the server

### Monitoring
- Check backup statistics regularly: `python backup_cli.py stats`
- Monitor backup size growth
- Verify backups are being created (check logs)

## Integration with Server

The backup system is automatically integrated into `main_server.py`:

```python
# Backup manager is initialized on server startup
self.backup_manager = BackupManager(library_path)

# Scheduled backups start automatically
self.backup_manager.start_scheduled_backups()

# Initial backup created on startup (if enabled)
self.backup_manager.create_backup(tag='startup')

# Backups stop gracefully on shutdown
self.backup_manager.stop_scheduled_backups()
```

## Backup Logs

Backup operations are logged to the server log file:

```
2025-01-14 12:00:00 - INFO - Backup manager initialized
2025-01-14 12:00:00 - INFO - Source: /home/user/ValCore1/Library
2025-01-14 12:00:00 - INFO - Backup: /home/user/ValCore1/Backups
2025-01-14 12:00:00 - INFO - Starting backup scheduler (interval: 24h)
2025-01-14 12:00:05 - INFO - Creating backup: backup_20250114_120005_startup
2025-01-14 12:00:06 - INFO - Backup created successfully: /home/user/ValCore1/Backups/backup_20250114_120005_startup
2025-01-14 12:00:06 - INFO - Files backed up: 42
```

## Troubleshooting

### Backup Failed
- Check disk space: `df -h`
- Check permissions on Library and Backups directories
- Check server logs for error details

### Restore Failed
- Ensure server is stopped
- Verify backup exists: `python backup_cli.py list`
- Check backup integrity (backup_metadata.json should exist)
- Check permissions on Library directory

### Scheduler Not Running
- Check `backup_cli.py stats` - shows scheduler status
- Verify server is running
- Check for errors in server logs
- Ensure `schedule` package is installed: `pip install schedule`

### Large Backup Size
- Normal growth over time as conversations accumulate
- Consider adjusting `MAX_BACKUPS` if disk space is limited
- FAISS index size grows with conversation count
- Typical size: 100-200MB per backup (varies)

## Security Considerations

### .gitignore
The `Backups/` directory is automatically excluded from git to prevent:
- Committing large binary files
- Exposing conversation history
- Repository bloat

### Access Control
- Backups contain full conversation history
- Store backups on secure, access-controlled storage
- Consider encrypting backups for additional security

### Network Backups
For additional safety, consider copying backups to network storage:

```bash
# Example: Copy backups to network drive
rsync -av /home/user/ValCore1/Backups/ /mnt/network/valcore1_backups/
```

## Advanced Usage

### Programmatic Backup Creation

```python
from core.backup_manager import BackupManager

# Initialize
backup_mgr = BackupManager('/home/user/ValCore1/Library')

# Create manual backup
backup_path = backup_mgr.create_backup(tag='my-custom-tag')

# List backups
backups = backup_mgr.list_backups()

# Restore
success = backup_mgr.restore_backup('backup_20250114_120000_startup')

# Get statistics
stats = backup_mgr.get_stats()
```

### Custom Backup Schedule

Modify the backup interval via environment variables:

```bash
# Hourly backups
BACKUP_INTERVAL_HOURS=1

# Backup every 12 hours
BACKUP_INTERVAL_HOURS=12

# Backup every 3 days
BACKUP_INTERVAL_HOURS=72
```

## Support

For issues or questions about the backup system:
1. Check server logs: `logs/valcore1_server.log`
2. Review this documentation
3. Check backup statistics: `python backup_cli.py stats`
4. Verify configuration in `.env` file
