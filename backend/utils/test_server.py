"""
Automated end-to-end test suite for AI Career Guidance System using standard library urllib.
Tests Flask server startup, static page routes, and all REST endpoints.
"""
import time
import urllib.request
import urllib.parse
import json
import os
import sys

BASE_URL = "http://127.0.0.1:5000"

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TestClient"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8")

def http_post(url, data_dict):
    json_bytes = json.dumps(data_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_bytes,
        headers={"Content-Type": "application/json", "User-Agent": "TestClient"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8")

def run_tests():
    print("Testing server endpoints...")
    # 1. Health check
    status, body = http_get(f"{BASE_URL}/api/health")
    assert status == 200, f"Health check failed: {status}"
    print("✓ Health check OK:", body)

    # 2. Page routes
    for page in ["/", "/profile", "/dashboard", "/recommendations", "/skill-gap", "/roadmap"]:
        status, body = http_get(f"{BASE_URL}{page}")
        assert status == 200, f"Page {page} failed with status {status}"
        print(f"✓ Page {page} OK ({len(body)} bytes)")

    # 3. Skills catalog API
    status, body = http_get(f"{BASE_URL}/api/skills/catalog")
    assert status == 200
    skills_count = len(json.loads(body).get("catalog", {}))
    assert skills_count > 10, f"Expected >10 skills in catalog, got {skills_count}"
    print(f"✓ Skills catalog OK ({skills_count} skills)")

    # 4. Profile save API
    profile_payload = {
        "full_name": "Test Student",
        "college_name": "National Institute of Technology",
        "branch": "Computer Science",
        "current_semester": 6,
        "graduation_year": 2026,
        "programming_languages": ["Python", "JavaScript", "C++"],
        "frameworks": ["PyTorch", "Flask", "React"],
        "databases": ["SQL", "MongoDB"],
        "tools_technologies": ["Git", "Docker", "Linux"],
        "technical_skills": ["Machine Learning", "Deep Learning", "Data Structures"],
        "skill_proficiencies": {
            "Python": "Advanced",
            "PyTorch": "Intermediate",
            "Machine Learning": "Intermediate",
            "JavaScript": "Beginner"
        },
        "interest_areas": ["Artificial Intelligence", "Machine Learning", "Web Development"],
        "preferred_work_area": "Remote",
        "preferred_career_type": "Full-time",
        "hours_per_week": 15
    }
    status, body = http_post(f"{BASE_URL}/api/profile/save", profile_payload)
    assert status == 200, f"Profile save failed: {body}"
    save_json = json.loads(body)
    student_id = save_json.get("student_id")
    assert student_id is not None
    print(f"✓ Profile save OK (student_id={student_id})")

    # 5. Recommendations generate API
    status, body = http_post(f"{BASE_URL}/api/recommendations/generate", {"student_id": student_id})
    assert status == 200, f"Recommendations failed: {body}"
    rec_data = json.loads(body)
    assert len(rec_data["top_3"]) == 3, f"Expected Top 3, got {len(rec_data['top_3'])}"
    top_role = rec_data["top_3"][0]
    print(f"✓ Recommendations OK: Top 1 is '{top_role['title']}' with score {top_role['match_score']}%")

    # 6. Skill Gap API
    status, body = http_get(f"{BASE_URL}/api/skill-gap/{top_role['id']}?student_id={student_id}")
    assert status == 200, f"Skill gap failed: {body}"
    gap_data = json.loads(body)["data"]
    print(f"✓ Skill gap OK: Known={gap_data['summary']['known_count']}, Partial={gap_data['summary']['partial_count']}, Missing={gap_data['summary']['missing_count']}")

    # 7. Roadmap API
    status, body = http_get(f"{BASE_URL}/api/roadmap/{top_role['id']}?student_id={student_id}")
    assert status == 200, f"Roadmap failed: {body}"
    road_data = json.loads(body)["data"]
    assert len(road_data["milestones"]) == 4
    print(f"✓ Roadmap OK: {len(road_data['milestones'])} monthly milestones generated")

    # 8. Roadmap Task Toggle API
    first_task_id = road_data["milestones"][0]["tasks"][0]["id"]
    status, body = http_post(
        f"{BASE_URL}/api/roadmap/task/toggle",
        {
            "student_id": student_id,
            "career_role": top_role["id"],
            "task_id": first_task_id,
            "is_completed": True,
            "milestone_month": 1
        }
    )
    assert status == 200, f"Toggle task failed: {body}"
    toggle_json = json.loads(body)
    print(f"✓ Task toggle OK: task '{first_task_id}' checked -> overall progress {toggle_json['overall_progress_percentage']}%")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The application is fully functional and ready.")

if __name__ == "__main__":
    run_tests()
