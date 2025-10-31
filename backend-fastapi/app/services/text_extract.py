from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import io
import base64


def extract_text_from_upload(file: UploadFile) -> str:
    """
    Extract text from uploaded file (PDF, TXT, or Image)

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
    elif file_ext in ["jpg", "jpeg", "png"]:
        return extract_text_from_image(file.file, file_ext)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Please upload PDF, TXT, JPG, or PNG files."
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


def extract_text_from_image(file_data: io.BytesIO, file_ext: str) -> str:
    """
    Extract medical findings from image using Claude Vision API

    Args:
        file_data: Image file data
        file_ext: File extension (jpg, jpeg, png)

    Returns:
        str: Extracted medical findings text
    """
    from app.services.anthropic_client import client

    try:
        # Read image data
        image_bytes = file_data.read()

        # Convert to base64
        image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        # Determine media type
        media_type = f"image/{file_ext if file_ext != 'jpg' else 'jpeg'}"

        # Use Claude Vision API to analyze the image
        findings_text = client.analyze_medical_image(image_base64, media_type)

        return findings_text

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from image: {str(e)}"
        )
