from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models.user import User, UserResponse
from ..models.content import Course, Chapter, Lesson, CourseResponse
from ..models.lesson_content import Word, Story, Subtitle
from ..models.progress import UserCourseProgress, UserLessonProgress, UserWordProgress, QuestionResult, QuizResultRequest
from ..services.user_service import get_or_create_user

router = APIRouter(prefix="/students", tags=["Students"])


class UserRequest(BaseModel):
    zehn_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class CourseWithContent(BaseModel):
    id: int
    title: str
    native_language: str
    learning_language: str
    logo_url: Optional[str] = None
    chapters: List[dict]  # Will contain nested chapters with lessons and words
    
    class Config:
        from_attributes = True


def get_user_from_headers(
    zehn_id: str = Header(..., alias="X-User-ID"),
    first_name: str = Header(..., alias="X-First-Name"),
    last_name: str = Header(..., alias="X-Last-Name"),
    phone_number: Optional[str] = Header(None, alias="X-Phone-Number"),
    db: Session = Depends(get_db)
) -> User:
    """Auto-register or get existing user from headers"""
    return get_or_create_user(db, zehn_id, first_name, last_name, phone_number)


@router.get("/profile", response_model=UserResponse)
async def get_profile(user: User = Depends(get_user_from_headers)):
    """Get current user profile"""
    return user


@router.get("/courses")
async def get_available_courses(
    db: Session = Depends(get_db),
    user: User = Depends(get_user_from_headers)
):
    """Get all available courses with user progress"""
    courses = db.query(Course).all()
    
    result = []
    for course in courses:
        # Get user's course progress
        course_progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user.id,
            UserCourseProgress.course_id == course.id
        ).first()
        
        progress_percentage = course_progress.progress_percentage if course_progress else 0.0
        
        result.append({
            "id": course.id,
            "title": course.title,
            "native_language": course.native_language,
            "learning_language": course.learning_language,
            "logo_url": course.logo_url,
            "progress_percentage": progress_percentage
        })
    
    return result


@router.get("/courses/{course_id}")
async def get_course_structure(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_from_headers)
):
    """Get course with chapters and lessons with progress percentages"""
    course = db.query(Course).options(
        joinedload(Course.chapters).options(
            joinedload(Chapter.lessons)
        )
    ).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get all user progress for this course
    lesson_progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == user.id,
        UserLessonProgress.course_id == course_id
    ).all()
    
    # Create lookup for lesson progress
    lesson_progress_map = {lp.lesson_id: lp for lp in lesson_progress}
    
    # Build structure with progress
    course_data = {
        "id": course.id,
        "title": course.title,
        "native_language": course.native_language,
        "learning_language": course.learning_language,
        "logo_url": course.logo_url,
        "chapters": []
    }
    
    for chapter in sorted(course.chapters, key=lambda x: x.order):
        chapter_lessons = []
        completed_lessons = 0
        
        for lesson in sorted(chapter.lessons, key=lambda x: x.order):
            progress = lesson_progress_map.get(lesson.id)
            is_completed = progress.is_completed if progress else False
            
            if is_completed:
                completed_lessons += 1
                
            lesson_data = {
                "id": lesson.id,
                "title": lesson.title,
                "order": lesson.order,
                "lesson_type": lesson.lesson_type.value,
                "is_completed": is_completed,
                "progress_percentage": 100.0 if is_completed else 0.0
            }
            chapter_lessons.append(lesson_data)
        
        # Calculate chapter progress
        total_lessons = len(chapter_lessons)
        chapter_progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0.0
        
        chapter_data = {
            "id": chapter.id,
            "title": chapter.title,
            "order": chapter.order,
            "progress_percentage": chapter_progress,
            "lessons": chapter_lessons
        }
        
        course_data["chapters"].append(chapter_data)
    
    return course_data





@router.get("/lessons/{lesson_id}/content")
async def get_lesson_content(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_from_headers)
):
    """Get lesson content with words and progress"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    words = db.query(Word).filter(Word.lesson_id == lesson_id).all()
    stories = db.query(Story).options(joinedload(Story.subtitles)).filter(Story.lesson_id == lesson_id).all()
    
    # Get word progress for this user
    word_progress = db.query(UserWordProgress).filter(
        UserWordProgress.user_id == user.id,
        UserWordProgress.lesson_id == lesson_id
    ).all()
    
    # Create word progress lookup
    word_progress_map = {wp.word_id: wp for wp in word_progress}
    
    return {
        "lesson": {
            "id": lesson.id,
            "title": lesson.title,
            "lesson_type": lesson.lesson_type.value,
            "content": lesson.content
        },
        "words": [
            {
                "id": word.id,
                "word": word.word,
                "translation": word.translation,
                "audio_url": word.audio_url,
                "image_url": word.image_url,
                "example_sentence": word.example_sentence,
                "example_audio": word.example_audio,
                "progress": {
                    "is_learned": word_progress_map[word.id].is_learned if word.id in word_progress_map else False,
                    "last_5_results": word_progress_map[word.id].last_5_results if word.id in word_progress_map else ""
                }
            }
            for word in words
        ],
        "stories": [
            {
                "id": story.id,
                "story_text": story.story_text,
                "audio_url": story.audio_url,
                "word_lesson_id": story.word_lesson_id,
                "subtitles": [
                    {
                        "id": subtitle.id,
                        "text": subtitle.text,
                        "start_audio": subtitle.start_audio,
                        "end_audio": subtitle.end_audio,
                        "start_position": subtitle.start_position,
                        "end_position": subtitle.end_position
                    }
                    for subtitle in story.subtitles
                ]
            }
            for story in stories
        ]
    }




@router.post("/quiz/complete")
async def complete_quiz(
    quiz_result: QuizResultRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_from_headers)
):
    """Complete quiz and update all progress"""
    # Calculate score percentage
    score_percentage = (quiz_result.correct_answers / quiz_result.total_questions) * 100
    
    # Get lesson for course/chapter info
    lesson = db.query(Lesson).filter(Lesson.id == quiz_result.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Update lesson progress
    lesson_progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == user.id,
        UserLessonProgress.lesson_id == quiz_result.lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = UserLessonProgress(
            user_id=user.id,
            lesson_id=quiz_result.lesson_id,
            course_id=lesson.chapter.course_id
        )
        db.add(lesson_progress)
    
    # Mark lesson as completed if score is good (e.g., >= 70%)
    if score_percentage >= 70:
        lesson_progress.is_completed = True
        if not lesson_progress.completed_at:
            lesson_progress.completed_at = datetime.utcnow()
    
    lesson_progress.score = score_percentage
    lesson_progress.attempts = (lesson_progress.attempts or 0) + 1
    
    # Update course progress
    course_progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user.id,
        UserCourseProgress.course_id == lesson.chapter.course_id
    ).first()
    
    if not course_progress:
        course_progress = UserCourseProgress(
            user_id=user.id,
            course_id=lesson.chapter.course_id
        )
        db.add(course_progress)
    
    # Calculate overall course progress
    total_lessons = db.query(Lesson).join(Chapter).filter(
        Chapter.course_id == lesson.chapter.course_id
    ).count()
    
    completed_lessons = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == user.id,
        UserLessonProgress.course_id == lesson.chapter.course_id,
        UserLessonProgress.is_completed == True
    ).count()
    
    course_progress.progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    # Update individual word progress from question results
    words_updated = 0
    for question_result in quiz_result.question_results:
        if question_result.word_id:  # Only for word-based questions
            # Get or create word progress
            word_progress = db.query(UserWordProgress).filter(
                UserWordProgress.user_id == user.id,
                UserWordProgress.word_id == question_result.word_id
            ).first()
            
            if not word_progress:
                word_progress = UserWordProgress(
                    user_id=user.id,
                    word_id=question_result.word_id,
                    lesson_id=quiz_result.lesson_id
                )
                db.add(word_progress)
            
            # Update word stats - no individual counters needed, just track results
            
            # Update last 5 results (1 = correct, 0 = wrong)
            result = "1" if question_result.is_correct else "0"
            last_results = word_progress.last_5_results or ""
            last_results = result + last_results[:4]  # Add new result, keep last 4
            word_progress.last_5_results = last_results
            
            # Simple learning logic: learned if last 3 attempts were correct
            if len(last_results) >= 3 and last_results[:3] == "111":
                word_progress.is_learned = True
            
            words_updated += 1
    
    db.commit()
    
    return {
        "lesson_id": quiz_result.lesson_id,
        "score_percentage": score_percentage,
        "correct_answers": quiz_result.correct_answers,
        "total_questions": quiz_result.total_questions,
        "time_spent": quiz_result.time_spent,
        "lesson_completed": score_percentage >= 70,
        "course_progress": course_progress.progress_percentage,
        "words_updated": words_updated,
        "message": "Quiz completed successfully"
    }