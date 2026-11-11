"""
Main Flask Application for AI Career Guidance System.
Serves both REST APIs and Frontend Single/Multi-Page interfaces.
"""
import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, send_from_directory, render_template, jsonify
from backend.database.db import init_db
from backend.ai_engine.decision_tree_model import get_decision_tree_model
from backend.routes import profile_bp, resume_bp, recommendation_bp, roadmap_bp, chat_bp, auth_bp

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    template_folder=FRONTEND_DIR
)
app.secret_key = "career-guidance-ai-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size

# Register REST Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(roadmap_bp)
app.register_blueprint(chat_bp)

# Frontend Page Routes
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/login")
def serve_login():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/profile")
def serve_profile():
    return send_from_directory(FRONTEND_DIR, "profile.html")

@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

@app.route("/recommendations")
def serve_recommendations():
    return send_from_directory(FRONTEND_DIR, "recommendations.html")

@app.route("/skill-gap")
def serve_skill_gap():
    return send_from_directory(FRONTEND_DIR, "skill_gap.html")

@app.route("/career-details")
def serve_career_details():
    return send_from_directory(FRONTEND_DIR, "career_details.html")

@app.route("/roadmap")
def serve_roadmap():
    return send_from_directory(FRONTEND_DIR, "roadmap.html")

# Static assets router
@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "assets"), filename)

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "AI Career Guidance System API",
        "version": "1.0.0"
    }), 200

@app.route("/api/system/network-info", methods=["GET"])
def network_info():
    official_cloud_url = os.environ.get("RENDER_EXTERNAL_URL") or "https://ai-career-guidance-system-fm0s.onrender.com/"
    if not official_cloud_url.endswith("/"):
        official_cloud_url += "/"

    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = "127.0.0.1"

    data = {
        "status": "success",
        "cloud_url": official_cloud_url,
        "mobile_url": official_cloud_url,
        "tunnel_url": official_cloud_url,
        "local_url": "http://127.0.0.1:5000",
        "lan_url": f"http://{lan_ip}:5000",
        "lan_ip": lan_ip,
        "port": 5000,
        "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={official_cloud_url}"
    }

    info_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "network_info.json"))
    try:
        os.makedirs(os.path.dirname(info_file), exist_ok=True)
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

    return jsonify(data), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# Initialize subsystem components
with app.app_context():
    init_db()
    try:
        get_decision_tree_model()
    except Exception as e:
        print("Warning: Decision Tree pre-training notice:", e)

if __name__ == "__main__":
    print("=" * 65)
    print("AI Career Guidance System running at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)
