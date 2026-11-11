"""
Personalized Learning Roadmap Generator.
Synthesizes a realistic 4-month curriculum adapted to student's missing and partially matched skills.
Includes learning objectives, topics, skills to develop, free resources, YouTube tutorials,
official docs, practical assignments, mini-projects, and persistent checklists.
"""
import os
import json
from typing import Dict, Any, List
from .skill_gap_analyzer import SkillGapAnalyzer
from ..database.db import get_roadmap_progress

class RoadmapGenerator:
    def __init__(self):
        self.gap_analyzer = SkillGapAnalyzer()

    def generate(self, student_dict: Dict[str, Any], role_id_or_title: str) -> Dict[str, Any]:
        """
        Dynamically generates 4 monthly milestones targeting the student's specific gaps for the selected career.
        """
        student_id = student_dict.get("id")
        gap_results = self.gap_analyzer.analyze(student_dict, role_id_or_title)
        if "error" in gap_results:
            return gap_results

        missing = gap_results.get("missing_skills", [])
        partial = gap_results.get("partially_matched_skills", [])
        role_title = gap_results["role_title"]
        role_id = gap_results["role_id"]

        completed_tasks = {}
        if student_id:
            completed_tasks = get_roadmap_progress(student_id, role_id)

        hours_per_week = int(student_dict.get("hours_per_week", 12))

        # Ordered skills to acquire (Critical missing first, then Partial, then Recommended missing)
        skills_queue = []
        for s in missing:
            if s["priority"] == "Critical":
                skills_queue.append(s)
        for s in partial:
            skills_queue.append(s)
        for s in missing:
            if s["priority"] != "Critical":
                skills_queue.append(s)

        # Baseline milestone structures
        milestones = [
            {
                "month": 1,
                "title": f"Month 1: {role_title} Core Fundamentals & Tooling",
                "objectives": "Establish foundational programming syntax, development environment, and core prerequisite concepts.",
                "weekly_hours": hours_per_week,
                "topics_to_cover": [
                    "Language syntax, control flow, functions, and error handling",
                    "Git version control and collaborative branching",
                    "Development IDE setup, package managers, and virtual environments",
                    "Foundational data manipulation and basic algorithmic problem solving"
                ],
                "skills_to_develop": [],
                "tasks": [
                    {"id": f"{role_id}_m1_t1", "text": "Set up clean local environment, install required runtimes & Git."},
                    {"id": f"{role_id}_m1_t2", "text": "Read official documentation fundamentals and complete 15+ coding exercises."},
                    {"id": f"{role_id}_m1_t3", "text": "Complete practical assignment: build a CLI data parser or calculator."},
                    {"id": f"{role_id}_m1_t4", "text": "Push starter project repository to GitHub with a clean README."}
                ],
                "practical_assignment": "Create a modular Python/script utility processing structured JSON/CSV files with input validation.",
                "mini_project": {
                    "title": f"Foundational {role_title} Command-Line Utility",
                    "description": "A well-structured utility showcasing robust exception handling, unit tests, and automated CLI flags.",
                    "deliverable": "Public GitHub repo with documentation and automated unit test runs."
                },
                "resources": []
            },
            {
                "month": 2,
                "title": f"Month 2: {role_title} Frameworks & Data Integration",
                "objectives": "Master primary industry frameworks, database connections, schema design, and asynchronous operations.",
                "weekly_hours": hours_per_week,
                "topics_to_cover": [
                    "Component architecture / MVC pattern in core frameworks",
                    "Database modeling, normalization, indexing, and CRUD queries",
                    "RESTful API design, parameter validation, and status code protocols",
                    "Integration testing and asynchronous request handling"
                ],
                "skills_to_develop": [],
                "tasks": [
                    {"id": f"{role_id}_m2_t1", "text": "Build modular application architecture using the primary framework."},
                    {"id": f"{role_id}_m2_t2", "text": "Design normalized database tables and write complex queries/migrations."},
                    {"id": f"{role_id}_m2_t3", "text": "Implement secure authentication (JWT/OAuth) and endpoint routing."},
                    {"id": f"{role_id}_m2_t4", "text": "Complete practical assignment: containerize application with Docker."}
                ],
                "practical_assignment": "Design a relational or document database schema and expose secure CRUD endpoints with OpenAPI Swagger docs.",
                "mini_project": {
                    "title": f"Interactive {role_title} Web/Data Service",
                    "description": "Full-stack application or analytical pipeline connecting backend storage with responsive client interfaces.",
                    "deliverable": "Containerized application with Dockerfile and seed database."
                },
                "resources": []
            },
            {
                "month": 3,
                "title": f"Month 3: Advanced Architecture, Cloud & Optimization",
                "objectives": "Implement system scalability, caching, cloud infrastructure, security hardening, and CI/CD automation.",
                "weekly_hours": hours_per_week,
                "topics_to_cover": [
                    "Performance optimization, caching strategies, and database query profiling",
                    "Container orchestration, cloud deployment, and VPC networking",
                    "Automated CI/CD pipelines with GitHub Actions",
                    "Application security auditing and vulnerability mitigations"
                ],
                "skills_to_develop": [],
                "tasks": [
                    {"id": f"{role_id}_m3_t1", "text": "Optimize latency, database query indexing, and caching layers (Redis)."},
                    {"id": f"{role_id}_m3_t2", "text": "Integrate automated CI/CD pipeline using GitHub Actions."},
                    {"id": f"{role_id}_m3_t3", "text": "Conduct security audit, input sanitation, and vulnerability patching."},
                    {"id": f"{role_id}_m3_t4", "text": "Deploy live service to cloud environment (AWS / GCP / Netlify / Render)."}
                ],
                "practical_assignment": "Set up a zero-downtime automated deployment workflow that lints, tests, and deploys on git push.",
                "mini_project": {
                    "title": f"Production-Grade Cloud-Deployed {role_title} System",
                    "description": "Production deployed microservice or cloud-native dashboard featuring zero-downtime deployment and telemetry.",
                    "deliverable": "Live hosted URL with monitoring telemetry and API documentation."
                },
                "resources": []
            },
            {
                "month": 4,
                "title": f"Month 4: Flagship Capstone Portfolio & Interview Prep",
                "objectives": "Engineer an enterprise-grade capstone project, refine GitHub technical showcase, and master technical interviews.",
                "weekly_hours": hours_per_week,
                "topics_to_cover": [
                    "End-to-end full-lifecycle software or data engineering delivery",
                    "Technical case study authoring with architectural diagrams",
                    "Algorithmic coding challenge patterns and domain interview questions",
                    "Resume tailoring and portfolio website refinement"
                ],
                "skills_to_develop": [],
                "tasks": [
                    {"id": f"{role_id}_m4_t1", "text": "Complete flagship portfolio capstone solving a real-world enterprise problem."},
                    {"id": f"{role_id}_m4_t2", "text": "Publish high-quality README with architectural diagrams, demo GIF, and benchmarks."},
                    {"id": f"{role_id}_m4_t3", "text": "Practice 30+ domain-specific technical interview questions and scenario problems."},
                    {"id": f"{role_id}_m4_t4", "text": "Tailor resume and LinkedIn profile highlighting newly acquired competencies."}
                ],
                "practical_assignment": "Conduct two mock technical interviews and record an architectural walkthrough video of your capstone.",
                "mini_project": {
                    "title": f"Enterprise Flagship {role_title} Capstone Solution",
                    "description": "Comprehensive portfolio project solving real business or operational requirements with production documentation.",
                    "deliverable": "Case study document, live demonstration link, and open-source repository."
                },
                "resources": []
            }
        ]

        # Distribute student's missing/partial skills into the 4 milestones
        for idx, s in enumerate(skills_queue):
            m_idx = min(idx % 4, 3)
            milestones[m_idx]["skills_to_develop"].append(s["name"])
            
            doc_url = s.get("documentation")
            yt_url = s.get("youtube")
            
            if doc_url and not any(r["url"] == doc_url for r in milestones[m_idx]["resources"]):
                milestones[m_idx]["resources"].append({
                    "title": f"Official {s['name']} Documentation",
                    "url": doc_url,
                    "type": "Documentation"
                })
            if yt_url and not any(r["url"] == yt_url for r in milestones[m_idx]["resources"]):
                milestones[m_idx]["resources"].append({
                    "title": f"{s['name']} Masterclass & Crash Course",
                    "url": yt_url,
                    "type": "YouTube Tutorial"
                })

        # Apply completion status to tasks
        total_tasks = 0
        completed_count = 0
        for m in milestones:
            for task in m["tasks"]:
                total_tasks += 1
                is_done = completed_tasks.get(task["id"], False)
                task["completed"] = is_done
                if is_done:
                    completed_count += 1

        overall_progress = round((completed_count / max(1, total_tasks)) * 100, 1)

        return {
            "role_id": role_id,
            "role_title": role_title,
            "overall_progress_percentage": overall_progress,
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "weekly_commitment_hours": hours_per_week,
            "milestones": milestones
        }
