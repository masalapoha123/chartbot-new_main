import json
import pickle
import faiss
import numpy as np
from rag_engine.embedding_builder import getEmbeddings

def retrieve(userQuery: str, k: int = 5):
    with open("./knowledge_base/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    index = faiss.read_index("./knowledge_base/index.faiss")

    with open("./knowledge_base/bm25.pkl", "rb") as f:
        bm25 = pickle.load(f)

    retrieval_k = 20

    query_embedding = getEmbeddings([userQuery])

    _, faiss_indices = index.search(query_embedding, retrieval_k)
    faiss_ranking = faiss_indices[0].tolist()

    tokenized_query = userQuery.split()
    scores = bm25.get_scores(tokenized_query)
    bm25_ranking = np.argsort(scores)[::-1][:retrieval_k].tolist()

    rrf_scores = {}
    rrf_k = 60

    for rank, chunk_id in enumerate(faiss_ranking):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rrf_k + rank + 1)

    for rank, chunk_id in enumerate(bm25_ranking):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rrf_k + rank + 1)

    best_chunks = sorted(
        rrf_scores,
        key=rrf_scores.get,
        reverse=True
    )[:k]

    return [chunks[i] for i in best_chunks]
