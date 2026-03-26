"""GET /api/v1/device — Device detection endpoint.

Runs rkdeveloptool.exe ld, validates VID/PID (0x2207).
Returns DeviceInfo or 404.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent.models.schemas import DeviceInfo, ErrorResponse
from agent.services.device_detector import ToolNotFoundError, detect_maskrom_device

router = APIRouter()


@router.get(
    "/device",
    response_model=DeviceInfo,
    responses={
        404: {"model": ErrorResponse, "description": "Device not found"},
        500: {"model": ErrorResponse, "description": "Tool execution failed"},
    },
)
async def check_device() -> DeviceInfo | JSONResponse:
    """Check for connected Rockchip devices in MaskROM mode."""
    try:
        device_info = await detect_maskrom_device()
        
        if not device_info.connected:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No device found. Please connect your Luckfox board in MaskROM mode.",
                    "code": "DEVICE_NOT_FOUND",
                },
            )
        
        return device_info

    except ToolNotFoundError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "code": "TOOL_NOT_FOUND",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Device detection failed: {e}",
                "code": "DETECTION_FAILED",
            },
        )
