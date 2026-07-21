import os
import hashlib
import time
from datetime import datetime
from typing import Optional
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
from pipeline.extractor import extract_text, is_supported

def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()

def compute_bytes_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def index_file(
    file_path: str,
    title: str = None,
    source_url: str = None,
    firm_id: str = "arigato",
    valid_from: str = None,
    expires_at: str = None,
    force: bool = False
) -> dict:
    """
    Full production indexing pipeline for any supported file.
    Supports: PDF, DOCX, TXT, XLSX, XLS, CSV

    Steps:
    1. Hash check (deduplication)
    2. Extract text (format-aware)
    3. Clean text
    4. Detect category
    5. Chunk text
    6. Embed + upsert to Pinecone
    7. Register in SQLite
    8. Update BM25 index
    """
    start_time = time.time()
    filename = os.path.basename(file_path)
    ext = filename.lower().split(".")[-1]

    print(f"\n{'='*60}")
    print(f"Indexing: {filename}")
    print(f"{'='*60}")

    # Check format
    if not is_supported(filename):
        return {
            "status": "failed",
            "reason": f"Unsupported format: {ext}. Supported: PDF, DOCX, TXT, XLSX, CSV"
        }

    # Step 1 — Hash check
    doc_id = compute_file_hash(file_path)
    if document_exists(doc_id) and not force:
        print(f"✓ Already indexed (hash: {doc_id[:12]}...) — skipping")
        return {"status": "skipped", "reason": "already_indexed", "doc_id": doc_id}

    # Step 2 — Extract text
    print(f"Extracting content ({ext.upper()})...")
    try:
        text = extract_text(file_path, filename)
        if not text or len(text.strip()) < 100:
            return {"status": "failed", "reason": "No text extracted from file"}
        print(f"  Extracted {len(text)} characters")
    except Exception as e:
        print(f"  Extraction failed: {e}")
        return {"status": "failed", "reason": str(e)}

    # Step 3 — Detect category and metadata
    category, subcategory = detect_category(text[:2000])
    credibility = detect_credibility(source_url or f"upload://{filename}")
    financial_year = detect_financial_year(text[:1000])

    if not title:
        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    if not source_url:
        source_url = f"upload://{filename}"

    print(f"  Category: {category} → {subcategory}")
    print(f"  Credibility: {credibility}")
    print(f"  Financial Year: {financial_year}")

    # Step 4 — Chunk text
    print("Chunking...")
    chunks = chunk_text(
        text=text,
        source_url=source_url,
        title=title,
        firm_id=firm_id,
        chunk_size=300,
        overlap_sentences=2
    )

    for chunk in chunks:
        chunk.metadata["category"] = category
        chunk.metadata["subcategory"] = subcategory
        chunk.metadata["credibility"] = credibility
        chunk.metadata["financial_year"] = financial_year
        chunk.metadata["file_type"] = ext

    print(f"  Created {len(chunks)} chunks")

    # Step 5 — Embed and upsert to Pinecone
    print("Uploading to Pinecone...")
    upsert_chunks(chunks)

    # Step 6 — Register in SQLite
    print("Registering in database...")
    register_document(
        doc_id=doc_id,
        filename=filename,
        title=title,
        source_url=source_url,
        source_type=ext,
        category=category,
        credibility=credibility,
        firm_id=firm_id,
        chunk_count=len(chunks),
        valid_from=valid_from,
        expires_at=expires_at
    )

    for chunk in chunks:
        register_chunk(
            chunk_id=chunk.chunk_id,
            doc_id=doc_id,
            text=chunk.text,
            category=category,
            subcategory=subcategory,
            pinecone_id=chunk.chunk_id
        )

    # Step 7 — Update BM25 index
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

def index_file_bytes(
    file_bytes: bytes,
    filename: str,
    title: str = None,
    source_url: str = None,
    firm_id: str = "arigato",
    force: bool = False
) -> dict:
    """Index a file from bytes (for API uploads). Supports all formats."""
    tmp_path = f"/tmp/{filename}"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)
    result = index_file(
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
    """Index all supported files in a directory."""
    from pipeline.extractor import SUPPORTED_FORMATS
    results = []
    all_files = [
        f for f in os.listdir(directory)
        if f.lower().split(".")[-1] in SUPPORTED_FORMATS
    ]
    print(f"Found {len(all_files)} supported files in {directory}")

    for filename in all_files:
        file_path = os.path.join(directory, filename)
        result = index_file(file_path=file_path, firm_id=firm_id, force=force)
        results.append(result)

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

# Backward compatibility aliases
index_pdf = index_file
index_pdf_bytes = index_file_bytes

if __name__ == "__main__":
    import sys
    init_db()
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else None
        result = index_file(file_path=file_path, title=title)
        print(f"\nResult: {result}")
    else:
        print("Usage: python3 -m pipeline.indexing_pipeline <file> [title]")
        print("Supported: PDF, DOCX, TXT, XLSX, XLS, CSV")
