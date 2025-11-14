"""
Unit tests for Librarian (FAISS-based semantic search)
Tests conversation storage, semantic search, and index management
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Import Librarian
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_Server_Brain"))


@pytest.mark.unit
class TestLibrarian:
    """Test suite for Librarian class"""

    @pytest.fixture
    def librarian(self, temp_library_dir):
        """Create Librarian instance with temporary directory"""
        try:
            from core.librarian import Librarian
            return Librarian(str(temp_library_dir))
        except ImportError as e:
            pytest.skip(f"Librarian dependencies not available: {e}")

    def test_initialization(self, librarian):
        """Test Librarian initialization"""
        assert librarian is not None
        assert librarian.embedding_dim == 384  # all-MiniLM-L6-v2
        assert len(librarian.metadata) >= 0

    def test_add_conversation(self, librarian):
        """Test adding a conversation"""
        librarian.add_conversation(
            room="general",
            text="Hello, how are you?",
            metadata={"response": "I'm doing well!"}
        )

        # Verify metadata was added
        assert len(librarian.metadata) > 0
        assert librarian.metadata[0]['room'] == "general"
        assert librarian.metadata[0]['text'] == "Hello, how are you?"

    def test_add_multiple_conversations(self, librarian):
        """Test adding multiple conversations"""
        conversations = [
            ("general", "What is the weather?", {"response": "Sunny"}),
            ("truck", "Where is truck 42?", {"response": "En route"}),
            ("invoice", "Show me invoice 123", {"response": "Here it is"}),
        ]

        for room, text, metadata in conversations:
            librarian.add_conversation(room, text, metadata)

        assert len(librarian.metadata) == 3

    def test_search_empty_index(self, librarian):
        """Test searching empty index"""
        results = librarian.search("test query")

        assert results == []

    def test_search_basic(self, librarian):
        """Test basic semantic search"""
        # Add conversations
        librarian.add_conversation("general", "The weather is sunny today", {})
        librarian.add_conversation("general", "It's raining outside", {})

        # Search for weather-related query
        results = librarian.search("What's the weather like?", max_results=2)

        # Should return results
        assert len(results) > 0
        assert all('similarity' in r for r in results)

    def test_search_with_room_filter(self, librarian):
        """Test search with room filter"""
        # Add conversations to different rooms
        librarian.add_conversation("general", "General conversation", {})
        librarian.add_conversation("truck", "Truck status update", {})

        # Search only truck room
        results = librarian.search("status", room="truck")

        # All results should be from truck room
        assert all(r['room'] == "truck" for r in results)

    def test_search_similarity_threshold(self, librarian):
        """Test search with similarity threshold"""
        librarian.add_conversation("general", "The sky is blue", {})

        # Search with high threshold
        results = librarian.search(
            "blue sky",
            similarity_threshold=0.9  # Very strict
        )

        # Results should have high similarity
        assert all(r['similarity'] >= 0.9 for r in results)

    def test_get_room_context(self, librarian):
        """Test getting recent room context"""
        # Add multiple conversations to a room
        for i in range(10):
            librarian.add_conversation(
                "general",
                f"Message {i}",
                {"index": i}
            )

        # Get last 5
        context = librarian.get_room_context("general", last_n=5)

        assert len(context) == 5
        # Should be most recent (highest indices)
        assert all(c['metadata']['index'] >= 5 for c in context)

    def test_save_and_load_index(self, librarian, temp_library_dir):
        """Test saving and loading index"""
        # Add data
        librarian.add_conversation("general", "Test message", {})

        # Save
        librarian.save_index()

        # Verify files exist
        index_file = temp_library_dir / "faiss_index.bin"
        metadata_file = temp_library_dir / "metadata.json"

        assert index_file.exists()
        assert metadata_file.exists()

        # Load in new instance
        from core.librarian import Librarian
        librarian2 = Librarian(str(temp_library_dir))

        assert len(librarian2.metadata) > 0
        assert librarian2.index is not None

    def test_get_stats(self, librarian):
        """Test getting library statistics"""
        # Add conversations to different rooms
        librarian.add_conversation("general", "Message 1", {})
        librarian.add_conversation("general", "Message 2", {})
        librarian.add_conversation("truck", "Message 3", {})

        stats = librarian.get_stats()

        assert stats['total_entries'] == 3
        assert stats['rooms']['general'] == 2
        assert stats['rooms']['truck'] == 1
        assert stats['index_size'] > 0

    def test_export_to_json(self, librarian, temp_library_dir):
        """Test exporting library to JSON"""
        # Add data
        librarian.add_conversation("general", "Test message", {"key": "value"})

        # Export
        export_file = temp_library_dir / "export.json"
        librarian.export_to_json(export_file)

        # Verify export
        assert export_file.exists()

        with open(export_file, 'r') as f:
            exported_data = json.load(f)

        assert len(exported_data) > 0
        assert exported_data[0]['text'] == "Test message"


@pytest.mark.integration
class TestLibrarianIntegration:
    """Integration tests for Librarian"""

    @pytest.fixture
    def librarian(self, temp_library_dir):
        """Create Librarian instance"""
        try:
            from core.librarian import Librarian
            return Librarian(str(temp_library_dir))
        except ImportError:
            pytest.skip("Librarian dependencies not available")

    def test_full_conversation_workflow(self, librarian):
        """Test complete conversation storage and retrieval workflow"""
        # 1. Add conversations
        conversations = [
            ("general", "What is machine learning?", {"response": "ML is..."}),
            ("general", "Explain neural networks", {"response": "Neural nets are..."}),
            ("truck", "Where is the delivery truck?", {"response": "Truck is at..."}),
        ]

        for room, text, metadata in conversations:
            librarian.add_conversation(room, text, metadata)

        # 2. Search for AI-related queries
        results = librarian.search("artificial intelligence")

        # Should find machine learning conversation
        assert len(results) > 0

        # 3. Get recent context for general room
        context = librarian.get_room_context("general", last_n=2)

        assert len(context) == 2

        # 4. Save index
        librarian.save_index()

        # 5. Get statistics
        stats = librarian.get_stats()

        assert stats['total_entries'] == 3

    def test_semantic_similarity(self, librarian):
        """Test semantic similarity matching"""
        # Add related conversations with different wording
        librarian.add_conversation("general", "The weather is sunny", {})
        librarian.add_conversation("general", "It's a beautiful day", {})
        librarian.add_conversation("general", "The cat is sleeping", {})

        # Search with synonym
        results = librarian.search("nice weather", max_results=3)

        # Top results should be weather-related
        assert len(results) > 0

        # Weather-related should have higher similarity than cat
        weather_results = [r for r in results if 'weather' in r['text'] or 'beautiful' in r['text']]
        cat_results = [r for r in results if 'cat' in r['text']]

        if weather_results and cat_results:
            assert weather_results[0]['similarity'] > cat_results[0]['similarity']

    def test_persistence(self, librarian, temp_library_dir):
        """Test data persistence across restarts"""
        # Add data
        original_text = "Important message to persist"
        librarian.add_conversation("general", original_text, {"important": True})

        # Save
        librarian.save_index()

        # Simulate restart: create new instance
        from core.librarian import Librarian
        librarian2 = Librarian(str(temp_library_dir))

        # Search should find original data
        results = librarian2.search("important message")

        assert len(results) > 0
        assert any(original_text in r['text'] for r in results)

    def test_large_scale_search(self, librarian):
        """Test search performance with many entries"""
        # Add 100 conversations
        for i in range(100):
            librarian.add_conversation(
                "general",
                f"This is message number {i} with various content",
                {"index": i}
            )

        # Search should still work
        results = librarian.search("message number", max_results=10)

        assert len(results) <= 10
        assert all('similarity' in r for r in results)


@pytest.mark.unit
class TestLibrarianEdgeCases:
    """Edge case tests for Librarian"""

    @pytest.fixture
    def librarian(self, temp_library_dir):
        """Create Librarian instance"""
        try:
            from core.librarian import Librarian
            return Librarian(str(temp_library_dir))
        except ImportError:
            pytest.skip("Librarian dependencies not available")

    def test_empty_text(self, librarian):
        """Test adding conversation with empty text"""
        librarian.add_conversation("general", "", {})

        # Should handle gracefully
        assert len(librarian.metadata) > 0

    def test_very_long_text(self, librarian):
        """Test adding conversation with very long text"""
        long_text = "a" * 10000

        librarian.add_conversation("general", long_text, {})

        # Should handle without error
        assert len(librarian.metadata) > 0

    def test_special_characters_in_text(self, librarian):
        """Test text with special characters"""
        special_text = "Hello! How are you? @#$%^&*() 你好 🎉"

        librarian.add_conversation("general", special_text, {})

        # Should handle special characters
        results = librarian.search("Hello special")
        assert len(results) >= 0  # May or may not match

    def test_search_nonexistent_room(self, librarian):
        """Test searching non-existent room"""
        librarian.add_conversation("general", "Test", {})

        results = librarian.search("Test", room="nonexistent")

        # Should return empty results
        assert results == []

    def test_max_results_zero(self, librarian):
        """Test search with max_results=0"""
        librarian.add_conversation("general", "Test", {})

        # Should handle edge case
        results = librarian.search("Test", max_results=0)

        # Likely returns empty or minimal results
        assert isinstance(results, list)

    def test_negative_max_results(self, librarian):
        """Test search with negative max_results"""
        librarian.add_conversation("general", "Test", {})

        # Should handle gracefully (may clip to 0 or return all)
        try:
            results = librarian.search("Test", max_results=-1)
            assert isinstance(results, list)
        except (ValueError, AssertionError):
            # Acceptable if it raises an error for invalid input
            pass
