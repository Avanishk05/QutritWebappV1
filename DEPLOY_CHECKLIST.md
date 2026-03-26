# Luckfox Flasher Deployment Checklist

## Developer Setup (Once per release)
- [ ] Create GitHub repo (public)
- [ ] Push project to `main` branch
- [ ] Create GitHub Release `v1.0.0`
- [ ] Upload to release:
    - `MiniLoaderAll.bin`
    - `parameter.txt`
    - `uboot.img`
    - `boot.img`
    - `ExportImage.img`
- [ ] Run `packaging/build.ps1` locally to bundle PyInstaller & NSIS
- [ ] Upload `dist/luckfox-setup.exe` to same GitHub Release
- [ ] Enable GitHub Pages (source: `main` `/docs`)
- [ ] Update `installer.nsi` with the final real GitHub Pages URL
- [ ] Update `IMAGE_BASE_URL` in `agent/config.py` with real release URL
- [ ] Rebuild and re-upload `luckfox-setup.exe`

## User Instructions
- [ ] Open GitHub Pages URL
- [ ] Click "Download Luckfox Flasher"
- [ ] Double-click installer `.exe`
- [ ] Click through standard setup (Next → Install)
- [ ] Web page auto-continues
- [ ] Connect Luckfox board in MaskROM mode
- [ ] Click Flash