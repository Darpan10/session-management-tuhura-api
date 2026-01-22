from fastapi import APIRouter
from config import Settings

router = APIRouter(prefix="/api/config", tags=["config"])

settings = Settings()

@router.get("/google-maps-key")
async def get_google_maps_key():
    """Get Google Maps API key for frontend use - No authentication required"""
    return {"apiKey": settings.google_maps_api_key}
