from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..database import Base


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    progress_percentage = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="course_progress")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
    )


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    is_completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="lesson_progress")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),
    )


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    is_learned = Column(Boolean, default=False)
    correct_answers = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_5_results = Column(String(5), default="")  # Only 5 chars max
    
    user = relationship("User", back_populates="word_progress")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='unique_user_word'),
    )


# Pydantic Models
class QuestionResult(BaseModel):
    word_id: Optional[int] = None
    story_id: Optional[int] = None  
    is_correct: bool


class QuizResultRequest(BaseModel):
    lesson_id: int
    total_questions: int
    correct_answers: int
    time_spent: int
    question_results: list[QuestionResult]


class LessonProgressResponse(BaseModel):
    lesson_id: int
    is_completed: bool
    score: Optional[float] = None
    attempts: int
    
    class Config:
        from_attributes = True


class WordProgressResponse(BaseModel):
    word_id: int
    is_learned: bool
    correct_answers: int
    total_attempts: int
    last_5_results: str
    
    class Config:
        from_attributes = True


class StudentStatsResponse(BaseModel):
    user_id: int
    full_name: str
    phone_number: Optional[str] = None
    lessons_completed: int


class CourseStatsOverview(BaseModel):
    course_id: int
    course_title: str
    total_students: int


class CourseStatsResponse(BaseModel):
    courses: list[CourseStatsOverview]


class CourseDetailStats(BaseModel):
    id: int
    title: str


class CourseDetailStatsResponse(BaseModel):
    course_info: CourseDetailStats
    total_students: int
    students: list[StudentStatsResponse]