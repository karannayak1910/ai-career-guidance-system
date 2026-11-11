"""
Resume Parser Module for AI Career Guidance System.
Extracts text from PDF & DOCX resumes, matching entities against the skill taxonomy.
"""
import re
import os
import json
from typing import Dict, Any, List, Optional

# Supported imports with graceful fallback
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

SKILLS_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_skills.json")

def load_skills_taxonomy() -> Dict[str, Any]:
    """Load skill taxonomy dictionary from career_skills.json."""
    if os.path.exists(SKILLS_DATA_PATH):
        try:
            with open(SKILLS_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("skills", {})
        except Exception as e:
            print("Error loading skills taxonomy:", e)
    return {}

class ResumeParser:
    def __init__(self):
        self.skills_taxonomy = load_skills_taxonomy()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using pypdf or PyPDF2."""
        text = ""
        if pypdf:
            try:
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text
            except Exception as e:
                print(f"pypdf extraction error: {e}")

        if PyPDF2:
            try:
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text
            except Exception as e:
                print(f"PyPDF2 extraction error: {e}")

        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file using python-docx."""
        if not docx:
            raise ImportError("python-docx is not installed.")
        
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        full_text.append(cell.text)
        return "\n".join(full_text)

    def extract_text(self, file_path: str) -> str:
        """Extract text depending on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        else:
            # Fallback plain text read
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses resume file and extracts structured student profile information.
        """
        raw_text = self.extract_text(file_path)
        normalized_text = " " + re.sub(r"\s+", " ", raw_text).lower() + " "

        extracted = {
            "full_name": self._extract_name(raw_text),
            "college_name": self._extract_college(raw_text),
            "branch": self._extract_branch(raw_text),
            "current_semester": self._extract_semester(raw_text),
            "graduation_year": self._extract_grad_year(raw_text),
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "tools_technologies": [],
            "technical_skills": [],
            "skill_proficiencies": {},
            "interest_areas": self._extract_interests(raw_text),
            "raw_text_snippet": raw_text[:600] + ("..." if len(raw_text) > 600 else "")
        }

        # Match skills against taxonomy
        matched_skills = {}
        for skill_name, info in self.skills_taxonomy.items():
            category = info.get("category", "Technical Skills")
            aliases = info.get("aliases", [skill_name.lower()])
            
            # Check skill name and aliases
            matched = False
            for alias in aliases:
                # Use regex with word boundaries or special handling for C++, C#
                escaped = re.escape(alias.lower())
                pattern = r"(?:\b|_)" + escaped + r"(?:\b|_)"
                if alias.lower() in ["c++", "c#", ".net"]:
                    pattern = r"(?:^|\s|[,\(\);])" + escaped + r"(?:$|\s|[,\(\);])"
                
                if re.search(pattern, normalized_text):
                    matched = True
                    break
            
            if matched:
                matched_skills[skill_name] = category

        # Distribute into appropriate profile lists
        for skill, category in matched_skills.items():
            if category == "Programming Languages":
                extracted["programming_languages"].append(skill)
            elif category == "Frameworks":
                extracted["frameworks"].append(skill)
            elif category == "Databases":
                extracted["databases"].append(skill)
            elif category in ["Tools", "Cloud Computing"]:
                extracted["tools_technologies"].append(skill)
            else:
                extracted["technical_skills"].append(skill)

            # Assign default or detected proficiency
            prof = self._detect_proficiency(raw_text, skill)
            extracted["skill_proficiencies"][skill] = prof

        return extracted

    def _extract_name(self, text: str) -> str:
        """Extract name heuristic from first non-empty lines."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Ignore lines containing typical header words
            lower = line.lower()
            if any(w in lower for w in ["resume", "curriculum", "cv", "email", "phone", "contact", "http"]):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.\'-]+$", w) for w in words):
                return line.title()
        return ""

    def _extract_college(self, text: str) -> str:
        """Extract college/university name heuristic."""
        patterns = [
            r"([A-Z][a-zA-Z\s]+(?:Institute|University|College|Academy|Engineering College)[a-zA-Z\s,]*)",
            r"(IIT\s+[A-Za-z]+|NIT\s+[A-Za-z]+|IIIT\s+[A-Za-z]+|BITS\s+[A-Za-z]+|DTU|NSUT|VIT)"
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                res = match.group(1).strip()
                # Clean up any multiline prefix
                if "\n" in res:
                    lines = [ln.strip() for ln in res.split("\n") if ln.strip()]
                    for ln in lines:
                        if any(w in ln.lower() for w in ["institute", "university", "college", "academy", "dtu", "iit", "nit"]):
                            return ln.title()
                if len(res) > 4 and len(res) < 80:
                    return res.title()
        return ""

    def _extract_branch(self, text: str) -> str:
        """Detect student branch / field of study."""
        branches = [
            ("Computer Science", ["computer science", "cse", "cs & e", "computer engineering"]),
            ("Information Technology", ["information technology", "it"]),
            ("Artificial Intelligence", ["artificial intelligence", "ai & ds", "ai/ml", "aiml"]),
            ("Data Science", ["data science", "data analytics"]),
            ("Electronics & Communication", ["electronics", "ece", "telecommunication"]),
            ("Electrical Engineering", ["electrical engineering", "eee"]),
            ("Mechanical Engineering", ["mechanical"]),
            ("Civil Engineering", ["civil"])
        ]
        lower_text = text.lower()
        for branch_name, keywords in branches:
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
                    return branch_name
        return "Computer Science" # default standard

    def _extract_semester(self, text: str) -> int:
        """Detect current semester."""
        match = re.search(r"(?:semester|sem)\s*[:\-]?\s*([1-8])\b", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Year to semester heuristic
        year_match = re.search(r"\b(1st|2nd|3rd|4th)\s+year\b", text, re.IGNORECASE)
        if year_match:
            mapping = {"1st": 2, "2nd": 4, "3rd": 6, "4th": 8}
            return mapping.get(year_match.group(1).lower(), 6)
        return 6 # Default 3rd year / 6th sem for college students

    def _extract_grad_year(self, text: str) -> int:
        """Detect graduation year."""
        years = re.findall(r"\b(202[4-9]|203[0-2])\b", text)
        if years:
            return int(years[-1])
        return 2026

    def _extract_interests(self, text: str) -> List[str]:
        """Detect interest areas from resume summary/projects."""
        interests_catalog = [
            "Artificial Intelligence", "Machine Learning", "Web Development",
            "Data Science", "Cybersecurity", "Cloud Computing",
            "Software Development", "Data Analytics"
        ]
        lower_text = text.lower()
        detected = []
        for area in interests_catalog:
            if re.search(r"\b" + re.escape(area.lower()) + r"\b", lower_text):
                detected.append(area)
        return detected if detected else ["Software Development", "Web Development"]

    def _detect_proficiency(self, text: str, skill: str) -> str:
        """Heuristic for skill proficiency: Beginner, Intermediate, or Advanced."""
        lower_text = text.lower()
        s_lower = skill.lower()
        # Look for phrases nearby
        pattern_adv = rf"(advanced|proficient|expert|lead|mastered).{{0,30}}\b{re.escape(s_lower)}\b|\b{re.escape(s_lower)}\b.{{0,30}}(advanced|proficient|expert)"
        if re.search(pattern_adv, lower_text):
            return "Advanced"
        
        pattern_beg = rf"(beginner|basic|learning|familiar with|elementary).{{0,30}}\b{re.escape(s_lower)}\b|\b{re.escape(s_lower)}\b.{{0,30}}(beginner|basic)"
        if re.search(pattern_beg, lower_text):
            return "Beginner"

        return "Intermediate"

def parse_resume_file(file_path: str) -> Dict[str, Any]:
    parser = ResumeParser()
    return parser.parse(file_path)
