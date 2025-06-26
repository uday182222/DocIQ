#!/usr/bin/env python3
"""
Test script for resume parsing
"""

import json
import os
import sys
from pathlib import Path

# Add doc_pipeline to path
sys.path.append(str(Path(__file__).parent / "doc_pipeline"))

from llm.llm_client import extract_fields_from_text
from utils.file_utils import load_text


def test_resume_parser():
    """Test resume parsing with OCR text files"""
    
    # Paths
    test_dir = Path("test/resumes")
    prompt_path = Path("doc_pipeline/prompts/resume_extraction.txt")
    output_dir = Path("test/output")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if test directory exists
    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return
    
    # Check if prompt exists
    if not prompt_path.exists():
        print(f"Prompt file not found: {prompt_path}")
        return
    
    # Load the prompt
    prompt = load_text(str(prompt_path))
    print(f"Loaded prompt from: {prompt_path}")
    
    # Process each .txt file in test/resumes/
    txt_files = list(test_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in {test_dir}")
        return
    
    print(f"Found {len(txt_files)} test files")
    
    for txt_file in txt_files:
        print(f"\n{'='*50}")
        print(f"Processing: {txt_file.name}")
        print(f"{'='*50}")
        
        try:
            # Load OCR text
            ocr_text = load_text(str(txt_file))
            print(f"OCR Text length: {len(ocr_text)} characters")
            print(f"OCR Text preview: {ocr_text[:200]}...")
            
            # Extract fields using LLM
            print("\nExtracting fields...")
            result = extract_fields_from_text(ocr_text, str(prompt_path))
            
            # Print result with indentation
            print("\nExtracted Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check if all values are null or empty
            all_empty = True
            for key, value in result.items():
                if value is not None and value != "" and value != []:
                    all_empty = False
                    break
            
            # Save result to JSON file
            output_file = output_dir / f"{txt_file.stem}_result.json"
            
            if all_empty:
                print(f"\n⚠️  All extracted values are null/empty. Deleting output file: {output_file}")
                if output_file.exists():
                    output_file.unlink()
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Result saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {txt_file.name}: {e}")
            continue
    
    print(f"\n{'='*50}")
    print("Testing complete!")


if __name__ == "__main__":
    test_resume_parser() 