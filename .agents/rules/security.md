# Security Rules

## Network
- API binds to `127.0.0.1` ONLY — never `0.0.0.0`
- CORS whitelist: `http://localhost:*` and `https://*.github.io` only

## Subprocess
- NEVER use `shell=True` — always pass list args
- Validate ALL subprocess inputs against allowlist before execution
- Only allowed executables: `rkdeveloptool.exe`, `adb.exe`, `DriverInstall.exe`
- Timeout all subprocess calls (10s for device ops, 300s for flash writes)

## File System
- All file writes must stay within the project directory
- No secrets in source code — use environment variables
- Log files must not contain sensitive data

## Input Validation
- Sanitize WiFi SSID and password before ADB injection
- Reject SSID/password with shell metacharacters
- Validate all API request bodies against Pydantic schemas
