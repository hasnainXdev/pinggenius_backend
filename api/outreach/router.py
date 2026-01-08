from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from services.sequence_generator import SequenceGeneratorService, Tone
from models.sequence import OutreachSequence
from models.profile import LinkedInProfile
from database.mongo import get_db
from bson import ObjectId
import logging

router = APIRouter()
sequence_service = SequenceGeneratorService()


class GenerateRequest(BaseModel):
    profile_id: str
    tone: Optional[Tone] = Tone.FRIENDLY


class RefineRequest(BaseModel):
    sequence_id: str
    message_position: int  # 1-4: connection_note, dm_1, follow_up_1, follow_up_2
    feedback: Optional[str] = None
    tone: Optional[Tone] = None


class SequenceResponse(BaseModel):
    id: Optional[str] = None
    profile_id: str
    connection_note: str
    dm_1: str
    follow_up_1: str
    follow_up_2: str
    tone: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("/generate", response_model=SequenceResponse)
async def generate_outreach_sequence(request: GenerateRequest):
    """
    Generate a complete LinkedIn outreach sequence based on profile context
    """
    try:
        # Fetch the profile from the database
        db = get_db()
        profile_data = db.profiles.find_one({"_id": ObjectId(request.profile_id)})

        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Profile not found",
                    "message": f"Profile with ID {request.profile_id} does not exist in the system",
                    "actionable_alternative": "Please analyze the LinkedIn profile first using the /profile/analyze endpoint",
                },
            )

        # Create a LinkedInProfile object from the database data
        profile_data["id"] = str(profile_data["_id"])
        profile_data.pop("_id")

        profile = LinkedInProfile(**profile_data)

        # Generate the outreach sequence
        sequence = await sequence_service.generate_sequence(profile, request.tone)

        # Store the sequence in the database
        result = db.sequences.insert_one(
            {
                **sequence.dict(),
                "profile_snapshot": {
                    "role": profile.role,
                    "company": profile.company,
                    "industry": profile.industry,
                },
            }
        )
        sequence.id = str(result.inserted_id)

        # Prepare the response
        response = SequenceResponse(
            id=sequence.id,
            profile_id=sequence.profile_id,
            connection_note=sequence.connection_note,
            dm_1=sequence.dm_1,
            follow_up_1=sequence.follow_up_1,
            follow_up_2=sequence.follow_up_2,
            tone=sequence.tone,
            created_at=sequence.created_at.isoformat(),
            updated_at=sequence.updated_at.isoformat(),
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error generating outreach sequence: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while generating the outreach sequence",
                "actionable_alternative": "Please try again later or contact support if the issue persists",
            },
        )


@router.post("/refine", response_model=SequenceResponse)
async def refine_outreach_sequence(request: RefineRequest):
    """
    Refine a specific message in an existing sequence based on feedback
    """
    try:
        # Fetch the sequence from the database
        db = get_db()
        sequence_data = db.sequences.find_one({"_id": ObjectId(request.sequence_id)})

        if not sequence_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Sequence not found",
                    "message": f"Sequence with ID {request.sequence_id} does not exist in the system",
                    "actionable_alternative": "Please generate a new sequence first or verify the sequence ID is correct",
                },
            )

        # Create an OutreachSequence object from the database data
        sequence = OutreachSequence(**sequence_data)

        # Fetch the profile for context
        profile_data = db.profiles.find_one({"_id": sequence.profile_id})
        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Profile not found",
                    "message": f"Profile with ID {sequence.profile_id} does not exist in the system",
                    "actionable_alternative": "The associated profile may have been deleted. Please analyze the profile again.",
                },
            )
        profile = LinkedInProfile(**profile_data)

        # Validate message position
        if request.message_position < 1 or request.message_position > 4:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid message position",
                    "message": f"Message position must be between 1 and 4, got {request.message_position}",
                    "actionable_alternative": "Use position 1 for connection_note, 2 for dm_1, 3 for follow_up_1, 4 for follow_up_2",
                },
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
        response = SequenceResponse(
            id=request.sequence_id,
            profile_id=refined_sequence.profile_id,
            connection_note=refined_sequence.connection_note,
            dm_1=refined_sequence.dm_1,
            follow_up_1=refined_sequence.follow_up_1,
            follow_up_2=refined_sequence.follow_up_2,
            tone=refined_sequence.tone,
            created_at=(
                sequence_data.get("created_at").isoformat()
                if sequence_data.get("created_at")
                else None
            ),
            updated_at=refined_sequence.updated_at.isoformat(),
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error refining outreach sequence: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while refining the outreach sequence",
                "actionable_alternative": "Please try again later or contact support if the issue persists",
            },
        )


@router.get("/{sequence_id}", response_model=SequenceResponse)
async def get_outreach_sequence(sequence_id: str):
    """
    Retrieve an existing outreach sequence by ID
    """
    try:
        # TODO: enforce ownership after auth is added

        # Fetch the sequence from the database
        db = get_db()
        sequence_data = db.sequences.find_one({"_id": ObjectId(sequence_id)})

        if not sequence_data:
            raise HTTPException(
                status_code=404, detail=f"Sequence with ID {sequence_id} not found"
            )

        # Prepare the response
        response = SequenceResponse(
            id=sequence_id,
            profile_id=sequence_data["profile_id"],
            connection_note=sequence_data["connection_note"],
            dm_1=sequence_data["dm_1"],
            follow_up_1=sequence_data["follow_up_1"],
            follow_up_2=sequence_data["follow_up_2"],
            tone=sequence_data["tone"],
            created_at=(
                sequence_data.get("created_at").isoformat()
                if sequence_data.get("created_at")
                else None
            ),
            updated_at=(
                sequence_data.get("updated_at").isoformat()
                if sequence_data.get("updated_at")
                else None
            ),
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error retrieving outreach sequence {sequence_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving outreach sequence",
        )
