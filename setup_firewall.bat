@echo off
title Allow Port 5000 in Windows Firewall
echo ======================================================================
echo           OPENING PORT 5000 FOR MOBILE WI-FI ACCESS
echo ======================================================================
echo.
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo Please right click this file and select "Run as administrator".
    pause
    exit /b 1
)

netsh advfirewall firewall add rule name="AI Career Guidance System Port 5000" dir=in action=allow protocol=TCP localport=5000
echo.
echo [SUCCESS] Port 5000 is now open!
echo Any mobile device on your Wi-Fi network can now visit your computer's IP on port 5000.
echo.
pause
