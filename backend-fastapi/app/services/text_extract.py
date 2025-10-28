from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import io


def extract_text_from_upload(file: UploadFile) -> str:
    """
    Extract text from uploaded file (PDF or TXT)
    
    Args:
        file: Uploaded file
        
    Returns:
        str: Extracted text content
        
    Raises:
        HTTPException: If file type is not supported
    """
    filename = file.filename or ""
    file_ext = filename.lower().split(".")[-1] if "." in filename else ""
    
    if file_ext == "pdf":
        return extract_text_from_pdf(file.file)
    elif file_ext == "txt":
        return extract_text_from_txt(file.file)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Please upload PDF or TXT files."
        )


def extract_text_from_pdf(file_data: io.BytesIO) -> str:
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_data)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


def extract_text_from_txt(file_data: io.BytesIO) -> str:
    """Extract text from TXT file"""
    try:
        content = file_data.read()
        return content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Failed to decode text file. Please ensure the file is UTF-8 encoded."
        )
