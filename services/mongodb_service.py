import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service for interacting with MongoDB database"""
    
    def __init__(self):
        self.collection_name = "itineraries"
        self.database_name = "travel_itinerary_db"
        self.client = None
        self.db = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MongoDB client"""
        # Get MongoDB connection string from environment variable
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        try:
            self.client = AsyncIOMotorClient(mongodb_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"MongoDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise ValueError(f"MongoDB connection failed: {e}")
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            await self.client.admin.command('ping')
            logger.info("MongoDB connection test successful")
            return True
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection test failed: {e}")
            return False
    
    async def create_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Create a new document in the itineraries collection"""
        try:
            # Add the document ID to the data
            data["_id"] = document_id
            data["jobId"] = document_id
            
            # Convert datetime objects to ISO format strings for MongoDB
            processed_data = self._prepare_data_for_mongodb(data)
            
            result = await self.collection.insert_one(processed_data)
            logger.info(f"Document created with ID: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"Failed to create document {document_id}: {e}")
            raise
    
    async def update_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Update an existing document in the itineraries collection"""
        try:
            # Convert datetime objects to ISO format strings for MongoDB
            processed_data = self._prepare_data_for_mongodb(data)
            
            result = await self.collection.update_one(
                {"_id": document_id},
                {"$set": processed_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"No document found with ID: {document_id}")
            else:
                logger.info(f"Document updated: {document_id}")
                
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document from the itineraries collection"""
        try:
            document = await self.collection.find_one({"_id": document_id})
            
            if document:
                # Convert ISO format strings back to datetime objects
                document = self._process_data_from_mongodb(document)
                logger.info(f"Document retrieved: {document_id}")
                return document
            else:
                logger.info(f"Document not found: {document_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            raise
    
    async def mark_as_completed(self, document_id: str, itinerary_data: list) -> None:
        """Mark a document as completed with the generated itinerary"""
        update_data = {
            "status": "completed",
            "completedAt": datetime.utcnow(),
            "itinerary": [item.dict() if hasattr(item, 'dict') else item for item in itinerary_data],
            "error": None
        }
        await self.update_document(document_id, update_data)
    
    async def mark_as_failed(self, document_id: str, error_message: str) -> None:
        """Mark a document as failed with an error message"""
        update_data = {
            "status": "failed",
            "completedAt": datetime.utcnow(),
            "error": error_message
        }
        await self.update_document(document_id, update_data)
    
    async def get_all_documents(self, limit: int = 100) -> list:
        """Get all documents (for debugging/admin purposes)"""
        try:
            cursor = self.collection.find().limit(limit).sort("createdAt", -1)
            documents = []
            async for document in cursor:
                documents.append(self._process_data_from_mongodb(document))
            return documents
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            raise
    
    def _prepare_data_for_mongodb(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python datetime objects to MongoDB-compatible format"""
        processed_data = {}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                # Convert datetime to ISO format string
                processed_data[key] = value.isoformat()
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                processed_data[key] = self._prepare_data_for_mongodb(value)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries
                processed_data[key] = [
                    self._prepare_data_for_mongodb(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                processed_data[key] = value
        
        return processed_data
    
    def _process_data_from_mongodb(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document back to Python objects"""
        processed_data = {}
        
        for key, value in data.items():
            if key == "_id" and key != "jobId":
                # Skip MongoDB's _id field unless it's our jobId
                continue
            elif isinstance(value, str) and self._is_iso_datetime(value):
                # Convert ISO format string back to datetime
                try:
                    processed_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    processed_data[key] = value
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                processed_data[key] = self._process_data_from_mongodb(value)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries
                processed_data[key] = [
                    self._process_data_from_mongodb(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                processed_data[key] = value
        
        return processed_data
    
    def _is_iso_datetime(self, value: str) -> bool:
        """Check if a string is in ISO datetime format"""
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    async def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed") 