"""
Chatbot Routes Blueprint for AI Career Guidance System.
Provides conversational AI guidance grounded in student profile, recommendations,
skill gaps, and career knowledge base.
"""
from flask import Blueprint, request, jsonify, session
from ..database.db import get_student_profile, get_latest_student_profile, get_latest_recommendation
from ..ai_engine.career_chatbot import CareerChatbot

chat_bp = Blueprint("chat_bp", __name__)
chatbot = CareerChatbot()

@chat_bp.route("/api/chat", methods=["POST"])
def chat_with_advisor():
    """Handle conversational career counseling requests."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"status": "error", "message": "Message cannot be empty."}), 400

    student_id = data.get("student_id") or session.get("student_id")
    profile = None
    if student_id:
        try:
            profile = get_student_profile(int(student_id))
        except (ValueError, TypeError):
            profile = None

    if not profile:
        profile = get_latest_student_profile()

    recommendations = None
    if profile and profile.get("id"):
        recommendations = get_latest_recommendation(profile["id"])
        if recommendations and "full_result" in recommendations:
            recommendations = recommendations["full_result"]

    try:
        response = chatbot.respond(
            message=message,
            student_profile=profile,
            recommendations=recommendations
        )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Chatbot error: {str(e)}"}), 500
