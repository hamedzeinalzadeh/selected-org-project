import asyncio
import logging
from typing import List

from models import DayItinerary
from services.openai_service import OpenAIService
from services.mongodb_service import MongoDBService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItineraryGenerator:
    """Service that coordinates itinerary generation and storage"""
    
    def __init__(self, openai_service: OpenAIService, mongodb_service: MongoDBService):
        self.openai_service = openai_service
        self.mongodb_service = mongodb_service
    
    async def generate_and_save_itinerary(
        self, 
        job_id: str, 
        destination: str, 
        duration_days: int
    ) -> None:
        """
        Generate an itinerary using OpenAI and save it to MongoDB.
        This method handles the entire async workflow including error handling.
        """
        try:
            logger.info(f"Starting itinerary generation for job {job_id}")
            
            # Generate itinerary using OpenAI
            itinerary = await self.openai_service.generate_itinerary(destination, duration_days)
            
            # Validate the generated itinerary
            self._validate_itinerary(itinerary, duration_days)
            
            # Save completed itinerary to MongoDB
            await self.mongodb_service.mark_as_completed(job_id, itinerary)
            
            logger.info(f"Successfully completed itinerary generation for job {job_id}")
            
        except Exception as e:
            error_message = f"Failed to generate itinerary: {str(e)}"
            logger.error(f"Error for job {job_id}: {error_message}")
            
            # Mark as failed in MongoDB
            try:
                await self.mongodb_service.mark_as_failed(job_id, error_message)
            except Exception as mongodb_error:
                logger.error(f"Failed to update MongoDB with error status for job {job_id}: {mongodb_error}")
    
    def _validate_itinerary(self, itinerary: List[DayItinerary], expected_days: int) -> None:
        """
        Validate the generated itinerary structure and content
        """
        if not itinerary:
            raise ValueError("Generated itinerary is empty")
        
        if len(itinerary) != expected_days:
            raise ValueError(f"Expected {expected_days} days, but got {len(itinerary)} days")
        
        # Validate each day
        for i, day in enumerate(itinerary, 1):
            if day.day != i:
                raise ValueError(f"Day numbering mismatch: expected day {i}, got day {day.day}")
            
            if not day.theme or not day.theme.strip():
                raise ValueError(f"Day {i} is missing a theme")
            
            if not day.activities:
                raise ValueError(f"Day {i} has no activities")
            
            # Validate activities
            required_times = {"Morning", "Afternoon", "Evening"}
            activity_times = {activity.time for activity in day.activities}
            
            if not required_times.issubset(activity_times):
                missing_times = required_times - activity_times
                raise ValueError(f"Day {i} is missing activities for: {', '.join(missing_times)}")
            
            # Validate each activity
            for activity in day.activities:
                if not activity.description or not activity.description.strip():
                    raise ValueError(f"Day {i}, {activity.time} activity is missing description")
                
                if not activity.location or not activity.location.strip():
                    raise ValueError(f"Day {i}, {activity.time} activity is missing location")
        
        logger.info(f"Itinerary validation passed: {len(itinerary)} days with all required fields") 