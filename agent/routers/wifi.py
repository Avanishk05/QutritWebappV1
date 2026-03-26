"""POST /api/v1/wifi — Configure WiFi via ADB.

Accepts SSID and password from the web UI form.
Runs adb shell command to write wpa_supplicant.conf and reboot.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent.models.schemas import ErrorResponse, WifiConfig, WifiResponse
from agent.services.wifi_configurator import AdbExecutionError, AdbNotFoundError, configure_wifi

router = APIRouter()


@router.post(
    "/wifi",
    response_model=WifiResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "ADB execution failed"},
        503: {"model": ErrorResponse, "description": "ADB tool not found"},
    },
)
async def set_wifi_credentials(config: WifiConfig) -> WifiResponse | JSONResponse:
    """Configure WiFi on the recently flashed Luckfox board via ADB."""
    try:
        # Pydantic (WifiConfig) validates length, configure_wifi sanitizes shell input
        success = await configure_wifi(config.ssid, config.password)
        
        return WifiResponse(
            message="WiFi credentials written. Device is rebooting.",
            success=success,
        )

    except ValueError as e:
        # E.g., sanitize_input raised ValueError for forbidden characters
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e),
                "code": "INVALID_WIFI_CREDENTIALS",
            },
        )
    except AdbNotFoundError as e:
        return JSONResponse(
            status_code=503,
            content={
                "error": str(e),
                "code": "ADB_NOT_FOUND",
            },
        )
    except AdbExecutionError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to apply WiFi configuration: {e}",
                "code": "WIFI_CONFIG_FAILED",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Unexpected error while configuring WiFi: {e}",
                "code": "UNKNOWN_ERROR",
            },
        )
