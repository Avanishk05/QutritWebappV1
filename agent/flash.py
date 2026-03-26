"""Flash orchestration script (Python, NOT bash).

Executes the 6-step flash sequence via rkdeveloptool.exe subprocess calls.
Emits structured log markers to stdout for real-time parsing.

Steps:
  1. [STEP 1/6] Download bootloader (db MiniLoaderAll.bin)
  2. [STEP 2/6] Write partition table (gpt parameter.txt)
  3. [STEP 3/6] Write uboot (wl <offset> uboot.img)
  4. [STEP 4/6] Write boot (wl <offset> boot.img)
  5. [STEP 5/6] Write rootfs (wl <offset> ExportImage.img)
  6. [STEP 6/6] Reboot device (rd)

Usage: Called by services/flasher.py, not directly.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the project root to sys.path so we can import from agent package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.config import get_rkdeveloptool_path, PARAMETER_PATH, MINILOADER_PATH, SUBPROCESS_TIMEOUT_FLASH
from agent.services.parameter_parser import parse_parameter_file


def run_command(desc: str, step: int, args: list[str]) -> None:
    """Run an rkdeveloptool command and emit structured logs."""
    print(f"[STEP {step}/6] {desc}", flush=True)
    
    try:
        # Run subprocess (synchronous since this is a dedicated script)
        # Using list args — never shell=True (Security Rule)
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_FLASH,
            check=False, # We check return code manually for custom error logging
        )
        
        # Log stdout/stderr for debugging
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                print(f"  > {line}", flush=True)
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines():
                print(f"  ! {line}", flush=True)

        if result.returncode != 0:
            print(f"[ERROR msg] Command failed with exit code {result.returncode}", file=sys.stderr, flush=True)
            sys.exit(1)
            
        print("[OK]", flush=True)
        
    except subprocess.TimeoutExpired:
        print("[ERROR msg] Command timed out", file=sys.stderr, flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR msg] Execution failed: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


def main() -> None:
    """Execute the flash sequence."""
    print("[INIT] Starting flash process", flush=True)
    
    rktool = get_rkdeveloptool_path()
    if not rktool:
        print("[ERROR msg] rkdeveloptool.exe not found", file=sys.stderr, flush=True)
        sys.exit(1)
    
    rktool_str = str(rktool)
    
    # Needs to parse parameter offsets dynamically
    try:
        partitions = parse_parameter_file(PARAMETER_PATH)
    except Exception as e:
        print(f"[ERROR msg] Failed to parse parameter.txt: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
        
    # Build dictionary of partition name -> offset for easy lookup
    # Only keep those that have an image mapped
    offset_map = {p.name: p.offset_decimal for p in partitions if p.image_file}
    
    # Validate we have the three required ones
    required_parts = ["uboot", "boot", "rootfs"]
    for req in required_parts:
        if req not in offset_map:
            print(f"[ERROR msg] Partition '{req}' not found in parameter.txt", file=sys.stderr, flush=True)
            sys.exit(1)
            
    # Locate all required files
    from agent.config import UBOOT_PATH, BOOT_PATH, ROOTFS_PATH
    
    # Sequence definition
    seq = [
        (1, "Download bootloader", ["db", str(MINILOADER_PATH)]),
        (2, "Write partition table", ["gpt", str(PARAMETER_PATH)]),
        (3, "Write uboot", ["wl", str(offset_map["uboot"]), str(UBOOT_PATH)]),
        (4, "Write boot", ["wl", str(offset_map["boot"]), str(BOOT_PATH)]),
        (5, "Write rootfs", ["wl", str(offset_map["rootfs"]), str(ROOTFS_PATH)]),
        (6, "Reboot device", ["rd"]),
    ]
    
    for step, desc, cmd_args in seq:
        full_args = [rktool_str] + cmd_args
        run_command(desc, step, full_args)
        
    print("[DONE] Flash completed successfully", flush=True)


if __name__ == "__main__":
    main()
