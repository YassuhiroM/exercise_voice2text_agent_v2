@echo off
TITLE Close Voice2Text Agent
cd /d "%~dp0"

echo Stopping Voice2Text Agent...

REM Kill the python process running main.py
taskkill /F /FI "WINDOWTITLE eq Voice-to-Text Agent Launcher" /T >nul 2>&1

REM Also kill any python process running main.py directly (uses Get-CimInstance, wmic is deprecated on Windows 11)
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*main.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host ('Agent process (PID ' + $_.ProcessId + ') terminated.') }"

echo Done.
timeout /t 2 /nobreak >nul
