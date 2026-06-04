"""Document chunking for RAG ingestion.

Splits text into overlapping chunks for vector storage.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Chunk:
    """A text chunk with metadata."""

    text: str
    index: int
    source: str
    start_char: int
    end_char: int
    metadata: dict


def chunk_text(
    text: str,
    source: str = "unknown",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """Split text into overlapping chunks.

    Args:
        text: Raw text to chunk.
        source: Source file name or identifier.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of Chunk objects.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end within last 20% of chunk
            search_start = max(start + int(chunk_size * 0.8), start)
            for punct in [". ", ".\n", "! ", "!\n", "? ", "?\n"]:
                last_punct = text.rfind(punct, search_start, end)
                if last_punct > start:
                    end = last_punct + len(punct)
                    break

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                index=index,
                source=source,
                start_char=start,
                end_char=end,
                metadata={
                    "source": source,
                    "chunk_index": index,
                    "char_start": start,
                    "char_end": end,
                },
            ))
            index += 1

        # Move forward with overlap
        start = end - chunk_overlap if end < len(text) else end

    return chunks


def chunk_file(
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """Read a file and chunk its contents.

    Args:
        file_path: Path to the text file.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of Chunk objects.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    return chunk_text(
        text=text,
        source=path.name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
