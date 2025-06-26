#!/usr/bin/env python3
"""
Receipt Document Processing Pipeline
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

# Import our modules
from doc_pipeline.ocr.ocr_engine import extract_text_from_file, get_supported_formats
from doc_pipeline.extractors.receipt import parse_receipt
from doc_pipeline.parsers.receipt_parser import parse_receipt as parse_receipt_regex, ReceiptExtractionError
from doc_pipeline.utils.validators import validate_receipt_output

logger = logging.getLogger(__name__)

def process_documents(input_dir: Path, output_dir: Path, test_mode: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Process receipt documents.
    
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
    supported_exts = get_supported_formats()
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts]
    
    if test_mode and files:
        files = files[:1]  # Process only first file in test mode
    
    total = len(files)
    success = 0
    failed = 0
    gemini_fallback = 0
    
    for file in files:
        try:
            logger.info(f"Processing: {file}")
            ocr_text = extract_text_from_file(str(file))
            
            # Try regex first, fallback to Gemini
            try:
                regex_result = parse_receipt_regex(ocr_text)
                if validate_receipt_output(regex_result):
                    logger.info("Regex extraction succeeded.")
                    result = regex_result
                else:
                    logger.info("Regex extraction failed, falling back to Gemini.")
                    result = parse_receipt(ocr_text)
                    gemini_fallback += 1
            except ReceiptExtractionError:
                logger.info("Regex extraction failed, falling back to Gemini.")
                result = parse_receipt(ocr_text)
                gemini_fallback += 1
            
            # Validate and save
            if not validate_receipt_output(result):
                raise Exception("Validation failed for receipt output.")
            
            output_file = output_dir / (file.stem + ".json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved: {output_file}")
            success += 1
            
        except Exception as e:
            logger.error(f"Failed to process {file}: {e}")
            failed += 1
    
    return {
        "total_files": total,
        "success": success,
        "failed": failed,
        "gemini_fallback": gemini_fallback
    }


class ReceiptPipeline:
    """
    Receipt Pipeline class for compatibility with backend.
    """
    
    def __init__(self, ocr_engine, gemini_client):
        """
        Initialize the receipt pipeline.
        
        Args:
            ocr_engine: OCR engine instance
            gemini_client: Gemini client instance
        """
        self.ocr_engine = ocr_engine
        self.gemini_client = gemini_client
        self.logger = logging.getLogger(__name__)
    
    def process_single_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Process a single receipt file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            
        Returns:
            Dict with extracted data
        """
        try:
            self.logger.info(f"Processing receipt: {input_file}")
            
            # Extract text using OCR
            ocr_text = self.ocr_engine.extract_text(input_file)
            
            # Try regex first, fallback to Gemini
            try:
                regex_result = parse_receipt_regex(ocr_text)
                if validate_receipt_output(regex_result):
                    self.logger.info("Regex extraction succeeded.")
                    result = regex_result
                else:
                    self.logger.info("Regex extraction failed, falling back to Gemini.")
                    result = parse_receipt(ocr_text)
            except ReceiptExtractionError:
                self.logger.info("Regex extraction failed, falling back to Gemini.")
                result = parse_receipt(ocr_text)
            
            # Validate and save
            if not validate_receipt_output(result):
                raise Exception("Validation failed for receipt output.")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved receipt data: {output_file}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process receipt {input_file}: {e}")
            raise 