from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
app.mount("/audio", StaticFiles(directory=f"{settings.STORAGE_PATH}/audio"), name="audio")
app.mount("/images", StaticFiles(directory=f"{settings.STORAGE_PATH}/images"), name="images")

# Include routers
app.include_router(admin.router)
app.include_router(students.router)


@app.get("/")
async def root():
    return {"message": "Zehnly Duo API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}