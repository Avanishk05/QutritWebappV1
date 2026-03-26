"""Application configuration.

Resolves paths to all tools, images, and directories.
All paths via pathlib.Path. Environment variable overrides supported.
Detection order for tools: bundled path → PATH → download.
"""

import os
import platform
import shutil
from pathlib import Path


import sys

# ---------------------------------------------------------------------------
# Project root: works for both pyinstaller and dev uvicorn
# ---------------------------------------------------------------------------
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    PROJECT_ROOT: Path = Path(sys.executable).parent
else:
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_VERSION: str = "0.1.0"
APP_NAME: str = "Luckfox Device Flasher"

# ---------------------------------------------------------------------------
# Server configuration
# ---------------------------------------------------------------------------
HOST: str = os.environ.get("AGENT_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("AGENT_PORT", "5001"))

# ---------------------------------------------------------------------------
# CORS allowed origins
# ---------------------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    "http://localhost:*",
    "http://127.0.0.1:*",
    "https://yourusername.github.io",  # placeholder — update before deploy
]

# ---------------------------------------------------------------------------
# Flash image paths (img/ folder — Downloaded dynamically or cached)
# ---------------------------------------------------------------------------
IMAGE_BASE_URL: str = "https://github.com/YOURNAME/YOURREPO/releases/download/v1.0.0/"

IMG_DIR: Path = PROJECT_ROOT / "img"
MINILOADER_PATH: Path = IMG_DIR / "MiniLoaderAll.bin"
PARAMETER_PATH: Path = IMG_DIR / "parameter.txt"
UBOOT_PATH: Path = IMG_DIR / "uboot.img"
BOOT_PATH: Path = IMG_DIR / "boot.img"
ROOTFS_PATH: Path = IMG_DIR / "ExportImage.img"

REQUIRED_IMAGES: list[Path] = [
    MINILOADER_PATH,
    PARAMETER_PATH,
    UBOOT_PATH,
    BOOT_PATH,
    ROOTFS_PATH,
]

IMAGE_DOWNLOAD_URLS: dict[str, str] = {
    "MiniLoaderAll.bin": IMAGE_BASE_URL + "MiniLoaderAll.bin",
    "parameter.txt": IMAGE_BASE_URL + "parameter.txt",
    "uboot.img": IMAGE_BASE_URL + "uboot.img",
    "boot.img": IMAGE_BASE_URL + "boot.img",
    "ExportImage.img": IMAGE_BASE_URL + "ExportImage.img",
}

# ---------------------------------------------------------------------------
# Partition-to-image mapping (name in parameter.txt → file path)
# ---------------------------------------------------------------------------
PARTITION_IMAGE_MAP: dict[str, Path] = {
    "uboot": UBOOT_PATH,
    "boot": BOOT_PATH,
    "rootfs": ROOTFS_PATH,
}

# ---------------------------------------------------------------------------
# Log configuration
# ---------------------------------------------------------------------------
LOG_DIR: Path = PROJECT_ROOT / "agent" / "logs"
FLASH_LOG_PATH: Path = LOG_DIR / "flash.log"
FLASH_LOCK_PATH: Path = LOG_DIR / "flash.lock"


# ---------------------------------------------------------------------------
# Tool resolution helpers
# ---------------------------------------------------------------------------

def _find_tool(bundled_path: Path, tool_name: str) -> Path | None:
    """Resolve a tool binary using detection order.

    1. Bundled path (relative to PROJECT_ROOT)
    2. System PATH lookup
    3. Returns None if not found (caller handles download)

    Args:
        bundled_path: Expected path relative to PROJECT_ROOT.
        tool_name: Executable name to search in PATH as fallback.

    Returns:
        Resolved Path to the tool, or None if not found anywhere.
    """
    # 1. Bundled path
    absolute_path = PROJECT_ROOT / bundled_path
    if absolute_path.is_file():
        return absolute_path

    # 2. System PATH
    path_result = shutil.which(tool_name)
    if path_result is not None:
        return Path(path_result)

    # 3. Not found
    return None


# ---------------------------------------------------------------------------
# rkdeveloptool — CLI flash tool
# ---------------------------------------------------------------------------
# Required files for the rkdeveloptool bundle (must ALL be present)
RKDEV_TOOL_BUNDLE: list[str] = [
    "rkdeveloptool.exe",
    "libusb-1.0.dll",
    "msvcp140.dll",
    "vcruntime140.dll",
]

RKDEV_TOOL_DIR: Path = PROJECT_ROOT / "tools" / "bin"

# GitHub source for auto-download
RKDEV_TOOL_DOWNLOAD_BASE: str = (
    "https://raw.githubusercontent.com/cpebit/rkdeveloptool-bin/master/bin"
)


def get_rkdeveloptool_path() -> Path | None:
    """Resolve the path to rkdeveloptool.exe.

    Detection order:
        1. tools/bin/rkdeveloptool.exe  (bundled)
        2. System PATH
        3. None (caller should trigger download)

    Returns:
        Path to rkdeveloptool.exe, or None if not found.
    """
    return _find_tool(
        Path("tools") / "bin" / "rkdeveloptool.exe",
        "rkdeveloptool.exe",
    )


def is_rkdev_bundle_complete() -> bool:
    """Check if all 4 rkdeveloptool bundle files are present.

    Returns:
        True if rkdeveloptool.exe AND all 3 required DLLs exist.
    """
    return all((RKDEV_TOOL_DIR / fname).is_file() for fname in RKDEV_TOOL_BUNDLE)


# ---------------------------------------------------------------------------
# ADB — Android Debug Bridge
# ---------------------------------------------------------------------------

def get_adb_path() -> Path | None:
    """Resolve the path to adb.exe.

    Detection order:
        1. tools/DriverAssitant_v5.13/ADBDriver/adb.exe  (bundled)
        2. System PATH
        3. None (caller should trigger download)

    Returns:
        Path to adb.exe, or None if not found.
    """
    return _find_tool(
        Path("tools") / "DriverAssitant_v5.13" / "ADBDriver" / "adb.exe",
        "adb.exe",
    )


# ---------------------------------------------------------------------------
# USB Driver Installer
# ---------------------------------------------------------------------------
DRIVER_INSTALL_PATH: Path = (
    PROJECT_ROOT / "tools" / "DriverAssitant_v5.13" / "DriverInstall.exe"
)


def get_driver_install_path() -> Path | None:
    """Resolve the path to DriverInstall.exe.

    Returns:
        Path to DriverInstall.exe, or None if not found.
    """
    if DRIVER_INSTALL_PATH.is_file():
        return DRIVER_INSTALL_PATH
    return None


# ---------------------------------------------------------------------------
# Subprocess configuration
# ---------------------------------------------------------------------------
SUBPROCESS_TIMEOUT_DEVICE: int = 10     # seconds — device detection
SUBPROCESS_TIMEOUT_FLASH: int = 600     # seconds — flash write (large images)
SUBPROCESS_TIMEOUT_ADB: int = 30        # seconds — ADB commands

# Allowed executables for subprocess (security allowlist)
ALLOWED_EXECUTABLES: set[str] = {
    "rkdeveloptool.exe",
    "adb.exe",
    "DriverInstall.exe",
}


# ---------------------------------------------------------------------------
# Platform info
# ---------------------------------------------------------------------------

def get_platform_info() -> dict[str, str]:
    """Return current platform information.

    Returns:
        Dict with os, arch, and python version.
    """
    return {
        "os": platform.system(),
        "arch": platform.machine(),
        "python": platform.python_version(),
    }
