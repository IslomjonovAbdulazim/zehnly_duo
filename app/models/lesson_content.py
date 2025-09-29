from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from ..database import Base


class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    example_sentence = Column(Text, nullable=True)
    example_audio = Column(String, nullable=True)
    
    lesson = relationship("Lesson", back_populates="words")
    
    __table_args__ = (
        UniqueConstraint('lesson_id', 'word', name='unique_lesson_word'),
    )


class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    audio_url = Column(String, nullable=True)
    story_text = Column(Text, nullable=False)
    
    lesson = relationship("Lesson", back_populates="stories")
    subtitles = relationship("Subtitle", back_populates="story")


class Subtitle(Base):
    __tablename__ = "subtitles"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), index=True)
    text = Column(String, nullable=False)
    start_audio = Column(Float, nullable=False)
    end_audio = Column(Float, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    
    story = relationship("Story", back_populates="subtitles")
    
    __table_args__ = (
        CheckConstraint('start_audio < end_audio', name='valid_audio_timing'),
        CheckConstraint('start_position < end_position', name='valid_text_position'),
    )


class WordCreate(BaseModel):
    lesson_id: int
    word: str
    translation: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    example_sentence: Optional[str] = None
    example_audio: Optional[str] = None


class WordUpdate(BaseModel):
    word: Optional[str] = None
    translation: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    example_sentence: Optional[str] = None
    example_audio: Optional[str] = None


class StoryCreate(BaseModel):
    lesson_id: int
    audio_url: Optional[str] = None
    story_text: str


class SubtitleCreate(BaseModel):
    story_id: int
    text: str
    start_audio: float
    end_audio: float
    start_position: int
    end_position: int


class WordResponse(BaseModel):
    id: int
    lesson_id: int
    word: str
    translation: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    example_sentence: Optional[str] = None
    example_audio: Optional[str] = None
    
    class Config:
        from_attributes = True


class SubtitleResponse(BaseModel):
    id: int
    story_id: int
    text: str
    start_audio: float
    end_audio: float
    start_position: int
    end_position: int
    
    class Config:
        from_attributes = True


class StoryResponse(BaseModel):
    id: int
    lesson_id: int
    audio_url: Optional[str] = None
    story_text: str
    subtitles: List[SubtitleResponse] = []
    
    class Config:
        from_attributes = True