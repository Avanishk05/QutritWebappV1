# 🚀 MISSION: IoT Device Flasher System — Production Build

## ⚠️ IMPLEMENTATION STRATEGY (CRITICAL — READ FIRST)

DO NOT over-engineer initially. All agents must follow phased delivery.

Phase 1 (MVP — must be fully working and tested before Phase 2):
- Device detection
- Flash execution
- Log streaming

Phase 2 (only after Phase 1 is green):
- Progress bar parsing
- Frontend UI polish
- Edge case handling

Phase 3 (only after Phase 2 is green):
- Auto-update system
- Installer improvements
- Coverage hardening

Each agent must attach terminal output or a browser screenshot Artifact
confirming the current phase is working before advancing.

---

## 🧠 ARCHITECT CONTEXT

You are operating in Google Antigravity's Agent-First paradigm.
Before writing a single line of code, enter Planning Mode and generate:
- A verified Architecture Artifact (system diagram)
- A phased Task List Artifact with agent assignments
- A Dependency Graph Artifact

Do NOT begin implementation until I approve the plan.

---

## 📐 SYSTEM OVERVIEW

Build a production-grade IoT Device Flasher that allows a NON-TECHNICAL
USER to flash a custom OS image onto a Luckfox Lyra Zero W board using ONLY:
  1. Plug USB-C cable
  2. Press BOOT button (MaskROM mode)
  3. Click buttons in a web app

Stack:
  - Frontend:      Pure static HTML/CSS/JS (GitHub Pages compatible)
  - Local Agent:   Python 3.12 + FastAPI (NOT Flask)
  - Flash Engine:  rkdeveloptool subprocess wrapper
  - Transport:     USB via local agent at http://localhost:5001
  - Packaging:     .deb (Linux) + .exe (Windows) one-click installers

---

## 🚀 AGENT BOOTSTRAP STRATEGY (CRITICAL)

The system MUST support first-time users with ZERO manual setup.

### Agent Availability Detection (Frontend, on page load)
- Attempt GET http://localhost:5001/api/v1/status with 3s timeout
- If request fails:
  → Show "Agent Not Installed" screen
  → Detect OS via navigator.platform / navigator.userAgent
  → Show correct installer download:
      Windows  → luckfox-agent-setup.exe
      Linux    → luckfox-agent.deb
  → Single prominent "Download & Install Agent" button
- After user installs:
  → Frontend retries GET /status automatically every 2 seconds
  → On success: auto-transition to Device Detection screen
  → Show live "Waiting for agent…" pulse animation during retry

### Installer Requirements
- Windows .exe and Linux .deb must:
  → Install agent binary silently
  → Start the agent service automatically post-install
  → Require zero CLI interaction from the user
  → Open the web app URL in the default browser after install

---

## ⚡ PARALLEL AGENT MISSIONS

Spawn the following agents simultaneously in Agent Manager:

### Agent A — "Architect"
Responsibility: Workspace scaffolding + GEMINI.md rules + Skills authoring
Completes before Agents B/C/D begin implementation.

### Agent B — "Frontend Engineer"
Responsibility: Static web app (GitHub Pages)
Uses Browser subagent to screenshot and validate each screen.

### Agent C — "Systems Engineer"
Responsibility: FastAPI local agent + flashing engine + flash.sh
Runs terminal tests after each module.

### Agent D — "DevOps Engineer"
Responsibility: Installers + systemd service + auto-update logic (Phase 3)
Verifies service lifecycle in terminal.

---

## 📋 WORKSPACE RULES (Agent A writes to GEMINI.md)
```gemini
## Project Identity
Production IoT flashing tool for non-technical users.
All UX must be zero-friction. No terminal. No config. No manual steps.

## Tech Stack
- Backend:    Python 3.12, FastAPI (async/await throughout), Pydantic v2
- Frontend:   Vanilla JS ES2022, CSS custom properties, zero frameworks
- Packaging:  PyInstaller for agent binary, fpm for .deb, NSIS for .exe
- Shell:      bash (Linux/macOS), PowerShell (Windows)

## Code Standards
- Type-hint ALL Python function signatures
- Use async/await for ALL I/O in FastAPI — no blocking calls
- Docstrings on every public function and class
- Pydantic models for ALL API request/response schemas
- NEVER use shell=True in subprocess — always use list args
- ALL file paths via pathlib.Path — never string concatenation

## Security Rules
- API binds to 127.0.0.1 ONLY — never 0.0.0.0
- Validate all subprocess inputs against allowlist before execution
- No secrets in source — use environment variables
- All file writes must stay within the agent's sandboxed directory

## Agent Behaviour
- Explore full project tree before modifying any file
- Write a plan Artifact before implementing each module
- After each module: write test → run in terminal → confirm green
- If terminal command fails: analyze error → fix → re-run
- Never mark a task complete without verified terminal or browser evidence
- Respect the phased delivery strategy — do not skip ahead
```

---

## 🛠️ WORKSPACE SKILLS (Agent A writes to .agents/skills/)

### skill: flash-device
```yaml
name: flash-device
description: >
  Triggered when implementing, debugging, or testing the rkdeveloptool
  pipeline, flash.sh, or the /flash and /device API endpoints.
triggers:
  - "rkdeveloptool"
  - "flash device"
  - "MaskROM"
  - "loader.bin"
  - "Luckfox"
```
Instructions: Load references/rkdeveloptool-api.md. Known Rockchip USB
VID: 0x2207. Validate device VID/PID before any write. Always log to
logs/flash.log using structured markers.

### skill: frontend-validator
```yaml
name: frontend-validator
description: >
  Triggered when building or testing the static web UI. Uses browser
  subagent to screenshot each screen and verify against UX spec.
triggers:
  - "web UI"
  - "frontend screen"
  - "Agent Check Screen"
  - "Progress Screen"
  - "Bootstrap installer"
```
Instructions: Open index.html in browser subagent. Navigate each screen.
Capture screenshot Artifact. Assert no console errors. Test at 375px,
768px, 1280px.

### skill: installer-packager
```yaml
name: installer-packager
description: >
  Triggered when building .deb, .exe, or systemd service files.
triggers:
  - "installer"
  - "systemd"
  - ".deb"
  - ".exe"
  - "pyinstaller"
```
Instructions: Load references/packaging-guide.md. Always test full
lifecycle: install → start → status → stop → uninstall in terminal.

---

## 🗂️ REQUIRED PROJECT STRUCTURE

Agent A scaffolds this in full before other agents begin:
```
luckfox-flasher/
├── GEMINI.md
├── AGENTS.md
├── .agents/
│   ├── skills/
│   │   ├── flash-device/
│   │   │   ├── SKILL.md
│   │   │   └── references/rkdeveloptool-api.md
│   │   ├── frontend-validator/
│   │   │   └── SKILL.md
│   │   └── installer-packager/
│   │       ├── SKILL.md
│   │       └── references/packaging-guide.md
│   └── rules/security.md
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── agent/
│   ├── server.py
│   ├── routers/
│   │   ├── status.py
│   │   ├── device.py
│   │   ├── flash.py
│   │   └── deps.py
│   ├── services/
│   │   ├── flasher.py
│   │   ├── installer.py
│   │   ├── updater.py          # Phase 3 only
│   │   └── image_manager.py
│   ├── models/schemas.py
│   ├── flash.sh
│   ├── config.py
│   ├── logs/.gitkeep
│   └── images/.gitkeep
│
├── packaging/
│   ├── linux/
│   │   ├── build-deb.sh
│   │   ├── luckfox-agent.service
│   │   └── postinst
│   ├── windows/
│   │   ├── installer.nsi
│   │   └── build-exe.ps1
│   └── build-all.sh
│
├── tests/
│   ├── test_api.py
│   ├── test_flasher.py
│   └── conftest.py
│
└── README.md
```

---

## 🟩 AGENT B MISSION: FRONTEND

### Screens (Single Page Application)

**Screen 0 — Agent Bootstrap (NEW)**
- On load: fetch GET /api/v1/status (3s timeout)
- If reachable → auto-advance to Screen 1
- If not:
  → Detect OS
  → Show download button for correct installer
  → Retry every 2s with animated "Waiting for agent…" state
  → Auto-advance on success

**Screen 1 — Device Detection**
- Button: "Check for Device"
- Calls: GET /api/v1/device
- On success: Show device info card
  (device_type, chip, maskrom status, serial)
- On failure: Actionable error with retry button

**Screen 2 — Flash**
- Display confirmed device summary
- Button: "Flash OS Image →"
- Calls: POST /api/v1/flash
- Disabled + spinner while flash is in progress

**Screen 3 — Progress**
- Poll GET /api/v1/logs every 2 seconds
- Parse structured log markers:
  [STEP n/4], [OK], [ERROR msg], [DONE]
- Animated CSS progress bar (no JS animation library)
- Auto-scroll log viewer
- Auto-advance to Screen 4 on [DONE]

**Screen 4 — Success**
- Full-screen success state
- "Flash Complete ✓"
- Device reboot countdown
- "Flash Another Device" button → returns to Screen 1

---

### ⚠️ EDGE CASE HANDLING (MANDATORY — Phase 2)

**1. Agent Crash**
- If /status fails during any operation:
  → Show persistent banner: "Agent Disconnected — retrying…"
  → Auto-retry every 2s
  → Resume flow when restored

**2. USB Disconnect During Flash**
- Detect via [ERROR] in logs OR /status failure
- Show: "Device disconnected during flashing. Reconnect and retry."

**3. Flash Timeout**
- If no new log line for 10 seconds during active flash:
  → Show warning: "No activity detected — flash may have stalled"
  → Offer: "Cancel" and "Retry" buttons

**4. API Errors**
- NEVER show raw error objects or stack traces to user
- Map all HTTP error codes to plain-English messages

**5. Button States**
- All action buttons disabled during active operations
- Visual disabled state must be obvious (opacity + cursor)
- Prevent double-submit on all async actions

**6. Recovery**
- Every error screen must have a clearly labelled restart/retry path
- User should never reach a dead end with no forward action

---

### Browser Subagent Validation
After each screen: screenshot → verify no console errors →
confirm layout at 375px / 768px / 1280px → attach as Artifact.

---

## 🟨 AGENT C MISSION: LOCAL AGENT

### server.py — FastAPI App Factory
```python
# - Bind ONLY to 127.0.0.1:5001
# - CORS: allow http://localhost:* and https://*.github.io only
# - Middleware: request logging, X-Response-Time header
# - Startup: verify rkdeveloptool installed, auto-install if missing
# - Lifespan context manager (NOT deprecated @app.on_event)
# - All routers under /api/v1 prefix
```

### routers/device.py
```python
# GET /api/v1/device
# - Run: ["rkdeveloptool", "ld"] via asyncio.create_subprocess_exec
# - Parse output into DeviceInfo Pydantic model
# - VALIDATE USB VID/PID against known Luckfox identifiers:
#     Rockchip VID: 0x2207
#     Expected PIDs for MaskROM mode: 0x330d, 0x350a (verify in refs)
# - If VID/PID does not match:
#     → HTTP 400: { "error": "Unsupported device detected" }
# - Return structured response:
#   {
#     "connected": true,
#     "device_type": "luckfox_lyra_zero_w",
#     "chip": "RK3506B",
#     "maskrom": true,
#     "serial": "..."
#   }
# - HTTP 404 if no device found
# - HTTP 503 if rkdeveloptool not installed
# - Timeout: 10 seconds
```

### routers/flash.py
```python
# POST /api/v1/flash
# - Validate: device present and VID/PID matches
# - Validate: loader.bin exists
# - Validate: os.img exists (trigger download if not)
# - Check global flash lock — HTTP 409 if already running
# - Launch flash.sh as background asyncio task
# - Stream stdout/stderr to logs/flash.log in real-time
# - Return 202 Accepted immediately

# GET /api/v1/logs
# - Return last 200 lines of logs/flash.log
# - Return structured:
#   {
#     "lines": [...],
#     "progress": 0-100,
#     "status": "idle|running|done|error"
#   }
# - Derive progress % from [STEP n/4] markers
```

### services/flasher.py
```python
# CONCURRENCY CONTROL:
# - Single global asyncio.Lock — only one flash at a time
# - Reject concurrent /flash calls with HTTP 409
# - Create lockfile: logs/flash.lock on start, remove on finish
# - On startup: if flash.lock exists → log warning, clean stale state
#
# RELIABILITY:
# - Structured log markers: [STEP 1/4], [OK], [ERROR msg], [DONE]
# - Retry logic: 3 attempts on transient USB errors
# - Atomic log writes via asyncio.Lock
# - Clean state reset between flash attempts
```

### flash.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

TOTAL_STEPS=4
log_step() { echo "[STEP $1/$TOTAL_STEPS] $2"; }
log_ok()   { echo "[OK] $1"; }
log_err()  { echo "[ERROR] $1"; exit 1; }
log_done() { echo "[DONE] Flashing complete"; }

# Step 1: Validate device connected
# Step 2: Load bootloader  → rkdeveloptool db loader.bin
# Step 3: Write OS image   → rkdeveloptool wl 0 os.img
# Step 4: Reboot device    → rkdeveloptool rd
# Each step: validate exit code → log result → handle error
log_done
```

### services/image_manager.py
```python
# - Check images/os.img exists and SHA256 matches manifest
# - If missing: download from IMAGE_URL env var with progress logging
# - Emit [DOWNLOAD n%] markers to logs/flash.log during download
# - Version manifest schema: { version, url, sha256, size }
# - Cache manifest for 1 hour
```

### services/updater.py  (Phase 3 — do not implement until Phase 2 complete)
```python
# AUTO-UPDATE REQUIREMENTS:
# - On agent startup: fetch remote version.json manifest
# - Compare semantic version (packaging.version.Version)
# - If newer available AND no flash in progress:
#     → Download update package to temp dir
#     → Verify SHA256
#     → Apply update and restart service
# - MUST NOT interrupt active flash (check lock before updating)
# - Endpoints:
#     GET  /api/v1/version  → { current, latest, update_available }
#     POST /api/v1/update   → triggers update, returns 202
```

### Terminal Validation (Agent C runs after each module)
```bash
cd agent
pip install -r requirements.txt
pytest tests/ -v --tb=short
uvicorn server:app --host 127.0.0.1 --port 5001 &
sleep 2
curl -s http://localhost:5001/api/v1/status | python -m json.tool
# Expected: { "status": "running", "version": "x.y.z" }
curl -s http://localhost:5001/api/v1/device | python -m json.tool
# Expected: 404 with no device connected
```

---

## 🟥 AGENT D MISSION: PACKAGING

### Linux .deb
- Use fpm to package PyInstaller binary
- postinst must:
  1. Install udev rule for Rockchip VID 0x2207
  2. Add user to `plugdev` group
  3. Enable and start luckfox-agent.service
  4. Run `udevadm control --reload-rules && udevadm trigger`

### systemd Service
```ini
[Unit]
Description=Luckfox Flasher Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/luckfox-agent
Restart=on-failure
RestartSec=5s
User=luckfox-agent
Environment=AGENT_LOG_LEVEL=INFO
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Windows .exe (NSIS)
- Install agent binary silently
- Create Windows Service via NSSM
- Add Windows Firewall rule scoped to localhost:5001
- Create Start Menu shortcut
- Open web app in browser post-install
- Include uninstaller that reverses all changes

### Terminal Validation (Agent D)
```bash
sudo systemctl start luckfox-agent
sudo systemctl status luckfox-agent
curl -s http://localhost:5001/api/v1/status
sudo systemctl stop luckfox-agent
sudo dpkg -r luckfox-agent && curl http://localhost:5001/api/v1/status
# Expected: connection refused after uninstall
```

---

## ✅ COMPLETION CRITERIA

Mission is NOT complete until ALL are verified with Artifact evidence:

### Phase 1
- [ ] Agent C: `pytest tests/ -v` passes
- [ ] Agent C: `/api/v1/status` returns 200
- [ ] Agent C: `/api/v1/device` returns correct 404 (no device)
- [ ] Agent C: `/api/v1/flash` returns 409 on concurrent call
- [ ] Agent B: Screens 0–4 render in browser subagent (Phase 1 fidelity)

### Phase 2
- [ ] Agent B: All 5 screens pixel-correct at 375/768/1280px
- [ ] Agent B: Zero console errors across all screens
- [ ] Agent B: All 6 edge cases handled and demoed
- [ ] Agent C: Coverage ≥ 90% on core modules

### Phase 3
- [ ] Agent D: systemd lifecycle passes (start/status/stop/uninstall)
- [ ] Agent D: .deb installs cleanly on Ubuntu 22.04
- [ ] Agent C: Auto-update does not trigger during active flash
- [ ] README: Single-command install verified end-to-end

---

## 📌 KNOWLEDGE ITEMS TO PERSIST

Save after build for future sessions:

1. "Rockchip MaskROM USB VID/PID" — 0x2207 + confirmed PIDs
2. "rkdeveloptool MaskROM sequence" — exact working command order
3. "Flash log marker schema" — [STEP n/4], [OK], [ERROR], [DONE], [DOWNLOAD n%]
4. "GitHub Pages CORS origin pattern" — for FastAPI CORS config
5. "Luckfox udev rule" — exact udev rule that enables non-root USB access