import os
import shutil
import sys
import django
from django.conf import settings

# 1. Setup Django Env
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from evidence_engine.models import SourceDocument, EvidenceArtifact
from ingest_universal_v2_draft import run_universal_ingestion

def clean_slate():
    print("🧹 STARTING CLEANUP...")
    
    # 1. SQL Cleanup
    count, _ = SourceDocument.objects.all().delete()
    print(f"   - Deleted {count} entries from SQL Database (SourceDocuments & related).")
    
    # 2. ChromaDB Cleanup
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    # Also check the other path just in case
    chroma_path_2 = os.path.join(os.path.dirname(__file__), "evidence_engine", "chroma_db")
    
    for path in [chroma_path, chroma_path_2]:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"   - Deleted Vector Store at: {path}")
            except Exception as e:
                print(f"   ⚠️ Could not delete {path}: {e}")
        else:
             print(f"   - No Vector Store found at: {path} (Clean)")

    # 3. Media Cleanup (Optional but good)
    media_source_docs = os.path.join(settings.MEDIA_ROOT, 'source_documents')
    if os.path.exists(media_source_docs):
         # We'll just delete the files inside, not the folder itself, or both.
         # shutil.rmtree(media_source_docs)
         # os.makedirs(media_source_docs)
         # print("   - Cleared media/source_documents.")
         pass 

    print("✨ CLEANUP DONE. Starting Fresh Ingestion...\n")

if __name__ == "__main__":
    confirm = input("⚠️ This will DELETE ALL ingested data. Type 'yes' to proceed: ")
    if confirm.lower() == "yes":
        clean_slate()
        run_universal_ingestion()
    else:
        print("❌ Aborted.")
