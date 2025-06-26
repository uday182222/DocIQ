"""

OCR Engine for text extraction from images.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

# Try to import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available. Install with: pip install easyocr")

# Try to import Tesseract
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not available. Install with: pip install pytesseract")

logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png'}


def preprocess_image(image_path: str) -> str:
    """
    Preprocess image to improve OCR accuracy.
    
    Args:
        image_path (str): Path to the input image
        
    Returns:
        str: Path to the temporary preprocessed image
        
    Raises:
        Exception: If preprocessing fails
    """
    try:
        logger.info(f"Preprocessing image: {image_path}")
        
        # Read image with OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"Failed to read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Sharpen the image using unsharp masking
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        sharpened = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        # Resize to 2x original size
        height, width = sharpened.shape
        resized = cv2.resize(sharpened, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        
        # Create temporary file for preprocessed image
        temp_dir = tempfile.gettempdir()
        temp_filename = f"preprocessed_{Path(image_path).stem}.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Save preprocessed image
        cv2.imwrite(temp_path, resized)
        
        logger.info(f"Preprocessing completed. Temporary file: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        raise Exception(f"Preprocessing failed: {e}")


def extract_text_from_file(file_path: str, preprocess: bool = True) -> str:
    """
    Extract text from an image file using OCR.
    
    Args:
        file_path (str): Path to the image file
        preprocess (bool): Whether to preprocess the image before OCR (default: True)
        
    Returns:
        str: Extracted text
        
    Raises:
        ValueError: If file format is not supported
        Exception: If OCR fails
    """
    # Validate file format
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: {SUPPORTED_FORMATS}")
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Extracting text from: {file_path} (preprocess: {preprocess})")
    
    # Preprocess the image if requested
    preprocessed_path = None
    try:
        if preprocess:
            preprocessed_path = preprocess_image(file_path)
            image_path_for_ocr = preprocessed_path
        else:
            image_path_for_ocr = file_path
        
        # Try EasyOCR first
        if EASYOCR_AVAILABLE:
            try:
                text = _extract_with_easyocr(image_path_for_ocr)
                logger.info("Successfully extracted text using EasyOCR")
                return text
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        # Fallback to Tesseract
        if TESSERACT_AVAILABLE:
            try:
                text = _extract_with_tesseract(image_path_for_ocr)
                logger.info("Successfully extracted text using Tesseract")
                return text
            except Exception as e:
                logger.warning(f"Tesseract failed: {e}")
        
        # If both OCR engines fail
        raise Exception("Both EasyOCR and Tesseract failed to extract text")
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise Exception(f"Text extraction failed: {e}")
    
    finally:
        # Clean up temporary preprocessed file
        if preprocessed_path and os.path.exists(preprocessed_path):
            try:
                os.remove(preprocessed_path)
                logger.debug(f"Cleaned up temporary file: {preprocessed_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {preprocessed_path}: {e}")


def _extract_with_easyocr(image_path: str) -> str:
    """
    Extract text using EasyOCR.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text
    """
    # Initialize EasyOCR reader (lazy loading)
    if not hasattr(_extract_with_easyocr, 'reader'):
        _extract_with_easyocr.reader = easyocr.Reader(['en'])
    
    # Extract text
    results = _extract_with_easyocr.reader.readtext(image_path)
    
    # Combine all detected text
    text_parts = []
    for (bbox, text, confidence) in results:
        if confidence > 0.5:  # Filter low confidence results
            text_parts.append(text.strip())
    
    return ' '.join(text_parts)


def _extract_with_tesseract(image_path: str) -> str:
    """
    Extract text using Tesseract.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text
    """
    # Configure Tesseract
    custom_config = r'--oem 3 --psm 6'
    
    # Extract text
    text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
    
    return text.strip()


def get_supported_formats() -> set:
    """Get list of supported image formats."""
    return SUPPORTED_FORMATS.copy()


def is_ocr_available() -> bool:
    """Check if any OCR engine is available."""
    return EASYOCR_AVAILABLE or TESSERACT_AVAILABLE


class OCREngine:
    """
    OCR Engine class wrapper for compatibility with pipeline modules.
    """
    
    def __init__(self):
        """Initialize the OCR engine."""
        if not is_ocr_available():
            raise Exception("No OCR engine available. Install EasyOCR or Tesseract.")
    
    def extract_text(self, file_path: str, preprocess: bool = True) -> str:
        """
        Extract text from an image file.
        
        Args:
            file_path (str): Path to the image file
            preprocess (bool): Whether to preprocess the image before OCR
            
        Returns:
            str: Extracted text
        """
        return extract_text_from_file(file_path, preprocess)
    
    def get_supported_formats(self) -> set:
        """Get list of supported image formats."""
        return get_supported_formats()
    
    def is_available(self) -> bool:
        """Check if OCR engine is available."""
        return is_ocr_available()
