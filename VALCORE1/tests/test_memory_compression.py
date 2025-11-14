"""
Unit tests for Memory Compression
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "02_Server_Brain"))

from core.memory_compression import MemoryCompressor


@pytest.fixture
def compression_config(temp_dir):
    """Create compression config file"""
    config = {
        "daily_compression": {
            "target_tokens": 2000,
            "preserve_categories": ["decision", "action_item", "error"],
            "discard_categories": ["greeting", "acknowledgment"],
            "semantic_importance": {
                "high": {"threshold": 0.7, "keep_percentage": 100},
                "medium": {"threshold": 0.4, "keep_percentage": 50},
                "low": {"threshold": 0.0, "keep_percentage": 10}
            }
        },
        "backup_before_compression": True,
        "daily": {
            "time": "02:00"
        }
    }

    config_file = temp_dir / "compression_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def mock_librarian_for_compression(temp_dir):
    """Mock librarian with library path"""
    librarian = Mock()
    librarian.library_path = str(temp_dir / "library")
    Path(librarian.library_path).mkdir(exist_ok=True)
    return librarian


@pytest.fixture
def compressor(compression_config, mock_librarian_for_compression):
    """Create MemoryCompressor instance"""
    return MemoryCompressor(str(compression_config), mock_librarian_for_compression)


@pytest.mark.unit
class TestMemoryCompressor:
    """Test MemoryCompressor class"""

    def test_initialization(self, compressor):
        """Test compressor initializes correctly"""
        assert compressor is not None
        assert compressor.config is not None

    def test_score_semantic_importance_no_embedder(self, compressor):
        """Test importance scoring without embedder"""
        compressor.embedder = None

        # Preserved category should score high
        score = compressor.score_semantic_importance("Important decision", "decision")
        assert score == 0.9

        # Discarded category should score low
        score = compressor.score_semantic_importance("Hello", "greeting")
        assert score == 0.3

        # Unknown category should score medium
        score = compressor.score_semantic_importance("Test", "unknown")
        assert score == 0.5

    def test_catchup_compression_no_directory(self, compressor, temp_dir):
        """Test catchup when no daily directory exists"""
        # Should not raise exception
        compressor._catchup_compression()

    def test_catchup_compression_no_previous(self, compressor, temp_dir):
        """Test catchup when no previous compressions"""
        library_path = Path(compressor.librarian.library_path)
        daily_path = library_path / "daily"
        daily_path.mkdir(parents=True, exist_ok=True)

        # Create mock compress_daily_summary method
        compressor.compress_daily_summary = Mock()

        compressor._catchup_compression()

        # Should compress yesterday
        assert compressor.compress_daily_summary.call_count == 1

    def test_catchup_compression_up_to_date(self, compressor, temp_dir):
        """Test catchup when compression is up to date"""
        library_path = Path(compressor.librarian.library_path)
        daily_path = library_path / "daily"
        daily_path.mkdir(parents=True, exist_ok=True)

        # Create a recent compressed file (yesterday)
        yesterday = datetime.now() - timedelta(days=1)
        compressed_file = daily_path / f"{yesterday:%Y-%m-%d}_compressed.json"
        compressed_file.write_text(json.dumps({"date": yesterday.isoformat()}))

        compressor.compress_daily_summary = Mock()

        compressor._catchup_compression()

        # Should not compress anything
        assert compressor.compress_daily_summary.call_count == 0

    def test_catchup_compression_behind(self, compressor, temp_dir):
        """Test catchup when several days behind"""
        library_path = Path(compressor.librarian.library_path)
        daily_path = library_path / "daily"
        daily_path.mkdir(parents=True, exist_ok=True)

        # Create a compressed file from 3 days ago
        three_days_ago = datetime.now() - timedelta(days=3)
        compressed_file = daily_path / f"{three_days_ago:%Y-%m-%d}_compressed.json"
        compressed_file.write_text(json.dumps({"date": three_days_ago.isoformat()}))

        compressor.compress_daily_summary = Mock()

        compressor._catchup_compression()

        # Should compress 2 days (day before yesterday and yesterday)
        # Not today
        assert compressor.compress_daily_summary.call_count == 2

    def test_compress_daily_summary_no_data(self, compressor, temp_dir):
        """Test compressing day with no data"""
        date = datetime.now() - timedelta(days=1)
        result = compressor.compress_daily_summary(date)

        assert result == {}

    def test_compress_daily_summary_with_data(self, compressor, temp_dir):
        """Test compressing day with data"""
        library_path = Path(compressor.librarian.library_path)
        daily_path = library_path / "daily"
        daily_path.mkdir(parents=True, exist_ok=True)

        # Create sample data
        date = datetime.now() - timedelta(days=1)
        daily_file = daily_path / f"{date:%Y-%m-%d}.json"

        sample_conversations = [
            {"text": "We decided to use Python", "category": "decision"},
            {"text": "This is an action item", "category": "action_item"},
            {"text": "Hello there", "category": "greeting"}
        ]

        with open(daily_file, 'w') as f:
            json.dump(sample_conversations, f)

        result = compressor.compress_daily_summary(date)

        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'key_decisions' in result
        assert 'action_items' in result
        assert len(result['key_decisions']) == 1
        assert len(result['action_items']) == 1

    def test_daily_compression_job(self, compressor):
        """Test daily compression job"""
        compressor.compress_daily_summary = Mock()

        compressor.daily_compression_job()

        # Should call compress_daily_summary once with yesterday's date
        assert compressor.compress_daily_summary.call_count == 1
        call_args = compressor.compress_daily_summary.call_args[0]
        assert len(call_args) == 1
        # Check that the date is approximately yesterday
        yesterday = datetime.now() - timedelta(days=1)
        assert call_args[0].date() == yesterday.date()
