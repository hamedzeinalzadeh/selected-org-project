// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

print("Starting MongoDB initialization...");

// Switch to the travel itinerary database
db = db.getSiblingDB('travel_itinerary_db');

// Create the itineraries collection with indexes
db.createCollection('itineraries');

// Create indexes for better performance
db.itineraries.createIndex({ "_id": 1 }, { unique: true });
db.itineraries.createIndex({ "status": 1 });
db.itineraries.createIndex({ "createdAt": 1 });
db.itineraries.createIndex({ "destination": 1 });

print("Created itineraries collection with indexes");

// Insert a sample document for testing (optional)
db.itineraries.insertOne({
    "_id": "sample-job-id-123",
    "jobId": "sample-job-id-123",
    "status": "completed",
    "destination": "Sample City",
    "durationDays": 2,
    "createdAt": new Date().toISOString(),
    "completedAt": new Date().toISOString(),
    "itinerary": [
        {
            "day": 1,
            "theme": "Sample Day",
            "activities": [
                {
                    "time": "Morning",
                    "description": "Sample morning activity",
                    "location": "Sample Location"
                },
                {
                    "time": "Afternoon", 
                    "description": "Sample afternoon activity",
                    "location": "Sample Location 2"
                },
                {
                    "time": "Evening",
                    "description": "Sample evening activity",
                    "location": "Sample Location 3"
                }
            ]
        }
    ],
    "error": null
});

print("Inserted sample document for testing");
print("MongoDB initialization completed successfully!"); 