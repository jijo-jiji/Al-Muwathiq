import os
import shutil
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from django.conf import settings
from .models import SourceDocument

# Persistence directory
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'chroma_db')

def ingest_document(source_doc: SourceDocument):
    """
    Ingests a SourceDocument into the Real ChromaDB.
    """
    if not source_doc.file_path:
        print(f"Skipping {source_doc.title}: No file path.")
        return

    file_abs_path = source_doc.file_path.path
    print(f"Ingesting: {file_abs_path}")

    # 1. Load PDF
    loader = PyMuPDFLoader(file_abs_path)
    docs = loader.load()
    print(f"Loaded {len(docs)} pages.")

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} chunks.")

    # 3. Store in ChromaDB
    # Enrich metadata
    for split in splits:
        split.metadata['source_doc_id'] = str(source_doc.id)
        split.metadata['authority'] = source_doc.authority
        # Ensure page_number is 1-indexed (PyMuPDF is 0-indexed)
        page_idx = split.metadata.get('page', 0)
        split.metadata['page_number'] = page_idx + 1

    # Initialize Embeddings (using a lightweight local model)
    # Initialize Embeddings (using Google GenAI to match ingestion pipeline)
    print("Initializing Embeddings (Google GenAI)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Initialize Vector Store
    vectorstore = Chroma(
        collection_name="al_muwathiq_standards",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    # Add documents
    vectorstore.add_documents(documents=splits)
    print(f"Saved {len(splits)} chunks to ChromaDB at {CHROMA_DB_DIR}")
