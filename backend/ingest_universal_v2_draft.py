import os
import sys
import django
from tqdm import tqdm
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# 1. Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Add project root to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evidence_engine.models import SourceDocument
from evidence_engine.ingestion import ingest_document

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "../data_source/BNM/data_bnm")

def clean_title(filename):
    """
    Converts '20130628_B_PL_0035.PDF' to 'B PL 0035' or keeps original if not parseable.
    Actually, let's just use the filename but remove extension and replace underscores.
    """
    name = os.path.splitext(filename)[0]
    return name.replace('_', ' ').replace('-', ' ').strip()

def run_universal_ingestion():
    if not os.path.exists(DATA_FOLDER):
        print(f"Folder not found: {DATA_FOLDER}")
        return

    files = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith(('.pdf'))]
    print(f"Found {len(files)} PDFs in folder.")

    for filename in tqdm(files):
        file_path = os.path.join(DATA_FOLDER, filename)
        
        # 1. Check/Create DB Entry
        # Check by title (or filename if we want strict)
        clean_name = clean_title(filename)
        
        # Check if already exists by Title OR Filename
        # We can search if title matches
        source_doc = SourceDocument.objects.filter(title=clean_name).first()
        
        if not source_doc:
            print(f"Creating DB Entry for: {clean_name}")
            source_doc = SourceDocument(
                title=clean_name,
                authority='BNM',
                is_ingested=False,
                is_active=True
            )
            # Open file and save to field (this copies it to media/)
            from django.core.files import File
            try:
                with open(file_path, 'rb') as f:
                    # Truncate filename if too long (keep extension)
                    safe_filename = filename
                    if len(safe_filename) > 90:
                        name, ext = os.path.splitext(safe_filename)
                        safe_filename = name[:85] + ext
                        
                    source_doc.file_path.save(safe_filename, File(f), save=True)
            except Exception as e:
                print(f"❌ Failed to save file {filename}: {e}")
                continue
        else:
            # Check if file matches? If file_path is missing, add it.
            if not source_doc.file_path:
                print(f"Updating file for: {clean_name}")
                from django.core.files import File
                try:
                    with open(file_path, 'rb') as f:
                        source_doc.file_path.save(filename, File(f), save=True)
                except Exception as e:
                    print(f"❌ Failed to save file {filename}: {e}")
                    continue
        
        # 2. Ingest
        if not source_doc.is_ingested:
            try:
                ingest_document(source_doc)
            except Exception as e:
                print(f"Failed to ingest {filename}: {e}")
        else:
             # print(f"Skipping {filename} (Already Ingested)")
             pass

if __name__ == "__main__":
    run_universal_ingestion()
