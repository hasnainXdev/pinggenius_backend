from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import logging
from config.settings import settings


# MongoDB Connection and Index Management
class MongoDB:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None

    def connect(self):
        """Connect to MongoDB"""
        if self.database is not None:
            return
        try:
            self.client = MongoClient(settings.mongo_url)
            self.database = self.client[settings.mongodb_database]
            logging.info(
                f"Connected to MongoDB: {settings.mongo_url}/{settings.mongodb_database}"
            )

            # Create indexes as specified in the data model
            self._create_indexes()
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logging.info("Disconnected from MongoDB")

    def get_database(self) -> Database:
        """Get the database instance"""
        if self.database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.database

    def _create_indexes(self):
        """Create required indexes for collections"""
        try:
            # LinkedInProfile indexes
            profiles_collection = self.database["profiles"]
            profiles_collection.create_index(
                "url", unique=True
            )  # Unique index for efficient lookup
            profiles_collection.create_index(
                "created_at"
            )  # Index for time-based queries

            # OutreachSequence indexes
            sequences_collection = self.database["sequences"]
            sequences_collection.create_index(
                "profile_id"
            )  # Index for efficient profile-to-sequence lookups
            sequences_collection.create_index(
                "created_at"
            )  # Index for time-based queries

            logging.info("Database indexes created successfully")
        except Exception as e:
            logging.error(f"Failed to create database indexes: {e}")


# Singleton instance of MongoDB
mongodb = MongoDB()

# Helper function to get the database
def get_db():
    mongodb.connect()
    return mongodb.get_database()