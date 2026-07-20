import re
from nltk.tokenize import sent_tokenize
from typing import List, Dict

def compute_overlap(query_words: set, sentence: str) -> float:
    """Calculate word overlap between query and sentence."""
    sentence_words = set(sentence.lower().split())
    if not sentence_words:
        return 0.0
    overlap = query_words.intersection(sentence_words)
    return len(overlap) / len(query_words) if query_words else 0.0

def compress_chunk(query: str, chunk_text: str, max_sentences: int = 4, threshold: float = 0.1) -> str:
    """
    Extract only the most relevant sentences from a chunk.
    
    Args:
        query: The user question
        chunk_text: The full chunk text
        max_sentences: Maximum sentences to keep
        threshold: Minimum overlap score to include a sentence
    
    Returns:
        Compressed text with only relevant sentences
    """
    sentences = sent_tokenize(chunk_text)
    if len(sentences) <= max_sentences:
        return chunk_text

    # Get query keywords — remove stopwords
    stopwords = {
        'what', 'is', 'the', 'a', 'an', 'of', 'in', 'on', 'for',
        'to', 'and', 'or', 'how', 'do', 'i', 'my', 'can', 'are',
        'does', 'will', 'when', 'where', 'which', 'who', 'under',
        'per', 'as', 'at', 'by', 'it', 'its', 'this', 'that'
    }
    query_words = set(query.lower().split()) - stopwords

    # Score each sentence by relevance
    scored = []
    for i, sentence in enumerate(sentences):
        score = compute_overlap(query_words, sentence)
        # Boost first and last sentences — often contain key info
        if i == 0 or i == len(sentences) - 1:
            score += 0.05
        scored.append((score, i, sentence))

    # Sort by score, keep top sentences
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_sentences]

    # Filter by threshold
    top = [(s, i, sent) for s, i, sent in top if s >= threshold]

    if not top:
        return " ".join(sentences[:max_sentences])

    # Re-sort by original position to maintain flow
    top.sort(key=lambda x: x[1])

    return " ".join([sent for _, _, sent in top])

def compress_chunks(query: str, chunks: List[Dict], max_sentences: int = 4) -> List[Dict]:
    """
    Compress all retrieved chunks to relevant sentences only.
    
    Args:
        query: The user question
        chunks: List of chunks from re-ranker
        max_sentences: Max sentences per chunk
    
    Returns:
        Chunks with compressed text
    """
    compressed = []
    for chunk in chunks:
        original_text = chunk.get("metadata", {}).get("text", "")
        if not original_text:
            compressed.append(chunk)
            continue

        compressed_text = compress_chunk(
            query=query,
            chunk_text=original_text,
            max_sentences=max_sentences
        )

        # Create new chunk with compressed text
        new_chunk = {**chunk}
        new_chunk["metadata"] = {
            **chunk.get("metadata", {}),
            "text": compressed_text,
            "original_length": len(original_text.split()),
            "compressed_length": len(compressed_text.split())
        }
        compressed.append(new_chunk)

        reduction = (1 - len(compressed_text.split()) / max(1, len(original_text.split()))) * 100
        print(f"Compressed chunk: {len(original_text.split())} → {len(compressed_text.split())} words ({reduction:.0f}% reduction)")

    return compressed