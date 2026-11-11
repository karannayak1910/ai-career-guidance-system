"""
Rule-Based AI Recommendation Engine.
Applies deductive reasoning, IF-ELSE conditions, and transparent rules across all 15 technology careers.
Returns normalized suitability scores (0-100), matched/missing skills, and explicit rule explanations.
"""
import os
import json
from typing import Dict, Any, List

ROLES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roles.json")

def load_career_roles() -> List[Dict[str, Any]]:
    if os.path.exists(ROLES_PATH):
        try:
            with open(ROLES_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("roles", [])
        except Exception as e:
            print("Error loading career roles in rule engine:", e)
    return []

class RuleBasedCareerEngine:
    def __init__(self):
        self.roles = load_career_roles()

    def _normalize(self, s: str) -> str:
        return s.lower().strip().replace(" ", "").replace("-", "").replace(".", "")

    def evaluate(self, student_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate student profile against all 15 careers using transparent IF-ELSE rules.
        Returns full evaluated list, Top 3 recommendations, and rule explanation chains.
        """
        # 1. Aggregate Student Skills
        raw_skills = []
        for k in ["programming_languages", "frameworks", "databases", "tools_technologies", "technical_skills"]:
            val = student_dict.get(k, [])
            if isinstance(val, list):
                raw_skills.extend(val)
            elif isinstance(val, str) and val.strip():
                raw_skills.extend([s.strip() for s in val.split(",") if s.strip()])

        proficiencies = student_dict.get("skill_proficiencies", {})
        if isinstance(proficiencies, str):
            try:
                proficiencies = json.loads(proficiencies)
            except Exception:
                proficiencies = {}

        student_norm = {self._normalize(s): s for s in raw_skills}
        interests = [str(x).lower().strip() for x in student_dict.get("interest_areas", [])]
        branch = str(student_dict.get("branch", "")).lower()

        def has_skill(skill_query: str) -> bool:
            nq = self._normalize(skill_query)
            return any(nq in ns or ns in nq for ns in student_norm)

        def get_proficiency_weight(skill_query: str) -> float:
            nq = self._normalize(skill_query)
            for ns, orig in student_norm.items():
                if nq in ns or ns in nq:
                    prof = proficiencies.get(orig, "Intermediate")
                    if prof == "Advanced": return 1.25
                    if prof == "Beginner": return 0.75
                    return 1.0
            return 0.0

        evaluated_careers = []

        for role in self.roles:
            role_id = role["id"]
            role_title = role["title"]
            req_skills = role.get("required_skills", [])
            pref_skills = role.get("preferred_skills", [])

            rule_explanations = []
            score_points = 0.0
            max_points = 100.0

            # -----------------------------------------------------------------
            # Core Skill Matching Base (Up to 50 Points)
            # -----------------------------------------------------------------
            matched_required = []
            missing_required = []
            for s in req_skills:
                if has_skill(s):
                    matched_required.append(s)
                    score_points += 10.0 * get_proficiency_weight(s)
                else:
                    missing_required.append(s)

            matched_preferred = []
            missing_preferred = []
            for s in pref_skills:
                if has_skill(s):
                    matched_preferred.append(s)
                    score_points += 4.0 * get_proficiency_weight(s)
                else:
                    missing_preferred.append(s)

            skill_cov_pct = (len(matched_required) / max(1, len(req_skills))) * 100
            rule_explanations.append(
                f"Core skill coverage: {len(matched_required)}/{len(req_skills)} required skills matched ({round(skill_cov_pct, 1)}%)."
            )

            # -----------------------------------------------------------------
            # Specific Deductive Rules by Career Role
            # -----------------------------------------------------------------
            # Rule 1: Data Analyst
            if role_id == "data_analyst":
                if has_skill("SQL") and has_skill("Statistics") and (has_skill("Power BI") or has_skill("Tableau") or has_skill("Excel")):
                    score_points += 15.0
                    rule_explanations.append("Rule Applied: Strong business intelligence synergy detected (SQL + Statistics + Visual Dashboards).")
                if any("data analytics" in i or "data science" in i for i in interests):
                    score_points += 10.0
                    rule_explanations.append("Interest Alignment: High student affinity for Data Analytics.")

            # Rule 2: Data Scientist
            elif role_id == "data_scientist":
                if has_skill("Python") and has_skill("Machine Learning") and has_skill("Statistics"):
                    score_points += 18.0
                    rule_explanations.append("Rule Applied: Foundational Data Science trio satisfied (Python + ML + Statistics).")
                if has_skill("Mathematics") or has_skill("Deep Learning"):
                    score_points += 8.0
                    rule_explanations.append("Advanced Bonus: Mathematical/Deep Learning background significantly elevates modeling capacity.")
                if not has_skill("Python") and has_skill("Machine Learning"):
                    score_points -= 10.0
                    rule_explanations.append("Deductive Penalty: Machine Learning without Python foundation creates hiring friction.")

            # Rule 3: Machine Learning Engineer
            elif role_id == "ml_engineer":
                if has_skill("Python") and has_skill("Machine Learning") and (has_skill("Docker") or has_skill("REST APIs") or has_skill("FastAPI")):
                    score_points += 18.0
                    rule_explanations.append("Rule Applied: Production ML Engineering capability detected (ML + Containerization/APIs).")
                if any("machine learning" in i or "software development" in i for i in interests):
                    score_points += 8.0
                    rule_explanations.append("Interest Alignment: Strong passion for Machine Learning software engineering.")

            # Rule 4: AI Engineer
            elif role_id == "ai_engineer":
                if has_skill("Python") and has_skill("Deep Learning") and (has_skill("PyTorch") or has_skill("TensorFlow")):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Advanced Deep Learning framework mastery confirmed (Python + PyTorch/TensorFlow).")
                if any("artificial intelligence" in i for i in interests):
                    score_points += 10.0
                    rule_explanations.append("Interest Alignment: Primary interest aligns with Artificial Intelligence.")

            # Rule 5: Frontend Developer
            elif role_id == "frontend_developer":
                if has_skill("HTML") and has_skill("CSS") and has_skill("JavaScript") and (has_skill("React") or has_skill("Next.js")):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Modern Frontend component stack verified (HTML/CSS + JavaScript + React).")
                if has_skill("TypeScript") or has_skill("Tailwind CSS"):
                    score_points += 6.0
                    rule_explanations.append("Bonus: Modern production tooling (TypeScript / Tailwind CSS) detected.")

            # Rule 6: Backend Developer
            elif role_id == "backend_developer":
                if (has_skill("Python") or has_skill("Node.js")) and (has_skill("SQL") or has_skill("Databases")) and has_skill("REST APIs"):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Complete backend architectural pipeline present (Server language + Database + REST APIs).")

            # Rule 7: Full Stack Developer
            elif role_id == "fullstack_developer":
                has_fe = has_skill("HTML") and has_skill("JavaScript") and has_skill("React")
                has_be = (has_skill("Node.js") or has_skill("Python")) and has_skill("SQL")
                if has_fe and has_be:
                    score_points += 24.0
                    rule_explanations.append("Rule Applied: Full-Stack synergy confirmed across client UI, server runtime, and database tier.")

            # Rule 8: Python Developer
            elif role_id == "python_developer":
                if has_skill("Python") and (has_skill("Django") or has_skill("Flask") or has_skill("FastAPI")) and has_skill("SQL"):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Idiomatic Python web stack matched (Python + Django/Flask/FastAPI + SQL).")

            # Rule 9: Java Developer
            elif role_id == "java_developer":
                if has_skill("Java") and (has_skill("Spring Boot") or has_skill("OOP")) and has_skill("SQL"):
                    score_points += 22.0
                    rule_explanations.append("Rule Applied: Enterprise Java foundation confirmed (Java + Spring Boot / OOP + SQL).")

            # Rule 10: Software Engineer
            elif role_id == "software_engineer":
                if has_skill("Data Structures") and (has_skill("Java") or has_skill("C++") or has_skill("Python")):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Strong algorithmic problem solving & data structures competency.")

            # Rule 11: Cybersecurity Analyst
            elif role_id == "cybersecurity_analyst":
                if has_skill("Networking") and has_skill("Linux") and (has_skill("Cybersecurity") or has_skill("Python")):
                    score_points += 22.0
                    rule_explanations.append("Rule Applied: Security defense fundamentals met (Networking + Linux + Security practices).")
                if any("cyber" in i or "security" in i for i in interests):
                    score_points += 10.0
                    rule_explanations.append("Interest Alignment: Dedicated interest in Cybersecurity and network defense.")

            # Rule 12: Cloud Engineer
            elif role_id == "cloud_engineer":
                if (has_skill("AWS") or has_skill("Cloud Computing")) and has_skill("Docker") and has_skill("Linux"):
                    score_points += 20.0
                    rule_explanations.append("Rule Applied: Cloud container infrastructure pipeline met (AWS + Docker + Linux).")

            # Rule 13: DevOps Engineer
            elif role_id == "devops_engineer":
                if has_skill("Docker") and (has_skill("Kubernetes") or has_skill("CI/CD")) and has_skill("Linux"):
                    score_points += 22.0
                    rule_explanations.append("Rule Applied: Modern DevOps orchestration mastery verified (Docker + Kubernetes/CI/CD + Linux).")

            # Rule 14: Database Administrator
            elif role_id == "database_administrator":
                if has_skill("SQL") and (has_skill("PostgreSQL") or has_skill("MySQL") or has_skill("Databases")) and has_skill("Linux"):
                    score_points += 22.0
                    rule_explanations.append("Rule Applied: Core RDBMS administrative foundation met (Advanced SQL + Postgres/MySQL + Linux).")

            # Rule 15: UI/UX Developer
            elif role_id == "ui_ux_developer":
                if (has_skill("HTML") or has_skill("CSS")) and (has_skill("UI/UX Design") or has_skill("Figma") or has_skill("Responsive Design")):
                    score_points += 22.0
                    rule_explanations.append("Rule Applied: Visual design and front-of-the-frontend UI/UX engineering capability.")
                if any("ui" in i or "ux" in i or "web" in i for i in interests):
                    score_points += 8.0
                    rule_explanations.append("Interest Alignment: Affinity for user interface prototyping and visual interaction.")

            # -----------------------------------------------------------------
            # Academic Background & Branch Affinity Deductions
            # -----------------------------------------------------------------
            if "data science" in branch and role_id in ["data_analyst", "data_scientist"]:
                score_points += 5.0
                rule_explanations.append("Academic Alignment: Formal degree major in Data Science.")
            elif "artificial intelligence" in branch and role_id in ["ai_engineer", "ml_engineer"]:
                score_points += 5.0
                rule_explanations.append("Academic Alignment: Formal degree major in Artificial Intelligence.")
            elif "computer science" in branch or "information technology" in branch:
                score_points += 3.0

            # Normalize final score strictly between 15% and 98%
            normalized_score = round(max(15.0, min(98.0, score_points)), 1)

            evaluated_careers.append({
                "id": role_id,
                "title": role_title,
                "domain": role.get("domain", ""),
                "description": role.get("description", ""),
                "average_salary": role.get("average_salary", ""),
                "market_demand": role.get("market_demand", "High"),
                "learning_difficulty": role.get("learning_difficulty", "Intermediate"),
                "suitability_score": normalized_score,
                "matched_required_skills": matched_required,
                "missing_required_skills": missing_required,
                "matched_preferred_skills": matched_preferred,
                "missing_preferred_skills": missing_preferred,
                "all_matched_skills": matched_required + matched_preferred,
                "all_missing_skills": missing_required + missing_preferred,
                "rule_explanations": rule_explanations
            })

        # Rank all 15 careers descending
        evaluated_careers.sort(key=lambda x: x["suitability_score"], reverse=True)
        top_3 = evaluated_careers[:3]

        return {
            "top_3": top_3,
            "all_ranked": evaluated_careers
        }
