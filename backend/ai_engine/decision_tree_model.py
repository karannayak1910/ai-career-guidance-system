"""
Decision Tree Classification Module for Career Guidance using Scikit-Learn.
Trains, evaluates (accuracy, precision, recall, F1, confusion matrix), serializes (joblib),
and predicts career categories with confidence scores.
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from typing import Dict, Any, List, Tuple

TRAINING_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "training_data.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "decision_tree_model.joblib")

SKILL_FEATURE_COLUMNS = [
    "python", "java", "cpp", "html_css", "javascript", "sql", 
    "statistics", "mathematics", "machine_learning", "networking", 
    "aws_cloud", "database_general", "react", "nodejs", "docker", 
    "kubernetes", "linux", "deep_learning", "data_structures", 
    "powerbi_tableau", "excel", "ui_ux_design", "spring_boot", 
    "fastapi_django", "cybersecurity"
]

INTEREST_FEATURE_COLUMNS = [
    "interest_ai", "interest_ml", "interest_web", "interest_data", 
    "interest_cyber", "interest_cloud", "interest_software", "interest_uiux"
]

BRANCH_MAPPING = {
    "computer science": 1,
    "information technology": 2,
    "data science": 3,
    "artificial intelligence": 4,
    "electronics & communication": 5,
    "electrical engineering": 5,
    "mechanical engineering": 6,
    "civil engineering": 6,
    "other": 6
}

class CareerDecisionTreeModel:
    def __init__(self, data_path: str = TRAINING_DATA_PATH):
        self.data_path = data_path
        self.model: DecisionTreeClassifier = None
        self.classes_: List[str] = []
        self.feature_columns: List[str] = SKILL_FEATURE_COLUMNS + INTEREST_FEATURE_COLUMNS + ["branch_code", "semester"]
        self.metrics_: Dict[str, Any] = {}
        self.tree_visualization_: str = ""
        self._is_trained = False
        self.train_or_load()

    def train_or_load(self):
        """Train model, evaluate metrics, and save with joblib."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Training data not found at {self.data_path}")

        df = pd.read_csv(self.data_path)
        X = df[self.feature_columns]
        y = df["career_role"]

        # Stratified train/test split to evaluate without data leakage
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        clf = DecisionTreeClassifier(
            criterion="gini",
            max_depth=11,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42
        )
        clf.fit(X_train, y_train)

        # Evaluate model performance on holdout test set
        y_pred = clf.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        self.model = clf
        self.classes_ = list(clf.classes_)
        self.metrics_ = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "num_classes": len(self.classes_)
        }

        # Generate readable tree structure visualization
        try:
            self.tree_visualization_ = export_text(clf, feature_names=self.feature_columns, max_depth=3)
        except Exception:
            self.tree_visualization_ = "Tree visualization available"

        # Persist model with joblib
        os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
        joblib.dump({"model": clf, "metrics": self.metrics_, "classes": self.classes_}, MODEL_SAVE_PATH)
        self._is_trained = True

        print(f"Decision Tree trained across {len(self.classes_)} classes | Accuracy: {acc*100:.2f}%, F1: {f1*100:.2f}% | Saved to joblib.")

    def extract_features(self, student_dict: Dict[str, Any]) -> pd.DataFrame:
        """Extract vectorized feature row from student input."""
        raw_skills = []
        for k in ["programming_languages", "frameworks", "databases", "tools_technologies", "technical_skills"]:
            val = student_dict.get(k, [])
            if isinstance(val, list):
                raw_skills.extend([s.lower().strip() for s in val])
            elif isinstance(val, str) and val.strip():
                raw_skills.extend([s.lower().strip() for s in val.split(",")])

        skill_set = set(raw_skills)
        features = {}

        features["python"] = 1 if any(s in skill_set for s in ["python", "python3", "py"]) else 0
        features["java"] = 1 if any(s in skill_set for s in ["java", "core java"]) else 0
        features["cpp"] = 1 if any(s in skill_set for s in ["c++", "cpp", "c"]) else 0
        features["html_css"] = 1 if any(s in skill_set for s in ["html", "css", "html5", "css3", "tailwind css", "bootstrap"]) else 0
        features["javascript"] = 1 if any(s in skill_set for s in ["javascript", "js", "typescript", "ts"]) else 0
        features["sql"] = 1 if any(s in skill_set for s in ["sql", "mysql", "postgresql", "postgres", "sqlite"]) else 0
        features["statistics"] = 1 if any(s in skill_set for s in ["statistics", "probability", "statistical analysis"]) else 0
        features["mathematics"] = 1 if any(s in skill_set for s in ["mathematics", "linear algebra", "calculus"]) else 0
        features["machine_learning"] = 1 if any(s in skill_set for s in ["machine learning", "ml", "scikit-learn"]) else 0
        features["networking"] = 1 if any(s in skill_set for s in ["networking", "computer networks", "tcp/ip"]) else 0
        features["aws_cloud"] = 1 if any(s in skill_set for s in ["aws", "cloud computing", "gcp", "azure", "cloud"]) else 0
        features["database_general"] = 1 if any(s in skill_set for s in ["sql", "databases", "mongodb", "postgresql", "mysql", "redis"]) else 0
        features["react"] = 1 if any(s in skill_set for s in ["react", "react.js", "next.js", "nextjs", "vue"]) else 0
        features["nodejs"] = 1 if any(s in skill_set for s in ["node.js", "nodejs", "node", "express"]) else 0
        features["docker"] = 1 if any(s in skill_set for s in ["docker", "containers"]) else 0
        features["kubernetes"] = 1 if any(s in skill_set for s in ["kubernetes", "k8s"]) else 0
        features["linux"] = 1 if any(s in skill_set for s in ["linux", "ubuntu", "bash", "shell"]) else 0
        features["deep_learning"] = 1 if any(s in skill_set for s in ["deep learning", "tensorflow", "pytorch", "neural networks"]) else 0
        features["data_structures"] = 1 if any(s in skill_set for s in ["data structures", "dsa", "algorithms", "oop"]) else 0
        features["powerbi_tableau"] = 1 if any(s in skill_set for s in ["power bi", "powerbi", "tableau", "data visualization"]) else 0
        features["excel"] = 1 if any(s in skill_set for s in ["excel", "ms excel", "spreadsheets"]) else 0
        features["ui_ux_design"] = 1 if any(s in skill_set for s in ["ui/ux design", "ui/ux", "figma", "responsive design"]) else 0
        features["spring_boot"] = 1 if any(s in skill_set for s in ["spring boot", "springboot", "spring", "hibernate"]) else 0
        features["fastapi_django"] = 1 if any(s in skill_set for s in ["django", "flask", "fastapi"]) else 0
        features["cybersecurity"] = 1 if any(s in skill_set for s in ["cybersecurity", "ethical hacking", "infosec", "cryptography"]) else 0

        # Interests mapping (1-5)
        interests = [str(x).lower().strip() for x in student_dict.get("interest_areas", [])]
        features["interest_ai"] = 5 if any("artificial intelligence" in i or "ai" in i for i in interests) else 2
        features["interest_ml"] = 5 if any("machine learning" in i or "ml" in i for i in interests) else 2
        features["interest_web"] = 5 if any("web" in i for i in interests) else 2
        features["interest_data"] = 5 if any("data" in i for i in interests) else 2
        features["interest_cyber"] = 5 if any("cyber" in i or "security" in i for i in interests) else 2
        features["interest_cloud"] = 5 if any("cloud" in i for i in interests) else 2
        features["interest_software"] = 5 if any("software" in i for i in interests) else 2
        features["interest_uiux"] = 5 if any("ui/ux" in i or "ui" in i or "ux" in i for i in interests) else 2

        # Branch & Semester
        branch_str = str(student_dict.get("branch", "")).lower().strip()
        features["branch_code"] = BRANCH_MAPPING.get(branch_str, 1)
        features["semester"] = int(student_dict.get("current_semester", 6))

        return pd.DataFrame([features])[self.feature_columns]

    def predict(self, student_dict: Dict[str, Any]) -> Tuple[str, float]:
        """Predict the single most probable career role and confidence."""
        probs = self.predict_probabilities(student_dict)
        if not probs:
            return "software_engineer", 0.5
        top_role = max(probs.items(), key=lambda x: x[1])
        return top_role[0], round(top_role[1] * 100, 1)

    def predict_probabilities(self, student_dict: Dict[str, Any]) -> Dict[str, float]:
        """Return dictionary of all 15 roles to predicted probability score."""
        if not self._is_trained:
            self.train_or_load()

        X = self.extract_features(student_dict)
        probas = self.model.predict_proba(X)[0]
        
        result = {}
        for role_name, prob in zip(self.classes_, probas):
            result[role_name] = float(prob)
        return result

    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Return model evaluation metrics dictionary."""
        return self.metrics_

# Singleton instance
_model_instance = None

def get_decision_tree_model() -> CareerDecisionTreeModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = CareerDecisionTreeModel()
    return _model_instance
