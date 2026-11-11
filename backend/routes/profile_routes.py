"""
Profile Routes Blueprint.
Handles saving, updating, retrieving student profiles, and serving skills taxonomy catalog.
"""
from flask import Blueprint, request, jsonify, session
import os
import json
from ..database.db import save_student_profile, get_student_profile, get_latest_student_profile, get_student_profile_by_user_id
from ..models.student import StudentProfile

profile_bp = Blueprint("profile_bp", __name__)

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_skills.json")

@profile_bp.route("/api/skills/catalog", methods=["GET"])
def get_skills_catalog():
    """Return categorized skill catalog for UI tags and autocomplete."""
    if os.path.exists(SKILLS_PATH):
        try:
            with open(SKILLS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return jsonify({"status": "success", "catalog": data.get("skills", {})})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "success", "catalog": {}})

@profile_bp.route("/api/profile", methods=["POST"])
@profile_bp.route("/api/profile/save", methods=["POST"])
def save_profile():
    """Validate and persist student profile."""
    data = request.get_json() or {}
    
    student = StudentProfile.from_dict(data)
    errors = student.validate()
    if errors:
        return jsonify({"status": "error", "errors": errors, "message": "Validation failed"}), 400

    student_dict = student.to_dict()
    # Attach authenticated user_id if logged in
    user_id = session.get("user_id") or data.get("user_id")
    if user_id:
        student_dict["user_id"] = user_id

    try:
        student_id = save_student_profile(student_dict)
        session["student_id"] = student_id
        return jsonify({
            "status": "success",
            "message": "Student profile saved successfully!",
            "student_id": student_id,
            "profile": student_dict
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

@profile_bp.route("/api/profile/current", methods=["GET"])
def get_current_profile():
    """Get active student profile from session or fallback to latest record."""
    user_id = session.get("user_id")
    profile = None
    if user_id:
        profile = get_student_profile_by_user_id(user_id)

    if not profile:
        student_id = session.get("student_id") or request.args.get("student_id")
        if student_id:
            try:
                profile = get_student_profile(int(student_id))
            except (ValueError, TypeError):
                profile = None

    if not profile:
        profile = get_latest_student_profile()

    if not profile:
        return jsonify({"status": "empty", "message": "No profile found. Please register."}), 404

    return jsonify({"status": "success", "profile": profile}), 200

    if not profile:
        profile = get_latest_student_profile()

    if not profile:
        return jsonify({"status": "empty", "message": "No profile found. Please register."}), 404

    return jsonify({"status": "success", "profile": profile}), 200

@profile_bp.route("/api/profile/<int:student_id>", methods=["GET"])
def get_profile_by_id(student_id):
    """Get student profile by specific ID."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404
    return jsonify({"status": "success", "profile": profile}), 200
