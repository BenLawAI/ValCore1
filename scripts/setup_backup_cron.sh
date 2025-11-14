#!/bin/bash
# Setup automated backups using cron
# This script adds a cron job to run backups daily at 2 AM

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.py"

# Cron schedule: Daily at 2 AM
CRON_SCHEDULE="0 2 * * *"

# Cron command
CRON_COMMAND="$CRON_SCHEDULE cd $SCRIPT_DIR/.. && python3 $BACKUP_SCRIPT >> logs/backup.log 2>&1"

echo "Setting up VALCORE1 automated backups..."
echo ""
echo "Schedule: Daily at 2:00 AM"
echo "Script: $BACKUP_SCRIPT"
echo "Logs: logs/backup.log"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "Backup cron job already exists!"
    echo "Current crontab:"
    crontab -l | grep "$BACKUP_SCRIPT"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    echo "Backup cron job added successfully!"
    echo ""
    echo "To verify:"
    echo "  crontab -l"
    echo ""
    echo "To remove:"
    echo "  crontab -e  # and delete the line"
fi

echo ""
echo "You can also run backups manually:"
echo "  python3 $BACKUP_SCRIPT"
