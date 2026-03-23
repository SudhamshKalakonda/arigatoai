import os
import fitz
from pipeline.chunker import chunk_text, Chunk

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
            full_text += f"\n{text}"

    doc.close()

    if not full_text.strip():
        print(f"Warning: No text extracted from {file_path}")
        return []

    if not title:
        title = os.path.basename(file_path).replace(".pdf", "").replace("_", " ")

    source_url = f"pdf://{os.path.basename(file_path)}"

    chunks = chunk_text(
        text=full_text,
        source_url=source_url,
        title=title,
        firm_id=firm_id,
        chunk_size=400,
        overlap=50
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
