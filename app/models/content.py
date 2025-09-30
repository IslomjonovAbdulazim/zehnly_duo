from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from enum import Enum as PyEnum
from ..database import Base


class LessonType(PyEnum):
    WORD = "word"
    STORY = "story"
    TEST = "test"


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    native_language = Column(String, nullable=False)
    learning_language = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    
    chapters = relationship("Chapter", back_populates="course")


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    order = Column(Integer, nullable=False)
    
    course = relationship("Course", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter")
    
    __table_args__ = (
        UniqueConstraint('course_id', 'order', name='unique_chapter_order'),
        Index('idx_course_order', 'course_id', 'order'),
    )


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), index=True)
    order = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    lesson_type = Column(Enum(LessonType), nullable=False, default=LessonType.WORD, index=True)
    word_lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True)
    
    chapter = relationship("Chapter", back_populates="lessons")
    words = relationship("Word", back_populates="lesson")
    stories = relationship("Story", back_populates="lesson")
    word_lesson = relationship("Lesson", remote_side=[id], backref="test_lessons")
    
    __table_args__ = (
        UniqueConstraint('chapter_id', 'order', name='unique_lesson_order'),
        Index('idx_chapter_order', 'chapter_id', 'order'),
    )



class CourseCreate(BaseModel):
    title: str
    native_language: str
    learning_language: str
    logo_url: Optional[str] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    logo_url: Optional[str] = None


class ChapterCreate(BaseModel):
    title: str
    course_id: int
    order: int


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None


class LessonCreate(BaseModel):
    title: str
    chapter_id: int
    order: int
    content: Optional[str] = None
    lesson_type: LessonType = LessonType.WORD
    word_lesson_id: Optional[int] = None


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    content: Optional[str] = None
    lesson_type: Optional[LessonType] = None
    word_lesson_id: Optional[int] = None


class CourseResponse(BaseModel):
    id: int
    title: str
    native_language: str
    learning_language: str
    logo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChapterResponse(BaseModel):
    id: int
    title: str
    course_id: int
    order: int
    
    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: int
    title: str
    chapter_id: int
    order: int
    content: Optional[str] = None
    lesson_type: LessonType
    word_lesson_id: Optional[int] = None
    
    class Config:
        from_attributes = True


