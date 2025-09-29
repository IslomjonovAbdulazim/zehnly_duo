import os
import httpx
from typing import Optional


class NarakeetService:
    def __init__(self):
        self.api_key = os.getenv("NARAKEET")
        self.base_url = "https://api.narakeet.com"
    
    async def generate_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        if not self.api_key:
            return None
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "text/plain"
        }
        
        params = {"voice": voice} if voice else {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/mp3",
                    headers=headers,
                    params=params,
                    content=text
                )
                
                if response.status_code == 200:
                    return response.content
                return None
        except Exception:
            return None


narakeet_service = NarakeetService()