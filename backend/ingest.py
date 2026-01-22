import os
import time
from tqdm import tqdm
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.vectorstores.utils import filter_complex_metadata

load_dotenv()

# --- CONFIGURATION ---
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "../data_source/BNM/data_bnm")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
# HARDCODE KEY IF .ENV FAILS
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 

def get_loader_for_file(file_path):
    if file_path.endswith('.pdf'):
        return PyPDFLoader(file_path)
    elif file_path.endswith('.docx') or file_path.endswith('.doc'):
        return Docx2txtLoader(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return UnstructuredExcelLoader(file_path, mode="elements")
    else:
        return None

def add_documents_with_retry(vector_db, chunks, file_name):
    """
    Retries with Exponential Backoff (60s -> 120s -> 240s)
    """
    max_retries = 5
    base_delay = 60
    
    for attempt in range(max_retries):
        try:
            vector_db.add_documents(chunks)
            return True
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                # EXPONENTIAL BACKOFF: Wait longer each time
                delay = base_delay * (2 ** attempt) 
                print(f"\n⏳ Rate limit on {file_name}. Waiting {delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
            else:
                print(f"\n❌ Critical error on {file_name}: {e}")
                return False
    return False

def ingest_data():
    if not GOOGLE_API_KEY:
        raise ValueError("Check your API Key.")
    
    if not os.path.exists(DATA_FOLDER):
        raise FileNotFoundError(f"Folder not found: {DATA_FOLDER}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=GOOGLE_API_KEY
    )

    vector_db = Chroma(
        collection_name="al_muwathiq_standards",
        persist_directory=DB_PATH, 
        embedding_function=embeddings
    )

    all_files = os.listdir(DATA_FOLDER)
    valid_files = [f for f in all_files if f.endswith(('.pdf', '.docx', '.doc', '.xlsx', '.xls'))]
    
    print(f"📚 Found {len(valid_files)} documents to ingest.")

    for file_name in tqdm(valid_files, desc="Ingesting"):
        file_path = os.path.join(DATA_FOLDER, file_name)
        
        try:
            loader = get_loader_for_file(file_path)
            if not loader: continue

            docs = loader.load()
            
            # --- UPDATED CHUNK STRATEGY ---
            # Smaller chunks = Easier for Free Tier to handle
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # Reduced from 800
                chunk_overlap=100
            )
            chunks = text_splitter.split_documents(docs)
            chunks = filter_complex_metadata(chunks) # Fix for ['eng'] list error
            
            if chunks:
                for chunk in chunks:
                    chunk.metadata['source'] = file_name
                
                success = add_documents_with_retry(vector_db, chunks, file_name)
                
                if success:
                    time.sleep(1) # Small breather
            else:
                pass # Empty file

        except Exception as e:
            print(f"\n⚠️ Error loading {file_name}: {e}")
            continue

    print(f"✅ Ingestion Complete! Brain saved to '{DB_PATH}'")

if __name__ == "__main__":
    ingest_data()