#!/usr/bin/env python3
"""
Course Analytics Script - Generate detailed user progress statistics for any course
Usage: python course_analytics.py [course_id]
"""

import sys
import os
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import func
from app.database import engine
from app.models.content import Course, Chapter, Lesson, LessonType
from app.models.lesson_content import Word
from app.models.user import User
from app.models.progress import UserCourseProgress, UserLessonProgress, UserWordProgress


def analyze_course_progress(course_id):
    """Generate comprehensive analytics for a specific course"""
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print(f"🔍 ANALYZING COURSE PROGRESS FOR COURSE ID: {course_id}")
        print("=" * 60)
        
        # Get course info
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            print(f"❌ Course with ID {course_id} not found!")
            return
        
        print(f"📚 COURSE: {course.title}")
        print(f"   Language Pair: {course.learning_language} ← {course.native_language}")
        
        # Get course structure
        chapters = db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.order).all()
        total_lessons = db.query(Lesson).join(Chapter).filter(Chapter.course_id == course_id).count()
        total_words = db.query(Word).join(Lesson).join(Chapter).filter(Chapter.course_id == course_id).count()
        
        print(f"   Structure: {len(chapters)} chapters, {total_lessons} lessons, {total_words} words")
        print()
        
        # Get all users who have progress in this course
        users_in_course = db.query(User).join(UserLessonProgress).join(Lesson).join(Chapter).filter(
            Chapter.course_id == course_id
        ).distinct().all()
        
        if not users_in_course:
            print("ℹ️  No users have started this course yet.")
            return
        
        print(f"👥 TOTAL USERS IN COURSE: {len(users_in_course)}")
        print("=" * 60)
        
        # Overall course statistics
        print("📊 OVERALL COURSE STATISTICS:")
        
        # Users by completion level
        completion_stats = defaultdict(int)
        lesson_completion_count = defaultdict(int)
        
        for user in users_in_course:
            # Get user's lesson progress
            completed_lessons = db.query(UserLessonProgress).join(Lesson).join(Chapter).filter(
                UserLessonProgress.user_id == user.id,
                UserLessonProgress.is_completed == True,
                Chapter.course_id == course_id
            ).count()
            
            completion_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
            
            if completion_percentage == 100:
                completion_stats["Completed (100%)"] += 1
            elif completion_percentage >= 75:
                completion_stats["Advanced (75-99%)"] += 1
            elif completion_percentage >= 50:
                completion_stats["Intermediate (50-74%)"] += 1
            elif completion_percentage >= 25:
                completion_stats["Beginner (25-49%)"] += 1
            elif completion_percentage > 0:
                completion_stats["Started (1-24%)"] += 1
            else:
                completion_stats["Not Started (0%)"] += 1
            
            lesson_completion_count[completed_lessons] += 1
        
        for level, count in completion_stats.items():
            percentage = (count / len(users_in_course)) * 100
            print(f"   {level}: {count} users ({percentage:.1f}%)")
        
        print()
        
        # Lesson completion statistics
        print("📈 LESSON COMPLETION BREAKDOWN:")
        lesson_stats = db.query(
            Lesson.id,
            Lesson.title,
            Lesson.lesson_type,
            Lesson.order.label('lesson_order'),
            Chapter.title.label('chapter_title'),
            Chapter.order.label('chapter_order'),
            func.count(UserLessonProgress.id).label('completed_count')
        ).join(Chapter).outerjoin(
            UserLessonProgress, 
            (UserLessonProgress.lesson_id == Lesson.id) & (UserLessonProgress.is_completed == True)
        ).filter(
            Chapter.course_id == course_id
        ).group_by(
            Lesson.id, Lesson.title, Lesson.lesson_type, Lesson.order, 
            Chapter.title, Chapter.order
        ).order_by(
            Chapter.order, Lesson.order
        ).all()
        
        current_chapter = None
        for lesson_stat in lesson_stats:
            if current_chapter != lesson_stat.chapter_title:
                current_chapter = lesson_stat.chapter_title
                print(f"\n   📖 {current_chapter}:")
            
            completion_rate = (lesson_stat.completed_count / len(users_in_course)) * 100
            lesson_type_icon = "📝" if lesson_stat.lesson_type == LessonType.WORD else "📖" if lesson_stat.lesson_type == LessonType.STORY else "📊"
            
            print(f"      {lesson_type_icon} {lesson_stat.title}")
            print(f"         Completed by: {lesson_stat.completed_count}/{len(users_in_course)} users ({completion_rate:.1f}%)")
        
        print()
        
        # User performance details
        print("👤 INDIVIDUAL USER PROGRESS:")
        
        user_details = []
        for user in users_in_course:
            # Get detailed progress
            user_progress = db.query(UserLessonProgress).join(Lesson).join(Chapter).filter(
                UserLessonProgress.user_id == user.id,
                Chapter.course_id == course_id
            ).all()
            
            completed_lessons = len([p for p in user_progress if p.is_completed])
            total_attempts = sum(p.attempts for p in user_progress)
            avg_score = sum(p.score for p in user_progress if p.score is not None) / len([p for p in user_progress if p.score is not None]) if any(p.score is not None for p in user_progress) else 0
            
            # Word progress
            learned_words = db.query(UserWordProgress).join(Word).join(Lesson).join(Chapter).filter(
                UserWordProgress.user_id == user.id,
                UserWordProgress.is_learned == True,
                Chapter.course_id == course_id
            ).count()
            
            user_details.append({
                'user': user,
                'completed_lessons': completed_lessons,
                'total_attempts': total_attempts,
                'avg_score': avg_score,
                'learned_words': learned_words,
                'completion_rate': (completed_lessons / total_lessons) * 100
            })
        
        # Sort by completion rate
        user_details.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        for i, user_detail in enumerate(user_details[:20], 1):  # Show top 20 users
            user = user_detail['user']
            print(f"   {i:2d}. {user.first_name} {user.last_name} (@{user.zehn_id})")
            print(f"       Lessons: {user_detail['completed_lessons']}/{total_lessons} ({user_detail['completion_rate']:.1f}%)")
            print(f"       Words Learned: {user_detail['learned_words']}/{total_words}")
            print(f"       Avg Score: {user_detail['avg_score']:.1f}%, Attempts: {user_detail['total_attempts']}")
            
            if user_detail['completion_rate'] == 100:
                print("       🎉 COURSE COMPLETED!")
            elif user_detail['completion_rate'] >= 75:
                print("       ⭐ ADVANCED LEARNER")
            elif user_detail['completion_rate'] >= 50:
                print("       📚 GOOD PROGRESS")
            elif user_detail['completion_rate'] >= 25:
                print("       🌱 GETTING STARTED")
            
            print()
        
        if len(user_details) > 20:
            print(f"   ... and {len(user_details) - 20} more users")
        
        # Summary statistics
        print("=" * 60)
        print("📋 SUMMARY STATISTICS:")
        
        total_completions = sum(1 for u in user_details if u['completion_rate'] == 100)
        avg_completion = sum(u['completion_rate'] for u in user_details) / len(user_details)
        avg_score = sum(u['avg_score'] for u in user_details) / len(user_details)
        total_lesson_completions = sum(u['completed_lessons'] for u in user_details)
        total_words_learned = sum(u['learned_words'] for u in user_details)
        
        print(f"   📊 Course Completion Rate: {(total_completions/len(users_in_course))*100:.1f}%")
        print(f"   📈 Average Progress: {avg_completion:.1f}%")
        print(f"   🎯 Average Score: {avg_score:.1f}%")
        print(f"   ✅ Total Lesson Completions: {total_lesson_completions}")
        print(f"   📖 Total Words Learned: {total_words_learned}")
        print(f"   👥 Active Learners: {len([u for u in user_details if u['completion_rate'] > 0])}")
        print(f"   🏆 Course Graduates: {total_completions}")
        
        # Most/least popular lessons
        popular_lessons = sorted(lesson_stats, key=lambda x: x.completed_count, reverse=True)
        if popular_lessons:
            print(f"\n   🔥 Most Popular Lesson: {popular_lessons[0].title} ({popular_lessons[0].completed_count} completions)")
            print(f"   📉 Least Popular Lesson: {popular_lessons[-1].title} ({popular_lessons[-1].completed_count} completions)")
        
    except Exception as e:
        print(f"❌ Error analyzing course progress: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def main():
    """Main function to run course analytics"""
    if len(sys.argv) > 1:
        try:
            course_id = int(sys.argv[1])
            analyze_course_progress(course_id)
        except ValueError:
            print("❌ Please provide a valid course ID (number)")
            print("Usage: python course_analytics.py [course_id]")
    else:
        print("📚 Available courses:")
        
        # Show available courses
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            courses = db.query(Course).all()
            if courses:
                for course in courses:
                    print(f"   ID {course.id}: {course.title}")
                print(f"\nUsage: python course_analytics.py [course_id]")
                print(f"Example: python course_analytics.py 12")
            else:
                print("   No courses found in database")
        finally:
            db.close()


if __name__ == "__main__":
    main()