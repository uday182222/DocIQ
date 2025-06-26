#!/usr/bin/env python3
"""
Document Processing Pipeline CLI
A user-friendly command-line interface for processing documents.
"""

import typer
from pathlib import Path
from typing import Optional
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import pipeline modules
from pipeline.license_pipeline import process_documents as process_licenses
from pipeline.receipt_pipeline import process_documents as process_receipts
from pipeline.resume_pipeline import process_documents as process_resumes

app = typer.Typer(help="Document Processing Pipeline CLI")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_startup_message():
    """Show startup message with supported formats."""
    print("╔═════════╤═════════════════════════╤═══════════════════════════════════╗")
    print("║ Type    │ Formats                 │ Description                       ║")
    print("╠═════════╪═════════════════════════╪═══════════════════════════════════╣")
    print("║ License │ .jpg, .jpeg, .png       │ Driving licenses and ID documents ║")
    print("║ Receipt │ .jpg, .jpeg, .png       │ Shop receipts and invoices        ║")
    print("║ Resume  │ .pdf, .jpg, .jpeg, .png │ Resumes and CVs                   ║")
    print("╚═════════╧═════════════════════════╧═══════════════════════════════════╝")
    print()

def setup_logging(verbose: bool, output_dir: Path):
    """Setup logging configuration."""
    if verbose:
        # Create log file
        log_file = output_dir / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        
        print(f"📝 Detailed logs will be saved to: {log_file}")

def display_results(results: dict, mode: str):
    """Display processing results."""
    print("\n📊 Summary:")
    print(f"• Total Files: {results.get('total_files', 0)}")
    print(f"• Success: {results.get('success', 0)}")
    print(f"• Failed: {results.get('failed', 0)}")
    print(f"• Gemini Fallback Used: {results.get('gemini_fallback', 0)}")
    
    # Add skipped count for resumes
    if 'skipped' in results:
        print(f"• Skipped: {results.get('skipped', 0)}")

@app.command()
def process(
    mode: str = typer.Option(..., "--mode", "-m", help="Document type: license, receipt, or resume"),
    input_dir: Path = typer.Option(..., "--input", "-i", help="Input folder path"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output folder path (default: output/{mode})"),
    test: bool = typer.Option(False, "--test", help="Process only 1 file for testing"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Process documents using OCR and AI extraction.
    
    Examples:
    - python cli.py process --mode resume --input data/resumes --test
    - python cli.py process --mode receipt --input data/receipts --output results
    - python cli.py process --mode license --input data/licenses --verbose
    """
    
    # Validate mode
    if mode not in ["license", "receipt", "resume"]:
        print(f"❌ Invalid mode: {mode}. Must be one of: license, receipt, resume")
        raise typer.Exit(1)
    
    # Validate input directory
    if not input_dir.exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        raise typer.Exit(1)
    
    # Set default output directory if not provided
    if output_dir is None:
        output_dir = Path(f"output/{mode}")
    
    # Show startup message
    show_startup_message()
    
    # Setup logging
    setup_logging(verbose, output_dir)
    
    # Process documents based on mode
    try:
        if mode == "license":
            results = process_licenses(input_dir, output_dir, test, verbose)
        elif mode == "receipt":
            results = process_receipts(input_dir, output_dir, test, verbose)
        elif mode == "resume":
            results = process_resumes(input_dir, output_dir, test, verbose)
        
        # Display results
        display_results(results, mode)
        
        # Show output location
        print(f"\n✅ Processing completed!")
        print(f"📁 Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

@app.command()
def info():
    """Show information about supported document types and formats."""
    show_startup_message()
    print("Usage Examples:")
    print("• python cli.py process --mode resume --input data/resumes --test")
    print("• python cli.py process --mode receipt --input data/receipts --output results")
    print("• python cli.py process --mode license --input data/licenses --verbose")

if __name__ == "__main__":
    app() 