# Travel Itinerary Generator

A FastAPI-based application that generates personalized travel itineraries using OpenAI's GPT models and stores them in MongoDB. Features a beautiful Streamlit interface for checking job status and viewing completed itineraries.

## Features

- **Async Itinerary Generation**: Uses OpenAI GPT-4o with background processing
- **MongoDB Database**: Local NoSQL database for data persistence
- **Streamlit Interface**: Beautiful web UI for checking job status
- **Docker Support**: Full containerization with Docker Compose
- **Virtual Environment**: Easy local development setup
- **Input Validation**: Comprehensive request and response validation
- **Error Handling**: Robust retry logic and error management

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate to project
cd travel-itinerary-generator

# 2. Set your OpenAI API key
export OPENAI_API_KEY="your_openai_api_key_here"

# 3. Start everything with Docker Compose
docker-compose up -d

# 4. Access the applications
# API: http://localhost:8000
# Streamlit UI: http://localhost:8501
# MongoDB: localhost:27017
```

### Option 2: Local Development

```bash
# 1. Set up virtual environment
./setup_venv.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Set up environment variables
cp env.local .env
# Edit .env file with your OpenAI API key

# 4. Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 5. Run the API
python main.py

# 6. Run Streamlit interface (in another terminal)
streamlit run streamlit_app.py
```

## Architecture

### Core Components

```
travel-itinerary-generator/
├── main.py                     # FastAPI application
├── streamlit_app.py           # Streamlit web interface
├── models.py                  # Pydantic data models
├── services/
│   ├── mongodb_service.py     # MongoDB operations
│   ├── openai_service.py      # OpenAI API integration
│   └── itinerary_generator.py # Business logic coordination
├── docker-compose.yml         # Multi-container setup
├── Dockerfile                 # API container
├── Dockerfile.streamlit       # UI container
└── setup_venv.sh             # Development setup
```

### Data Flow

1. **Submit Request**: User sends POST to `/generate-itinerary`
2. **Immediate Response**: API returns unique job ID (202 Accepted)
3. **Background Processing**: OpenAI generates itinerary asynchronously
4. **Data Storage**: Results saved to MongoDB with status updates
5. **Status Checking**: Streamlit UI or CLI tools query job status
6. **Display Results**: Completed itineraries shown in beautiful interface

## API Endpoints

### Generate Itinerary
```http
POST /generate-itinerary
Content-Type: application/json

{
  "destination": "Tokyo, Japan",
  "durationDays": 5
}
```

**Response (202 Accepted):**
```json
{
  "jobId": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Check Job Status
```http
GET /job-status/{job_id}
```

**Response:**
```json
{
  "status": "completed",
  "destination": "Tokyo, Japan",
  "durationDays": 5,
  "createdAt": "2023-12-01T10:00:00",
  "completedAt": "2023-12-01T10:02:30",
  "itinerary": [...],
  "error": null
}
```

### Health Check
```http
GET /health
```

## Streamlit Interface

The Streamlit web interface provides:

- **Job Status Checking**: Enter job ID to see real-time status
- **Auto-refresh**: Automatic updates every 5 seconds
- **Beautiful Display**: Color-coded status and formatted itineraries
- **Download Option**: Export itineraries as JSON files
- **API Health Check**: Monitor backend service status

### Screenshots

**Main Interface:**
- Clean, modern design with travel theme
- Single input field for job ID
- Real-time status updates

**Completed Itinerary Display:**
- Day-by-day breakdown with themes
- Morning/Afternoon/Evening activities
- Location and description details
- Download functionality

## Environment Variables

Create a `.env` file with:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults shown)
MONGODB_URI=mongodb://localhost:27017/travel_itinerary_db
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## Database Schema

MongoDB stores documents in the `itineraries` collection:

```javascript
{
  "_id": "job-uuid",
  "jobId": "job-uuid",
  "status": "completed|processing|failed",
  "destination": "Paris, France",
  "durationDays": 3,
  "createdAt": "2023-12-01T10:00:00.000Z",
  "completedAt": "2023-12-01T10:02:30.000Z",
  "itinerary": [
    {
      "day": 1,
      "theme": "Historical Paris",
      "activities": [
        {
          "time": "Morning",
          "description": "Visit the Louvre Museum. Pre-book tickets to avoid queues.",
          "location": "Louvre Museum"
        }
      ]
    }
  ],
  "error": null
}
```

## Development Setup

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized setup)
- OpenAI API key

### Local Development Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd travel-itinerary-generator
   ```

2. **Set Up Virtual Environment**
   ```bash
   ./setup_venv.sh
   source venv/bin/activate
   ```

3. **Configure Environment**
   ```bash
   cp env.local .env
   # Edit .env with your OpenAI API key
   ```

4. **Start MongoDB**
   ```bash
   # Option A: Docker
   docker run -d -p 27017:27017 --name mongodb mongo:7.0
   
   # Option B: Local installation
   # Follow MongoDB installation guide for your OS
   ```

5. **Run Services**
   ```bash
   # Terminal 1: API
   python main.py
   
   # Terminal 2: Streamlit UI
   streamlit run streamlit_app.py
   ```

6. **Test Setup**
   ```bash
   python test_setup.py
   python check_job_status.py --test
   ```

## Docker Deployment

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Individual Containers

```bash
# API only
docker build -t travel-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key travel-api

# Streamlit UI only
docker build -f Dockerfile.streamlit -t travel-ui .
docker run -p 8501:8501 travel-ui
```

## Testing

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Generate itinerary
curl -X POST http://localhost:8000/generate-itinerary \
     -H "Content-Type: application/json" \
     -d '{"destination": "Paris, France", "durationDays": 3}'

# Check status (replace with actual job ID)
curl http://localhost:8000/job-status/your-job-id-here
```

### Test Streamlit Interface

1. Open http://localhost:8501
2. Enter job ID: `sample-job-id-123`
3. Click "Check Status"
4. View the sample itinerary

### Test Job Status CLI

```bash
# Test with sample data
python check_job_status.py --test

# Test with real job ID
python check_job_status.py your-job-id-here
```

## Troubleshooting

### Common Issues

**"MongoDB connection failed"**
- Ensure MongoDB is running on port 27017
- Check MONGODB_URI in environment variables
- For Docker: `docker run -d -p 27017:27017 mongo:7.0`

**"OpenAI API rate limit exceeded"**
- Check your OpenAI usage limits and billing
- Ensure API key is valid
- The app includes retry logic for temporary limits

**"Cannot connect to API"**
- Verify FastAPI is running on port 8000
- Check for port conflicts
- Ensure virtual environment is activated

**Streamlit interface shows errors**
- Ensure API is running before starting Streamlit
- Check API_BASE_URL in streamlit_app.py
- Verify MongoDB is accessible

### Logs and Debugging

```bash
# View application logs
python main.py

# Docker logs
docker-compose logs api
docker-compose logs streamlit
docker-compose logs mongodb

# Test connectivity
python -c "from services.mongodb_service import MongoDBService; import asyncio; asyncio.run(MongoDBService().test_connection())"
```

## Performance & Scaling

### Current Configuration

- **FastAPI**: Async framework for high concurrency
- **MongoDB**: Indexed for fast queries
- **Background Tasks**: Non-blocking itinerary generation
- **Docker**: Easy horizontal scaling

### Optimization Tips

1. **Database Indexing**: Indexes on status, createdAt, destination
2. **Connection Pooling**: MongoDB connection reuse
3. **Caching**: Consider Redis for frequent destinations
4. **Rate Limiting**: Implement client rate limiting if needed

## Cost Estimates

**OpenAI API:**
- GPT-4o: ~$0.03-0.15 per itinerary
- Varies by destination complexity and trip length

**Infrastructure (Local):**
- MongoDB: Free
- FastAPI: Free
- Streamlit: Free

**Total Cost Per Itinerary: $0.03-0.15**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Set up development environment with `./setup_venv.sh`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Security Considerations

- OpenAI API key stored in environment variables
- No API keys in code or logs
- Docker containers run as non-root users
- Input validation with Pydantic models
- MongoDB connection strings configurable

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run `python test_setup.py` to verify setup
3. Check logs for specific error messages
4. Review MongoDB and FastAPI documentation

---

**Happy Travel Planning!** ✈️ 