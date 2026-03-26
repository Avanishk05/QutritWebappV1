# Build PyInstaller and NSIS deployment package
$ErrorActionPreference = "Stop"

$workspaceRoot = (Resolve-Path "..\").Path
Set-Location $workspaceRoot

Write-Host "[Build] Cleaning previous dist/ and build/ directories..."
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

Write-Host "[Build] Executing PyInstaller to bundle Python execution contexts..."
pyinstaller packaging\luckfox-agent.spec

if (-not (Test-Path "dist\luckfox-agent\luckfox-agent.exe")) {
    Write-Error "PyInstaller failed to emit target executable."
    exit 1
}

Write-Host "[Build] Executing makensis to generate universal Windows Installer..."
makensis packaging\installer.nsi

if (Test-Path "dist\luckfox-setup.exe") {
    Write-Host "[Build] SUCCESS. Build complete: dist\luckfox-setup.exe"
} else {
    Write-Error "[Build] FAILED. Output installer not found."
    exit 1
}
