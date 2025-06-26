#!/usr/bin/env python3
"""
Debug script to test OCR on failing license images
"""

import sys
from pathlib import Path

# Add the doc_pipeline directory to the Python path
sys.path.append('doc_pipeline')

from ocr.ocr_engine import extract_text_from_file


def test_image(image_path):
    print(f"\nTesting OCR on: {image_path}")
    print("=" * 50)
    
    try:
        ocr_text = extract_text_from_file(image_path)
        print("OCR Output:")
        print("-" * 30)
        print(ocr_text)
        print("-" * 30)
        print(f"Text length: {len(ocr_text)} characters")
        
        if not ocr_text.strip():
            print("WARNING: No text extracted!")
        else:
            print("Text extracted successfully")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    # Test multiple failing images
    test_images = [
        "doc_pipeline/data/Drivers_license/generated_license_1071.png",
        "doc_pipeline/data/Drivers_license/generated_license_1063.png",
        "doc_pipeline/data/Drivers_license/generated_license_1077.png"
    ]
    
    for image in test_images:
        test_image(image)


if __name__ == "__main__":
    main() 