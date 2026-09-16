from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(r"C:\Users\Sritam.Nanda\Downloads\embedding_model\all-Mini-l6-V2")

def getEmbeddings(chunks: list[str]) -> np.ndarray:
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.astype("float32")