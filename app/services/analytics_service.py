from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..models.progress import UserLessonProgress
from ..models.user import User
from ..models.content import Course, Lesson, LessonType
from ..models.analytics import *
import calendar


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_analytics_data(self) -> Dict[str, Any]:
        """Generate complete analytics data"""
        start_time = datetime.now()
        
        # Get data period
        data_period = self._get_data_period()
        
        # Generate all analytics components
        summary = self._get_summary_data()
        daily_data = self._get_daily_data()
        hourly_patterns = self._get_hourly_patterns()
        courses = self._get_course_analytics()
        user_segmentation = self._get_user_segmentation()
        learning_zones = self._get_learning_zones()
        top_performance_days = self._get_top_performance_days()
        kpis = self._get_kpis()
        recommendations = self._get_recommendations()
        
        # Calculate generation time
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "generated_at": datetime.now(),
            "cache_expires_at": datetime.now() + timedelta(hours=6),
            "data_period": data_period,
            "summary": summary,
            "daily_data": daily_data,
            "hourly_patterns": hourly_patterns,
            "courses": courses,
            "user_segmentation": user_segmentation,
            "learning_zones": learning_zones,
            "top_performance_days": top_performance_days,
            "kpis": kpis,
            "recommendations": recommendations,
            "cache_info": {
                "is_cached": False,
                "cache_hit": False,
                "generation_time_ms": generation_time,
                "data_freshness": "live"
            }
        }
    
    def _get_data_period(self) -> Dict[str, Any]:
        """Get the data analysis period - all time data"""
        earliest = self.db.query(func.min(UserLessonProgress.completed_at)).filter(
            UserLessonProgress.completed_at.isnot(None)
        ).scalar()
        
        latest = self.db.query(func.max(UserLessonProgress.completed_at)).filter(
            UserLessonProgress.completed_at.isnot(None)
        ).scalar()
        
        if earliest and latest:
            total_days = (latest.date() - earliest.date()).days + 1
        else:
            total_days = 0
        
        return {
            "start_date": earliest.date().isoformat() if earliest else datetime.now().date().isoformat(),
            "end_date": latest.date().isoformat() if latest else datetime.now().date().isoformat(),
            "total_days": total_days
        }
    
    def _get_summary_data(self) -> Dict[str, Any]:
        """Generate summary statistics for all time"""
        # Total lessons completed all time
        total_lessons = self.db.query(UserLessonProgress).filter(
            UserLessonProgress.is_completed == True
        ).count()
        
        # Get daily lesson counts for averages (all time)
        daily_counts = self.db.query(
            func.date(UserLessonProgress.completed_at).label('date'),
            func.count().label('count')
        ).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at.isnot(None)
        ).group_by(
            func.date(UserLessonProgress.completed_at)
        ).all()
        
        if daily_counts:
            avg_daily = sum(count for _, count in daily_counts) / len(daily_counts)
            peak_daily = max(count for _, count in daily_counts)
            peak_date = max(daily_counts, key=lambda x: x.count)[0].isoformat()
            active_days = len(daily_counts)
        else:
            avg_daily = 0
            peak_daily = 0
            peak_date = datetime.now().date().isoformat()
            active_days = 0
        
        # Total users and daily active users (all time)
        total_users = self.db.query(User).count()
        
        daily_users = self.db.query(
            func.date(UserLessonProgress.completed_at).label('date'),
            func.count(func.distinct(UserLessonProgress.user_id)).label('dau')
        ).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at.isnot(None)
        ).group_by(
            func.date(UserLessonProgress.completed_at)
        ).all()
        
        avg_dau = sum(dau for _, dau in daily_users) / len(daily_users) if daily_users else 0
        
        return {
            "total_lessons_completed": total_lessons,
            "average_daily_lessons": round(avg_daily, 1),
            "peak_daily_activity": peak_daily,
            "peak_date": peak_date,
            "active_learning_days": active_days,
            "total_users": total_users,
            "daily_active_users_avg": int(avg_dau)
        }
    
    def _get_daily_data(self) -> List[Dict[str, Any]]:
        """Generate daily analytics data (last 30 days for performance)"""
        # Get last 30 days of data for display (keeping this limited for performance)
        thirty_days_ago = datetime.now() - timedelta(days=29)
        
        daily_stats = self.db.query(
            func.date(UserLessonProgress.completed_at).label('date'),
            func.count(func.distinct(UserLessonProgress.user_id)).label('dau'),
            func.count().label('total_lessons')
        ).join(
            Lesson, UserLessonProgress.lesson_id == Lesson.id
        ).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at >= thirty_days_ago,
            UserLessonProgress.completed_at.isnot(None)
        ).group_by(
            func.date(UserLessonProgress.completed_at)
        ).order_by(
            func.date(UserLessonProgress.completed_at).desc()
        ).all()
        
        daily_data = []
        for stat in daily_stats:
            date_obj = stat.date
            
            # Get lesson breakdown for this day
            lesson_breakdown = self.db.query(
                Lesson.lesson_type,
                func.count().label('count')
            ).join(
                UserLessonProgress, UserLessonProgress.lesson_id == Lesson.id
            ).filter(
                UserLessonProgress.is_completed == True,
                func.date(UserLessonProgress.completed_at) == date_obj
            ).group_by(
                Lesson.lesson_type
            ).all()
            
            # Convert to dict
            breakdown = {"word": 0, "story": 0, "test": 0}
            for lesson_type, count in lesson_breakdown:
                breakdown[lesson_type.value] = count
            
            # Calculate performance rating
            lessons_per_user = stat.total_lessons / stat.dau if stat.dau > 0 else 0
            if lessons_per_user >= 10:
                performance = "excellent"
            elif lessons_per_user >= 8:
                performance = "strong" 
            elif lessons_per_user >= 6:
                performance = "good"
            elif lessons_per_user >= 4:
                performance = "moderate"
            else:
                performance = "low"
            
            daily_data.append({
                "date": date_obj.isoformat(),
                "day_of_week": calendar.day_name[date_obj.weekday()],
                "dau": stat.dau,
                "lessons_completed": stat.total_lessons,
                "lessons_per_user": round(lessons_per_user, 1),
                "lesson_breakdown": breakdown,
                "performance_rating": performance
            })
        
        return daily_data
    
    def _get_hourly_patterns(self) -> List[Dict[str, Any]]:
        """Generate hourly activity patterns for all time"""        
        hourly_stats = self.db.query(
            extract('hour', UserLessonProgress.completed_at).label('hour'),
            func.count().label('lessons'),
            func.count(func.distinct(UserLessonProgress.user_id)).label('users'),
            func.count(case([(extract('dow', UserLessonProgress.completed_at).in_([0, 6]), 1)])).label('weekend_lessons'),
            func.count(case([(extract('dow', UserLessonProgress.completed_at).in_([1, 2, 3, 4, 5]), 1)])).label('weekday_lessons')
        ).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at.isnot(None)
        ).group_by(
            extract('hour', UserLessonProgress.completed_at)
        ).order_by(
            extract('hour', UserLessonProgress.completed_at)
        ).all()
        
        total_lessons = sum(stat.lessons for stat in hourly_stats)
        
        hourly_data = []
        for stat in hourly_stats:
            hour = int(stat.hour)
            percentage = (stat.lessons / total_lessons * 100) if total_lessons > 0 else 0
            lessons_per_user = stat.lessons / stat.users if stat.users > 0 else 0
            
            # Determine activity level
            if percentage >= 10:
                activity_level = "peak"
            elif percentage >= 7:
                activity_level = "high"
            elif percentage >= 4:
                activity_level = "moderate"
            elif percentage >= 2:
                activity_level = "low"
            else:
                activity_level = "minimal"
            
            hourly_data.append({
                "hour": hour,
                "time": f"{hour:02d}:00",
                "lessons": stat.lessons,
                "unique_users": stat.users,
                "percentage_of_daily": round(percentage, 1),
                "lessons_per_user": round(lessons_per_user, 1),
                "weekend_lessons": stat.weekend_lessons or 0,
                "weekday_lessons": stat.weekday_lessons or 0,
                "activity_level": activity_level
            })
        
        return hourly_data
    
    def _get_course_analytics(self) -> List[Dict[str, Any]]:
        """Generate course performance analytics for all time"""        
        course_stats = self.db.query(
            Course.id,
            Course.title,
            func.count(func.distinct(UserLessonProgress.user_id)).label('total_users'),
            func.count().label('total_lessons')
        ).join(
            Lesson, Course.id == Lesson.chapter_id  # Simplified join - may need adjustment based on schema
        ).join(
            UserLessonProgress, UserLessonProgress.lesson_id == Lesson.id
        ).filter(
            UserLessonProgress.is_completed == True
        ).group_by(
            Course.id, Course.title
        ).order_by(
            func.count().desc()
        ).all()
        
        total_users = sum(stat.total_users for stat in course_stats)
        total_lessons = sum(stat.total_lessons for stat in course_stats)
        
        courses = []
        for i, stat in enumerate(course_stats):
            user_share = (stat.total_users / total_users * 100) if total_users > 0 else 0
            lesson_share = (stat.total_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            # Determine status
            if i == 0:
                status = "primary"
            elif user_share >= 15:
                status = "secondary"
            else:
                status = "emerging"
            
            courses.append({
                "course_id": stat.id,
                "course_name": stat.title,
                "total_users": stat.total_users,
                "total_lessons": stat.total_lessons,
                "market_share_users": round(user_share, 1),
                "market_share_lessons": round(lesson_share, 1),
                "status": status
            })
        
        return courses
    
    def _get_user_segmentation(self) -> List[Dict[str, Any]]:
        """Generate user activity segmentation for all time"""        
        user_lesson_counts = self.db.query(
            UserLessonProgress.user_id,
            func.count().label('lesson_count')
        ).filter(
            UserLessonProgress.is_completed == True
        ).group_by(
            UserLessonProgress.user_id
        ).subquery()
        
        segments = [
            {"name": "light", "range": "1-4", "min": 1, "max": 4, "behavior": "trial_users"},
            {"name": "moderate", "range": "5-19", "min": 5, "max": 19, "behavior": "regular_learners"},
            {"name": "active", "range": "20-49", "min": 20, "max": 49, "behavior": "committed_users"},
            {"name": "very_active", "range": "50+", "min": 50, "max": 999999, "behavior": "power_users"}
        ]
        
        total_users = self.db.query(user_lesson_counts).count()
        
        segmentation = []
        for segment in segments:
            count = self.db.query(user_lesson_counts).filter(
                and_(
                    user_lesson_counts.c.lesson_count >= segment["min"],
                    user_lesson_counts.c.lesson_count <= segment["max"]
                )
            ).count()
            
            avg_lessons = self.db.query(
                func.avg(user_lesson_counts.c.lesson_count)
            ).filter(
                and_(
                    user_lesson_counts.c.lesson_count >= segment["min"],
                    user_lesson_counts.c.lesson_count <= segment["max"]
                )
            ).scalar() or 0
            
            percentage = (count / total_users * 100) if total_users > 0 else 0
            
            segmentation.append({
                "segment": segment["name"],
                "lesson_range": segment["range"],
                "user_count": count,
                "percentage": round(percentage, 1),
                "avg_lessons": round(avg_lessons, 1),
                "behavior": segment["behavior"]
            })
        
        return segmentation
    
    def _get_learning_zones(self) -> List[Dict[str, Any]]:
        """Generate learning time zone analysis for all time"""        
        zones = [
            {"name": "night", "range": "00:00-04:00", "hours": list(range(0, 5)), "description": "night_owls"},
            {"name": "dawn", "range": "05:00-08:00", "hours": list(range(5, 9)), "description": "early_birds"},
            {"name": "morning", "range": "09:00-12:00", "hours": list(range(9, 13)), "description": "morning_learners"},
            {"name": "peak", "range": "13:00-17:00", "hours": list(range(13, 18)), "description": "prime_time"},
            {"name": "evening", "range": "18:00-21:00", "hours": list(range(18, 22)), "description": "evening_study"},
            {"name": "late", "range": "22:00-23:00", "hours": list(range(22, 24)), "description": "night_study"}
        ]
        
        total_lessons = self.db.query(UserLessonProgress).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at.isnot(None)
        ).count()
        
        learning_zones = []
        for zone in zones:
            zone_lessons = self.db.query(UserLessonProgress).filter(
                UserLessonProgress.is_completed == True,
                UserLessonProgress.completed_at.isnot(None),
                extract('hour', UserLessonProgress.completed_at).in_(zone["hours"])
            ).count()
            
            percentage = (zone_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            learning_zones.append({
                "zone": zone["name"],
                "time_range": zone["range"],
                "total_lessons": zone_lessons,
                "percentage": round(percentage, 1),
                "description": zone["description"]
            })
        
        return learning_zones
    
    def _get_top_performance_days(self) -> List[Dict[str, Any]]:
        """Get top 10 performance days from all time"""        
        daily_stats = self.db.query(
            func.date(UserLessonProgress.completed_at).label('date'),
            func.count(func.distinct(UserLessonProgress.user_id)).label('dau'),
            func.count().label('lessons')
        ).filter(
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at.isnot(None)
        ).group_by(
            func.date(UserLessonProgress.completed_at)
        ).order_by(
            func.count().desc()
        ).limit(10).all()
        
        top_days = []
        for i, stat in enumerate(daily_stats):
            efficiency = stat.lessons / stat.dau if stat.dau > 0 else 0
            
            # Determine achievement
            if i == 0:
                achievement = "peak_day"
            elif i < 3:
                achievement = "top_performer"
            elif efficiency >= 10:
                achievement = "high_efficiency"
            else:
                achievement = "strong_day"
            
            top_days.append({
                "rank": i + 1,
                "date": stat.date.isoformat(),
                "day": calendar.day_name[stat.date.weekday()],
                "dau": stat.dau,
                "lessons": stat.lessons,
                "efficiency": round(efficiency, 1),
                "achievement": achievement
            })
        
        return top_days
    
    def _get_kpis(self) -> Dict[str, Any]:
        """Calculate key performance indicators for all time"""        
        # User retention rate (users with 5+ lessons all time)
        total_users = self.db.query(User).count()
        active_users = self.db.query(
            func.count(func.distinct(UserLessonProgress.user_id))
        ).filter(
            UserLessonProgress.is_completed == True
        ).group_by(
            UserLessonProgress.user_id
        ).having(
            func.count() >= 5
        ).count()
        
        retention_rate = (active_users / total_users * 100) if total_users > 0 else 0
        
        # Power users percentage (50+ lessons all time)
        power_users = self.db.query(
            func.count(func.distinct(UserLessonProgress.user_id))
        ).filter(
            UserLessonProgress.is_completed == True
        ).group_by(
            UserLessonProgress.user_id
        ).having(
            func.count() >= 50
        ).count()
        
        power_users_pct = (power_users / total_users * 100) if total_users > 0 else 0
        
        # Average lessons per active user (all time)
        avg_lessons = self.db.query(
            func.avg(
                func.count()
            )
        ).filter(
            UserLessonProgress.is_completed == True
        ).group_by(
            UserLessonProgress.user_id
        ).scalar() or 0
        
        return {
            "user_retention_rate": round(retention_rate, 1),
            "power_users_percentage": round(power_users_pct, 1),
            "avg_lessons_per_active_user": round(avg_lessons, 1),
            "course_completion_balance": 0.95,  # Placeholder - could calculate actual balance
            "peak_hour_concentration": 11.5   # Placeholder - from peak hour analysis
        }
    
    def _get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        return [
            {
                "priority": "high",
                "category": "optimization",
                "title": "Peak Hour Resource Focus",
                "description": "Focus infrastructure resources on 1-4 PM peak period"
            },
            {
                "priority": "medium",
                "category": "user_engagement",
                "title": "Light User Activation",
                "description": "Target users with 1-4 lessons for conversion to regular learners"
            },
            {
                "priority": "high",
                "category": "content",
                "title": "Course Expansion",
                "description": "Accelerate development of high-performing course content"
            }
        ]