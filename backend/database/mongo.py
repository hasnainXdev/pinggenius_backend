from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from config.settings import settings


class MongoDB:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        if self.database is not None:
            return
        try:
            self.client = AsyncIOMotorClient(settings.mongo_url)
            self.database = self.client[settings.mongodb_database]
            logging.info(f"Connected to MongoDB: {settings.mongo_url}/{settings.mongodb_database}")
            await self._create_indexes()
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self):
        if self.client:
            self.client.close()
            logging.info("Disconnected from MongoDB")

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.database

    async def _create_indexes(self):
        try:
            await self.database["profiles"].create_index("url", unique=True)
            await self.database["profiles"].create_index("created_at")
            await self.database["sequences"].create_index("profile_id")
            await self.database["sequences"].create_index("created_at")
            logging.info("Database indexes created successfully")
        except Exception as e:
            logging.error(f"Failed to create database indexes: {e}")


mongodb = MongoDB()


async def get_db() -> AsyncIOMotorDatabase:
    await mongodb.connect()
    return mongodb.get_database()
