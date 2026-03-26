---
name: installer-packager
description: >
  Triggered when building .exe installer or packaging the agent.
---

# Installer Packager Skill

## Triggers
- "installer"
- ".exe"
- "pyinstaller"
- "NSIS"

## Instructions

1. Load `references/packaging-guide.md` for build instructions.
2. Always test full lifecycle: install → start → status → stop → uninstall.
3. Windows .exe installer must:
   - Install agent binary silently
   - Bundle rkdeveloptool.exe + all 3 DLLs
   - Start agent service automatically post-install
   - Open web app URL in default browser after install
