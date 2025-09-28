from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import admin, students
from .config import settings

# TODO: REMOVE IN PRODUCTION - This drops and recreates all tables on startup
# This is only for development. In production, use proper migrations.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://xojar.uz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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