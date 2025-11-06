#!/usr/bin/env python3
"""
Daily Lesson Progress Analysis
Analyzes user lesson completion statistics by date
"""

import psycopg2
import os
from datetime import datetime, date
from collections import defaultdict, Counter
from urllib.parse import urlparse


def get_db_connection():
    """Get database connection from environment variables"""
    # Try to load from .env file first
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    except:
        database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        parsed = urlparse(database_url)
        return psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]
        )
    return None


def analyze_daily_progress():
    """Analyze lesson completion statistics by date"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Could not connect to database!")
            return
            
        cursor = conn.cursor()
        
        print("📊 DAILY LESSON PROGRESS ANALYSIS")
        print("=" * 60)
        
        # Query all completed lessons with dates
        query = """
        SELECT 
            ulp.completed_at,
            ulp.user_id,
            ulp.lesson_id,
            ulp.course_id,
            ulp.score,
            u.full_name,
            c.title as course_title,
            l.title as lesson_title,
            l.lesson_type
        FROM user_lesson_progress ulp
        JOIN users u ON ulp.user_id = u.id
        JOIN courses c ON ulp.course_id = c.id
        JOIN lessons l ON ulp.lesson_id = l.id
        WHERE ulp.is_completed = true 
        AND ulp.completed_at IS NOT NULL
        ORDER BY ulp.completed_at DESC;
        """
        
        cursor.execute(query)
        completed_lessons = cursor.fetchall()
        
        if not completed_lessons:
            print("❌ No completed lessons found!")
            return
        
        print(f"📈 Found {len(completed_lessons)} completed lessons")
        print()
        
        # Group by date
        daily_stats = defaultdict(list)
        user_daily_stats = defaultdict(lambda: defaultdict(int))
        course_daily_stats = defaultdict(lambda: defaultdict(int))
        lesson_type_daily_stats = defaultdict(lambda: defaultdict(int))
        
        for lesson in completed_lessons:
            completed_at, user_id, lesson_id, course_id, score, full_name, course_title, lesson_title, lesson_type = lesson
            
            if completed_at:
                completion_date = completed_at.date()
                lesson_data = {
                    'completed_at': completed_at,
                    'user_id': user_id,
                    'lesson_id': lesson_id,
                    'course_id': course_id,
                    'score': score,
                    'full_name': full_name,
                    'course_title': course_title,
                    'lesson_title': lesson_title,
                    'lesson_type': lesson_type
                }
                
                daily_stats[completion_date].append(lesson_data)
                user_daily_stats[completion_date][full_name] += 1
                course_daily_stats[completion_date][course_title] += 1
                lesson_type_daily_stats[completion_date][lesson_type] += 1
        
        # Sort dates
        sorted_dates = sorted(daily_stats.keys(), reverse=True)
        
        print("📅 DAILY BREAKDOWN (Most Recent First)")
        print("=" * 60)
        
        total_lessons_all_time = 0
        
        for completion_date in sorted_dates:
            lessons_on_date = daily_stats[completion_date]
            daily_count = len(lessons_on_date)
            total_lessons_all_time += daily_count
            
            print(f"\n🗓️  {completion_date.strftime('%A, %B %d, %Y')}")
            print(f"   📚 Total Lessons Completed: {daily_count}")
            
            # User breakdown
            user_counts = user_daily_stats[completion_date]
            if user_counts:
                print(f"   👥 By User:")
                for user_name, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"      • {user_name}: {count} lessons")
            
            # Course breakdown
            course_counts = course_daily_stats[completion_date]
            if course_counts:
                print(f"   📖 By Course:")
                for course_name, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"      • {course_name}: {count} lessons")
            
            # Lesson type breakdown
            type_counts = lesson_type_daily_stats[completion_date]
            if type_counts:
                print(f"   📝 By Lesson Type:")
                for lesson_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"      • {lesson_type.title()}: {count} lessons")
            
            # Show individual lessons if less than 10
            if daily_count <= 10:
                print(f"   📋 Individual Lessons:")
                for lesson in lessons_on_date:
                    score_text = f" (Score: {lesson['score']:.1f}%)" if lesson['score'] else ""
                    time_text = lesson['completed_at'].strftime('%H:%M')
                    print(f"      • {time_text} - {lesson['full_name']}: {lesson['lesson_title']}{score_text}")
            
            print("   " + "-" * 50)
        
        # Overall statistics
        print("\n📊 OVERALL STATISTICS")
        print("=" * 60)
        print(f"🎯 Total Lessons Completed: {total_lessons_all_time}")
        print(f"📅 Active Days: {len(sorted_dates)}")
        print(f"📈 Average Lessons per Day: {total_lessons_all_time / len(sorted_dates):.1f}")
        
        # Most active users
        all_user_counts = Counter()
        for date_users in user_daily_stats.values():
            for user, count in date_users.items():
                all_user_counts[user] += count
        
        print(f"\n🏆 TOP USERS (All Time):")
        for user, count in all_user_counts.most_common(10):
            print(f"   • {user}: {count} lessons")
        
        # Most popular courses
        all_course_counts = Counter()
        for date_courses in course_daily_stats.values():
            for course, count in date_courses.items():
                all_course_counts[course] += count
        
        print(f"\n📚 MOST POPULAR COURSES:")
        for course, count in all_course_counts.most_common():
            print(f"   • {course}: {count} lessons")
        
        # Lesson type distribution
        all_type_counts = Counter()
        for date_types in lesson_type_daily_stats.values():
            for lesson_type, count in date_types.items():
                all_type_counts[lesson_type] += count
        
        print(f"\n📝 LESSON TYPE DISTRIBUTION:")
        for lesson_type, count in all_type_counts.most_common():
            percentage = (count / total_lessons_all_time) * 100
            print(f"   • {lesson_type.title()}: {count} lessons ({percentage:.1f}%)")
        
        # Recent activity (last 7 days)
        recent_dates = [d for d in sorted_dates[:7]]
        if recent_dates:
            recent_total = sum(len(daily_stats[d]) for d in recent_dates)
            print(f"\n🔥 RECENT ACTIVITY (Last 7 Days):")
            print(f"   📚 Total Lessons: {recent_total}")
            print(f"   📈 Average per Day: {recent_total / len(recent_dates):.1f}")
            
            # Most active recent users
            recent_user_counts = Counter()
            for d in recent_dates:
                for user, count in user_daily_stats[d].items():
                    recent_user_counts[user] += count
            
            if recent_user_counts:
                print(f"   🏆 Most Active Users:")
                for user, count in recent_user_counts.most_common(5):
                    print(f"      • {user}: {count} lessons")
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    analyze_daily_progress()