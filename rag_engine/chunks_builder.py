import fitz  
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

def getChunks(pdf_bytes):
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    
        
    text = ""
    for page in pdf:
        text += page.get_text() + "\n"
    
    pdf.close()
    
        
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    chunks = splitter.split_text(text)
    
    with open('./knowledge_base/chunks.json', "w") as f: json.dump(chunks, f, indent=2)
    
    return chunks