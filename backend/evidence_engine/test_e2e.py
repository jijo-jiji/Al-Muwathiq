
import os
import sys
import django
from django.core.files.base import ContentFile

# Setup
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from evidence_engine.models import SourceDocument
from evidence_engine.ingestion import ingest_document
from evidence_engine.rag_service import RAGService
from django.conf import settings
import fitz

def run_test():
    print("=== STARTING END-TO-END TEST ===")
    
    # 1. Create a dummy SourceDocument with a real PDF file
    pdf_path = os.path.join(settings.MEDIA_ROOT, "source_documents", "bnm_tawarruq.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Create the PDF content
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Bank Negara Malaysia (BNM) Policy Document on Tawarruq.
    Effective Date: 1 January 2024.
    
    Paragraph 10.1: Arrangement of Tawarruq.
    The contracting parties shall ensure that the arrangement involves a real transfer of ownership of the commodity.
    
    Paragraph 12: Wakalah.
    The purchasing customer may appoint the bank as an agent to sell the commodity.
    """
    page.insert_text((50, 50), text)
    doc.save(pdf_path)
    
    # Save the model
    # Note: We assign the file path manually to the FileField
    source_doc, created = SourceDocument.objects.get_or_create(
        title="BNM Tawarruq Policy",
        authority="BNM",
    )
    # Re-assign file to ensure it's picked up
    source_doc.file_path.name = "source_documents/bnm_tawarruq.pdf"
    source_doc.save()
    print(f"Created Source Document: {source_doc}")

    # 2. Ingest
    print("\n--- INGESTION ---")
    ingest_document(source_doc)

    # 3. Query
    print("\n--- QUERYING ---")
    rag = RAGService()
    query = "transfer of ownership"
    result = rag.answer_question(query)

    print("\n=== RESULT ===")
    print(f"Answer: {result['answer']}")
    print(f"Evidence URL: {result['evidence_url']}")
    
    if result['evidence_url']:
        full_path = os.path.join(settings.BASE_DIR, result['evidence_url'].lstrip('/'))
        if os.path.exists(full_path):
             print(f"VERIFIED: Evidence image exists at {full_path}")
        else:
             print(f"ERROR: Image path returned but file missing: {full_path}")
    else:
        print("ERROR: No evidence URL returned.")

if __name__ == "__main__":
    run_test()
