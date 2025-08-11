import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.oauth2 import service_account


class FirestoreService:
    """Service for interacting with Google Cloud Firestore"""
    
    def __init__(self):
        self.collection_name = "itineraries"
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Firestore client with service account credentials"""
        # Try to get credentials from environment variable (JSON string)
        credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if credentials_json:
            try:
                # Parse JSON credentials from environment variable
                credentials_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                self.db = firestore.Client(credentials=credentials)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid GOOGLE_APPLICATION_CREDENTIALS_JSON format: {e}")
        else:
            # Try to use default credentials or service account key file
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.db = firestore.Client.from_service_account_json(credentials_path)
            else:
                # Use default credentials (when running on Google Cloud)
                try:
                    self.db = firestore.Client()
                except Exception as e:
                    raise ValueError(
                        "Firestore credentials not found. Please set either:\n"
                        "1. GOOGLE_APPLICATION_CREDENTIALS_JSON (service account JSON as string), or\n"
                        "2. GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON file)"
                    )
    
    async def create_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Create a new document in the itineraries collection"""
        def _create_doc():
            # Convert datetime objects to Firestore timestamps
            processed_data = self._prepare_data_for_firestore(data)
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc_ref.set(processed_data)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_doc)
    
    async def update_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Update an existing document in the itineraries collection"""
        def _update_doc():
            # Convert datetime objects to Firestore timestamps
            processed_data = self._prepare_data_for_firestore(data)
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc_ref.update(processed_data)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _update_doc)
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document from the itineraries collection"""
        def _get_doc():
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, _get_doc)
        return result
    
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
    
    def _prepare_data_for_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python datetime objects to Firestore-compatible format"""
        processed_data = {}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                # Convert datetime to Firestore timestamp
                processed_data[key] = value
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                processed_data[key] = self._prepare_data_for_firestore(value)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries
                processed_data[key] = [
                    self._prepare_data_for_firestore(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                processed_data[key] = value
        
        return processed_data 