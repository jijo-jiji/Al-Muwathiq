"""
Fresh ChromaDB Ingestion - Ensures metadata is properly saved.
Run this after deleting the chroma_db folder.
"""
import os
import django
import dotenv

# Load environment first
dotenv.load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from evidence_engine.models import SourceDocument
from django.conf import settings

CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'chroma_db')

def fresh_ingest():
    print("=" * 70)
    print("FRESH CHROMADB INGESTION")
    print("=" * 70)
    
    # 1. Check if chroma_db exists
    if os.path.exists(CHROMA_DB_DIR):
        print(f"\n⚠️  WARNING: ChromaDB already exists at: {CHROMA_DB_DIR}")
        print("Please delete it first, then run this script again.")
        return
    
    print(f"\n✓ ChromaDB directory is clean")
    
    # 2. Get all SourceDocuments
    print("\n[Step 1/3] Fetching SourceDocuments from Django database...")
    source_docs = SourceDocument.objects.all()
    
    if not source_docs.exists():
        print("✗ No SourceDocuments found!")
        print("Please upload PDFs via Django admin first.")
        return
    
    print(f"✓ Found {source_docs.count()} documents:")
    for doc in source_docs:
        print(f"  - {doc.title}")
        print(f"    ID: {doc.id}")
        print(f"    Authority: {doc.authority}")
        print(f"    File: {doc.file_path.path}")
    
    # 3. Initialize ChromaDB
    print("\n[Step 2/3] Initializing ChromaDB...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        collection_name="al_muwathiq_standards",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    print("✓ ChromaDB initialized")
    
    # 4. Process each document
    print("\n[Step 3/3] Processing documents...")
    total_chunks = 0
    
    for i, source_doc in enumerate(source_docs, 1):
        print(f"\n[{i}/{source_docs.count()}] Processing: {source_doc.title}")
        
        try:
            # Load PDF
            file_path = source_doc.file_path.path
            loader = PyMuPDFLoader(file_path)
            pages = loader.load()
            print(f"  ✓ Loaded {len(pages)} pages")
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(pages)
            print(f"  ✓ Created {len(chunks)} chunks")
            
            # CRITICAL: Add metadata to each chunk
            for chunk in chunks:
                # Get page number (PyMuPDF uses 0-indexed 'page')
                page_idx = chunk.metadata.get('page', 0)
                
                # Set our custom metadata
                chunk.metadata['source_doc_id'] = str(source_doc.id)
                chunk.metadata['authority'] = source_doc.authority
                chunk.metadata['page_number'] = page_idx + 1  # Convert to 1-indexed
                chunk.metadata['title'] = source_doc.title
                
                # Keep only simple metadata (remove complex objects)
                chunk.metadata = {
                    'source_doc_id': str(source_doc.id),
                    'authority': source_doc.authority,
                    'page_number': page_idx + 1,
                    'title': source_doc.title,
                    'source': chunk.metadata.get('source', '')
                }
            
            # Add to vectorstore
            vectorstore.add_documents(documents=chunks)
            total_chunks += len(chunks)
            print(f"  ✓ Added {len(chunks)} chunks to ChromaDB")
            
            # Verify metadata was saved
            print(f"  ✓ Verifying metadata...")
            test_results = vectorstore.similarity_search(source_doc.title, k=1)
            if test_results and test_results[0].metadata.get('source_doc_id'):
                print(f"  ✓ Metadata verified: source_doc_id = {test_results[0].metadata['source_doc_id']}")
            else:
                print(f"  ✗ WARNING: Metadata verification failed!")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"✅ INGESTION COMPLETE!")
    print(f"   Total chunks ingested: {total_chunks}")
    print(f"   ChromaDB location: {CHROMA_DB_DIR}")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart Django server if it's running")
    print("2. Test the chat interface")

if __name__ == "__main__":
    fresh_ingest()
