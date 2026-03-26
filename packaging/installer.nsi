!define APPNAME "LuckfoxFlasher"
!define COMPANYNAME "Luckfox"
!define DESCRIPTION "Luckfox IoT Flasher Agent"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

; Install to 64-bit Program Files
InstallDir "$PROGRAMFILES64\LuckfoxFlasher"
OutFile "dist\luckfox-setup.exe"
Name "Luckfox Flasher"
RequestExecutionLevel admin

; Make installation silent by default unless overridden
SilentInstall silent

Section "Luckfox Flasher Software" SEC01
    ; 1. Extract application payload
    SetOutPath "$INSTDIR"
    File /r "dist\luckfox-agent\*"
    
    ; 2. Install Rockchip USB Driver Silently
    DetailPrint "Installing Rockchip USB Driver..."
    ExecWait '"$INSTDIR\tools\DriverAssitant_v5.13\DriverInstall.exe" /S'
    
    ; 3. Re-create and configure Windows Service
    DetailPrint "Registering Agent daemon..."
    nsExec::ExecToLog 'sc stop LuckfoxFlasherAgent'
    Sleep 1000
    nsExec::ExecToLog 'sc delete LuckfoxFlasherAgent'
    
    nsExec::ExecToLog 'sc create LuckfoxFlasherAgent binPath= "\"$INSTDIR\luckfox-agent.exe\"" start= auto'
    
    ; Enable service autorestart (fails 1: 5s, fails 2: 10s, fails 3+: 30s)
    nsExec::ExecToLog 'sc failure LuckfoxFlasherAgent reset= 86400 actions= restart/5000/restart/10000/restart/30000'
    
    ; 4. Sandbox Firewall Rule to localhost
    DetailPrint "Configuring Windows Firewall..."
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="LuckfoxFlasher"'
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="LuckfoxFlasher" dir=in action=allow protocol=TCP localport=5001 remoteip=127.0.0.1'
    
    ; 5. Start Service
    DetailPrint "Starting Agent daemon..."
    nsExec::ExecToLog 'sc start LuckfoxFlasherAgent'
    
    ; 6. Write Uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; 7. Open Setup Sequence in Web Browser
    ExecShell "open" "https://Avanishk05.github.io/QutritWebappV1"
SectionEnd

Section "Uninstall"
    ; Stop and delete service
    nsExec::ExecToLog 'sc stop LuckfoxFlasherAgent'
    Sleep 2000
    nsExec::ExecToLog 'sc delete LuckfoxFlasherAgent'
    
    ; Prune Firewall rules
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="LuckfoxFlasher"'
    
    ; Delete files
    RMDir /r "$INSTDIR"
SectionEnd
