"""
Test script to verify environment setup and dependencies
Run this script to check if all required components are properly configured.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✓ aiohttp imported successfully")
    except ImportError as e:
        print(f"✗ aiohttp import failed: {e}")
        return False
    
    try:
        import motor
        print("✓ Motor (async MongoDB driver) imported successfully")
    except ImportError as e:
        print(f"✗ Motor import failed: {e}")
        return False
    
    try:
        import pymongo
        print("✓ PyMongo imported successfully")
    except ImportError as e:
        print(f"✗ PyMongo import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        from models import TravelRequest, JobResponse, ItineraryData
        print("✓ Local models imported successfully")
    except ImportError as e:
        print(f"✗ Local models import failed: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\nTesting environment variables...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✓ OPENAI_API_KEY is set")
    else:
        print("✗ OPENAI_API_KEY is not set")
        return False
    
    # Check MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/travel_itinerary_db")
    print(f"✓ MONGODB_URI: {mongodb_uri}")
    
    return True

async def test_services():
    """Test if services can be initialized"""
    print("\nTesting service initialization...")
    
    try:
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()
        print("✓ OpenAI service initialized successfully")
    except Exception as e:
        print(f"✗ OpenAI service initialization failed: {e}")
        return False
    
    try:
        from services.mongodb_service import MongoDBService
        mongodb_service = MongoDBService()
        print("✓ MongoDB service initialized successfully")
        
        # Test MongoDB connection
        connection_ok = await mongodb_service.test_connection()
        if connection_ok:
            print("✓ MongoDB connection test successful")
        else:
            print("✗ MongoDB connection test failed")
            print("  Make sure MongoDB is running: docker run -d -p 27017:27017 mongo:7.0")
            return False
        
    except Exception as e:
        print(f"✗ MongoDB service initialization failed: {e}")
        print("  Make sure MongoDB is running: docker run -d -p 27017:27017 mongo:7.0")
        return False
    
    try:
        from services.itinerary_generator import ItineraryGenerator
        generator = ItineraryGenerator(openai_service, mongodb_service)
        print("✓ Itinerary generator initialized successfully")
    except Exception as e:
        print(f"✗ Itinerary generator initialization failed: {e}")
        return False
    
    # Cleanup
    try:
        await mongodb_service.close_connection()
        print("✓ MongoDB connection closed successfully")
    except Exception as e:
        print(f"⚠ Warning: Failed to close MongoDB connection: {e}")
    
    return True

def test_models():
    """Test Pydantic models"""
    print("\nTesting data models...")
    
    try:
        from models import TravelRequest, JobResponse, ItineraryData, Activity, DayItinerary
        
        # Test TravelRequest
        request = TravelRequest(destination="Tokyo, Japan", durationDays=3)
        print("✓ TravelRequest model works")
        
        # Test JobResponse
        response = JobResponse(jobId="test-job-id")
        print("✓ JobResponse model works")
        
        # Test Activity
        activity = Activity(
            time="Morning",
            description="Visit the Louvre Museum",
            location="Louvre Museum"
        )
        print("✓ Activity model works")
        
        # Test DayItinerary
        day = DayItinerary(
            day=1,
            theme="Historical Paris",
            activities=[activity]
        )
        print("✓ DayItinerary model works")
        
        # Test ItineraryData
        itinerary_data = ItineraryData(
            status="processing",
            destination="Paris, France",
            durationDays=3,
            createdAt=datetime.utcnow(),
            completedAt=None,
            itinerary=[day],
            error=None
        )
        print("✓ ItineraryData model works")
        
    except Exception as e:
        print(f"✗ Model validation failed: {e}")
        return False
    
    return True

def test_docker_availability():
    """Test if Docker is available (optional)"""
    print("\nTesting Docker availability (optional)...")
    
    try:
        import subprocess
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Docker is available: {result.stdout.strip()}")
            return True
        else:
            print("✗ Docker command failed")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Docker command timed out")
        return False
    except FileNotFoundError:
        print("✗ Docker is not installed")
        return False
    except Exception as e:
        print(f"✗ Error checking Docker: {e}")
        return False

async def test_api_endpoints():
    """Test if the main application can start (quick test)"""
    print("\nTesting FastAPI application startup...")
    
    try:
        # Import the main app
        from main import app
        print("✓ FastAPI application imported successfully")
        
        # Test if we can create the app instance
        if app:
            print("✓ FastAPI application created successfully")
            return True
        else:
            print("✗ FastAPI application is None")
            return False
            
    except Exception as e:
        print(f"✗ FastAPI application startup test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Starting environment setup verification...\n")
    print("=" * 60)
    print("TRAVEL ITINERARY GENERATOR - SETUP VERIFICATION")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_imports(),
        test_environment_variables(),
        await test_services(),
        test_models(),
        test_docker_availability(),
        await test_api_endpoints()
    ]
    
    # Summary
    print("\n" + "="*60)
    print("SETUP VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for test in tests if test)
    total = len(tests)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Start MongoDB:")
        print("   docker run -d -p 27017:27017 --name mongodb mongo:7.0")
        print("\n2. Run the API:")
        print("   python main.py")
        print("\n3. Run the Streamlit interface (in another terminal):")
        print("   streamlit run streamlit_app.py")
        print("\n4. Test with sample data:")
        print("   python check_job_status.py --test")
        print("\n🌐 Application URLs:")
        print("   API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("   Streamlit UI: http://localhost:8501")
    else:
        print(f"❌ {total - passed} test(s) failed out of {total}")
        print("\nPlease fix the issues above before running the application.")
        print("\n💡 Common solutions:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Set OpenAI API key: export OPENAI_API_KEY='your_key_here'")
        print("- Start MongoDB: docker run -d -p 27017:27017 mongo:7.0")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 