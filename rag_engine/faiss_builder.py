import faiss
import numpy as np


def buildFaissIndex(embeddings: np.ndarray) -> faiss.Index:

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    faiss.write_index(index, "./knowledge_base/index.faiss")
    
    return {"message":"Knowledge Base Created Successfy"}