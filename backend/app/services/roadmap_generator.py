import os
import json
from typing import List, Dict, Any, Optional

RES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "datasets", "learning_resources.json"
)

def load_resources() -> Dict[str, Any]:
    with open(RES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

RESOURCE_DATA = load_resources()

STAGE_DEFINITIONS = [
    {
        "stage": 1,
        "level": "Level 1: Novice",
        "title": "Core Foundations & Tooling",
        "icon": "🛡️",
        "description": "Foundational programming languages, syntax mechanics, and developer workflow tools."
    },
    {
        "stage": 2,
        "level": "Level 2: Adept",
        "title": "Frameworks & Component Architecture",
        "icon": "⚡",
        "description": "Modern application frameworks, component hierarchies, and interactive logic."
    },
    {
        "stage": 3,
        "level": "Level 3: Specialist",
        "title": "Systems, Data Stores & Microservices",
        "icon": "🚀",
        "description": "Database management, persistent state storage, and scalable distributed APIs."
    },
    {
        "stage": 4,
        "level": "Level 4: Master",
        "title": "Production Engineering, Cloud & Capstone",
        "icon": "👑",
        "description": "Containerization, automated CI/CD pipelines, system architecture & capstone validation."
    }
]

class RoadmapGeneratorService:
    """
    Game-like Chained Stage Roadmap generation service.
    Guarantees ONLY 100% FREE courses (YouTube, freeCodeCamp, Harvard CS50, MDN, Kaggle, etc.).
    Stages are sequentially linked like levels in an adventure game.
    """

    def __init__(self):
        self.resources = RESOURCE_DATA["resources"]
        self.cluster_fallbacks = RESOURCE_DATA["cluster_fallbacks"]

    def generate_roadmap(
        self,
        gap_rows: List[Dict[str, Any]],
        experience_years: float = 0.5,
        target_role: str = "frontend",
        detected_skills: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a game-like chained staged roadmap with free YouTube and platform courses.
        """
        detected_skills = detected_skills or {}
        pace_multiplier = 0.85 if experience_years >= 2.0 else 1.1

        # We will collect courses for each skill mentioned in gap_rows
        courses_by_stage: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: []}
        
        # Sort gaps: open gaps first, then already possessed
        sorted_gaps = sorted(gap_rows, key=lambda x: (x.get("match_pct", 0), -x.get("weight", 1)))

        seen_skills = set()
        for gap in sorted_gaps:
            skill = gap.get("skill", "General")
            if skill in seen_skills:
                continue
            seen_skills.add(skill)

            match_pct = gap.get("match_pct", 30.0)
            res = self.resources.get(skill)

            if not res:
                cluster = gap.get("cluster", target_role.lower())
                fallback = self.cluster_fallbacks.get(cluster, self.cluster_fallbacks.get("general", {}))
                res = {
                    "platform": fallback.get("platform", "YouTube · freeCodeCamp"),
                    "platform_type": "youtube",
                    "title": fallback.get("title", f"Mastering {skill} (Free Curriculum)"),
                    "hrs": fallback.get("hrs", 6),
                    "level": "Intermediate" if match_pct > 40 else "Beginner",
                    "url": fallback.get("url", "https://www.youtube.com/watch?v=PkZNo7MFNFg"),
                    "is_free": True,
                    "cost": "100% Free",
                    "stage": fallback.get("stage", 2)
                }

            stage_num = res.get("stage", 2)
            if stage_num not in courses_by_stage:
                stage_num = 2

            base_hrs = int(round(res.get("hrs", 6) * pace_multiplier))
            is_completed = match_pct >= 75.0 or (skill in detected_skills and detected_skills[skill] >= 75.0)

            difficulty = res.get("level", "Intermediate")
            platform = res.get("platform", "YouTube · freeCodeCamp")
            platform_type = "youtube" if "YouTube" in platform else "platform"

            course_item = {
                "id": f"course_{skill.lower().replace('/', '_').replace('.', '_').replace(' ', '_')}",
                "skill": skill,
                "action": f"Master {skill} Core Patterns & Build Practical Feature",
                "resource_title": res.get("title"),
                "resource_platform": platform,
                "platform_type": platform_type,
                "resource_url": res.get("url", "https://www.youtube.com"),
                "estimated_hours": max(2, base_hrs),
                "current_match_pct": round(match_pct, 1),
                "is_free": True,
                "cost": "100% Free",
                "difficulty": difficulty,
                "stage": stage_num,
                "stage_title": STAGE_DEFINITIONS[stage_num - 1]["title"],
                "stage_level": STAGE_DEFINITIONS[stage_num - 1]["level"],
                "stage_icon": STAGE_DEFINITIONS[stage_num - 1]["icon"],
                "completed": is_completed,
                "learning_outcomes": [
                    f"Solve practical engineering challenges with {skill}",
                    f"Build hands-on code project and verify in Exam Center",
                    f"Boost Digital Twin alignment for {target_role.capitalize()} role"
                ]
            }
            courses_by_stage[stage_num].append(course_item)

        # Build chained stage list
        roadmap_stages = []
        is_previous_stage_completed = True

        for stage_def in STAGE_DEFINITIONS:
            s_num = stage_def["stage"]
            courses = courses_by_stage.get(s_num, [])
            
            # If a stage has no courses directly from gaps, inject general relevant courses
            if not courses:
                fallback_res = self.cluster_fallbacks.get(target_role.lower(), self.cluster_fallbacks["general"])
                courses = [{
                    "id": f"course_stage_{s_num}_default",
                    "skill": f"{target_role.capitalize()} Engineering Part {s_num}",
                    "action": f"Progress through {stage_def['title']}",
                    "resource_title": fallback_res.get("title", f"Hands-on {stage_def['title']}"),
                    "resource_platform": fallback_res.get("platform", "YouTube · freeCodeCamp"),
                    "platform_type": "youtube",
                    "resource_url": fallback_res.get("url", "https://www.youtube.com"),
                    "estimated_hours": 6,
                    "current_match_pct": 50.0,
                    "is_free": True,
                    "cost": "100% Free",
                    "difficulty": "Intermediate",
                    "stage": s_num,
                    "stage_title": stage_def["title"],
                    "stage_level": stage_def["level"],
                    "stage_icon": stage_def["icon"],
                    "completed": False,
                    "learning_outcomes": [
                        "Complete free video tutorials and exercises",
                        "Demonstrate hands-on knowledge in the digital twin"
                    ]
                }]

            total_count = len(courses)
            completed_count = sum(1 for c in courses if c.get("completed"))
            stage_pct = round((completed_count / max(total_count, 1)) * 100)

            # Determine lock status (game-like unlocking)
            if s_num == 1:
                status = "completed" if completed_count == total_count else "in_progress"
            else:
                if is_previous_stage_completed:
                    status = "completed" if completed_count == total_count else "in_progress"
                else:
                    status = "locked"

            stage_obj = {
                "stage": s_num,
                "level": stage_def["level"],
                "title": stage_def["title"],
                "icon": stage_def["icon"],
                "description": stage_def["description"],
                "status": status,
                "total_courses": total_count,
                "completed_courses": completed_count,
                "completion_pct": stage_pct,
                "courses": courses
            }
            roadmap_stages.append(stage_obj)

            # Stage is considered "completed" if >= 80% done
            is_previous_stage_completed = (stage_pct >= 80)

        return roadmap_stages

roadmap_generator = RoadmapGeneratorService()
