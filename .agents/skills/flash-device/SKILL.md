---
name: flash-device
description: >
  Triggered when implementing, debugging, or testing the rkdeveloptool
  pipeline, flash.py, or the /flash and /device API endpoints.
---

# Flash Device Skill

## Triggers
- "rkdeveloptool"
- "flash device"
- "MaskROM"
- "MiniLoaderAll"
- "Luckfox"

## Instructions

1. Load `references/rkdeveloptool-api.md` for command reference.
2. Known Rockchip USB VID: `0x2207`.
3. Validate device VID/PID before any write operation.
4. Always log to `agent/logs/flash.log` using structured markers:
   - `[STEP n/6]` — step progress
   - `[OK]` — step success
   - `[ERROR msg]` — step failure
   - `[DONE]` — flash complete
5. Flash tool is at `tools/bin/rkdeveloptool.exe` with bundled DLLs.
6. Parse partition offsets from `img/parameter.txt` at runtime — NEVER hardcode.
7. Flash sequence:
   ```
   rkdeveloptool.exe db  MiniLoaderAll.bin
   rkdeveloptool.exe gpt parameter.txt
   rkdeveloptool.exe wl  <uboot_offset>  uboot.img
   rkdeveloptool.exe wl  <boot_offset>   boot.img
   rkdeveloptool.exe wl  <rootfs_offset> ExportImage.img
   rkdeveloptool.exe rd
   ```
