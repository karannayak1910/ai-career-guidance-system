"""
Skill Gap Analysis and Learning Roadmap Blueprint.
Provides detailed skill diagnostics and monthly interactive milestones with free resources.
Integrates with SQLite skill_gap_analysis, learning_roadmaps, and roadmap_progress tables.
"""
from flask import Blueprint, request, jsonify, session
from ..database.db import (
    get_student_profile, get_latest_student_profile, toggle_roadmap_task,
    get_roadmap_progress, save_skill_gap_analysis, get_latest_skill_gap_analysis,
    save_learning_roadmap_record, get_learning_roadmap_record, get_latest_recommendation
)
from ..ai_engine.skill_gap_analyzer import SkillGapAnalyzer
from ..ai_engine.roadmap_generator import RoadmapGenerator

roadmap_bp = Blueprint("roadmap_bp", __name__)
gap_analyzer = SkillGapAnalyzer()
roadmap_generator = RoadmapGenerator()

def get_current_student(req):
    """Helper to resolve active student profile from request or session."""
    student_id = req.args.get("student_id") or session.get("student_id")
    if student_id:
        try:
            return get_student_profile(int(student_id))
        except (ValueError, TypeError):
            pass
    return get_latest_student_profile()

def get_target_role_for_student(student_id, preferred_role=None):
    """Resolve target career role ID, defaulting to student's #1 match."""
    if preferred_role:
        return preferred_role
    recs = get_latest_recommendation(student_id)
    if recs and recs.get("full_result") and recs["full_result"].get("top_3"):
        return recs["full_result"]["top_3"][0]["id"]
    return "software_engineer"

# 1. Skill Gap for Student ID
@roadmap_bp.route("/api/skill-gap/<int:student_id>", methods=["GET"])
def get_skill_gap_by_student_id(student_id):
    """Retrieve skill-gap analysis for a specific student ID."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404

    role_id = request.args.get("role_id") or get_target_role_for_student(student_id)

    try:
        gap_data = gap_analyzer.analyze(profile, role_id)
        if "error" in gap_data:
            return jsonify({"status": "error", "message": gap_data["error"]}), 404

        save_skill_gap_analysis(student_id, gap_data["role_id"], gap_data)

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "data": gap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Skill gap analysis failed: {str(e)}"}), 500

# Skill Gap by Role ID (frontend tab switching)
@roadmap_bp.route("/api/skill-gap/<role_id>", methods=["GET"])
def get_skill_gap(role_id):
    """Run skill gap analysis for active student against target career role."""
    profile = get_current_student(request)
    if not profile:
        return jsonify({"status": "error", "message": "No active student profile found. Please register first."}), 404

    try:
        gap_data = gap_analyzer.analyze(profile, role_id)
        if "error" in gap_data:
            return jsonify({"status": "error", "message": gap_data["error"]}), 404

        if profile.get("id"):
            save_skill_gap_analysis(profile["id"], gap_data["role_id"], gap_data)

        return jsonify({
            "status": "success",
            "student_id": profile.get("id"),
            "data": gap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Skill gap analysis failed: {str(e)}"}), 500

# 2. Roadmap Generation for Student ID
@roadmap_bp.route("/api/roadmap/<int:student_id>", methods=["POST"])
def generate_roadmap_for_student(student_id):
    """Generate personalized learning roadmap for student."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404

    data = request.get_json(silent=True) or {}
    role_id = data.get("role_id") or request.args.get("role_id") or get_target_role_for_student(student_id)

    try:
        roadmap_data = roadmap_generator.generate(profile, role_id)
        if "error" in roadmap_data:
            return jsonify({"status": "error", "message": roadmap_data["error"]}), 404

        save_learning_roadmap_record(student_id, roadmap_data["role_id"], roadmap_data)

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "data": roadmap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Roadmap generation failed: {str(e)}"}), 500

# Roadmap Retrieval for Student ID
@roadmap_bp.route("/api/roadmap/<int:student_id>", methods=["GET"])
def get_roadmap_by_student_id(student_id):
    """Retrieve learning roadmap for student."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404

    role_id = request.args.get("role_id") or get_target_role_for_student(student_id)

    try:
        roadmap_data = roadmap_generator.generate(profile, role_id)
        if "error" in roadmap_data:
            return jsonify({"status": "error", "message": roadmap_data["error"]}), 404

        save_learning_roadmap_record(student_id, roadmap_data["role_id"], roadmap_data)

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "data": roadmap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Roadmap retrieval failed: {str(e)}"}), 500

# Roadmap by Role ID (frontend tab switching)
@roadmap_bp.route("/api/roadmap/<role_id>", methods=["GET"])
def get_learning_roadmap(role_id):
    """Generate personalized 4-month learning roadmap for active student."""
    profile = get_current_student(request)
    if not profile:
        return jsonify({"status": "error", "message": "No active student profile found. Please register first."}), 404

    try:
        roadmap_data = roadmap_generator.generate(profile, role_id)
        if "error" in roadmap_data:
            return jsonify({"status": "error", "message": roadmap_data["error"]}), 404

        if profile.get("id"):
            save_learning_roadmap_record(profile["id"], roadmap_data["role_id"], roadmap_data)

        return jsonify({
            "status": "success",
            "student_id": profile.get("id"),
            "data": roadmap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Learning roadmap failed: {str(e)}"}), 500

# 3. Roadmap Progress Toggle
@roadmap_bp.route("/api/roadmap/progress", methods=["POST"])
@roadmap_bp.route("/api/roadmap/task/toggle", methods=["POST"])
def toggle_task_progress():
    """Toggle completed state of a roadmap checklist task."""
    data = request.get_json() or {}
    student_id = data.get("student_id") or session.get("student_id")

    if not student_id:
        latest = get_latest_student_profile()
        if latest:
            student_id = latest["id"]

    if not student_id:
        return jsonify({"status": "error", "message": "No student profile context found."}), 400

    career_role = data.get("career_role")
    task_id = data.get("task_id")
    is_completed = bool(data.get("is_completed", False))
    milestone_month = int(data.get("milestone_month", 1))

    if not career_role or not task_id:
        return jsonify({"status": "error", "message": "Missing career_role or task_id."}), 400

    try:
        toggle_roadmap_task(int(student_id), career_role, task_id, is_completed, milestone_month)
        all_tasks = get_roadmap_progress(int(student_id), career_role)

        completed_count = sum(1 for v in all_tasks.values() if v)
        total_tasks = 16  # 4 tasks per month * 4 months
        overall_progress = round((completed_count / total_tasks) * 100, 1)

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "career_role": career_role,
            "task_id": task_id,
            "is_completed": is_completed,
            "completed_count": completed_count,
            "total_tasks": total_tasks,
            "overall_progress_percentage": overall_progress
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to update task: {str(e)}"}), 500
