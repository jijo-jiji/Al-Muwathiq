import os
import django
import sys
import dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
dotenv.load_dotenv()

from evidence_engine.rag_service import RAGService

def test_evidence():
    print("--- Testing Evidence Generation ---")
    rag = RAGService()
    
    query = "What is the definition of Tawarruq?"
    print(f"Query: {query}")
    
    response = rag.answer_question(query)
    
    print("\n--- RESULT ---")
    print(f"Answer length: {len(response['answer'])}")
    print(f"Evidence URL: {response.get('evidence_url')}")
    print(f"Metadata: {response.get('metadata')}")
    
    if response.get('evidence_url'):
        print("✅ Evidence URL generated.")
    else:
        print("❌ Evidence URL is MISSING.")

if __name__ == "__main__":
    test_evidence()
