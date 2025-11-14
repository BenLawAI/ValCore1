"""
VALCORE1 Librarian
Semantic memory search using FAISS and sentence transformers
"""

import logging
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning("FAISS or sentence-transformers not available")

logger = logging.getLogger(__name__)


class Librarian:
    """Manages semantic memory search and storage"""

    def __init__(self, library_path: str):
        """
        Initialize librarian

        Args:
            library_path: Path to library root directory
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("FAISS and sentence-transformers are required")

        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings model
        logger.info("Loading sentence transformer model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2

        # Initialize FAISS index
        self.index = None
        self.metadata = []  # Stores metadata for each vector

        # Paths
        self.index_file = self.library_path / "faiss_index.bin"
        self.metadata_file = self.library_path / "metadata.json"

        # Load existing index if available
        self.load_index()

        logger.info(f"Librarian initialized with {len(self.metadata)} entries")

    def add_conversation(self, room: str, text: str, metadata: Optional[Dict] = None):
        """
        Add conversation to library

        Args:
            room: Room name
            text: Conversation text
            metadata: Additional metadata
        """
        try:
            # Generate embedding
            embedding = self.embedder.encode(text)

            # Create metadata entry
            entry = {
                "room": room,
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            # Add to index
            if self.index is None:
                # Create new index
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product (cosine similarity)

            # Normalize embedding for cosine similarity
            embedding_norm = embedding / np.linalg.norm(embedding)

            # Add to FAISS
            self.index.add(np.array([embedding_norm], dtype=np.float32))

            # Add metadata
            self.metadata.append(entry)

            logger.debug(f"Added conversation to library: {room}")

            # Save to disk periodically (every 10 entries)
            if len(self.metadata) % 10 == 0:
                self.save_index()

        except Exception as e:
            logger.error(f"Error adding conversation: {e}")

    def search(
        self,
        query: str,
        room: Optional[str] = None,
        max_results: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search library for similar conversations

        Args:
            query: Search query
            room: Optional room filter (None = search all rooms)
            max_results: Maximum results to return
            similarity_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of matching conversation dictionaries
        """
        if self.index is None or len(self.metadata) == 0:
            logger.warning("Index is empty")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query)
            query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)

            # Search index
            distances, indices = self.index.search(
                np.array([query_embedding_norm], dtype=np.float32),
                min(max_results * 2, len(self.metadata))  # Search more to allow for filtering
            )

            # Process results
            results = []

            for dist, idx in zip(distances[0], indices[0]):
                # Check threshold
                if dist < similarity_threshold:
                    continue

                # Get metadata
                entry = self.metadata[idx]

                # Apply room filter
                if room and entry['room'] != room:
                    continue

                # Add to results
                results.append({
                    **entry,
                    'similarity': float(dist)
                })

                # Stop if we have enough
                if len(results) >= max_results:
                    break

            # Security: Don't log query content (may contain sensitive data)
            logger.info(f"Search completed (query_length: {len(query)} chars, results: {len(results)}, room: {room})")
            return results

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def get_room_context(self, room: str, last_n: int = 5) -> List[Dict]:
        """
        Get recent context for a room

        Args:
            room: Room name
            last_n: Number of recent conversations to retrieve

        Returns:
            List of recent conversation dictionaries
        """
        # Filter by room and sort by timestamp
        room_entries = [
            entry for entry in self.metadata
            if entry['room'] == room
        ]

        # Sort by timestamp (most recent first)
        room_entries.sort(key=lambda x: x['timestamp'], reverse=True)

        return room_entries[:last_n]

    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))

            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)

            logger.info(f"Index saved: {len(self.metadata)} entries")

        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def load_index(self):
        """Load FAISS index and metadata from disk"""
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                # Load index
                self.index = faiss.read_index(str(self.index_file))

                # Load metadata
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)

                logger.info(f"Index loaded: {len(self.metadata)} entries")

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            # Initialize empty
            self.index = None
            self.metadata = []

    def build_index(self):
        """Rebuild FAISS index from existing metadata"""
        logger.info("Rebuilding index from metadata...")

        if not self.metadata:
            logger.warning("No metadata to rebuild from")
            return

        # Create new index
        self.index = faiss.IndexFlatIP(self.embedding_dim)

        # Re-embed all texts
        embeddings = []
        for entry in self.metadata:
            embedding = self.embedder.encode(entry['text'])
            embedding_norm = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding_norm)

        # Add to index
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_array)

        logger.info(f"Index rebuilt with {len(self.metadata)} entries")

        # Save
        self.save_index()

    def get_stats(self) -> Dict:
        """
        Get library statistics

        Returns:
            Statistics dictionary
        """
        # Count by room
        room_counts = {}
        for entry in self.metadata:
            room = entry['room']
            room_counts[room] = room_counts.get(room, 0) + 1

        return {
            "total_entries": len(self.metadata),
            "rooms": room_counts,
            "index_size": self.index.ntotal if self.index else 0
        }

    def export_to_json(self, output_file: Path):
        """
        Export library to JSON file

        Args:
            output_file: Output file path
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)

            logger.info(f"Library exported to {output_file}")

        except Exception as e:
            logger.error(f"Export error: {e}")
