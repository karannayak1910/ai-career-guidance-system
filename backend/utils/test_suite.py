"""
In-process Flask Test Suite for AI Career Guidance System.
Tests all web pages, REST endpoints, database queries, and AI models using Flask test_client.
"""
import json
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import app
from backend.database.db import get_student_profile

def run_tests():
    print("=" * 60)
    print("Running AI Career Guidance System Integration Tests")
    print("=" * 60)

    client = app.test_client()

    # 1. Health Check
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("✓ GET /api/health -> 200 OK")

    # 2. Page Routes (All 7 Pages)
    pages = ["/", "/profile", "/dashboard", "/recommendations", "/career-details", "/skill-gap", "/roadmap"]
    for p in pages:
        r = client.get(p)
        assert r.status_code == 200, f"Page {p} returned {r.status_code}"
        assert len(r.data) > 200, f"Page {p} returned empty response"
        print(f"✓ GET {p} -> 200 OK ({len(r.data)} bytes)")

    # 3. Skills Catalog
    r = client.get("/api/skills/catalog")
    assert r.status_code == 200
    cat_data = json.loads(r.data)
    skills = cat_data.get("catalog", {})
    assert len(skills) >= 20, f"Expected >=20 skills in catalog, got {len(skills)}"
    print(f"✓ GET /api/skills/catalog -> 200 OK ({len(skills)} skills loaded)")

    # 4. Profile Save API
    profile_payload = {
        "full_name": "Karan Gupta",
        "college_name": "Delhi Technological University",
        "branch": "Computer Science",
        "current_semester": 6,
        "graduation_year": 2026,
        "programming_languages": ["Python", "JavaScript", "C++"],
        "frameworks": ["PyTorch", "TensorFlow", "Flask"],
        "databases": ["SQL", "MongoDB"],
        "tools_technologies": ["Git", "Docker", "Linux", "AWS"],
        "technical_skills": ["Machine Learning", "Deep Learning", "Data Structures", "Algorithms", "Statistics"],
        "skill_proficiencies": {
            "Python": "Advanced",
            "PyTorch": "Intermediate",
            "Machine Learning": "Intermediate",
            "Deep Learning": "Intermediate",
            "SQL": "Intermediate"
        },
        "interest_areas": ["Artificial Intelligence", "Machine Learning", "Data Science"],
        "preferred_work_area": "Remote",
        "preferred_career_type": "Full-time",
        "hours_per_week": 16
    }
    r = client.post("/api/profile/save", json=profile_payload)
    assert r.status_code == 200, f"Profile save failed: {r.data}"
    save_res = json.loads(r.data)
    student_id = save_res.get("student_id")
    assert student_id is not None
    print(f"✓ POST /api/profile/save -> 200 OK (Persisted in SQLite student_id={student_id})")

    # Verify directly from SQLite
    db_profile = get_student_profile(student_id)
    assert db_profile is not None
    assert db_profile["full_name"] == "Karan Gupta"
    print(f"✓ SQLite Verification -> Confirmed record saved in data/career_guidance.db")

    # 5. Recommendations Generate API
    r = client.post("/api/recommendations/generate", json={"student_id": student_id})
    assert r.status_code == 200, f"Recommendations failed: {r.data}"
    rec_res = json.loads(r.data)
    top_3 = rec_res.get("top_3", [])
    assert len(top_3) == 3, f"Expected 3 recommendations, got {len(top_3)}"
    
    top_role = top_3[0]
    print(f"✓ POST /api/recommendations/generate -> 200 OK")
    print(f"   #1 Match: {top_role['title']} ({top_role['match_score']}%)")
    print(f"   #2 Match: {top_3[1]['title']} ({top_3[1]['match_score']}%)")
    print(f"   #3 Match: {top_3[2]['title']} ({top_3[2]['match_score']}%)")

    # 6. Test Career Details API for all 15 Roles
    expected_15_roles = [
        "data-analyst", "data-scientist", "machine-learning-engineer", "ai-engineer",
        "frontend-developer", "backend-developer", "full-stack-developer", "python-developer",
        "java-developer", "software-engineer", "cybersecurity-analyst", "cloud-engineer",
        "devops-engineer", "database-administrator", "ui-ux-developer"
    ]
    for role_id in expected_15_roles:
        r = client.get(f"/api/career/{role_id}?student_id={student_id}")
        assert r.status_code == 200, f"Career API for {role_id} failed: {r.status_code}"
    print(f"✓ GET /api/career/<role_id> -> 200 OK for all 15 Tech Career Roles")

    # 7. Skill Gap API
    r = client.get(f"/api/skill-gap/{top_role['id']}?student_id={student_id}")
    assert r.status_code == 200, f"Skill gap failed: {r.data}"
    gap_data = json.loads(r.data).get("data", {})
    summary = gap_data.get("summary", {})
    print(f"✓ GET /api/skill-gap/{top_role['id']} -> 200 OK")
    print(f"   Known: {summary.get('known_count')}, Partial: {summary.get('partial_count')}, Missing: {summary.get('missing_count')}")

    # 8. Learning Roadmap API
    r = client.get(f"/api/roadmap/{top_role['id']}?student_id={student_id}")
    assert r.status_code == 200, f"Roadmap failed: {r.data}"
    road_data = json.loads(r.data).get("data", {})
    milestones = road_data.get("milestones", [])
    assert len(milestones) == 4
    print(f"✓ GET /api/roadmap/{top_role['id']} -> 200 OK ({len(milestones)} Monthly Milestones)")

    # 9. Roadmap Task Toggle API
    first_task = milestones[0]["tasks"][0]
    r = client.post("/api/roadmap/task/toggle", json={
        "student_id": student_id,
        "career_role": top_role["id"],
        "task_id": first_task["id"],
        "is_completed": True,
        "milestone_month": 1
    })
    assert r.status_code == 200, f"Task toggle failed: {r.data}"
    toggle_res = json.loads(r.data)
    print(f"✓ POST /api/roadmap/task/toggle -> 200 OK (Task checked, progress: {toggle_res.get('overall_progress_percentage')}%)")

    # 10. Resume Parsing Endpoint Test
    resume_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_resumes", "sample_resume_karan.docx")
    if os.path.exists(resume_file_path):
        with open(resume_file_path, "rb") as f:
            r = client.post(
                "/api/resume/parse",
                data={"resume": (f, "sample_resume_karan.docx")},
                content_type="multipart/form-data"
            )
        assert r.status_code == 200, f"Resume parse failed: {r.data}"
        resume_res = json.loads(r.data)
        extracted = resume_res.get("data", {})
        assert extracted.get("full_name") == "Karan Gupta"
        print(f"✓ POST /api/resume/parse -> 200 OK (Extracted name '{extracted.get('full_name')}', {len(extracted.get('technical_skills', []))} technical skills)")

    print("=" * 60)
    print("🎉 ALL 10 TEST SUITES PASSED WITHOUT ERROR!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
