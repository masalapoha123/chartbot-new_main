from rag_engine.chunks_builder import getChunks
from rag_engine.embedding_builder import getEmbeddings
from rag_engine.bm25_builder import bm25_builder
from rag_engine.faiss_builder import buildFaissIndex

def handler(pdf_bytes):

    chunks = getChunks(pdf_bytes)
    
    embeddings = getEmbeddings(chunks)
    
    bm25_builder(chunks)
    
    message = buildFaissIndex(embeddings)
    
    return {"message":"built successfully"}
    
    
    
    
    