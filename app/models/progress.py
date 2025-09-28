from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, Index, UniqueConstraint, Enum, func, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum
from ..database import Base


class ProgressStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, index=True)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="course_progress")
    course = relationship("Course")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
        Index('idx_user_course_status', 'user_id', 'course_id', 'status'),
        CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='valid_progress_percentage'),
    )


class UserChapterProgress(Base):
    __tablename__ = "user_chapter_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="chapter_progress")
    chapter = relationship("Chapter")
    course = relationship("Course")


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    is_completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    attempts = Column(Integer, default=0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson")
    chapter = relationship("Chapter")
    course = relationship("Course")


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    is_learned = Column(Boolean, default=False, index=True)
    correct_answers = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_reviewed = Column(DateTime, server_default=func.now())
    last_5_results = Column(String, default="")
    
    user = relationship("User", back_populates="word_progress")
    word = relationship("Word")
    lesson = relationship("Lesson")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='unique_user_word'),
        Index('idx_user_lesson_learned', 'user_id', 'lesson_id', 'is_learned'),
    )


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