"""
OCR package for text extraction from images.
"""

from .ocr_engine import extract_text_from_file, get_supported_formats

__all__ = ["extract_text_from_file", "get_supported_formats"] 