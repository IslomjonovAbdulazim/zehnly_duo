from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LessonBreakdown(BaseModel):
    word: int
    story: int
    test: int


class DailyData(BaseModel):
    date: str
    day_of_week: str
    dau: int
    lessons_completed: int
    lessons_per_user: float
    lesson_breakdown: LessonBreakdown
    performance_rating: str


class HourlyPattern(BaseModel):
    hour: int
    time: str
    lessons: int
    unique_users: int
    percentage_of_daily: float
    lessons_per_user: float
    weekend_lessons: int
    weekday_lessons: int
    activity_level: str


class CourseAnalytics(BaseModel):
    course_id: int
    course_name: str
    total_users: int
    total_lessons: int
    market_share_users: float
    market_share_lessons: float
    status: str


class UserSegment(BaseModel):
    segment: str
    lesson_range: str
    user_count: int
    percentage: float
    avg_lessons: float
    behavior: str


class LearningZone(BaseModel):
    zone: str
    time_range: str
    total_lessons: int
    percentage: float
    description: str


class TopPerformanceDay(BaseModel):
    rank: int
    date: str
    day: str
    dau: int
    lessons: int
    efficiency: float
    achievement: str


class KPIs(BaseModel):
    user_retention_rate: float
    power_users_percentage: float
    avg_lessons_per_active_user: float
    course_completion_balance: float
    peak_hour_concentration: float


class Recommendation(BaseModel):
    priority: str
    category: str
    title: str
    description: str


class DataPeriod(BaseModel):
    start_date: str
    end_date: str
    total_days: int


class Summary(BaseModel):
    total_lessons_completed: int
    average_daily_lessons: float
    peak_daily_activity: int
    peak_date: str
    active_learning_days: int
    total_users: int
    daily_active_users_avg: int


class CacheInfo(BaseModel):
    is_cached: bool
    cache_hit: bool
    generation_time_ms: int
    data_freshness: str


class AnalyticsResponse(BaseModel):
    generated_at: datetime
    cache_expires_at: datetime
    data_period: DataPeriod
    summary: Summary
    daily_data: List[DailyData]
    hourly_patterns: List[HourlyPattern]
    courses: List[CourseAnalytics]
    user_segmentation: List[UserSegment]
    learning_zones: List[LearningZone]
    top_performance_days: List[TopPerformanceDay]
    kpis: KPIs
    recommendations: List[Recommendation]
    cache_info: CacheInfo