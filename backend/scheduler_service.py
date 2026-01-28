import time
import schedule
import os
import sys
import django
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add backend directory to sys.path
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from scrapers.bnm_scraper import scrape_bnm
from evidence_engine.models import SourceDocument
from evidence_engine.ingestion import ingest_document

def run_ingestion():
    print("Checking for un-ingested documents...")
    docs = SourceDocument.objects.filter(is_ingested=False, is_active=True)
    if not docs.exists():
        print("No new documents to ingest.")
        return

    for doc in docs:
        print(f"Ingesting: {doc.title}")
        try:
            ingest_document(doc)
        except Exception as e:
            print(f"Failed to ingest {doc.title}: {e}")

def job():
    print("Starting scheduled job...")
    try:
        scrape_bnm()
    except Exception as e:
        print(f"Scraper failed: {e}")
        
    try:
        run_ingestion()
    except Exception as e:
        print(f"Ingestion failed: {e}")
    print("Job complete.")

if __name__ == "__main__":
    print("Scheduler Service Started.")
    # Run once immediately
    job()
    
    # Schedule every day
    schedule.every(24).hours.do(job)
    
    print("Scheduler running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(60)
