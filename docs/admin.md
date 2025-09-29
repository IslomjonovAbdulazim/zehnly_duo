# Admin API Documentation

This document describes all admin endpoints for the Language Learning Center API. All admin endpoints require authentication via JWT token.

## Authentication

All admin endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

First obtain a token using the login endpoint.

---

## Authentication Endpoints

### Login
```http
POST /admin/login
```

**Request Body:**
```json
{
  "email": "admin@gmail.com",
  "password": "admin123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Error Cases:**
- `401 Unauthorized` - Invalid credentials

---

## Course Management

### Create Course
```http
POST /admin/courses
```

**Request Body:**
```json
{
  "title": "English for Beginners",
  "native_language": "Uzbek",
  "learning_language": "English"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "English for Beginners",
  "native_language": "Uzbek",
  "learning_language": "English",
  "logo_url": null
}
```

### Get All Courses
```http
GET /admin/courses
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "English for Beginners",
    "native_language": "Uzbek",
    "learning_language": "English",
    "logo_url": "https://storage.example.com/logo1.png"
  }
]
```

### Get Single Course
```http
GET /admin/courses/{course_id}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "English for Beginners",
  "native_language": "Uzbek",
  "learning_language": "English",
  "logo_url": "https://storage.example.com/logo1.png"
}
```

**Error Cases:**
- `404 Not Found` - Course not found

### Update Course
```http
PUT /admin/courses/{course_id}
```

**Request Body:**
```json
{
  "title": "English for Beginners - Updated",
  "native_language": "Uzbek",
  "learning_language": "English"
}
```

**Success Response (200):** Same as create course response

**Error Cases:**
- `404 Not Found` - Course not found

### Delete Course
```http
DELETE /admin/courses/{course_id}
```

**Success Response (200):**
```json
{
  "message": "Course deleted successfully"
}
```

**Error Cases:**
- `404 Not Found` - Course not found

---

## Chapter Management

### Create Chapter
```http
POST /admin/chapters
```

**Request Body:**
```json
{
  "title": "Basic Greetings",
  "course_id": 1,
  "order": 1
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Basic Greetings",
  "course_id": 1,
  "order": 1
}
```

### Get Course Chapters
```http
GET /admin/courses/{course_id}/chapters
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "Basic Greetings",
    "course_id": 1,
    "order": 1
  },
  {
    "id": 2,
    "title": "Family Members",
    "course_id": 1,
    "order": 2
  }
]
```

### Update Chapter
```http
PUT /admin/chapters/{chapter_id}
```

**Request Body:**
```json
{
  "title": "Basic Greetings - Updated",
  "course_id": 1,
  "order": 1
}
```

**Success Response (200):** Same as create chapter response

**Error Cases:**
- `404 Not Found` - Chapter not found

### Delete Chapter
```http
DELETE /admin/chapters/{chapter_id}
```

**Success Response (200):**
```json
{
  "message": "Chapter deleted successfully"
}
```

**Error Cases:**
- `404 Not Found` - Chapter not found

---

## Lesson Management

### Create Lesson
```http
POST /admin/lessons
```

**Request Body:**
```json
{
  "title": "Hello and Goodbye",
  "chapter_id": 1,
  "order": 1,
  "lesson_type": "word",
  "content": "In this lesson we learn basic greetings"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Hello and Goodbye",
  "chapter_id": 1,
  "order": 1,
  "lesson_type": "word",
  "content": "In this lesson we learn basic greetings"
}
```

### Get Chapter Lessons
```http
GET /admin/chapters/{chapter_id}/lessons
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "Hello and Goodbye",
    "chapter_id": 1,
    "order": 1,
    "lesson_type": "word",
    "content": "In this lesson we learn basic greetings"
  }
]
```

### Update Lesson
```http
PUT /admin/lessons/{lesson_id}
```

**Request Body:** Same as create lesson

**Success Response (200):** Same as create lesson response

**Error Cases:**
- `404 Not Found` - Lesson not found

### Delete Lesson
```http
DELETE /admin/lessons/{lesson_id}
```

**Success Response (200):**
```json
{
  "message": "Lesson deleted successfully"
}
```

**Error Cases:**
- `404 Not Found` - Lesson not found

---

## Word Management

### Create Word
```http
POST /admin/words
```

**Request Body:**
```json
{
  "lesson_id": 1,
  "word": "hello",
  "translation": "salom",
  "example_sentence": "Hello, how are you?",
  "audio_url": null,
  "image_url": null,
  "example_audio": null
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "lesson_id": 1,
  "word": "hello",
  "translation": "salom",
  "example_sentence": "Hello, how are you?",
  "audio_url": null,
  "image_url": null,
  "example_audio": null
}
```

### Get Lesson Words
```http
GET /admin/lessons/{lesson_id}/words
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "lesson_id": 1,
    "word": "hello",
    "translation": "salom",
    "example_sentence": "Hello, how are you?",
    "audio_url": "https://storage.example.com/word_1_audio.mp3",
    "image_url": "https://storage.example.com/word_1_image.jpg",
    "example_audio": "https://storage.example.com/word_1_example_audio.mp3"
  }
]
```

### Update Word
```http
PUT /admin/words/{word_id}
```

**Request Body:** Same as create word

**Success Response (200):** Same as create word response

**Error Cases:**
- `404 Not Found` - Word not found

### Delete Word
```http
DELETE /admin/words/{word_id}
```

**Success Response (200):**
```json
{
  "message": "Word deleted successfully"
}
```

**Error Cases:**
- `404 Not Found` - Word not found

---

## Story Management

### Create Story
```http
POST /admin/stories
```

**Request Body:**
```json
{
  "lesson_id": 1,
  "story_text": "Once upon a time, there was a young student learning English...",
  "audio_url": null
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "lesson_id": 1,
  "story_text": "Once upon a time, there was a young student learning English...",
  "audio_url": null
}
```

### Get Lesson Stories
```http
GET /admin/lessons/{lesson_id}/stories
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "lesson_id": 1,
    "story_text": "Once upon a time, there was a young student learning English...",
    "audio_url": "https://storage.example.com/story_1_audio.mp3"
  }
]
```

### Update Story
```http
PUT /admin/stories/{story_id}
```

**Request Body:** Same as create story

**Success Response (200):** Same as create story response

**Error Cases:**
- `404 Not Found` - Story not found

### Delete Story
```http
DELETE /admin/stories/{story_id}
```

**Success Response (200):**
```json
{
  "message": "Story deleted successfully"
}
```

**Error Cases:**
- `404 Not Found` - Story not found

---

## Audio Generation

### Generate Word Audio
```http
POST /admin/words/{word_id}/generate-audio?voice=amy
```

**Query Parameters:**
- `voice` (optional): Voice to use for audio generation (default: "amy")

**Success Response (200):**
```json
{
  "message": "Audio generated successfully",
  "audio_url": "https://storage.example.com/word_1_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Word not found
- `500 Internal Server Error` - Audio generation failed

### Generate Example Sentence Audio
```http
POST /admin/words/{word_id}/generate-example-audio?voice=amy
```

**Query Parameters:**
- `voice` (optional): Voice to use for audio generation (default: "amy")

**Success Response (200):**
```json
{
  "message": "Example audio generated successfully",
  "audio_url": "https://storage.example.com/word_1_example_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Word not found
- `400 Bad Request` - Word has no example sentence
- `500 Internal Server Error` - Audio generation failed

### Generate Story Audio
```http
POST /admin/stories/{story_id}/generate-audio?voice=amy
```

**Query Parameters:**
- `voice` (optional): Voice to use for audio generation (default: "amy")

**Success Response (200):**
```json
{
  "message": "Story audio generated successfully",
  "audio_url": "https://storage.example.com/story_1_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Story not found
- `500 Internal Server Error` - Audio generation failed

---

## File Upload

### Upload Course Logo
```http
POST /admin/upload/logo/{course_id}
```

**Request:** Multipart form with file upload

**Success Response (200):**
```json
{
  "message": "Logo uploaded successfully",
  "logo_url": "https://storage.example.com/course_1_logo.png"
}
```

**Error Cases:**
- `404 Not Found` - Course not found

### Upload Word Audio
```http
POST /admin/upload/audio/{word_id}
```

**Request:** Multipart form with file upload

**Success Response (200):**
```json
{
  "message": "Audio uploaded successfully",
  "audio_url": "https://storage.example.com/word_1_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Word not found

### Upload Word Example Audio
```http
POST /admin/upload/example-audio/{word_id}
```

**Request:** Multipart form with file upload

**Success Response (200):**
```json
{
  "message": "Example audio uploaded successfully",
  "audio_url": "https://storage.example.com/word_1_example_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Word not found

### Upload Story Audio
```http
POST /admin/upload/story-audio/{story_id}
```

**Request:** Multipart form with file upload

**Success Response (200):**
```json
{
  "message": "Story audio uploaded successfully",
  "audio_url": "https://storage.example.com/story_1_audio.mp3"
}
```

**Error Cases:**
- `404 Not Found` - Story not found

### Upload Word Image
```http
POST /admin/upload/image/{word_id}
```

**Request:** Multipart form with file upload

**Success Response (200):**
```json
{
  "message": "Image uploaded successfully",
  "image_url": "https://storage.example.com/word_1_image.jpg"
}
```

**Error Cases:**
- `404 Not Found` - Word not found

---

## Common Error Responses

### Authentication Error
```json
{
  "detail": "Not authenticated"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Not Found Error
```json
{
  "detail": "Course not found"
}
```

---

## Data Models

### Lesson Types
- `word` - Lesson focused on vocabulary
- `story` - Lesson focused on reading comprehension
- 
### File Upload Requirements
- **Audio files:** MP3 format recommended
- **Images:** JPG, PNG formats supported
- **Maximum file size:** 10MB per file

---

## Workflow Examples

### Creating a Complete Course Structure

1. **Create Course**
   ```http
   POST /admin/courses
   ```

2. **Add Chapter**
   ```http
   POST /admin/chapters
   ```

3. **Add Lesson**
   ```http
   POST /admin/lessons
   ```

4. **Add Words**
   ```http
   POST /admin/words
   ```

5. **Generate Audio**
   ```http
   POST /admin/words/{word_id}/generate-audio
   POST /admin/words/{word_id}/generate-example-audio
   ```

6. **Upload Images**
   ```http
   POST /admin/upload/image/{word_id}
   ```

### Adding Story Content

1. **Create Story**
   ```http
   POST /admin/stories
   ```

2. **Generate Story Audio**
   ```http
   POST /admin/stories/{story_id}/generate-audio
   ```

This documentation covers all admin endpoints with request/response examples and error handling. Use this as a reference when integrating with the admin API.