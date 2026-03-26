"""Flash orchestrator service.

Executes the 6-step flash sequence via rkdeveloptool.exe:
  1. db MiniLoaderAll.bin
  2. gpt parameter.txt
  3. wl <offset> uboot.img
  4. wl <offset> boot.img
  5. wl <offset> ExportImage.img
  6. rd (reboot)

Concurrency: single global asyncio.Lock — one flash at a time.
Structured log markers: [STEP n/6], [OK], [ERROR msg], [DONE]
"""

import asyncio
import sys
from collections import deque
from pathlib import Path

from agent.config import PROJECT_ROOT, FLASH_LOG_PATH
from agent.models.schemas import FlashStatus


# Global state
_FLASH_LOCK = asyncio.Lock()
_CURRENT_STATUS: FlashStatus = FlashStatus.IDLE
_CURRENT_PROGRESS: int = 0
_CURRENT_STEP: int = 0
_TOTAL_STEPS: int = 6  # 6 rkdeveloptool steps

# In-memory log buffer for streaming to UI (last 200 lines)
_LOG_BUFFER: deque[str] = deque(maxlen=200)


def get_flash_status() -> dict:
    """Return the current flash status and progress.

    Returns:
        Dict with keys: status, progress, current_step, total_steps, lines
    """
    return {
        "status": _CURRENT_STATUS,
        "progress": _CURRENT_PROGRESS,
        "current_step": _CURRENT_STEP,
        "total_steps": _TOTAL_STEPS,
        "lines": list(_LOG_BUFFER),
    }


def _append_log(message: str) -> None:
    """Append a message to the in-memory buffer and file."""
    _LOG_BUFFER.append(message)
    try:
        # Append to log file
        with open(FLASH_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass  # Fail gracefully if log file can't be written


async def start_flash() -> bool:
    """Start the flash process if not already running.

    Returns:
        True if started successfully, False if already running.
    """
    global _CURRENT_STATUS, _CURRENT_PROGRESS, _CURRENT_STEP
    
    if _FLASH_LOCK.locked():
        return False

    # Start background task holding the lock
    asyncio.create_task(_run_flash_subprocess())
    return True


async def _run_flash_subprocess() -> None:
    """Background task to run the python flash.py script."""
    global _CURRENT_STATUS, _CURRENT_PROGRESS, _CURRENT_STEP
    
    async with _FLASH_LOCK:
        _CURRENT_STATUS = FlashStatus.RUNNING
        _CURRENT_PROGRESS = 0
        _CURRENT_STEP = 0
        _LOG_BUFFER.clear()
        
        # 1. Ensure log directory exists, truncate previous log file
        FLASH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(FLASH_LOG_PATH, "w", encoding="utf-8") as f:
                f.write("=== FLASH STARTED ===\n")
        except Exception:
            pass

        _append_log("[INIT] Launching flash.py orchestrator")
        
        script_path = PROJECT_ROOT / "agent" / "flash.py"
        
        try:
            # We execute sys.executable so it runs in the same environment
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            
            # Read stdout line by line
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                    
                _append_log(line)
                
                # Parse progress markers: [STEP 1/6]
                if line.startswith("[STEP "):
                    # Extract step number
                    try:
                        parts = line.split("]")[0].split(" ")[1] # "1/6"
                        step_num = int(parts.split("/")[0])
                        _CURRENT_STEP = step_num
                        _CURRENT_PROGRESS = int((step_num / _TOTAL_STEPS) * 100)
                    except Exception:
                        pass
                
                # Parse error marker
                elif "[ERROR" in line:
                    _CURRENT_STATUS = FlashStatus.ERROR
                    
            await proc.wait()
            
            if proc.returncode == 0 and _CURRENT_STATUS != FlashStatus.ERROR:
                _CURRENT_STATUS = FlashStatus.DONE
                _CURRENT_PROGRESS = 100
                _append_log("[DONE] Flash completed successfully")
            else:
                _CURRENT_STATUS = FlashStatus.ERROR
                _append_log(f"[ERROR msg] Subprocess exited with code {proc.returncode}")
                
        except Exception as e:
            _CURRENT_STATUS = FlashStatus.ERROR
            _append_log(f"[ERROR msg] Flasher service exception: {e}")

