from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


class ProgressStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    status = Column(String, default=ProgressStatus.NOT_STARTED.value)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)


class UserChapterProgress(Base):
    __tablename__ = "user_chapter_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    status = Column(String, default=ProgressStatus.NOT_STARTED.value)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    is_completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    attempts = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("words.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    is_learned = Column(Boolean, default=False)
    correct_answers = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_reviewed = Column(DateTime, default=datetime.utcnow)
    last_5_results = Column(String, default="")


class ProgressCreate(BaseModel):
    user_id: int
    course_id: int


class LessonProgressUpdate(BaseModel):
    user_id: int
    lesson_id: int
    is_completed: bool
    score: Optional[float] = None


class WordProgressUpdate(BaseModel):
    user_id: int
    word_id: int
    is_correct: bool


class CourseProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed: datetime
    
    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    chapter_id: int
    course_id: int
    is_completed: bool
    score: Optional[float] = None
    attempts: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WordProgressResponse(BaseModel):
    id: int
    user_id: int
    word_id: int
    lesson_id: int
    is_learned: bool
    correct_answers: int
    total_attempts: int
    last_reviewed: datetime
    last_5_results: str
    
    class Config:
        from_attributes = True