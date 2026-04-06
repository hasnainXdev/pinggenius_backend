from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional, Dict, Any
import datetime
import hashlib
import json
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

            # Idempotency cache indexes
            idempotency_collection = self.database["idempotency_cache"]
            idempotency_collection.create_index(
                "key", unique=True
            )  # Unique index for idempotency keys
            idempotency_collection.create_index(
                [("expires_at", 1)], expireAfterSeconds=0
            )  # TTL index for automatic cleanup

            logging.info("Database indexes created successfully")
        except Exception as e:
            logging.error(f"Failed to create database indexes: {e}")

    def store_idempotency_result(self, key: str, result: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """
        Stores a result with an idempotency key to prevent duplicate processing.

        Args:
            key: The idempotency key
            result: The result to store
            ttl_seconds: Time-to-live for the cached result in seconds (default 1 hour)

        Returns:
            Boolean indicating success
        """
        try:
            idempotency_collection = self.database["idempotency_cache"]

            # Create document with expiration
            document = {
                "key": key,
                "result": result,
                "created_at": datetime.datetime.utcnow(),
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)
            }

            # Insert with upsert (update if exists, insert if not)
            result = idempotency_collection.replace_one(
                {"key": key},
                document,
                upsert=True
            )

            return result.acknowledged
        except Exception as e:
            logging.error(f"Failed to store idempotency result: {e}")
            return False

    def get_idempotency_result(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a result using an idempotency key.

        Args:
            key: The idempotency key

        Returns:
            The stored result if found, None otherwise
        """
        try:
            idempotency_collection = self.database["idempotency_cache"]
            document = idempotency_collection.find_one({"key": key})

            if document:
                return document["result"]
            return None
        except Exception as e:
            logging.error(f"Failed to get idempotency result: {e}")
            return None

    def check_idempotency_exists(self, key: str) -> bool:
        """
        Checks if an idempotency key already exists.

        Args:
            key: The idempotency key

        Returns:
            Boolean indicating if the key exists
        """
        try:
            idempotency_collection = self.database["idempotency_cache"]
            count = idempotency_collection.count_documents({"key": key})
            return count > 0
        except Exception as e:
            logging.error(f"Failed to check idempotency existence: {e}")
            return False

    def generate_idempotency_key(self, request_params: Dict[str, Any]) -> str:
        """
        Generates an idempotency key based on request parameters.

        Args:
            request_params: Dictionary of request parameters

        Returns:
            Generated idempotency key
        """
        # Convert params to JSON string and hash it
        params_str = json.dumps(request_params, sort_keys=True, default=str)
        key_hash = hashlib.sha256(params_str.encode()).hexdigest()
        return key_hash

    def get_cached_result_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a cached result using an idempotency key.

        Args:
            key: The idempotency key

        Returns:
            The stored result if found, None otherwise
        """
        try:
            idempotency_collection = self.database["idempotency_cache"]
            document = idempotency_collection.find_one({"key": key})

            if document:
                return document["result"]
            return None
        except Exception as e:
            logging.error(f"Failed to get cached result by idempotency key: {e}")
            return None

    def cache_result_with_idempotency_key(self, key: str, result: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """
        Caches a result with an idempotency key to prevent duplicate processing.

        Args:
            key: The idempotency key
            result: The result to cache
            ttl_seconds: Time-to-live for the cached result in seconds (default 1 hour)

        Returns:
            Boolean indicating success
        """
        try:
            idempotency_collection = self.database["idempotency_cache"]

            # Create document with expiration
            document = {
                "key": key,
                "result": result,
                "created_at": datetime.datetime.utcnow(),
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)
            }

            # Insert with upsert (update if exists, insert if not)
            result_op = idempotency_collection.replace_one(
                {"key": key},
                document,
                upsert=True
            )

            return result_op.acknowledged
        except Exception as e:
            logging.error(f"Failed to cache result with idempotency key: {e}")
            return False


# Singleton instance of MongoDB
mongodb = MongoDB()

# Helper function to get the database
def get_db():
    mongodb.connect()
    return mongodb.get_database()