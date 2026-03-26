"""WiFi configuration via ADB.

After flash + reboot, once ADB device is available, runs:
  adb shell "echo -e '...' > /etc/wpa_supplicant.conf && reboot"

SSID and password are sanitized before injection.
"""

import asyncio

from agent.config import SUBPROCESS_TIMEOUT_ADB, get_adb_path


class AdbNotFoundError(Exception):
    """Raised when adb.exe is not found."""
    pass


class AdbExecutionError(Exception):
    """Raised when an ADB command fails."""
    pass


def _sanitize_input(value: str) -> str:
    """Sanitize WiFi inputs to prevent remote shell injection.
    
    Rejects completely any value containing shell metacharacters.
    WPA2 passwords can theoretically contain these, but for this
    agent we enforce a strictly safe subset to avoid exploitation.
    """
    forbidden = ["'", "\"", "\\", "$", "`", ";", "&", "|", ">", "<", "\n", "\r"]
    if any(char in value for char in forbidden):
        raise ValueError("Invalid characters in SSID or password for security reasons.")
    return value


async def wait_for_adb_device(timeout: int = 60) -> bool:
    """Wait until an ADB device is connected and authorized.

    Args:
        timeout: Maximum time to wait in seconds.

    Returns:
        True if a device is found, False if timed out.
    """
    adb_path = get_adb_path()
    if not adb_path:
        raise AdbNotFoundError("adb.exe not found on system.")

    try:
        proc = await asyncio.create_subprocess_exec(
            str(adb_path),
            "wait-for-device",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode == 0
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except OSError:
            pass
        return False
    except Exception as e:
        raise AdbExecutionError(f"Failed to run adb wait-for-device: {e}")


async def configure_wifi(ssid: str, password: str) -> bool:
    """Configure WiFi on the connected device via ADB and reboot.

    Uses `adb shell` to write wpa_supplicant.conf.

    Args:
        ssid: WiFi network name.
        password: WiFi password.

    Returns:
        True if configuration command sent successfully.

    Raises:
        AdbNotFoundError: If adb.exe is not found.
        AdbExecutionError: If command fails to execute.
        ValueError: If inputs contain forbidden characters.
    """
    adb_path = get_adb_path()
    if not adb_path:
        raise AdbNotFoundError("adb.exe not found on system.")

    safe_ssid = _sanitize_input(ssid)
    safe_pass = _sanitize_input(password)

    # Format the wpa_supplicant.conf content exactly as required
    conf_content = (
        "ctrl_interface=/var/run/wpa_supplicant\\n"
        "update_config=1\\n"
        "network={\\n"
        f'  ssid="{safe_ssid}"\\n'
        f'  psk="{safe_pass}"\\n'
        "}"
    )

    # Construct the remote shell command
    remote_command = f"echo -e '{conf_content}' > /etc/wpa_supplicant.conf && reboot"

    try:
        proc = await asyncio.create_subprocess_exec(
            str(adb_path),
            "shell",
            remote_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), 
            timeout=SUBPROCESS_TIMEOUT_ADB
        )
        
        if proc.returncode != 0:
            err = stderr_bytes.decode('utf-8', errors='replace').strip()
            raise AdbExecutionError(f"ADB shell command failed (code {proc.returncode}): {err}")
            
        return True
        
    except asyncio.TimeoutError:
        raise AdbExecutionError("Timed out waiting for ADB shell command output.")
    except Exception as e:
        if isinstance(e, AdbExecutionError):
            raise
        raise AdbExecutionError(f"Failed to execute adb shell: {e}")
