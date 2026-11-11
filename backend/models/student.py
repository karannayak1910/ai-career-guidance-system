"""
Student Profile model representing student academic background, skills, and preferences.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class StudentProfile:
    full_name: str
    branch: str
    current_semester: int
    graduation_year: int
    id: Optional[int] = None
    college_name: str = ""
    programming_languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    tools_technologies: List[str] = field(default_factory=list)
    technical_skills: List[str] = field(default_factory=list)
    skill_proficiencies: Dict[str, str] = field(default_factory=dict) # e.g. {"Python": "Advanced"}
    interest_areas: List[str] = field(default_factory=list)
    preferred_work_area: str = "Remote"
    preferred_career_type: str = "Full-time"
    hours_per_week: int = 10
    resume_filename: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        def parse_list(val):
            if isinstance(val, list):
                return [str(x).strip() for x in val if str(x).strip()]
            if isinstance(val, str) and val.strip():
                return [x.strip() for x in val.split(",") if x.strip()]
            return []

        proficiencies = data.get("skill_proficiencies", {})
        if isinstance(proficiencies, str):
            import json
            try:
                proficiencies = json.loads(proficiencies)
            except Exception:
                proficiencies = {}

        return cls(
            id=data.get("id"),
            full_name=data.get("full_name", "").strip(),
            college_name=data.get("college_name", "").strip(),
            branch=data.get("branch", "").strip(),
            current_semester=int(data.get("current_semester", 1)),
            graduation_year=int(data.get("graduation_year", 2026)),
            programming_languages=parse_list(data.get("programming_languages")),
            frameworks=parse_list(data.get("frameworks")),
            databases=parse_list(data.get("databases")),
            tools_technologies=parse_list(data.get("tools_technologies")),
            technical_skills=parse_list(data.get("technical_skills")),
            skill_proficiencies=proficiencies,
            interest_areas=parse_list(data.get("interest_areas")),
            preferred_work_area=data.get("preferred_work_area", "Remote"),
            preferred_career_type=data.get("preferred_career_type", "Full-time"),
            hours_per_week=int(data.get("hours_per_week", 10)),
            resume_filename=data.get("resume_filename", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "college_name": self.college_name,
            "branch": self.branch,
            "current_semester": self.current_semester,
            "graduation_year": self.graduation_year,
            "programming_languages": self.programming_languages,
            "frameworks": self.frameworks,
            "databases": self.databases,
            "tools_technologies": self.tools_technologies,
            "technical_skills": self.technical_skills,
            "skill_proficiencies": self.skill_proficiencies,
            "interest_areas": self.interest_areas,
            "preferred_work_area": self.preferred_work_area,
            "preferred_career_type": self.preferred_career_type,
            "hours_per_week": self.hours_per_week,
            "resume_filename": self.resume_filename
        }

    def get_all_skills(self) -> List[str]:
        """Aggregate unique skills across all categories."""
        combined = set()
        for s in (self.programming_languages + self.frameworks + 
                  self.databases + self.tools_technologies + self.technical_skills):
            if s and s.strip():
                combined.add(s.strip())
        return sorted(list(combined))

    def validate(self) -> List[str]:
        """Validate model integrity, returning list of validation error messages."""
        errors = []
        if not self.full_name:
            errors.append("Student Name is required.")
        if not self.branch:
            errors.append("College Branch is required.")
        if not (1 <= self.current_semester <= 12):
            errors.append("Current semester must be between 1 and 12.")
        if not (2020 <= self.graduation_year <= 2035):
            errors.append("Graduation year must be between 2020 and 2035.")
        if len(self.get_all_skills()) == 0 and len(self.interest_areas) == 0:
            errors.append("Please specify at least one skill or career interest area.")
        return errors
