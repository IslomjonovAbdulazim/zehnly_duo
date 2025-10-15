#!/usr/bin/env python3
"""
Script to fetch and display current courses with their content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker, joinedload
from app.database import engine
from app.models.content import Course, Chapter, Lesson
from app.models.lesson_content import Word, Story


def fetch_and_display_courses():
    """Fetch all courses and their content, display in chat format"""
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🎓 FETCHING ALL COURSES AND CONTENT...")
        print("=" * 50)
        
        # Fetch all courses with their relationships
        courses = db.query(Course).options(
            joinedload(Course.chapters).joinedload(Chapter.lessons)
        ).all()
        
        if not courses:
            print("❌ No courses found in database")
            return
        
        for course in courses:
            print(f"\n📚 COURSE: {course.title}")
            print(f"   ID: {course.id}")
            print(f"   Native Language: {course.native_language}")
            print(f"   Learning Language: {course.learning_language}")
            if course.logo_url:
                print(f"   Logo: {course.logo_url}")
            print(f"   Chapters: {len(course.chapters)}")
            
            # Display chapters
            for chapter in sorted(course.chapters, key=lambda x: x.order):
                print(f"\n   📖 CHAPTER {chapter.order}: {chapter.title}")
                print(f"      ID: {chapter.id}")
                print(f"      Lessons: {len(chapter.lessons)}")
                
                # Display lessons
                for lesson in sorted(chapter.lessons, key=lambda x: x.order):
                    print(f"\n      📝 LESSON {lesson.order}: {lesson.title}")
                    print(f"         ID: {lesson.id}")
                    print(f"         Type: {lesson.lesson_type.value}")
                    if lesson.content:
                        print(f"         Content: {lesson.content[:100]}...")
                    if lesson.word_lesson_id:
                        print(f"         Word Lesson ID: {lesson.word_lesson_id}")
                    
                    # Fetch and display words for this lesson
                    words = db.query(Word).filter(Word.lesson_id == lesson.id).all()
                    if words:
                        print(f"         💡 WORDS ({len(words)}):")
                        for word in words:
                            print(f"            • {word.word} → {word.translation}")
                            if word.example_sentence:
                                print(f"              Example: {word.example_sentence}")
                            if word.audio_url:
                                print(f"              Audio: {word.audio_url}")
                            if word.image_url:
                                print(f"              Image: {word.image_url}")
                    
                    # Fetch and display stories for this lesson
                    stories = db.query(Story).filter(Story.lesson_id == lesson.id).all()
                    if stories:
                        print(f"         📖 STORIES ({len(stories)}):")
                        for story in stories:
                            print(f"            Story ID: {story.id}")
                            print(f"            Text: {story.story_text[:200]}...")
                            if story.audio_url:
                                print(f"            Audio: {story.audio_url}")
                            if story.word_lesson_id:
                                print(f"            Related Word Lesson: {story.word_lesson_id}")
                            
                            # Count subtitles
                            subtitle_count = len(story.subtitles) if hasattr(story, 'subtitles') else 0
                            if subtitle_count > 0:
                                print(f"            Subtitles: {subtitle_count}")
        
        print("\n" + "=" * 50)
        print("✅ COURSE FETCH COMPLETE!")
        
        # Summary
        total_chapters = sum(len(course.chapters) for course in courses)
        total_lessons = sum(len(chapter.lessons) for course in courses for chapter in course.chapters)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Courses: {len(courses)}")
        print(f"   Total Chapters: {total_chapters}")
        print(f"   Total Lessons: {total_lessons}")
        
    except Exception as e:
        print(f"❌ Error fetching courses: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_display_courses()