
import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from evidence_engine.services import EvidenceGenerator
from django.conf import settings
import fitz

def create_dummy_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Rank 1: BNM (Bank Negara Malaysia)
    Ruling on Tawarruq:
    Tawarruq is permissible provided it follows the policy document.
    Specific Sentence: Real commodity assets must be used.
    """
    page.insert_text((50, 50), text)
    doc.save(path)
    print(f"Created dummy PDF at {path}")

def test_highlighter():
    # 1. Create dummy PDF
    pdf_path = os.path.join(settings.MEDIA_ROOT, "test_doc.pdf")
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    create_dummy_pdf(pdf_path)

    # 2. Test Generator
    generator = EvidenceGenerator()
    target_text = "Real commodity assets must be used."
    
    print(f"Testing highlighting for: '{target_text}' on page 1")
    image_rel_path = generator.generate_evidence(pdf_path, 1, target_text)
    
    if image_rel_path:
        full_path = os.path.join(settings.MEDIA_ROOT, image_rel_path)
        print(f"SUCCESS: Image generated at {full_path}")
        if os.path.exists(full_path):
             print(f"Verified: File exists.")
        else:
             print(f"ERROR: File returned but not found on disk.")
    else:
        print("FAILURE: Generator returned None.")

if __name__ == "__main__":
    test_highlighter()
