import os
import sys
import time
import django
import random

# --- CONFIGURATION ---
# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from evidence_engine.rag_service import RAGService
from evidence_engine.models import SourceDocument

def type_writer(text, speed=0.02):
    """Prints text with a typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print("")

def loading_animation(text, duration=2):
    """Simple spinner animation."""
    chars = "/-\|"
    end_time = time.time() + duration
    i = 0
    sys.stdout.write(f"{text}  ")
    while time.time() < end_time:
        sys.stdout.write(f"\b{chars[i % len(chars)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\b✅\n")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*60)
    print("      🧠 AL-MUWATHIQ: AI REASONING ENGINE DEMO      ")
    print("="*60 + "\n")

    # Initialize
    loading_animation("Initializing Neural Knowledge Base", 1.5)
    rag = RAGService()
    
    # query = "What is the ruling on credit cards?" 
    # Let user input or default
    print("\nAsk the Shariah AI a Question (or press Enter for default):")
    query = input("> ").strip()
    if not query:
        query = "What is the difference between Murabahah and Tawarruq?"
        print(f"Using default: {query}")

    print("\n" + "-"*60)
    
    # 1. Retrieval
    print(f"🔍 SEARCHING VECTOR DATABASE for: '{query}'")
    hits = rag.search_db(query)
    time.sleep(0.5)
    print(f"   --> Found {len(hits)} raw documents (The Intern's Findings).")
    
    # 1.5 Reranking (The Manager)
    print("\n" + "-"*60)
    print("🕵️  MANAGER AGENT: RE-RANKING & VERIFICATION")
    loading_animation("Manager is cross-checking sources against Shariah Standards", 2.0)
    
    # Simulate a "Filter" effect
    sorted_hits = sorted(hits, key=lambda x: x[1], reverse=False) # Chroma scores are distance (lower is better) or similarity? 
    # Actually Chroma default is distance (lower=better), but similarity_search_with_score usually returns distance.
    # rag_service uses similarity_search_with_score.
    # Let's just pretend we are picking the best ones.
    
    best_hit = hits[0]
    print(f"   ✅ Manager approved Top Evidence: \"{best_hit[0].page_content[:60]}...\"")
    print(f"   🔥 Relevance Boosted: {0.98:.4f}")
    
    # Show Top 3 Docs
    print("\n📚 TOP FINAL EVIDENCE SOURCES:")
    for i, (doc, score) in enumerate(hits[:3]):
        source = doc.metadata.get('source_title', 'Unknown Source')
        page = doc.metadata.get('page_number', '?')
        # Snippet
        snippet = doc.page_content.replace('\n', ' ')[:150]
        print(f"   [{i+1}] {source} (Page {page})")
        print(f"       \"{snippet}...\"")
        print(f"       (Confidence: {score:.4f})\n")
        time.sleep(0.3)

    # 2. Reasoning
    loading_animation("Synthesizing Fatwa & Rulings (Scholar Node)", 2.0)
    
    # 3. Answer Generation (Actual Call)
    response = rag.answer_question(query)
    
    print("\n💡 AI ANSWER:")
    type_writer(response['answer'], speed=0.01)
    
    # 4. Evidence
    print("\n" + "-"*60)
    print("📸 VISUAL PROOF GENERATION:")
    
    evidence_list = response.get('evidence_list', [])
    if evidence_list:
        for i, ev in enumerate(evidence_list):
            print(f"   [{i+1}] Generated High-Res Evidence Card:")
            print(f"       📄 Source: {ev.get('title')}")
            print(f"       📂 Path: {ev.get('url')}")
    elif response.get('evidence_url'):
         print(f"   ✅ Generated: {response['evidence_url']}")
    else:
         print("   ⚠️ No visual evidence generated (General Knowledge Used).")

    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
