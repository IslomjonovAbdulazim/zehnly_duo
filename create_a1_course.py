#!/usr/bin/env python3
"""
Script to create A1 English-Uzbek course from JSON data
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.content import Course, Chapter, Lesson, LessonType
from app.models.lesson_content import Word, Story


def load_course_from_json():
    """Load the A1 English-Uzbek course from JSON file"""
    
    # Read JSON file
    with open('english_uzbek_a1_course.json', 'r', encoding='utf-8') as f:
        course_data = json.load(f)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 CREATING A1 ENGLISH-UZBEK COURSE...")
        print("=" * 50)
        
        # Create course
        course_info = course_data['course']
        course = Course(
            title=course_info['title'],
            native_language=course_info['native_language'],
            learning_language=course_info['learning_language']
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        print(f"✅ Created course: {course.title} (ID: {course.id})")
        
        # Create chapters and lessons
        for chapter_data in course_data['chapters']:
            print(f"\n📖 Creating Chapter {chapter_data['order']}: {chapter_data['title']}")
            
            # Create chapter
            chapter = Chapter(
                title=chapter_data['title'],
                course_id=course.id,
                order=chapter_data['order']
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)
            print(f"   ✅ Chapter created (ID: {chapter.id})")
            
            # Create lessons
            for lesson_data in chapter_data['lessons']:
                print(f"   📝 Creating Lesson {lesson_data['order']}: {lesson_data['title']}")
                
                # Determine lesson type
                lesson_type = LessonType.WORD if lesson_data['type'] == 'word' else \
                             LessonType.STORY if lesson_data['type'] == 'story' else \
                             LessonType.TEST
                
                # Create lesson
                lesson = Lesson(
                    title=lesson_data['title'],
                    chapter_id=chapter.id,
                    order=lesson_data['order'],
                    content=lesson_data['content'],
                    lesson_type=lesson_type
                )
                
                # For test lessons, link to word lesson
                if lesson_type == LessonType.TEST:
                    # Find the word lesson (should be 3 lessons back)
                    word_lesson = db.query(Lesson).filter(
                        Lesson.chapter_id == chapter.id,
                        Lesson.order == lesson_data['order'] - 2,
                        Lesson.lesson_type == LessonType.WORD
                    ).first()
                    if word_lesson:
                        lesson.word_lesson_id = word_lesson.id
                
                db.add(lesson)
                db.commit()
                db.refresh(lesson)
                print(f"      ✅ Lesson created (ID: {lesson.id}, Type: {lesson_type.value})")
                
                # Add words for word lessons
                if lesson_type == LessonType.WORD and 'words' in lesson_data:
                    print(f"      📚 Adding {len(lesson_data['words'])} words...")
                    for word_data in lesson_data['words']:
                        word = Word(
                            lesson_id=lesson.id,
                            word=word_data['word'],
                            translation=word_data['translation'],
                            example_sentence=word_data['example']
                        )
                        db.add(word)
                    db.commit()
                    print(f"      ✅ Added {len(lesson_data['words'])} words")
                
                # Add story for story lessons
                if lesson_type == LessonType.STORY and 'story' in lesson_data:
                    print(f"      📖 Adding story...")
                    story_data = lesson_data['story']
                    
                    # Find the related word lesson (should be 1 lesson back)
                    word_lesson = db.query(Lesson).filter(
                        Lesson.chapter_id == chapter.id,
                        Lesson.order == lesson_data['order'] - 1,
                        Lesson.lesson_type == LessonType.WORD
                    ).first()
                    
                    story = Story(
                        lesson_id=lesson.id,
                        story_text=story_data['text'],
                        word_lesson_id=word_lesson.id if word_lesson else None
                    )
                    db.add(story)
                    db.commit()
                    print(f"      ✅ Added story: {story_data['title']}")
        
        print("\n" + "=" * 50)
        print("🎉 COURSE CREATION COMPLETE!")
        
        # Summary
        total_chapters = len(course_data['chapters'])
        total_lessons = sum(len(ch['lessons']) for ch in course_data['chapters'])
        total_words = sum(len(lesson['words']) for ch in course_data['chapters'] 
                         for lesson in ch['lessons'] if 'words' in lesson)
        total_stories = sum(1 for ch in course_data['chapters'] 
                           for lesson in ch['lessons'] if 'story' in lesson)
        
        print(f"\n📊 COURSE SUMMARY:")
        print(f"   Course: {course.title}")
        print(f"   Chapters: {total_chapters}")
        print(f"   Lessons: {total_lessons}")
        print(f"   Words: {total_words}")
        print(f"   Stories: {total_stories}")
        print(f"   Language Pair: {course.learning_language} ← {course.native_language}")
        
        print(f"\n🔮 FUTURE CHAPTERS PLANNED:")
        future_chapters = course_data['future_chapters_plan']
        for chapter_key, chapter_info in future_chapters.items():
            chapter_num = chapter_key.split('_')[1]
            print(f"   Chapter {chapter_num}: {chapter_info['title']}")
            topics = ', '.join(chapter_info['topics'])
            print(f"      Topics: {topics}")
        
    except Exception as e:
        print(f"❌ Error creating course: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    load_course_from_json()