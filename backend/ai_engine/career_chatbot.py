"""
AI Career Guidance Chatbot Advisor Module.
Provides interactive, context-aware career counseling grounded in the 15-role knowledge base,
the student's personal skills, skill gaps, and learning roadmaps.
"""
import os
import json
import re
from typing import Dict, Any, List

ROLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roles.json"))
SKILLS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_skills.json"))

class CareerChatbot:
    """Intelligent conversational career counselor for technology career paths."""

    def __init__(self):
        self.roles = self._load_roles()
        self.skills_meta = self._load_skills()

    def _load_roles(self) -> List[Dict[str, Any]]:
        if os.path.exists(ROLES_PATH):
            try:
                with open(ROLES_PATH, "r", encoding="utf-8") as f:
                    return json.load(f).get("roles", [])
            except Exception as e:
                print("Error loading roles in chatbot:", e)
        return []

    def _load_skills(self) -> Dict[str, Any]:
        if os.path.exists(SKILLS_PATH):
            try:
                with open(SKILLS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f).get("skills", {})
            except Exception as e:
                print("Error loading skills in chatbot:", e)
        return {}

    def get_role_by_query(self, query: str) -> Dict[str, Any]:
        """Find matching career role from text."""
        q = query.lower()
        for r in self.roles:
            title = r["title"].lower()
            role_id = r["id"].replace("_", " ")
            if title in q or role_id in q:
                return r
            # Also check partials
            if r["id"] == "ai_engineer" and ("ai engineer" in q or "artificial intelligence engineer" in q):
                return r
            if r["id"] == "machine_learning_engineer" and ("ml engineer" in q or "machine learning" in q):
                return r
            if r["id"] == "cybersecurity_analyst" and ("cybersecurity" in q or "security analyst" in q):
                return r
            if r["id"] == "ui_ux_developer" and ("ui/ux" in q or "ui ux" in q or "ui developer" in q):
                return r
            if r["id"] == "database_administrator" and ("dba" in q or "database admin" in q):
                return r
        return None

    def respond(self, message: str, student_profile: Dict[str, Any] = None, recommendations: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate intelligent, grounded response to user query.
        """
        msg = message.strip()
        lower = msg.lower()
        student_name = (student_profile.get("full_name") or "there") if student_profile else "there"
        student_branch = student_profile.get("branch") if student_profile else None
        
        # Extract student known skills
        known_skills = set()
        if student_profile:
            for field in ["programming_languages", "frameworks", "databases", "tools_technologies", "technical_skills"]:
                val = student_profile.get(field, "")
                if isinstance(val, str):
                    for s in val.split(","):
                        if s.strip():
                            known_skills.add(s.strip())
                elif isinstance(val, (list, set)):
                    for s in val:
                        if str(s).strip():
                            known_skills.add(str(s).strip())

        top_3 = recommendations.get("top_3", []) if recommendations else []
        top_role = top_3[0]["title"] if top_3 else None

        # 1. Greetings
        if re.search(r"\b(hi|hello|hey|greetings|good morning|good afternoon)\b", lower):
            reply = (
                f"Hello **{student_name}**! 👋 I am **CareerAI Advisor**, your intelligent career guidance counselor.\n\n"
                f"I can help you explore technology roles, diagnose skill gaps, plan personalized roadmaps, or give learning and project advice."
            )
            if top_role:
                reply += f"\n\nBased on your registered profile, your current #1 recommended path is **{top_role}**."
            
            return {
                "status": "success",
                "reply": reply,
                "suggestions": [
                    "What are my Top 3 career matches?",
                    "What skills should I learn next?",
                    "Compare Data Analyst vs Data Scientist",
                    "Suggest portfolio projects for me"
                ]
            }

        # 2. Inquire about Top Career Matches
        if "top match" in lower or "my recommendation" in lower or "suit me" in lower or "best career" in lower:
            if top_3:
                reply = (
                    f"🎯 **Your Top Recommended Technology Careers** (analyzed from your profile & AI Decision Tree):\n\n"
                )
                for idx, r in enumerate(top_3, 1):
                    reply += f"**{idx}. {r['title']}** — **{r['match_score']}% Match**\n"
                    reply += f"   - *Why*: {r.get('why_matches', '')}\n"
                    reply += f"   - *Market Demand*: {r.get('market_demand', 'High')} | *Salary*: {r.get('average_salary', 'Competitive')}\n\n"
                reply += "Would you like me to break down your skill gap for your top match or recommend project ideas?"
                return {
                    "status": "success",
                    "reply": reply,
                    "suggestions": [
                        f"What skills am I missing for {top_3[0]['title']}?",
                        f"Suggest a project for {top_3[0]['title']}",
                        "How is my match score calculated?"
                    ]
                }
            else:
                return {
                    "status": "success",
                    "reply": (
                        f"You haven't completed your profile assessment yet, {student_name}!\n\n"
                        f"Head over to the **Profile & Resume Studio** to select your technical skills and interests, "
                        f"or upload your resume. I'll immediately analyze your profile across 15 tech roles!"
                    ),
                    "suggestions": ["Go to Profile Page", "What career roles are available?", "What does a Software Engineer do?"]
                }

        # 3. Missing skills & Next steps
        if "missing skill" in lower or "learn next" in lower or "skill gap" in lower or "what should i learn" in lower:
            target_role = self.get_role_by_query(lower)
            if not target_role and top_3:
                role_id = top_3[0]["id"]
                target_role = next((r for r in self.roles if r["id"] == role_id), self.roles[0])

            if target_role:
                req_skills = target_role.get("required_skills", [])
                missing = [s for s in req_skills if s not in known_skills]
                known = [s for s in req_skills if s in known_skills]

                reply = f"🔍 **Skill Diagnostic for {target_role['title']}**:\n\n"
                if known:
                    reply += f"✅ **Skills You Already Possess ({len(known)})**: {', '.join(known)}\n\n"
                if missing:
                    reply += f"🚀 **Key Missing Skills to Target ({len(missing)})**:\n"
                    for s in missing:
                        meta = self.skills_meta.get(s, {})
                        why = meta.get("why_it_matters", "Core prerequisite for production engineering.")
                        reply += f"- **{s}**: {why}\n"
                    reply += f"\n💡 *Recommendation*: Start by checking off Month 1 milestones in your **Learning Roadmap**!"
                else:
                    reply += "🎉 Incredible! You already possess all fundamental required skills for this role! Focus on building an advanced portfolio project."

                return {
                    "status": "success",
                    "reply": reply,
                    "suggestions": [
                        f"Show learning roadmap for {target_role['title']}",
                        f"What projects should I build for {target_role['title']}?",
                        "What is the average salary?"
                    ]
                }

        # 4. Role Comparison (e.g. Data Analyst vs Data Scientist)
        if " vs " in lower or "compare" in lower or "difference between" in lower:
            matched_roles = []
            for r in self.roles:
                if r["title"].lower() in lower or r["id"].replace("_", " ") in lower:
                    matched_roles.append(r)
            if len(matched_roles) >= 2:
                r1, r2 = matched_roles[0], matched_roles[1]
                reply = (
                    f"⚖️ **Comparison: {r1['title']} vs {r2['title']}**\n\n"
                    f"**1. Core Focus**:\n"
                    f"- **{r1['title']}**: {r1['description']}\n"
                    f"- **{r2['title']}**: {r2['description']}\n\n"
                    f"**2. Essential Skills**:\n"
                    f"- **{r1['title']}**: {', '.join(r1.get('required_skills', [])[:5])}\n"
                    f"- **{r2['title']}**: {', '.join(r2.get('required_skills', [])[:5])}\n\n"
                    f"**3. Industry Metrics**:\n"
                    f"- **{r1['title']}**: Salary ~ {r1['average_salary']} | Difficulty: {r1['learning_difficulty']}\n"
                    f"- **{r2['title']}**: Salary ~ {r2['average_salary']} | Difficulty: {r2['learning_difficulty']}\n\n"
                    f"💡 *Which to choose?* If you prefer {r1.get('domain', 'this area')}, choose **{r1['title']}**. If you lean towards {r2.get('domain', 'that area')}, choose **{r2['title']}**!"
                )
                return {
                    "status": "success",
                    "reply": reply,
                    "suggestions": [
                        f"Tell me more about {r1['title']}",
                        f"Tell me more about {r2['title']}",
                        "What are my Top 3 career matches?"
                    ]
                }

        # 5. Specific Career Role Information
        target_role = self.get_role_by_query(lower)
        if target_role:
            projs = target_role.get("recommended_projects", [])
            proj_text = projs[0]["title"] if projs else "Production portfolio project"
            reply = (
                f"📌 **Career Overview: {target_role['title']}**\n\n"
                f"**Domain**: {target_role.get('domain', 'Technology')}\n\n"
                f"**What they do**: {target_role.get('description', '')}\n\n"
                f"💰 **Average Salary**: {target_role.get('average_salary', 'Competitive')}\n"
                f"📈 **Market Demand**: {target_role.get('market_demand', 'High')} | **Difficulty**: {target_role.get('learning_difficulty', 'Moderate')}\n\n"
                f"🛠️ **Core Required Skills**: {', '.join(target_role.get('required_skills', []))}\n"
                f"💻 **Tools & Frameworks**: {', '.join(target_role.get('tools_and_frameworks', []))}\n\n"
                f"🏆 **Recommended Project**: *{proj_text}*"
            )
            return {
                "status": "success",
                "reply": reply,
                "suggestions": [
                    f"What skills am I missing for {target_role['title']}?",
                    f"View learning roadmap for {target_role['title']}",
                    f"Project ideas for {target_role['title']}"
                ]
            }

        # 6. Project Suggestions
        if "project" in lower or "portfolio" in lower:
            target = self.get_role_by_query(lower) or (next((r for r in self.roles if r["id"] == top_3[0]["id"]), self.roles[0]) if top_3 else self.roles[0])
            projs = target.get("recommended_projects", [])
            reply = f"🚀 **Recommended Portfolio Projects for {target['title']}**:\n\n"
            for idx, p in enumerate(projs, 1):
                reply += f"**{idx}. {p['title']}**\n"
                reply += f"   - *Concept*: {p['description']}\n"
                reply += f"   - *Deliverable*: {p['deliverable']}\n\n"
            reply += "Building and publishing these on GitHub with clean READMEs will significantly boost your resume!"
            return {
                "status": "success",
                "reply": reply,
                "suggestions": [
                    f"What skills do I need for {target['title']}?",
                    "How to prepare for coding interviews",
                    "Review my roadmap"
                ]
            }

        # 7. Interview / Resume / Learning Advice
        if "interview" in lower or "resume" in lower or "how to prepare" in lower:
            reply = (
                f"💼 **High-Impact Career Preparation Strategy**:\n\n"
                f"1. **Master Core Fundamentals First**: Focus on Data Structures, Algorithms, and Language idiomatic syntax.\n"
                f"2. **Build Proof of Competence**: Employers look for completed, deployed projects over certificates. Build 2-3 end-to-end applications.\n"
                f"3. **Targeted Resume Tailoring**: Feature relevant keywords for your chosen track (e.g. Docker, PyTorch, React, SQL).\n"
                f"4. **Active Problem Solving**: Practice coding on LeetCode/HackerRank for technical interviews and brush up on system design basics."
            )
            return {
                "status": "success",
                "reply": reply,
                "suggestions": [
                    "What are my Top 3 career matches?",
                    "What skills should I learn next?",
                    "Suggest portfolio projects"
                ]
            }

        # Default intelligent response
        reply = (
            f"I can assist you with your technology career journey, **{student_name}**!\n\n"
            f"Here are a few things you can ask me:\n"
            f"- Ask about any of the **15 tech roles** (e.g. *'Tell me about Cloud Engineer'* or *'What does a Data Scientist do?'*)\n"
            f"- Compare roles (e.g. *'Data Analyst vs Data Scientist'* or *'Frontend vs Backend'*)\n"
            f"- Ask for skill diagnostics (e.g. *'What skills am I missing?'*)\n"
            f"- Ask for portfolio ideas (e.g. *'What projects should I build?'*)"
        )
        return {
            "status": "success",
            "reply": reply,
            "suggestions": [
                "What are my Top 3 career matches?",
                "What skills should I learn next?",
                "Tell me about Machine Learning Engineer",
                "Suggest portfolio projects for me"
            ]
        }
