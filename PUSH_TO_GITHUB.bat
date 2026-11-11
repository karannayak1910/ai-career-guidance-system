@echo off
title Push AI Career Guidance System to GitHub for Render Deployment
color 0B
cd /d "%~dp0"

echo ======================================================================
echo    PUSH TO GITHUB FOR AUTOMATIC RENDER.COM DEPLOYMENT
echo ======================================================================
echo.
echo Step 1: Make sure you have created an empty repository on GitHub:
echo         https://github.com/new
echo         Repository name recommendation: ai-career-guidance-system
echo.
echo Step 2: Enter your GitHub Repository URL below.
echo Example: https://github.com/karannayak1910/ai-career-guidance-system.git
echo.
set /p REPO_URL="Enter your GitHub Repository URL: "

if "%REPO_URL%"=="" (
    set "REPO_URL=https://github.com/karannayak1910/ai-career-guidance-system.git"
)

echo.
echo Linking to: %REPO_URL% ...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo Pushing code to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo [SUCCESS] Code successfully pushed to GitHub!
    echo ======================================================================
    echo.
    echo Now open Render to deploy with 1-click:
    echo 1. Go to: https://dashboard.render.com
    echo 2. Click "New +" -^> "Web Service"
    echo 3. Select your repository: ai-career-guidance-system
    echo 4. Click "Deploy Web Service"
    echo.
    echo Render will build and give you your permanent 24/7 link!
) else (
    echo.
    echo [NOTICE] If prompted for GitHub login, please sign in or use a GitHub Personal Access Token.
)

echo.
pause
