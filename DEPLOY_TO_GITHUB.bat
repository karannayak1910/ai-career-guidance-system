@echo off
title Deploy AI Career Guidance System to GitHub
color 0A
cd /d "%~dp0"

echo ======================================================================
echo       AUTOMATIC GITHUB DEPLOYMENT - AI CAREER GUIDANCE SYSTEM
echo ======================================================================
echo.

if not exist "bin\gh.exe" (
    echo [ERROR] GitHub CLI helper not found in bin\gh.exe.
    pause
    exit /b 1
)

echo [1/3] Checking GitHub Authentication...
.\bin\gh.exe auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ------------------------------------------------------------------
    echo  GitHub login required.
    echo  A browser window will open at https://github.com/login/device
    echo  Please enter the one-time code shown below in your browser.
    echo ------------------------------------------------------------------
    echo.
    .\bin\gh.exe auth login --hostname github.com --git-protocol https --web
)

echo.
echo [2/3] Checking / Creating GitHub Repository 'ai-career-guidance-system'...
.\bin\gh.exe repo view karannayak1910/ai-career-guidance-system >nul 2>&1
if %errorlevel% equ 0 (
    echo Repository 'karannayak1910/ai-career-guidance-system' already exists on GitHub.
    echo Configuring git remote origin...
    git remote remove origin 2>nul
    git remote add origin https://github.com/karannayak1910/ai-career-guidance-system.git
    echo Pushing latest code to main...
    git branch -M main
    git push -u origin main
) else (
    echo Creating public repository 'ai-career-guidance-system' and pushing code...
    .\bin\gh.exe repo create ai-career-guidance-system --public --source=. --remote=origin --push
)

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  [SUCCESS] PROJECT DEPLOYED TO GITHUB!
    echo ======================================================================
    echo.
    echo  Repository URL:
    echo  https://github.com/karannayak1910/ai-career-guidance-system
    echo.
    echo  Now you can link this GitHub repo to Render.com with 1-click:
    echo  1. Open https://dashboard.render.com
    echo  2. Click "New +" -^> "Web Service"
    echo  3. Select "ai-career-guidance-system"
    echo  4. Click "Create Web Service"
    echo.
    start "" "https://github.com/karannayak1910/ai-career-guidance-system"
) else (
    echo.
    echo [ERROR] Deployment failed. Please check the error message above.
)

echo.
pause
