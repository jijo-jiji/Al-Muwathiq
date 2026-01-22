"""
Test script to verify ChromaDB metadata is correctly stored.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from evidence_engine.ingestion import CHROMA_DB_DIR

print("=" * 60)
print("ChromaDB Metadata Test")
print("=" * 60)

# Initialize embeddings and vectorstore
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = Chroma(
    collection_name="al_muwathiq_standards",
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_DIR
)

# Test query
query = "What is the definition of Tawarruq?"
results = vectorstore.similarity_search_with_score(query, k=3)

print(f"\nQuery: {query}")
print(f"Found {len(results)} results\n")

for i, (doc, score) in enumerate(results):
    print(f"Result {i+1}:")
    print(f"  Score: {score:.4f}")
    print(f"  Content: {doc.page_content[:60]}...")
    print(f"  Metadata: {doc.metadata}")
    print()
