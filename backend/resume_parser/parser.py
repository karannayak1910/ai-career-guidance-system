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

    def parse_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Parses raw text (from file or user paste) and extracts structured student profile information.
        """
        if not raw_text:
            raw_text = ""

        # Normalize text for skill matching
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
            
            matched = False
            for alias in aliases:
                escaped = re.escape(alias.lower())
                # Handle special punctuation characters in languages like C++, C#, .NET
                if alias.lower() in ["c++", "c#", ".net"]:
                    pattern = r"(?:^|\s|[,\(\);\[\]\{\}])" + escaped + r"(?:$|\s|[,\(\);\[\]\{\}])"
                else:
                    pattern = r"(?:\b|_)" + escaped + r"(?:\b|_)"
                
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

            # Assign detected or default proficiency
            prof = self._detect_proficiency(raw_text, skill)
            extracted["skill_proficiencies"][skill] = prof

        return extracted

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses resume file and extracts structured student profile information.
        """
        raw_text = self.extract_text(file_path)
        return self.parse_text(raw_text)

    def _extract_name(self, text: str) -> str:
        """
        Robustly extracts student/candidate name from resume text.
        Handles titles, pipe/dash separators, inline email/phone, 'Name:' prefix, etc.
        """
        if not text:
            return ""

        # Strategy 1: Explicit "Name: <First> <Last>"
        name_match = re.search(r"(?:^|\n)\s*(?:Candidate\s+)?Name\s*[:\-]\s*([A-Za-z\.\'\s]{2,40})", text, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
            candidate = re.split(r"[,\|\–\—\-\(\n]", candidate)[0].strip()
            words = candidate.split()
            if 2 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.\'-]{2,25}$", w) for w in words):
                return candidate.title()

        # Strategy 2: First non-empty lines before section headings
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:8]:
            # Strip out email addresses, URLs, and phone numbers
            cleaned = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "", line)
            cleaned = re.sub(r"https?://\S+", "", cleaned)
            cleaned = re.sub(r"\+?\d[\d\s\-\(\)]{8,}\d", "", cleaned)
            
            # Split by delimiters like |, -, bullet, comma, parentheses
            parts = re.split(r"[\t\|\•\–\—\*\,\(\)\-]", cleaned)
            for part in parts:
                candidate = part.strip()
                if not candidate:
                    continue
                lower_cand = candidate.lower()
                # Skip words that cannot be a human name
                if any(w in lower_cand for w in [
                    "resume", "curriculum", "vitae", "cv", "portfolio", "profile", 
                    "education", "experience", "projects", "skills", "summary", "contact",
                    "engineer", "developer", "student", "intern", "github", "linkedin",
                    "objective", "phone", "email", "address", "page", "declaration",
                    "b.tech", "btech", "m.tech", "b.e", "b.sc", "computer", "science"
                ]):
                    continue
                
                words = candidate.split()
                if 2 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.\'-]{2,25}$", w) for w in words):
                    return candidate.title()
                elif len(words) == 1 and line == lines[0] and re.match(r"^[A-Za-z\.\'-]{3,25}$", words[0]):
                    return candidate.title()

        return ""

    def _extract_college(self, text: str) -> str:
        """
        Robustly extracts college/university name.
        """
        if not text:
            return ""

        # Prioritize education section if present
        edu_match = re.search(r"(?:education|academic|qualification|university|college)[\s\:\-]*\n([\s\S]{1,500})", text, re.IGNORECASE)
        search_corpus = edu_match.group(1) if edu_match else text

        patterns = [
            r"([A-Z][a-zA-Z \t\&\.\']+(?:Institute|University|College|Academy|Engineering College|Polytechnic)[a-zA-Z \t\&\,\.\']*)",
            r"\b(IIT\s+[A-Za-z]+|NIT\s+[A-Za-z]+|IIIT\s+[A-Za-z]+|BITS\s+[A-Za-z]+|DTU|NSUT|VIT|MIT|BITS Pilani|Stanford|Harvard)\b"
        ]
        for p in patterns:
            for match in re.finditer(p, search_corpus, re.IGNORECASE):
                res = match.group(1).strip()
                res = re.split(r"[\n\r]", res)[0].strip()
                res = re.sub(r"^(?:at|from|in|pursuing|graduated from|studied at|b\.?tech from|degree from)\s+", "", res, flags=re.IGNORECASE).strip()
                res = re.sub(r"\s*[\,\-]\s*(?:b\.?tech|b\.?e\.?|cse|it|bachelor|master|m\.?tech).*$", "", res, flags=re.IGNORECASE).strip()
                if 4 <= len(res) <= 80:
                    return res.title()

        return ""

    def _extract_branch(self, text: str) -> str:
        """Detect student branch / field of study with high specificity."""
        branches = [
            ("Artificial Intelligence", ["artificial intelligence", "ai & ds", "ai/ds", "ai/ml", "aiml", "ai and data science", "ai & machine learning"]),
            ("Data Science", ["data science", "data analytics", "big data analytics"]),
            ("Information Technology", ["information technology", "b.tech it", "bachelor of technology in it"]),
            ("Electrical Engineering", ["electrical & electronics", "electrical and electronics", "eee", "electrical engineering"]),
            ("Electronics & Communication", ["electronics & communication", "electronics and communication", "ece", "telecommunication", "electronics"]),
            ("Mechanical Engineering", ["mechanical engineering", "mechanical", "mech"]),
            ("Civil Engineering", ["civil engineering", "civil"]),
            ("Computer Science", ["computer science", "cse", "cs & e", "computer engineering", "computer science and engineering", "software engineering", r"\bcs\b"])
        ]
        lower_text = text.lower()
        for branch_name, keywords in branches:
            for kw in keywords:
                if kw.startswith(r"\b"):
                    pattern = kw
                else:
                    pattern = r"(?:\b|_)" + re.escape(kw) + r"(?:\b|_)"
                if re.search(pattern, lower_text):
                    return branch_name
        return "Computer Science"

    def _extract_semester(self, text: str) -> int:
        """Detect current semester (supports numbers, year words, Roman numerals)."""
        # Explicit semester label: Semester 6, Sem: 6, Sem-6
        match = re.search(r"(?:semester|sem)\s*[:\-]?\s*([1-8])\b", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Roman numeral semesters: Semester VI, Sem IV
        roman_match = re.search(r"(?:semester|sem)\s*[:\-]?\s*\b(I|II|III|IV|V|VI|VII|VIII)\b", text, re.IGNORECASE)
        if roman_match:
            roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
            return roman_map.get(roman_match.group(1).upper(), 6)

        # Year to semester mapping
        year_match = re.search(r"\b(1st|2nd|3rd|4th)\s+year\b", text, re.IGNORECASE)
        if year_match:
            mapping = {"1st": 2, "2nd": 4, "3rd": 6, "4th": 8}
            return mapping.get(year_match.group(1).lower(), 6)

        return 6

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

def parse_resume_text(text: str) -> Dict[str, Any]:
    parser = ResumeParser()
    return parser.parse_text(text)
