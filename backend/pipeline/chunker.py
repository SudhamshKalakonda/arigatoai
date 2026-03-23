import re
import hashlib
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def chunk_text(
    text: str,
    source_url: str,
    title: str,
    firm_id: str = "arigato",
    chunk_size: int = 500,
    overlap: int = 50
) -> list[Chunk]:
    text = clean_text(text)
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) < 50:
            start += chunk_size - overlap
            continue

        chunk_id = hashlib.md5(
            f"{source_url}_{start}".encode()
        ).hexdigest()

        chunks.append(Chunk(
            chunk_id=chunk_id,
            text=chunk_text,
            metadata={
                "source_url": source_url,
                "title": title,
                "firm_id": firm_id,
                "chunk_index": len(chunks),
                "word_count": len(chunk_words)
            }
        ))

        start += chunk_size - overlap

    return chunks