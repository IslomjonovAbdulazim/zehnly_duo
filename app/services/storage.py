import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException


class StorageService:
    def __init__(self):
        self.storage_path = Path(os.getenv("STORAGE_PATH", "/tmp/persistent_storage"))
        self._ensure_directories()
    
    def _ensure_directories(self):
        directories = ["logos", "audio", "images"]
        for directory in directories:
            (self.storage_path / directory).mkdir(parents=True, exist_ok=True)
    
    async def save_logo(self, file: UploadFile, course_id: int) -> str:
        return await self._save_file(file, "logos", f"course_{course_id}")
    
    async def save_audio(self, file: UploadFile, lesson_id: int) -> str:
        return await self._save_file(file, "audio", f"lesson_{lesson_id}")
    
    async def _save_file(self, file: UploadFile, subdirectory: str, prefix: str) -> str:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{prefix}_{uuid.uuid4()}{file_extension}"
        file_path = self.storage_path / subdirectory / filename
        
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            return f"{subdirectory}/{filename}"
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


storage_service = StorageService()