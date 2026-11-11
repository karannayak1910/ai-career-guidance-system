"""
Career Recommendations Blueprint.
Invokes the Hybrid Recommendation Engine and provides Top 3 matches,
career details, and Chart.js telemetry across all 15 technology roles.
"""
from flask import Blueprint, request, jsonify, session
from ..database.db import get_student_profile, get_latest_student_profile, save_recommendations, get_latest_recommendation
from ..ai_engine.matcher import CareerRecommendationEngine
from ..ai_engine.rule_engine import load_career_roles

recommendation_bp = Blueprint("recommendation_bp", __name__)
engine = CareerRecommendationEngine()
ALL_ROLES = load_career_roles()

@recommendation_bp.route("/api/recommendations/generate", methods=["POST"])
@recommendation_bp.route("/api/recommendations", methods=["POST"])
def generate_recommendations():
    """Run dynamic AI recommendation engine for student profile."""
    data = request.get_json() or {}
    student_id = data.get("student_id") or session.get("student_id")

    profile = None
    if student_id:
        try:
            profile = get_student_profile(int(student_id))
        except (ValueError, TypeError):
            profile = None

    if not profile and "full_name" in data:
        profile = data

    if not profile:
        profile = get_latest_student_profile()

    if not profile:
        return jsonify({
            "status": "error",
            "message": "No profile found to generate recommendations. Please complete your profile first."
        }), 404

    try:
        results = engine.recommend(profile)
        
        if profile.get("id"):
            save_recommendations(profile["id"], results)

        return jsonify({
            "status": "success",
            "student_id": profile.get("id"),
            "student_name": profile.get("full_name", "Student"),
            "top_3": results["top_3"],
            "all_ranked_roles": results["all_ranked_roles"],
            "disagreement_explanation": results.get("disagreement_explanation"),
            "ml_model_metrics": results.get("ml_model_metrics"),
            "radar_chart": results["radar_chart"]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"AI Engine error: {str(e)}"}), 500

@recommendation_bp.route("/api/recommendations/<int:student_id>", methods=["POST"])
def generate_recommendations_for_student(student_id):
    """Generate career recommendations for specific student ID."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404

    try:
        results = engine.recommend(profile)
        save_recommendations(student_id, results)

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "student_name": profile.get("full_name", "Student"),
            "top_3": results["top_3"],
            "all_ranked_roles": results["all_ranked_roles"],
            "disagreement_explanation": results.get("disagreement_explanation"),
            "ml_model_metrics": results.get("ml_model_metrics"),
            "radar_chart": results["radar_chart"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"AI Engine error: {str(e)}"}), 500

@recommendation_bp.route("/api/recommendations/<int:student_id>", methods=["GET"])
def get_recommendations_by_student_id(student_id):
    """Retrieve Top 3 career matches and recommendations for a specific student ID."""
    profile = get_student_profile(student_id)
    if not profile:
        return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404

    cached = get_latest_recommendation(student_id)
    if cached and cached.get("full_result"):
        full_res = cached["full_result"]
        return jsonify({
            "status": "success",
            "student_id": student_id,
            "cached": True,
            "top_3": full_res.get("top_3", []),
            "all_ranked_roles": full_res.get("all_ranked_roles", []),
            "disagreement_explanation": full_res.get("disagreement_explanation"),
            "ml_model_metrics": full_res.get("ml_model_metrics"),
            "radar_chart": full_res.get("radar_chart", {})
        }), 200

    results = engine.recommend(profile)
    save_recommendations(student_id, results)
    return jsonify({
        "status": "success",
        "student_id": student_id,
        "cached": False,
        "top_3": results["top_3"],
        "all_ranked_roles": results["all_ranked_roles"],
        "disagreement_explanation": results.get("disagreement_explanation"),
        "ml_model_metrics": results.get("ml_model_metrics"),
        "radar_chart": results["radar_chart"]
    }), 200

@recommendation_bp.route("/api/recommendations/latest", methods=["GET"])
def get_latest_recommendations():
    """Retrieve the latest cached recommendations for the active student."""
    student_id = request.args.get("student_id") or session.get("student_id")
    if not student_id:
        latest_profile = get_latest_student_profile()
        if latest_profile:
            student_id = latest_profile["id"]

    if not student_id:
        return jsonify({"status": "empty", "message": "No student profile found."}), 404

    return get_recommendations_by_student_id(int(student_id))

@recommendation_bp.route("/api/career/<role_id>", methods=["GET"])
def get_career_details(role_id):
    """Retrieve career details enriched with active student profile match data."""
    student_id = request.args.get("student_id") or session.get("student_id")
    profile = None
    if student_id:
        profile = get_student_profile(int(student_id))
    if not profile:
        profile = get_latest_student_profile()

    # Find the role
    target_role = None
    role_norm = role_id.lower().replace("-", "_")
    for r in ALL_ROLES:
        if (r["id"] == role_id or 
            r["id"].replace("-", "_") == role_norm or 
            r["title"].lower().replace(" ", "_") == role_norm or
            r["title"].lower() == role_id.lower()):
            target_role = r
            break

    if not target_role:
        return jsonify({"status": "error", "message": f"Career role '{role_id}' not found."}), 404

    if profile:
        results = engine.recommend(profile)
        for r in results["all_ranked_roles"]:
            if r["id"] == target_role["id"]:
                return jsonify({"status": "success", "career": r, "has_student_context": True}), 200

    # Fallback without student context
    return jsonify({
        "status": "success",
        "career": {
            **target_role,
            "match_score": 0,
            "why_matches": "Complete your profile to view personalized match percentages and explanations.",
            "next_steps": "Set up your student profile to analyze skill alignment.",
            "matched_skills": [],
            "missing_skills": target_role.get("required_skills", [])
        },
        "has_student_context": False
    }), 200
