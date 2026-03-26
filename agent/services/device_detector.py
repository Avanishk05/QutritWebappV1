"""Device detection via rkdeveloptool.exe ld.

Runs subprocess, parses output, validates Rockchip VID 0x2207.
Returns DeviceInfo or raises appropriate error.
"""

import asyncio
import re

from agent.config import get_rkdeveloptool_path, SUBPROCESS_TIMEOUT_DEVICE
from agent.models.schemas import DeviceInfo


# Regex to parse the output of "rkdeveloptool.exe ld"
# Example output: "DevNo=1   Vid=0x2207,Pid=0x350d,LocationID=301   Maskrom"
_LD_OUTPUT_RE = re.compile(
    r"Vid=(0x[0-9a-fA-F]+),\s*Pid=(0x[0-9a-fA-F]+).*?(Maskrom|Loader)",
    re.IGNORECASE,
)

# Rockchip Vendor ID
ROCKCHIP_VID = "0x2207"

# TODO: confirm RK3506B MaskROM PID for Phase 2. Skipping PID filter for Phase 1.


class ToolNotFoundError(Exception):
    """Raised when rkdeveloptool.exe is not found."""
    pass


async def detect_maskrom_device() -> DeviceInfo:
    """Detect if a Rockchip device is connected in MaskROM mode.

    Runs `rkdeveloptool.exe ld` and checks for VID 0x2207.

    Returns:
        DeviceInfo object populated with current state.

    Raises:
        ToolNotFoundError: If rkdeveloptool.exe cannot be found.
        RuntimeError: If subprocess fails or times out.
    """
    tool_path = get_rkdeveloptool_path()
    if tool_path is None:
        raise ToolNotFoundError("rkdeveloptool.exe not found on system.")

    try:
        proc = await asyncio.create_subprocess_exec(
            str(tool_path),
            "ld",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), 
            timeout=SUBPROCESS_TIMEOUT_DEVICE
        )
    except asyncio.TimeoutError:
        raise RuntimeError("Timed out waiting for device detection.")
    except Exception as e:
        raise RuntimeError(f"Failed to execute rkdeveloptool: {e}")

    stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
    
    # "not found any devices!" is expected when nothing is connected.
    if proc.returncode != 0 or "not found any devices" in stdout.lower():
        return DeviceInfo(
            connected=False,
            maskrom=False,
        )

    # Parse output to find VID and PID
    match = _LD_OUTPUT_RE.search(stdout)
    if not match:
        # We got output but couldn't parse it
        return DeviceInfo(
            connected=False,
            maskrom=False,
        )

    vid, pid, mode = match.group(1).lower(), match.group(2).lower(), match.group(3).lower()

    if vid != ROCKCHIP_VID:
        # Not a Rockchip device
        return DeviceInfo(
            connected=False,
            maskrom=False,
            usb_vid=vid,
            usb_pid=pid,
        )

    return DeviceInfo(
        connected=True,
        maskrom=(mode == "maskrom"),
        usb_vid=vid,
        usb_pid=pid,
        # Defaulting chip value to RK3506B per RESUME.md
        chip="RK3506B",
    )
