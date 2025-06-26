#!/usr/bin/env python3
"""
Test script for document configuration module
"""

import sys
from pathlib import Path

# Add the doc_pipeline directory to the Python path
sys.path.append('doc_pipeline')

from config.doc_config import (
    get_document_config,
    get_supported_document_types,
    validate_document_type,
    get_prompt_path,
    get_validator_function,
    get_postprocess_function
)


def test_document_config():
    """
    Test the document configuration module.
    """
    print("=== Document Configuration Test ===")
    
    try:
        # 1. Test supported document types
        print("1. Testing supported document types...")
        supported_types = get_supported_document_types()
        print(f"   Supported types: {supported_types}")
        assert "resume" in supported_types
        assert "license" in supported_types
        assert "receipt" in supported_types
        print("   ✓ All expected document types are supported")
        
        # 2. Test document type validation
        print("\n2. Testing document type validation...")
        assert validate_document_type("resume") == True
        assert validate_document_type("license") == True
        assert validate_document_type("receipt") == True
        assert validate_document_type("invalid") == False
        print("   ✓ Document type validation working correctly")
        
        # 3. Test getting configurations
        print("\n3. Testing configuration retrieval...")
        for doc_type in supported_types:
            config = get_document_config(doc_type)
            print(f"   {doc_type}:")
            print(f"     Required fields: {config['required_fields']}")
            print(f"     Optional fields: {config['optional_fields']}")
            print(f"     Prompt path: {config['prompt_path']}")
            print(f"     Has validator: {config['validator_fn'] is not None}")
            print(f"     Has postprocessor: {config['postprocess_fn'] is not None}")
        
        # 4. Test prompt paths
        print("\n4. Testing prompt paths...")
        for doc_type in supported_types:
            prompt_path = get_prompt_path(doc_type)
            print(f"   {doc_type}: {prompt_path}")
            assert prompt_path.exists(), f"Prompt file not found: {prompt_path}"
        print("   ✓ All prompt files exist")
        
        # 5. Test validator functions
        print("\n5. Testing validator functions...")
        for doc_type in supported_types:
            validator_fn = get_validator_function(doc_type)
            print(f"   {doc_type}: {validator_fn.__name__}")
            assert callable(validator_fn), f"Validator for {doc_type} is not callable"
        print("   ✓ All validator functions are callable")
        
        # 6. Test postprocessor functions
        print("\n6. Testing postprocessor functions...")
        for doc_type in supported_types:
            postprocess_fn = get_postprocess_function(doc_type)
            print(f"   {doc_type}: {postprocess_fn.__name__}")
            assert callable(postprocess_fn), f"Postprocessor for {doc_type} is not callable"
        print("   ✓ All postprocessor functions are callable")
        
        # 7. Test error handling
        print("\n7. Testing error handling...")
        try:
            get_document_config("invalid_type")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"   ✓ Correctly raised ValueError: {e}")
        
        print("\n=== All tests passed successfully! ===")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_document_config() 