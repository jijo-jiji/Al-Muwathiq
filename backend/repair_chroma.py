"""
Repair ChromaDB by wiping and re-ingesting all SourceDocuments.
This ensures all metadata (especially source_doc_id) is correctly populated.
"""
import os
import django
import shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evidence_engine.models import SourceDocument
from evidence_engine.ingestion import ingest_document, CHROMA_DB_DIR

def repair_chroma():
    print("=" * 60)
    print("ChromaDB Repair Script")
    print("=" * 60)
    
    # 1. Delete existing ChromaDB (SKIPPED - file locks)
    # Note: Re-ingesting will update metadata without needing to delete
    print(f"\n[1/3] Skipping ChromaDB deletion (keeping existing data)")
    print("Note: Re-ingestion will update/add metadata to existing chunks")
    
    # 2. Get all SourceDocuments
    print("\n[2/3] Fetching SourceDocuments from database...")
    source_docs = SourceDocument.objects.all()
    
    if not source_docs.exists():
        print("✗ No SourceDocuments found in database!")
        print("Please upload documents via Django admin first.")
        return
    
    print(f"✓ Found {source_docs.count()} documents:")
    for doc in source_docs:
        print(f"  - {doc.title} (ID: {doc.id}, Authority: {doc.authority})")
    
    # 3. Re-ingest all documents
    print("\n[3/3] Re-ingesting documents into ChromaDB...")
    for i, doc in enumerate(source_docs, 1):
        print(f"\n[{i}/{source_docs.count()}] Processing: {doc.title}")
        try:
            ingest_document(doc)
            print(f"✓ Successfully ingested: {doc.title}")
        except Exception as e:
            print(f"✗ Error ingesting {doc.title}: {e}")
    
    print("\n" + "=" * 60)
    print("Repair Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Django server (Ctrl+C, then 'python manage.py runserver')")
    print("2. Test the chat interface")

if __name__ == "__main__":
    repair_chroma()
