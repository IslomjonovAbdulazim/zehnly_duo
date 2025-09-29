from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
import os
import logging
from .api import admin, students
from .config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://xojar.uz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/logos", StaticFiles(directory=f"{settings.STORAGE_PATH}/logos"), name="logos")
app.mount("/images", StaticFiles(directory=f"{settings.STORAGE_PATH}/images"), name="images")

# Custom audio endpoint to bypass caching
@app.get("/audio/{filename}")
async def serve_audio_no_cache(filename: str):
    """Serve audio files without caching"""
    logger = logging.getLogger(__name__)
    logger.info(f"Audio request for: {filename}")
    
    audio_path = os.path.join(settings.STORAGE_PATH, "audio", filename)
    logger.info(f"Looking for audio at: {audio_path}")
    logger.info(f"File exists: {os.path.exists(audio_path)}")
    
    if os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size == 0:
            logger.warning(f"Audio file is empty: {filename}")
            raise HTTPException(status_code=404, detail="Audio file is empty")
    else:
        logger.error(f"Audio file not found: {audio_path}")
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Determine media type based on file extension
    if filename.endswith('.m4a'):
        media_type = "audio/mp4"
    elif filename.endswith('.mp3'):
        media_type = "audio/mpeg"
    else:
        media_type = "audio/mpeg"  # default
    
    logger.info(f"Serving with media type: {media_type}")
    
    return FileResponse(
        audio_path,
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# Serve audio files from root (for existing URLs like /lesson_1_xxx.mp3)
@app.get("/{filename}")
async def serve_root_audio_no_cache(filename: str):
    """Serve audio files from root path without caching"""
    logger = logging.getLogger(__name__)
    logger.info(f"Root audio request for: {filename}")
    
    if not (filename.endswith('.mp3') or filename.endswith('.m4a')):
        logger.info(f"Not an audio file: {filename}")
        raise HTTPException(status_code=404, detail="Not found")
    
    audio_path = os.path.join(settings.STORAGE_PATH, "audio", filename)
    logger.info(f"Looking for root audio at: {audio_path}")
    logger.info(f"File exists: {os.path.exists(audio_path)}")
    
    if os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        logger.info(f"Root audio file size: {file_size} bytes")
        
        if file_size == 0:
            logger.warning(f"Root audio file is empty: {filename}")
            raise HTTPException(status_code=404, detail="Audio file is empty")
    else:
        logger.error(f"Root audio file not found: {audio_path}")
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Determine media type based on file extension
    if filename.endswith('.m4a'):
        media_type = "audio/mp4"
    elif filename.endswith('.mp3'):
        media_type = "audio/mpeg"
    else:
        media_type = "audio/mpeg"  # default
    
    logger.info(f"Serving root audio with media type: {media_type}")
    
    return FileResponse(
        audio_path,
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# Include routers
app.include_router(admin.router)
app.include_router(students.router)


@app.get("/")
async def root():
    return {"message": "Zehnly Duo API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}