@echo off
title AI Career Guidance System - Server & Mobile Cloudflare Tunnel
color 0A
cd /d "%~dp0"

echo ======================================================================
echo           AI CAREER GUIDANCE SYSTEM - 24/7 LAUNCHER
echo ======================================================================
echo.
echo [1/3] Checking Python Virtual Environment...
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please create it using: python -m venv .venv
    pause
    exit /b 1
)

echo [2/3] Starting AI Server and Cloudflare Edge Tunnel...
start "" "http://127.0.0.1:5000"

echo [3/3] Application is launching... Keep this terminal open!
echo.
.\.venv\Scripts\python.exe run.py

pause
