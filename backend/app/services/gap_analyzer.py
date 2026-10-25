import os
import json
from typing import Dict, Any, List, Optional
from backend.app.services.skill_extractor import TAXONOMY

SKILLS = TAXONOMY["skills"]
ADJACENT = TAXONOMY["adjacent_clusters"]
ROLE_REQUIREMENTS = TAXONOMY["role_requirements"]

# Directed Prerequisite & Transferability Knowledge Map
# format: target_skill -> list of (prerequisite_or_transferable_skill, match_percentage, kind)
SKILL_RELATIONSHIPS = {
    # Frontend
    "React": [
        ("JavaScript", 35.0, "prerequisite foundation (JS -> React)"),
        ("Vue.js", 40.0, "transferable component framework"),
        ("Angular", 35.0, "transferable component framework"),
        ("HTML/CSS", 15.0, "markup foundation")
    ],
    "TypeScript": [
        ("JavaScript", 40.0, "prerequisite foundation (JS -> TS)"),
        ("Java", 25.0, "transferable typed language"),
        ("C++", 20.0, "transferable typed language")
    ],
    "Next.js": [
        ("React", 50.0, "prerequisite foundation (React -> Next.js)"),
        ("JavaScript", 25.0, "language foundation"),
        ("Node.js", 25.0, "SSR backend foundation")
    ],
    "Tailwind CSS": [
        ("HTML/CSS", 40.0, "prerequisite foundation (CSS -> Tailwind)"),
        ("React", 15.0, "UI integration foundation")
    ],
    "Redux": [
        ("React", 45.0, "prerequisite foundation (React -> Redux)"),
        ("JavaScript", 25.0, "state management logic")
    ],
    "Testing": [
        ("JavaScript", 20.0, "scripting foundation"),
        ("Python", 20.0, "scripting foundation"),
        ("React", 20.0, "component testing foundation")
    ],
    "JavaScript": [
        ("TypeScript", 85.0, "superset knowledge (TS -> JS)"),
        ("HTML/CSS", 20.0, "frontend foundation"),
        ("Python", 25.0, "scripting transferability")
    ],
    "HTML/CSS": [
        ("Tailwind CSS", 75.0, "utility framework knowledge"),
        ("JavaScript", 20.0, "web foundation")
    ],
    
    # Backend
    "Node.js": [
        ("JavaScript", 45.0, "prerequisite runtime language"),
        ("TypeScript", 45.0, "typed runtime language"),
        ("Express.js", 80.0, "framework knowledge"),
        ("Python", 25.0, "backend transferability")
    ],
    "Express.js": [
        ("Node.js", 50.0, "prerequisite runtime (Node.js -> Express)"),
        ("JavaScript", 30.0, "language foundation"),
        ("REST APIs", 35.0, "API design foundation")
    ],
    "REST APIs": [
        ("Express.js", 75.0, "framework API implementation"),
        ("Node.js", 40.0, "backend foundation"),
        ("Django", 75.0, "backend framework implementation"),
        ("Flask", 75.0, "backend framework implementation"),
        ("FastAPI", 80.0, "modern API framework")
    ],
    "PostgreSQL": [
        ("SQL", 65.0, "relational SQL foundation"),
        ("MySQL", 70.0, "transferable relational RDBMS"),
        ("SQLite", 60.0, "relational database foundation"),
        ("MongoDB", 25.0, "database concept transferability")
    ],
    "SQL": [
        ("PostgreSQL", 85.0, "PostgreSQL knowledge -> SQL"),
        ("MySQL", 85.0, "MySQL knowledge -> SQL"),
        ("SQLite", 80.0, "SQLite knowledge -> SQL")
    ],
    "MongoDB": [
        ("PostgreSQL", 30.0, "database concepts"),
        ("SQL", 25.0, "querying foundation"),
        ("Node.js", 20.0, "stack synergy (MERN)")
    ],
    "System Design": [
        ("REST APIs", 30.0, "API architecture foundation"),
        ("Docker", 25.0, "containerization foundation"),
        ("PostgreSQL", 25.0, "database scaling foundation"),
        ("Node.js", 20.0, "backend service experience")
    ],

    # Data Science
    "Machine Learning": [
        ("Python", 35.0, "language foundation"),
        ("Pandas", 40.0, "data processing foundation"),
        ("NumPy", 35.0, "array computation foundation"),
        ("Statistics", 40.0, "mathematical foundation"),
        ("scikit-learn", 80.0, "library knowledge -> ML")
    ],
    "Deep Learning": [
        ("Machine Learning", 50.0, "prerequisite foundation (ML -> DL)"),
        ("TensorFlow", 80.0, "framework knowledge"),
        ("PyTorch", 80.0, "framework knowledge"),
        ("Python", 25.0, "language foundation")
    ],
    "Pandas": [
        ("Python", 40.0, "language foundation"),
        ("SQL", 30.0, "tabular querying foundation")
    ],
    "Statistics": [
        ("Python", 20.0, "computational foundation"),
        ("Machine Learning", 35.0, "applied statistics")
    ],

    # DevOps
    "Docker": [
        ("Linux", 40.0, "OS & container runtime foundation"),
        ("Git", 15.0, "version control foundation")
    ],
    "Kubernetes": [
        ("Docker", 45.0, "container prerequisite (Docker -> K8s)"),
        ("Linux", 25.0, "infrastructure foundation")
    ],
    "AWS": [
        ("Docker", 30.0, "cloud container deployment"),
        ("Linux", 25.0, "cloud server administration"),
        ("Terraform", 40.0, "infrastructure as code")
    ],
    "CI/CD": [
        ("Git", 35.0, "version control automation foundation"),
        ("Docker", 35.0, "containerized pipeline foundation")
    ],
    "Terraform": [
        ("AWS", 35.0, "cloud provider foundation"),
        ("Docker", 20.0, "infrastructure foundation")
    ]
}

class SkillGapAnalyzerService:
    def __init__(self):
        self.skills = SKILLS
        self.adjacent = ADJACENT
        self.roles = ROLE_REQUIREMENTS
        self.relationships = SKILL_RELATIONSHIPS

    def calculate_skill_similarity(self, req_skill: str, candidate_skills: Dict[str, float]) -> Dict[str, Any]:
        # 1. Exact match (Direct hit)
        if req_skill in candidate_skills:
            return {
                "match_pct": 100.0,
                "match_via": req_skill,
                "match_kind": "exact match",
                "badge_status": "strong"
            }

        # 2. Directed prerequisite or framework transferability graph lookup
        best_pct = 0.0
        best_via = None
        best_kind = "no related skill"

        rel_list = self.relationships.get(req_skill, [])
        for rel_skill, pct, kind in rel_list:
            if rel_skill in candidate_skills:
                # Scale by candidate's confidence if available
                cand_conf = candidate_skills[rel_skill] / 100.0
                effective_pct = pct * min(1.0, max(0.6, cand_conf))
                if effective_pct > best_pct:
                    best_pct = effective_pct
                    best_via = rel_skill
                    best_kind = kind

        # 3. Fallback: Check if candidate knows any direct alias
        if best_pct < 20.0:
            req_cluster = self.skills.get(req_skill, "general")
            # If same cluster but no specific prerequisite edge: minimal 10% awareness
            for cand_skill in candidate_skills.keys():
                cand_cluster = self.skills.get(cand_skill, "general")
                if cand_cluster == req_cluster and best_pct < 10.0:
                    best_pct = 10.0
                    best_via = cand_skill
                    best_kind = f"general {req_cluster} domain awareness"

        # Determine badge status based on realistic thresholds
        if best_pct >= 75.0:
            badge = "strong"
        elif best_pct >= 30.0:
            badge = "partial"
        else:
            badge = "gap"

        return {
            "match_pct": round(best_pct, 1),
            "match_via": best_via,
            "match_kind": best_kind,
            "badge_status": badge
        }

    def analyze_gaps(self, role_key: str, candidate_skills: Dict[str, float]) -> Dict[str, Any]:
        norm_role = role_key.lower().strip()
        if norm_role not in self.roles:
            norm_role = "frontend"
            
        role_data = self.roles[norm_role]
        rows = []
        total_weighted_sum = 0.0
        total_weight = 0

        for skill, weight in role_data["requirements"]:
            sim = self.calculate_skill_similarity(skill, candidate_skills)
            total_weighted_sum += (sim["match_pct"] * weight)
            total_weight += weight
            
            rows.append({
                "skill": skill,
                "weight": weight,
                "match_pct": sim["match_pct"],
                "match_via": sim["match_via"],
                "match_kind": sim["match_kind"],
                "badge_status": sim["badge_status"]
            })

        readiness = round(total_weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        return {
            "role_key": norm_role,
            "role_label": role_data["label"],
            "readiness_percentage": readiness,
            "gap_rows": rows
        }

gap_analyzer = SkillGapAnalyzerService()
