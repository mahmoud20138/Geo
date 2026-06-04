"""Vector store for RAG using ChromaDB.

Provides persistent vector storage with embedding-based retrieval.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


@dataclass
class SearchResult:
    """A single search result from the vector store."""

    text: str
    score: float
    source: str
    metadata: dict


class VectorStore:
    """ChromaDB-backed vector store for document embeddings.

    Args:
        collection_name: Name of the collection.
        persist_dir: Directory to persist the database.
        embedding_model: Sentence-transformers model name.
    """

    def __init__(
        self,
        collection_name: str = "geo_agents",
        persist_dir: str = ".chromadb",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        if not HAS_CHROMADB:
            raise ImportError(
                "chromadb is required for RAG. Install with: pip install chromadb sentence-transformers"
            )

        self._persist_dir = persist_dir
        self._collection_name = collection_name
        self._embedding_model = embedding_model

        # Initialize ChromaDB
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> int:
        """Add texts to the vector store.

        Args:
            texts: List of text strings to add.
            metadatas: Optional metadata for each text.
            ids: Optional IDs for each text.

        Returns:
            Number of texts added.
        """
        if not texts:
            return 0

        if ids is None:
            import hashlib
            ids = [hashlib.md5(t.encode()).hexdigest()[:16] for t in texts]

        if metadatas is None:
            metadatas = [{}] * len(texts)

        self._collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )
        return len(texts)

    def query(
        self,
        text: str,
        n_results: int = 5,
        where: dict | None = None,
    ) -> list[SearchResult]:
        """Search for similar texts.

        Args:
            text: Query text.
            n_results: Number of results to return.
            where: Optional metadata filter.

        Returns:
            List of SearchResult objects.
        """
        if self._collection.count() == 0:
            return []

        kwargs = {
            "query_texts": [text],
            "n_results": min(n_results, self._collection.count()),
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        search_results = []
        for i in range(len(results["ids"][0])):
            search_results.append(SearchResult(
                text=results["documents"][0][i],
                score=1 - results["distances"][0][i],  # Convert distance to similarity
                source=results["metadatas"][0][i].get("source", "unknown"),
                metadata=results["metadatas"][0][i],
            ))

        return search_results

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        self._collection.delete(ids=ids)

    def clear(self) -> None:
        """Clear all documents."""
        if self._collection.count() > 0:
            all_ids = self._collection.get()["ids"]
            if all_ids:
                self._collection.delete(ids=all_ids)

    @property
    def count(self) -> int:
        """Number of documents in the store."""
        return self._collection.count()

    def stats(self) -> dict:
        """Get store statistics."""
        return {
            "collection": self._collection_name,
            "documents": self._collection.count(),
            "persist_dir": self._persist_dir,
            "embedding_model": self._embedding_model,
        }
