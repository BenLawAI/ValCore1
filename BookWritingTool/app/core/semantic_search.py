"""
Semantic Search - FAISS-based semantic search for manuscript consistency checking
"""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger


class SemanticSearch:
    """Semantic search engine using FAISS and sentence transformers"""

    def __init__(
        self,
        index_path: Optional[Path] = None,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        """Initialize semantic search

        Args:
            index_path: Path to save/load FAISS index
            model_name: Sentence transformer model name
            chunk_size: Words per chunk
            chunk_overlap: Overlapping words between chunks
        """
        self.index_path = index_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Load sentence transformer model
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # FAISS index
        self.index: Optional[faiss.IndexFlatL2] = None
        self.chunks: List[Dict[str, Any]] = []

        # Load existing index if available
        if index_path and index_path.exists():
            self.load()

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dicts with {text, metadata, chunk_id}
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_data = {
                "text": chunk_text,
                "chunk_id": len(chunks),
                "word_start": i,
                "word_end": i + len(chunk_words),
                "metadata": metadata or {},
            }

            chunks.append(chunk_data)

        return chunks

    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add document to search index

        Args:
            text: Document text
            metadata: Metadata (chapter name, project, etc.)
        """
        # Chunk the text
        chunks = self.chunk_text(text, metadata)

        if not chunks:
            logger.warning("No chunks created from text")
            return

        # Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(chunk_texts, convert_to_numpy=True)

        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Add to FAISS index
        self.index.add(embeddings.astype("float32"))

        # Store chunk metadata
        self.chunks.extend(chunks)

        logger.info(f"Added {len(chunks)} chunks to search index")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar text chunks

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching chunks with scores
        """
        if self.index is None or len(self.chunks) == 0:
            logger.warning("Search index is empty")
            return []

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)

        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                results.append(chunk)

        return results

    def find_mentions(self, entity: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find all mentions of an entity (character, location, etc.)

        Args:
            entity: Entity name to search for
            top_k: Maximum results

        Returns:
            List of chunks mentioning the entity
        """
        # Semantic search for entity
        query = f"mentions of {entity}"
        results = self.search(query, top_k=top_k * 2)  # Get more results for filtering

        # Filter to only chunks that actually contain the entity
        filtered_results = []
        for result in results:
            if entity.lower() in result["text"].lower():
                filtered_results.append(result)

        return filtered_results[:top_k]

    def check_consistency(self, entity: str, attribute: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Check for potential consistency issues with an entity's attributes

        Args:
            entity: Entity name (e.g., "John")
            attribute: Attribute to check (e.g., "eyes", "hair")

        Returns:
            List of (text_snippet, extracted_value, metadata) tuples
        """
        # Find all mentions
        mentions = self.find_mentions(entity, top_k=20)

        # Extract attribute values from each mention
        attribute_mentions = []

        for mention in mentions:
            text = mention["text"]
            # Simple keyword-based extraction (could be enhanced with NLP)
            if attribute.lower() in text.lower():
                # Extract sentence containing the attribute
                sentences = text.split(".")
                for sentence in sentences:
                    if attribute.lower() in sentence.lower() and entity.lower() in sentence.lower():
                        attribute_mentions.append((sentence.strip(), attribute, mention["metadata"]))

        return attribute_mentions

    def save(self):
        """Save FAISS index and chunks to disk"""
        if not self.index_path:
            raise ValueError("index_path not set")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_file = self.index_path.with_suffix(".index")
        faiss.write_index(self.index, str(index_file))

        # Save chunks metadata
        chunks_file = self.index_path.with_suffix(".chunks")
        with open(chunks_file, "wb") as f:
            pickle.dump(self.chunks, f)

        logger.info(f"Saved search index to {self.index_path}")

    def load(self):
        """Load FAISS index and chunks from disk"""
        if not self.index_path or not self.index_path.exists():
            raise FileNotFoundError(f"Index not found: {self.index_path}")

        # Load FAISS index
        index_file = self.index_path.with_suffix(".index")
        self.index = faiss.read_index(str(index_file))

        # Load chunks metadata
        chunks_file = self.index_path.with_suffix(".chunks")
        with open(chunks_file, "rb") as f:
            self.chunks = pickle.load(f)

        logger.info(f"Loaded search index from {self.index_path}")

    def clear(self):
        """Clear the search index"""
        self.index = None
        self.chunks = []
        logger.info("Search index cleared")

    def rebuild(self, documents: List[Tuple[str, Dict[str, Any]]]):
        """Rebuild entire search index from documents

        Args:
            documents: List of (text, metadata) tuples
        """
        self.clear()

        for text, metadata in documents:
            self.add_document(text, metadata)

        if self.index_path:
            self.save()

        logger.info(f"Rebuilt search index with {len(documents)} documents")

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_chunks": len(self.chunks),
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_dim,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }
