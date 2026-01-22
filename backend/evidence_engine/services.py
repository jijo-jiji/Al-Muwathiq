import fitz  # PyMuPDF
import os
import uuid
from django.conf import settings
from django.core.files.base import ContentFile

class EvidenceGenerator:
    """
    Handles PDF opening, text searching, highlighting, and image generation.
    """
    
    def generate_evidence(self, pdf_path, page_number, text_snippet):
        """
        Generates a highlighted image for the given text on the specific PDF page.
        
        Args:
            pdf_path (str): Absolute file path to the PDF.
            page_number (int): 1-indexed page number.
            text_snippet (str): The text to search for and highlight.
            
        Returns:
            str: The relative path to the generated image in MEDIA_ROOT, or None if failed.
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return None

        # Validate page number
        if page_number < 1 or page_number > len(doc):
            print(f"Invalid page number: {page_number}")
            return None

        # fitz uses 0-indexed pages
        page_idx = page_number - 1
        page = doc[page_idx]

        # 1. Search for the text
        # quad_lists is a list of list of genearted quads (rects) for each match
        # We might want to be flexible with whitespace (TEXT_PRESERVE_WHITESPACE not used here, using search_for default)
        # Note: 'text_snippet' should be cleaned/normalized before passed here ideally.
        text_instances = page.search_for(text_snippet)

        # Fallback: If exact match fails, try a smaller chunk or just return the page?
        # Requirement: "If pymupdf cannot find the text coordinates, return the full page image without highlighting."
        
        should_highlight = True
        if not text_instances:
            print(f"Text not found: '{text_snippet}' on page {page_number}. Returning clean page.")
            should_highlight = False

        # 2. Add Annotations (Highlight)
        if should_highlight:
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=(1, 1, 0)) # Yellow
                highlight.update()

        # 3. Render Page to Image (Pixmap)
        # matrix=fitz.Matrix(1.5, 1.5) optimized for speed while maintaining readability
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)

        # 4. Save to Disk
        # Generate a unique filename
        filename = f"evidence_{uuid.uuid4()}.png"
        
        # We need to save it to MEDIA_ROOT/evidence_artifacts/
        # But since we use Django's storage in the model, we can return the content or path.
        # The prompt asks to "Export that single page... to the Django media/ folder."
        # And "Return the URL"
        
        relative_dir = "evidence_artifacts"
        output_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        pix.save(output_path)
        
        return os.path.join(relative_dir, filename)

