import os
from pathlib import Path

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from an image or PDF file.
    If PDF, uses PyMuPDF. If image, uses EasyOCR.
    Returns the extracted text as a string.
    """
    file_path = str(file_path)
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        # PDF: Use PyMuPDF
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")
    else:
        # Image: Use EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(file_path, detail=0, paragraph=True)
            return "\n".join(result)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}") 