import json
import os
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF


def normalize_file(file_path: str) -> str:
    """
    Convert image/PDF to standard format.
    For images: ensure they're in a supported format (JPEG/PNG)
    For PDFs: return the path as-is
    Returns the normalized file path.
    """
    file_path = str(file_path)
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # If it's already a PDF, return as-is
    if path.suffix.lower() == '.pdf':
        return file_path
    
    # For images, ensure they're in a supported format
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # If it's not JPEG or PNG, convert to JPEG
            if path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                new_path = path.with_suffix('.jpg')
                img.save(new_path, 'JPEG', quality=95)
                return str(new_path)
            
            return file_path
    except Exception as e:
        raise RuntimeError(f"Failed to normalize file {file_path}: {e}")


def save_file(data, out_path: str) -> None:
    """
    Write JSON data to disk.
    Args:
        data: Data to save (dict, list, or JSON-serializable object)
        out_path: Output file path
    """
    out_path = str(out_path)
    path = Path(out_path)
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to save file to {out_path}: {e}")


def load_text(file_path: str) -> str:
    """
    Read a file as string.
    Args:
        file_path: Path to the file to read
    Returns:
        File contents as string
    """
    file_path = str(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to load text from {file_path}: {e}") 