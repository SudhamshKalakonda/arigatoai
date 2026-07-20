import re
import hashlib
from dataclasses import dataclass, field
from nltk.tokenize import sent_tokenize

@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict

# Clause boundary patterns for Indian tax documents
CLAUSE_PATTERNS = [
    r'Section\s+\d+[A-Z]*',      # Section 44AB, Section 80C
    r'Chapter\s+[IVXLC]+',        # Chapter IV, Chapter VI
    r'Rule\s+\d+[A-Z]*',          # Rule 6DD
    r'GSTR[-\s]?\d+[A-Z]*',       # GSTR-1, GSTR-3B
    r'ITR[-\s]?\d+[A-Z]*',        # ITR-1, ITR-4
    r'Form\s+\d+[A-Z]*',          # Form 16, Form 26AS
    r'Schedule\s+[IVXLC]+',       # Schedule III
    r'Article\s+\d+',             # Article 246
    r'Clause\s+\d+',              # Clause 3
]

CLAUSE_REGEX = re.compile('|'.join(CLAUSE_PATTERNS), re.IGNORECASE)

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def is_clause_boundary(sentence: str) -> bool:
    """Check if sentence starts a new legal clause or section."""
    return bool(CLAUSE_REGEX.match(sentence.strip()))

def chunk_text(
    text: str,
    source_url: str,
    title: str,
    firm_id: str = "arigato",
    chunk_size: int = 300,
    overlap_sentences: int = 2
) -> list[Chunk]:
    text = clean_text(text)

    # Split into sentences using NLTK
    sentences = sent_tokenize(text)
    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_word_count = 0

    for i, sentence in enumerate(sentences):
        words_in_sentence = len(sentence.split())
        is_boundary = is_clause_boundary(sentence)

        # Start new chunk if:
        # 1. Current chunk is full AND we hit a clause boundary
        # 2. Current chunk exceeds max size
        should_split = (
            (current_word_count >= chunk_size and is_boundary) or
            (current_word_count >= chunk_size * 1.5)
        )

        if should_split and current_sentences:
            chunk_text_str = " ".join(current_sentences)
            if len(chunk_text_str.strip()) >= 50:
                chunk_id = hashlib.md5(
                    f"{source_url}_{len(chunks)}_{chunk_text_str[:50]}".encode()
                ).hexdigest()
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    text=chunk_text_str,
                    metadata={
                        "source_url": source_url,
                        "title": title,
                        "firm_id": firm_id,
                        "chunk_index": len(chunks),
                        "word_count": current_word_count,
                        "has_clause": bool(CLAUSE_REGEX.search(chunk_text_str)),
                    }
                ))

            # Keep last N sentences as overlap
            current_sentences = current_sentences[-overlap_sentences:] if overlap_sentences > 0 else []
            current_word_count = sum(len(s.split()) for s in current_sentences)

        current_sentences.append(sentence)
        current_word_count += words_in_sentence

    # Add remaining sentences as final chunk
    if current_sentences:
        chunk_text_str = " ".join(current_sentences)
        if len(chunk_text_str.strip()) >= 50:
            chunk_id = hashlib.md5(
                f"{source_url}_{len(chunks)}_{chunk_text_str[:50]}".encode()
            ).hexdigest()
            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=chunk_text_str,
                metadata={
                    "source_url": source_url,
                    "title": title,
                    "firm_id": firm_id,
                    "chunk_index": len(chunks),
                    "word_count": current_word_count,
                    "has_clause": bool(CLAUSE_REGEX.search(chunk_text_str)),
                }
            ))

    return chunks