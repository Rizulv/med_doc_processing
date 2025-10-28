from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db import crud
from app.services.text_extract import extract_text_from_upload
from app.services.storage_local import storage
from app.services.anthropic_client import client
import json

router = APIRouter()


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    run_pipeline: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload a document and optionally run the full pipeline
    
    Args:
        file: PDF or TXT file
        run_pipeline: If true, runs classify -> extract_codes -> summarize
        
    Returns:
        {
            document_id: int,
            processed: bool,
            results?: {classification, codes, summary}
        }
    """
    # Extract text from file
    try:
        document_text = extract_text_from_upload(file)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")
    
    # Reset file pointer for storage
    await file.seek(0)
    
    # Save file to local storage
    try:
        local_path = storage.save_file(file.file, file.filename or "unknown.txt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record
    doc = crud.create_document(db, file.filename or "unknown.txt", local_path)
    
    # Run pipeline if requested
    results = None
    if run_pipeline:
        try:
            # Step 1: Classify
            classification = client.classify(document_text)
            
            # Step 2: Extract codes
            codes = client.extract_codes(document_text, classification.get("document_type"))
            
            # Step 3: Summarize
            summary = client.summarize(
                document_text,
                classification.get("document_type"),
                codes.get("codes", [])
            )
            
            # Combine results
            results = {
                "classification": classification,
                "codes": codes,
                "summary": summary
            }
            
            # Save results
            crud.save_result(db, doc.id, results)
            
        except Exception as e:
            # Document is saved, but pipeline failed
            raise HTTPException(
                status_code=500,
                detail=f"Document saved but pipeline failed: {str(e)}"
            )
    
    return {
        "document_id": doc.id,
        "processed": run_pipeline,
        "results": results
    }


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """
    List all documents (most recent 50)
    
    Returns: List of documents with basic metadata
    """
    docs = crud.list_documents(db, limit=50)
    
    return [
        {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "created_at": doc.created_at.isoformat(),
            "local_path": doc.local_path
        }
        for doc in docs
    ]


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get document details including processing results
    
    Returns: Document with results if available
    """
    doc = crud.get_document(db, document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get results if available
    results = crud.get_document_result(db, document_id)
    
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "created_at": doc.created_at.isoformat(),
        "local_path": doc.local_path,
        "results": results
    }
