@echo off
title AI Career Guidance System - Auto-Start Setup
color 0A
cd /d "%~dp0"

echo ======================================================================
echo    INSTALLING 24/7 AUTO-START FOR AI CAREER GUIDANCE SYSTEM
echo ======================================================================
echo.
echo This will configure Windows to automatically launch the AI website
echo silently in the background whenever your computer boots up.
echo.

set "TARGET_SCRIPT=%~dp0run_hidden_24x7.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%STARTUP_FOLDER%\CareerAIServer.lnk'); $sc.TargetPath = 'wscript.exe'; $sc.Arguments = '\"%TARGET_SCRIPT%\"'; $sc.WorkingDirectory = '%~dp0'; $sc.Save()"

if exist "%STARTUP_FOLDER%\CareerAIServer.lnk" (
    echo [SUCCESS] Auto-start shortcut created successfully!
    echo Shortcut: %STARTUP_FOLDER%\CareerAIServer.lnk
    echo.
    echo The AI Career Guidance System will now launch silently in the
    echo background every time Windows boots up!
) else (
    echo [NOTICE] If prompt appears, allow PowerShell to create the shortcut.
)

echo.
pause
