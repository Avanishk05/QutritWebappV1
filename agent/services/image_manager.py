"""Validate and manage flash images exist in img/ folder."""

import asyncio
import httpx
from pathlib import Path
from pydantic import BaseModel

from agent.config import REQUIRED_IMAGES, IMAGE_DOWNLOAD_URLS, IMG_DIR


class DownloadProgress(BaseModel):
    filename: str
    downloaded_bytes: int
    total_bytes: int
    progress_percent: int
    status: str  # "pending", "downloading", "done", "error"


# Global state strictly for the downloading loop
_download_state: dict[str, DownloadProgress] = {}


def verify_images_present() -> bool:
    """Check if all required flash images are present on disk."""
    return len(get_missing_images()) == 0


def get_missing_images() -> list[str]:
    """Return a list of missing required flash image names."""
    missing: list[str] = []
    for img_path in REQUIRED_IMAGES:
        if not img_path.is_file() or img_path.stat().st_size == 0:
            missing.append(img_path.name)
    return missing


def get_image_path(filename: str) -> Path | None:
    """Safely get the path to an image file if it exists and is required."""
    for img_path in REQUIRED_IMAGES:
        if img_path.name == filename and img_path.is_file() and img_path.stat().st_size > 0:
            return img_path
    return None


def get_download_status() -> dict:
    """Get overall status of the background downloads."""
    missing_count = len(get_missing_images())
    file_statuses = list(_download_state.values())
    
    # Calculate overall progress safely avoiding zero division
    total_expected = sum(st.total_bytes for st in file_statuses if st.total_bytes > 0)
    total_received = sum(st.downloaded_bytes for st in file_statuses if st.total_bytes > 0)
    
    overall_progress = int((total_received / total_expected) * 100) if total_expected > 0 else (100 if missing_count == 0 else 0)
    
    return {
        "files_ready": missing_count == 0,
        "overall_progress": overall_progress,
        "files": file_statuses,
    }


async def _download_file(url: str, dest: Path, filename: str) -> None:
    """Download single file with progress updates."""
    _download_state[filename] = DownloadProgress(
        filename=filename,
        downloaded_bytes=0,
        total_bytes=0,
        progress_percent=0,
        status="pending"
    )
    
    try:
        # Create dir if not exists
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                
                _download_state[filename].total_bytes = total
                _download_state[filename].status = "downloading"
                
                # Write to incomplete file first
                temp_dest = dest.with_suffix(dest.suffix + ".download")
                downloaded = 0
                
                with open(temp_dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024): # 1MB chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        _download_state[filename].downloaded_bytes = downloaded
                        if total > 0:
                            _download_state[filename].progress_percent = int((downloaded / total) * 100)
                            
                # Swap to real file
                temp_dest.replace(dest)
                _download_state[filename].progress_percent = 100
                _download_state[filename].status = "done"

    except Exception as e:
        _download_state[filename].status = "error"
        print(f"Failed to download {filename}: {e}")
        # Cleanup temp file on failure
        temp_dest = dest.with_suffix(dest.suffix + ".download")
        if temp_dest.exists():
            temp_dest.unlink()


async def download_missing_images_task() -> None:
    """Background task to fetch all missing images concurrently."""
    missing = get_missing_images()
    if not missing:
        return
        
    tasks = []
    for filename in missing:
        url = IMAGE_DOWNLOAD_URLS.get(filename)
        dest = IMG_DIR / filename
        if url:
            tasks.append(_download_file(url, dest, filename))
            
    if tasks:
        await asyncio.gather(*tasks)
