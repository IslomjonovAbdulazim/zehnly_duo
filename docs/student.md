# Student API Documentation

This document describes all student endpoints for the Language Learning Center API. Student endpoints use header-based authentication to automatically register/login users.

## Authentication

All student endpoints require user information via HTTP headers. Users are automatically registered on first request and logged in on subsequent requests.

**Required Headers (JSON format):**
```json
{
  "X-User-ID": "unique_student_id",
  "X-First-Name": "John",
  "X-Last-Name": "Doe",
  "X-Phone-Number": "+998901234567"
}
```

---

## User Profile

### Get User Profile
```http
GET /students/profile
```

**Request Headers:**
```json
{
  "X-User-ID": "student_123",
  "X-First-Name": "John",
  "X-Last-Name": "Doe",
  "X-Phone-Number": "+998901234567"
}
```

**Request Body:** None

**Success Response (200):**
```json
{
  "id": 1,
  "zehn_id": "student_123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+998901234567",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "X-User-ID"],
      "msg": "Field required",
      "input": null,
      "url": "https://errors.pydantic.dev/2.11/v/missing"
    },
    {
      "type": "missing", 
      "loc": ["header", "X-First-Name"],
      "msg": "Field required",
      "input": null,
      "url": "https://errors.pydantic.dev/2.11/v/missing"
    },
    {
      "type": "missing",
      "loc": ["header", "X-Last-Name"], 
      "msg": "Field required",
      "input": null,
      "url": "https://errors.pydantic.dev/2.11/v/missing"
    }
  ]
}
```

---

## Course Management

### Get Available Courses
```http
GET /students/courses
```

**Request Headers:**
```json
{
  "X-User-ID": "student_123",
  "X-First-Name": "John",
  "X-Last-Name": "Doe",
  "X-Phone-Number": "+998901234567"
}
```

**Request Body:** None

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "English for Beginners",
    "native_language": "Uzbek",
    "learning_language": "English",
    "logo_url": "https://example.com/logos/course_1_logo.png",
    "progress_percentage": 45.5
  },
  {
    "id": 2,
    "title": "Russian Basics",
    "native_language": "Uzbek", 
    "learning_language": "Russian",
    "logo_url": "https://example.com/logos/course_2_logo.png",
    "progress_percentage": 0.0
  }
]
```

**Response Fields:**
- `progress_percentage`: User's completion percentage for this course (0-100)

### Get Course Structure
```http
GET /students/courses/{course_id}
```

**Request Headers:**
```json
{
  "X-User-ID": "student_123",
  "X-First-Name": "John",
  "X-Last-Name": "Doe",
  "X-Phone-Number": "+998901234567"
}
```

**Request Body:** None

**Success Response (200):**
```json
{
  "id": 1,
  "title": "English for Beginners",
  "native_language": "Uzbek",
  "learning_language": "English",
  "logo_url": "https://example.com/logos/course_1_logo.png",
  "chapters": [
    {
      "id": 1,
      "title": "Basic Greetings",
      "order": 1,
      "progress_percentage": 75.0,
      "lessons": [
        {
          "id": 1,
          "title": "Hello and Goodbye",
          "order": 1,
          "lesson_type": "word",
          "is_completed": true,
          "progress_percentage": 100.0
        },
        {
          "id": 2,
          "title": "How are you?",
          "order": 2,
          "lesson_type": "word",
          "is_completed": false,
          "progress_percentage": 0.0
        }
      ]
    }
  ]
}
```

**Response Fields:**
- `lesson_type`: Either "word" or "story"
- `is_completed`: Whether student has completed this lesson
- `progress_percentage`: Chapter completion percentage based on completed lessons

**Error Response (404):**
```json
{
  "detail": "Course not found"
}
```

---

## Lesson Content

### Get Lesson Content
```http
GET /students/lessons/{lesson_id}/content
```

**Headers:** Same as above

**Success Response (200):**
```json
{
  "lesson": {
    "id": 1,
    "title": "Hello and Goodbye",
    "lesson_type": "word",
    "content": "In this lesson we learn basic greetings"
  },
  "words": [
    {
      "id": 1,
      "word": "hello",
      "translation": "salom",
      "audio_url": "https://example.com/audio/word_1_audio.m4a",
      "image_url": "https://example.com/images/word_1_image.jpg",
      "example_sentence": "Hello, how are you?",
      "example_audio": "https://example.com/audio/word_1_example_audio.m4a",
      "progress": {
        "is_learned": false,
        "last_5_results": "101"
      }
    },
    {
      "id": 2,
      "word": "goodbye", 
      "translation": "xayr",
      "audio_url": "https://example.com/audio/word_2_audio.m4a",
      "image_url": null,
      "example_sentence": "Goodbye, see you tomorrow!",
      "example_audio": "https://example.com/audio/word_2_example_audio.m4a",
      "progress": {
        "is_learned": true,
        "last_5_results": "11110"
      }
    }
  ],
  "stories": [
    {
      "id": 1,
      "story_text": "John walks into the office. 'Hello everyone!' he says cheerfully. His colleagues respond with warm greetings...",
      "audio_url": "https://example.com/audio/story_1_audio.m4a",
      "subtitles": [
        {
          "id": 1,
          "text": "John walks into the office.",
          "start_audio": 0.0,
          "end_audio": 2.5,
          "start_position": 0,
          "end_position": 28
        },
        {
          "id": 2,
          "text": "Hello everyone!",
          "start_audio": 2.5,
          "end_audio": 4.0,
          "start_position": 29,
          "end_position": 44
        }
      ]
    }
  ]
}
```

**Progress Fields:**
- `is_learned`: Whether the student has mastered this word (based on recent performance)
- `last_5_results`: String of last 5 quiz results ("1" = correct, "0" = incorrect, most recent first)

**Audio Speed Configuration:**
- **Word audio**: Played at 0.8x speed (20% slower for better learning)
- **Example sentence audio**: Played at 1.0x speed (normal speed)
- **Story audio**: Played at 1.0x speed (normal speed)

**Error Cases:**
- `404 Not Found` - Lesson not found

---

## Quiz and Progress

### Complete Quiz
```http
POST /students/quiz/complete
```

**Headers:** Same as above

**Request Body:**
```json
{
  "lesson_id": 1,
  "correct_answers": 8,
  "total_questions": 10,
  "time_spent": 180,
  "question_results": [
    {
      "word_id": 1,
      "is_correct": true
    },
    {
      "word_id": 2,
      "is_correct": false
    },
    {
      "word_id": 3,
      "is_correct": true
    }
  ]
}
```

**Success Response (200):**
```json
{
  "lesson_id": 1,
  "score_percentage": 80.0,
  "correct_answers": 8,
  "total_questions": 10,
  "time_spent": 180,
  "lesson_completed": true,
  "course_progress": 45.5,
  "words_updated": 3,
  "message": "Quiz completed successfully"
}
```

**Request Fields:**
- `lesson_id`: ID of the completed lesson
- `correct_answers`: Number of correct answers
- `total_questions`: Total number of questions
- `time_spent`: Time in seconds
- `question_results`: Array of individual question results

**Response Fields:**
- `lesson_completed`: true if score >= 70%
- `course_progress`: Updated overall course progress percentage
- `words_updated`: Number of word progress records updated

**Learning Logic:**
- A word is marked as "learned" if the last 3 quiz attempts were correct
- Lesson is marked as completed if quiz score >= 70%
- Course progress is calculated as percentage of completed lessons

**Error Cases:**
- `404 Not Found` - Lesson not found

---

## Audio Files

### Audio File Access
Audio files are served directly via HTTP GET requests to the URLs provided in the API responses:

```http
GET /audio/{filename}
```

**Examples:**
- Word audio: `GET /audio/word_1_audio.m4a`
- Example audio: `GET /audio/word_1_example_audio.m4a`
- Story audio: `GET /audio/story_1_audio.m4a`

**Response:** Audio file stream with proper MIME type

**Cache Headers:**
Audio files are served with no-cache headers to ensure fresh content delivery.

---

## Common Error Responses

### Missing Headers Error
```json
{
  "detail": "Header 'X-User-ID' is required"
}
```

### Not Found Error
```json
{
  "detail": "Lesson not found"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "lesson_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Data Models

### Lesson Types
- `word` - Vocabulary-focused lesson with word cards and definitions
- `story` - Reading comprehension lesson with stories and audio

### Progress Tracking
- **Course Progress**: Percentage of completed lessons in the course
- **Lesson Progress**: Binary completion status (completed if quiz score >= 70%)
- **Word Progress**: Individual word mastery based on quiz performance

### Audio Speed Settings
- **Word Audio**: 0.8x speed (slower for pronunciation learning)
- **Example Sentences**: 1.0x speed (normal conversation pace)
- **Stories**: 1.0x speed (natural reading pace)

---

## Workflow Examples

### Starting a New Course

1. **Get Available Courses**
   ```http
   GET /students/courses
   ```

2. **View Course Structure**
   ```http
   GET /students/courses/1
   ```

3. **Access First Lesson**
   ```http
   GET /students/lessons/1/content
   ```

### Completing a Lesson

1. **Study Lesson Content**
   - Listen to word pronunciations
   - Read example sentences
   - Practice with story content

2. **Complete Quiz**
   ```http
   POST /students/quiz/complete
   ```

3. **Track Progress**
   - View updated course progress
   - See word mastery status
   - Move to next lesson

### Learning Path

1. **Word Lessons**: Learn vocabulary with slow pronunciation
2. **Story Lessons**: Practice reading comprehension with normal-speed audio
3. **Progress Tracking**: Monitor mastery of individual words and overall course progress
4. **Adaptive Learning**: Focus on words that need more practice based on quiz results

---

## Authentication Flow

### First-Time User
```http
GET /students/profile
X-User-ID: new_student_456
X-First-Name: Maria
X-Last-Name: Garcia
X-Phone-Number: +998901234567
```
→ User automatically registered and returned

### Returning User
```http
GET /students/courses
X-User-ID: new_student_456
X-First-Name: Maria
X-Last-Name: Garcia
```
→ Existing user recognized and courses returned with progress

---

This documentation covers all student endpoints with examples and explains the learning progression system. Students can seamlessly start learning without manual registration and track their progress across courses, lessons, and individual words.