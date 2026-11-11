"""
Integrated Career Recommendation Engine.
Synthesizes Rule-Based Deductive AI and Scikit-Learn Decision Tree Classifications
into transparent, explainable Top 3 career recommendations across all 15 technology paths.
"""
import os
import json
from typing import Dict, Any, List
from .decision_tree_model import get_decision_tree_model
from .rule_engine import RuleBasedCareerEngine

ROLES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roles.json")

def load_career_roles() -> List[Dict[str, Any]]:
    if os.path.exists(ROLES_PATH):
        try:
            with open(ROLES_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("roles", [])
        except Exception as e:
            print("Error loading roles in matcher:", e)
    return []

class CareerRecommendationEngine:
    def __init__(self):
        self.roles = load_career_roles()
        self.dt_model = get_decision_tree_model()
        self.rule_engine = RuleBasedCareerEngine()

    def _normalize(self, s: str) -> str:
        return s.lower().strip().replace(" ", "").replace("-", "").replace(".", "")

    def recommend(self, student_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrates Rule-Based and Decision Tree inference to produce explainable Top 3 recommendations.
        """
        # 1. Execute Rule-Based AI
        rule_results = self.rule_engine.evaluate(student_dict)
        rule_map = {r["id"]: r for r in rule_results["all_ranked"]}
        top_rule_role = rule_results["top_3"][0]["id"] if rule_results["top_3"] else ""

        # 2. Execute Decision Tree ML Classifier
        ml_probabilities = self.dt_model.predict_probabilities(student_dict)
        top_ml_role, top_ml_conf = self.dt_model.predict(student_dict)
        model_metrics = self.dt_model.get_evaluation_metrics()

        # 3. Detect & Explain Model Disagreement (if any)
        disagreement_explanation = None
        if top_rule_role and top_ml_role and top_rule_role != top_ml_role:
            rule_title = rule_map.get(top_rule_role, {}).get("title", top_rule_role)
            ml_title = rule_map.get(top_ml_role, {}).get("title", top_ml_role)
            disagreement_explanation = (
                f"Model Comparison Note: The Scikit-learn Decision Tree assigned highest probability to '{ml_title}' "
                f"({top_ml_conf}% confidence) based on learned feature split thresholds, whereas the Rule-Based Engine "
                f"ranked '{rule_title}' highest due to strict prerequisite rules and explicit skill proficiencies. "
                f"Both pathways are highlighted below for your strategic review."
            )

        # 4. Compute Documented Blended Score for each of the 15 roles
        ranked_roles = []
        chart_labels = []
        chart_scores = []

        for role in self.roles:
            r_id = role["id"]
            title = role["title"]
            r_data = rule_map.get(r_id, {})

            rule_score = r_data.get("suitability_score", 40.0)
            ml_prob = ml_probabilities.get(r_id, 0.05)
            ml_score = round(ml_prob * 100.0, 1)

            # Skill coverage percentage
            req_skills = role.get("required_skills", [])
            matched_req = r_data.get("matched_required_skills", [])
            skill_cov_pct = (len(matched_req) / max(1, len(req_skills))) * 100.0

            # Interest score
            interests = [str(x).lower().strip() for x in student_dict.get("interest_areas", [])]
            role_interests = [i.lower() for i in role.get("relevant_interests", [])]
            has_interest_match = any(any(ri in i or i in ri for i in interests) for ri in role_interests)
            interest_score = 95.0 if has_interest_match else 50.0

            # Transparent, Documented Weighted Formula:
            # 35% Rule-Based Deduction + 30% Skill Coverage + 20% ML Tree Probability + 15% Interest Alignment
            blended_raw = (
                (0.35 * rule_score) +
                (0.30 * skill_cov_pct) +
                (0.20 * ml_score) +
                (0.15 * interest_score)
            )

            final_match = round(max(15.0, min(98.5, blended_raw)), 1)

            # Why this career matches explanation
            matched_skills = r_data.get("all_matched_skills", [])
            missing_skills = r_data.get("all_missing_skills", [])
            
            why_match = (
                f"Matches your profile through {len(matched_skills)} verified competencies "
                f"including {', '.join(matched_skills[:3]) if matched_skills else 'foundational prerequisites'}. "
                f"{r_data.get('rule_explanations', ['Aligned with current engineering trajectory.'])[0]}"
            )

            # Recommended next steps
            if missing_skills:
                next_steps = f"Focus your learning roadmap on closing high-priority gaps in {', '.join(missing_skills[:3])}."
            else:
                next_steps = f"Build an advanced portfolio capstone demonstrating end-to-end {title} architectures."

            entry = {
                "id": r_id,
                "title": title,
                "domain": role.get("domain", ""),
                "description": role.get("description", ""),
                "average_salary": role.get("average_salary", ""),
                "market_demand": role.get("market_demand", "High"),
                "learning_difficulty": role.get("learning_difficulty", "Intermediate"),
                "match_score": final_match,
                "why_matches": why_match,
                "next_steps": next_steps,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "required_skills": role.get("required_skills", []),
                "preferred_skills": role.get("preferred_skills", []),
                "recommended_projects": role.get("recommended_projects", []),
                "learning_resources": role.get("learning_resources", []),
                "breakdown": {
                    "rule_score": round(rule_score, 1),
                    "skill_coverage": round(skill_cov_pct, 1),
                    "ml_confidence": ml_score,
                    "interest_alignment": interest_score
                },
                "rule_explanations": r_data.get("rule_explanations", [])
            }

            ranked_roles.append(entry)

        # Sort descending by match percentage
        ranked_roles.sort(key=lambda x: x["match_score"], reverse=True)

        for r in ranked_roles:
            chart_labels.append(r["title"])
            chart_scores.append(r["match_score"])

        top_3 = ranked_roles[:3]

        return {
            "student_name": student_dict.get("full_name", "Student"),
            "top_3": top_3,
            "all_ranked_roles": ranked_roles,
            "disagreement_explanation": disagreement_explanation,
            "ml_model_metrics": model_metrics,
            "radar_chart": {
                "labels": chart_labels,
                "data": chart_scores
            }
        }
