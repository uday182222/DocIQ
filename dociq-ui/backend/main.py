#!/usr/bin/env python3
"""
FastAPI backend for DocIQ React frontend
Integrates with the existing document processing pipeline
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Add the parent directory to Python path to import the pipeline modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the existing pipeline modules
try:
    from doc_pipeline.pipeline.license_pipeline import LicensePipeline
    from doc_pipeline.pipeline.receipt_pipeline import ReceiptPipeline
    from doc_pipeline.pipeline.resume_pipeline import ResumePipeline
    from doc_pipeline.llm.gemini_client import GeminiClient
    from doc_pipeline.ocr.ocr_engine import OCREngine
except ImportError as e:
    print(f"Warning: Could not import pipeline modules: {e}")
    print("Running in mock mode for development")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DocIQ API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ProcessingRequest(BaseModel):
    mode: str

class ProcessingStatus(BaseModel):
    fileId: str
    status: str
    progress: int
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class Statistics(BaseModel):
    totalDocuments: int
    processedToday: int
    pending: int
    successRate: float
    averageProcessingTime: float

# Global storage (replace with database in production)
documents_db: Dict[str, Dict[str, Any]] = {}
processing_tasks: Dict[str, asyncio.Task] = {}

# Initialize pipeline components (with fallback to mock)
try:
    ocr_engine = OCREngine()
    gemini_client = GeminiClient()
    license_pipeline = LicensePipeline(ocr_engine, gemini_client)
    receipt_pipeline = ReceiptPipeline(ocr_engine, gemini_client)
    resume_pipeline = ResumePipeline(ocr_engine, gemini_client)
    PIPELINE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Pipeline not available, using mock mode: {e}")
    PIPELINE_AVAILABLE = False

# File storage
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_file_id() -> str:
    """Generate a unique file ID"""
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"

async def process_document_background(file_id: str, file_path: Path, document_type: str, processing_mode: str):
    """Background task to process documents"""
    try:
        # Update status to processing
        documents_db[file_id]["status"] = "processing"
        documents_db[file_id]["progress"] = 10

        if PIPELINE_AVAILABLE:
            # Select pipeline based on processing mode
            if processing_mode == "license":
                pipeline = license_pipeline
            elif processing_mode == "receipt":
                pipeline = receipt_pipeline
            elif processing_mode == "resume":
                pipeline = resume_pipeline
            else:
                raise ValueError(f"Unknown processing mode: {processing_mode}")

            # Process with real pipeline
            documents_db[file_id]["progress"] = 30
            
            # Run the pipeline
            result = await asyncio.to_thread(
                pipeline.process_single_file,
                str(file_path),
                OUTPUT_DIR / f"{file_id}.json"
            )
            
            documents_db[file_id]["progress"] = 80
            
            # Load the result
            output_file = OUTPUT_DIR / f"{file_id}.json"
            if output_file.exists():
                with open(output_file, 'r') as f:
                    extracted_data = json.load(f)
            else:
                extracted_data = {"error": "Processing failed"}
            
            documents_db[file_id]["progress"] = 100
            documents_db[file_id]["status"] = "completed"
            documents_db[file_id]["processedAt"] = datetime.now().isoformat()
            documents_db[file_id]["extractedFields"] = extracted_data
            documents_db[file_id]["completionRate"] = 95.0
            
        else:
            # Mock processing for development
            await asyncio.sleep(2)  # Simulate processing time
            documents_db[file_id]["progress"] = 50
            await asyncio.sleep(1)
            documents_db[file_id]["progress"] = 100
            
            # Mock extracted data
            mock_data = {
                "license": {
                    "name": "John Doe",
                    "licenseNumber": "DL123456789",
                    "dateOfBirth": "1990-05-15",
                    "expiryDate": "2025-05-15",
                    "address": "123 Main St, City, State"
                },
                "receipt": {
                    "merchantName": "Walmart",
                    "totalAmount": "$156.78",
                    "dateOfPurchase": "2024-01-14",
                    "items": [
                        {"name": "Groceries", "price": "$45.23"},
                        {"name": "Electronics", "price": "$111.55"}
                    ]
                },
                "resume": {
                    "fullName": "Jane Smith",
                    "email": "jane.smith@email.com",
                    "phone": "+1-555-0123",
                    "skills": ["React", "TypeScript", "Node.js", "Python"],
                    "experience": "5 years",
                    "education": "Bachelor in Computer Science"
                }
            }
            
            documents_db[file_id]["status"] = "completed"
            documents_db[file_id]["processedAt"] = datetime.now().isoformat()
            documents_db[file_id]["extractedFields"] = mock_data.get(processing_mode, {})
            documents_db[file_id]["completionRate"] = 92.0
            
    except Exception as e:
        logger.error(f"Processing failed for {file_id}: {e}")
        documents_db[file_id]["status"] = "failed"
        documents_db[file_id]["message"] = str(e)
        documents_db[file_id]["completionRate"] = 0.0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "pipeline_available": PIPELINE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    documentType: str = Form("license"),
    processingMode: str = Form("license")
):
    print(f"[DEBUG] Received upload: documentType={documentType}, processingMode={processingMode}, filename={getattr(file, 'filename', None)}")
    try:
        # Validate file
        if not file.filename:
            print("[DEBUG] No file provided or file.filename is empty")
            raise HTTPException(status_code=400, detail="No file provided")
        file_content = await file.read()
        print(f"[DEBUG] Uploaded file size: {len(file_content)} bytes")
        file.file.seek(0)  # Reset file pointer for later use
        
        # Generate file ID
        file_id = generate_file_id()
        
        # Save file
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create document record
        documents_db[file_id] = {
            "id": file_id,
            "filename": file.filename,
            "documentType": documentType,
            "status": "pending",
            "uploadedAt": datetime.now().isoformat(),
            "processedAt": None,
            "completionRate": 0.0,
            "extractedFields": {},
            "originalFile": str(file_path),
            "progress": 0,
            "message": None
        }
        
        # Start background processing
        background_tasks.add_task(
            process_document_background,
            file_id,
            file_path,
            documentType,
            processingMode
        )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "fileId": file_id
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_processing_status(file_id: str):
    """Get processing status for a file"""
    if file_id not in documents_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    doc = documents_db[file_id]
    return ProcessingStatus(
        fileId=file_id,
        status=doc["status"],
        progress=doc.get("progress", 0),
        message=doc.get("message"),
        result=doc.get("extractedFields")
    )

@app.get("/documents")
async def get_documents():
    """Get all processed documents"""
    documents = []
    for doc in documents_db.values():
        documents.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "documentType": doc["documentType"],
            "status": doc["status"],
            "uploadedAt": doc["uploadedAt"],
            "processedAt": doc["processedAt"],
            "completionRate": doc["completionRate"],
            "extractedFields": doc["extractedFields"],
            "thumbnail": None  # Could generate thumbnails here
        })
    
    # Sort by upload date (newest first)
    documents.sort(key=lambda x: x["uploadedAt"], reverse=True)
    return documents

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_db[document_id]
    return {
        "id": doc["id"],
        "filename": doc["filename"],
        "documentType": doc["documentType"],
        "status": doc["status"],
        "uploadedAt": doc["uploadedAt"],
        "processedAt": doc["processedAt"],
        "completionRate": doc["completionRate"],
        "extractedFields": doc["extractedFields"],
        "thumbnail": None
    }

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from database
    del documents_db[document_id]
    
    # Clean up files
    try:
        for file_path in UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path.unlink()
        output_file = OUTPUT_DIR / f"{document_id}.json"
        if output_file.exists():
            output_file.unlink()
    except Exception as e:
        logger.warning(f"Failed to clean up files for {document_id}: {e}")
    
    return {"success": True, "message": "Document deleted successfully"}

@app.get("/documents/{document_id}/download")
async def download_results(document_id: str):
    """Download processing results as JSON"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_db[document_id]
    if doc["status"] != "completed":
        raise HTTPException(status_code=400, detail="Document processing not completed")
    
    # Create JSON file
    result_file = OUTPUT_DIR / f"{document_id}_results.json"
    with open(result_file, 'w') as f:
        json.dump(doc["extractedFields"], f, indent=2)
    
    return FileResponse(
        result_file,
        filename=f"{doc['filename']}_results.json",
        media_type="application/json"
    )

@app.get("/statistics")
async def get_statistics():
    """Get processing statistics"""
    total = len(documents_db)
    today = datetime.now().date()
    
    processed_today = sum(
        1 for doc in documents_db.values()
        if datetime.fromisoformat(doc["uploadedAt"]).date() == today
    )
    
    pending = sum(1 for doc in documents_db.values() if doc["status"] == "pending")
    processing = sum(1 for doc in documents_db.values() if doc["status"] == "processing")
    completed = sum(1 for doc in documents_db.values() if doc["status"] == "completed")
    
    success_rate = (completed / total * 100) if total > 0 else 0
    
    return Statistics(
        totalDocuments=total,
        processedToday=processed_today,
        pending=pending + processing,
        successRate=round(success_rate, 2),
        averageProcessingTime=2.5  # Mock value
    )

@app.get("/activity")
async def get_recent_activity():
    """Get recent activity"""
    activities = []
    for doc in documents_db.values():
        activities.append({
            "id": doc["id"],
            "type": doc["documentType"],
            "action": "Processed" if doc["status"] == "completed" else "Uploaded",
            "time": doc["uploadedAt"],
            "status": doc["status"]
        })
    
    # Sort by time (newest first) and limit to 10
    activities.sort(key=lambda x: x["time"], reverse=True)
    return activities[:10]

@app.post("/process/{file_id}")
async def process_document(file_id: str, request: ProcessingRequest):
    """Manually trigger processing for a file"""
    if file_id not in documents_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    doc = documents_db[file_id]
    if doc["status"] in ["processing", "completed"]:
        raise HTTPException(status_code=400, detail="File already processed or processing")
    
    # Start processing
    file_path = Path(doc["originalFile"])
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        process_document_background,
        file_id,
        file_path,
        doc["documentType"],
        request.mode
    )
    
    return {"success": True, "message": "Processing started"}

@app.post("/retry/{file_id}")
async def retry_document(file_id: str):
    """Retry processing a failed document"""
    if file_id not in documents_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    doc = documents_db[file_id]
    if doc["status"] != "failed":
        raise HTTPException(status_code=400, detail="File is not in failed state")
    
    # Reset status and retry
    doc["status"] = "pending"
    doc["progress"] = 0
    doc["message"] = None
    
    file_path = Path(doc["originalFile"])
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        process_document_background,
        file_id,
        file_path,
        doc["documentType"],
        doc["documentType"]  # Use document type as processing mode
    )
    
    return {"success": True, "message": "Retry started"}

@app.get("/supported-types")
async def get_supported_types():
    """Get supported file types for each document type"""
    return {
        "license": [".jpg", ".jpeg", ".png"],
        "receipt": [".jpg", ".jpeg", ".png"],
        "resume": [".jpg", ".jpeg", ".png", ".pdf"]
    }

@app.post("/validate")
async def validate_file(file: UploadFile = File(...), documentType: str = "license"):
    """Validate file before upload"""
    # Check file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        return {
            "valid": False,
            "message": "File size exceeds 10MB limit",
            "maxSize": 10 * 1024 * 1024
        }
    
    # Check file extension
    supported_types = {
        "license": [".jpg", ".jpeg", ".png"],
        "receipt": [".jpg", ".jpeg", ".png"],
        "resume": [".jpg", ".jpeg", ".png", ".pdf"]
    }
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in supported_types.get(documentType, []):
        return {
            "valid": False,
            "message": f"File type {file_ext} not supported for {documentType}",
            "supportedTypes": supported_types.get(documentType, [])
        }
    
    return {
        "valid": True,
        "message": "File is valid",
        "maxSize": 10 * 1024 * 1024
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 