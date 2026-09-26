# rag_store.py

import os
import pickle
from pathlib import Path

import numpy as np

# Lazy import — do NOT import sentence_transformers at module level.
# It pulls in torch, which costs 2-8 seconds at first import.
_HAS_FAISS = None
_faiss = None
_chromadb = None

INDEX_ROOT = Path("faiss_index")
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_model = None


def _load_faiss_or_chroma():
    """Load FAISS or ChromaDB lazily, on first use."""
    global _HAS_FAISS, _faiss, _chromadb
    if _HAS_FAISS is not None:
        return
    try:
        import faiss as _f
        _faiss = _f
        _HAS_FAISS = True
    except ImportError:
        import chromadb as _c
        _chromadb = _c
        _HAS_FAISS = False


def get_embedder():
    """Load sentence-transformers lazily, on first embed call."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def embed_texts(texts):
    model = get_embedder()
    vecs = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vecs.astype("float32")


def _company_dir(company):
    return INDEX_ROOT / company


def index_exists(company):
    return (_company_dir(company) / "index.faiss").exists() \
        or (_company_dir(company) / "chroma").exists()


def save_index(company, chunks, metadatas, vectors):
    _load_faiss_or_chroma()

    d = _company_dir(company)
    d.mkdir(parents=True, exist_ok=True)

    if _HAS_FAISS:
        dim = vectors.shape[1]
        index = _faiss.IndexFlatIP(dim)   # inner product on normalized vecs = cosine
        index.add(vectors)
        _faiss.write_index(index, str(d / "index.faiss"))
    else:
        client = _chromadb.PersistentClient(path=str(d / "chroma"))
        col = client.get_or_create_collection(name="docs")
        col.add(
            documents=chunks,
            metadatas=metadatas,
            embeddings=vectors.tolist(),
            ids=[f"{company}_{i}" for i in range(len(chunks))],
        )

    with open(d / "chunks.pkl", "wb") as f:
        pickle.dump({"chunks": chunks, "metadatas": metadatas}, f)


def load_index(company):
    _load_faiss_or_chroma()

    d = _company_dir(company)

    if not d.exists():
        return None

    chunks_path = d / "chunks.pkl"
    if not chunks_path.exists():
        return None

    with open(chunks_path, "rb") as f:
        data = pickle.load(f)

    if _HAS_FAISS:
        index_path = d / "index.faiss"
        if not index_path.exists():
            return None
        index = _faiss.read_index(str(index_path))
        return index, data["chunks"], data["metadatas"]
    else:
        client = _chromadb.PersistentClient(path=str(d / "chroma"))
        try:
            col = client.get_collection(name="docs")
        except Exception:
            return None
        return col, data["chunks"], data["metadatas"]


def search(company, query, top_k=5):
    loaded = load_index(company)
    if not loaded:
        return []

    index, chunks, metadatas = loaded

    q_vec = embed_texts([query])

    if _HAS_FAISS:
        scores, ids = index.search(q_vec, top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "text": chunks[idx],
                "metadata": metadatas[idx],
            })
        return results
    else:
        res = index.query(
            query_embeddings=q_vec.tolist(),
            n_results=top_k,
        )
        results = []
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        ):
            results.append({
                "score": 1 - dist,
                "text": doc,
                "metadata": meta,
            })
        return results