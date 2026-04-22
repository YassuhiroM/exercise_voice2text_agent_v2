@echo off
TITLE Close Voice2Text Agent
cd /d "%~dp0"

echo Stopping Voice2Text Agent...

REM Kill the python process running main.py
taskkill /F /FI "WINDOWTITLE eq Voice-to-Text Agent Launcher" /T >nul 2>&1

REM Also kill any python process running main.py directly
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /i "PID"') do (
  wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /i "main.py" >nul
  if not errorlevel 1 (
    taskkill /F /PID %%i >nul 2>&1
    echo Agent process (PID %%i) terminated.
  )
)

echo Done.
timeout /t 2 /nobreak >nul
