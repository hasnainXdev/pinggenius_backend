"""
Data privacy and GDPR compliance utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from database.mongo import mongodb
from config.settings import settings
import logging


def schedule_data_cleanup(days_to_retain: int = 30):
    """
    Schedule automatic cleanup of data older than specified days
    Implements data minimization by automatically deleting old records
    """
    try:
        db = mongodb.get_database()

        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_retain)

        # Delete old profile records
        result_profiles = db.profiles.delete_many(
            {"created_at": {"$lt": cutoff_date.isoformat()}}
        )

        # Delete old sequence records
        result_sequences = db.sequences.delete_many(
            {"created_at": {"$lt": cutoff_date.isoformat()}}
        )

        logging.info(
            f"Data cleanup completed: {result_profiles.deleted_count} profiles and {result_sequences.deleted_count} sequences deleted"
        )

    except Exception as e:
        logging.error(f"Error during data cleanup: {e}")


def anonymize_user_data(user_identifier: str):
    """
    Anonymize user data based on identifier
    """
    try:
        db = mongodb.get_database()

        # Update profile records to anonymize user data
        db.profiles.update_many(
            {"url": {"$regex": user_identifier}},
            {
                "$set": {
                    "role": "Anonymized",
                    "company": "Anonymized",
                    "industry": "Anonymized",
                    "recent_activity": "Anonymized",
                }
            },
        )

        logging.info(f"User data anonymized for identifier: {user_identifier}")

    except Exception as e:
        logging.error(f"Error during data anonymization: {e}")


def user_data_removal_request(user_identifier: str):
    """
    Process a user request to delete their data
    """
    try:
        db = mongodb.get_database()

        # Delete profile records associated with the user
        result_profiles = db.profiles.delete_many({"url": {"$regex": user_identifier}})

        # Delete sequence records associated with the user's profiles
        # First get profile IDs to delete associated sequences
        profile_ids = [
            str(p["_id"])
            for p in db.profiles.find({"url": {"$regex": user_identifier}}, {"_id": 1})
        ]
        if profile_ids:
            result_sequences = db.sequences.delete_many(
                {"profile_id": {"$in": profile_ids}}
            )
        else:
            result_sequences = type("obj", (object,), {"deleted_count": 0})()

        logging.info(
            f"User data removal completed: {result_profiles.deleted_count} profiles and {result_sequences.deleted_count} sequences deleted for user: {user_identifier}"
        )

        return {
            "profiles_deleted": result_profiles.deleted_count,
            "sequences_deleted": result_sequences.deleted_count,
        }

    except Exception as e:
        logging.error(f"Error during user data removal: {e}")
        raise
