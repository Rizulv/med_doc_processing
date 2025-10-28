from sqlalchemy.orm import Session
from app.db.models import Document, DocumentResult
from typing import List, Optional
import json


def create_document(db: Session, filename: str, local_path: Optional[str] = None) -> Document:
    """Create a new document record"""
    doc = Document(original_filename=filename, local_path=local_path)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session, limit: int = 50) -> List[Document]:
    """List recent documents"""
    return db.query(Document).order_by(Document.created_at.desc()).limit(limit).all()


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """Get a document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def save_result(db: Session, document_id: int, payload: dict) -> DocumentResult:
    """Save pipeline result for a document"""
    result = DocumentResult(
        document_id=document_id,
        payload_json=json.dumps(payload)
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_document_result(db: Session, document_id: int) -> Optional[dict]:
    """Get result for a document"""
    result = db.query(DocumentResult).filter(DocumentResult.document_id == document_id).first()
    if result:
        return json.loads(result.payload_json)
    return None
