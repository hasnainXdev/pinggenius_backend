from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.profile_scraper import ProfileService
from services.context_extractor import ContextExtractor
from models.profile import LinkedInProfile
from database.mongo import get_db
from utils.retry import retry_with_backoff
from typing import Optional
import logging

router = APIRouter()
profile_service = ProfileService()
context_extractor = ContextExtractor()


class ProfileAnalysisRequest(BaseModel):
    url: str
    role: str
    company: str
    industry: str
    pain_point: Optional[str] = None
    recent_signal: Optional[str] = None
    tone: str

class ProfileAnalysisResponse(BaseModel):
    id: Optional[str] = None
    url: str
    role: str
    company: str
    industry: str
    recent_activity: Optional[str] = None


@router.post("/analyze", response_model=ProfileAnalysisResponse)
async def analyze_linkedin_profile(request: ProfileAnalysisRequest):
    try:
        # Build profile directly from user input
        profile = LinkedInProfile(
            url=request.url,
            role=request.role,
            company=request.company,
            industry=request.industry or "Unknown",
            recent_activity=request.recent_signal,
        )

        # Extract message context
        context = context_extractor.extract_context(
            profile=profile
        )

        if not context_extractor.validate_context(context):
            logging.warning("Insufficient context but proceeding")

        db = get_db()
        result = db.profiles.insert_one({
            **profile.dict(),
            "tone": request.tone,
            "pain_point": request.pain_point or "",
            "context": context,
        })

        profile.id = str(result.inserted_id)

        return ProfileAnalysisResponse(
            id=profile.id,
            url=profile.url,
            role=profile.role,
            company=profile.company,
            industry=profile.industry,
            recent_activity=profile.recent_activity,
        )

    except Exception as e:
        logging.error(f"Analyze failed: {e}")
        raise HTTPException(status_code=500, detail="Generation failed")
