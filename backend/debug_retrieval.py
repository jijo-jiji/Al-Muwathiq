import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evidence_engine.rag_service import RAGService

def debug_query(query):
    print(f"\n--- Debugging Query: '{query}' ---")
    rag = RAGService()
    
    # Get raw hits
    results = rag.vectorstore.similarity_search_with_score(query, k=5)
    
    for i, (doc, score) in enumerate(results):
        print(f"\nHIT {i+1} (Score: {score:.4f})")
        print(f"Doc ID: {doc.metadata.get('source_doc_id')}")
        print(f"Page: {doc.metadata.get('page_number')}")
        print("-" * 40)
        print(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
        print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        q = "What is Tawarruq?"
    debug_query(q)
