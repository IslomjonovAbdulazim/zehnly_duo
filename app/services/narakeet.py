import os
import httpx
import logging
from typing import Optional


class NarakeetService:
    def __init__(self):
        self.api_key = os.getenv("NARAKEET")
        self.base_url = "https://api.narakeet.com"
    
    async def generate_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        logger = logging.getLogger(__name__)
        logger.info(f"🎵 Starting audio generation for text: '{text[:50]}...'")
        logger.info(f"🎤 Voice requested: {voice}")
        
        if not self.api_key:
            logger.error("❌ NARAKEET API key not found in environment variables")
            return None
        
        logger.info(f"🔑 API key present: {'*' * 10}{self.api_key[-4:] if len(self.api_key) > 4 else '****'}")
        
        headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "text/plain",
            "x-api-key": self.api_key,
        }
        
        url = f"{self.base_url}/text-to-speech/m4a"
        if voice:
            url += f'?voice={voice}'
        
        logger.info(f"🌐 Making request to: {url}")
        logger.info(f"🎤 Voice parameter: {voice}")
        logger.info(f"📄 Text length: {len(text)} characters")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info("📡 Sending request to Narakeet...")
                response = await client.post(
                    url,
                    headers=headers,
                    content=text.encode('utf8')
                )
                
                logger.info(f"📊 Response status: {response.status_code}")
                logger.info(f"📋 Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    content_length = len(response.content)
                    logger.info(f"✅ Audio generated successfully! Size: {content_length} bytes")
                    
                    if content_length == 0:
                        logger.warning("⚠️ Audio content is empty!")
                        return None
                    
                    return response.content
                else:
                    logger.error(f"❌ Narakeet API error: {response.status_code}")
                    logger.error(f"📄 Error response: {response.text}")
                    return None
                    
        except httpx.TimeoutException as e:
            logger.error(f"⏰ Request timeout: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"🌐 Network error: {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            logger.error(f"📚 Full traceback: {traceback.format_exc()}")
            return None


narakeet_service = NarakeetService()