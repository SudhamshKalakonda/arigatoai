import os
import re
import fitz
from pipeline.chunker import chunk_text, Chunk

def clean_pdf_text(text: str) -> str:
    # Fix numbers split across lines e.g. "1,50,\n000" → "1,50,000"
    text = re.sub(r'(\d),\s*\n\s*(\d)', r'\1,\2', text)
    # Fix words split across lines with hyphen
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    # Replace multiple newlines with single space
    text = re.sub(r'\n+', ' ', text)
    # Fix multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    # Fix rupee symbol spacing
    text = re.sub(r'₹\s+(\d)', r'₹\1', text)
    return text.strip()

def parse_pdf(file_path: str, title: str = None, firm_id: str = "arigato") -> list[Chunk]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    doc = fitz.open(file_path)
    full_text = ""
    page_count = len(doc)

    for page_num in range(page_count):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            full_text += f" {text}"

    doc.close()

    if not full_text.strip():
        print(f"Warning: No text extracted from {file_path}")
        return []

    # Clean the extracted text
    full_text = clean_pdf_text(full_text)

    if not title:
        title = os.path.basename(file_path).replace(".pdf", "").replace("_", " ")

    source_url = f"pdf://{os.path.basename(file_path)}"

    chunks = chunk_text(
        text=full_text,
        source_url=source_url,
        title=title,
        firm_id=firm_id,
        chunk_size=300,
        overlap_sentences=2
    )

    print(f"Parsed {page_count} pages -> {len(chunks)} chunks from {title}")
    return chunks


def parse_pdf_bytes(file_bytes: bytes, filename: str, title: str = None, firm_id: str = "arigato") -> list[Chunk]:
    tmp_path = f"/tmp/{filename}"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)
    chunks = parse_pdf(tmp_path, title=title, firm_id=firm_id)
    os.remove(tmp_path)
    return chunks