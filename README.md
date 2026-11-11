# AI Career Guidance System 🎯

An intelligent AI-powered platform designed to help students choose the right career path based on their skills, academic background, and interests.

> 🌐 **Live Cloud Deployment (24/7):** [https://ai-career-guidance-system-fm0s.onrender.com](https://ai-career-guidance-system-fm0s.onrender.com)  
> 📱 **Direct Mobile Link (All Devices):** [https://ai-career-guidance-system-fm0s.onrender.com/](https://ai-career-guidance-system-fm0s.onrender.com/)  
> 🐙 **GitHub Repository:** [https://github.com/karannayak1910/ai-career-guidance-system](https://github.com/karannayak1910/ai-career-guidance-system)

### Key Features
- **Student Profile Analysis:** Collect skills, interests, academic details, and resumes.
- **AI Career Recommendations:** Suggest the Top 3 suitable technology careers with match percentages.
- **Skill Gap Analysis:** Identify existing, partially matched, and missing skills.
- **Personalized Learning Roadmap:** Generate monthly learning plans with free resources and practical projects.

### AI Technologies
- Rule-Based AI
- Decision Tree Classification
- Deductive Reasoning
- Machine Learning

### Technology Stack
- Python
- Flask
- HTML, CSS, JavaScript
- Scikit-learn
- Pandas and NumPy
- SQLite
- Chart.js

### Project Goal
To provide students with intelligent, personalized, and actionable career guidance that helps them understand their current skills and prepare for future technology careers.

---

## 🌟 Core System Capabilities

### 1. Student Profile Collection & Resume Ingestion Studio
- **Academic & Personal Info**: Student Name, College Name, College Branch (CSE, IT, AI/DS, Data Science, ECE, EEE, Mechanical, Civil, etc.), Current Semester (1–8), and Graduation Year.
- **Granular Skill Proficiency**: Interactive multi-select badges across Programming Languages, Frameworks, Databases, Tools/DevOps, and Core Technical Competencies with individual proficiencies (*Beginner*, *Intermediate*, *Advanced*).
- **Interests & Preferences**: Domain checkboxes (AI, ML, Web, Data Science, Cybersecurity, Cloud, Software Dev, Analytics), work mode (Remote/Hybrid/On-site), career role type, and a weekly learning availability slider (5–40 hrs/week).
- **Automated Resume Ingestion**: Drag-and-drop upload supporting both **PDF** (`pypdf` / `PyPDF2`) and **DOCX** (`python-docx`).
- **Interactive Review Modal**: Extracted entities are displayed in an extraction preview modal before SQLite persistence.

### 2. Intelligent Career Recommendation Engine
- **Top 3 Recommended Careers**: Dynamically ranks candidate suitability across **15 technology career roles**:
  1. **Data Analyst**
  2. **Data Scientist**
  3. **Machine Learning Engineer**
  4. **AI Engineer**
  5. **Frontend Developer**
  6. **Backend Developer**
  7. **Full Stack Developer**
  8. **Python Developer**
  9. **Java Developer**
  10. **Software Engineer**
  11. **Cybersecurity Analyst**
  12. **Cloud Engineer**
  13. **DevOps Engineer**
  14. **Database Administrator (DBA)**
  15. **UI/UX Developer**
- **Dynamic Percentage Match Scores**: Blended dynamically from:
  - Technical Skills Alignment (40%)
  - Domain Interest Alignment (25%)
  - Scikit-Learn Decision Tree Probability (25%)
  - Deductive Rule-Based Adjustments (10%)
- **Model Disagreement Explanation**: Explains divergences whenever the Decision Tree ML classifier differs from the Rule Engine's top recommendation.
- **Chart.js Radar Chart**: 15-axis multidimensional competency visualization.

### 3. Deep-Dive Skill Gap Analysis
- **Three-Tier Classification**:
  - 🟢 **Known Skills**: Acquired competencies with Intermediate/Advanced mastery.
  - 🟠 **Partially Matched Skills**: Transferrable knowledge (e.g. knowing SQL for PostgreSQL, knowing React for Next.js).
  - 🔴 **Missing Skills**: Prioritized as *Critical* vs *Recommended*.
- **Hiring Context**: Industry explanations of **Why This Skill Matters** in enterprise hiring, plus direct links to official documentation and tutorials.
- **Visual Doughnut Chart**: Interactive percentage breakdown of your skill portfolio.

### 4. Personalized 4-Month Learning Roadmap & Checklist
- **Structured Milestones**:
  - *Month 1*: Core Fundamentals & Prerequisite Foundations.
  - *Month 2*: Modern Frameworks & Practical Application.
  - *Month 3*: Advanced Architectures, Testing & Cloud Integration.
  - *Month 4*: Flagship Capstone Portfolio & Interview Preparation.
- **Curated Free Resources**: Official documentation links and verified YouTube tutorial playlists.
- **Hands-on Projects**: Capstone project briefs with expected technical deliverables.
- **Interactive Checklist**: Dynamic checkboxes synced directly to SQLite with real-time completion tracking.

### 5. CareerAI Advisor Chatbot
- **Conversational Career Guidance**: Floating, context-aware chatbot widget on every page.
- **Context-Aware Responses**: Grounded in the student's personal skills, Top 3 matches, and missing competencies.
- **Quick-Prompt Suggestions**: One-click prompt chips for quick role comparisons, project advice, and next steps.

### 6. User Authentication & Login Studio (`/login`)
- **Secure Student Registration & Sign In**: Supports user authentication with:
  - **User Name** (Unique handle)
  - **Email** (Unique valid email address)
  - **Date of Birth (D.O.B)** (Validated calendar picker)
  - **Password** (Securely salted and hashed using Werkzeug PBKDF2:SHA256)
- **Session Management**: Session-aware top navigation that dynamically displays the logged-in student's identity and provides an instant one-click sign-out action.

---

## 🎨 Design System & Theme

- **Maroon** (`#800020`, `#5C0017`, `#9E1B32`, `#FDF2F4`)
- **Light Yellow** (`#FFFDF0`, `#FEF9E7`, `#FEF3C7`, `#92400E`)
- **Light Blue** (`#EBF5FB`, `#F0F9FF`, `#E0F2FE`, `#0284C7`)
- **White Backgrounds** (`#FFFFFF`, `#F8FAFC`)
- **Subtle Purple Accents** (`#7C3AED`, `#F3E8FF`)

---

## 🗄️ Database Architecture (SQLite Core Tables)

The SQLite database (`data/career_guidance.db`) implements 10 relational tables:
1. `users`: Authentication records storing username, email, password hash, and date of birth (D.O.B).
2. `students`: Stores core student profile records, academics, and preferences linked to `user_id`.
3. `student_skills`: Normalized table mapping student skills, categories, and proficiencies.
4. `student_interests`: Normalized table storing individual student interest areas.
5. `career_roles`: Master knowledge base of all 15 tech career profiles.
6. `career_required_skills`: Required and preferred skills mapped to each career role (182 requirements).
7. `career_recommendations`: Persisted AI recommendation scores and Top 3 snapshots.
8. `skill_gap_analysis`: Diagnostic snapshots of Known, Partial, and Missing skills.
9. `learning_roadmaps`: Generated 4-month milestone curricula and deliverables.
10. `roadmap_progress`: Checkbox task completion states synced in real time.

---

## 🌐 Backend REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user account with username, email, password, and D.O.B |
| `POST` | `/api/auth/login` | Sign in using username/email and password, establishing session |
| `POST` | `/api/auth/logout` | Sign out and clear active session |
| `GET` | `/api/auth/me` | Verify authentication state and retrieve active user/student profile |
| `POST` | `/api/profile` | Save/update student profile (persists to `students`, `student_skills`, `student_interests`) |
| `POST` | `/api/resume/upload` | Ingest and parse PDF/DOCX resume file |
| `GET` | `/api/profile/<student_id>` | Retrieve full student profile with relational skills and interests |
| `POST` | `/api/recommendations/<student_id>` | Run AI recommendation engine and persist Top 3 matches |
| `GET` | `/api/recommendations/<student_id>` | Retrieve latest Top 3 career matches and radar chart telemetry |
| `GET` | `/api/skill-gap/<student_id>` | Retrieve Known / Partial / Missing skill gap analysis |
| `POST` | `/api/roadmap/<student_id>` | Generate personalized 4-month learning roadmap |
| `GET` | `/api/roadmap/<student_id>` | Retrieve roadmap milestones and task checklist |
| `POST` | `/api/roadmap/progress` | Update completed state for a learning task item |
| `POST` | `/api/chat` | Conversational CareerAI Advisor chatbot endpoint |

---

## 📂 Project Directory Structure

```text
AI Career Guidance System/
├── backend/
│   ├── app.py                      # Flask Application entry point & route registration
│   ├── routes/
│   │   ├── __init__.py             # Route blueprint exports
│   │   ├── auth_routes.py          # User authentication (/api/auth: login, register, logout, me)
│   │   ├── profile_routes.py       # Profile saving, editing, fetching (/api/profile)
│   │   ├── resume_routes.py        # PDF/DOCX resume parsing (/api/resume/upload)
│   │   ├── recommendation_routes.py# AI matching APIs (/api/recommendations/<id>)
│   │   ├── roadmap_routes.py       # Skill gap & roadmap APIs (/api/skill-gap, /api/roadmap)
│   │   └── chat_routes.py          # Conversational CareerAI Advisor (/api/chat)
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   ├── decision_tree_model.py  # Scikit-learn DecisionTreeClassifier (trained on 15 classes)
│   │   ├── rule_engine.py          # Deductive rule-based logic & gating
│   │   ├── matcher.py              # Blended weighted similarity scoring & disagreement analysis
│   │   ├── skill_gap_analyzer.py   # 3-tier Known, Partial, Missing skill categorization
│   │   ├── roadmap_generator.py    # 4-month milestone & curated resource generator
│   │   └── career_chatbot.py       # Grounded conversational career counselor
│   ├── resume_parser/
│   │   ├── __init__.py
│   │   └── parser.py               # PDF & DOCX text extractor & entity matcher
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                   # SQLite 9-table schema creation, seeding & CRUD
│   ├── models/
│   │   ├── __init__.py
│   │   └── student.py              # Data structures & validation
│   └── utils/
│       ├── __init__.py
│       ├── test_evaluator.py       # Comprehensive 14-subsystem & 5-test-case runner
│       ├── test_suite.py           # In-process Flask integration test suite
│       └── generate_training_data.py # 975-row dataset generator across 15 career classes
├── data/
│   ├── career_roles.json           # 15 tech career profiles with salary, skills, projects
│   ├── career_skills.json          # 45+ skill definitions, links & explanations
│   ├── training_data.csv           # 975-sample synthetic training dataset
│   ├── decision_tree_model.joblib  # Serialized Scikit-learn model
│   ├── career_guidance.db          # SQLite relational database (9 tables)
│   └── sample_resumes/             # Sample resumes (.docx/.pdf) for testing
├── frontend/
│   ├── index.html                  # Landing page & feature showcase
│   ├── login.html                  # Sign in & registration (Username, Email, Password, D.O.B)
│   ├── profile.html                # Registration & resume parser studio
│   ├── dashboard.html              # Student dashboard & career summary
│   ├── recommendations.html        # Top 3 matches, radar chart, 15-role rankings
│   ├── career_details.html         # Individual career deep-dive
│   ├── skill_gap.html              # 3-column Known/Partial/Missing breakdown
│   ├── roadmap.html                # 4-month milestone checklist
│   ├── css/
│   │   ├── styles.css              # Theme variables, typography & layout
│   │   ├── components.css          # Cards, buttons, dropzones, badges, modals
│   │   └── chatbot.css             # CareerAI Advisor floating widget styles
│   └── js/
│       ├── main.js                 # Toast notifications & navbar sync
│       ├── login.js                # Auth controller for Sign In & Registration
│       ├── profile.js              # Tag pickers, proficiencies & resume dropzone
│       ├── dashboard.js            # Dashboard stats & doughnut chart
│       ├── recommendations.js      # Match cards & 15-role radar chart
│       ├── career_details.js       # Career page logic
│       ├── skill_gap.js            # 15-role gap tab switching
│       ├── roadmap.js              # Milestone checklist & SQLite progress sync
│       └── chatbot.js              # CareerAI Advisor frontend controller
├── requirements.txt
├── run.py                          # Root application runner
└── README.md
```

---

## 📦 Requirements & Dependencies

The project dependencies are listed in `requirements.txt`:
```text
Flask==3.1.3
scikit-learn==1.9.1
pandas==3.1.1
numpy==2.5.4
joblib==1.4.2
pypdf==7.0.1
PyPDF2==3.0.1
python-docx==1.2.0
Werkzeug==3.1.9
Jinja2==3.1.6
```

---

## 🚀 Installation & Local Execution

### 1. Prerequisites
- Python 3.9 or higher.

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```

### 4. Open in Your Browser
- **Primary Local URL**: [https://ai-career-guidance-system-fm0s.onrender.com/](https://ai-career-guidance-system-fm0s.onrender.com/)
- **Localhost URL**: [https://ai-career-guidance-system-fm0s.onrender.com/](https://ai-career-guidance-system-fm0s.onrender.com/)

---

## 🧪 Comprehensive Testing Report

The testing evaluation suite (`backend/utils/test_evaluator.py`) verifies all 14 project subsystems and all 5 mandatory user test scenarios:

### Subsystem Verification (100% Pass)
1. **Student profile submission**: Validated with SQLite persistence into `students`, `student_skills`, and `student_interests`.
2. **Manual skill selection**: Verified multi-select tag badges and individual proficiency pickers (Beginner, Intermediate, Advanced).
3. **Resume upload & extraction**: Verified PDF (`pypdf`/`PyPDF2`) and DOCX (`python-docx`) parsing.
4. **Skill identification from resumes**: Extracted skills and mapped to taxonomy catalog.
5. **Rule-Based AI recommendations**: Deductive IF-ELSE logic evaluated with transparent rule explanation chains.
6. **Decision Tree classification**: Scikit-Learn `DecisionTreeClassifier` (85.64% test accuracy, 85.29% macro F1).
7. **Top 3 career matching**: Correctly isolates and ranks candidate top 3 matches across 15 tech roles.
8. **Match percentage calculations**: Verified dynamic weighted formula (40% skills + 25% interests + 25% ML + 10% rules).
9. **Skill-gap identification**: Categorized into Known (Green), Partially Matched (Orange), and Missing (Red) with priorities.
10. **Personalized roadmap generation**: Generated 4-month milestone curricula with weekly availability alignment.
11. **Free learning resource links**: Curated official documentation and YouTube playlist URLs verified.
12. **Roadmap progress tracking**: Persistent SQLite task toggling with real-time percentage recalculation.
13. **SQLite database storage**: Verified all 9 tables exist, with 15 seeded career roles and 182 skill requirements.
14. **Frontend and backend integration**: Verified seamless REST API communication, clean button alignments, and CareerAI Advisor chatbot.

### Mandatory User Test Cases Evaluation Results
| Test Case | Inputs | Expected Role | System Result | Status |
|---|---|---|---|---|
| **Test Case 1** | Python, SQL, Excel, Statistics | Data Analyst | **Data Analyst** (88.0%), Data Scientist (51.6%), DBA (49.2%) | **PASSED** |
| **Test Case 2** | HTML, CSS, JavaScript, React | Frontend Developer | **Frontend Developer** (88.7%), UI/UX Developer (62.0%), Full Stack (59.1%) | **PASSED** |
| **Test Case 3** | Python, Math, ML, Deep Learning | AI/ML Roles | **AI Engineer** (98.5%), Data Scientist (72.2%), ML Engineer (60.1%) | **PASSED** |
| **Test Case 4** | Java, OOP, DBMS, Data Structures | Software Developer | **Java Developer** (96.4%), Software Engineer (65.8%), DBA (62.4%) | **PASSED** |
| **Test Case 5** | Limited skills, high interest | Foundational Paths | **Frontend Developer** (39.5%), ML Engineer (19.5%), Backend Developer (19.5%) with beginner milestones | **PASSED** |

### Execution Command for Evaluation Suite
```bash
.\.venv\Scripts\python.exe backend/utils/test_evaluator.py
```

---

## ⚠️ Known Limitations
1. **Resume OCR for Scanned Images**: The current parser extracts structured text from standard PDF and DOCX files. Scanned bitmap/image resumes (without embedded text layers) require an OCR pre-processor such as Tesseract.
2. **Local Decision Tree Feature Dimensions**: The Decision Tree is trained on 975 synthetic academic-to-industry profiles across 15 classes. When thousands of real student records are accumulated, retraining via `generate_training_data.py` will further refine edge-case accuracy.
3. **External Resource Availability**: YouTube playlists and documentation links point to official free sources; offline environments will access all local roadmaps and project briefs, but external video links require an active internet connection.
