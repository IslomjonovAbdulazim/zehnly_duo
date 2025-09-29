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
        logger.info(f"📄 Text length: {len(text)} characters")
        
        if not self.api_key:
            logger.error("❌ NARAKEET API key not found in environment variables")
            return None
        
        logger.info(f"🔑 API key present: {'*' * 10}{self.api_key[-4:] if len(self.api_key) > 4 else '****'}")
        
        # Check if we need long content API
        if len(text) > 1000:
            logger.info("📏 Text is long, using Long Content API")
            return await self._generate_long_audio(text, voice)
        else:
            logger.info("📏 Text is short, using Simple API")
            return await self._generate_short_audio(text, voice)

    async def _generate_short_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        logger = logging.getLogger(__name__)
        
        headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "text/plain",
            "x-api-key": self.api_key,
        }
        
        url = f"{self.base_url}/text-to-speech/m4a"
        if voice:
            url += f'?voice={voice}'
        
        logger.info(f"🌐 Making SHORT request to: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info("📡 Sending SHORT request to Narakeet...")
                response = await client.post(
                    url,
                    headers=headers,
                    content=text.encode('utf8')
                )
                
                logger.info(f"📊 SHORT Response status: {response.status_code}")
                
                if response.status_code == 200:
                    content_length = len(response.content)
                    logger.info(f"✅ SHORT Audio generated successfully! Size: {content_length} bytes")
                    
                    if content_length == 0:
                        logger.warning("⚠️ SHORT Audio content is empty!")
                        return None
                    
                    return response.content
                else:
                    logger.error(f"❌ SHORT Narakeet API error: {response.status_code}")
                    logger.error(f"📄 SHORT Error response: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"💥 SHORT API error: {e}")
            return None

    async def _generate_long_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        logger = logging.getLogger(__name__)
        
        # Step 1: Start build
        headers = {
            "Content-Type": "text/plain",
            "x-api-key": self.api_key,
        }
        
        url = f"{self.base_url}/text-to-speech/m4a"
        if voice:
            url += f'?voice={voice}'
        
        logger.info(f"🚀 LONG: Starting build request to: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Request build
                logger.info("📡 LONG: Sending build request...")
                response = await client.post(
                    url,
                    headers=headers,
                    content=text.encode('utf8')
                )
                
                logger.info(f"📊 LONG: Build response status: {response.status_code}")
                
                if response.status_code != 202:  # Long content returns 202 Accepted
                    logger.error(f"❌ LONG: Build failed: {response.status_code}")
                    logger.error(f"📄 LONG: Build error: {response.text}")
                    return None
                
                build_response = response.json()
                status_url = build_response.get("statusUrl")
                
                if not status_url:
                    logger.error("❌ LONG: No statusUrl in build response")
                    return None
                
                logger.info(f"✅ LONG: Build started, status URL: {status_url}")
                
                # Step 2: Poll status
                max_attempts = 30  # 30 attempts * 3 seconds = 90 seconds max
                for attempt in range(max_attempts):
                    logger.info(f"🔄 LONG: Polling attempt {attempt + 1}/{max_attempts}")
                    
                    await httpx.AsyncClient().aclose()  # Small delay
                    import asyncio
                    await asyncio.sleep(3)  # Wait 3 seconds between polls
                    
                    # Poll status (NO API KEY needed for status URL)
                    status_response = await client.get(status_url)
                    
                    if status_response.status_code != 200:
                        logger.error(f"❌ LONG: Status check failed: {status_response.status_code}")
                        continue
                    
                    status_data = status_response.json()
                    logger.info(f"📊 LONG: Status: {status_data}")
                    
                    if status_data.get("finished"):
                        result_url = status_data.get("result")
                        if result_url:
                            logger.info(f"✅ LONG: Build finished! Download URL: {result_url}")
                            
                            # Step 3: Download audio (NO API KEY needed)
                            download_response = await client.get(result_url)
                            
                            if download_response.status_code == 200:
                                audio_content = download_response.content
                                logger.info(f"✅ LONG: Audio downloaded! Size: {len(audio_content)} bytes")
                                return audio_content
                            else:
                                logger.error(f"❌ LONG: Download failed: {download_response.status_code}")
                                return None
                        else:
                            logger.error("❌ LONG: No result URL in finished status")
                            return None
                    
                    if status_data.get("failed"):
                        logger.error(f"❌ LONG: Build failed: {status_data}")
                        return None
                
                logger.error("⏰ LONG: Polling timeout - build took too long")
                return None
                
        except Exception as e:
            logger.error(f"💥 LONG API error: {e}")
            import traceback
            logger.error(f"📚 LONG Full traceback: {traceback.format_exc()}")
            return None


narakeet_service = NarakeetService()