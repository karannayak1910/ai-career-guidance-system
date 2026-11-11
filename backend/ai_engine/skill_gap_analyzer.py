"""
Intelligent Skill Gap Analysis Module.
Categorizes role requirements into:
1. Known Skills (Green)
2. Partially Matched Skills (Orange)
3. Missing Skills (Red)
Enriches each missing skill with industry importance, learning priority, resource links, and a practical project.
"""
import os
import json
from typing import Dict, Any, List

ROLES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roles.json")
SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_skills.json")

ADJACENT_SKILLS = {
    "Java": ["C++", "C#", "Kotlin", "Object-Oriented Programming"],
    "C++": ["C", "Java", "Rust"],
    "Python": ["R", "Ruby"],
    "PostgreSQL": ["MySQL", "SQL", "SQLite"],
    "MySQL": ["PostgreSQL", "SQL", "Oracle"],
    "React": ["Vue.js", "Angular", "Next.js", "JavaScript"],
    "Next.js": ["React", "JavaScript", "Node.js"],
    "Node.js": ["Express", "JavaScript", "TypeScript"],
    "Django": ["Flask", "FastAPI", "Python"],
    "Flask": ["Django", "FastAPI", "Python"],
    "FastAPI": ["Flask", "Django", "Python"],
    "Spring Boot": ["Java", "Hibernate", "OOP"],
    "AWS": ["GCP", "Azure", "Cloud Computing"],
    "Docker": ["Kubernetes", "Linux"],
    "Kubernetes": ["Docker"],
    "CI/CD": ["Git", "Docker", "Linux"],
    "Pandas": ["NumPy", "Excel", "R", "SQL"],
    "NumPy": ["Pandas", "Mathematics"],
    "Machine Learning": ["Statistics", "Python", "Deep Learning", "Mathematics"],
    "Deep Learning": ["Machine Learning", "PyTorch", "TensorFlow"],
    "TensorFlow": ["PyTorch", "Keras", "Deep Learning"],
    "PyTorch": ["TensorFlow", "Deep Learning"],
    "Power BI": ["Tableau", "Excel", "Data Visualization"],
    "Tableau": ["Power BI", "Excel", "Data Visualization"],
    "Excel": ["Power BI", "Tableau", "SQL"],
    "UI/UX Design": ["Figma", "HTML", "CSS", "Responsive Design"],
    "Figma": ["UI/UX Design", "HTML", "CSS"],
    "Tailwind CSS": ["CSS", "HTML", "Responsive Design"],
    "Cybersecurity": ["Networking", "Linux", "Ethical Hacking"],
    "Networking": ["Linux", "Cybersecurity"],
    "Linux": ["Bash", "Networking", "Docker"]
}

class SkillGapAnalyzer:
    def __init__(self):
        self.roles_dict = self._load_roles_dict()
        self.skills_meta = self._load_skills_meta()

    def _load_roles_dict(self) -> Dict[str, Any]:
        if os.path.exists(ROLES_PATH):
            try:
                with open(ROLES_PATH, "r", encoding="utf-8") as f:
                    roles = json.load(f).get("roles", [])
                    res = {}
                    for r in roles:
                        res[r["id"]] = r
                        res[r["id"].replace("_", "-")] = r
                        res[r["id"].replace("-", "_")] = r
                        res[r["title"].lower().replace(" ", "_")] = r
                        res[r["title"].lower().replace(" ", "-")] = r
                        res[r["title"].lower()] = r
                    return res
            except Exception as e:
                print("Error loading roles in gap analyzer:", e)
        return {}

    def _load_skills_meta(self) -> Dict[str, Any]:
        if os.path.exists(SKILLS_PATH):
            try:
                with open(SKILLS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f).get("skills", {})
            except Exception as e:
                print("Error loading skills meta in gap analyzer:", e)
        return {}

    def _normalize(self, s: str) -> str:
        return s.lower().strip().replace(" ", "").replace("-", "").replace(".", "")

    def analyze(self, student_dict: Dict[str, Any], role_id_or_title: str) -> Dict[str, Any]:
        """
        Dynamically analyzes gaps between student skills and target career requirements.
        """
        key = role_id_or_title.lower().replace(" ", "_")
        role = self.roles_dict.get(key)
        if not role:
            for k, r in self.roles_dict.items():
                if role_id_or_title.lower() in k or k in role_id_or_title.lower():
                    role = r
                    break

        if not role:
            return {"error": f"Role '{role_id_or_title}' not found in Knowledge Base."}

        # Gather student skills
        all_skills = []
        for k in ["programming_languages", "frameworks", "databases", "tools_technologies", "technical_skills"]:
            v = student_dict.get(k, [])
            if isinstance(v, list):
                all_skills.extend(v)
            elif isinstance(v, str) and v.strip():
                all_skills.extend([s.strip() for s in v.split(",") if s.strip()])

        proficiencies = student_dict.get("skill_proficiencies", {})
        if isinstance(proficiencies, str):
            try:
                proficiencies = json.loads(proficiencies)
            except Exception:
                proficiencies = {}

        norm_student = {self._normalize(s): s for s in all_skills}

        req_skills = role.get("required_skills", [])
        pref_skills = role.get("preferred_skills", [])

        # Priority tagged requirements
        tagged_skills = [(s, "Critical") for s in req_skills] + [(s, "Recommended") for s in pref_skills]

        known_skills = []
        partially_matched_skills = []
        missing_skills = []

        seen_skills = set()

        for skill, priority in tagged_skills:
            if skill in seen_skills:
                continue
            seen_skills.add(skill)

            norm_s = self._normalize(skill)
            meta = self.skills_meta.get(skill, {})
            why_it_matters = meta.get(
                "why_it_matters", 
                f"Essential competency required for reliable execution in the {role['title']} role."
            )
            doc_link = meta.get("documentation", "https://developer.mozilla.org/")
            yt_link = meta.get("youtube", "https://www.youtube.com/")
            project_idea = meta.get("project_idea", f"Build a practical demonstration project leveraging {skill}.")

            # 1. Exact or Alias Match
            found_orig = None
            for ns, orig in norm_student.items():
                if norm_s == ns or norm_s in ns or ns in norm_s:
                    found_orig = orig
                    break

            if found_orig:
                prof = proficiencies.get(found_orig, "Intermediate")
                if prof == "Beginner":
                    partially_matched_skills.append({
                        "name": skill,
                        "priority": priority,
                        "proficiency": "Beginner",
                        "status": "Needs Mastery",
                        "color": "orange",
                        "reason": f"You have foundational exposure ({prof}), but professional competency requires intermediate hands-on project depth.",
                        "why_it_matters": why_it_matters,
                        "documentation": doc_link,
                        "youtube": yt_link,
                        "project_idea": project_idea
                    })
                else:
                    known_skills.append({
                        "name": skill,
                        "priority": priority,
                        "proficiency": prof,
                        "status": "Acquired",
                        "color": "green",
                        "why_it_matters": why_it_matters
                    })
            else:
                # 2. Check for Adjacent Transferrable Skill
                adjacent_candidates = ADJACENT_SKILLS.get(skill, [])
                has_adjacent = False
                matched_adj_name = ""
                for adj in adjacent_candidates:
                    norm_adj = self._normalize(adj)
                    for ns, orig in norm_student.items():
                        if norm_adj == ns or norm_adj in ns or ns in norm_adj:
                            has_adjacent = True
                            matched_adj_name = orig
                            break
                    if has_adjacent:
                        break

                if has_adjacent:
                    partially_matched_skills.append({
                        "name": skill,
                        "priority": priority,
                        "proficiency": "Transferrable",
                        "status": "Transferrable Skill",
                        "color": "orange",
                        "reason": f"You know related technology ({matched_adj_name}), giving you high learning velocity to quickly adopt {skill}.",
                        "why_it_matters": why_it_matters,
                        "documentation": doc_link,
                        "youtube": yt_link,
                        "project_idea": project_idea
                    })
                else:
                    # 3. Missing Skill
                    missing_skills.append({
                        "name": skill,
                        "priority": priority,
                        "proficiency": "None",
                        "status": "Missing",
                        "color": "red",
                        "reason": f"Required {priority.lower()} skill missing from your current technical profile.",
                        "why_it_matters": why_it_matters,
                        "documentation": doc_link,
                        "youtube": yt_link,
                        "project_idea": project_idea
                    })

        total_reqs = len(tagged_skills)
        readiness_score = round(((len(known_skills) + (0.5 * len(partially_matched_skills))) / max(1, total_reqs)) * 100, 1)

        return {
            "role_id": role["id"],
            "role_title": role["title"],
            "domain": role.get("domain", ""),
            "summary": {
                "total_skills": total_reqs,
                "known_count": len(known_skills),
                "partial_count": len(partially_matched_skills),
                "missing_count": len(missing_skills),
                "readiness_percentage": readiness_score
            },
            "chart_data": {
                "labels": ["Known Skills", "Partially Matched", "Missing Skills"],
                "data": [len(known_skills), len(partially_matched_skills), len(missing_skills)],
                "colors": ["#10b981", "#f59e0b", "#ef4444"]
            },
            "known_skills": known_skills,
            "partially_matched_skills": partially_matched_skills,
            "missing_skills": missing_skills
        }
