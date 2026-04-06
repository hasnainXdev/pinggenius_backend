"""
MongoDB indexes setup for the PingGenius application
"""
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo import get_db
from pymongo import ASCENDING
import logging


def create_indexes():
    """
    Create indexes for MongoDB collections as specified in the data model
    """
    try:
        db = get_db()

        # LinkedInProfile indexes
        # Index on URL for efficient lookup
        db.profiles.create_index(
            [("url", ASCENDING)], unique=True, name="profiles_url_unique_index"
        )
        logging.info("Created unique index on profiles.url")

        # Index on created_at for time-based queries
        db.profiles.create_index(
            [("created_at", ASCENDING)], name="profiles_created_at_index"
        )
        logging.info("Created index on profiles.created_at")

        # OutreachSequence indexes
        # Index on profile_id for efficient profile-to-sequence lookups
        db.sequences.create_index(
            [("profile_id", ASCENDING)], name="sequences_profile_id_index"
        )
        logging.info("Created index on sequences.profile_id")

        # Index on created_at for time-based queries
        db.sequences.create_index(
            [("created_at", ASCENDING)], name="sequences_created_at_index"
        )
        logging.info("Created index on sequences.created_at")

        # Index on tone for filtering by tone
        db.sequences.create_index([("tone", ASCENDING)], name="sequences_tone_index")
        logging.info("Created index on sequences.tone")

        # Index on status for filtering by sequence status
        db.sequences.create_index(
            [("status", ASCENDING)], name="sequences_status_index"
        )
        logging.info("Created index on sequences.status")

        print("All indexes created successfully!")

    except Exception as e:
        logging.error(f"Error creating indexes: {e}")
        raise


if __name__ == "__main__":
    # Connect to MongoDB
    mongodb.connect()

    # Create indexes
    create_indexes()

    # Disconnect
    mongodb.disconnect()
