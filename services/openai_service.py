import json
import os
from typing import Dict, Any, List
import asyncio
import aiohttp
from datetime import datetime

from models import DayItinerary, Activity


class OpenAIService:
    """Service for interacting with OpenAI API to generate travel itineraries"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def _create_prompt(self, destination: str, duration_days: int) -> str:
        """Create a detailed prompt for the OpenAI API"""
        return f"""
        Create a detailed travel itinerary for a {duration_days}-day trip to {destination}.

        Return the response as a valid JSON object with the following structure:
        {{
            "itinerary": [
                {{
                    "day": 1,
                    "theme": "Theme of the day",
                    "activities": [
                        {{
                            "time": "Morning",
                            "description": "Detailed activity description with practical tips",
                            "location": "Specific location name"
                        }},
                        {{
                            "time": "Afternoon", 
                            "description": "Detailed activity description with practical tips",
                            "location": "Specific location name"
                        }},
                        {{
                            "time": "Evening",
                            "description": "Detailed activity description with practical tips", 
                            "location": "Specific location name"
                        }}
                    ]
                }}
            ]
        }}

        Guidelines:
        - Each day should have a clear theme (e.g., "Historical Sites", "Cultural Immersion", "Nature & Adventure")
        - Include 3 activities per day: Morning, Afternoon, and Evening
        - Provide specific location names, not just general areas
        - Include practical tips in descriptions (e.g., "Pre-book tickets", "Best visited early morning")
        - Make activities realistic and achievable within the time slots
        - Consider travel time between locations
        - Include a mix of must-see attractions, cultural experiences, and local cuisine
        - Ensure the itinerary flows logically from day to day

        IMPORTANT: Return ONLY the JSON object, no additional text or formatting.
        """
    
    async def generate_itinerary(self, destination: str, duration_days: int) -> List[DayItinerary]:
        """
        Generate a travel itinerary using OpenAI API with retry logic
        """
        prompt = self._create_prompt(destination, duration_days)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional travel planner. Generate detailed, practical travel itineraries in the exact JSON format requested."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            content = result["choices"][0]["message"]["content"].strip()
                            
                            # Parse the JSON response
                            try:
                                itinerary_data = json.loads(content)
                                return self._parse_itinerary(itinerary_data["itinerary"])
                            except (json.JSONDecodeError, KeyError) as e:
                                raise ValueError(f"Invalid JSON response from OpenAI: {e}")
                        
                        elif response.status == 429:  # Rate limit
                            if attempt < self.max_retries - 1:
                                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise Exception("Rate limit exceeded after all retries")
                        
                        else:
                            error_text = await response.text()
                            raise Exception(f"OpenAI API error {response.status}: {error_text}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception("Request timeout after all retries")
            
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Network error after all retries: {e}")
        
        raise Exception("Failed to generate itinerary after all retries")
    
    def _parse_itinerary(self, itinerary_data: List[Dict[str, Any]]) -> List[DayItinerary]:
        """Parse and validate the itinerary data from OpenAI response"""
        parsed_itinerary = []
        
        for day_data in itinerary_data:
            try:
                activities = [
                    Activity(
                        time=activity["time"],
                        description=activity["description"],
                        location=activity["location"]
                    )
                    for activity in day_data["activities"]
                ]
                
                day_itinerary = DayItinerary(
                    day=day_data["day"],
                    theme=day_data["theme"],
                    activities=activities
                )
                
                parsed_itinerary.append(day_itinerary)
                
            except (KeyError, TypeError) as e:
                raise ValueError(f"Invalid itinerary structure for day {day_data.get('day', 'unknown')}: {e}")
        
        return parsed_itinerary 