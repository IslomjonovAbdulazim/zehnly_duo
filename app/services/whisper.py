import os
import tempfile
import logging
from typing import List, Optional
from openai import AsyncOpenAI
from ..models.lesson_content import SubtitleCreate


class WhisperService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPEN_AI"))
        self.logger = logging.getLogger(__name__)
    
    async def generate_subtitles(self, audio_content: bytes, story_text: str, story_id: int) -> List[SubtitleCreate]:
        """
        Generate subtitles from audio using OpenAI Whisper API
        
        Args:
            audio_content: The audio file content as bytes
            story_text: The original story text for validation
            story_id: The story ID to associate subtitles with
        
        Returns:
            List of SubtitleCreate objects with timing and text information
        """
        if not self.client.api_key:
            self.logger.error("❌ OpenAI API key not found in environment variables")
            return []
        
        self.logger.info(f"🎵 Starting subtitle generation for story {story_id}")
        self.logger.info(f"📄 Story text length: {len(story_text)} characters")
        self.logger.info(f"🎵 Audio content size: {len(audio_content)} bytes")
        
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_audio:
                temp_audio.write(audio_content)
                temp_audio_path = temp_audio.name
            
            try:
                # Transcribe audio with timestamps using Whisper
                with open(temp_audio_path, "rb") as audio_file:
                    transcription = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["word"]
                    )
                
                self.logger.info("✅ Transcription completed successfully")
                
                # Extract words with timestamps
                subtitles = []
                consumed_position = 0  # Track where we've already mapped words
                
                if hasattr(transcription, 'words') and transcription.words:
                    for word_data in transcription.words:
                        word_text = word_data.word.strip()
                        
                        # Find word AFTER the last consumed position (sequential mapping)
                        start_pos = story_text.lower().find(word_text.lower(), consumed_position)
                        
                        if start_pos != -1:
                            end_pos = start_pos + len(word_text)
                            consumed_position = end_pos  # Move forward for next word
                        else:
                            # Fallback if word not found - use current consumed position
                            start_pos = consumed_position
                            end_pos = consumed_position + len(word_text)
                            consumed_position = end_pos
                        
                        # Ensure end_audio is always greater than start_audio
                        start_time = word_data.start
                        end_time = word_data.end
                        if end_time <= start_time:
                            end_time = start_time + 0.1  # Add 100ms minimum duration
                        
                        subtitle = SubtitleCreate(
                            story_id=story_id,
                            text=word_text,
                            start_audio=start_time,
                            end_audio=end_time,
                            start_position=start_pos,
                            end_position=end_pos
                        )
                        subtitles.append(subtitle)
                
                # If no word-level timestamps available, create sentence-level subtitles
                if not subtitles and hasattr(transcription, 'segments'):
                    for segment in transcription.segments:
                        start_pos = story_text.lower().find(segment.text.lower().strip())
                        end_pos = start_pos + len(segment.text.strip()) if start_pos != -1 else len(segment.text.strip())
                        
                        if start_pos == -1:
                            start_pos = 0
                            end_pos = len(segment.text.strip())
                        
                        # Ensure end_audio is always greater than start_audio
                        start_time = segment.start
                        end_time = segment.end
                        if end_time <= start_time:
                            end_time = start_time + 0.1  # Add 100ms minimum duration
                        
                        subtitle = SubtitleCreate(
                            story_id=story_id,
                            text=segment.text.strip(),
                            start_audio=start_time,
                            end_audio=end_time,
                            start_position=start_pos,
                            end_position=end_pos
                        )
                        subtitles.append(subtitle)
                
                # Fallback: create single subtitle for entire audio
                if not subtitles:
                    self.logger.warning("⚠️ No timestamps available, creating single subtitle")
                    subtitle = SubtitleCreate(
                        story_id=story_id,
                        text=story_text,
                        start_audio=0.0,
                        end_audio=30.0,  # Approximate duration
                        start_position=0,
                        end_position=len(story_text)
                    )
                    subtitles.append(subtitle)
                
                self.logger.info(f"✅ Generated {len(subtitles)} subtitles")
                return subtitles
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_audio_path)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to delete temp file: {e}")
        
        except Exception as e:
            self.logger.error(f"💥 Whisper API error: {e}")
            return []
    
    async def update_subtitle_timing(self, audio_content: bytes, existing_text: str) -> Optional[tuple]:
        """
        Update timing for existing subtitle text
        
        Args:
            audio_content: The audio file content as bytes
            existing_text: The subtitle text to find timing for
        
        Returns:
            Tuple of (start_time, end_time) or None if not found
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_audio:
                temp_audio.write(audio_content)
                temp_audio_path = temp_audio.name
            
            try:
                with open(temp_audio_path, "rb") as audio_file:
                    transcription = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["word"]
                    )
                
                # Find the text in transcription
                if hasattr(transcription, 'words') and transcription.words:
                    for word_data in transcription.words:
                        if existing_text.lower().strip() in word_data.word.lower():
                            return (word_data.start, word_data.end)
                
                return None
                
            finally:
                os.unlink(temp_audio_path)
        
        except Exception as e:
            self.logger.error(f"💥 Timing update error: {e}")
            return None


whisper_service = WhisperService()