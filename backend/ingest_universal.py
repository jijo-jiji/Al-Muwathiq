
import os
import time
from tqdm import tqdm
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- LOADERS ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "../data_source/BNM/data_bnm")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_GEMINI_API_KEY")

def get_loader_for_file(file_path):
    """Factory function: Returns the correct loader based on extension"""
    if file_path.endswith('.pdf'):
        return PyPDFLoader(file_path)
    elif file_path.endswith('.docx') or file_path.endswith('.doc'):
        return Docx2txtLoader(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        # Mode="elements" keeps the table structure better
        return UnstructuredExcelLoader(file_path, mode="elements")
    else:
        return None

def ingest_data():
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
        raise ValueError("Please set your GOOGLE_API_KEY")
    
    # 1. Setup Brain
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=GOOGLE_API_KEY
    )
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    # 2. Get all valid files
    if not os.path.exists(DATA_FOLDER):
         raise FileNotFoundError(f"Data folder not found at: {DATA_FOLDER}")

    all_files = os.listdir(DATA_FOLDER)
    valid_files = [f for f in all_files if f.endswith(('.pdf', '.docx', '.doc', '.xlsx', '.xls'))]
    
    print(f"📚 Found {len(valid_files)} documents to ingest.")

    # 3. Process loop
    for file_name in tqdm(valid_files, desc="Ingesting"):
        file_path = os.path.join(DATA_FOLDER, file_name)
        
        try:
            # A. Select the right tool for the job
            loader = get_loader_for_file(file_path)
            if not loader:
                print(f"⚠️ Skipping unknown type: {file_name}")
                continue

            # B. Load content
            docs = loader.load()
            
            # C. Split (Chunking)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(docs)
            
            # D. Save to DB
            if chunks:
                vector_db.add_documents(chunks)
            else:
                print(f"⚠️ Warning: {file_name} was empty.")

            # E. Rate Limit Protection
            time.sleep(2) 
            
        except Exception as e:
            print(f"\n❌ Error processing {file_name}: {e}")
            continue

    print(f"✅ Ingestion Complete! Brain saved to '{DB_PATH}'")

if __name__ == "__main__":
    ingest_data()
