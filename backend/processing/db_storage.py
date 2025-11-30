from pymongo import MongoClient
import os
from datetime import datetime
from typing import Dict, Any, Optional

class MongoDBStorage:
    def __init__(self, connection_string: str = None, database_name: str = "clipsmart"):
        self.connection_string = connection_string or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        return self.client is not None and self.db is not None
    
    def log_processing_request(self, endpoint: str, content_data: Dict[str, Any], classification: Dict[str, bool], response_data: Dict[str, Any]) -> Optional[str]:
        if not self.is_connected():
            return None
        
        try:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "endpoint": endpoint,
                "content_preview": content_data.get("preview", ""),
                "content_length": content_data.get("length", 0),
                "classification": classification,
                "processing_success": response_data.get("status") != "error",
                "has_s3_storage": "s3_storage" in response_data,
                "has_latex_conversion": "latex_conversion" in response_data
            }
            
            result = self.db.processing_logs.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"MongoDB logging failed: {e}")
            return None
    
    def close(self):
        if self.client:
            self.client.close()