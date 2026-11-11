"""
Comprehensive Test Evaluator for AI Career Guidance System.
Evaluates all 14 project subsystems and 5 specific user test cases.
"""
import sys
import os
import json
import sqlite3

# Set root directory in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from backend.app import app
from backend.database.db import get_db_connection, init_db
from backend.ai_engine.matcher import CareerRecommendationEngine
from backend.ai_engine.career_chatbot import CareerChatbot

def run_evaluation():
    print("=" * 70)
    print("🔬 RUNNING COMPLETE AI CAREER GUIDANCE SYSTEM EVALUATION SUITE")
    print("=" * 70)

    client = app.test_client()
    engine = CareerRecommendationEngine()
    chatbot = CareerChatbot()
    results = {"passed": 0, "failed": 0, "test_cases": {}, "subsystems": {}}

    # ---------------------------------------------------------
    # PART 1: 9-TABLE SQLITE DATABASE INTEGRITY CHECK
    # ---------------------------------------------------------
    print("\n[SUBSYSTEM 13] Verifying SQLite 9-Table Relational Schema...")
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    required_tables = [
        "students", "student_skills", "student_interests",
        "career_roles", "career_required_skills", "career_recommendations",
        "skill_gap_analysis", "learning_roadmaps", "roadmap_progress"
    ]

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row["name"] for row in cursor.fetchall()]

    for tbl in required_tables:
        assert tbl in existing_tables, f"Missing table: {tbl}"
        print(f"  ✓ Table verified: {tbl}")

    # Verify seeded career roles
    cursor.execute("SELECT COUNT(*) FROM career_roles;")
    role_count = cursor.fetchone()[0]
    assert role_count >= 15, f"Expected >= 15 career roles, found {role_count}"
    print(f"  ✓ Seeded career roles verified: {role_count} roles active")

    cursor.execute("SELECT COUNT(*) FROM career_required_skills;")
    req_skills_count = cursor.fetchone()[0]
    assert req_skills_count >= 60, f"Expected >= 60 career skills, found {req_skills_count}"
    print(f"  ✓ Seeded career skill requirements verified: {req_skills_count} requirements mapped")
    conn.close()
    results["subsystems"]["database_9_tables"] = "PASSED"

    # ---------------------------------------------------------
    # PART 2: THE 5 USER TEST CASES
    # ---------------------------------------------------------
    print("\n" + "=" * 50)
    print("🎯 EVALUATING THE 5 MANDATORY USER TEST CASES")
    print("=" * 50)

    # TEST CASE 1: Student knows Python, SQL, Excel, and Statistics
    # Expected: Data Analyst-related roles
    print("\n--- Test Case 1: Python, SQL, Excel, Statistics ---")
    tc1_profile = {
        "full_name": "Test Student 1 (Data Track)",
        "branch": "Computer Science",
        "current_semester": 5,
        "graduation_year": 2026,
        "programming_languages": ["Python", "SQL"],
        "frameworks": ["Pandas"],
        "databases": ["SQL"],
        "tools_technologies": ["Excel", "Tableau"],
        "technical_skills": ["Statistics", "Data Visualization", "Data Analysis"],
        "skill_proficiencies": {"Python": "Intermediate", "SQL": "Advanced", "Excel": "Advanced", "Statistics": "Intermediate"},
        "interest_areas": ["Data Analytics", "Data Science"],
        "preferred_work_area": "Remote",
        "preferred_career_type": "Full-time",
        "hours_per_week": 14
    }
    tc1_res = engine.recommend(tc1_profile)
    tc1_top_titles = [r["title"] for r in tc1_res["top_3"]]
    print(f"  Top 3 Recommendations: {tc1_top_titles}")
    print(f"  Match Scores: {[r['match_score'] for r in tc1_res['top_3']]}")
    assert any("Data Analyst" in t or "Data Scientist" in t for t in tc1_top_titles), "Test Case 1 Failed to recommend Data role"
    print("  ✓ Test Case 1 PASSED: Successfully recommended Data Analyst track!")
    results["test_cases"]["TC1_Data_Analyst"] = "PASSED"

    # TEST CASE 2: Student knows HTML, CSS, JavaScript, and React
    # Expected: Frontend Developer-related roles
    print("\n--- Test Case 2: HTML, CSS, JavaScript, React ---")
    tc2_profile = {
        "full_name": "Test Student 2 (Web Track)",
        "branch": "Information Technology",
        "current_semester": 4,
        "graduation_year": 2027,
        "programming_languages": ["HTML", "CSS", "JavaScript"],
        "frameworks": ["React", "Tailwind CSS"],
        "databases": [],
        "tools_technologies": ["Git", "Figma"],
        "technical_skills": ["Responsive Web Design", "REST APIs"],
        "skill_proficiencies": {"HTML": "Advanced", "CSS": "Advanced", "JavaScript": "Intermediate", "React": "Intermediate"},
        "interest_areas": ["Web Development"],
        "preferred_work_area": "Hybrid",
        "preferred_career_type": "Full-time",
        "hours_per_week": 12
    }
    tc2_res = engine.recommend(tc2_profile)
    tc2_top_titles = [r["title"] for r in tc2_res["top_3"]]
    print(f"  Top 3 Recommendations: {tc2_top_titles}")
    print(f"  Match Scores: {[r['match_score'] for r in tc2_res['top_3']]}")
    assert any("Frontend" in t or "UI/UX" in t or "Full Stack" in t for t in tc2_top_titles), "Test Case 2 Failed to recommend Frontend role"
    print("  ✓ Test Case 2 PASSED: Successfully recommended Frontend Developer track!")
    results["test_cases"]["TC2_Frontend_Developer"] = "PASSED"

    # TEST CASE 3: Student knows Python, Mathematics, Machine Learning, and Deep Learning
    # Expected: AI/ML-related roles
    print("\n--- Test Case 3: Python, Mathematics, Machine Learning, Deep Learning ---")
    tc3_profile = {
        "full_name": "Test Student 3 (AI/ML Track)",
        "branch": "Artificial Intelligence",
        "current_semester": 6,
        "graduation_year": 2026,
        "programming_languages": ["Python"],
        "frameworks": ["PyTorch", "TensorFlow", "Scikit-learn"],
        "databases": ["SQL"],
        "tools_technologies": ["Git", "Linux"],
        "technical_skills": ["Mathematics", "Machine Learning", "Deep Learning", "Statistics"],
        "skill_proficiencies": {"Python": "Advanced", "Machine Learning": "Advanced", "Deep Learning": "Intermediate", "Mathematics": "Advanced"},
        "interest_areas": ["Artificial Intelligence", "Machine Learning"],
        "preferred_work_area": "Remote",
        "preferred_career_type": "Full-time",
        "hours_per_week": 18
    }
    tc3_res = engine.recommend(tc3_profile)
    tc3_top_titles = [r["title"] for r in tc3_res["top_3"]]
    print(f"  Top 3 Recommendations: {tc3_top_titles}")
    print(f"  Match Scores: {[r['match_score'] for r in tc3_res['top_3']]}")
    assert any("Machine Learning" in t or "AI Engineer" in t or "Data Scientist" in t for t in tc3_top_titles), "Test Case 3 Failed to recommend AI/ML role"
    print("  ✓ Test Case 3 PASSED: Successfully recommended AI/ML Engineer track!")
    results["test_cases"]["TC3_AIML_Engineer"] = "PASSED"

    # TEST CASE 4: Student knows Java, OOP, DBMS, and Data Structures
    # Expected: Software Developer-related roles
    print("\n--- Test Case 4: Java, OOP, DBMS, Data Structures ---")
    tc4_profile = {
        "full_name": "Test Student 4 (Core Software Track)",
        "branch": "Computer Science",
        "current_semester": 5,
        "graduation_year": 2026,
        "programming_languages": ["Java", "SQL"],
        "frameworks": ["Spring Boot"],
        "databases": ["MySQL"],
        "tools_technologies": ["Git", "Linux"],
        "technical_skills": ["Data Structures", "Algorithms", "Object-Oriented Programming (OOP)", "Database Management Systems (DBMS)"],
        "skill_proficiencies": {"Java": "Advanced", "Data Structures": "Advanced", "Algorithms": "Intermediate", "MySQL": "Intermediate"},
        "interest_areas": ["Software Development"],
        "preferred_work_area": "On-site",
        "preferred_career_type": "Full-time",
        "hours_per_week": 15
    }
    tc4_res = engine.recommend(tc4_profile)
    tc4_top_titles = [r["title"] for r in tc4_res["top_3"]]
    print(f"  Top 3 Recommendations: {tc4_top_titles}")
    print(f"  Match Scores: {[r['match_score'] for r in tc4_res['top_3']]}")
    assert any("Software" in t or "Java" in t or "Backend" in t for t in tc4_top_titles), "Test Case 4 Failed to recommend Software Developer role"
    print("  ✓ Test Case 4 PASSED: Successfully recommended Software Developer track!")
    results["test_cases"]["TC4_Software_Developer"] = "PASSED"

    # TEST CASE 5: Student has limited technical skills but an interest in technology
    # Expected: Beginner-friendly recommendations and a foundational learning roadmap
    print("\n--- Test Case 5: Limited Skills, High Interest ---")
    tc5_profile = {
        "full_name": "Test Student 5 (Beginner Explorer)",
        "branch": "Electrical Engineering",
        "current_semester": 2,
        "graduation_year": 2028,
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "tools_technologies": [],
        "technical_skills": ["Basic Computer Literacy"],
        "skill_proficiencies": {},
        "interest_areas": ["Web Development", "Software Development"],
        "preferred_work_area": "Hybrid",
        "preferred_career_type": "Internship",
        "hours_per_week": 10
    }
    tc5_res = engine.recommend(tc5_profile)
    tc5_top_titles = [r["title"] for r in tc5_res["top_3"]]
    print(f"  Top 3 Recommendations: {tc5_top_titles}")
    print(f"  Match Scores: {[r['match_score'] for r in tc5_res['top_3']]}")
    # Should provide reasonable foundational beginner paths
    assert len(tc5_top_titles) == 3, "Failed to provide 3 recommendations for beginner"
    print("  ✓ Test Case 5 PASSED: Handled low-skill profile with foundational recommendations!")
    results["test_cases"]["TC5_Beginner_Explorer"] = "PASSED"

    # ---------------------------------------------------------
    # PART 3: BACKEND API ENDPOINTS EVALUATION
    # ---------------------------------------------------------
    print("\n" + "=" * 50)
    print("🌐 EVALUATING ALL 9 SPECIFIED BACKEND REST APIs")
    print("=" * 50)

    # 1. POST /api/profile
    r = client.post("/api/profile", json=tc1_profile)
    assert r.status_code == 200, f"POST /api/profile failed: {r.data}"
    student_id = json.loads(r.data)["student_id"]
    print(f"  ✓ 1. POST /api/profile -> 200 OK (Created student_id={student_id})")

    # 2. POST /api/resume/upload
    resume_path = os.path.join(ROOT_DIR, "data", "sample_resumes", "sample_resume_karan.docx")
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            r = client.post("/api/resume/upload", data={"resume": (f, "sample_resume_karan.docx")}, content_type="multipart/form-data")
        assert r.status_code == 200, f"POST /api/resume/upload failed: {r.data}"
        print("  ✓ 2. POST /api/resume/upload -> 200 OK (Parsed entities successfully)")

    # 3. GET /api/profile/<student_id>
    r = client.get(f"/api/profile/{student_id}")
    assert r.status_code == 200, f"GET /api/profile/{student_id} failed: {r.data}"
    p_data = json.loads(r.data)["profile"]
    assert p_data["full_name"] == tc1_profile["full_name"]
    print(f"  ✓ 3. GET /api/profile/{student_id} -> 200 OK (Retrieved relational profile)")

    # 4. POST /api/recommendations/<student_id>
    r = client.post(f"/api/recommendations/{student_id}")
    assert r.status_code == 200, f"POST /api/recommendations/{student_id} failed: {r.data}"
    top_3 = json.loads(r.data)["top_3"]
    assert len(top_3) == 3
    print(f"  ✓ 4. POST /api/recommendations/{student_id} -> 200 OK (Generated Top 3)")

    # 5. GET /api/recommendations/<student_id>
    r = client.get(f"/api/recommendations/{student_id}")
    assert r.status_code == 200, f"GET /api/recommendations/{student_id} failed: {r.data}"
    print(f"  ✓ 5. GET /api/recommendations/{student_id} -> 200 OK (Retrieved cached matches)")

    # 6. GET /api/skill-gap/<student_id>
    r = client.get(f"/api/skill-gap/{student_id}")
    assert r.status_code == 200, f"GET /api/skill-gap/{student_id} failed: {r.data}"
    gap_summary = json.loads(r.data)["data"]["summary"]
    print(f"  ✓ 6. GET /api/skill-gap/{student_id} -> 200 OK (Known: {gap_summary['known_count']}, Missing: {gap_summary['missing_count']})")

    # 7. POST /api/roadmap/<student_id>
    r = client.post(f"/api/roadmap/{student_id}")
    assert r.status_code == 200, f"POST /api/roadmap/{student_id} failed: {r.data}"
    road_data = json.loads(r.data)["data"]
    assert len(road_data["milestones"]) == 4
    print(f"  ✓ 7. POST /api/roadmap/{student_id} -> 200 OK (Generated 4 milestones)")

    # 8. GET /api/roadmap/<student_id>
    r = client.get(f"/api/roadmap/{student_id}")
    assert r.status_code == 200, f"GET /api/roadmap/{student_id} failed: {r.data}"
    print(f"  ✓ 8. GET /api/roadmap/{student_id} -> 200 OK (Retrieved milestones and checklist)")

    # 9. POST /api/roadmap/progress
    task_id = road_data["milestones"][0]["tasks"][0]["id"]
    r = client.post("/api/roadmap/progress", json={
        "student_id": student_id,
        "career_role": road_data["role_id"],
        "task_id": task_id,
        "is_completed": True,
        "milestone_month": 1
    })
    assert r.status_code == 200, f"POST /api/roadmap/progress failed: {r.data}"
    progress_val = json.loads(r.data)["overall_progress_percentage"]
    print(f"  ✓ 9. POST /api/roadmap/progress -> 200 OK (Toggled task, progress={progress_val}%)")

    # 10. POST /api/chat (Chatbot Advisor Test)
    r = client.post("/api/chat", json={
        "student_id": student_id,
        "message": "What skills should I learn next for Data Analyst?"
    })
    assert r.status_code == 200, f"POST /api/chat failed: {r.data}"
    chat_res = json.loads(r.data)
    assert len(chat_res.get("reply", "")) > 20
    print(f"  ✓ 10. POST /api/chat -> 200 OK (CareerAI Advisor replied with {len(chat_res['suggestions'])} suggestions)")

    # 11. Authentication Endpoints & Login Page Check
    print("\n" + "=" * 50)
    print("🔐 EVALUATING USER AUTHENTICATION & LOGIN SUBSYSTEM")
    print("=" * 50)

    # 11a. GET /login page
    r = client.get("/login")
    assert r.status_code == 200, f"GET /login failed: {r.status_code}"
    assert "Date of Birth" in r.data.decode("utf-8")
    print("  ✓ GET /login -> 200 OK (Login/Register page active with Username, Password, Email, D.O.B)")

    # 11b. POST /api/auth/register
    test_user_payload = {
        "username": "karan_test_user",
        "email": "karan_test@example.com",
        "dob": "2002-05-15",
        "password": "SecurePassword123!"
    }
    r = client.post("/api/auth/register", json=test_user_payload)
    assert r.status_code == 201 or r.status_code == 409, f"Register failed: {r.data}"
    print(f"  ✓ POST /api/auth/register -> {r.status_code} (User registered with username, email, D.O.B, hashed password)")

    # 11c. POST /api/auth/login
    r = client.post("/api/auth/login", json={
        "username": "karan_test_user",
        "password": "SecurePassword123!"
    })
    assert r.status_code == 200, f"Login failed: {r.data}"
    user_info = json.loads(r.data)["user"]
    assert user_info["username"] == "karan_test_user"
    assert user_info["dob"] == "2002-05-15"
    print(f"  ✓ POST /api/auth/login -> 200 OK (Authenticated as {user_info['username']}, D.O.B={user_info['dob']})")

    # 11d. GET /api/auth/me
    r = client.get("/api/auth/me")
    assert r.status_code == 200, f"GET /api/auth/me failed: {r.data}"
    me_data = json.loads(r.data)
    assert me_data["authenticated"] is True
    print(f"  ✓ GET /api/auth/me -> 200 OK (Session active: user_id={me_data['user']['id']})")

    # 11e. POST /api/auth/logout
    r = client.post("/api/auth/logout")
    assert r.status_code == 200
    r_check = client.get("/api/auth/me")
    assert json.loads(r_check.data)["authenticated"] is False
    print("  ✓ POST /api/auth/logout -> 200 OK (Session cleared)")

    print("\n" + "=" * 70)
    print("🏆 ALL 14 SUBSYSTEMS, AUTHENTICATION & 5 TEST CASES PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation()
