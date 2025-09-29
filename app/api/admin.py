from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..database import get_db
from ..auth import verify_admin_token, login_admin, AdminLogin, AdminToken
from ..models.content import Course, Chapter, Lesson, CourseCreate, ChapterCreate, LessonCreate, CourseResponse, ChapterResponse, LessonResponse
from ..models.lesson_content import Word, Story, Subtitle, WordCreate, StoryCreate, WordResponse, StoryResponse
from ..services.storage import storage_service
from ..services.narakeet import narakeet_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=AdminToken)
async def admin_login(login_data: AdminLogin):
    return login_admin(login_data)


# Course CRUD
@router.post("/courses", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    return db.query(Course).all()


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for key, value in course_update.dict().items():
        setattr(course, key, value)
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}


# Chapter CRUD
@router.post("/chapters", response_model=ChapterResponse)
async def create_chapter(
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    db_chapter = Chapter(**chapter.dict())
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


@router.get("/courses/{course_id}/chapters", response_model=List[ChapterResponse])
async def get_course_chapters(
    course_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    return db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.order).all()


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_update: ChapterCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    for key, value in chapter_update.dict().items():
        setattr(chapter, key, value)
    
    db.commit()
    db.refresh(chapter)
    return chapter


@router.delete("/chapters/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    db.delete(chapter)
    db.commit()
    return {"message": "Chapter deleted successfully"}


# Lesson CRUD
@router.post("/lessons", response_model=LessonResponse)
async def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.get("/chapters/{chapter_id}/lessons", response_model=List[LessonResponse])
async def get_chapter_lessons(
    chapter_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    return db.query(Lesson).filter(Lesson.chapter_id == chapter_id).order_by(Lesson.order).all()


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_update: LessonCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    for key, value in lesson_update.dict().items():
        setattr(lesson, key, value)
    
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}


# Word CRUD
@router.post("/words", response_model=WordResponse)
async def create_word(
    word: WordCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    db_word = Word(**word.dict())
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


@router.get("/lessons/{lesson_id}/words", response_model=List[WordResponse])
async def get_lesson_words(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    return db.query(Word).filter(Word.lesson_id == lesson_id).all()


@router.put("/words/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: int,
    word_update: WordCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    for key, value in word_update.dict().items():
        setattr(word, key, value)
    
    db.commit()
    db.refresh(word)
    return word


@router.delete("/words/{word_id}")
async def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    db.delete(word)
    db.commit()
    return {"message": "Word deleted successfully"}


# Story CRUD
@router.post("/stories", response_model=StoryResponse)
async def create_story(
    story: StoryCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    db_story = Story(**story.dict())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


@router.get("/lessons/{lesson_id}/stories", response_model=List[StoryResponse])
async def get_lesson_stories(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    return db.query(Story).filter(Story.lesson_id == lesson_id).all()


@router.put("/stories/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int,
    story_update: StoryCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    for key, value in story_update.dict().items():
        setattr(story, key, value)
    
    db.commit()
    db.refresh(story)
    return story


@router.delete("/stories/{story_id}")
async def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}


# Audio Generation
@router.post("/words/{word_id}/generate-audio")
async def generate_word_audio(
    word_id: int,
    voice: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    logger = logging.getLogger(__name__)
    logger.info(f"🎯 Starting word audio generation for word_id: {word_id}")
    
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        logger.error(f"❌ Word not found: {word_id}")
        raise HTTPException(status_code=404, detail="Word not found")
    
    logger.info(f"📝 Found word: '{word.word}' (ID: {word_id})")
    logger.info(f"🎤 Voice parameter: {voice}")
    
    logger.info("🔄 Calling Narakeet service...")
    audio_data = await narakeet_service.generate_audio(word.word, voice)
    
    if not audio_data:
        logger.error("❌ Narakeet service returned no audio data")
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    
    logger.info(f"✅ Audio data received: {len(audio_data)} bytes")
    
    logger.info("💾 Saving audio file...")
    audio_url = await _save_audio_from_data(audio_data, f"word_{word_id}_audio.m4a", word_id)
    logger.info(f"📁 Audio saved to: {audio_url}")
    
    # Update word with audio URL
    word.audio_url = audio_url
    db.commit()
    logger.info("✅ Database updated with audio URL")
    
    return {"message": "Audio generated successfully", "audio_url": audio_url}


# File Upload
@router.post("/upload/logo/{course_id}")
async def upload_course_logo(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    logo_url = await storage_service.save_logo(file, course_id)
    course.logo_url = logo_url
    db.commit()
    
    return {"message": "Logo uploaded successfully", "logo_url": logo_url}


@router.post("/upload/audio/{word_id}")
async def upload_word_audio(
    word_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    audio_url = await storage_service.save_audio(file, word_id)
    word.audio_url = audio_url
    db.commit()
    
    return {"message": "Audio uploaded successfully", "audio_url": audio_url}


@router.post("/words/{word_id}/generate-example-audio")
async def generate_example_audio(
    word_id: int,
    voice: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    if not word.example_sentence:
        raise HTTPException(status_code=400, detail="Word has no example sentence")
    
    audio_data = await narakeet_service.generate_audio(word.example_sentence, voice)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    
    audio_url = await _save_audio_from_data(audio_data, f"word_{word_id}_example_audio.m4a", word_id)
    
    # Update word with example audio URL
    word.example_audio = audio_url
    db.commit()
    
    return {"message": "Example audio generated successfully", "audio_url": audio_url}


@router.post("/stories/{story_id}/generate-audio")
async def generate_story_audio(
    story_id: int,
    voice: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    audio_data = await narakeet_service.generate_audio(story.story_text, voice)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    
    audio_url = await _save_audio_from_data(audio_data, f"story_{story_id}_audio.m4a", story_id)
    
    # Update story with audio URL
    story.audio_url = audio_url
    db.commit()
    
    return {"message": "Story audio generated successfully", "audio_url": audio_url}


@router.post("/upload/example-audio/{word_id}")
async def upload_word_example_audio(
    word_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    audio_url = await storage_service.save_audio(file, word_id)
    word.example_audio = audio_url
    db.commit()
    
    return {"message": "Example audio uploaded successfully", "audio_url": audio_url}


@router.post("/upload/story-audio/{story_id}")
async def upload_story_audio(
    story_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    audio_url = await storage_service.save_audio(file, story_id)
    story.audio_url = audio_url
    db.commit()
    
    return {"message": "Story audio uploaded successfully", "audio_url": audio_url}


@router.post("/upload/image/{word_id}")
async def upload_word_image(
    word_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Use storage service for image (assuming it handles images too)
    image_url = await storage_service.save_logo(file, word_id)  # Reuse logo upload for images
    word.image_url = image_url
    db.commit()
    
    return {"message": "Image uploaded successfully", "image_url": image_url}


# Helper function for audio generation
async def _save_audio_from_data(audio_data: bytes, filename: str, entity_id: int) -> str:
    """Helper function to save audio data and return URL"""
    import tempfile
    import os
    
    logger = logging.getLogger(__name__)
    logger.info(f"💾 Saving audio data to file: {filename}")
    logger.info(f"📊 Audio data size: {len(audio_data)} bytes")
    logger.info(f"🆔 Entity ID: {entity_id}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
        logger.info(f"📁 Created temp file: {temp_file.name}")
        
        temp_file.write(audio_data)
        temp_file.flush()
        
        # Verify temp file was written correctly
        temp_file_size = os.path.getsize(temp_file.name)
        logger.info(f"✅ Temp file written: {temp_file_size} bytes")
        
        if temp_file_size == 0:
            logger.error("❌ Temp file is empty!")
            os.unlink(temp_file.name)
            raise HTTPException(status_code=500, detail="Generated audio file is empty")
        
        # Create UploadFile-like object
        class AudioFile:
            def __init__(self, file_path, filename):
                self.filename = filename
                self.file_path = file_path
                logger.info(f"📄 AudioFile created: {filename} -> {file_path}")
            
            async def read(self):
                logger.info(f"📖 Reading audio file: {self.file_path}")
                with open(self.file_path, 'rb') as f:
                    data = f.read()
                    logger.info(f"📖 Read {len(data)} bytes from temp file")
                    return data
        
        audio_file = AudioFile(temp_file.name, filename)
        logger.info("🔄 Calling storage service...")
        audio_url = await storage_service.save_audio(audio_file, entity_id)
        logger.info(f"✅ Storage service returned URL: {audio_url}")
        
        # Clean up temp file
        logger.info(f"🗑️ Cleaning up temp file: {temp_file.name}")
        os.unlink(temp_file.name)
        
        return audio_url