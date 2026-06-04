"""RAG Engine — combines chunking, storage, and retrieval.

Main entry point for RAG operations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from geo_agents.rag.chunker import chunk_text, chunk_file, Chunk
from geo_agents.rag.store import VectorStore, SearchResult


@dataclass
class RAGResult:
    """Result from a RAG query."""

    answer: str
    sources: list[dict]
    query: str
    num_results: int

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "query": self.query,
            "num_results": self.num_results,
        }


class RAGEngine:
    """Main RAG engine for document ingestion and retrieval.

    Args:
        collection_name: Name of the vector collection.
        persist_dir: Directory to persist the database.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.
        embedding_model: Sentence-transformers model name.
    """

    def __init__(
        self,
        collection_name: str = "geo_agents",
        persist_dir: str = ".chromadb",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._store = VectorStore(
            collection_name=collection_name,
            persist_dir=persist_dir,
            embedding_model=embedding_model,
        )

    # ── Ingestion ──────────────────────────────────────────────

    def ingest_text(
        self,
        text: str,
        source: str = "manual_input",
        metadata: dict | None = None,
    ) -> int:
        """Ingest raw text into the vector store.

        Args:
            text: Text content to ingest.
            source: Source identifier (filename, URL, etc.).
            metadata: Optional additional metadata.

        Returns:
            Number of chunks created.
        """
        chunks = chunk_text(
            text=text,
            source=source,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )

        if not chunks:
            return 0

        texts = [c.text for c in chunks]
        metadatas = []
        for c in chunks:
            m = {**c.metadata}
            if metadata:
                m.update(metadata)
            metadatas.append(m)

        return self._store.add(texts=texts, metadatas=metadatas)

    def ingest_file(
        self,
        file_path: str,
        metadata: dict | None = None,
    ) -> int:
        """Ingest a text file into the vector store.

        Args:
            file_path: Path to the file.
            metadata: Optional additional metadata.

        Returns:
            Number of chunks created.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text = path.read_text(encoding="utf-8", errors="replace")
        return self.ingest_text(
            text=text,
            source=path.name,
            metadata=metadata,
        )

    def ingest_directory(
        self,
        dir_path: str,
        extensions: list[str] | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Ingest all text files in a directory.

        Args:
            dir_path: Path to the directory.
            extensions: File extensions to include (default: .txt, .md, .csv).
            metadata: Optional additional metadata.

        Returns:
            Dict with ingestion results.
        """
        if extensions is None:
            extensions = [".txt", ".md", ".csv", ".log"]

        path = Path(dir_path)
        if not path.exists():
            return {"error": f"Directory not found: {dir_path}"}

        results = {"files": [], "total_chunks": 0, "errors": []}

        for ext in extensions:
            for file_path in sorted(path.glob(f"*{ext}")):
                try:
                    chunks = self.ingest_file(str(file_path), metadata)
                    results["files"].append({"file": file_path.name, "chunks": chunks})
                    results["total_chunks"] += chunks
                except Exception as e:
                    results["errors"].append({"file": file_path.name, "error": str(e)})

        return results

    # ── Retrieval ──────────────────────────────────────────────

    def query(
        self,
        text: str,
        n_results: int = 5,
        source_filter: str | None = None,
    ) -> RAGResult:
        """Query the vector store for relevant chunks.

        Args:
            text: Query text.
            n_results: Number of results to return.
            source_filter: Optional source name filter.

        Returns:
            RAGResult with answer context and sources.
        """
        where = {"source": source_filter} if source_filter else None
        results = self._store.query(text=text, n_results=n_results, where=where)

        if not results:
            return RAGResult(
                answer="No relevant documents found.",
                sources=[],
                query=text,
                num_results=0,
            )

        # Build context from results
        context_parts = []
        sources = []
        for i, r in enumerate(results, 1):
            context_parts.append(f"[{i}] (source: {r.source}, similarity: {r.score:.2f})\n{r.text}")
            sources.append({
                "source": r.source,
                "similarity": round(r.score, 3),
                "text_preview": r.text[:200],
                "metadata": r.metadata,
            })

        answer = "\n\n".join(context_parts)

        return RAGResult(
            answer=answer,
            sources=sources,
            query=text,
            num_results=len(results),
        )

    # ── Management ─────────────────────────────────────────────

    def clear(self) -> None:
        """Clear all documents from the store."""
        self._store.clear()

    def stats(self) -> dict:
        """Get RAG engine statistics."""
        store_stats = self._store.stats()
        return {
            **store_stats,
            "chunk_size": self._chunk_size,
            "chunk_overlap": self._chunk_overlap,
        }

    # ── Tool Integration ───────────────────────────────────────

    def as_tools(self) -> list:
        """Return RAG capabilities as LangChain tools for agent use.

        Returns:
            List of LangChain tool objects.
        """
        from langchain_core.tools import tool

        rag = self  # Capture for closures

        @tool
        def rag_query(query: str, n_results: int = 3) -> dict:
            """Search the document knowledge base for relevant information.

            Use this to find information from ingested documents like
            historical reports, drill logs, and technical papers.

            Args:
                query: Natural language query to search for.
                n_results: Number of results to return (default 3).
            """
            result = rag.query(query, n_results=n_results)
            return result.to_dict()

        @tool
        def rag_ingest_text(text: str, source: str = "user_input") -> dict:
            """Add new text to the document knowledge base.

            Use this to ingest new reports, notes, or data into the RAG system.

            Args:
                text: Text content to add.
                source: Source identifier (filename or description).
            """
            chunks = rag.ingest_text(text, source=source)
            return {"chunks_created": chunks, "source": source, "status": "ingested"}

        @tool
        def rag_stats() -> dict:
            """Get statistics about the document knowledge base.

            Returns info about how many documents are stored.
            """
            return rag.stats()

        return [rag_query, rag_ingest_text, rag_stats]
