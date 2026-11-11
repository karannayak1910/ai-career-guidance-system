"""
Root runner for AI Career Guidance System.
Allows running directly from workspace root using:
python run.py
"""
import sys
import os
import socket
import threading

# Set root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from backend.app import app
from backend.utils.tunnel_manager import run_tunnel, save_network_info, get_lan_ip

def find_available_port(preferred_port=5000):
    for port in [preferred_port, 5050, 8080, 8000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    return preferred_port

if __name__ == "__main__":
    port = find_available_port(5000)
    lan_ip = get_lan_ip()
    
    # Pre-save local network info
    save_network_info()
    
    # Start auto-reconnecting mobile tunnel in background daemon thread
    tunnel_thread = threading.Thread(target=run_tunnel, daemon=True)
    tunnel_thread.start()

    print("\n" + "=" * 70)
    print("🚀 AI Career Guidance System is running!")
    print(f"📍 External / Desktop Browser:  http://127.0.0.1:{port}")
    print(f"📍 Localhost Browser:           http://localhost:{port}")
    print("📱 24/7 Cloud & Mobile Link:    https://ai-career-guidance-system-fm0s.onrender.com/")
    print(f"📱 Mobile Phone (Local Wi-Fi):  http://{lan_ip}:{port}")
    print("=" * 70)
    print("💡 Mobile Phone Access:")
    print("   • Live Cloud (Any Device / Any Network): https://ai-career-guidance-system-fm0s.onrender.com/")
    print(f"   • On Local Wi-Fi: open http://{lan_ip}:{port}")
    print("=" * 70 + "\n")
    
    # Bind to 0.0.0.0 to enable access from internal/external browsers and mobile phones
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
