from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class QuizType(str, Enum):
    CHOOSE_CORRECT_IMAGE = "CHOOSE_CORRECT_IMAGE"
    CHOOSE_CORRECT_WORD = "CHOOSE_CORRECT_WORD"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_IN_THE_BLANK = "FILL_IN_THE_BLANK"
    ARRANGE_SENTENCE_CORRECTLY = "ARRANGE_SENTENCE_CORRECTLY"
    AUDIO = "AUDIO"


class ImageOption(BaseModel):
    image_url: str
    name: str

class ChooseCorrectImageQuiz(BaseModel):
    type: QuizType = QuizType.CHOOSE_CORRECT_IMAGE
    audio_url: str
    options: List[ImageOption]

class ChooseCorrectWordQuiz(BaseModel):
    type: QuizType = QuizType.CHOOSE_CORRECT_WORD
    question: str
    options: List[str]

class TrueFalseQuiz(BaseModel):
    type: QuizType = QuizType.TRUE_FALSE
    question: str
    fact: str


class FillInTheBlankQuiz(BaseModel):
    type: QuizType = QuizType.FILL_IN_THE_BLANK
    question: str
    options: List[str]


class ArrangeSentenceQuiz(BaseModel):
    type: QuizType = QuizType.ARRANGE_SENTENCE_CORRECTLY
    options: List[str]


class AudioQuiz(BaseModel):
    type: QuizType = QuizType.AUDIO
    text_options: List[str]
    audio_url: str
    start_audio: float
    end_audio: float


class QuizRequest(BaseModel):
    lesson_id: int
    quiz_type: QuizType


class QuizResponse(BaseModel):
    quiz_id: str
    quiz_data: dict