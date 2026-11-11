"""
Script to generate realistic synthetic training dataset across all 15 technology career roles
and baseline sample student profiles.
"""
import csv
import random
import os

ROLE_PROFILES = {
    "data_analyst": {
        "skills": ["python", "sql", "statistics", "powerbi_tableau", "excel"],
        "optional_skills": ["database_general", "html_css"],
        "interests": {"interest_data": (4, 5), "interest_ai": (2, 3), "interest_web": (1, 2), "interest_cyber": (1, 2), "interest_cloud": (1, 2), "interest_software": (2, 3), "interest_ml": (2, 4)},
        "branches": [1, 2, 3, 5, 6]
    },
    "data_scientist": {
        "skills": ["python", "machine_learning", "statistics", "sql", "mathematics"],
        "optional_skills": ["deep_learning", "powerbi_tableau", "docker", "data_structures", "database_general"],
        "interests": {"interest_data": (4, 5), "interest_ai": (4, 5), "interest_ml": (4, 5), "interest_web": (1, 2), "interest_cyber": (1, 2), "interest_cloud": (2, 3), "interest_software": (2, 4)},
        "branches": [1, 2, 3, 4]
    },
    "ml_engineer": {
        "skills": ["python", "machine_learning", "docker", "fastapi_django", "data_structures"],
        "optional_skills": ["deep_learning", "sql", "linux", "aws_cloud", "mathematics"],
        "interests": {"interest_ml": (5, 5), "interest_ai": (4, 5), "interest_software": (3, 5), "interest_cloud": (3, 4), "interest_data": (3, 4), "interest_web": (1, 3), "interest_cyber": (1, 2)},
        "branches": [1, 2, 3, 4]
    },
    "ai_engineer": {
        "skills": ["python", "deep_learning", "mathematics", "machine_learning"],
        "optional_skills": ["docker", "linux", "cpp", "data_structures", "aws_cloud"],
        "interests": {"interest_ai": (5, 5), "interest_ml": (4, 5), "interest_data": (3, 4), "interest_software": (3, 4), "interest_cloud": (2, 4), "interest_web": (1, 2), "interest_cyber": (1, 2)},
        "branches": [1, 2, 3, 4]
    },
    "frontend_developer": {
        "skills": ["html_css", "javascript", "react"],
        "optional_skills": ["ui_ux_design", "docker", "nodejs"],
        "interests": {"interest_web": (5, 5), "interest_software": (3, 5), "interest_uiux": (3, 5), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_data": (1, 2), "interest_cyber": (1, 2), "interest_cloud": (1, 2)},
        "branches": [1, 2, 5, 6]
    },
    "backend_developer": {
        "skills": ["python", "sql", "database_general", "data_structures", "fastapi_django"],
        "optional_skills": ["docker", "linux", "nodejs", "aws_cloud", "java"],
        "interests": {"interest_software": (4, 5), "interest_cloud": (3, 5), "interest_web": (3, 4), "interest_data": (2, 4), "interest_ai": (1, 3), "interest_ml": (1, 2), "interest_cyber": (2, 3)},
        "branches": [1, 2, 5]
    },
    "fullstack_developer": {
        "skills": ["html_css", "javascript", "react", "nodejs", "sql", "database_general"],
        "optional_skills": ["docker", "python", "git", "aws_cloud"],
        "interests": {"interest_web": (5, 5), "interest_software": (4, 5), "interest_cloud": (3, 4), "interest_data": (2, 3), "interest_ai": (1, 3), "interest_ml": (1, 2), "interest_cyber": (1, 2)},
        "branches": [1, 2, 5, 6]
    },
    "python_developer": {
        "skills": ["python", "fastapi_django", "sql", "data_structures"],
        "optional_skills": ["linux", "docker", "html_css", "database_general", "statistics"],
        "interests": {"interest_software": (4, 5), "interest_web": (3, 4), "interest_data": (2, 4), "interest_ai": (2, 4), "interest_ml": (2, 3), "interest_cyber": (1, 2), "interest_cloud": (2, 4)},
        "branches": [1, 2, 3, 5]
    },
    "java_developer": {
        "skills": ["java", "spring_boot", "sql", "data_structures", "database_general"],
        "optional_skills": ["docker", "linux", "git", "aws_cloud"],
        "interests": {"interest_software": (5, 5), "interest_cloud": (3, 4), "interest_web": (2, 4), "interest_data": (2, 3), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_cyber": (1, 3)},
        "branches": [1, 2, 5]
    },
    "software_engineer": {
        "skills": ["data_structures", "cpp", "java", "python", "mathematics"],
        "optional_skills": ["sql", "linux", "git", "docker", "database_general"],
        "interests": {"interest_software": (5, 5), "interest_web": (2, 4), "interest_cloud": (2, 4), "interest_ai": (2, 4), "interest_ml": (1, 3), "interest_data": (2, 3), "interest_cyber": (1, 3)},
        "branches": [1, 2, 5]
    },
    "cybersecurity_analyst": {
        "skills": ["networking", "cybersecurity", "linux", "python"],
        "optional_skills": ["docker", "aws_cloud", "sql", "data_structures"],
        "interests": {"interest_cyber": (5, 5), "interest_software": (3, 4), "interest_cloud": (2, 4), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_web": (1, 2), "interest_data": (1, 3)},
        "branches": [1, 2, 5]
    },
    "cloud_engineer": {
        "skills": ["aws_cloud", "docker", "linux", "networking"],
        "optional_skills": ["kubernetes", "python", "database_general", "cybersecurity"],
        "interests": {"interest_cloud": (5, 5), "interest_software": (3, 5), "interest_cyber": (2, 4), "interest_web": (2, 3), "interest_ai": (1, 3), "interest_ml": (1, 2), "interest_data": (1, 3)},
        "branches": [1, 2, 5]
    },
    "devops_engineer": {
        "skills": ["docker", "kubernetes", "linux", "aws_cloud"],
        "optional_skills": ["python", "networking", "fastapi_django", "git"],
        "interests": {"interest_cloud": (5, 5), "interest_software": (4, 5), "interest_cyber": (2, 4), "interest_web": (2, 3), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_data": (1, 2)},
        "branches": [1, 2, 5]
    },
    "database_administrator": {
        "skills": ["sql", "database_general", "linux"],
        "optional_skills": ["python", "aws_cloud", "docker", "statistics"],
        "interests": {"interest_data": (4, 5), "interest_software": (3, 5), "interest_cloud": (3, 4), "interest_web": (1, 3), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_cyber": (2, 4)},
        "branches": [1, 2, 5, 6]
    },
    "ui_ux_developer": {
        "skills": ["html_css", "javascript", "ui_ux_design"],
        "optional_skills": ["react", "nodejs"],
        "interests": {"interest_uiux": (5, 5), "interest_web": (4, 5), "interest_software": (3, 4), "interest_data": (1, 2), "interest_ai": (1, 2), "interest_ml": (1, 2), "interest_cyber": (1, 2), "interest_cloud": (1, 2)},
        "branches": [1, 2, 5, 6]
    }
}

SKILL_KEYS = [
    "python", "java", "cpp", "html_css", "javascript", "sql", 
    "statistics", "mathematics", "machine_learning", "networking", 
    "aws_cloud", "database_general", "react", "nodejs", "docker", 
    "kubernetes", "linux", "deep_learning", "data_structures", 
    "powerbi_tableau", "excel", "ui_ux_design", "spring_boot", 
    "fastapi_django", "cybersecurity"
]

INTEREST_KEYS = [
    "interest_ai", "interest_ml", "interest_web", "interest_data", 
    "interest_cyber", "interest_cloud", "interest_software", "interest_uiux"
]

def generate_dataset(num_samples_per_role=65):
    rows = []
    header = SKILL_KEYS + INTEREST_KEYS + ["branch_code", "semester", "career_role"]
    
    random.seed(42)
    for role, profile in ROLE_PROFILES.items():
        for _ in range(num_samples_per_role):
            row_data = {k: 0 for k in SKILL_KEYS}
            
            # Set required skills with very high probability (90-98%)
            for s in profile["skills"]:
                if s in row_data:
                    row_data[s] = 1 if random.random() < 0.94 else 0
                    
            # Set optional skills with moderate probability (40-65%)
            for s in profile.get("optional_skills", []):
                if s in row_data:
                    row_data[s] = 1 if random.random() < 0.55 else 0
                    
            # Background noise (10% random chance)
            for k in SKILL_KEYS:
                if k not in profile["skills"] and k not in profile.get("optional_skills", []):
                    row_data[k] = 1 if random.random() < 0.10 else 0

            # Interests
            for ik in INTEREST_KEYS:
                min_v, max_v = profile["interests"].get(ik, (1, 3))
                row_data[ik] = random.randint(min_v, max_v)
                
            # Branch code
            row_data["branch_code"] = random.choice(profile["branches"])
            # Semester
            row_data["semester"] = random.randint(2, 8)
            # Career role
            row_data["career_role"] = role
            
            row = [row_data[col] for col in header]
            rows.append(row)
            
    return header, rows

def main():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    os.makedirs(target_dir, exist_ok=True)
    csv_path = os.path.join(target_dir, "training_data.csv")
    
    header, rows = generate_dataset(num_samples_per_role=65) # 65 * 15 = 975 samples
    random.shuffle(rows)
    
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} training samples across 15 roles into {csv_path}")

if __name__ == "__main__":
    main()
