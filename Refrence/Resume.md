# RESUME.md — Last updated: 26-Mar-2026

## Project: Luckfox Flasher (QutritWebapp)

## Model Notes
- Planning: Claude Opus — all decisions final, do not revisit
- Implementation: Gemini 2.5 Pro (High)
- Do not re-research anything marked confirmed below

## Current Status
- Phase 0:  ✅ Complete
- Phase 1A: ✅ Complete (all 15 tasks done, pytest green)
- Phase 1B: ✅ Complete
- Phase 1C-1F: ✅ Complete (Packaging, Installers, Background DLs built)
- Next Task: 🔄 Deploy to GitHub and test on physical hardware

## Verified at Runtime (do not re-test)
- GET /api/v1/status → 200 { status, version, platform, tools_ready }
- GET /api/v1/device → 404 DEVICE_NOT_FOUND (correct, no board)
- Server binds 127.0.0.1:5001 ✅
- pytest exit code 0 ✅

## Confirmed Facts (locked)
- Chip: RK3506B
- USB VID: 0x2207 (Rockchip)
- USB PID: TBD — skip Phase 1, add Phase 2
- Tool: tools/bin/rkdeveloptool.exe ✅ working
- ADB: tools/DriverAssitant_v5.13/ADBDriver/adb.exe
- Driver: tools/DriverAssitant_v5.13/DriverInstall.exe
- img/ folder (not images/)
- DriverAssitant (typo is correct, matches disk)

## Partition Offsets (verified, do not re-parse)
- uboot  → 0x00002000 → uboot.img
- boot   → 0x00004000 → boot.img
- rootfs → 0x00010000 → ExportImage.img

## Flash Sequence (locked, 6 steps)
1. rkdeveloptool.exe db  MiniLoaderAll.bin
2. rkdeveloptool.exe gpt parameter.txt
3. rkdeveloptool.exe wl  0x00002000 uboot.img
4. rkdeveloptool.exe wl  0x00004000 boot.img
5. rkdeveloptool.exe wl  0x00010000 ExportImage.img
6. rkdeveloptool.exe rd

## Decisions (locked)
- flash.py not flash.sh (Windows-first)
- No mock mode — real hardware only
- Dark theme, accent #3B82F6
- CORS: https://yourusername.github.io (placeholder)
- 6 screens: 0→1→2→3→4(WiFi)→5(Success)
- POST /flash body: { ssid, password }
- POST /wifi body: { ssid, password }
- TOTAL_STEPS = 7 (6 flash + 1 wifi)
- WiFi config via adb after reboot

## Screen Map (locked)
- Screen 0: Bootstrap — agent check + tool download + image download
- Screen 1: Device Detection
- Screen 2: Flash (device summary + WiFi form + Flash button)
- Screen 3: Progress (live logs + progress bar)
- Screen 4: WiFi Config confirmation
- Screen 5: Success

## API Endpoints (all implemented)
- GET  /api/v1/status
- GET  /api/v1/device
- POST /api/v1/flash       body: { ssid, password }
- GET  /api/v1/logs
- POST /api/v1/wifi        body: { ssid, password }
- GET  /api/v1/images/status
- POST /api/v1/images/download
- POST /api/v1/install-deps

## Output Rules (every session)
- SILENT MODE — no narration, no thinking out loud
- No "I will now...", "I'm focusing on..."
- Artifacts only — no code blocks in chat
- Max 3 lines of text between artifacts
- Do not repeat file contents before editing
- Do not quote instructions back before following

## Next Task
GitHub Deploy & Physical Hardware Test
```

---

Then paste this to start 1B:
```
SILENT MODE. Read RESUME.md.

Phase 1B — execute in order, no stopping:
  1. style.css  — dark theme, #3B82F6 accent, CSS custom
                  properties, Inter font, all component styles
  2. index.html — 6 screen containers (screens 0-5)
  3. app.js     — full SPA logic for all 6 screens,
                  poll /logs every 2s on screen 3,
                  WiFi form on screen 2 before flash button

After all 3 files complete:
  Open index.html in browser subagent
  Screenshot all 6 screens at 1280px
  Show screenshots as Artifacts

Only stop for genuine blocker.--

### 📏 Rules Going Forward

**One prompt per session, not a conversation:**
- Dump `RESUME.md` content + single instruction
- Let agent run to completion uninterrupted
- Only intervene at explicit checkpoints

**Keep your messages short:**
- Bad: long back-and-forth clarifications mid-build
- Good: one dense briefing → agent runs → you review artifact → one approval/correction

**Use checkpoints, not commentary:**
Instead of sending 5 correction messages, wait for the agent to finish a full task then send one consolidated correction list.

## Model Notes
- Planning was done with Claude Opus — all decisions are final
- Implementation continues with Gemini 3.1 Pro (High)
- Do not revisit any locked decisions in RESUME.md
---

### 🔁 Session Template

Every future session starts with just this:
```
Read RESUME.md. Read GEMINI.md. Then execute next task.
Do not ask questions — follow RESUME.md decisions.
Show artifact when done.


## Output Rules (saves context)
- No thinking narration — just do the task
- No "I will now...", "I'm focusing on...", "I recalled..."
- No explaining what tools you're about to use
- No summarizing what you just did after doing it
- Show ONLY: code files, terminal output, artifacts
- If you must communicate: one line max
- Silent execution is preferred
```

And at the top of every session prompt add:
```
SILENT MODE: No narration. No thinking out loud.
Code and terminal output only.
Read RESUME.md → execute → show artifact.


markdown- Do not repeat file contents back to me before editing
- Do not quote my instructions back before following them  
- Artifacts only — no code blocks in chat
- Max 3 lines of text between artifacts