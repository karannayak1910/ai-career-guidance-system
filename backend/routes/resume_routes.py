"""
Resume Ingestion & Parsing Routes Blueprint.
Accepts PDF and DOCX uploads, extracts text, identifies skills and education entities,
and returns structured fields for review.
"""
from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from ..resume_parser.parser import parse_resume_file

resume_bp = Blueprint("resume_bp", __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route("/api/resume/upload", methods=["POST"])
@resume_bp.route("/api/resume/parse", methods=["POST"])
def upload_and_parse_resume():
    """Upload resume and parse metadata and skills."""
    if "resume" not in request.files:
        return jsonify({"status": "error", "message": "No resume file attached"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Unsupported format. Only PDF and DOCX files are supported."}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    orig_name = secure_filename(file.filename)
    safe_name = f"{uuid.uuid4().hex[:8]}_{orig_name}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    try:
        file.save(file_path)
        extracted_data = parse_resume_file(file_path)
        extracted_data["resume_filename"] = orig_name

        try:
            os.remove(file_path)
        except Exception:
            pass

        return jsonify({
            "status": "success",
            "message": "Resume parsed successfully! Please review the extracted details.",
            "data": extracted_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to parse resume: {str(e)}"}), 500
