#!/usr/bin/env python3
"""
Test script for license parser
"""

import json
import os
import sys
from pathlib import Path

# Add the doc_pipeline directory to the Python path
sys.path.append('doc_pipeline')

from llm.llm_client import extract_fields_from_text


def load_sample_ocr_text():
    """
    Load a sample OCR text string from a driving license image.
    This is a sample text that might be extracted from a driver's license.
    """
    sample_text = """
    CALIFORNIA DRIVER LICENSE
    CLASS C
    NAME: JOHN MICHAEL SMITH
    ADDRESS: 1234 MAIN STREET
    CITY: LOS ANGELES, CA 90210
    DOB: 05/15/1985
    LICENSE NO: A123456789
    ISSUED: 03/20/2020
    EXPIRES: 03/20/2025
    SEX: M
    HEIGHT: 5'10"
    WEIGHT: 175 LBS
    EYES: BROWN
    HAIR: BROWN
    RESTRICTIONS: NONE
    ENDORSEMENTS: NONE
    """
    return sample_text.strip()


def load_license_prompt():
    """
    Load the license_extraction.txt prompt from the prompts directory.
    """
    prompt_path = Path("doc_pipeline/prompts/license_extraction.txt")
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"License prompt not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """
    Main test function for license parser.
    """
    print("=== License Parser Test ===")
    
    try:
        # 1. Load sample OCR text
        print("1. Loading sample OCR text...")
        ocr_text = load_sample_ocr_text()
        print(f"   OCR Text length: {len(ocr_text)} characters")
        print(f"   Sample text: {ocr_text[:100]}...")
        
        # 2. Load license extraction prompt
        print("\n2. Loading license extraction prompt...")
        prompt = load_license_prompt()
        print(f"   Prompt loaded successfully")
        
        # 3. Call extract_fields_from_text()
        print("\n3. Calling extract_fields_from_text()...")
        result = extract_fields_from_text(ocr_text, prompt)
        
        # 4. Print the resulting JSON object
        print("\n4. Extracted JSON result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 5. Save output to file
        print("\n5. Saving output to file...")
        output_dir = Path("test/output/license")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "license_test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   Output saved to: {output_file}")
        
        # Additional validation
        print("\n6. Validation:")
        required_fields = ['Name', 'DateOfBirth', 'LicenseNumber', 'IssuingState', 'ExpiryDate']
        for field in required_fields:
            value = result.get(field)
            status = "✓" if value is not None else "✗"
            print(f"   {status} {field}: {value}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 