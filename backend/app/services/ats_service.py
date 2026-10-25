import re
from typing import Dict, Any, List, Optional
from backend.app.services.skill_extractor import SKILLS, TAXONOMY

ROLE_REQUIREMENTS = TAXONOMY["role_requirements"]

# Comprehensive Industry Job Profiles Database for CV Match & Recommendations
INDUSTRY_JOB_POSTINGS = [
    {
        "role_id": "junior_web_dev",
        "title": "Junior Web Developer",
        "category": "Frontend / Web",
        "road_key": "frontend",
        "required_skills": ["HTML/CSS", "JavaScript", "Git"],
        "bonus_skills": ["Tailwind CSS", "React"],
        "avg_salary_lpa": "4.5 - 6.8",
        "description": "Build responsive client-facing web interfaces, convert Figma designs to semantic HTML/CSS, and maintain cross-browser compatibility.",
        "experience_level": "Entry Level (0-2 yrs)"
    },
    {
        "role_id": "frontend_dev",
        "title": "Frontend Engineer (React / UI)",
        "category": "Frontend",
        "road_key": "frontend",
        "required_skills": ["JavaScript", "React", "TypeScript", "HTML/CSS", "Git"],
        "bonus_skills": ["Next.js", "Redux", "Tailwind CSS"],
        "avg_salary_lpa": "6.5 - 11.5",
        "description": "Develop scalable single-page web applications using modern React, state management, and type-safe TypeScript codebases.",
        "experience_level": "Associate (1-3 yrs)"
    },
    {
        "role_id": "senior_frontend_dev",
        "title": "Senior Frontend & Architecture Specialist",
        "category": "Frontend",
        "road_key": "frontend",
        "required_skills": ["React", "Next.js", "TypeScript", "Testing", "Git"],
        "bonus_skills": ["Tailwind CSS", "System Design", "CI/CD"],
        "avg_salary_lpa": "12.0 - 20.0",
        "description": "Lead frontend component systems, implement SSR and App Router performance tuning, and champion UI testing coverage.",
        "experience_level": "Senior (3-6 yrs)"
    },
    {
        "role_id": "backend_dev",
        "title": "Backend API Developer (Node / Express)",
        "category": "Backend",
        "road_key": "backend",
        "required_skills": ["Node.js", "Express.js", "REST APIs", "SQL", "Git"],
        "bonus_skills": ["PostgreSQL", "MongoDB", "Docker", "Python"],
        "avg_salary_lpa": "7.0 - 12.0",
        "description": "Architect high-throughput RESTful microservices, optimize database queries, and secure authentication flows.",
        "experience_level": "Associate (1-3 yrs)"
    },
    {
        "role_id": "backend_systems_engineer",
        "title": "Distributed Systems & Backend Engineer",
        "category": "Backend",
        "road_key": "backend",
        "required_skills": ["Node.js", "PostgreSQL", "System Design", "Docker", "REST APIs"],
        "bonus_skills": ["Redis", "Kubernetes", "Linux", "SQL"],
        "avg_salary_lpa": "11.0 - 19.5",
        "description": "Engineer fault-tolerant distributed services, optimize SQL transaction bottlenecks, and design caching layers.",
        "experience_level": "Mid / Senior (2-5 yrs)"
    },
    {
        "role_id": "fullstack_dev",
        "title": "Full-Stack Web Developer",
        "category": "Fullstack",
        "road_key": "fullstack",
        "required_skills": ["JavaScript", "React", "Node.js", "SQL", "Git", "REST APIs"],
        "bonus_skills": ["TypeScript", "Docker", "PostgreSQL", "Next.js"],
        "avg_salary_lpa": "8.0 - 14.5",
        "description": "Own end-to-end feature delivery from responsive frontend interfaces down to backend databases and cloud deployment.",
        "experience_level": "Associate / Mid (2-4 yrs)"
    },
    {
        "role_id": "data_analyst",
        "title": "Junior Data Analyst & Python Dev",
        "category": "Data",
        "road_key": "data",
        "required_skills": ["Python", "SQL", "Pandas", "Git"],
        "bonus_skills": ["Machine Learning", "Statistics", "NumPy", "Data Visualization"],
        "avg_salary_lpa": "6.0 - 10.0",
        "description": "Extract insights from relational data, build automated Python ETL pipelines, and visualize key business metrics.",
        "experience_level": "Entry / Associate (0-2 yrs)"
    },
    {
        "role_id": "data_scientist_ml",
        "title": "Applied Machine Learning & Data Scientist",
        "category": "Data",
        "road_key": "data",
        "required_skills": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy"],
        "bonus_skills": ["Deep Learning", "SQL", "Git"],
        "avg_salary_lpa": "9.5 - 18.0",
        "description": "Train predictive models, run feature engineering, evaluate ML algorithms, and deploy models into production services.",
        "experience_level": "Mid-Level (2-5 yrs)"
    },
    {
        "role_id": "devops_cloud_engineer",
        "title": "Cloud & DevOps Junior Engineer",
        "category": "DevOps",
        "road_key": "devops",
        "required_skills": ["Docker", "Linux", "Git", "CI/CD"],
        "bonus_skills": ["Kubernetes", "AWS", "Terraform", "Python"],
        "avg_salary_lpa": "7.5 - 13.0",
        "description": "Maintain containerized deployments, automate CI/CD release pipelines, and monitor cloud infrastructure health.",
        "experience_level": "Associate (1-3 yrs)"
    },
    {
        "role_id": "sre_cloud_architect",
        "title": "Site Reliability Engineer & Cloud Architect",
        "category": "DevOps",
        "road_key": "devops",
        "required_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "Linux"],
        "bonus_skills": ["CI/CD", "System Design", "Python"],
        "avg_salary_lpa": "13.0 - 22.0",
        "description": "Architect multi-cloud high-availability systems, enforce zero-downtime infrastructure as code, and optimize cloud spend.",
        "experience_level": "Mid / Senior (3-6 yrs)"
    },
    {
        "role_id": "mobile_app_dev",
        "title": "Mobile Application Developer (Cross-Platform)",
        "category": "Mobile",
        "road_key": "mobile",
        "required_skills": ["JavaScript", "React Native", "Git"],
        "bonus_skills": ["TypeScript", "Android SDK", "Flutter"],
        "avg_salary_lpa": "6.5 - 12.5",
        "description": "Develop and deploy cross-platform iOS and Android applications with native performance, offline caching, and responsive UI.",
        "experience_level": "Associate (1-3 yrs)"
    },
    {
        "role_id": "flutter_native_engineer",
        "title": "Flutter & Mobile Systems Engineer",
        "category": "Mobile",
        "road_key": "mobile",
        "required_skills": ["Flutter", "Git", "REST APIs"],
        "bonus_skills": ["Android SDK", "Swift", "Kotlin"],
        "avg_salary_lpa": "7.0 - 13.5",
        "description": "Build high-speed mobile interfaces with Dart and Flutter, integrate with backend REST APIs, and publish to app stores.",
        "experience_level": "Associate (1-3 yrs)"
    },
    {
        "role_id": "qa_automation_dev",
        "title": "QA Automation & Test Engineer",
        "category": "Testing / QA",
        "road_key": "frontend",
        "required_skills": ["JavaScript", "Testing", "Git"],
        "bonus_skills": ["CI/CD", "Docker", "HTML/CSS"],
        "avg_salary_lpa": "5.0 - 8.5",
        "description": "Implement automated end-to-end test suites, run regression testing, and ensure code release reliability.",
        "experience_level": "Entry / Associate (0-2 yrs)"
    }
]

class ATSService:
    """
    Evaluates ATS compatibility, calculates role-specific skill confidence,
    and generates AI-matched job post recommendations dynamically prioritized
    by the candidate's selected career road and Digital Twin skills.
    """

    def evaluate_cv(
        self,
        resume_text: str,
        detected_skills: Dict[str, float],
        target_role: str,
        verified_certs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        text = resume_text or ""
        lower_text = text.lower()
        word_count = len(re.findall(r'\b\w+\b', text))
        target_role_key = (target_role or "frontend").lower().strip()

        # 1. ATS Structure & Formatting Checks
        has_summary = bool(re.search(r'\b(summary|objective|profile|about)\b', lower_text))
        has_skills_section = bool(re.search(r'\b(skills|technical skills|technologies|proficiencies|competencies)\b', lower_text))
        has_projects = bool(re.search(r'\b(projects|academic projects|experience|work history|portfolio)\b', lower_text))
        has_education = bool(re.search(r'\b(education|b\.tech|degree|university|college|bachelor|master)\b', lower_text))
        has_contact_meta = bool(re.search(r'(@|github|linkedin|phone|\+91|[0-9]{10})', lower_text))

        # Action verbs check
        action_verbs = ["built", "developed", "implemented", "designed", "created", "engineered", "optimized", "managed", "deployed", "integrated", "tested"]
        action_verb_count = sum(1 for v in action_verbs if re.search(rf"\b{v}\b", lower_text))

        format_score = 35.0
        if has_summary: format_score += 15.0
        if has_skills_section: format_score += 20.0
        if has_projects: format_score += 20.0
        if has_education: format_score += 15.0
        format_score = min(100.0, format_score)

        action_score = min(100.0, max(35.0, action_verb_count * 18.0))
        
        # Skill Density Score (0 - 100)
        skills_detected_count = len(detected_skills)
        skill_density_score = min(100.0, max(40.0, skills_detected_count * 12.0 + (10.0 if word_count > 40 else 0.0)))

        # Certificate boost if verified credentials attached
        cert_count = len(verified_certs or [])
        cert_boost = min(18, cert_count * 6)

        # Overall ATS Friendly CV Score
        raw_ats = int(round(format_score * 0.35 + skill_density_score * 0.40 + action_score * 0.25))
        ats_score = min(98, max(50, raw_ats + cert_boost))

        ats_rating = (
            "Highly ATS Optimized & Certified" if (ats_score >= 85 and cert_count > 0)
            else "Highly ATS Optimized" if ats_score >= 80 
            else "ATS Compatible (Good)" if ats_score >= 65 
            else "Needs ATS Formatting & Keywords"
        )

        # 2. Target Role Skill Coverage & Confidence
        role_data = ROLE_REQUIREMENTS.get(target_role_key, ROLE_REQUIREMENTS.get("frontend", {}))
        
        if isinstance(role_data, dict):
            req_items = role_data.get("requirements", [])
            role_label = role_data.get("label", f"{target_role_key.capitalize()} Developer")
        else:
            req_items = role_data
            role_label = f"{target_role_key.capitalize()} Developer"

        role_reqs = []
        for item in req_items:
            if isinstance(item, (list, tuple)):
                role_reqs.append({"skill": item[0], "weight": item[1]})
            elif isinstance(item, dict):
                role_reqs.append({"skill": item.get("skill"), "weight": item.get("weight", 2)})
            else:
                role_reqs.append({"skill": str(item), "weight": 2})

        total_req_count = len(role_reqs)
        matched_role_skills = []
        missing_role_skills = []
        for req in role_reqs:
            req_skill = req["skill"]
            if req_skill in detected_skills:
                matched_role_skills.append({
                    "skill": req_skill,
                    "confidence": detected_skills[req_skill],
                    "weight": req["weight"]
                })
            else:
                missing_role_skills.append({
                    "skill": req_skill,
                    "weight": req["weight"]
                })

        direct_coverage_pct = round((len(matched_role_skills) / max(total_req_count, 1)) * 100, 1)

        coverage_summary = (
            f"You possess {len(matched_role_skills)} out of {total_req_count} essential skills "
            f"({direct_coverage_pct}% direct match) for {role_label} on your selected roadmap."
        )

        # 3. Dynamic Job Recommendations Prioritized by Selected Career Road
        recommended_jobs = []
        for job in INDUSTRY_JOB_POSTINGS:
            req_skills = job["required_skills"]
            req_matched = [s for s in req_skills if s in detected_skills]
            bonus_matched = [s for s in job.get("bonus_skills", []) if s in detected_skills]

            req_pct = (len(req_matched) / max(len(req_skills), 1)) * 100.0
            bonus_pct = (len(bonus_matched) / max(len(job.get("bonus_skills", [1])), 1)) * 20.0
            
            total_match = min(98, int(round(req_pct * 0.85 + bonus_pct)))
            missing_skills = [s for s in req_skills if s not in detected_skills]

            # Check if this job is on the user's SELECTED ROAD
            is_selected_road = (job.get("road_key") == target_role_key or target_role_key in job["role_id"])

            is_high_fit = total_match >= 65
            is_medium_fit = total_match >= 40

            if is_selected_road:
                badge_text = f"🎯 Selected Road Priority ({total_match}% Fit)" if is_high_fit else f"🎯 Target Road ({total_match}% Fit)"
                badge_color = "var(--accent)"
            else:
                badge_text = "Adjacent Path Match" if is_high_fit else "Career Growth Opportunity"
                badge_color = "var(--blue)" if is_high_fit else "var(--text-dim)"

            recommended_jobs.append({
                "role_id": job["role_id"],
                "title": job["title"],
                "category": job["category"],
                "match_percentage": total_match,
                "badge_text": badge_text,
                "badge_color": badge_color,
                "is_selected_road": is_selected_road,
                "matched_skills": req_matched + bonus_matched,
                "missing_skills": missing_skills,
                "avg_salary_lpa": job["avg_salary_lpa"],
                "experience_level": job["experience_level"],
                "description": job["description"]
            })

        # Sort jobs: First by selected road match (so selected roadmap jobs come first!), then by match percentage
        recommended_jobs.sort(key=lambda x: (x["is_selected_road"], x["match_percentage"]), reverse=True)

        return {
            "ats_score": ats_score,
            "ats_rating": ats_rating,
            "ats_breakdown": {
                "format_score": int(format_score),
                "skill_density_score": int(skill_density_score),
                "action_verbs_score": int(action_score),
                "has_contact_meta": has_contact_meta,
                "has_projects": has_projects,
                "has_education": has_education
            },
            "role_coverage": {
                "target_role": target_role,
                "total_required": total_req_count,
                "matched_count": len(matched_role_skills),
                "direct_coverage_pct": direct_coverage_pct,
                "matched_skills": matched_role_skills,
                "missing_skills": missing_role_skills,
                "summary": coverage_summary
            },
            "verified_credentials": verified_certs or [],
            "certificate_boost": cert_boost,
            "recommended_job_posts": recommended_jobs
        }

ats_service = ATSService()
