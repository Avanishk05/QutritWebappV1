"""GET /api/v1/images/status — Background download progress tracking."""

from fastapi import APIRouter
from agent.services.image_manager import get_download_status

router = APIRouter()

@router.get("/images/status")
async def check_image_downloads() -> dict:
    """Return the progress of background firmware parsing and downloading."""
    return get_download_status()
