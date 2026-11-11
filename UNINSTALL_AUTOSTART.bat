@echo off
title AI Career Guidance System - Remove Auto-Start
color 0C
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\CareerAIServer.vbs"

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo [SUCCESS] Auto-start script removed from Windows startup.
) else (
    echo Auto-start script was not found in Windows startup.
)
pause
