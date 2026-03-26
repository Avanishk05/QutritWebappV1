# Packaging Guide

## Windows .exe Installer (NSIS)

### Build Steps
1. PyInstaller: bundle agent into single .exe
2. NSIS: create installer wrapping the agent + tools
3. Include:
   - Agent binary
   - tools/bin/rkdeveloptool.exe + 3 DLLs
   - tools/DriverAssitant_v5.13/DriverInstall.exe
   - tools/DriverAssitant_v5.13/ADBDriver/adb.exe
   - img/ folder with flash images
   - frontend/ folder

### Installer Actions
- Install agent to Program Files
- Run DriverInstall.exe silently for USB driver setup
- Create Windows Service via NSSM
- Add firewall rule scoped to localhost:5001
- Create Start Menu shortcut
- Open web app in default browser
- Include uninstaller

### Required Tool Bundle (verify ALL 4 files present)
- `tools/bin/rkdeveloptool.exe`
- `tools/bin/libusb-1.0.dll`
- `tools/bin/msvcp140.dll`
- `tools/bin/vcruntime140.dll`
