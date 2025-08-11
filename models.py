from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    """Request model for travel itinerary generation"""
    destination: str = Field(..., description="Travel destination (e.g., 'Tokyo, Japan')")
    durationDays: int = Field(..., gt=0, le=30, description="Duration of trip in days (1-30)")


class JobResponse(BaseModel):
    """Response model containing the job ID"""
    jobId: str = Field(..., description="Unique identifier for the itinerary generation job")


class Activity(BaseModel):
    """Individual activity within a day"""
    time: str = Field(..., description="Time of day (e.g., 'Morning', 'Afternoon', 'Evening')")
    description: str = Field(..., description="Detailed description of the activity")
    location: str = Field(..., description="Location where the activity takes place")


class DayItinerary(BaseModel):
    """Itinerary for a single day"""
    day: int = Field(..., ge=1, description="Day number of the trip")
    theme: str = Field(..., description="Theme or focus of the day")
    activities: List[Activity] = Field(..., description="List of activities for the day")


class ItineraryData(BaseModel):
    """Complete itinerary data structure stored in Firestore"""
    status: Literal["processing", "completed", "failed"] = Field(..., description="Current status of the job")
    destination: str = Field(..., description="Travel destination")
    durationDays: int = Field(..., description="Duration of trip in days")
    createdAt: datetime = Field(..., description="Timestamp when the job was created")
    completedAt: Optional[datetime] = Field(None, description="Timestamp when the job was completed")
    itinerary: List[DayItinerary] = Field(default=[], description="Generated travel itinerary")
    error: Optional[str] = Field(None, description="Error message if status is 'failed'")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        } 