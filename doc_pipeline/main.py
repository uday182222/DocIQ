#!/usr/bin/env python3
"""
FastAPI server for document processing
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import json
import tempfile
import os
from pathlib import Path
from pipeline.generic_pipeline import process_document

app = FastAPI(title="Document Processing API", version="1.0.0")

# Supported file types
SUPPORTED_TYPES = {
    "image": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
    "pdf": [".pdf"]
}

@app.get("/")
async def root():
    return {"message": "Document Processing API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-processor"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(..., description="Document type: resume, receipt, or license")
):
    """
    Upload and process a document
    """
    # Validate document type
    if doc_type not in ["resume", "receipt", "license"]:
        raise HTTPException(status_code=400, detail="Invalid doc_type. Must be resume, receipt, or license")
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    supported_extensions = SUPPORTED_TYPES["image"] + SUPPORTED_TYPES["pdf"]
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
        )
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the document
        prompt_dir = Path(__file__).parent / "prompts"
        result = process_document(temp_file_path, doc_type, str(prompt_dir))
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Parse the JSON result
        parsed_result = json.loads(result)
        
        return JSONResponse(content=parsed_result)
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/supported-types")
async def get_supported_types():
    """Get supported file types and document types"""
    return {
        "document_types": ["resume", "receipt", "license"],
        "file_types": {
            "images": SUPPORTED_TYPES["image"],
            "pdfs": SUPPORTED_TYPES["pdf"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 