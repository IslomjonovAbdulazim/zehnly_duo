-- Comprehensive Analytics: Users, DAU, Registrations, and Lesson Completion
-- Enhanced analysis for Zehnly Duo platform

\echo '==========================================';
\echo 'COMPREHENSIVE PLATFORM ANALYTICS';
\echo '==========================================';

-- 1. DAILY USER REGISTRATIONS
\echo '';
\echo '📝 DAILY USER REGISTRATIONS (Last 30 Days):';
SELECT 
    DATE(created_at) as "Registration Date",
    TO_CHAR(DATE(created_at), 'Day') as "Day of Week",
    COUNT(*) as "New Users",
    SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as "Cumulative Users"
FROM users
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- 2. TOTAL USER GROWTH
\echo '';
\echo '👥 USER GROWTH OVERVIEW:';
SELECT 
    COUNT(*) as "Total Users",
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as "New Users (7d)",
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as "New Users (30d)",
    MIN(DATE(created_at)) as "First Registration",
    MAX(DATE(created_at)) as "Latest Registration"
FROM users;

-- 3. DAILY ACTIVE USERS (DAU) - Based on lesson completion
\echo '';
\echo '📈 DAILY ACTIVE USERS (DAU) - Last 30 Days:';
SELECT 
    DATE(ulp.completed_at) as "Date",
    TO_CHAR(DATE(ulp.completed_at), 'Day') as "Day",
    COUNT(DISTINCT ulp.user_id) as "DAU",
    COUNT(*) as "Total Lessons",
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT ulp.user_id), 1) as "Lessons per User"
FROM user_lesson_progress ulp
WHERE ulp.is_completed = true 
    AND ulp.completed_at IS NOT NULL
    AND ulp.completed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(ulp.completed_at)
ORDER BY DATE(ulp.completed_at) DESC;

-- 4. USER ACTIVITY PATTERNS
\echo '';
\echo '🎯 USER ACTIVITY PATTERNS:';
SELECT 
    CASE 
        WHEN lesson_count >= 100 THEN 'Super Active (100+)'
        WHEN lesson_count >= 50 THEN 'Very Active (50-99)'
        WHEN lesson_count >= 20 THEN 'Active (20-49)'
        WHEN lesson_count >= 5 THEN 'Moderate (5-19)'
        ELSE 'Light (1-4)'
    END as "User Type",
    COUNT(*) as "User Count",
    ROUND(COUNT(*)::numeric * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage",
    ROUND(AVG(lesson_count), 1) as "Avg Lessons per User"
FROM (
    SELECT 
        user_id,
        COUNT(*) as lesson_count
    FROM user_lesson_progress
    WHERE is_completed = true
    GROUP BY user_id
) user_stats
GROUP BY 
    CASE 
        WHEN lesson_count >= 100 THEN 'Super Active (100+)'
        WHEN lesson_count >= 50 THEN 'Very Active (50-99)'
        WHEN lesson_count >= 20 THEN 'Active (20-49)'
        WHEN lesson_count >= 5 THEN 'Moderate (5-19)'
        ELSE 'Light (1-4)'
    END
ORDER BY MIN(lesson_count) DESC;

-- 5. RETENTION ANALYSIS
\echo '';
\echo '🔄 USER RETENTION ANALYSIS:';
SELECT 
    'Day 1' as "Period",
    COUNT(DISTINCT CASE WHEN first_lesson.completed_at >= first_lesson.user_created_at 
                            AND first_lesson.completed_at < first_lesson.user_created_at + INTERVAL '1 day' 
                        THEN first_lesson.user_id END) as "Active Users",
    ROUND(COUNT(DISTINCT CASE WHEN first_lesson.completed_at >= first_lesson.user_created_at 
                                   AND first_lesson.completed_at < first_lesson.user_created_at + INTERVAL '1 day' 
                               THEN first_lesson.user_id END)::numeric * 100.0 / 
          COUNT(DISTINCT first_lesson.user_id), 1) as "Retention %"
FROM (
    SELECT 
        u.id as user_id,
        u.created_at as user_created_at,
        ulp.completed_at,
        ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY ulp.completed_at) as lesson_rank
    FROM users u
    LEFT JOIN user_lesson_progress ulp ON u.id = ulp.user_id AND ulp.is_completed = true
    WHERE u.created_at >= CURRENT_DATE - INTERVAL '30 days'
) first_lesson
WHERE lesson_rank = 1 OR lesson_rank IS NULL;

-- 6. COURSE ADOPTION BY USERS
\echo '';
\echo '📚 COURSE ADOPTION BY USERS:';
SELECT 
    c.title as "Course",
    COUNT(DISTINCT ulp.user_id) as "Unique Users",
    COUNT(*) as "Total Lessons",
    ROUND(AVG(ulp.score), 1) as "Avg Score",
    MIN(DATE(ulp.completed_at)) as "First Completion",
    MAX(DATE(ulp.completed_at)) as "Latest Activity"
FROM user_lesson_progress ulp
JOIN courses c ON ulp.course_id = c.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY c.id, c.title
ORDER BY COUNT(DISTINCT ulp.user_id) DESC;

-- 7. LESSON COMPLETION BY TYPE
\echo '';
\echo '📝 LESSON COMPLETION BY TYPE:';
SELECT 
    l.lesson_type as "Lesson Type",
    COUNT(*) as "Completions",
    COUNT(DISTINCT ulp.user_id) as "Unique Users",
    ROUND(COUNT(*)::numeric * 100.0 / SUM(COUNT(*)) OVER (), 1) as "% of Total",
    ROUND(AVG(ulp.score), 1) as "Avg Score"
FROM user_lesson_progress ulp
JOIN lessons l ON ulp.lesson_id = l.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY l.lesson_type
ORDER BY COUNT(*) DESC;

-- 8. TOP PERFORMING USERS
\echo '';
\echo '🏆 TOP PERFORMING USERS:';
SELECT 
    u.id as "User ID",
    COALESCE(u.full_name, 'User #' || u.id) as "User Name",
    COUNT(*) as "Lessons Completed",
    ROUND(AVG(ulp.score), 1) as "Avg Score",
    COUNT(DISTINCT ulp.course_id) as "Courses",
    MIN(DATE(ulp.completed_at)) as "First Lesson",
    MAX(DATE(ulp.completed_at)) as "Latest Activity",
    DATE(u.created_at) as "Registered"
FROM user_lesson_progress ulp
JOIN users u ON ulp.user_id = u.id
WHERE ulp.is_completed = true AND ulp.completed_at IS NOT NULL
GROUP BY u.id, u.full_name, u.created_at
ORDER BY COUNT(*) DESC
LIMIT 20;

-- 9. WEEKLY SUMMARY
\echo '';
\echo '📊 WEEKLY ACTIVITY SUMMARY:';
SELECT 
    DATE_TRUNC('week', ulp.completed_at)::date as "Week Starting",
    COUNT(DISTINCT ulp.user_id) as "Weekly Active Users",
    COUNT(*) as "Total Lessons",
    COUNT(DISTINCT DATE(ulp.completed_at)) as "Active Days",
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT ulp.user_id), 1) as "Lessons per User",
    ROUND(AVG(ulp.score), 1) as "Avg Score"
FROM user_lesson_progress ulp
WHERE ulp.is_completed = true 
    AND ulp.completed_at IS NOT NULL
    AND ulp.completed_at >= CURRENT_DATE - INTERVAL '8 weeks'
GROUP BY DATE_TRUNC('week', ulp.completed_at)
ORDER BY DATE_TRUNC('week', ulp.completed_at) DESC;

\echo '';
\echo '==========================================';
\echo 'Comprehensive Analysis Complete! ✅';
\echo '==========================================';