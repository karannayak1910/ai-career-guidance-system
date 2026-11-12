"""
Resume Ingestion & Parsing Routes Blueprint.
Accepts PDF and DOCX uploads, extracts text, identifies skills and education entities,
and returns structured fields for review.
"""
from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from ..resume_parser.parser import parse_resume_file, parse_resume_text

resume_bp = Blueprint("resume_bp", __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route("/api/resume/upload", methods=["POST"])
@resume_bp.route("/api/resume/parse", methods=["POST"])
def upload_and_parse_resume():
    """
    Parse resume from either:
    1. Uploaded PDF/DOCX/TXT file (via multipart/form-data 'resume')
    2. Raw pasted resume text (via JSON or form 'resume_text')
    """
    # Option A: Check for pasted text in JSON or form-data
    resume_text = None
    if request.is_json:
        data = request.get_json() or {}
        resume_text = data.get("resume_text")
    elif "resume_text" in request.form:
        resume_text = request.form.get("resume_text")

    if resume_text and resume_text.strip():
        try:
            extracted_data = parse_resume_text(resume_text.strip())
            extracted_data["resume_filename"] = "Pasted_Resume_Text.txt"
            return jsonify({
                "status": "success",
                "message": "Resume text parsed successfully! Extracted details populated into form.",
                "data": extracted_data
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to parse resume text: {str(e)}"}), 500

    # Option B: Check for uploaded file
    if "resume" not in request.files:
        return jsonify({
            "status": "error", 
            "message": "No resume file or resume text provided. Please upload a PDF/DOCX resume or paste your resume text."
        }), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error", 
            "message": "Unsupported format. Only PDF, DOCX, and TXT files are supported."
        }), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    orig_name = secure_filename(file.filename) or "uploaded_resume.pdf"
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
            "message": "Resume parsed successfully! Extracted details populated into form.",
            "data": extracted_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to parse resume: {str(e)}"}), 500
