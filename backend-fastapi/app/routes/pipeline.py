from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db import crud
from app.services.text_extract import extract_text_from_upload
from app.services.storage_local import storage
from app.services.anthropic_client import client

router = APIRouter()

# Allowed document types (must match the frontend/schema)
ALLOWED_DOC_TYPES = {
    "COMPLETE BLOOD COUNT",
    "BASIC METABOLIC PANEL",
    "X-RAY",
    "CT",
    "CLINICAL NOTE",
}


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    run_pipeline: bool = Form(True),
    document_type_hint: Optional[str] = Form(None),  # <-- NEW
    db: Session = Depends(get_db),
):
    """
    Upload a document and optionally run the full pipeline.

    Form fields:
      - file: PDF or TXT
      - run_pipeline: if true, runs classify -> extract_codes -> summarize
      - document_type_hint: optional, one of 5 types; if provided, classification is skipped

    Returns:
      {
        document_id: int,
        processed: bool,
        results?: {classification, codes, summary}
      }
    """
    # 1) Extract text from file
    try:
        document_text = extract_text_from_upload(file)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    # 2) Validate that this is a medical document (not CV, resume, etc.)
    if run_pipeline:
        try:
            is_valid = client.validate_medical_document(document_text)
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail="This does not appear to be a medical document. Please upload a valid medical document (lab report, imaging report, or clinical note)."
                )
        except HTTPException:
            raise
        except Exception as e:
            # If validation fails for technical reasons, allow the document to proceed
            pass

    # Reset file pointer for storage
    await file.seek(0)

    # 2) Save file to local storage
    try:
        local_path = storage.save_file(file.file, file.filename or "unknown.txt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 3) Create DB record
    doc = crud.create_document(db, file.filename or "unknown.txt", local_path)

    # 4) Optionally run pipeline
    results = None
    if run_pipeline:
        try:
            # Normalize/validate user hint if present
            normalized_hint: Optional[str] = None
            if document_type_hint:
                candidate = document_type_hint.strip()
                # Enforce exact allowed names to keep everything predictable
                if candidate not in ALLOWED_DOC_TYPES:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Invalid document_type_hint. "
                            "Allowed: "
                            + ", ".join(sorted(ALLOWED_DOC_TYPES))
                        ),
                    )
                normalized_hint = candidate

            # Step 1: classification (skip if user provided hint)
            if normalized_hint:
                classification = {
                    "document_type": normalized_hint,
                    "confidence": 1.0,
                    "rationale": "User selected document type in UI; classification skipped.",
                    "evidence": [],
                }
            else:
                classification = client.classify(document_text)

            # Step 2: extract codes (use the resolved type)
            resolved_type = classification.get("document_type")
            codes = client.extract_codes(document_text, resolved_type)

            # Step 3: summarize
            summary = client.summarize(
                document_text,
                resolved_type,
                codes.get("codes", []),
            )

            conf = summary.get("confidence")
            try:
                conf = float(conf)
            except Exception:
                conf = None
            summary["confidence"] = max(0.0, min(1.0, conf)) if conf is not None else (0.75 if codes.get("codes") else 0.5)
            # Combine
            results = {
                "classification": classification,
                "codes": codes,
                "summary": summary,
            }

            # Persist results
            crud.save_result(db, doc.id, results)

        except HTTPException:
            # propagate validation errors cleanly
            raise
        except Exception as e:
            # Document is saved, but pipeline failed
            raise HTTPException(
                status_code=500,
                detail=f"Document saved but pipeline failed: {str(e)}",
            )

    return {
        "document_id": doc.id,
        "processed": run_pipeline,
        "results": results,
    }


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """
    List most recent 50 documents.
    """
    docs = crud.list_documents(db, limit=50)
    return [
        {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "created_at": doc.created_at.isoformat(),
            "local_path": doc.local_path,
        }
        for doc in docs
    ]


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get document metadata and processing results (if any).
    """
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    results = crud.get_document_result(db, document_id)
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "created_at": doc.created_at.isoformat(),
        "local_path": doc.local_path,
        "results": results,
    }
