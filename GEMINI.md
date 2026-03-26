## Project Identity
Production IoT flashing tool for non-technical users.
All UX must be zero-friction. No terminal. No config. No manual steps.
Target board: Luckfox Lyra Zero W (RK3506B, Rockchip).

## Tech Stack
- Backend:    Python 3.12, FastAPI (async/await throughout), Pydantic v2
- Frontend:   Vanilla JS ES2022, CSS custom properties, zero frameworks
- Flash Tool: rkdeveloptool.exe (Windows CLI, bundled at tools/bin/)
- ADB:        adb.exe (bundled at tools/DriverAssitant_v5.13/ADBDriver/)
- Shell:      PowerShell (Windows-first project)

## Code Standards
- Type-hint ALL Python function signatures
- Use async/await for ALL I/O in FastAPI — no blocking calls
- Docstrings on every public function and class
- Pydantic models for ALL API request/response schemas
- NEVER use shell=True in subprocess — always use list args
- ALL file paths via pathlib.Path — never string concatenation
- No bash scripts — all orchestration in Python (flash.py, not flash.sh)

## Security Rules
- API binds to 127.0.0.1 ONLY — never 0.0.0.0
- Validate all subprocess inputs against allowlist before execution
- No secrets in source — use environment variables
- All file writes must stay within the agent's sandboxed directory

## Flash Tool Bundle
rkdeveloptool.exe requires these DLLs (must ALL be present):
- tools/bin/rkdeveloptool.exe
- tools/bin/libusb-1.0.dll
- tools/bin/msvcp140.dll
- tools/bin/vcruntime140.dll
Auto-download must fetch ALL four files, not just the .exe.

## Flash Image Files (DO NOT MODIFY)
All flash images are in img/ folder:
- MiniLoaderAll.bin  — bootloader
- parameter.txt     — partition table (parse offsets at runtime)
- uboot.img         — secondary bootloader
- boot.img          — kernel
- ExportImage.img   — custom rootfs (buildroot-based)

## Partition Offsets
Parse from parameter.txt CMDLINE at runtime. NEVER hardcode.
Format: mtdparts=:SIZE@OFFSET(name),...

## Agent Behaviour
- Explore full project tree before modifying any file
- Write a plan Artifact before implementing each module
- After each module: write test → run in terminal → confirm green
- If terminal command fails: analyze error → fix → re-run
- Never mark a task complete without verified terminal or browser evidence
- Respect the phased delivery strategy — do not skip ahead
