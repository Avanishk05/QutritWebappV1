"""Flash endpoints.

POST /api/v1/flash — Launch flash.py as background task, return 202.
GET  /api/v1/logs  — Return last 200 lines of flash log + progress + status.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent.models.schemas import ErrorResponse, FlashResponse, FlashStatus, LogResponse
from agent.services.flasher import get_flash_status, start_flash
from agent.services.image_manager import get_missing_images, verify_images_present

router = APIRouter()


@router.post(
    "/flash",
    response_model=FlashResponse,
    status_code=202,
    responses={
        409: {"model": ErrorResponse, "description": "Flash already in progress"},
        422: {"model": ErrorResponse, "description": "Missing flash images"},
    },
)
async def trigger_flash() -> FlashResponse | JSONResponse:
    """Trigger the asynchronous flash process."""
    # 1. Validate images
    if not verify_images_present():
        missing = get_missing_images()
        return JSONResponse(
            status_code=422,
            content={
                "error": f"Missing required OS images: {', '.join(missing)}. Please ensure all files are in the img folder.",
                "code": "MISSING_IMAGES",
            },
        )
        
    # 2. Attempt to start flash
    started = await start_flash()
    if not started:
        return JSONResponse(
            status_code=409,
            content={
                "error": "A flash operation is already in progress.",
                "code": "FLASH_IN_PROGRESS",
            },
        )
        
    # 3. Success
    return FlashResponse(
        message="Flash started successfully in the background.",
        status=FlashStatus.RUNNING,
    )


@router.get(
    "/logs",
    response_model=LogResponse,
)
async def get_logs() -> LogResponse:
    """Get real-time log streaming for the active flash session.
    
    Returns the current state, progress bar percentage, and the trailing
    log output from rkdeveloptool.
    """
    status_dict = get_flash_status()
    return LogResponse(**status_dict)
