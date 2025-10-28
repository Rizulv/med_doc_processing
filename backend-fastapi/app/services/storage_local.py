import os
import uuid
from pathlib import Path
from typing import BinaryIO


class LocalStorage:
    """Local file storage for uploaded documents"""
    
    def __init__(self, base_path: str = "app/local_storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_data: BinaryIO, filename: str) -> str:
        """
        Save file to local storage
        
        Args:
            file_data: File content
            filename: Original filename
            
        Returns:
            str: Path to saved file
        """
        # Create unique directory for this file
        file_id = str(uuid.uuid4())
        file_dir = self.base_path / file_id
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = file_dir / filename
        with open(file_path, "wb") as f:
            content = file_data.read()
            f.write(content)
        
        return str(file_path)
    
    def get_file_path(self, local_path: str) -> Path:
        """Get full path to a stored file"""
        return Path(local_path)
    
    def file_exists(self, local_path: str) -> bool:
        """Check if file exists"""
        return Path(local_path).exists()


storage = LocalStorage()
