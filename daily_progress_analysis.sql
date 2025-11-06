-- Daily Lesson Progress Analysis
-- Shows lesson completion statistics by date

\echo '==========================================';
\echo 'DAILY LESSON PROGRESS ANALYSIS';
\echo '==========================================';

-- Total completed lessons
\echo '';
\echo '📊 OVERALL STATISTICS:';
SELECT 
    COUNT(*) as "Total Completed Lessons",
    COUNT(DISTINCT DATE(completed_at)) as "Active Days",
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT DATE(completed_at)), 1) as "Avg Lessons/Day"
FROM user_lesson_progress 
WHERE is_completed = true AND completed_at IS NOT NULL;

\echo '';
\echo '📅 LESSONS COMPLETED BY DATE (Last 30 Days):';
SELECT 
    DATE(ulp.completed_at) as "Date",
    TO_CHAR(DATE(ulp.completed_at), 'Day') as "Day of Week",
    COUNT(*) as "Lessons Completed",
    COUNT(DISTINCT ulp.user_id) as "Active Users",
    STRING_AGG(DISTINCT c.title, ', ') as "Courses"
FROM user_lesson_progress ulp
JOIN courses c ON ulp.course_id = c.id
WHERE ulp.is_completed = true 
    AND ulp.completed_at IS NOT NULL
    AND ulp.completed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(ulp.completed_at)
ORDER BY DATE(ulp.completed_at) DESC;

\echo '';
\echo '👥 TOP USERS BY LESSONS COMPLETED:';
SELECT 
    u.full_name as "User Name",
    COUNT(*) as "Lessons Completed",
    ROUND(AVG(ulp.score), 1) as "Avg Score",
    MAX(DATE(ulp.completed_at)) as "Last Activity"
FROM user_lesson_progress ulp
JOIN users u ON ulp.user_id = u.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY u.id, u.full_name
ORDER BY COUNT(*) DESC
LIMIT 10;

\echo '';
\echo '📚 LESSONS BY COURSE:';
SELECT 
    c.title as "Course",
    COUNT(*) as "Lessons Completed",
    COUNT(DISTINCT ulp.user_id) as "Active Users",
    ROUND(AVG(ulp.score), 1) as "Avg Score"
FROM user_lesson_progress ulp
JOIN courses c ON ulp.course_id = c.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY c.id, c.title
ORDER BY COUNT(*) DESC;

\echo '';
\echo '📝 LESSONS BY TYPE:';
SELECT 
    l.lesson_type as "Lesson Type",
    COUNT(*) as "Completed",
    ROUND(COUNT(*)::numeric * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage",
    ROUND(AVG(ulp.score), 1) as "Avg Score"
FROM user_lesson_progress ulp
JOIN lessons l ON ulp.lesson_id = l.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY l.lesson_type
ORDER BY COUNT(*) DESC;

\echo '';
\echo '🔥 RECENT ACTIVITY (Last 7 Days) - Daily Breakdown:';
SELECT 
    DATE(ulp.completed_at) as "Date",
    TO_CHAR(DATE(ulp.completed_at), 'Day') as "Day",
    COUNT(*) as "Lessons",
    COUNT(DISTINCT ulp.user_id) as "Users",
    ROUND(AVG(ulp.score), 1) as "Avg Score"
FROM user_lesson_progress ulp
WHERE ulp.is_completed = true 
    AND ulp.completed_at IS NOT NULL
    AND ulp.completed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(ulp.completed_at)
ORDER BY DATE(ulp.completed_at) DESC;

\echo '';
\echo '⏰ ACTIVITY BY HOUR OF DAY:';
SELECT 
    EXTRACT(HOUR FROM completed_at) as "Hour",
    COUNT(*) as "Lessons Completed",
    ROUND(COUNT(*)::numeric * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage"
FROM user_lesson_progress
WHERE is_completed = true AND completed_at IS NOT NULL
GROUP BY EXTRACT(HOUR FROM completed_at)
ORDER BY EXTRACT(HOUR FROM completed_at);

\echo '';
\echo '==========================================';
\echo 'Analysis Complete! ✅';
\echo '==========================================';