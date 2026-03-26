"""GET /api/v1/status — Agent health check endpoint.

Returns: { status, version, platform, tools_ready }
"""

from fastapi import APIRouter

from agent.config import APP_VERSION, get_platform_info, is_rkdev_bundle_complete
from agent.models.schemas import StatusResponse

router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
)
async def health_check() -> StatusResponse:
    """Check agent health and tool readiness.

    Returns:
        StatusResponse containing version info, OS, and tool bundle availability.
    """
    platform_data = get_platform_info()
    os_descriptor = f"{platform_data['os']} ({platform_data['arch']})"

    return StatusResponse(
        status="running",
        version=APP_VERSION,
        platform=os_descriptor,
        tools_ready=is_rkdev_bundle_complete(),
    )
