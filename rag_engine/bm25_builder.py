from rank_bm25 import BM25Okapi
import pickle

def bm25_builder(chunks: list[str]):
    bm25 = BM25Okapi([chunk.lower().split() for chunk in chunks])
    
    with open('./knowledge_base/bm25.pkl', "wb") as f: pickle.dump(bm25,f)
    