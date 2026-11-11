# 24/7 Free Cloud Deployment Guide for AI Career Guidance System

This guide explains how to host your **AI Career Guidance System** on a free cloud provider so it is accessible **24 hours a day, 365 days a year, from any device, anywhere in the world** — even when your personal laptop or computer is turned off.

---

## Option 1: Deploy on Render.com (Recommended - 100% Free)

Render provides free cloud web services with automatic HTTPS SSL certificates.

### Step 1: Create a GitHub Repository
1. Go to [github.com](https://github.com) and create a new repository named `ai-career-guidance-system`.
2. Push your project code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for AI Career Guidance System"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-career-guidance-system.git
   git push -u origin main
   ```

### Step 2: Connect to Render
1. Go to [render.com](https://render.com) and create a free account.
2. Click **New +** and select **Web Service**.
3. Select your GitHub repository `ai-career-guidance-system`.
4. Configure the settings:
   - **Name:** `ai-career-guidance-system`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app --workers 2 --threads 4 --timeout 120`
   - **Plan:** Free
5. Click **Create Web Service**.

Your app will be live within 2 minutes at:
`https://ai-career-guidance-system.onrender.com`

---

## Option 2: Deploy on Railway.app

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `ai-career-guidance-system`.
4. Railway will automatically detect the `Procfile` and deploy your app.
5. In **Settings** -> **Domains**, click **Generate Domain** to get your permanent 24/7 HTTPS URL.

---

## Option 3: Run 24/7 on Your Local Windows PC

If you prefer to host locally from your Windows computer without cloud platforms:

1. **Keep it running silently in the background:**
   Double-click `run_hidden_24x7.vbs`. It runs Python and the Cloudflare Tunnel without any console window.
2. **Auto-start on Windows boot:**
   Double-click `INSTALL_AUTOSTART_ON_BOOT.bat`. This automatically adds the launcher to your Windows Startup folder so it boots up whenever Windows starts.
3. **One-Click Manual Launch:**
   Double-click `START_WEBSITE_NOW.bat`. It starts the application and opens your default browser automatically.
