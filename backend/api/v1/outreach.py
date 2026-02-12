from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, validator
from typing import Optional, Union, Dict, Any
from services.sequence_generator import SequenceGeneratorService, VALID_TONES, TONE_FRIENDLY
from models.sequence import OutreachSequence
from models.profile import LinkedInProfile
from database.mongo import get_db
from bson import ObjectId
import logging

# Import validation components
from services.profile_validation import ProfileValidationService
from utils.validation import create_standard_error_response
from utils.logging import log_validation_failure

router = APIRouter()
sequence_service = SequenceGeneratorService()
profile_validation_service = ProfileValidationService()


class GenerateRequest(BaseModel):
    user_id: str  # ID of the user generating the sequence
    profile_id: str
    tone: Optional[str] = TONE_FRIENDLY
    
    @validator('tone', pre=True)
    def validate_and_convert_tone(cls, v):
        if isinstance(v, str):
            # Convert to proper case for comparison
            v_capitalized = v.capitalize() if len(v) > 0 else v
            # Handle different input formats
            if v.lower() == 'friendly':
                return TONE_FRIENDLY
            elif v.lower() == 'direct':
                return TONE_DIRECT
            elif v.lower() == 'authority':
                return TONE_AUTHORITY
            elif v.lower() == 'casual':
                return TONE_CASUAL
            elif v_capitalized in VALID_TONES:
                return v_capitalized
            else:
                raise ValueError(f"Tone must be one of {VALID_TONES}")
        return v


class RefineRequest(BaseModel):
    sequence_id: str
    message_position: int  # 1-4: connection_note, dm_1, follow_up_1, follow_up_2
    feedback: Optional[str] = None
    tone: Optional[str] = None
    
    @validator('tone', pre=True)
    def validate_and_convert_refine_tone(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            # Convert to proper case for comparison
            v_capitalized = v.capitalize() if len(v) > 0 else v
            # Handle different input formats
            if v.lower() == 'friendly':
                return TONE_FRIENDLY
            elif v.lower() == 'direct':
                return TONE_DIRECT
            elif v.lower() == 'authority':
                return TONE_AUTHORITY
            elif v.lower() == 'casual':
                return TONE_CASUAL
            elif v_capitalized in VALID_TONES:
                return v_capitalized
            else:
                raise ValueError(f"Tone must be one of {VALID_TONES}")
        return v


class SequenceResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    actionable_alternative: Optional[str] = None


@router.post("/generate",
             response_model=Union[SequenceResponse, ErrorResponse],
             responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_outreach_sequence(request: GenerateRequest):
    """
    Generate a complete LinkedIn outreach sequence based on profile context
    """
    try:
        # Fetch the profile from the database
        db = get_db()
        profile_data = db.profiles.find_one({"_id": ObjectId(request.profile_id)})

        if not profile_data:
            return ErrorResponse(
                error="Profile not found",
                message=f"Profile with ID {request.profile_id} does not exist in the system",
                actionable_alternative="Please analyze the LinkedIn profile first using the /profile/analyze endpoint",
            )

        # Create a LinkedInProfile object from the database data
        profile_data["id"] = str(profile_data["_id"])
        profile_data.pop("_id")

        profile = LinkedInProfile(**profile_data)

        # Validate the profile for outreach generation
        profile_validation_result = (
            profile_validation_service.validate_profile_completeness(profile.dict())
        )

        if not profile_validation_result.is_valid:
            # Log the validation failure
            log_validation_failure(profile.dict(), profile_validation_result.errors)

            # Create enhanced error response with actionable alternatives
            error_response = profile_validation_service.enhance_error_message(
                profile_validation_result, profile
            )

            return ErrorResponse(
                error="Validation failed",
                message=error_response.get("message", "Profile validation failed"),
                actionable_alternative=error_response.get("actionable_alternative")
            )

        # Generate the outreach sequence
        # The tone is already validated and converted to the proper format
        sequence = await sequence_service.generate_sequence(profile, request.tone)

        # Store the sequence in the database
        sequence_dict = sequence.dict()
        result = db.sequences.insert_one(
            {
                **sequence_dict,
                "user_id": request.user_id,  # Store the user ID with the sequence
                "profile_snapshot": {
                    "role": getattr(profile, "role", profile_data.get("role", "")),
                    "company": getattr(
                        profile, "company", profile_data.get("company", "")
                    ),
                    "industry": getattr(
                        profile, "industry", profile_data.get("industry", "")
                    ),
                },
            }
        )
        sequence.id = str(result.inserted_id)

        # Persist the sequence context if it's valuable
        if sequence_dict.get("sequence_context"):
            sequence_service.persist_sequence_context(
                sequence.id, {"_id": result.inserted_id, **sequence_dict}
            )

        # Prepare the response
        response_data = {
            "id": sequence.id,
            "profile_id": sequence.profile_id,
            "connection_note": sequence.connection_note,
            "dm_1": sequence.dm_1,
            "follow_up_1": sequence.follow_up_1,
            "follow_up_2": sequence.follow_up_2,
            "tone": sequence.tone,
            "predicted_reply_score": sequence.predicted_reply_score,
            "created_at": sequence.created_at.isoformat(),
            "updated_at": sequence.updated_at.isoformat(),
        }

        return SequenceResponse(data=response_data)

    except Exception as e:
        logging.error(f"Error generating outreach sequence: {e}")
        return ErrorResponse(
            error="Internal server error",
            message="An unexpected error occurred while generating the outreach sequence",
            actionable_alternative="Please try again later or contact support if the issue persists",
        )


@router.post("/refine",
             response_model=Union[SequenceResponse, ErrorResponse],
             responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def refine_outreach_sequence(request: RefineRequest):
    """
    Refine a specific message in an existing sequence based on feedback
    """
    try:
        # Fetch the sequence from the database
        db = get_db()
        sequence_data = db.sequences.find_one({"_id": ObjectId(request.sequence_id)})

        if not sequence_data:
            return ErrorResponse(
                error="Sequence not found",
                message=f"Sequence with ID {request.sequence_id} does not exist in the system",
                actionable_alternative="Please generate a new sequence first or verify the sequence ID is correct",
            )

        # Create an OutreachSequence object from the database data
        sequence = OutreachSequence(**sequence_data)

        # Fetch the profile for context
        profile_data = db.profiles.find_one({"_id": sequence.profile_id})
        if not profile_data:
            return ErrorResponse(
                error="Profile not found",
                message=f"Profile with ID {sequence.profile_id} does not exist in the system",
                actionable_alternative="The associated profile may have been deleted. Please analyze the profile again.",
            )
        profile = LinkedInProfile(**profile_data)

        # Validate message position
        if request.message_position < 1 or request.message_position > 4:
            return ErrorResponse(
                error="Invalid message position",
                message=f"Message position must be between 1 and 4, got {request.message_position}",
                actionable_alternative="Use position 1 for connection_note, 2 for dm_1, 3 for follow_up_1, 4 for follow_up_2",
            )

        # Refine the specific message
        refined_sequence = await sequence_service.refine_message(
            sequence, request.message_position, request.feedback, request.tone
        )

        # Update the sequence in the database
        db.sequences.update_one(
            {"_id": request.sequence_id},
            {
                "$set": {
                    "connection_note": refined_sequence.connection_note,
                    "dm_1": refined_sequence.dm_1,
                    "follow_up_1": refined_sequence.follow_up_1,
                    "follow_up_2": refined_sequence.follow_up_2,
                    "tone": refined_sequence.tone,
                    "status": refined_sequence.status,
                    "updated_at": refined_sequence.updated_at,
                }
            },
        )

        # Prepare the response
        response_data = {
            "id": request.sequence_id,
            "profile_id": refined_sequence.profile_id,
            "connection_note": refined_sequence.connection_note,
            "dm_1": refined_sequence.dm_1,
            "follow_up_1": refined_sequence.follow_up_1,
            "follow_up_2": refined_sequence.follow_up_2,
            "tone": refined_sequence.tone,
            "predicted_reply_score": sequence_data.get("predicted_reply_score", 0.0),  # Keep original score
            "created_at": (
                sequence_data.get("created_at").isoformat()
                if sequence_data.get("created_at")
                else None
            ),
            "updated_at": refined_sequence.updated_at.isoformat(),
        }

        return SequenceResponse(data=response_data)

    except Exception as e:
        logging.error(f"Error refining outreach sequence: {e}")
        return ErrorResponse(
            error="Internal server error",
            message="An unexpected error occurred while refining the outreach sequence",
            actionable_alternative="Please try again later or contact support if the issue persists",
        )


@router.get("/{sequence_id}",
            response_model=Union[SequenceResponse, ErrorResponse],
            responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_outreach_sequence(sequence_id: str, user_id: str = Query(None, alias="user_id")):
    """
    Retrieve an existing outreach sequence by ID
    """
    try:
        # TODO: enforce ownership after auth is added

        # Fetch the sequence from the database for the authenticated user
        # TODO: Replace with actual user ID from authentication when implemented
        db = get_db()
        # For now, checking for any sequence - in production, filter by user_id
        query_filter = {"_id": ObjectId(sequence_id)}
        if user_id:
            query_filter["user_id"] = user_id
        
        # For now, we'll just fetch by ID, but in the future we'll check ownership
        sequence_data = db.sequences.find_one(query_filter)

        if not sequence_data:
            return ErrorResponse(
                error="Not found",
                message=f"Sequence with ID {sequence_id} not found",
                actionable_alternative="Please check the sequence ID and try again"
            )

        # Prepare the response
        response_data = {
            "id": sequence_id,
            "profile_id": sequence_data["profile_id"],
            "connection_note": sequence_data["connection_note"],
            "dm_1": sequence_data["dm_1"],
            "follow_up_1": sequence_data["follow_up_1"],
            "follow_up_2": sequence_data["follow_up_2"],
            "tone": sequence_data["tone"],
            "predicted_reply_score": sequence_data.get("predicted_reply_score", 0.0),
            "created_at": (
                sequence_data.get("created_at").isoformat()
                if sequence_data.get("created_at")
                else None
            ),
            "updated_at": (
                sequence_data.get("updated_at").isoformat()
                if sequence_data.get("updated_at")
                else None
            ),
        }

        return SequenceResponse(data=response_data)

    except Exception as e:
        logging.error(f"Error retrieving outreach sequence {sequence_id}: {e}")
        return ErrorResponse(
            error="Internal server error",
            message="Internal server error while retrieving outreach sequence",
            actionable_alternative="Please try again later or contact support if the issue persists"
        )


@router.get("/",
            response_model=Union[SequenceResponse, ErrorResponse],
            responses={500: {"model": ErrorResponse}})
async def get_all_outreach_sequences(user_id: str = Query(None, alias="user_id")):
    """
    Retrieve all outreach sequences for a user
    """
    try:
        # TODO: enforce ownership after auth is added

        db = get_db()
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
            
        # For now, we'll filter by user_id if provided, otherwise return all
        # In production with proper auth, we'd get user_id from the authenticated session
        sequences_cursor = db.sequences.find(query_filter).sort("created_at", -1)  # Sort by newest first
        
        sequences_list = []
        for sequence_data in sequences_cursor:
            sequence_item = {
                "id": str(sequence_data["_id"]),
                "profile_id": sequence_data["profile_id"],
                "connection_note": sequence_data["connection_note"],
                "dm_1": sequence_data["dm_1"],
                "follow_up_1": sequence_data["follow_up_1"],
                "follow_up_2": sequence_data["follow_up_2"],
                "tone": sequence_data["tone"],
                "predicted_reply_score": sequence_data.get("predicted_reply_score", 0.0),
                "created_at": (
                    sequence_data.get("created_at").isoformat()
                    if sequence_data.get("created_at")
                    else None
                ),
                "updated_at": (
                    sequence_data.get("updated_at").isoformat()
                    if sequence_data.get("updated_at")
                    else None
                ),
            }
            sequences_list.append(sequence_item)

        return SequenceResponse(data={"sequences": sequences_list})

    except Exception as e:
        logging.error(f"Error retrieving all outreach sequences: {e}")
        return ErrorResponse(
            error="Internal server error",
            message="Internal server error while retrieving outreach sequences",
            actionable_alternative="Please try again later or contact support if the issue persists"
        )


