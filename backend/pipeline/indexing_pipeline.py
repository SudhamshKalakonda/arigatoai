import os
import hashlib
import time
from datetime import datetime
from typing import Optional
import pymupdf4llm
from database.registry import (
    document_exists, register_document,
    register_chunk, init_db
)
from pipeline.category_detector import (
    detect_category, detect_credibility, detect_financial_year
)
from pipeline.chunker import chunk_text
from pipeline.pinecone_client import upsert_chunks, get_index
from pipeline.bm25_index import add_to_index

def compute_file_hash(file_path: str) -> str:
    """SHA256 hash of file contents for deduplication."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()

def compute_bytes_hash(file_bytes: bytes) -> str:
    """SHA256 hash of file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()

def extract_pdf_markdown(file_path: str) -> str:
    """
    Extract PDF content as clean markdown using pymupdf4llm.
    Handles tables, headers, and formatting properly.
    """
    md_text = pymupdf4llm.to_markdown(file_path)
    return md_text

def clean_markdown(text: str) -> str:
    """Clean extracted markdown for better chunking."""
    import re
    # Fix broken numbers across lines
    text = re.sub(r'(\d),\s*\n\s*(\d)', r'\1,\2', text)
    # Fix rupee symbol
    text = re.sub(r'₹\s+(\d)', r'₹\1', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove page headers/footers (common patterns)
    text = re.sub(r'\n\d+\s*\n', '\n', text)
    return text.strip()

def index_pdf(
    file_path: str,
    title: str = None,
    source_url: str = None,
    firm_id: str = "arigato",
    valid_from: str = None,
    expires_at: str = None,
    force: bool = False
) -> dict:
    """
    Full production indexing pipeline for a PDF file.
    
    Steps:
    1. Hash check (deduplication)
    2. Extract markdown with pymupdf4llm
    3. Clean text
    4. Detect category
    5. Chunk text
    6. Embed + upsert to Pinecone
    7. Register in SQLite
    8. Update BM25 index
    
    Returns: summary dict
    """
    start_time = time.time()
    filename = os.path.basename(file_path)

    print(f"\n{'='*60}")
    print(f"Indexing: {filename}")
    print(f"{'='*60}")

    # Step 1 — Hash check
    doc_id = compute_file_hash(file_path)
    if document_exists(doc_id) and not force:
        print(f"✓ Already indexed (hash: {doc_id[:12]}...) — skipping")
        return {"status": "skipped", "reason": "already_indexed", "doc_id": doc_id}

    # Step 2 — Extract markdown
    print("Extracting PDF content...")
    try:
        md_text = extract_pdf_markdown(file_path)
        print(f"  Extracted {len(md_text)} characters")
    except Exception as e:
        print(f"  ❌ Extraction failed: {e}")
        return {"status": "failed", "reason": str(e)}

    # Step 3 — Clean text
    md_text = clean_markdown(md_text)

    # Step 4 — Detect category and credibility
    category, subcategory = detect_category(md_text[:2000])
    credibility = detect_credibility(source_url or f"pdf://{filename}")
    financial_year = detect_financial_year(md_text[:1000])
    
    if not title:
        title = filename.replace(".pdf", "").replace("_", " ").replace("-", " ")
    if not source_url:
        source_url = f"pdf://{filename}"

    print(f"  Category: {category} → {subcategory}")
    print(f"  Credibility: {credibility}")
    print(f"  Financial Year: {financial_year}")

    # Step 5 — Chunk text
    print("Chunking...")
    chunks = chunk_text(
        text=md_text,
        source_url=source_url,
        title=title,
        firm_id=firm_id,
        chunk_size=300,
        overlap_sentences=2
    )

    # Add category to each chunk metadata
    for chunk in chunks:
        chunk.metadata["category"] = category
        chunk.metadata["subcategory"] = subcategory
        chunk.metadata["credibility"] = credibility
        chunk.metadata["financial_year"] = financial_year

    print(f"  Created {len(chunks)} chunks")

    # Step 6 — Embed and upsert to Pinecone
    print("Uploading to Pinecone...")
    upsert_chunks(chunks)

    # Step 7 — Register in SQLite
    print("Registering in database...")
    register_document(
        doc_id=doc_id,
        filename=filename,
        title=title,
        source_url=source_url,
        source_type="pdf",
        category=category,
        credibility=credibility,
        firm_id=firm_id,
        chunk_count=len(chunks),
        valid_from=valid_from,
        expires_at=expires_at
    )

    # Register chunks in SQLite
    for chunk in chunks:
        register_chunk(
            chunk_id=chunk.chunk_id,
            doc_id=doc_id,
            text=chunk.text,
            category=category,
            subcategory=subcategory,
            pinecone_id=chunk.chunk_id
        )

    # Step 8 — Update BM25 index
    print("Updating BM25 index...")
    bm25_docs = [{"text": c.text, "metadata": c.metadata} for c in chunks]
    add_to_index(bm25_docs)

    elapsed = time.time() - start_time
    print(f"\n✅ Done in {elapsed:.1f}s")
    print(f"   {len(chunks)} chunks indexed")
    print(f"   Category: {category} → {subcategory}")

    return {
        "status": "success",
        "doc_id": doc_id,
        "filename": filename,
        "title": title,
        "category": category,
        "subcategory": subcategory,
        "chunk_count": len(chunks),
        "elapsed_seconds": round(elapsed, 1)
    }

def index_pdf_bytes(
    file_bytes: bytes,
    filename: str,
    title: str = None,
    source_url: str = None,
    firm_id: str = "arigato",
    force: bool = False
) -> dict:
    """Index a PDF from bytes (for API uploads)."""
    tmp_path = f"/tmp/{filename}"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)
    result = index_pdf(
        file_path=tmp_path,
        title=title,
        source_url=source_url,
        firm_id=firm_id,
        force=force
    )
    os.remove(tmp_path)
    return result

def index_directory(
    directory: str,
    firm_id: str = "arigato",
    force: bool = False
) -> list:
    """Index all PDFs in a directory."""
    results = []
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDFs in {directory}")

    for filename in pdf_files:
        file_path = os.path.join(directory, filename)
        result = index_pdf(file_path=file_path, firm_id=firm_id, force=force)
        results.append(result)

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")

    print(f"\n{'='*60}")
    print(f"INDEXING COMPLETE")
    print(f"  Success: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"{'='*60}")

    return results

if __name__ == "__main__":
    import sys
    init_db()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else None
        result = index_pdf(file_path=file_path, title=title)
        print(f"\nResult: {result}")
    else:
        print("Usage: python3 -m pipeline.indexing_pipeline <file.pdf> [title]")