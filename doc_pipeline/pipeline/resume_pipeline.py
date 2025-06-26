#!/usr/bin/env python3
"""
Resume Document Processing Pipeline
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

# Import our modules
from doc_pipeline.extractors.resume import parse_resume

logger = logging.getLogger(__name__)

def is_valid_resume_file(file_path: Path) -> bool:
    """Check if file is a valid resume file."""
    valid_extensions = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png'}
    return file_path.suffix.lower() in valid_extensions

def extract_text_from_resume_file(file_path: Path) -> str:
    """Extract text from resume file."""
    try:
        # For now, use OCR for all file types
        from doc_pipeline.ocr.ocr_engine import extract_text_from_file
        return extract_text_from_file(str(file_path))
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        return ""

def process_documents(input_dir: Path, output_dir: Path, test_mode: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Process resume documents.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        test_mode: Process only 1 file if True
        verbose: Enable verbose logging
        
    Returns:
        Dict with processing results
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in input_dir.iterdir() if is_valid_resume_file(f)]
    
    if test_mode and files:
        files = files[:1]  # Process only first file in test mode
    
    total = len(files)
    processed = 0
    skipped = 0
    errors = 0
    gemini_fallback = 0
    
    for file in files:
        try:
            logger.info(f"Processing: {file}")
            text = extract_text_from_resume_file(file)
            
            if text.strip():
                # Extract fields (resume parsing always uses Gemini fallback for missing fields)
                parsed = parse_resume(text)
                out_json = output_dir / (file.stem + ".json")
                with open(out_json, 'w', encoding='utf-8') as fout:
                    json.dump(parsed, fout, indent=2, ensure_ascii=False)
                logger.info(f"Extracted fields saved to: {out_json}")
                processed += 1
                
                # Check if Gemini was used (resume parsing always uses it for missing fields)
                gemini_fallback += 1
            else:
                logger.warning(f"No text extracted from: {file}")
                skipped += 1
                
        except Exception as e:
            logger.error(f"Error processing {file}: {e}")
            errors += 1
    
    return {
        "total_files": total,
        "success": processed,
        "failed": errors,
        "skipped": skipped,
        "gemini_fallback": gemini_fallback
    }


class ResumePipeline:
    """
    Resume Pipeline class for compatibility with backend.
    """
    
    def __init__(self, ocr_engine, gemini_client):
        """
        Initialize the resume pipeline.
        
        Args:
            ocr_engine: OCR engine instance
            gemini_client: Gemini client instance
        """
        self.ocr_engine = ocr_engine
        self.gemini_client = gemini_client
        self.logger = logging.getLogger(__name__)
    
    def process_single_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Process a single resume file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            
        Returns:
            Dict with extracted data
        """
        try:
            self.logger.info(f"Processing resume: {input_file}")
            
            # Extract text from resume file
            text = extract_text_from_resume_file(Path(input_file))
            
            if text.strip():
                # Parse resume data
                parsed_data = parse_resume(text)
                
                # Save results
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Saved resume data: {output_file}")
                return parsed_data
            else:
                raise Exception("No text extracted from resume file")
                
        except Exception as e:
            self.logger.error(f"Failed to process resume {input_file}: {e}")
            raise 