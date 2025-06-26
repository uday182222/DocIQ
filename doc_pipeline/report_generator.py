#!/usr/bin/env python3
"""
Report Generator for Document Processing Pipeline
Analyzes JSON output files and generates summary reports.
"""

import argparse
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def detect_document_type(file_path: Path) -> str:
    """
    Detect document type from filename or folder name.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Document type: 'license', 'receipt', or 'resume'
    """
    # Check parent directory name first
    parent_dir = file_path.parent.name.lower()
    if 'license' in parent_dir:
        return 'license'
    elif 'receipt' in parent_dir:
        return 'receipt'
    elif 'resume' in parent_dir:
        return 'resume'
    
    # Check filename for patterns
    filename = file_path.stem.lower()
    if any(keyword in filename for keyword in ['license', 'driving', 'id']):
        return 'license'
    elif any(keyword in filename for keyword in ['receipt', 'invoice', 'bill']):
        return 'receipt'
    elif any(keyword in filename for keyword in ['resume', 'cv', 'curriculum']):
        return 'resume'
    
    # Default based on common patterns
    return 'unknown'

def get_expected_fields(doc_type: str) -> List[str]:
    """
    Get expected fields for each document type.
    
    Args:
        doc_type: Document type
        
    Returns:
        List of expected field names
    """
    if doc_type == 'license':
        return ['Name', 'DateOfBirth', 'LicenseNumber', 'Address', 'IssueDate', 'ExpiryDate']
    elif doc_type == 'receipt':
        return ['MerchantName', 'TotalAmount', 'DateOfPurchase', 'Items', 'PaymentMethod']
    elif doc_type == 'resume':
        return ['FullName', 'Email', 'PhoneNumber', 'Skills', 'WorkExperience', 'Education']
    else:
        return []

def analyze_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a single JSON file and extract metrics.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with analysis results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doc_type = detect_document_type(file_path)
        expected_fields = get_expected_fields(doc_type)
        
        # Count total fields
        total_fields = len(expected_fields)
        
        # Count missing/null fields
        missing_fields = 0
        for field in expected_fields:
            value = data.get(field)
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                missing_fields += 1
        
        # Determine fallback used (check for Gemini usage patterns)
        fallback_used = False
        if doc_type == 'resume':
            # Resume always uses Gemini for missing fields
            fallback_used = missing_fields > 0
        elif doc_type == 'receipt':
            # Check if items were extracted (indicates Gemini fallback)
            items = data.get('Items', [])
            if items and len(items) > 0:
                # Check if items have names (regex might not extract names)
                has_item_names = any(item.get('name') for item in items if isinstance(item, dict))
                fallback_used = has_item_names
        elif doc_type == 'license':
            # License parsing always uses Gemini
            fallback_used = True
        
        # Calculate completion rate
        completion_rate = ((total_fields - missing_fields) / total_fields * 100) if total_fields > 0 else 0
        
        return {
            'filename': file_path.name,
            'document_type': doc_type,
            'total_fields': total_fields,
            'missing_fields': missing_fields,
            'fallback_used': fallback_used,
            'completion_rate': round(completion_rate, 2)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return {
            'filename': file_path.name,
            'document_type': 'error',
            'total_fields': 0,
            'missing_fields': 0,
            'fallback_used': False,
            'completion_rate': 0
        }

def generate_csv_report(results: List[Dict[str, Any]], output_path: Path):
    """
    Generate CSV report.
    
    Args:
        results: List of analysis results
        output_path: Output file path
    """
    fieldnames = ['FileName', 'DocumentType', 'TotalFields', 'MissingFields', 'FallbackUsed', 'CompletionRate']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'FileName': result['filename'],
                'DocumentType': result['document_type'],
                'TotalFields': result['total_fields'],
                'MissingFields': result['missing_fields'],
                'FallbackUsed': 'Yes' if result['fallback_used'] else 'No',
                'CompletionRate': f"{result['completion_rate']}%"
            })

def generate_markdown_report(results: List[Dict[str, Any]], output_path: Path):
    """
    Generate Markdown report.
    
    Args:
        results: List of analysis results
        output_path: Output file path
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Document Processing Report\n\n")
        f.write("## Summary\n\n")
        
        # Summary statistics
        total_files = len(results)
        total_completion = sum(r['completion_rate'] for r in results)
        avg_completion = total_completion / total_files if total_files > 0 else 0
        fallback_count = sum(1 for r in results if r['fallback_used'])
        
        f.write(f"- **Total Files Processed**: {total_files}\n")
        f.write(f"- **Average Completion Rate**: {avg_completion:.2f}%\n")
        f.write(f"- **Files Using Fallback**: {fallback_count}\n\n")
        
        # Detailed table
        f.write("## Detailed Results\n\n")
        f.write("| FileName | DocumentType | TotalFields | MissingFields | FallbackUsed | CompletionRate |\n")
        f.write("|----------|--------------|-------------|---------------|--------------|----------------|\n")
        
        for result in results:
            f.write(f"| {result['filename']} | {result['document_type']} | {result['total_fields']} | {result['missing_fields']} | {'Yes' if result['fallback_used'] else 'No'} | {result['completion_rate']}% |\n")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate reports from document processing JSON outputs")
    parser.add_argument("--input", "-i", type=str, required=True, 
                       help="Path to folder containing JSON output files")
    parser.add_argument("--format", "-f", type=str, choices=['csv', 'md'], default='csv',
                       help="Output format: csv (default) or md (markdown)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1
    
    # Find all JSON files
    json_files = list(input_path.rglob("*.json"))
    if not json_files:
        logger.error(f"No JSON files found in {input_path}")
        return 1
    
    logger.info(f"Found {len(json_files)} JSON files to analyze")
    
    # Analyze each file
    results = []
    for json_file in json_files:
        logger.info(f"Analyzing {json_file}")
        result = analyze_json_file(json_file)
        results.append(result)
    
    # Generate report
    output_filename = f"report_summary.{args.format}"
    output_path = input_path / output_filename
    
    if args.format == 'csv':
        generate_csv_report(results, output_path)
    else:
        generate_markdown_report(results, output_path)
    
    # Log summary
    total_files = len(results)
    avg_completion = sum(r['completion_rate'] for r in results) / total_files if total_files > 0 else 0
    fallback_count = sum(1 for r in results if r['fallback_used'])
    
    logger.info("=" * 60)
    logger.info("REPORT GENERATION COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Total Files Analyzed: {total_files}")
    logger.info(f"Average Completion Rate: {avg_completion:.2f}%")
    logger.info(f"Files Using Fallback: {fallback_count}")
    logger.info(f"Report saved to: {output_path}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main()) 