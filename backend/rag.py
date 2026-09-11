from pypdf import PdfReader
from .config import get_embedder, get_collection

NEEDS_EVERYTHING = ["how many", "count", "total", "average", "compare", "list all", "every", "each", "most", "least"]


def read_file_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    return open(path, "r", encoding="utf-8", errors="ignore").read()


def split_into_chunks(text: str, size: int = 800, overlap: int = 120) -> list:
    chunks, start = [], 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        start += size - overlap
    return chunks


def index_file(path: str, filename: str) -> int:
    chunks = split_into_chunks(read_file_text(path))
    if not chunks:
        return 0
    embedder, collection = get_embedder(), get_collection()
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    vectors = [v.tolist() for v in embedder.embed(chunks)]
    ids = [f"{filename}-{i}" for i in range(len(chunks))]
    metas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    collection.add(documents=chunks, embeddings=vectors, ids=ids, metadatas=metas)
    return len(chunks)

def _pack(texts, metas) -> list:
    return [{"text": t, "source": m["source"], "chunk_index": m["chunk_index"]} for t, m in zip(texts, metas)]

def find_relevant_chunks(question: str, top_k: int = 6):
    collection = get_collection()
    if collection.count() == 0:
        return [], 0.0
    if any(w in question.lower() for w in NEEDS_EVERYTHING):
        data = collection.get()
        return _pack(data["documents"], data["metadatas"]), 90.0
    vector = list(get_embedder().embed([question]))[0].tolist()
    result = collection.query(query_embeddings=[vector], n_results=top_k)
    docs, metas, dist = result["documents"][0], result["metadatas"][0], result["distances"][0]
    if not docs:
        return [], 0.0
    confidence = round(max(0.0, 1 - sum(dist) / len(dist)) * 100, 1)
    return _pack(docs, metas), confidence
