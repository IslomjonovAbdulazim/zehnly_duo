import os
import uuid
import logging
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
        logger = logging.getLogger(__name__)
        logger.info(f"🔊 Starting audio save for lesson_id: {lesson_id}")
        logger.info(f"📄 File name: {file.filename}")
        return await self._save_file(file, "audio", f"lesson_{lesson_id}")
    
    async def _save_file(self, file: UploadFile, subdirectory: str, prefix: str) -> str:
        logger = logging.getLogger(__name__)
        logger.info(f"💾 _save_file called: subdirectory={subdirectory}, prefix={prefix}")
        
        if not file.filename:
            logger.error("❌ No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")
        
        logger.info(f"📄 Original filename: {file.filename}")
        
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{prefix}_{uuid.uuid4()}{file_extension}"
        file_path = self.storage_path / subdirectory / filename
        
        logger.info(f"📁 Generated filename: {filename}")
        logger.info(f"🗂️ Full file path: {file_path}")
        logger.info(f"📂 Storage path exists: {self.storage_path.exists()}")
        logger.info(f"📁 Subdirectory exists: {(self.storage_path / subdirectory).exists()}")
        
        try:
            logger.info("📖 Reading file content...")
            content = await file.read()
            logger.info(f"📊 File content size: {len(content)} bytes")
            
            if len(content) == 0:
                logger.error("❌ File content is empty!")
                raise HTTPException(status_code=400, detail="File content is empty")
            
            logger.info(f"💾 Writing to: {file_path}")
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Verify file was written
            saved_size = file_path.stat().st_size
            logger.info(f"✅ File saved successfully: {saved_size} bytes")
            
            if saved_size == 0:
                logger.error("❌ Saved file is empty!")
                file_path.unlink()
                raise HTTPException(status_code=500, detail="Saved file is empty")
            
            relative_path = f"{subdirectory}/{filename}"
            logger.info(f"🔗 Returning relative path: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"💥 Error saving file: {e}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            if file_path.exists():
                logger.info("🗑️ Cleaning up failed file")
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


storage_service = StorageService()