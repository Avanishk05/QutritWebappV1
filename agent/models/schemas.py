"""Pydantic v2 schema models for the Luckfox Flasher Agent API.

All API request/response bodies are validated through these models.
"""

from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FlashStatus(str, Enum):
    """Current flash operation status."""

    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class StatusResponse(BaseModel):
    """GET /api/v1/status response."""

    status: str = Field(
        ...,
        description="Agent status — always 'running' if reachable.",
        examples=["running"],
    )
    version: str = Field(
        ...,
        description="Agent version string.",
        examples=["0.1.0"],
    )
    platform: str = Field(
        ...,
        description="Operating system.",
        examples=["Windows"],
    )
    tools_ready: bool = Field(
        ...,
        description="True if rkdeveloptool.exe and all DLLs are present.",
    )


class DeviceInfo(BaseModel):
    """GET /api/v1/device response — detected Rockchip device."""

    connected: bool = Field(
        ...,
        description="True if a Rockchip device is connected in MaskROM mode.",
    )
    device_type: str = Field(
        default="luckfox_lyra_zero_w",
        description="Device model identifier.",
    )
    chip: str = Field(
        default="RK3506B",
        description="SoC chip identifier.",
    )
    maskrom: bool = Field(
        ...,
        description="True if device is in MaskROM mode.",
    )
    serial: str = Field(
        default="",
        description="Device serial number if available.",
    )
    usb_vid: str = Field(
        default="0x2207",
        description="USB Vendor ID.",
    )
    usb_pid: str = Field(
        default="",
        description="USB Product ID.",
    )


class FlashResponse(BaseModel):
    """POST /api/v1/flash response — flash initiated."""

    message: str = Field(
        ...,
        description="Human-readable status message.",
        examples=["Flash started"],
    )
    status: FlashStatus = Field(
        ...,
        description="Current flash status.",
    )


class LogResponse(BaseModel):
    """GET /api/v1/logs response — flash log state."""

    lines: list[str] = Field(
        default_factory=list,
        description="Last N lines of the flash log.",
    )
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Estimated progress percentage (0-100).",
    )
    status: FlashStatus = Field(
        default=FlashStatus.IDLE,
        description="Current flash status.",
    )
    current_step: int = Field(
        default=0,
        ge=0,
        le=6,
        description="Current step number (0-6).",
    )
    total_steps: int = Field(
        default=6,
        description="Total number of flash steps.",
    )


class PartitionInfo(BaseModel):
    """Parsed partition entry from parameter.txt."""

    name: str = Field(
        ...,
        description="Partition name (e.g. 'uboot', 'boot', 'rootfs').",
    )
    offset: str = Field(
        ...,
        description="Sector offset as hex string (e.g. '0x2000').",
    )
    offset_decimal: int = Field(
        ...,
        description="Sector offset as decimal integer.",
    )
    size: str = Field(
        ...,
        description="Partition size as hex string, or '-' for grow-to-fill.",
    )
    image_file: str = Field(
        default="",
        description="Filename of the image to write to this partition.",
    )


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class WifiConfig(BaseModel):
    """POST /api/v1/wifi request body."""

    ssid: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="WiFi network name (SSID).",
        examples=["MyHomeWiFi"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=63,
        description="WiFi password (WPA2-PSK, 8-63 characters).",
        examples=["MySecurePassword123"],
    )


class WifiResponse(BaseModel):
    """POST /api/v1/wifi response."""

    message: str = Field(
        ...,
        description="Human-readable result message.",
    )
    success: bool = Field(
        ...,
        description="True if WiFi was configured successfully.",
    )


# ---------------------------------------------------------------------------
# Error model
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error response for all API errors."""

    error: str = Field(
        ...,
        description="Human-readable error message (plain English, no stack traces).",
        examples=["No device found. Please connect your Luckfox board and try again."],
    )
    code: str = Field(
        default="UNKNOWN_ERROR",
        description="Machine-readable error code.",
        examples=["DEVICE_NOT_FOUND", "FLASH_IN_PROGRESS", "TOOL_NOT_FOUND"],
    )
