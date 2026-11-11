"""
Database Manager for AI Career Guidance System.
Handles SQLite schema creation for all 9 core entities + Users authentication table,
seeding career knowledge base, and providing comprehensive CRUD operations.
"""
import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_guidance.db"))
ROLES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roles.json"))

def get_db_connection():
    """Create and return a row-mapped SQLite database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize SQLite tables for users and core entities, and seed career roles."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 0. Users table (Authentication: username, email, password, dob)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        dob TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 1. Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        full_name TEXT NOT NULL,
        college_name TEXT,
        branch TEXT NOT NULL,
        current_semester INTEGER NOT NULL,
        graduation_year INTEGER NOT NULL,
        programming_languages TEXT,
        frameworks TEXT,
        databases TEXT,
        tools_technologies TEXT,
        technical_skills TEXT,
        skill_proficiencies TEXT,
        interest_areas TEXT,
        preferred_work_area TEXT,
        preferred_career_type TEXT,
        hours_per_week INTEGER DEFAULT 12,
        resume_filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # Ensure user_id column in students if table was previously created
    cursor.execute("PRAGMA table_info(students);")
    columns = [col[1] for col in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN user_id INTEGER REFERENCES users(id);")

    # 2. Student Skills table (Normalized relational skills)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        category TEXT,
        proficiency TEXT DEFAULT 'Intermediate',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 3. Student Interests table (Normalized relational interests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_interests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        interest_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 4. Career Roles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_roles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        domain TEXT,
        description TEXT,
        average_salary TEXT,
        market_demand TEXT,
        learning_difficulty TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Career Required Skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_required_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_role_id TEXT NOT NULL,
        skill_name TEXT NOT NULL,
        skill_type TEXT DEFAULT 'required',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (career_role_id) REFERENCES career_roles(id) ON DELETE CASCADE
    );
    """)

    # 6. Career Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        top_career_1 TEXT,
        score_1 REAL,
        top_career_2 TEXT,
        score_2 REAL,
        top_career_3 TEXT,
        score_3 REAL,
        full_result_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # Backward compatibility table alias for recommendations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        top_career_1 TEXT,
        score_1 REAL,
        top_career_2 TEXT,
        score_2 REAL,
        top_career_3 TEXT,
        score_3 REAL,
        full_result_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 7. Skill Gap Analysis table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_gap_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        career_role_id TEXT NOT NULL,
        known_skills_json TEXT,
        partial_skills_json TEXT,
        missing_skills_json TEXT,
        match_percentage REAL,
        full_gap_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 8. Learning Roadmaps table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        career_role_id TEXT NOT NULL,
        milestones_json TEXT,
        weekly_hours INTEGER,
        full_roadmap_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 9. Roadmap Progress table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmap_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        career_role TEXT NOT NULL,
        milestone_month INTEGER NOT NULL,
        task_id TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        UNIQUE(student_id, career_role, task_id),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Seed career_roles & career_required_skills if empty
    cursor.execute("SELECT COUNT(*) FROM career_roles")
    role_count = cursor.fetchone()[0]
    if role_count == 0 and os.path.exists(ROLES_FILE):
        try:
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                roles_data = json.load(f).get("roles", [])
                for r in roles_data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO career_roles (id, title, domain, description, average_salary, market_demand, learning_difficulty)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r.get("id"),
                        r.get("title"),
                        r.get("domain", ""),
                        r.get("description", ""),
                        r.get("average_salary", ""),
                        r.get("market_demand", "High"),
                        r.get("learning_difficulty", "Intermediate")
                    ))
                    # Seed required skills
                    for req_s in r.get("required_skills", []):
                        cursor.execute("""
                            INSERT INTO career_required_skills (career_role_id, skill_name, skill_type)
                            VALUES (?, ?, 'required')
                        """, (r.get("id"), req_s))
                    # Seed preferred skills
                    for pref_s in r.get("preferred_skills", []):
                        cursor.execute("""
                            INSERT INTO career_required_skills (career_role_id, skill_name, skill_type)
                            VALUES (?, ?, 'preferred')
                        """, (r.get("id"), pref_s))
            conn.commit()
            print(f"Seeded {len(roles_data)} career roles into SQLite database.")
        except Exception as e:
            print("Notice seeding career_roles:", e)

    conn.close()
    print("Database initialized successfully at", DB_PATH)

# ==========================================
# User Authentication Helpers
# ==========================================

def create_user(username, email, password, dob):
    """
    Register a new user with username, email, password hash, and date of birth (D.O.B).
    Returns (user_id, error_message).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = generate_password_hash(password)
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, dob)
            VALUES (?, ?, ?, ?)
        """, (username.strip(), email.strip().lower(), pwd_hash, dob.strip()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id, None
    except sqlite3.IntegrityError as e:
        conn.close()
        err_msg = str(e).lower()
        if "username" in err_msg:
            return None, "Username already exists. Please choose a different username."
        elif "email" in err_msg:
            return None, "Email is already registered. Please sign in or use another email."
        return None, "An account with this username or email already exists."
    except Exception as e:
        conn.close()
        return None, str(e)

def authenticate_user(username_or_email, password):
    """
    Authenticate user by username or email and plaintext password.
    Returns (user_dict, error_message).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    val = username_or_email.strip().lower()
    cursor.execute("""
        SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?
    """, (val, val))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None, "No account found with that username or email."

    user = dict(row)
    if not check_password_hash(user["password_hash"], password):
        return None, "Incorrect password. Please try again."

    user.pop("password_hash", None)
    return user, None

def get_user_by_id(user_id):
    """Fetch user profile by ID without password hash."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, dob, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_profile_by_user_id(user_id):
    """Find student profile linked to a specific user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return get_student_profile(row["id"])

# ==========================================
# Student Profile Helpers
# ==========================================

def save_student_profile(profile_data):
    """
    Save or update a student profile in SQLite across students, student_skills,
    and student_interests tables.
    Returns the student_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    def stringify(val):
        if isinstance(val, (list, tuple)):
            return ", ".join(str(x) for x in val)
        if isinstance(val, dict):
            return json.dumps(val)
        return str(val) if val is not None else ""

    student_id = profile_data.get("id")
    user_id = profile_data.get("user_id")

    prog_langs_list = profile_data.get("programming_languages", [])
    frameworks_list = profile_data.get("frameworks", [])
    databases_list = profile_data.get("databases", [])
    tools_list = profile_data.get("tools_technologies", [])
    tech_skills_list = profile_data.get("technical_skills", [])
    proficiencies_dict = profile_data.get("skill_proficiencies", {})
    interests_list = profile_data.get("interest_areas", [])

    prog_langs = stringify(prog_langs_list)
    frameworks = stringify(frameworks_list)
    databases = stringify(databases_list)
    tools = stringify(tools_list)
    tech_skills = stringify(tech_skills_list)
    proficiencies = stringify(proficiencies_dict)
    interests = stringify(interests_list)

    if student_id:
        cursor.execute("""
            UPDATE students SET
                user_id = COALESCE(?, user_id),
                full_name = ?,
                college_name = ?,
                branch = ?,
                current_semester = ?,
                graduation_year = ?,
                programming_languages = ?,
                frameworks = ?,
                databases = ?,
                tools_technologies = ?,
                technical_skills = ?,
                skill_proficiencies = ?,
                interest_areas = ?,
                preferred_work_area = ?,
                preferred_career_type = ?,
                hours_per_week = ?,
                resume_filename = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            user_id,
            profile_data.get("full_name"),
            profile_data.get("college_name", ""),
            profile_data.get("branch"),
            int(profile_data.get("current_semester", 1)),
            int(profile_data.get("graduation_year", 2026)),
            prog_langs,
            frameworks,
            databases,
            tools,
            tech_skills,
            proficiencies,
            interests,
            profile_data.get("preferred_work_area", "Remote"),
            profile_data.get("preferred_career_type", "Full-time"),
            int(profile_data.get("hours_per_week", 12)),
            profile_data.get("resume_filename", ""),
            student_id
        ))
    else:
        cursor.execute("""
            INSERT INTO students (
                user_id, full_name, college_name, branch, current_semester, graduation_year,
                programming_languages, frameworks, databases, tools_technologies,
                technical_skills, skill_proficiencies, interest_areas,
                preferred_work_area, preferred_career_type, hours_per_week, resume_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            profile_data.get("full_name"),
            profile_data.get("college_name", ""),
            profile_data.get("branch"),
            int(profile_data.get("current_semester", 1)),
            int(profile_data.get("graduation_year", 2026)),
            prog_langs,
            frameworks,
            databases,
            tools,
            tech_skills,
            proficiencies,
            interests,
            profile_data.get("preferred_work_area", "Remote"),
            profile_data.get("preferred_career_type", "Full-time"),
            int(profile_data.get("hours_per_week", 12)),
            profile_data.get("resume_filename", "")
        ))
        student_id = cursor.lastrowid

    # Sync student_skills table
    cursor.execute("DELETE FROM student_skills WHERE student_id = ?", (student_id,))
    all_skill_groups = [
        (prog_langs_list, "Programming Languages"),
        (frameworks_list, "Frameworks"),
        (databases_list, "Databases"),
        (tools_list, "Tools & Technologies"),
        (tech_skills_list, "Technical Skills")
    ]
    seen_skills = set()
    for s_list, cat in all_skill_groups:
        for s in s_list:
            s_clean = s.strip()
            if s_clean and s_clean not in seen_skills:
                seen_skills.add(s_clean)
                prof = proficiencies_dict.get(s_clean, "Intermediate")
                cursor.execute("""
                    INSERT INTO student_skills (student_id, skill_name, category, proficiency)
                    VALUES (?, ?, ?, ?)
                """, (student_id, s_clean, cat, prof))

    # Sync student_interests table
    cursor.execute("DELETE FROM student_interests WHERE student_id = ?", (student_id,))
    for interest in interests_list:
        i_clean = interest.strip()
        if i_clean:
            cursor.execute("""
                INSERT INTO student_interests (student_id, interest_name)
                VALUES (?, ?)
            """, (student_id, i_clean))

    conn.commit()
    conn.close()
    return student_id

def get_student_profile(student_id):
    """Retrieve student profile by ID as a clean dictionary with parsed lists and dicts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    profile = dict(row)

    # Parse proficiencies JSON if valid
    try:
        profile["skill_proficiencies"] = json.loads(profile["skill_proficiencies"]) if profile["skill_proficiencies"] else {}
    except Exception:
        profile["skill_proficiencies"] = {}

    # Fetch relational skills from student_skills
    cursor.execute("SELECT skill_name, category, proficiency FROM student_skills WHERE student_id = ?", (student_id,))
    skills_rows = cursor.fetchall()
    profile["relational_skills"] = [dict(r) for r in skills_rows]

    # Fetch relational interests from student_interests
    cursor.execute("SELECT interest_name FROM student_interests WHERE student_id = ?", (student_id,))
    interest_rows = cursor.fetchall()
    profile["relational_interests"] = [r["interest_name"] for r in interest_rows]

    conn.close()
    return profile

def get_latest_student_profile():
    """Retrieve the most recently registered/updated student profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY updated_at DESC, id DESC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    student_id = row["id"]
    conn.close()
    return get_student_profile(student_id)

def save_recommendations(student_id, rec_data):
    """Save recommendation results snapshot into both career_recommendations and recommendations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    top_3 = rec_data.get("top_3", [])
    c1, s1 = (top_3[0]["title"], top_3[0]["match_score"]) if len(top_3) > 0 else ("", 0.0)
    c2, s2 = (top_3[1]["title"], top_3[1]["match_score"]) if len(top_3) > 1 else ("", 0.0)
    c3, s3 = (top_3[2]["title"], top_3[2]["match_score"]) if len(top_3) > 2 else ("", 0.0)
    result_json = json.dumps(rec_data)

    cursor.execute("""
        INSERT INTO career_recommendations (
            student_id, top_career_1, score_1, top_career_2, score_2, top_career_3, score_3, full_result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, c1, s1, c2, s2, c3, s3, result_json))

    cursor.execute("""
        INSERT INTO recommendations (
            student_id, top_career_1, score_1, top_career_2, score_2, top_career_3, score_3, full_result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, c1, s1, c2, s2, c3, s3, result_json))

    conn.commit()
    conn.close()

def get_latest_recommendation(student_id):
    """Get the latest saved recommendation result for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM career_recommendations WHERE student_id = ? ORDER BY created_at DESC LIMIT 1",
        (student_id,)
    )
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "SELECT * FROM recommendations WHERE student_id = ? ORDER BY created_at DESC LIMIT 1",
            (student_id,)
        )
        row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    res = dict(row)
    try:
        res["full_result"] = json.loads(res["full_result_json"])
    except Exception:
        res["full_result"] = {}
    return res

def save_skill_gap_analysis(student_id, career_role_id, gap_data):
    """Persist skill gap diagnostic snapshot into skill_gap_analysis table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    known = json.dumps(gap_data.get("known_skills", []))
    partial = json.dumps(gap_data.get("partially_matched_skills", []))
    missing = json.dumps(gap_data.get("missing_skills", []))
    match_pct = float(gap_data.get("match_percentage", 0.0))
    full_json = json.dumps(gap_data)

    cursor.execute("""
        INSERT INTO skill_gap_analysis (
            student_id, career_role_id, known_skills_json, partial_skills_json, missing_skills_json, match_percentage, full_gap_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_id, career_role_id, known, partial, missing, match_pct, full_json))

    conn.commit()
    conn.close()

def get_latest_skill_gap_analysis(student_id, career_role_id=None):
    """Retrieve the latest saved skill gap record for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if career_role_id:
        cursor.execute("""
            SELECT * FROM skill_gap_analysis 
            WHERE student_id = ? AND career_role_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id, career_role_id))
    else:
        cursor.execute("""
            SELECT * FROM skill_gap_analysis 
            WHERE student_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    res = dict(row)
    try:
        res["data"] = json.loads(res["full_gap_json"])
    except Exception:
        res["data"] = {}
    return res

def save_learning_roadmap_record(student_id, career_role_id, roadmap_data):
    """Persist generated learning roadmap into learning_roadmaps table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    milestones = json.dumps(roadmap_data.get("milestones", []))
    hours = int(roadmap_data.get("weekly_hours", 12))
    full_json = json.dumps(roadmap_data)

    cursor.execute("""
        INSERT INTO learning_roadmaps (
            student_id, career_role_id, milestones_json, weekly_hours, full_roadmap_json
        ) VALUES (?, ?, ?, ?, ?)
    """, (student_id, career_role_id, milestones, hours, full_json))

    conn.commit()
    conn.close()

def get_learning_roadmap_record(student_id, career_role_id=None):
    """Retrieve saved learning roadmap record for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if career_role_id:
        cursor.execute("""
            SELECT * FROM learning_roadmaps 
            WHERE student_id = ? AND career_role_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id, career_role_id))
    else:
        cursor.execute("""
            SELECT * FROM learning_roadmaps 
            WHERE student_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    res = dict(row)
    try:
        res["data"] = json.loads(res["full_roadmap_json"])
    except Exception:
        res["data"] = {}
    return res

def toggle_roadmap_task(student_id, career_role, task_id, is_completed, milestone_month=1):
    """Set completed status for a checklist task item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    completed_at = datetime.utcnow().isoformat() if is_completed else None
    cursor.execute("""
        INSERT INTO roadmap_progress (student_id, career_role, milestone_month, task_id, is_completed, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, career_role, task_id) DO UPDATE SET
            is_completed = excluded.is_completed,
            completed_at = excluded.completed_at
    """, (student_id, career_role, milestone_month, task_id, 1 if is_completed else 0, completed_at))

    conn.commit()
    conn.close()

def get_roadmap_progress(student_id, career_role):
    """Get all completed task IDs for a student and role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, is_completed FROM roadmap_progress
        WHERE student_id = ? AND career_role = ?
    """, (student_id, career_role))
    rows = cursor.fetchall()
    conn.close()
    return {row["task_id"]: bool(row["is_completed"]) for row in rows}
