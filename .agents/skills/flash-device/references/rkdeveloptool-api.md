# rkdeveloptool CLI Reference

## Tool Location
`tools/bin/rkdeveloptool.exe` (Windows pre-compiled binary)

## Required DLLs (must ALL be present alongside .exe)
- `libusb-1.0.dll`
- `msvcp140.dll`
- `vcruntime140.dll`

## Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| List Devices | `rkdeveloptool ld` | List connected Rockchip devices |
| Download Boot | `rkdeveloptool db <loader.bin>` | Download bootloader to device |
| Write GPT | `rkdeveloptool gpt <parameter.txt>` | Write GPT partition table |
| Write LBA | `rkdeveloptool wl <sector_offset> <file>` | Write image at sector offset |
| Write LBA (named) | `rkdeveloptool wlx <partition_name> <file>` | Write image to named partition |
| Reboot | `rkdeveloptool rd` | Reboot the device |
| Upgrade Loader | `rkdeveloptool ul <loader.bin>` | Upgrade loader |
| Read LBA | `rkdeveloptool rl <begin_sec> <sec_len> <file>` | Read sectors to file |
| Write Parameter | `rkdeveloptool prm <parameter>` | Write parameter |
| Print Partition | `rkdeveloptool ppt` | Print partition table |
| Version | `rkdeveloptool -v` or `--version` | Show version |
| Help | `rkdeveloptool -h` or `--help` | Show help |

## USB Identifiers
- **Vendor ID (VID):** `0x2207` (Rockchip)
- **Product IDs (PID) for MaskROM:** `0x330d`, `0x350a` (verify per device)

## Exit Codes
- `0` — Success
- `1` — No device found / command failed

## Source
Pre-compiled from: https://github.com/cpebit/rkdeveloptool-bin
