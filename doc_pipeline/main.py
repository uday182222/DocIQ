#!/usr/bin/env python3
"""
Document Processing Pipeline - Main Entry Point

A scalable pipeline that processes documents using OCR + Gemini,
with modular extractors per document type.
"""

import argparse
import logging
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import fitz  # PyMuPDF
import pdfplumber

# Import our modules
from doc_pipeline.ocr.ocr_engine import extract_text_from_file, get_supported_formats
from extractors.license import parse_license
from extractors.receipt import parse_receipt
from utils.validators import validate_extracted_data, validate_receipt_output, get_supported_document_types
from config import RECEIPT_INPUT_DIR, RECEIPT_OUTPUT_DIR
from parsers.driving_license_parser import parse_irish_driving_license
from parsers.receipt_parser import parse_receipt as parse_receipt_regex, ReceiptExtractionError
from extractors.resume import parse_resume

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Document type handlers
DOCUMENT_HANDLERS = {
    "license": parse_license,
    "receipt": parse_receipt,
    # 'resume' will be added later
}

SUPPORTED_RESUME_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png'}
CACHE_RESUME_DIR = Path("cache/resumes")
CACHE_RESUME_DIR.mkdir(parents=True, exist_ok=True)

def is_valid_resume_file(file_path: Path) -> bool:
    """Validate if the file is a supported resume format and not hidden/temp."""
    return file_path.is_file() and file_path.suffix.lower() in SUPPORTED_RESUME_FORMATS and not file_path.name.startswith('.')


def write_error_to_log(error_message: str, output_folder: Path):
    """
    Write error message to errors.log file in the output folder.
    
    Args:
        error_message (str): Error message to write
        output_folder (Path): Output folder path
    """
    try:
        errors_log_path = output_folder / "errors.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(errors_log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {error_message}\n")
            
    except Exception as e:
        logger.error(f"Failed to write to errors.log: {e}")


def process_single_file(input_path: Path, output_path: Path, doc_type: str, output_folder: Path) -> Dict[str, Any]:
    """
    Process a single image file through the pipeline.
    
    Args:
        input_path: Path to input image file
        output_path: Path to save output JSON
        doc_type: Type of document to process
        output_folder: Output folder for error logging
        
    Returns:
        Dict with processing results
    """
    try:
        logger.info(f"Processing: {input_path}")
        
        # Step 1: Extract text using OCR
        ocr_text = extract_text_from_file(str(input_path))
        logger.info(f"OCR completed for {input_path}")
        
        # Step 2: Parse based on document type
        if doc_type in DOCUMENT_HANDLERS:
            parsed_data = DOCUMENT_HANDLERS[doc_type](ocr_text)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")
        
        # Step 3: Save results
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully processed: {input_path} -> {output_path}")
        return {
            "status": "success",
            "input_file": str(input_path),
            "output_file": str(output_path),
            "extracted_data": parsed_data
        }
        
    except Exception as e:
        error_message = f"Error processing {input_path}: {str(e)}"
        logger.error(error_message)
        
        # Write error to log file
        write_error_to_log(error_message, output_folder)
        
        return {
            "status": "error",
            "input_file": str(input_path),
            "error": str(e)
        }


def process_folder(input_folder: Path, output_folder: Path, doc_type: str) -> Dict[str, Any]:
    """
    Process all supported images in a folder.
    
    Args:
        input_folder: Path to input folder
        output_folder: Path to output folder
        doc_type: Type of document to process
        
    Returns:
        Dict with batch processing results
    """
    logger.info(f"Starting batch processing: {input_folder} -> {output_folder}")
    
    # Supported image extensions
    supported_extensions = {'.jpg', '.jpeg', '.png'}
    
    # Find all supported image files
    image_files = [
        f for f in input_folder.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not image_files:
        logger.warning(f"No supported image files found in {input_folder}")
        return {"status": "no_files", "processed": 0, "errors": 0}
    
    logger.info(f"Found {len(image_files)} image files to process")
    
    # Process each file
    results = []
    success_count = 0
    error_count = 0
    
    for image_file in image_files:
        # Create output filename (same name + .json)
        output_filename = image_file.stem + '.json'
        output_path = output_folder / output_filename
        
        # Process the file
        result = process_single_file(image_file, output_path, doc_type, output_folder)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
        else:
            error_count += 1
    
    # Summary
    summary = {
        "status": "completed",
        "total_files": len(image_files),
        "successful": success_count,
        "errors": error_count,
        "results": results
    }
    
    logger.info(f"Batch processing completed: {success_count} successful, {error_count} errors")
    return summary


def process_licenses(input_dir: Path, output_dir: Path, test: bool = False) -> dict:
    """Process license documents with test mode support."""
    os.makedirs(output_dir, exist_ok=True)
    supported_exts = get_supported_formats()
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts]
    
    if test and files:
        files = files[:1]  # Process only first file in test mode
    
    total = len(files)
    success = 0
    failed = 0
    
    for file in files:
        try:
            logger.info(f"Processing: {file}")
            ocr_text = extract_text_from_file(str(file))
            parsed_data = parse_license(ocr_text)
            
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
        "successful": success,
        "failed": failed
    }

def process_receipts(input_dir: Path, output_dir: Path, test: bool = False) -> dict:
    """Process receipt documents with test mode support."""
    os.makedirs(output_dir, exist_ok=True)
    supported_exts = get_supported_formats()
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts]
    
    if test and files:
        files = files[:1]  # Process only first file in test mode
    
    total = len(files)
    success = 0
    failed = 0
    
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
            except ReceiptExtractionError:
                logger.info("Regex extraction failed, falling back to Gemini.")
                result = parse_receipt(ocr_text)
            
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
        "successful": success,
        "failed": failed
    }

def process_resumes(input_dir: Path, output_dir: Path, test: bool = False) -> dict:
    """Process resume documents with test mode support."""
    os.makedirs(output_dir, exist_ok=True)
    CACHE_RESUME_DIR.mkdir(parents=True, exist_ok=True)
    
    files = [f for f in input_dir.iterdir() if is_valid_resume_file(f)]
    
    if test and files:
        files = files[:1]  # Process only first file in test mode
    
    total = len(files)
    processed = 0
    skipped = 0
    errors = 0
    
    for file in files:
        try:
            logger.info(f"Processing: {file}")
            text = extract_text_from_resume_file(file)
            
            if text.strip():
                # Save raw text to cache
                cache_txt = CACHE_RESUME_DIR / (file.stem + ".txt")
                with open(cache_txt, 'w', encoding='utf-8') as ftxt:
                    ftxt.write(text)
                logger.info(f"Extracted text saved to: {cache_txt}")
                
                # Extract fields
                parsed = parse_resume(text)
                out_json = output_dir / (file.stem + ".json")
                with open(out_json, 'w', encoding='utf-8') as fout:
                    json.dump(parsed, fout, indent=2, ensure_ascii=False)
                logger.info(f"Extracted fields saved to: {out_json}")
                processed += 1
            else:
                logger.warning(f"No text extracted from: {file}")
                skipped += 1
                
        except Exception as e:
            logger.error(f"Error processing {file}: {e}")
            errors += 1
    
    return {
        "total_files": total,
        "successful": processed,
        "failed": errors,
        "skipped": skipped
    }

def extract_text_from_resume_file(file_path: Path) -> str:
    """
    Extract readable text from a resume file (image or PDF).
    Returns the extracted text (may be empty if failed).
    """
    suffix = file_path.suffix.lower()
    if suffix in {'.jpg', '.jpeg', '.png'}:
        # Use existing OCR pipeline
        return extract_text_from_file(str(file_path))
    elif suffix == '.pdf':
        # Try PyMuPDF first
        try:
            doc = fitz.open(str(file_path))
            text = "\n".join(page.get_text() for page in doc)
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"PyMuPDF failed for {file_path}: {e}")
        # Try pdfplumber
        try:
            with pdfplumber.open(str(file_path)) as pdf:
                text = "\n".join(page.extract_text() or '' for page in pdf.pages)
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
        # Fallback: OCR each page as image
        try:
            doc = fitz.open(str(file_path))
            ocr_text = []
            for page in doc:
                pix = page.get_pixmap()
                img_path = CACHE_RESUME_DIR / f"{file_path.stem}_page{page.number+1}.png"
                pix.save(str(img_path))
                ocr_text.append(extract_text_from_file(str(img_path)))
                img_path.unlink()  # Remove temp image
            return "\n".join(ocr_text)
        except Exception as e:
            logger.error(f"OCR fallback failed for {file_path}: {e}")
            return ""
    else:
        logger.error(f"Unsupported file type: {file_path}")
        return ""


def main():
    """Main entry point for the document processing pipeline."""
    parser = argparse.ArgumentParser(description="Document Processing Pipeline")
    parser.add_argument("--type", type=str, default="license", choices=["license", "receipt", "resume"], help="Document type to process (default: license)")
    parser.add_argument("--input", type=str, help="Input folder (overrides default)")
    parser.add_argument("--output", type=str, help="Output folder (overrides default)")
    parser.add_argument("--input-dir", type=str, help="Input folder for resumes (for --type resume)")
    parser.add_argument("--output-dir", type=str, help="Output folder for resumes (for --type resume)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.type == "receipt":
        process_receipts()
    elif args.type == "resume":
        # Use --input-dir and --output-dir for resumes
        if not args.input_dir or not args.output_dir:
            parser.error("the following arguments are required for resume: --input-dir, --output-dir")
        process_resumes(Path(args.input_dir), Path(args.output_dir))
    else:
        # For license, require input/output
        if not args.input or not args.output:
            parser.error("the following arguments are required for license: --input, --output")
        # Existing license processing logic
        pass


if __name__ == "__main__":
    main() 