# Project Reference Notes

## My Custom Image
- Filename: ExportImage.img
- This replaces rootfs.img
- It is a buildroot-based OS with custom packages pre-installed
- Do NOT use update.img or stock rootfs.img

## Flash File Locations (local, for development)
All files are in the images/ folder:
- MiniLoaderAll.bin   ← bootloader/loader (263 KB)
- parameter.txt       ← partition table with offsets
- uboot.img           ← secondary bootloader (4 MB)
- boot.img            ← kernel (6 MB)
- ExportImage.img     ← custom root filesystem (~121 MB)

## rkdeveloptool Location
- Already installed via DriverAssistant_v5.13
- Path rkdeveloptool: tools/DriverAssistant_v5.13/RKdev/RKDevTool.exe
- ADB path: tools/DriverAssistant_v5.13/ADBDriver/adb.exe


## USB Driver
- DriverInstall.exe is at tools/DriverAssistant_v5.13/DriverInstall.exe
- Must run silently before first device detection on fresh Windows install

## Device Info
- Board: Luckfox Lyra Zero W
- Chip: RK3506B
- USB VID: 0x2207 (Rockchip)
- MaskROM mode: hold BOOT button while plugging USB-C

## Post-Flash WiFi Config Command
After flash + reboot, once ADB is available, run:
adb shell "echo -e 'ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1\nnetwork={\n  ssid=\"SSID_HERE\"\n  psk=\"PASSWORD_HERE\"\n}' > /etc/wpa_supplicant.conf && reboot"

SSID and password come from the user via the web UI form.

## GitHub Releases Plan
Files to upload to GitHub Releases for user download:
1. MiniLoaderAll.bin
2. parameter.txt
3. uboot.img
4. boot.img
5. ExportImage.img  ← custom, uploaded separately

Repo URL: https://github.com/YOURNAME/YOURREPO
(replace with actual repo before deployment)

## Flash Partition Order
1. rkdeveloptool db MiniLoaderAll.bin
2. rkdeveloptool gpt parameter.txt
3. rkdeveloptool wl <offset> uboot.img    ← offset from parameter.txt
4. rkdeveloptool wl <offset> boot.img     ← offset from parameter.txt
5. rkdeveloptool wl <offset> ExportImage.img ← offset from parameter.txt
6. rkdeveloptool rd

## Development Machine
- OS: Windows 11
- All paths use Windows format
- Agent runs as Windows process (not systemd)
```

---

## 💬 WHAT TO ANSWER IN ANTIGRAVITY'S PROMPT

Paste this as your reply to the agent's open questions:
```
Proceed with Phase 1. Here are all answers and assets:

1. PHASES: Phase 1 only. Stop and show me evidence before Phase 2.

2. FILES: All flash files are in the images/ folder I provided:
   - MiniLoaderAll.bin    ← loader
   - parameter.txt        ← partition table (parse offsets from this)
   - uboot.img            ← uboot partition
   - boot.img             ← boot partition
   - ExportImage.img      ← my custom rootfs (NOT rootfs.img, NOT update.img)

3. rkdeveloptool: Available at:
   tools/DriverAssistant_v5.13/RKdev/RKDevTool.exe
   ADB at:
   tools/DriverAssistant_v5.13/ADBDriver/adb.exe
   Use these paths directly. Still apply fallback detection logic
   for other users who may not have this folder.

4. IMAGE FILENAMES: The custom rootfs file is named ExportImage.img
   Update ALL references from rootfs.img → ExportImage.img
   Update image_manager.py download filename accordingly.
   The GitHub Releases download URL will be decided by us as we will push this QutritWebapp folder so at that time the repo will be known 
   (use this as placeholder, I will update repo URL before deploy)

5. PARTITION OFFSETS: Do NOT hardcode.
   Parse offsets from parameter.txt at runtime.
   The parameter.txt file is in images/ folder — read it now
   to understand the format and write the parser correctly.

6. USB DRIVER: DriverInstall.exe is at:
   tools/DriverAssistant_v5.13/DriverInstall.exe
   Agent must run this silently on fresh Windows installs.

7. WIFI CONFIG: After flash + ADB available, run:
   adb shell "echo -e 'ctrl_interface=/var/run/wpa_supplicant\n
   update_config=1\nnetwork={\n  ssid=\"{SSID}\"\n
   psk=\"{PASSWORD}\"\n}' > /etc/wpa_supplicant.conf && reboot"
   where {SSID} and {PASSWORD} come from the web UI form.

8. GITHUB PAGES CORS: https://yourusername.github.io (placeholder)

9. THEME: Dark, accent #3B82F6

10. READ reference/notes.md — it has all additional context.
    READ images/parameter.txt — understand it before writing parser.
    READ tools/DriverAssistant_v5.13/Readme.txt if present.


Now begin Phase 0 scaffolding. Show me the file tree
as an Artifact before writing any code.