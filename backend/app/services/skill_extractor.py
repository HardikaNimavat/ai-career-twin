import os
import re
import json
from typing import Dict, Any, Tuple
from backend.app.services.ai_service import ai_service

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "datasets", "skills_taxonomy.json")

def load_taxonomy() -> Dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

TAXONOMY = load_taxonomy()
SKILLS = TAXONOMY["skills"]
ALIASES = TAXONOMY["aliases"]
CLUSTER_LABELS = TAXONOMY["cluster_labels"]

class SkillExtractorService:
    def __init__(self):
        self.skills = SKILLS
        self.aliases = ALIASES
        self.cluster_labels = CLUSTER_LABELS

    def extract_skills(self, resume_text: str) -> Dict[str, Any]:
        llm_data = ai_service.extract_skills_with_llm(resume_text)
        if llm_data and "detected_skills" in llm_data:
            detected = llm_data["detected_skills"]
            exp_years = float(llm_data.get("experience_years", 1.0))
        else:
            detected, exp_years = self._parse_with_taxonomy(resume_text)

        cluster_tally = {}
        for skill in detected.keys():
            c = self.skills.get(skill, "general")
            cluster_tally[c] = cluster_tally.get(c, 0) + 1

        dom_cluster_key = max(cluster_tally.items(), key=lambda x: x[1])[0] if cluster_tally else "general"
        dom_cluster_label = self.cluster_labels.get(dom_cluster_key, "General")

        # Extract candidate name from top lines of resume
        candidate_name = "Hardika"
        for line in resume_text.splitlines()[:6]:
            l = line.strip()
            if l and len(l) <= 35 and not any(kw in l.lower() for kw in ["resume", "curriculum", "vitae", "summary", "objective", "http", "@", "phone", "contact", "email", "education", "experience", "skills"]):
                cleaned = re.sub(r"[^a-zA-Z\s]", "", l).strip()
                if cleaned and len(cleaned.split()) in [1, 2, 3]:
                    candidate_name = cleaned.title()
                    break

        return {
            "candidate_name": candidate_name,
            "detected_skills": detected,
            "experience_years": exp_years,
            "dominant_cluster": dom_cluster_label,
            "skills_count": len(detected)
        }

    def _parse_with_taxonomy(self, text: str) -> Tuple[Dict[str, float], float]:
        clean_text = " " + text.lower().replace("\n", " ").replace("\r", " ") + " "
        detected = {}
        
        for skill in self.skills.keys():
            variants = self.aliases.get(skill, [skill.lower()])
            hits = 0
            for variant in variants:
                esc = re.escape(variant.lower())
                pattern = rf"(^|[^a-z0-9+#./]){esc}([^a-z0-9+#./]|$)"
                matches = re.findall(pattern, clean_text)
                if matches:
                    hits += len(matches)
            
            if hits > 0:
                confidence = min(98.0, 55.0 + hits * 15.0)
                detected[skill] = round(confidence, 1)

        exp_years = 0.5
        yr_match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(years|yrs|year)', text, re.IGNORECASE)
        if yr_match:
            exp_years = min(15.0, float(yr_match.group(1)))
        elif re.search(r'intern|fresher|student|junior', text, re.IGNORECASE):
            exp_years = 0.5
        elif len(detected) >= 8:
            exp_years = 2.0
        elif len(detected) >= 4:
            exp_years = 1.0

        return detected, exp_years

skill_extractor = SkillExtractorService()
