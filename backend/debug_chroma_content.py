import os
import sys
import dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

sys.stdout.reconfigure(encoding='utf-8')

# Setup
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DB_PATH = os.path.join(os.path.dirname(__file__), "evidence_engine/chroma_db") 
# Note: ingest_universal.py used "chroma_db", but rag_service.py uses "evidence_engine/chroma_db".
# I need to check which one is the REAL db.
# efficient check: try both.

def check_db(path, name):
    print(f"\n--- CHECKING DB at {path} ({name}) ---")
    if not os.path.exists(path):
        print("❌ Path does not exist.")
        return

    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        vector_db = Chroma(persist_directory=path, embedding_function=embeddings)
        
        # Get all documents (limited to avoid crash if huge)
        # Chroma doesn't have a simple "list all sources" without fetching.
        # We'll fetch a sample.
        print("   -> Fetching count...")
        # count = vector_db._collection.count() # Direct access if possible
        # LangChain wrapper wrapper...
        
        # fallback: search for *
        # actually, let's just use the internal collection if available
        collection = vector_db._client.get_collection("langchain") # Standard collection name
        count = collection.count()
        print(f"   -> Count: {count} chunks")
        
        if count > 0:
            print("   -> Peeking at first 10 sources...")
            peek = collection.get(limit=10, include=["metadatas"])
            seen_sources = set()
            for m in peek['metadatas']:
                if m and 'source' in m:
                    seen_sources.add(m['source'])
            
            for s in seen_sources:
                print(f"      - {s}")
                
            # Try to get ALL sources specifically
            print("   -> listing top 50 unique sources...")
            all_meta = collection.get(include=["metadatas"])
            all_sources = set()
            for m in all_meta['metadatas']:
                 if m and 'source' in m:
                    all_sources.add(m['source'])
            
            target_file = "20130628_B_PL_0035.PDF"
            found = False
            for s in all_sources:
                if target_file in s:
                    print(f"✅ FOUND TARGET FILE: {s}")
                    found = True
                    break
            if not found:
                print(f"❌ TARGET FILE '{target_file}' NOT FOUND in {len(all_sources)} sources.")

            sorted_src = sorted(list(all_sources))
            for s in sorted_src[:50]:
                print(f"      - {s}")
            if len(sorted_src) > 50:
                print(f"      ... and {len(sorted_src)-50} more.")
                
    except Exception as e:
        print(f"❌ Error inspecting DB: {e}")

if __name__ == "__main__":
    # Check the path used by RAG Service
    check_db(os.path.join(os.getcwd(), 'backend/evidence_engine/chroma_db'), "RAG Service DB")
    
    # Check the path used by Ingest Universal (if different)
    check_db(os.path.join(os.getcwd(), 'backend/chroma_db'), "Ingest Universal DB")
