from fastapi import APIRouter
from api.v1 import profile, outreach

# Main API v1 router
api_v1_router = APIRouter()

# Include all v1 API routes
api_v1_router.include_router(profile.router, prefix="/profile", tags=["profile-v1"])
api_v1_router.include_router(outreach.router, prefix="/outreach", tags=["outreach-v1"])