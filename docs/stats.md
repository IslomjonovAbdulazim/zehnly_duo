# Course Statistics API Documentation

## Overview
This document describes the statistics endpoints available in the admin API for tracking course performance and student progress.

## Authentication
All stats endpoints require admin authentication. Include the admin token in the Authorization header:
```
Authorization: Bearer <admin_token>
```

## Endpoints

### GET /admin/stats/courses
Get statistics for all courses including student counts.

**Request:**
```http
GET /admin/stats/courses HTTP/1.1
Host: your-domain.com
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "courses": [
    {
      "course_id": 1,
      "course_title": "English for Beginners A1",
      "total_students": 25
    },
    {
      "course_id": 2,
      "course_title": "English Intermediate A2", 
      "total_students": 15
    },
    {
      "course_id": 3,
      "course_title": "Russian for Beginners",
      "total_students": 8
    }
  ]
}
```

**Response Fields:**
- `courses`: Array of course statistics
  - `course_id`: Unique identifier for the course
  - `course_title`: Name of the course
  - `total_students`: Number of students enrolled in this course

---

### GET /admin/stats/courses/{course_id}
Get detailed statistics for a specific course including student list sorted by progress.

**Request:**
```http
GET /admin/stats/courses/1 HTTP/1.1
Host: your-domain.com
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "course_info": {
    "id": 1,
    "title": "English for Beginners A1"
  },
  "total_students": 3,
  "students": [
    {
      "user_id": 123,
      "full_name": "John Doe",
      "phone_number": "+998901234567",
      "lessons_completed": 34
    },
    {
      "user_id": 124,
      "full_name": "Jane Smith",
      "phone_number": "+998909876543", 
      "lessons_completed": 28
    },
    {
      "user_id": 125,
      "full_name": "Ali Karimov",
      "phone_number": null,
      "lessons_completed": 12
    }
  ]
}
```

**Response Fields:**
- `course_info`: Basic course information
  - `id`: Course ID
  - `title`: Course title
- `total_students`: Total number of students enrolled
- `students`: Array of student progress data (sorted by lessons_completed descending)
  - `user_id`: Unique user identifier  
  - `full_name`: Student's first name + last name
  - `phone_number`: Student's phone number (can be null)
  - `lessons_completed`: Number of lessons the student has completed

**URL Parameters:**
- `course_id`: Integer - The ID of the course to get statistics for

---

## Error Responses

### 404 Not Found
Returned when a course doesn't exist:
```json
{
  "detail": "Course not found"
}
```

### 401 Unauthorized
Returned when admin token is invalid or missing:
```json
{
  "detail": "Invalid admin token"
}
```

## Usage Examples

### Frontend JavaScript Example
```javascript
// Get all courses stats
const getCoursesStats = async () => {
  const response = await fetch('/admin/stats/courses', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  const data = await response.json();
  return data.courses;
};

// Get specific course stats
const getCourseDetails = async (courseId) => {
  const response = await fetch(`/admin/stats/courses/${courseId}`, {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  const data = await response.json();
  return {
    courseInfo: data.course_info,
    totalStudents: data.total_students,
    students: data.students
  };
};
```

### Python Example
```python
import requests

def get_courses_stats(admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = requests.get('/admin/stats/courses', headers=headers)
    return response.json()['courses']

def get_course_details(course_id, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = requests.get(f'/admin/stats/courses/{course_id}', headers=headers)
    return response.json()
```

## Notes
- Students are automatically sorted by `lessons_completed` in descending order (most active first)
- The `phone_number` field can be `null` if the student hasn't provided their phone number
- Only students who are enrolled in the course (have a record in `user_course_progress`) are included in the statistics