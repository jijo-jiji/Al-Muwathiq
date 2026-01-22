
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_GEMINI_API_KEY")

def test_brain():
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
        print("❌ GOOGLE_API_KEY is missing!")
        return

    # Connect to the DB you just built
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ DB path does not exist: {DB_PATH}")
        return

    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings, collection_name="al_muwathiq_standards")

    # Ask a specific question related to your PDFs
    query = "MSB"
    print(f"🔎 Querying: {query}")
    
    try:
        results = vector_db.similarity_search(query, k=2)

        print("--- Test Results ---")
        if not results:
            print("No results found. Is the database empty?")
        for doc in results:
            print(f"\nSource: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content Snippet: {doc.page_content[:200]}...")
            
    except Exception as e:
        print(f"❌ Error during query: {e}")

if __name__ == "__main__":
    test_brain()
