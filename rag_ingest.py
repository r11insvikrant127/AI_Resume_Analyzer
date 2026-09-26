# rag_ingest.py

import re
from pathlib import Path

from pypdf import PdfReader

from rag_store import embed_texts, save_index


DATA_ROOT = Path("data/companies")


def list_companies():
    if not DATA_ROOT.exists():
        return []
    return sorted(
        d.name for d in DATA_ROOT.iterdir() if d.is_dir()
    )


def _read_pdf(path):
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n".join(parts)


def _read_txt(path):
    return path.read_text(encoding="utf-8", errors="ignore")


def _chunk(text, chunk_size=800, overlap=100):
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def ingest_company(company):
    """
    Read all PDFs/TXTs from data/companies/<company>/,
    chunk, embed, and persist.
    Returns (doc_count, chunk_count).
    """

    folder = DATA_ROOT / company
    if not folder.exists():
        raise FileNotFoundError(f"No folder for {company}")

    all_chunks = []
    all_meta = []
    doc_count = 0

    for path in sorted(folder.iterdir()):

        if path.suffix.lower() == ".pdf":
            text = _read_pdf(path)
        elif path.suffix.lower() in {".txt", ".md"}:
            text = _read_txt(path)
        else:
            continue

        doc_count += 1

        for i, chunk in enumerate(_chunk(text)):
            all_chunks.append(chunk)
            all_meta.append({
                "company": company,
                "source": path.name,
                "chunk_index": i,
            })

    if not all_chunks:
        return doc_count, 0

    vectors = embed_texts(all_chunks)
    save_index(company, all_chunks, all_meta, vectors)

    return doc_count, len(all_chunks)