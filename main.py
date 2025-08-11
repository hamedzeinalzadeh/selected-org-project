import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from models import TravelRequest, JobResponse, ItineraryData
from services.mongodb_service import MongoDBService
from services.openai_service import OpenAIService
from services.itinerary_generator import ItineraryGenerator

# Global services
mongodb_service = None
openai_service = None
itinerary_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongodb_service, openai_service, itinerary_generator
    
    # Initialize services
    mongodb_service = MongoDBService()
    openai_service = OpenAIService()
    itinerary_generator = ItineraryGenerator(openai_service, mongodb_service)
    
    # Test MongoDB connection
    if not await mongodb_service.test_connection():
        raise Exception("Failed to connect to MongoDB")
    
    print("✅ Application started successfully")
    print("✅ MongoDB connection established")
    
    yield
    
    # Shutdown
    if mongodb_service:
        await mongodb_service.close_connection()
    print("✅ Application shutdown complete")


app = FastAPI(
    title="Travel Itinerary Generator", 
    version="1.0.0",
    description="Generate personalized travel itineraries using AI",
    lifespan=lifespan
)


@app.post("/generate-itinerary", response_model=JobResponse, status_code=202)
async def generate_itinerary(
    request: TravelRequest, 
    background_tasks: BackgroundTasks
) -> JobResponse:
    """
    Generate a travel itinerary asynchronously.
    Returns a job ID immediately and processes the request in the background.
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Create initial document in MongoDB with "processing" status
        initial_data = ItineraryData(
            status="processing",
            destination=request.destination,
            durationDays=request.durationDays,
            createdAt=datetime.utcnow(),
            completedAt=None,
            itinerary=[],
            error=None
        )
        
        await mongodb_service.create_document(job_id, initial_data.dict())
        
        # Add background task for itinerary generation
        background_tasks.add_task(
            itinerary_generator.generate_and_save_itinerary,
            job_id,
            request.destination,
            request.durationDays
        )
        
        return JobResponse(jobId=job_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")


@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of an itinerary generation job.
    This endpoint is used by the Streamlit interface.
    """
    try:
        document = await mongodb_service.get_document(job_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Job ID not found")
        
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job status: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongodb_healthy = await mongodb_service.test_connection()
        
        return {
            "status": "healthy" if mongodb_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if mongodb_healthy else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Travel Itinerary Generator API",
        "version": "1.0.0",
        "database": "MongoDB",
        "endpoints": {
            "generate_itinerary": "POST /generate-itinerary",
            "job_status": "GET /job-status/{job_id}",
            "health": "GET /health"
        },
        "ui": {
            "streamlit_interface": "Run 'streamlit run streamlit_app.py' for web interface"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 