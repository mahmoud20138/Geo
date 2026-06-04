"""RAG (Retrieval-Augmented Generation) module for geo-agents.

Provides document ingestion, chunking, vector storage, and retrieval
for unstructured data like historical geological reports.

Usage:
    from geo_agents.rag import RAGEngine

    rag = RAGEngine()

    # Ingest documents
    await rag.ingest_text("report.txt", "The copper mineralization...")
    await rag.ingest_file("drill_report.pdf")

    # Query
    results = await rag.query("What are the copper grades at depth?")

    # Use as tool in agent pipeline
    tools = rag.as_tools()
"""

from geo_agents.rag.engine import RAGEngine, RAGResult
from geo_agents.rag.chunker import chunk_text, chunk_file
from geo_agents.rag.store import VectorStore

__all__ = ["RAGEngine", "RAGResult", "chunk_text", "chunk_file", "VectorStore"]
