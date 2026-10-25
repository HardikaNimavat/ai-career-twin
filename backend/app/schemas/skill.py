from pydantic import BaseModel
from typing import Dict, List, Optional

class SkillTaxonomyItem(BaseModel):
    name: str
    cluster: str
    color: str

class GapAnalysisRequest(BaseModel):
    target_role: str
    candidate_skills: Dict[str, float]

class GapRow(BaseModel):
    skill: str
    weight: int
    match_pct: float
    match_via: Optional[str] = None
    match_kind: str
    badge_status: str
