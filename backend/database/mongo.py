from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import logging
from config.settings import settings


class MongoDB:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None

    def connect(self):
        if self.database is not None:
            return
        try:
            self.client = MongoClient(settings.mongo_url)
            self.database = self.client[settings.mongodb_database]
            logging.info(f"Connected to MongoDB: {settings.mongo_url}/{settings.mongodb_database}")
            self._create_indexes()
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self):
        if self.client:
            self.client.close()
            logging.info("Disconnected from MongoDB")

    def get_database(self) -> Database:
        if self.database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.database

    def _create_indexes(self):
        try:
            self.database["profiles"].create_index("url", unique=True)
            self.database["profiles"].create_index("created_at")
            self.database["sequences"].create_index("profile_id")
            self.database["sequences"].create_index("created_at")
            logging.info("Database indexes created successfully")
        except Exception as e:
            logging.error(f"Failed to create database indexes: {e}")


mongodb = MongoDB()


def get_db():
    mongodb.connect()
    return mongodb.get_database()
