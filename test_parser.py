#!/usr/bin/env python3
"""
Comprehensive test script for all document parsers using config loading
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add doc_pipeline to path
sys.path.append(str(Path(__file__).parent / "doc_pipeline"))

from llm.llm_client import extract_fields_from_text
from config.doc_config import (
    get_supported_document_types,
    get_document_config,
    get_prompt_path,
    get_validator_function,
    get_postprocess_function
)


def get_mock_ocr_text(doc_type: str) -> str:
    """
    Get mock OCR text for testing different document types.
    Returns realistic OCR text that should trigger field extraction.
    """
    mock_texts = {
        "resume": """
        JOHN DOE
        Software Engineer
        john.doe@email.com
        (555) 123-4567
        
        SKILLS
        Python, JavaScript, React, Node.js, AWS, Docker
        
        WORK EXPERIENCE
        Senior Developer at Tech Corp (2020-2023)
        - Led development of web applications
        - Managed team of 5 developers
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology (2016-2020)
        """,
        
        "license": """
        IRELAND
        DRIVING LICENCE
        
        1. SURNAME
        DOE
        
        2. GIVEN NAMES
        JOHN MICHAEL
        
        3. DATE OF BIRTH
        15.03.1990
        
        4a. DATE OF ISSUE
        20.05.2015
        
        4b. DATE OF EXPIRY
        20.05.2025
        
        5. AUTHORITY
        RSA
        
        7. LICENCE NUMBER
        123456789
        """,
        
        "receipt": """
        WALMART STORE #1234
        123 Main Street, Anytown, USA
        Phone: (555) 123-4567
        
        Receipt #: 123456789
        Date: 12/15/2023
        Time: 14:30:25
        
        ITEMS:
        Milk 2% 1gal          $3.99
        Bread Whole Wheat     $2.49
        Eggs Large Dozen      $4.99
        Bananas 2lb           $1.98
        
        SUBTOTAL:             $13.45
        TAX:                  $1.08
        TOTAL:                $14.53
        
        Payment Method: VISA
        Card: ****1234
        """
    }
    
    return mock_texts.get(doc_type, f"Mock OCR text for {doc_type} document")


def test_document_parser(doc_type: str) -> Dict[str, Any]:
    """
    Test a specific document parser with mock OCR text.
    
    Args:
        doc_type: The document type to test
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*60}")
    print(f"Testing {doc_type.upper()} Parser")
    print(f"{'='*60}")
    
    try:
        # 1. Get document configuration
        config = get_document_config(doc_type)
        print(f"✓ Loaded config for {doc_type}")
        print(f"  Required fields: {config['required_fields']}")
        print(f"  Optional fields: {config['optional_fields']}")
        
        # 2. Get prompt path and load prompt
        prompt_path = get_prompt_path(doc_type)
        if not prompt_path.exists():
            print(f"❌ Prompt file not found: {prompt_path}")
            return {"success": False, "error": f"Prompt file not found: {prompt_path}"}
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        print(f"✓ Loaded prompt from: {prompt_path}")
        
        # 3. Get mock OCR text
        mock_ocr = get_mock_ocr_text(doc_type)
        print(f"✓ Generated mock OCR text ({len(mock_ocr)} characters)")
        print(f"  Preview: {mock_ocr[:100]}...")
        
        # 4. Run LLM extraction
        print("\n🔄 Running LLM extraction...")
        extracted_data = extract_fields_from_text(mock_ocr, prompt)
        print("✓ LLM extraction completed")
        
        # 5. Print extracted result
        print("\n📋 Extracted Data:")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        
        # 6. Validate output
        print("\n🔍 Validating output...")
        validator_fn = get_validator_function(doc_type)
        validated_data = validator_fn(extracted_data)
        print("✓ Validation completed")
        
        # 7. Postprocess output
        print("\n⚙️  Postprocessing output...")
        postprocess_fn = get_postprocess_function(doc_type)
        final_data = postprocess_fn(validated_data)
        print("✓ Postprocessing completed")
        
        # 8. Print final result
        print("\n🎯 Final Result:")
        print(json.dumps(final_data, indent=2, ensure_ascii=False))
        
        # 9. Check for required fields
        missing_required = []
        for field in config['required_fields']:
            if field not in final_data or final_data[field] is None:
                missing_required.append(field)
        
        if missing_required:
            print(f"\n⚠️  Missing required fields: {missing_required}")
            return {
                "success": False,
                "error": f"Missing required fields: {missing_required}",
                "data": final_data
            }
        else:
            print(f"\n✅ All required fields present: {config['required_fields']}")
            return {
                "success": True,
                "data": final_data,
                "missing_required": []
            }
            
    except Exception as e:
        print(f"\n❌ Error testing {doc_type}: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Main test function that iterates through all document types.
    """
    print("🧪 DOC-IQ Parser Configuration Test")
    print("=" * 60)
    
    # Get all supported document types
    supported_types = get_supported_document_types()
    print(f"Found {len(supported_types)} supported document types: {supported_types}")
    
    # Test results summary
    results = {}
    successful_tests = 0
    failed_tests = 0
    
    # Test each document type
    for doc_type in supported_types:
        result = test_document_parser(doc_type)
        results[doc_type] = result
        
        if result["success"]:
            successful_tests += 1
        else:
            failed_tests += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total document types tested: {len(supported_types)}")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {failed_tests}")
    print(f"Success rate: {(successful_tests/len(supported_types)*100):.1f}%")
    
    # Print detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for doc_type, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {doc_type}: {status}")
        if not result["success"]:
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    # Save results to file
    output_file = Path("test/output/config_test_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Exit with error code if any tests failed
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the results above.")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed successfully!")


if __name__ == "__main__":
    main() 