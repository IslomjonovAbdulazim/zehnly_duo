from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    zehn_id = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    
    # Relationships
    course_progress = relationship("UserCourseProgress", back_populates="user")
    chapter_progress = relationship("UserChapterProgress", back_populates="user")
    lesson_progress = relationship("UserLessonProgress", back_populates="user")
    word_progress = relationship("UserWordProgress", back_populates="user")


class UserCreate(BaseModel):
    zehn_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    zehn_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    
    class Config:
        from_attributes = True