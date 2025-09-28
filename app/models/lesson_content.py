from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()


class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    example_sentence = Column(Text, nullable=True)
    example_audio = Column(String, nullable=True)


class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    audio_url = Column(String, nullable=True)
    story_text = Column(Text, nullable=False)
    
    subtitles = relationship("Subtitle", back_populates="story")


class Subtitle(Base):
    __tablename__ = "subtitles"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    text = Column(String, nullable=False)
    start_audio = Column(Float, nullable=False)
    end_audio = Column(Float, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    
    story = relationship("Story", back_populates="subtitles")


class WordCreate(BaseModel):
    lesson_id: int
    word: str
    translation: str
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