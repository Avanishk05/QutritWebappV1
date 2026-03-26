# Luckfox Device Flasher

One-click IoT device flasher for the **Luckfox Lyra Zero W** (RK3506B, Rockchip).

Flash a custom buildroot-based OS image onto your board with zero technical knowledge — just plug USB, hold BOOT, and click.

## Architecture

- **Frontend:** Static HTML/CSS/JS (GitHub Pages compatible)
- **Backend:** Python 3.12 + FastAPI local agent at `localhost:5001`
- **Flash Tool:** `rkdeveloptool.exe` subprocess wrapper
- **WiFi Config:** ADB-based post-flash WiFi setup

## Quick Start

### Prerequisites
- Windows 11
- Python 3.12+
- USB-C cable
- Luckfox Lyra Zero W board

### Development Setup

```powershell
# Install dependencies
pip install -r requirements.txt

# Start the agent
cd agent
uvicorn server:app --host 127.0.0.1 --port 5001

# Open frontend
start frontend/index.html
```

### Flash Flow
1. Put board in MaskROM mode (hold BOOT button while plugging USB-C)
2. Open the web app
3. Click "Check for Device"
4. Click "Flash OS Image"
5. Wait for completion
6. Enter WiFi credentials
7. Done!

## Project Structure

```
QutritWebapp/
├── frontend/          Static web app (HTML/CSS/JS)
├── agent/             FastAPI local agent
│   ├── routers/       API endpoints
│   ├── services/      Business logic
│   ├── models/        Pydantic schemas
│   └── flash.py       Flash orchestration script
├── img/               Flash images (DO NOT MODIFY)
├── tools/             Rockchip tools
│   ├── bin/           rkdeveloptool.exe + DLLs
│   └── DriverAssitant_v5.13/
└── tests/             Pytest test suite
```

## License

Proprietary — All rights reserved.
