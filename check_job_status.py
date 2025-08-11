"""
Utility script to check the status of itinerary generation jobs
Works with the local MongoDB-based API
Usage: python check_job_status.py <job_id>
"""

import sys
import asyncio
import json
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"


def check_job_status(job_id: str):
    """Check the status of a specific job using the API"""
    try:
        print(f"Checking status for job ID: {job_id}")
        print("-" * 50)
        
        # Get the document from the API
        response = requests.get(f"{API_BASE_URL}/job-status/{job_id}", timeout=10)
        
        if response.status_code == 404:
            print(f"Job ID '{job_id}' not found in database.")
            return
        elif response.status_code != 200:
            print(f"API error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        document = response.json()
        
        # Display job information
        status = document.get("status", "unknown")
        destination = document.get("destination", "N/A")
        duration_days = document.get("durationDays", "N/A")
        created_at = document.get("createdAt", "N/A")
        completed_at = document.get("completedAt", "N/A")
        error = document.get("error")
        itinerary = document.get("itinerary", [])
        
        print(f"Status: {status.upper()}")
        print(f"Destination: {destination}")
        print(f"Duration: {duration_days} days")
        print(f"Created: {created_at}")
        
        if status == "processing":
            print("\nYour itinerary is still being generated. Please check back later.")
        
        elif status == "completed":
            print(f"Completed: {completed_at}")
            print(f"\nItinerary generated successfully with {len(itinerary)} days!")
            
            # Display summary of each day
            print("\nItinerary Summary:")
            for day_data in itinerary:
                day_num = day_data.get("day", "?")
                theme = day_data.get("theme", "No theme")
                activities = day_data.get("activities", [])
                print(f"  Day {day_num}: {theme} ({len(activities)} activities)")
        
        elif status == "failed":
            print(f"Completed: {completed_at}")
            print(f"\nItinerary generation failed.")
            if error:
                print(f"Error: {error}")
        
        else:
            print(f"\nUnknown status: {status}")
        
        # Option to display full itinerary
        if status == "completed" and itinerary:
            response = input("\nWould you like to see the full itinerary? (y/n): ").lower().strip()
            if response == 'y':
                print("\n" + "="*60)
                print("FULL ITINERARY")
                print("="*60)
                
                for day_data in itinerary:
                    day_num = day_data.get("day", "?")
                    theme = day_data.get("theme", "No theme")
                    activities = day_data.get("activities", [])
                    
                    print(f"\nDay {day_num}: {theme}")
                    print("-" * 30)
                    
                    for activity in activities:
                        time = activity.get("time", "N/A")
                        description = activity.get("description", "N/A")
                        location = activity.get("location", "N/A")
                        
                        print(f"\n{time}:")
                        print(f"  Location: {location}")
                        print(f"  Activity: {description}")
                
                # Option to save to file
                save_response = input("\nWould you like to save this itinerary to a file? (y/n): ").lower().strip()
                if save_response == 'y':
                    filename = f"itinerary_{job_id}_{destination.replace(', ', '_').replace(' ', '_')}.json"
                    with open(filename, 'w') as f:
                        json.dump(document, f, indent=2, default=str)
                    print(f"Itinerary saved to: {filename}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print(f"Make sure the FastAPI server is running at {API_BASE_URL}")
        print("Run: python main.py")
    except requests.exceptions.Timeout:
        print("❌ Request timeout. The API might be busy.")
    except Exception as e:
        print(f"Error checking job status: {e}")


def test_sample_job():
    """Test with the sample job created during MongoDB initialization"""
    sample_job_id = "sample-job-id-123"
    print("🧪 Testing with sample job...")
    check_job_status(sample_job_id)


def main():
    """Main function"""
    if len(sys.argv) == 1:
        print("Usage: python check_job_status.py <job_id>")
        print("Example: python check_job_status.py 123e4567-e89b-12d3-a456-426614174000")
        print("\nOr test with sample data:")
        print("python check_job_status.py --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        test_sample_job()
    else:
        job_id = sys.argv[1]
        check_job_status(job_id)


if __name__ == "__main__":
    main() 