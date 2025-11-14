"""
Unit tests for BackupManager
Tests the automated backup system for Library data
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime

# Import BackupManager
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_Server_Brain"))
from core.backup_manager import BackupManager


@pytest.mark.unit
class TestBackupManager:
    """Test suite for BackupManager class"""

    def test_initialization(self, temp_library_dir, temp_backup_dir):
        """Test BackupManager initialization"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        assert backup_mgr.source_dir == temp_library_dir
        assert backup_mgr.backup_dir == temp_backup_dir
        assert backup_mgr.max_backups == 7  # Default value
        assert backup_mgr.backup_interval_hours == 24  # Default value

    def test_initialization_creates_directories(self, temp_dir):
        """Test that initialization creates missing directories"""
        source_dir = temp_dir / "new_library"
        backup_dir = temp_dir / "new_backups"

        # Directories don't exist yet
        assert not source_dir.exists()
        assert not backup_dir.exists()

        backup_mgr = BackupManager(
            source_dir=str(source_dir),
            backup_dir=str(backup_dir)
        )

        # Directories should be created
        assert source_dir.exists()
        assert backup_dir.exists()

    def test_create_backup(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test creating a backup"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create backup
        backup_path = backup_mgr.create_backup(tag="test")

        # Verify backup was created
        assert backup_path is not None
        assert backup_path.exists()
        assert "test" in backup_path.name

        # Verify backup contains metadata file
        metadata_file = backup_path / "backup_metadata.json"
        assert metadata_file.exists()

        # Verify metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert metadata['tag'] == "test"
        assert 'timestamp' in metadata
        assert 'files_backed_up' in metadata

    def test_create_backup_empty_source(self, temp_library_dir, temp_backup_dir):
        """Test creating backup with empty source directory"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Source is empty
        backup_path = backup_mgr.create_backup(tag="empty")

        # Should skip empty directory
        assert backup_path is None

    def test_list_backups(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test listing backups"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create multiple backups
        backup_mgr.create_backup(tag="first")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        backup_mgr.create_backup(tag="second")

        # List backups
        backups = backup_mgr.list_backups()

        assert len(backups) == 2
        assert any('first' in b.get('tag', '') for b in backups)
        assert any('second' in b.get('tag', '') for b in backups)

    def test_restore_backup(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test restoring from a backup"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create backup
        backup_path = backup_mgr.create_backup(tag="restore_test")
        backup_name = backup_path.name

        # Modify source data
        metadata_file = temp_library_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump([], f)  # Empty metadata

        # Restore backup
        success = backup_mgr.restore_backup(backup_name)

        assert success is True

        # Verify data was restored
        with open(metadata_file, 'r') as f:
            restored_metadata = json.load(f)

        assert len(restored_metadata) > 0  # Should have original data

    def test_restore_backup_clear_existing(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test restoring with clear_existing flag"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create backup
        backup_path = backup_mgr.create_backup(tag="clear_test")
        backup_name = backup_path.name

        # Add extra file to source
        extra_file = temp_library_dir / "extra_file.txt"
        extra_file.write_text("This should be deleted")

        # Restore with clear_existing
        success = backup_mgr.restore_backup(backup_name, clear_existing=True)

        assert success is True
        # Extra file should be gone
        assert not extra_file.exists()

    def test_restore_nonexistent_backup(self, temp_library_dir, temp_backup_dir):
        """Test restoring from a non-existent backup"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Try to restore non-existent backup
        success = backup_mgr.restore_backup("nonexistent_backup")

        assert success is False

    def test_cleanup_old_backups(self, temp_library_dir, temp_backup_dir, sample_faiss_data, monkeypatch):
        """Test automatic cleanup of old backups"""
        # Set max_backups to 3
        monkeypatch.setenv('MAX_BACKUPS', '3')

        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create 5 backups
        for i in range(5):
            backup_mgr.create_backup(tag=f"backup_{i}")
            time.sleep(0.1)  # Ensure different timestamps

        # Should only have 3 backups (oldest deleted)
        backups = backup_mgr.list_backups()
        assert len(backups) <= 3

    def test_get_stats(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test getting backup statistics"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Create a backup
        backup_mgr.create_backup(tag="stats_test")

        # Get stats
        stats = backup_mgr.get_stats()

        assert 'total_backups' in stats
        assert 'total_size_mb' in stats
        assert 'max_backups' in stats
        assert 'backup_interval_hours' in stats
        assert 'source_dir' in stats
        assert 'backup_dir' in stats
        assert 'scheduler_running' in stats

        assert stats['total_backups'] == 1
        assert stats['max_backups'] == 7  # Default

    def test_scheduled_backups_start_stop(self, temp_library_dir, temp_backup_dir):
        """Test starting and stopping scheduled backups"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # Start scheduler
        backup_mgr.start_scheduled_backups()
        assert backup_mgr.scheduler_running is True

        # Stop scheduler
        backup_mgr.stop_scheduled_backups()
        assert backup_mgr.scheduler_running is False

    def test_environment_variable_override(self, temp_library_dir, temp_backup_dir, monkeypatch):
        """Test environment variable configuration"""
        monkeypatch.setenv('MAX_BACKUPS', '5')
        monkeypatch.setenv('BACKUP_INTERVAL_HOURS', '12')

        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        assert backup_mgr.max_backups == 5
        assert backup_mgr.backup_interval_hours == 12


@pytest.mark.integration
class TestBackupManagerIntegration:
    """Integration tests for BackupManager"""

    def test_full_backup_restore_cycle(self, temp_library_dir, temp_backup_dir, sample_faiss_data):
        """Test complete backup and restore workflow"""
        backup_mgr = BackupManager(
            source_dir=str(temp_library_dir),
            backup_dir=str(temp_backup_dir)
        )

        # 1. Create initial backup
        backup1 = backup_mgr.create_backup(tag="initial")
        assert backup1 is not None

        # 2. Modify data
        metadata_file = temp_library_dir / "metadata.json"
        with open(metadata_file, 'r') as f:
            original_data = json.load(f)

        modified_data = original_data + [{"test": "new_entry"}]
        with open(metadata_file, 'w') as f:
            json.dump(modified_data, f)

        # 3. Create second backup
        backup2 = backup_mgr.create_backup(tag="modified")
        assert backup2 is not None

        # 4. List backups
        backups = backup_mgr.list_backups()
        assert len(backups) == 2

        # 5. Restore first backup
        success = backup_mgr.restore_backup(backup1.name)
        assert success is True

        # 6. Verify data matches original
        with open(metadata_file, 'r') as f:
            restored_data = json.load(f)

        assert len(restored_data) == len(original_data)
