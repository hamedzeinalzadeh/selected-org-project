import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Travel Itinerary Status Checker",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E88E5;
    text-align: center;
    margin-bottom: 2rem;
}
.status-processing {
    color: #FF9800;
    font-weight: bold;
}
.status-completed {
    color: #4CAF50;
    font-weight: bold;
}
.status-failed {
    color: #F44336;
    font-weight: bold;
}
.itinerary-day {
    background-color: #f8f9fa;
    border-left: 4px solid #1E88E5;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 8px 8px 0;
}
.activity-card {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">✈️ Travel Itinerary Status Checker</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.write("Check the status of your travel itinerary generation jobs.")
        st.write("Enter your Job ID to see the current status and view completed itineraries.")
        
        st.header("🔗 API Endpoints")
        st.code(f"{API_BASE_URL}/generate-itinerary")
        st.code(f"{API_BASE_URL}/job-status/{{job_id}}")
        
        # Health check
        if st.button("🏥 Check API Health"):
            check_api_health()
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Enter Job ID")
        job_id = st.text_input(
            "Job ID", 
            placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000",
            help="Enter the Job ID you received when requesting an itinerary"
        )
        
        col_check, col_auto = st.columns(2)
        
        with col_check:
            check_button = st.button("🔍 Check Status", use_container_width=True)
        
        with col_auto:
            auto_refresh = st.checkbox("🔄 Auto-refresh (5s)")
    
    # Auto-refresh logic
    if auto_refresh and job_id:
        # Create placeholder for dynamic content
        placeholder = st.empty()
        
        # Auto-refresh every 5 seconds
        while auto_refresh:
            with placeholder.container():
                display_job_status(job_id)
            time.sleep(5)
            st.rerun()
    
    # Manual check
    elif check_button and job_id:
        display_job_status(job_id)
    
    elif job_id and not check_button:
        st.info("👆 Click 'Check Status' to view the job details")
    
    # Example section
    if not job_id:
        st.markdown("---")
        st.subheader("🚀 How to Generate an Itinerary")
        
        st.write("**Step 1**: Send a POST request to generate an itinerary")
        
        example_request = {
            "destination": "Paris, France",
            "durationDays": 3
        }
        
        st.code(f"""
curl -X POST "{API_BASE_URL}/generate-itinerary" \\
     -H "Content-Type: application/json" \\
     -d '{json.dumps(example_request, indent=2)}'
        """, language="bash")
        
        st.write("**Step 2**: Copy the Job ID from the response")
        st.code('{"jobId": "123e4567-e89b-12d3-a456-426614174000"}', language="json")
        
        st.write("**Step 3**: Use the Job ID above to check status")

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.success(f"✅ API is healthy - Database: {health_data.get('database', 'Unknown')}")
        else:
            st.error(f"❌ API returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
    except Exception as e:
        st.error(f"❌ Error checking API health: {str(e)}")

def display_job_status(job_id: str):
    """Display the job status and itinerary if available"""
    try:
        response = requests.get(f"{API_BASE_URL}/job-status/{job_id}", timeout=10)
        
        if response.status_code == 404:
            st.error("❌ Job ID not found. Please check if the ID is correct.")
            return
        elif response.status_code != 200:
            st.error(f"❌ API error: {response.status_code}")
            return
        
        data = response.json()
        
        # Job info header
        st.subheader("📊 Job Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Destination", data.get("destination", "N/A"))
        
        with col2:
            st.metric("Duration", f"{data.get('durationDays', 0)} days")
        
        with col3:
            created_at = data.get("createdAt", "")
            if created_at:
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                st.metric("Created", created_time.strftime("%Y-%m-%d %H:%M"))
        
        # Status
        status = data.get("status", "unknown")
        st.subheader("📈 Status")
        
        if status == "processing":
            st.markdown('<p class="status-processing">🔄 PROCESSING</p>', unsafe_allow_html=True)
            st.info("Your itinerary is being generated. This usually takes 1-3 minutes.")
            
            # Progress bar simulation
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            st.write("💡 Tip: Enable auto-refresh to see updates automatically")
            
        elif status == "completed":
            completed_at = data.get("completedAt", "")
            if completed_at:
                completed_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                st.markdown(f'<p class="status-completed">✅ COMPLETED at {completed_time.strftime("%Y-%m-%d %H:%M")}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-completed">✅ COMPLETED</p>', unsafe_allow_html=True)
            
            # Display itinerary
            display_itinerary(data.get("itinerary", []))
            
        elif status == "failed":
            st.markdown('<p class="status-failed">❌ FAILED</p>', unsafe_allow_html=True)
            error_msg = data.get("error", "Unknown error occurred")
            st.error(f"Error: {error_msg}")
            
        else:
            st.warning(f"Unknown status: {status}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. The API might be busy processing your request.")
    except Exception as e:
        st.error(f"❌ Error fetching job status: {str(e)}")

def display_itinerary(itinerary_data):
    """Display the complete itinerary"""
    if not itinerary_data:
        st.warning("No itinerary data available")
        return
    
    st.subheader("🗺️ Your Travel Itinerary")
    
    # Download button
    itinerary_json = json.dumps(itinerary_data, indent=2, default=str)
    st.download_button(
        label="📥 Download Itinerary (JSON)",
        data=itinerary_json,
        file_name=f"itinerary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )
    
    # Display each day
    for day_data in itinerary_data:
        day_num = day_data.get("day", "?")
        theme = day_data.get("theme", "No theme")
        activities = day_data.get("activities", [])
        
        st.markdown(f"""
        <div class="itinerary-day">
            <h3>📅 Day {day_num}: {theme}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Display activities for this day
        for activity in activities:
            time_slot = activity.get("time", "Unknown time")
            description = activity.get("description", "No description")
            location = activity.get("location", "No location")
            
            # Activity icon
            icon = {"Morning": "🌅", "Afternoon": "☀️", "Evening": "🌙"}.get(time_slot, "🕐")
            
            st.markdown(f"""
            <div class="activity-card">
                <h4>{icon} {time_slot}</h4>
                <p><strong>📍 Location:</strong> {location}</p>
                <p><strong>📝 Activity:</strong> {description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")

if __name__ == "__main__":
    main() 