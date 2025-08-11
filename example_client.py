"""
Example client script demonstrating how to use the Travel Itinerary Generator API
"""

import asyncio
import aiohttp
import json
import time


async def generate_itinerary_example():
    """Example of how to call the API and check job status"""
    
    # API endpoint (adjust URL if running on different host/port)
    base_url = "http://localhost:8000"
    
    # Example request data
    request_data = {
        "destination": "Paris, France",
        "durationDays": 3
    }
    
    print("Travel Itinerary Generator API Example")
    print("=" * 40)
    print(f"Requesting itinerary for: {request_data['destination']}")
    print(f"Duration: {request_data['durationDays']} days")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Step 1: Submit itinerary generation request
            print("Step 1: Submitting itinerary generation request...")
            async with session.post(
                f"{base_url}/generate-itinerary",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 202:
                    result = await response.json()
                    job_id = result["jobId"]
                    print(f"✓ Request submitted successfully!")
                    print(f"✓ Job ID: {job_id}")
                    print(f"✓ Status: {response.status} Accepted")
                else:
                    error_text = await response.text()
                    print(f"✗ Request failed: {response.status}")
                    print(f"Error: {error_text}")
                    return
            
            print()
            print("Step 2: The itinerary is being generated in the background...")
            print("In a real application, you would:")
            print("- Store the job ID for later reference")
            print("- Check the status periodically or notify the user when complete")
            print("- Retrieve the completed itinerary from Firestore")
            
            print(f"\nTo check the status of this job, run:")
            print(f"python check_job_status.py {job_id}")
            
    except aiohttp.ClientConnectorError:
        print("✗ Could not connect to the API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"✗ Error: {e}")


async def test_health_endpoint():
    """Test the health check endpoint"""
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print("✓ Health check passed!")
                    print(f"Status: {result['status']}")
                    print(f"Timestamp: {result['timestamp']}")
                    return True
                else:
                    print(f"✗ Health check failed: {response.status}")
                    return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


async def main():
    """Main example function"""
    print("Testing API connection...")
    
    # Test health endpoint first
    if await test_health_endpoint():
        print("\n" + "-" * 50)
        
        # Run the itinerary generation example
        await generate_itinerary_example()
        
        print("\n" + "-" * 50)
        print("Example completed!")
        print("\nNext steps:")
        print("1. Use the job ID to check status with check_job_status.py")
        print("2. Check your Firestore database to see the stored data")
        print("3. Try different destinations and durations")
    else:
        print("\nCannot proceed - API server is not responding.")
        print("Please ensure the server is running with: python main.py")


if __name__ == "__main__":
    asyncio.run(main()) 