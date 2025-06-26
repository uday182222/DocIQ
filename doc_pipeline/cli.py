#!/usr/bin/env python3
"""
CLI tool for document processing
"""

import argparse
import json
import sys
from pathlib import Path
from pipeline.generic_pipeline import process_document


def main():
    parser = argparse.ArgumentParser(description="Document processing CLI")
    parser.add_argument("--mode", required=True, choices=["resume", "receipt", "license"],
                       help="Document type to process")
    parser.add_argument("--input", required=True, help="Input file or folder path")
    parser.add_argument("--output", required=True, help="Output path to save results")
    parser.add_argument("--prompt_dir", default="prompts", help="Directory containing prompt templates")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    prompt_dir = Path(args.prompt_dir)
    
    # Validate inputs
    if not input_path.exists():
        print(f"Error: Input path does not exist: {args.input}")
        sys.exit(1)
    
    if not prompt_dir.exists():
        print(f"Error: Prompt directory does not exist: {args.prompt_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process single file
    if input_path.is_file():
        try:
            print(f"Processing {input_path}...")
            result = process_document(str(input_path), args.mode, str(prompt_dir))
            
            # Save result
            output_file = output_path / f"{input_path.stem}_result.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            print(f"Result saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            sys.exit(1)
    
    # Process directory
    elif input_path.is_dir():
        supported_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp']
        files_processed = 0
        files_failed = 0
        
        for file_path in input_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    print(f"Processing {file_path.name}...")
                    result = process_document(str(file_path), args.mode, str(prompt_dir))
                    
                    # Save result
                    output_file = output_path / f"{file_path.stem}_result.json"
                    with open(output_file, 'w') as f:
                        f.write(result)
                    
                    files_processed += 1
                    print(f"✓ {file_path.name} -> {output_file.name}")
                    
                except Exception as e:
                    print(f"✗ {file_path.name}: {e}")
                    files_failed += 1
        
        print(f"\nProcessing complete:")
        print(f"  Files processed: {files_processed}")
        print(f"  Files failed: {files_failed}")
        
        if files_failed > 0:
            sys.exit(1)
    
    else:
        print(f"Error: Input path is neither a file nor directory: {args.input}")
        sys.exit(1)


if __name__ == "__main__":
    main() 