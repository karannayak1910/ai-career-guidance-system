@echo off
title AI Career Guidance System - Server & Mobile Cloudflare Tunnel
color 0B
cd /d "%~dp0"

echo ======================================================================
echo           AI CAREER GUIDANCE SYSTEM - 24/7 LAUNCHER
echo ======================================================================
echo.
echo [1/3] Verifying Python Environment...
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found!
    echo Please install dependencies first.
    pause
    exit /b 1
)

echo [2/3] Opening browser...
start "" "http://127.0.0.1:5000"

echo [3/3] Starting AI Engine, Flask Backend, and Cloudflare 24/7 Edge Tunnel...
echo.
echo ----------------------------------------------------------------------
echo  IMPORTANT: Keep this window open while using the website!
echo  To run invisibly in the background, double-click run_hidden_24x7.vbs
echo ----------------------------------------------------------------------
echo.

.\.venv\Scripts\python.exe -u run.py

pause
