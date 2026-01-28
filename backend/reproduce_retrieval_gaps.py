import os
import django
import sys
import dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
dotenv.load_dotenv()

from evidence_engine.rag_service import RAGService

def test_query(rag, query):
    print(f"\n--- TESTING QUERY: '{query}' ---")
    
    # 1. Broad Search (Intern)
    print("Step 1: Broad Search (k=10)...")
    results = rag.vectorstore.similarity_search_with_score(query, k=10)
    
    found_relevant = False
    for i, (doc, score) in enumerate(results):
        source = doc.metadata.get('source_title', 'Unknown')
        content_preview = doc.page_content[:100].replace('\n', ' ')
        print(f"   [{i}] Score {score:.4f} | Source: {source} | Content: {content_preview}...")
        
        # Simple keyword check
        keywords = ["credit", "card", "crypto", "token", "digital", "asset"]
        if any(k in doc.page_content.lower() for k in keywords):
            found_relevant = True

    if not found_relevant:
        print("   ⚠️ WARNING: No obvious keywords found in top 10.")
    else:
        print("   ✅ Found relevant chunks in broad search.")

    # 2. End-to-End Search (NO RERANK TEST)
    print("\nStep 2: Checking Vector Search ONLY (Top 15)...")
    # Manually get top 15 from vectorstore
    results = rag.vectorstore.similarity_search_with_score(query, k=15)
    hits = []
    for doc, score in results:
        hits.append((doc, score))
    
    print(f"   -> Top 5 Hits (Vector Only):")
    for i, (doc, score) in enumerate(hits[:5]):
        print(f"      [{i}] Score {score:.4f} | {doc.page_content[:200]}...")

    # 3. Ask LLM using these hits
    print("\nStep 3: Asking LLM (Bypassing RAG Service internal search logic)...")
    # We cheat and inject hits into the answer generation if possible, 
    # but answer_question calls search_db internally.
    # So we will copy the logic of answer_question here but use our `hits`.
    
    # Format context
    context_text = ""
    for i, (doc, _) in enumerate(hits):
        context_text += f"[Source {i}] (Page {doc.metadata.get('page_number')}): {doc.page_content}\n\n"
    
    # Prompt
    prompt = rag.prompt_template.format(context=context_text, question=query)
    print(f"   -> Prompt len: {len(prompt)}")
    
    if rag.client:
        response = rag.client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        print("ANSWER:", response.text)
    else:
        print("No Client.")

if __name__ == "__main__":
    rag = RAGService()
    
    # Test 1: Credit Card
    test_query(rag, "is credit card haram?")
    
    # Test 2: Crypto
    test_query(rag, "is cryptocurrency haram?")
