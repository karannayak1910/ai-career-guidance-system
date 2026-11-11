"""
Authentication Routes Blueprint for AI Career Guidance System.
Handles User Registration, Login, Logout, and Session Verification with
Username, Password (hashed), Email, and Date of Birth (D.O.B).
"""
import re
from flask import Blueprint, request, jsonify, session
from ..database.db import create_user, authenticate_user, get_user_by_id, get_student_profile_by_user_id

auth_bp = Blueprint("auth_bp", __name__)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new student/user account."""
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    dob = str(data.get("dob", "")).strip()

    # Input validation
    errors = []
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters long.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("Please provide a valid email address.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")
    if not dob:
        errors.append("Please provide your Date of Birth (D.O.B).")

    if errors:
        return jsonify({"status": "error", "message": errors[0], "errors": errors}), 400

    user_id, err = create_user(username=username, email=email, password=password, dob=dob)
    if err:
        return jsonify({"status": "error", "message": err}), 409

    # Establish session
    session["user_id"] = user_id
    session["username"] = username
    session["email"] = email

    return jsonify({
        "status": "success",
        "message": f"Welcome, {username}! Your account has been registered successfully.",
        "user": {
            "id": user_id,
            "username": username,
            "email": email,
            "dob": dob
        }
    }), 201

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user with username/email and password."""
    data = request.get_json(silent=True) or {}
    identifier = str(data.get("username", "")).strip() or str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not identifier:
        return jsonify({"status": "error", "message": "Please enter your username or email."}), 400
    if not password:
        return jsonify({"status": "error", "message": "Please enter your password."}), 400

    user, err = authenticate_user(identifier, password)
    if err:
        return jsonify({"status": "error", "message": err}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["email"] = user.get("email", "")

    # Check for linked student profile
    student_profile = get_student_profile_by_user_id(user["id"])
    if student_profile:
        session["student_id"] = student_profile["id"]

    return jsonify({
        "status": "success",
        "message": f"Welcome back, {user['username']}!",
        "user": user,
        "has_profile": student_profile is not None
    }), 200

@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clear user session."""
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("email", None)
    session.pop("student_id", None)
    return jsonify({"status": "success", "message": "Signed out successfully."}), 200

@auth_bp.route("/api/auth/me", methods=["GET"])
def current_user():
    """Check authentication state of current session."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "status": "guest",
            "authenticated": False,
            "user": None
        }), 200

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({
            "status": "guest",
            "authenticated": False,
            "user": None
        }), 200

    profile = get_student_profile_by_user_id(user_id)
    return jsonify({
        "status": "success",
        "authenticated": True,
        "user": user,
        "has_profile": profile is not None,
        "profile": profile
    }), 200
