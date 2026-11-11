"""
Mobile Access & Global Tunnel Manager for AI Career Guidance System.
Prioritizes Cloudflare Tunnel (trycloudflare.com) for fast, 24/7, zero-warning HTTPS access.
Falls back to SSH Serveo if needed. Automatically monitors, saves metadata, and reconnects.
"""
import os
import sys
import time
import json
import subprocess
import re
import socket

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INFO_FILE = os.path.join(ROOT_DIR, "data", "network_info.json")
CLOUDFLARED_EXE = os.path.join(ROOT_DIR, "bin", "cloudflared.exe")

def get_lan_ip():
    """Find local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def save_network_info(tunnel_url=None):
    lan_ip = get_lan_ip()
    chosen_url = tunnel_url if tunnel_url else f"http://{lan_ip}:5000"
    data = {
        "status": "success",
        "lan_ip": lan_ip,
        "port": 5000,
        "local_url": "http://127.0.0.1:5000",
        "lan_url": f"http://{lan_ip}:5000",
        "tunnel_url": chosen_url,
        "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={chosen_url}"
    }
    os.makedirs(os.path.dirname(INFO_FILE), exist_ok=True)
    with open(INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data

def run_cloudflared_tunnel():
    """Run Cloudflare Tunnel quick tunnel with automatic recovery."""
    cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:5000"]
    print("=" * 70)
    print("⚡ Launching Cloudflare 24/7 Edge Tunnel...")
    
    while True:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            tunnel_found = False
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                line_str = line.strip()
                match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line_str)
                if match and not tunnel_found:
                    tunnel_url = match.group(0)
                    save_network_info(tunnel_url)
                    tunnel_found = True
                    lan_ip = get_lan_ip()
                    print("\n" + "*" * 70)
                    print(f"🌟 PERMANENT 24/7 GLOBAL HTTPS URL:")
                    print(f"   {tunnel_url}")
                    print(f"📱 LOCAL WI-FI URL: http://{lan_ip}:5000")
                    print(f"💻 DESKTOP URL:     http://127.0.0.1:5000")
                    print("*" * 70 + "\n", flush=True)
            proc.wait()
            print("[Cloudflare] Tunnel exited. Restarting in 3 seconds...", flush=True)
            time.sleep(3)
        except Exception as e:
            print(f"[Cloudflare] Error: {e}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)

def run_ssh_serveo_tunnel():
    """Fallback SSH tunnel."""
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-R", "80:127.0.0.1:5000",
        "serveo.net"
    ]
    print("=" * 70)
    print("🌐 Launching Fallback SSH Tunnel (serveo.net)...")
    
    while True:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            tunnel_found = False
            for line in proc.stdout:
                line_str = line.strip()
                match = re.search(r"https://[a-zA-Z0-9\.\-_]+\.serveousercontent\.com", line_str)
                if match and not tunnel_found:
                    tunnel_url = match.group(0)
                    save_network_info(tunnel_url)
                    tunnel_found = True
                    print("\n" + "*" * 70)
                    print(f"📱 LIVE MOBILE ACCESS URL: {tunnel_url}")
                    print(f"📱 WI-FI LAN URL:          http://{get_lan_ip()}:5000")
                    print("*" * 70 + "\n")
            proc.wait()
            print("[Serveo] Tunnel disconnected. Reconnecting in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"[Serveo] Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def run_tunnel():
    """Main entry for tunnel management."""
    save_network_info()
    if os.path.exists(CLOUDFLARED_EXE):
        run_cloudflared_tunnel()
    else:
        run_ssh_serveo_tunnel()

if __name__ == "__main__":
    run_tunnel()
