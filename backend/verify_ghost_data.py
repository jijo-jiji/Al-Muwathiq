import os
import django
import sys
import dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
dotenv.load_dotenv()

from evidence_engine.models import SourceDocument

def check_ghosts():
    print("--- 👻 Ghostbuster: Checking for Dead Data ---")
    
    # 1. Get all valid IDs from SQL
    valid_ids = set(str(uid) for uid in SourceDocument.objects.values_list('id', flat=True))
    print(f"SQL Database has {len(valid_ids)} valid SourceDocuments.")
    
    # 2. Check Chroma
    CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'evidence_engine', 'chroma_db')
    # Or try the other path
    if not os.path.exists(CHROMA_DB_DIR):
        CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')
        
    print(f"Checking ChromaDB at: {CHROMA_DB_DIR}")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        collection_name="al_muwathiq_standards",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    # Peek
    try:
        # Get all metadatas
        data = vectorstore.get(include=["metadatas"])
        metadatas = data['metadatas']
        print(f"ChromaDB has {len(metadatas)} chunks.")
        
        ghost_count = 0
        checked_count = 0
        
        for m in metadatas:
            if not m: continue
            sid = m.get('source_doc_id')
            if sid:
                checked_count += 1
                if sid not in valid_ids:
                    ghost_count += 1
                    if ghost_count <= 5:
                        print(f"❌ Found Ghost Chunk! ID: {sid} (Source: {m.get('source_title', 'Unknown')})")
        
        if ghost_count > 0:
            print(f"\n🚨 FOUND {ghost_count} GHOST CHUNKS out of {checked_count} checked.")
            print("Explanation: The vector database contains references to files that were deleted from the SQL database.")
            print("Solution: You MUST stop the server and run 'clean_and_ingest.py' again.")
        else:
            print("\n✅ No ghosts found. Data is consistent.")
            
    except Exception as e:
        print(f"Error reading Chroma: {e}")

if __name__ == "__main__":
    check_ghosts()
