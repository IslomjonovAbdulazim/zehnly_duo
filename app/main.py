from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
import os
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

# Mount static files (except audio - handled separately)
app.mount("/logos", StaticFiles(directory=f"{settings.STORAGE_PATH}/logos"), name="logos")
app.mount("/images", StaticFiles(directory=f"{settings.STORAGE_PATH}/images"), name="images")

# Custom audio endpoint to bypass caching
@app.get("/{filename:path}")
async def serve_audio_no_cache(filename: str):
    """Serve audio files without caching"""
    if not filename.endswith('.mp3'):
        raise HTTPException(status_code=404, detail="File not found")
    
    audio_path = os.path.join(settings.STORAGE_PATH, "audio", filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
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