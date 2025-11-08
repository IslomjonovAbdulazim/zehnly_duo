# 📊 Zehnly Duo Analytics API Documentation

## Overview

The Analytics API provides comprehensive learning analytics with intelligent 6-hour caching for optimal performance. All analytics data is automatically generated from user lesson completion data and cached for fast retrieval.

## Base URL
```
/api/analytics
```

---

## 📈 Main Analytics Endpoint

### `GET /api/analytics/`

**Description:** Retrieves comprehensive analytics data including daily patterns, user segmentation, course performance, and key metrics.

#### Request

**URL:** `GET /api/analytics/`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `force_refresh` | boolean | `false` | Forces fresh data generation, bypassing cache |

**Example Requests:**
```bash
# Get cached analytics (recommended)
GET /api/analytics/

# Force fresh data generation
GET /api/analytics/?force_refresh=true
```

#### Response

**Status Code:** `200 OK`

**Content-Type:** `application/json`

**Response Body:**
```json
{
  "generated_at": "2025-11-08T14:30:00Z",
  "cache_expires_at": "2025-11-08T20:30:00Z",
  "data_period": {
    "start_date": "2025-10-06",
    "end_date": "2025-11-08", 
    "total_days": 33
  },
  "summary": {
    "total_lessons_completed": 29232,
    "average_daily_lessons": 885.8,
    "peak_daily_activity": 1740,
    "peak_date": "2025-10-29",
    "active_learning_days": 33,
    "total_users": 4030,
    "daily_active_users_avg": 112
  },
  "daily_data": [
    {
      "date": "2025-11-08",
      "day_of_week": "Friday",
      "dau": 45,
      "lessons_completed": 389,
      "lessons_per_user": 8.6,
      "lesson_breakdown": {
        "word": 142,
        "story": 128,
        "test": 119
      },
      "performance_rating": "moderate"
    }
  ],
  "hourly_patterns": [
    {
      "hour": 15,
      "time": "15:00", 
      "lessons": 3321,
      "unique_users": 320,
      "percentage_of_daily": 11.5,
      "lessons_per_user": 10.4,
      "weekend_lessons": 850,
      "weekday_lessons": 2471,
      "activity_level": "peak"
    }
  ],
  "courses": [
    {
      "course_id": 1,
      "course_name": "English for Russian Speakers - Elementary",
      "total_users": 2108,
      "total_lessons": 18685,
      "market_share_users": 52.3,
      "market_share_lessons": 63.9,
      "status": "primary"
    }
  ],
  "user_segmentation": [
    {
      "segment": "light",
      "lesson_range": "1-4",
      "user_count": 869,
      "percentage": 37.2,
      "avg_lessons": 1.9,
      "behavior": "trial_users"
    }
  ],
  "learning_zones": [
    {
      "zone": "peak",
      "time_range": "13:00-17:00",
      "total_lessons": 12096,
      "percentage": 41.8,
      "description": "prime_time"
    }
  ],
  "top_performance_days": [
    {
      "rank": 1,
      "date": "2025-10-29",
      "day": "Wednesday",
      "dau": 177,
      "lessons": 1740,
      "efficiency": 9.8,
      "achievement": "peak_day"
    }
  ],
  "kpis": {
    "user_retention_rate": 60.4,
    "power_users_percentage": 2.3,
    "avg_lessons_per_active_user": 14.7,
    "course_completion_balance": 0.95,
    "peak_hour_concentration": 11.5
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "optimization",
      "title": "Peak Hour Resource Focus",
      "description": "Focus infrastructure resources on 1-4 PM peak period"
    }
  ],
  "cache_info": {
    "is_cached": true,
    "cache_hit": true,
    "generation_time_ms": 245,
    "data_freshness": "6_hours"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | string (ISO 8601) | When the analytics were generated |
| `cache_expires_at` | string (ISO 8601) | When the cached data expires |
| `data_period` | object | Analysis time period information |
| `summary` | object | High-level platform statistics |
| `daily_data` | array | Daily activity breakdown (last 30 days) |
| `hourly_patterns` | array | 24-hour activity patterns |
| `courses` | array | Course performance metrics |
| `user_segmentation` | array | User activity level breakdown |
| `learning_zones` | array | Time-based learning zone analysis |
| `top_performance_days` | array | Best performing days ranked |
| `kpis` | object | Key performance indicators |
| `recommendations` | array | Actionable insights |
| `cache_info` | object | Cache status and performance info |

#### Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid request parameters"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to generate analytics: Database connection error"
}
```

---

## 🔄 Cache Management Endpoints

### `POST /api/analytics/refresh`

**Description:** Forces immediate refresh of analytics cache with fresh data.

#### Request
```bash
POST /api/analytics/refresh
```

#### Response
```json
{
  "message": "Analytics cache refreshed successfully",
  "cached": true,
  "generated_at": "2025-11-08T14:30:00Z",
  "expires_at": "2025-11-08T20:30:00Z"
}
```

### `GET /api/analytics/cache/status`

**Description:** Provides detailed information about cache status.

#### Request
```bash
GET /api/analytics/cache/status
```

#### Response
```json
{
  "cache_exists": true,
  "generated_at": "2025-11-08T14:30:00Z",
  "expires_at": "2025-11-08T20:30:00Z",
  "age_minutes": 180,
  "expires_in_minutes": 180,
  "is_expired": false,
  "needs_refresh": false
}
```

### `DELETE /api/analytics/cache`

**Description:** Clears the analytics cache. Next request will generate fresh data.

#### Request
```bash
DELETE /api/analytics/cache
```

#### Response
```json
{
  "message": "Analytics cache cleared successfully"
}
```

---

## 📊 Data Models

### Summary Object
```json
{
  "total_lessons_completed": 29232,        // Total completed lessons
  "average_daily_lessons": 885.8,          // Average lessons per day
  "peak_daily_activity": 1740,             // Highest single-day lesson count
  "peak_date": "2025-10-29",               // Date of peak activity
  "active_learning_days": 33,              // Days with activity
  "total_users": 4030,                     // Total registered users
  "daily_active_users_avg": 112            // Average daily active users
}
```

### Daily Data Object
```json
{
  "date": "2025-11-08",                     // Date in YYYY-MM-DD format
  "day_of_week": "Friday",                  // Day name
  "dau": 45,                                // Daily active users
  "lessons_completed": 389,                 // Total lessons completed
  "lessons_per_user": 8.6,                 // Efficiency metric
  "lesson_breakdown": {                     // Lessons by type
    "word": 142,
    "story": 128, 
    "test": 119
  },
  "performance_rating": "moderate"          // excellent|strong|good|moderate|low
}
```

### Hourly Pattern Object
```json
{
  "hour": 15,                               // Hour (0-23)
  "time": "15:00",                          // Time string
  "lessons": 3321,                          // Total lessons in this hour
  "unique_users": 320,                      // Unique users active
  "percentage_of_daily": 11.5,              // % of daily activity
  "lessons_per_user": 10.4,                 // Efficiency metric
  "weekend_lessons": 850,                   // Weekend activity
  "weekday_lessons": 2471,                  // Weekday activity
  "activity_level": "peak"                  // peak|high|moderate|low|minimal
}
```

### Course Analytics Object
```json
{
  "course_id": 1,                           // Course identifier
  "course_name": "English for Russian Speakers - Elementary",
  "total_users": 2108,                      // Users enrolled
  "total_lessons": 18685,                   // Lessons completed
  "market_share_users": 52.3,               // % of total users
  "market_share_lessons": 63.9,             // % of total lessons
  "status": "primary"                       // primary|secondary|emerging
}
```

### User Segmentation Object  
```json
{
  "segment": "light",                       // light|moderate|active|very_active
  "lesson_range": "1-4",                    // Lesson count range
  "user_count": 869,                        // Users in segment
  "percentage": 37.2,                       // % of total users
  "avg_lessons": 1.9,                       // Average lessons completed
  "behavior": "trial_users"                 // Behavior description
}
```

### Learning Zone Object
```json
{
  "zone": "peak",                           // Zone name
  "time_range": "13:00-17:00",              // Time range
  "total_lessons": 12096,                   // Lessons in this zone
  "percentage": 41.8,                       // % of total activity
  "description": "prime_time"               // Zone description
}
```

### Top Performance Day Object
```json
{
  "rank": 1,                                // Performance ranking
  "date": "2025-10-29",                     // Date
  "day": "Wednesday",                       // Day name
  "dau": 177,                               // Daily active users
  "lessons": 1740,                          // Total lessons
  "efficiency": 9.8,                        // Lessons per user
  "achievement": "peak_day"                 // Achievement type
}
```

### KPIs Object
```json
{
  "user_retention_rate": 60.4,              // % users with 5+ lessons
  "power_users_percentage": 2.3,            // % users with 50+ lessons
  "avg_lessons_per_active_user": 14.7,      // Average lesson completion
  "course_completion_balance": 0.95,         // Course balance metric
  "peak_hour_concentration": 11.5           // Peak hour activity %
}
```

### Recommendation Object
```json
{
  "priority": "high",                       // high|medium|low
  "category": "optimization",               // Category type
  "title": "Peak Hour Resource Focus",      // Recommendation title
  "description": "Focus infrastructure resources on 1-4 PM peak period"
}
```

---

## ⚡ Performance & Caching

### Cache Strategy
- **Cache Duration:** 6 hours
- **Background Refresh:** Automatic refresh at 5 hours
- **Cache Key:** `analytics:full_report`
- **Storage:** Redis with JSON serialization

### Performance Metrics
- **Cached Response:** ~0ms (instant)
- **Fresh Generation:** ~200-500ms
- **Data Processing:** Optimized SQL queries with aggregations
- **Memory Usage:** ~2-5MB per cached report

### Best Practices

1. **Use Default Caching:** Don't use `force_refresh=true` unless necessary
2. **Monitor Cache Status:** Check `/cache/status` for cache health
3. **Background Refresh:** Cache automatically refreshes before expiry
4. **Error Handling:** Graceful fallbacks if cache fails

---

## 🔐 Authentication & Access

Currently, the analytics endpoints are **public**. For production use, consider adding:

- **Admin Authentication** for refresh/clear cache endpoints
- **Rate Limiting** for analytics endpoint
- **Role-Based Access** for different analytics views

---

## 📝 Usage Examples

### JavaScript/Fetch
```javascript
// Get analytics data
const response = await fetch('/api/analytics/');
const analytics = await response.json();

console.log(`Total lessons: ${analytics.summary.total_lessons_completed}`);
console.log(`Peak hour: ${analytics.hourly_patterns.find(h => h.activity_level === 'peak').time}`);
```

### Python/Requests
```python
import requests

# Get analytics
response = requests.get('http://your-api.com/api/analytics/')
analytics = response.json()

print(f"Daily active users: {analytics['summary']['daily_active_users_avg']}")
print(f"Cache hit: {analytics['cache_info']['cache_hit']}")
```

### cURL
```bash
# Get analytics
curl -X GET "http://your-api.com/api/analytics/" \
  -H "Content-Type: application/json"

# Force refresh
curl -X GET "http://your-api.com/api/analytics/?force_refresh=true" \
  -H "Content-Type: application/json"

# Check cache status
curl -X GET "http://your-api.com/api/analytics/cache/status" \
  -H "Content-Type: application/json"
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Slow Response Times**
- Check if cache is working: `/cache/status`
- Verify Redis connection
- Consider database query optimization

**2. Empty or Incorrect Data** 
- Ensure `UserLessonProgress` table has data
- Check `completed_at` timestamps are not null
- Verify lesson completion flags are set

**3. Cache Not Working**
- Check Redis connection in `cache.py`
- Verify `REDIS_URL` configuration
- Monitor cache set/get operations

**4. Memory Issues**
- Monitor Redis memory usage
- Consider data retention policies
- Optimize query result sizes

### Debug Commands
```bash
# Check cache status
GET /api/analytics/cache/status

# Force fresh data
GET /api/analytics/?force_refresh=true

# Clear problematic cache
DELETE /api/analytics/cache
```

---

*Last updated: November 8, 2025*
*API Version: 1.0*