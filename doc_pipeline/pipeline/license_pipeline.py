#!/usr/bin/env python3
"""
License Document Processing Pipeline
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

# Import our modules
from doc_pipeline.ocr.ocr_engine import extract_text_from_file, get_supported_formats
from doc_pipeline.extractors.license import parse_license

logger = logging.getLogger(__name__)

def process_documents(input_dir: Path, output_dir: Path, test_mode: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Process license documents.
    
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
            parsed_data = parse_license(ocr_text)
            
            # Check if Gemini fallback was used (this would need to be tracked in parse_license)
            # For now, we'll assume it's always used since license parsing uses Gemini
            gemini_fallback += 1
            
            output_file = output_dir / (file.stem + ".json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
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


class LicensePipeline:
    """
    License Pipeline class for compatibility with backend.
    """
    
    def __init__(self, ocr_engine, gemini_client):
        """
        Initialize the license pipeline.
        
        Args:
            ocr_engine: OCR engine instance
            gemini_client: Gemini client instance
        """
        self.ocr_engine = ocr_engine
        self.gemini_client = gemini_client
        self.logger = logging.getLogger(__name__)
    
    def process_single_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Process a single license file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            
        Returns:
            Dict with extracted data
        """
        try:
            self.logger.info(f"Processing license: {input_file}")
            
            # Extract text using OCR
            ocr_text = self.ocr_engine.extract_text(input_file)
            
            # Parse license data
            parsed_data = parse_license(ocr_text)
            
            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved license data: {output_file}")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Failed to process license {input_file}: {e}")
            raise 