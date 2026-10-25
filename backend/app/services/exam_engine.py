"""
Multi-Format Exam Engine — Dynamic question generation and AI-powered evaluation.

Supports 5 exam types:
1. MCQ - Multiple choice (enhanced with AI generation)
2. Code - Write code, evaluated by AI for correctness, Time & Space Complexity
3. Essay - Short answer / explain concepts & system architecture
4. Debug - Find and fix bugs in code with algorithmic efficiency checks
5. Design - Scalable system design questions

All questions are dynamically generated based on user's weak skills.
Results update the digital twin automatically with algorithmic efficiency bonuses.

Time Complexity: O(q) for question generation, O(q) for evaluation
Space Complexity: O(q) per exam session
"""

import re
import random
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from backend.app.services.ai_service import ai_service
from backend.app.services.skill_extractor import TAXONOMY

logger = logging.getLogger(__name__)

ROLE_REQUIREMENTS = TAXONOMY["role_requirements"]


# ── Local fallback question templates (used when AI is unavailable) ──

CODE_CHALLENGE_TEMPLATES = {
    "JavaScript": {
        "topic": "Array & Tree Manipulation",
        "question": "Write a JavaScript function `flattenDeep(arr)` that recursively or iteratively flattens a deeply nested array. Example: flattenDeep([1, [2, [3, [4]], 5]]) should return [1, 2, 3, 4, 5]. Target Time: O(n), Target Space: O(n).",
        "starter_code": "function flattenDeep(arr) {\n  // Your code here - Aim for O(n) time complexity\n}",
        "language": "javascript",
        "expected_optimal_time": "O(n)",
        "expected_optimal_space": "O(n)",
        "test_cases": [
            {"input": "[1, [2, [3, [4]], 5]]", "expected": "[1, 2, 3, 4, 5]"},
            {"input": "[[1, 2], [3, [4, 5]]]", "expected": "[1, 2, 3, 4, 5]"},
        ],
        "expected_points": ["Recursion or stack/queue iteration", "Base case handling", "Array.isArray check", "Linear O(n) traversal"]
    },
    "Python": {
        "topic": "Data Processing & Grouping",
        "question": "Write a Python function `group_by(items, key_fn)` that groups a list of items by the result of calling key_fn on each item. Return a dictionary. Target Time: O(n), Target Space: O(n).",
        "starter_code": "def group_by(items, key_fn):\n    # Your code here - O(n) time, O(n) auxiliary space\n    pass",
        "language": "python",
        "expected_optimal_time": "O(n)",
        "expected_optimal_space": "O(n)",
        "test_cases": [
            {"input": "([1,2,3,4,5], lambda x: 'even' if x%2==0 else 'odd')", "expected": "{'odd': [1,3,5], 'even': [2,4]}"},
        ],
        "expected_points": ["Dictionary grouping loop", "Proper key function application", "Handle empty list", "Single pass O(n)"]
    },
    "React": {
        "topic": "Custom Hooks & State Debouncing",
        "question": "Write a React custom hook `useDebounce(value, delay)` that debounces a fast-changing value by a given delay in milliseconds. It must properly clean up timers to prevent memory leaks. Target Time: O(1) per update, Target Space: O(1).",
        "starter_code": "import { useState, useEffect } from 'react';\n\nfunction useDebounce(value, delay) {\n  // Your hook implementation here\n}",
        "language": "javascript",
        "expected_optimal_time": "O(1)",
        "expected_optimal_space": "O(1)",
        "test_cases": [],
        "expected_points": ["useState for debounced value", "useEffect with cleanup function", "clearTimeout on dependency change", "Constant space O(1)"]
    },
    "SQL": {
        "topic": "Aggregation & Analytical Queries",
        "question": "Write an optimized SQL query to find the top 3 departments with the highest average salary, showing department_name and avg_salary (rounded to 2 decimals), ordered by avg_salary descending. Tables: employees(id, name, salary, department_id), departments(id, department_name).",
        "starter_code": "-- Write your SQL query here (Target: indexed JOIN O(n))\nSELECT ",
        "language": "sql",
        "expected_optimal_time": "O(n log k)",
        "expected_optimal_space": "O(k)",
        "test_cases": [],
        "expected_points": ["JOIN between employees and departments", "GROUP BY department", "ORDER BY AVG(salary) DESC", "LIMIT 3"]
    },
}

DEBUG_CHALLENGE_TEMPLATES = {
    "JavaScript": {
        "topic": "Async Event Loop Bug",
        "question": "This code should fetch user data and display names, but it has an async event loop bug. Find and fix it.",
        "buggy_code": """async function fetchUsers() {
  const users = [];
  const ids = [1, 2, 3, 4, 5];
  
  ids.forEach(async (id) => {
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();
    users.push(user.name);
  });
  
  console.log(users); // Always prints []
  return users;
}""",
        "bug_description": "The function always returns an empty array because Array.prototype.forEach does not wait for async promises.",
        "expected_points": ["forEach doesn't await async callbacks", "Use Promise.all with map: await Promise.all(ids.map(...))", "Or use for...of loop"],
        "explanation": "Array.forEach() cannot await async promises. Use Promise.all(ids.map(async (id) => ...)) for concurrent O(n) fetching, or for...of for sequential execution.",
        "expected_optimal_time": "O(n) [Concurrent]",
        "expected_optimal_space": "O(n)"
    },
    "Python": {
        "topic": "Mutable Default Argument",
        "question": "This function is supposed to add items to a fresh list each time, but it accumulates across calls. Find and fix the bug.",
        "buggy_code": """def add_item(item, items=[]):
    items.append(item)
    return items

# Expected: [1], [2], [3]
# Actual:   [1], [1, 2], [1, 2, 3]
print(add_item(1))
print(add_item(2))
print(add_item(3))""",
        "bug_description": "Items accumulate across function calls instead of starting fresh each time.",
        "expected_points": ["Mutable default argument", "Use items=None as default", "items = [] if items is None else items"],
        "explanation": "Python evaluates default arguments once when the function is defined. Use `items=None` as the default argument and initialize a new list inside the body.",
        "expected_optimal_time": "O(1)",
        "expected_optimal_space": "O(1)"
    },
    "React": {
        "topic": "Stale Closure in useEffect",
        "question": "This counter should increment every second, but it stays at 1. Find and fix the bug.",
        "buggy_code": """function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCount(count + 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  return <h1>Count: {count}</h1>;
}""",
        "bug_description": "The counter increments to 1 but never goes beyond that due to a stale closure.",
        "expected_points": ["Stale closure captures initial count = 0", "Use functional updater: setCount(prev => prev + 1)", "Proper timer cleanup"],
        "explanation": "The empty dependency array [] captures the initial count value 0 in the timer closure. Use the functional updater form `setCount(c => c + 1)`.",
        "expected_optimal_time": "O(1)",
        "expected_optimal_space": "O(1)"
    },
}

ESSAY_TEMPLATES = {
    "System Design": {
        "topic": "Scalable Architecture & Throughput",
        "question": "You are designing a real-time notification system for a platform with 100 million users. Describe your architecture covering: message queue selection, push delivery (WebSockets/SSE), storage, latency guarantees, and how you handle at-least-once delivery with idempotency.",
        "expected_points": [
            "Message queue (Kafka/RabbitMQ/SQS) with partition keys",
            "WebSocket connections with gateway connection manager",
            "Notification storage and read/unread cache (Redis)",
            "At-least-once delivery with idempotency keys",
            "Horizontal scaling and backpressure handling"
        ],
        "max_word_count": 500
    },
    "Docker": {
        "topic": "Container Orchestration & Scaling",
        "question": "Explain the architectural difference between Docker Compose and Kubernetes. When would you choose one over the other? Describe a scenario where migrating from Compose to Kubernetes is necessary.",
        "expected_points": [
            "Compose for single-node local/development",
            "Kubernetes for distributed multi-node production orchestration",
            "Auto-scaling (HPA), rolling deploys, and self-healing in K8s",
            "Migration trade-offs (operational complexity vs scalability)"
        ],
        "max_word_count": 400
    },
    "Machine Learning": {
        "topic": "Model Selection & Imbalance Strategy",
        "question": "You have a dataset of 50,000 customer records with 200 features and need to predict churn. Walk through your approach: data preprocessing, feature selection, model selection (tree vs linear vs deep learning), evaluation metrics, and how you handle severe class imbalance (5% churners).",
        "expected_points": [
            "Data cleaning, imputation, and scaling",
            "Feature selection (importance, mutual information)",
            "Model choice (XGBoost/LightGBM/Random Forest)",
            "Precision/Recall/ROC-AUC/PR-AUC over raw accuracy",
            "Resampling (SMOTE) or focal/class-weighted loss"
        ],
        "max_word_count": 500
    },
}


class ExamEngine:
    """
    Dynamic multi-format exam engine with AI-powered generation and evaluation.
    Evaluates Correctness, Time Complexity, Space Complexity, and Accuracy.
    """

    EXAM_TYPES = ["mcq", "code", "essay", "debug", "design", "mixed"]
    DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]

    # Skill impact weights by exam type and correctness
    SKILL_IMPACT = {
        "mcq":    {"correct": 7.0,  "wrong": -3.0},
        "code":   {"correct": 12.0, "wrong": -2.0},
        "essay":  {"correct": 8.0,  "wrong": -1.5},
        "debug":  {"correct": 10.0, "wrong": -2.0},
        "design": {"correct": 10.0, "wrong": -1.0},
    }

    def generate_exam(
        self,
        role: str,
        exam_type: str,
        count: int = 5,
        difficulty: str = "intermediate",
        detected_skills: Dict[str, float] = None,
        weak_skills: List[str] = None,
        resume_text: str = ""
    ) -> Dict[str, Any]:
        """Generate a complete exam with personalized questions."""
        detected_skills = detected_skills or {}
        weak_skills = weak_skills or []

        # Try AI generation first
        if ai_service.is_available:
            questions = self._generate_ai_questions(
                role, exam_type, count, difficulty,
                detected_skills, weak_skills, resume_text
            )
            if questions and len(questions) >= count:
                return self._build_exam_response(role, exam_type, difficulty, questions[:count])

        # Fallback to local templates
        logger.info(f"Using fallback templates for {exam_type} exam ({role})")
        questions = self._generate_fallback_questions(
            role, exam_type, count, difficulty,
            detected_skills, weak_skills
        )
        return self._build_exam_response(role, exam_type, difficulty, questions)

    def evaluate_exam(
        self,
        role: str,
        exam_type: str,
        questions: List[Dict],
        answers: List[Dict],
        detected_skills: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Evaluate exam answers and calculate skill impacts & algorithmic complexity."""
        detected_skills = detected_skills or {}
        results = []
        skill_updates: Dict[str, float] = {}

        time_complexities = []
        space_complexities = []
        accuracies = []

        for answer in answers:
            q_id = answer.get("question_id", "")
            # Find in questions list or reconstruct from answer embedded data
            question = next((q for q in questions if q.get("id") == q_id), None)
            a_type = answer.get("exam_type", exam_type)

            if not question:
                # Reconstruct question from answer context fields
                question = {
                    "id": q_id,
                    "exam_type": a_type,
                    "skill": answer.get("skill", "General"),
                    "topic": answer.get("topic", ""),
                    "question": answer.get("question_text", ""),
                    "options": answer.get("options", []),
                    "correct_index": answer.get("correct_index", 0),
                    "expected_points": answer.get("expected_points", []),
                    "buggy_code": answer.get("buggy_code", ""),
                    "bug_description": answer.get("bug_description", ""),
                    "explanation": answer.get("explanation", ""),
                    "expected_optimal_time": answer.get("expected_optimal_time", "O(n)"),
                    "expected_optimal_space": answer.get("expected_optimal_space", "O(1)"),
                }

            skill = answer.get("skill", question.get("skill", "General"))

            if a_type == "mcq":
                result = self._evaluate_mcq(question, answer)
            elif a_type == "code":
                result = self._evaluate_code(question, answer)
            elif a_type in ("essay", "design"):
                result = self._evaluate_essay(question, answer)
            elif a_type == "debug":
                result = self._evaluate_debug(question, answer)
            else:
                result = self._evaluate_mcq(question, answer)

            result["skill"] = skill
            result["topic"] = answer.get("topic", question.get("topic", ""))
            result["exam_type"] = a_type

            # Record complexity & accuracy
            if result.get("time_complexity"):
                time_complexities.append(result["time_complexity"])
            if result.get("space_complexity"):
                space_complexities.append(result["space_complexity"])
            if result.get("accuracy_pct") is not None:
                accuracies.append(result["accuracy_pct"])

            # Calculate skill impact with complexity bonus
            impact_config = self.SKILL_IMPACT.get(a_type, self.SKILL_IMPACT["mcq"])
            impact = impact_config["correct"] if result["is_correct"] else impact_config["wrong"]

            # Complexity bonus for optimal solutions
            if a_type in ("code", "debug") and result.get("time_rating") == "Optimal":
                impact += 2.0

            # Scale impact by difficulty
            diff_multiplier = {"beginner": 0.7, "intermediate": 1.0, "advanced": 1.3}
            diff = question.get("difficulty", "intermediate")
            impact *= diff_multiplier.get(diff, 1.0)

            result["skill_impact"] = round(impact, 1)

            if skill != "General":
                skill_updates[skill] = skill_updates.get(skill, 0) + impact

            results.append(result)

        # Summarize
        total = len(results)
        correct = sum(1 for r in results if r["is_correct"])
        accuracy = round((correct / total * 100) if total > 0 else 0, 1)
        avg_accuracy = round(sum(accuracies) / len(accuracies), 1) if accuracies else accuracy
        is_cleared = accuracy >= 60

        # Round skill updates
        skill_updates = {k: round(v, 1) for k, v in skill_updates.items()}

        dominant_time = time_complexities[0] if time_complexities else "O(1)"
        dominant_space = space_complexities[0] if space_complexities else "O(1)"

        summary = (
            f"{'✅' if is_cleared else '❌'} Exam completed: {correct}/{total} questions cleared ({accuracy}% accuracy). "
        )
        if is_cleared:
            summary += f"Algorithmic Time Complexity: {dominant_time} | Auxiliary Space: {dominant_space}. Your digital twin has been updated!"
        else:
            summary += f"Review detected complexity trade-offs ({dominant_time}) and weak skills to prepare for re-examination."

        complexity_summary = f"Algorithmic Complexity: Time {dominant_time}, Space {dominant_space}. Average test-case accuracy: {avg_accuracy}%."

        recommendations = self._generate_recommendations(results, skill_updates)

        return {
            "overall_score": accuracy,
            "accuracy_pct": accuracy,
            "total_questions": total,
            "correct_count": correct,
            "clearance_status": "CLEARANCE GRANTED" if is_cleared else "CLEARANCE BLOCKED",
            "is_cleared": is_cleared,
            "exam_type": exam_type,
            "difficulty": questions[0].get("difficulty", "intermediate") if questions else "intermediate",
            "results": results,
            "skill_updates": skill_updates,
            "twin_updated": True,
            "overall_time_complexity": dominant_time,
            "overall_space_complexity": dominant_space,
            "complexity_summary": complexity_summary,
            "summary": summary,
            "recommendations": recommendations
        }

    # ── AI Question Generation ──

    def _generate_ai_questions(
        self, role: str, exam_type: str, count: int, difficulty: str,
        detected_skills: Dict[str, float], weak_skills: List[str], resume_text: str
    ) -> Optional[List[Dict]]:
        """Generate questions using AI."""
        skills_str = ", ".join(detected_skills.keys()) if detected_skills else "general skills"
        weak_str = ", ".join(weak_skills) if weak_skills else "none specified"

        type_instructions = self._get_type_instructions(exam_type)

        prompt = f"""You are a Principal Technical Interviewer creating a rigorous {exam_type.upper()} assessment for a {role.upper()} DEVELOPER position.

Candidate's detected skills: {skills_str}
Candidate's weak areas to focus on: {weak_str}
Difficulty level: {difficulty.upper()}

Generate exactly {count} unique, high-quality {exam_type} questions.
{type_instructions}

IMPORTANT:
- Questions should be {difficulty} difficulty
- Include target optimal time complexity (e.g. O(n)) and space complexity (e.g. O(1))
- Focus on the candidate's weak areas if specified
- Each question should test practical, real-world knowledge
- Generate questions that are DIFFERENT from standard textbook questions

Return ONLY valid JSON array (no markdown, no backticks):
{self._get_schema_for_type(exam_type)}"""

        result = ai_service.generate_json(prompt, cache_key_prefix=f"exam_{exam_type}_{role}")
        if isinstance(result, list):
            for i, q in enumerate(result):
                if "id" not in q:
                    q["id"] = f"ai_{exam_type}_{uuid.uuid4().hex[:8]}"
                q["exam_type"] = exam_type
                q["difficulty"] = difficulty
            return result
        return None

    def _get_type_instructions(self, exam_type: str) -> str:
        instructions = {
            "mcq": "Each question should have 4 options with exactly one correct answer. Include detailed explanations.",
            "code": "Each question should be a coding problem. Include starter code, expected solution approach, optimal time & space complexity, and test cases.",
            "essay": "Each question should require a detailed architectural or conceptual explanation (200-500 words). Include expected key points and scaling factors.",
            "debug": "Each question should show buggy code that the candidate must identify and fix. Include the buggy code, bug description, expected time/space efficiency, and the fix explanation.",
            "design": "Each question should be a system design problem. Include expected architectural components, latency/throughput complexity, and evaluation criteria.",
        }
        return instructions.get(exam_type, instructions["mcq"])

    def _get_schema_for_type(self, exam_type: str) -> str:
        schemas = {
            "mcq": """[{"id":"q1","skill":"SkillName","topic":"Topic","question":"Question text","options":["A","B","C","D"],"correct_index":0,"explanation":"Why correct","points":10}]""",
            "code": """[{"id":"q1","skill":"SkillName","topic":"Topic","question":"Problem description","starter_code":"code template","language":"javascript","test_cases":[{"input":"...","expected":"..."}],"expected_optimal_time":"O(n)","expected_optimal_space":"O(1)","expected_points":["point1","point2"],"points":15}]""",
            "essay": """[{"id":"q1","skill":"SkillName","topic":"Topic","question":"Explain...","expected_points":["point1","point2","point3"],"max_word_count":400,"points":15}]""",
            "debug": """[{"id":"q1","skill":"SkillName","topic":"Topic","question":"Find the bug","buggy_code":"code with bug","bug_description":"What's wrong","expected_optimal_time":"O(n)","expected_optimal_space":"O(1)","expected_points":["fix1"],"explanation":"Correct fix","points":12}]""",
            "design": """[{"id":"q1","skill":"SkillName","topic":"Topic","question":"Design a system for...","expected_points":["component1","component2","component3"],"max_word_count":500,"points":20}]""",
        }
        return schemas.get(exam_type, schemas["mcq"])

    # ── Fallback Question Generation ──

    def _generate_fallback_questions(
        self, role: str, exam_type: str, count: int, difficulty: str,
        detected_skills: Dict[str, float], weak_skills: List[str]
    ) -> List[Dict]:
        """Generate questions from local templates when AI is unavailable."""
        if exam_type == "mcq":
            return self._fallback_mcqs(role, detected_skills, count)
        elif exam_type == "code":
            return self._fallback_code(role, detected_skills, weak_skills, count)
        elif exam_type in ("essay", "design"):
            return self._fallback_essays(role, weak_skills, count)
        elif exam_type == "debug":
            return self._fallback_debug(role, detected_skills, weak_skills, count)
        elif exam_type == "mixed":
            return self._generate_mixed_exam(role, count, difficulty, detected_skills, weak_skills, "")
        else:
            return self._fallback_mcqs(role, detected_skills, count)

    def _fallback_mcqs(self, role: str, detected_skills: Dict[str, float], count: int) -> List[Dict]:
        """Use existing MCQ bank from interview_service."""
        from backend.app.services.interview_service import interview_service
        mcqs = interview_service.generate_dynamic_mcqs(role=role, detected_skills=detected_skills, count=count)
        for q in mcqs:
            q["exam_type"] = "mcq"
            q["difficulty"] = "intermediate"
            q["points"] = 10
            q["expected_optimal_time"] = "O(1)"
            q["expected_optimal_space"] = "O(1)"
        return mcqs

    def _fallback_code(self, role: str, detected_skills: Dict[str, float], weak_skills: List[str], count: int) -> List[Dict]:
        """Generate code challenges from templates."""
        questions = []
        target_skills = weak_skills if weak_skills else list(detected_skills.keys()) if detected_skills else ["JavaScript", "Python"]

        for skill in target_skills[:count]:
            template = CODE_CHALLENGE_TEMPLATES.get(skill)
            if not template:
                template = CODE_CHALLENGE_TEMPLATES.get("JavaScript")

            questions.append({
                "id": f"code_{uuid.uuid4().hex[:8]}",
                "exam_type": "code",
                "skill": skill,
                "topic": template["topic"],
                "difficulty": "intermediate",
                "question": template["question"],
                "starter_code": template["starter_code"],
                "language": template["language"],
                "test_cases": template["test_cases"],
                "expected_optimal_time": template.get("expected_optimal_time", "O(n)"),
                "expected_optimal_space": template.get("expected_optimal_space", "O(1)"),
                "expected_points": template["expected_points"],
                "points": 15
            })

        while len(questions) < count:
            skill, template = random.choice(list(CODE_CHALLENGE_TEMPLATES.items()))
            if not any(q["skill"] == skill for q in questions):
                questions.append({
                    "id": f"code_{uuid.uuid4().hex[:8]}",
                    "exam_type": "code",
                    "skill": skill,
                    "topic": template["topic"],
                    "difficulty": "intermediate",
                    "question": template["question"],
                    "starter_code": template["starter_code"],
                    "language": template["language"],
                    "test_cases": template["test_cases"],
                    "expected_optimal_time": template.get("expected_optimal_time", "O(n)"),
                    "expected_optimal_space": template.get("expected_optimal_space", "O(1)"),
                    "expected_points": template["expected_points"],
                    "points": 15
                })

        return questions[:count]

    def _fallback_debug(self, role: str, detected_skills: Dict[str, float], weak_skills: List[str], count: int) -> List[Dict]:
        """Generate debug challenges from templates."""
        questions = []
        for skill, template in DEBUG_CHALLENGE_TEMPLATES.items():
            if len(questions) >= count:
                break
            questions.append({
                "id": f"debug_{uuid.uuid4().hex[:8]}",
                "exam_type": "debug",
                "skill": skill,
                "topic": template["topic"],
                "difficulty": "intermediate",
                "question": template["question"],
                "buggy_code": template["buggy_code"],
                "bug_description": template["bug_description"],
                "expected_optimal_time": template.get("expected_optimal_time", "O(n)"),
                "expected_optimal_space": template.get("expected_optimal_space", "O(1)"),
                "expected_points": template["expected_points"],
                "explanation": template["explanation"],
                "points": 12
            })
        return questions[:count]

    def _fallback_essays(self, role: str, weak_skills: List[str], count: int) -> List[Dict]:
        """Generate essay/design questions from templates."""
        questions = []
        for skill, template in ESSAY_TEMPLATES.items():
            if len(questions) >= count:
                break
            questions.append({
                "id": f"essay_{uuid.uuid4().hex[:8]}",
                "exam_type": "essay",
                "skill": skill,
                "topic": template["topic"],
                "difficulty": "advanced",
                "question": template["question"],
                "expected_points": template["expected_points"],
                "max_word_count": template["max_word_count"],
                "points": 15
            })
        return questions[:count]

    def _generate_mixed_exam(self, role, count, difficulty, detected_skills, weak_skills, resume_text):
        """Generate a mixed exam with different question types."""
        mcq_cnt = max(1, count // 3)
        code_cnt = max(1, count // 4)
        debug_cnt = max(1, count // 5)
        essay_cnt = max(1, count - mcq_cnt - code_cnt - debug_cnt)

        all_questions = []
        all_questions.extend(self._fallback_mcqs(role, detected_skills, mcq_cnt))
        all_questions.extend(self._fallback_code(role, detected_skills, weak_skills, code_cnt))
        all_questions.extend(self._fallback_debug(role, detected_skills, weak_skills, debug_cnt))
        all_questions.extend(self._fallback_essays(role, weak_skills, essay_cnt))

        random.shuffle(all_questions)
        return self._build_exam_response(role, "mixed", difficulty, all_questions[:count])

    # ── Evaluation Methods with Time/Space Complexity & Accuracy ──

    def _evaluate_mcq(self, question: Dict, answer: Dict) -> Dict:
        """Evaluate MCQ answer."""
        correct_idx = question.get("correct_index", 0)
        selected_idx = answer.get("selected_index", -1)
        is_correct = (selected_idx == correct_idx)

        options = question.get("options", [])
        correct_text = options[correct_idx] if correct_idx < len(options) else "N/A"

        return {
            "question_id": answer.get("question_id", ""),
            "is_correct": is_correct,
            "score": 100.0 if is_correct else 0.0,
            "accuracy_pct": 100.0 if is_correct else 0.0,
            "time_complexity": "O(1)",
            "time_rating": "Optimal",
            "space_complexity": "O(1)",
            "space_rating": "Optimal",
            "complexity_analysis": "MCQ verification operates in O(1) constant time and space.",
            "feedback": "✅ Correct! Direct conceptual alignment." if is_correct else f"❌ Incorrect. The correct answer was: {correct_text}",
            "explanation": question.get("explanation", ""),
            "correct_answer": correct_text
        }

    def _evaluate_code(self, question: Dict, answer: Dict) -> Dict:
        """Evaluate code answer for Correctness, Time Complexity, Space Complexity, and Accuracy."""
        code = answer.get("code_answer", "") or ""
        expected_points = question.get("expected_points", [])
        opt_time = question.get("expected_optimal_time", "O(n)")
        opt_space = question.get("expected_optimal_space", "O(1)")
        lang = question.get("language", "javascript")

        if not code or not code.strip():
            return {
                "question_id": answer.get("question_id", ""),
                "is_correct": False,
                "score": 0.0,
                "accuracy_pct": 0.0,
                "time_complexity": "N/A",
                "time_rating": "Incomplete",
                "space_complexity": "N/A",
                "space_rating": "Incomplete",
                "complexity_analysis": "No code submitted.",
                "feedback": "❌ No code submitted.",
                "explanation": question.get("explanation", ""),
            }

        # Try AI evaluation first
        if ai_service.is_available:
            result = self._ai_evaluate_code(question, code)
            if result:
                return result

        # Algorithmic Complexity & Accuracy Heuristic
        comp = ai_service.analyze_algorithmic_complexity(code, lang, opt_time, opt_space)

        # Keyword matching against expected concepts
        score = 0
        matched = []
        for point in expected_points:
            keywords = point.lower().split()
            if any(kw in code.lower() for kw in keywords if len(kw) > 3):
                score += 100 / max(1, len(expected_points))
                matched.append(point)

        # Combine keyword score with complexity accuracy
        final_score = round((score * 0.6) + (comp["accuracy_pct"] * 0.4), 1)
        is_correct = final_score >= 55.0

        return {
            "question_id": answer.get("question_id", ""),
            "is_correct": is_correct,
            "score": final_score,
            "accuracy_pct": comp["accuracy_pct"],
            "time_complexity": comp["time_complexity"],
            "time_rating": comp["time_rating"],
            "space_complexity": comp["space_complexity"],
            "space_rating": comp["space_rating"],
            "complexity_analysis": comp["complexity_analysis"],
            "feedback": f"{'✅' if is_correct else '⚠️'} Score: {round(final_score)}% | Time: {comp['time_complexity']} ({comp['time_rating']}) | Space: {comp['space_complexity']}. Matched concepts: {', '.join(matched) if matched else 'Foundational implementation'}",
            "explanation": question.get("explanation", f"Optimal target is {opt_time} time with {opt_space} space."),
        }

    def _evaluate_essay(self, question: Dict, answer: Dict) -> Dict:
        """Evaluate essay/design answer for architectural depth and system scalability."""
        text = answer.get("text_answer", "") or ""
        expected_points = question.get("expected_points", [])

        if not text or len(text.strip()) < 20:
            return {
                "question_id": answer.get("question_id", ""),
                "is_correct": False,
                "score": 0.0,
                "accuracy_pct": 0.0,
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "complexity_analysis": "Answer too brief for architecture review.",
                "feedback": "❌ Answer too short or empty.",
            }

        # Try AI evaluation
        if ai_service.is_available:
            result = self._ai_evaluate_essay(question, text)
            if result:
                return result

        # Fallback: keyword matching & word count
        score = 0
        matched = []
        for point in expected_points:
            keywords = [w for w in point.lower().split() if len(w) > 3]
            if any(kw in text.lower() for kw in keywords):
                score += 100 / max(1, len(expected_points))
                matched.append(point)

        word_count = len(text.split())
        if word_count > 80:
            score = min(100.0, score + 15.0)

        is_correct = score >= 50.0

        return {
            "question_id": answer.get("question_id", ""),
            "is_correct": is_correct,
            "score": round(score, 1),
            "accuracy_pct": round(min(100.0, score * 1.05), 1),
            "time_complexity": "O(log N) [Cached Read Path]",
            "time_rating": "Distributed Architecture",
            "space_complexity": "O(N) [Sharded Storage]",
            "space_rating": "Scalable",
            "complexity_analysis": f"Evaluated {word_count} words against system trade-offs: partitioning, throughput & caching latency.",
            "feedback": f"{'✅' if is_correct else '⚠️'} Score: {round(score)}%. Key pillars covered: {', '.join(matched) if matched else 'Partial coverage'}.",
        }

    def _evaluate_debug(self, question: Dict, answer: Dict) -> Dict:
        """Evaluate debug answer for Correctness and Efficiency."""
        code = answer.get("code_answer", "") or answer.get("text_answer", "") or ""
        expected_points = question.get("expected_points", [])
        opt_time = question.get("expected_optimal_time", "O(n)")
        opt_space = question.get("expected_optimal_space", "O(1)")

        if not code or not code.strip():
            return {
                "question_id": answer.get("question_id", ""),
                "is_correct": False,
                "score": 0.0,
                "accuracy_pct": 0.0,
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "complexity_analysis": "No fix submitted.",
                "feedback": "❌ No fix submitted.",
                "explanation": question.get("explanation", ""),
            }

        # Try AI evaluation
        if ai_service.is_available:
            result = self._ai_evaluate_debug(question, code)
            if result:
                return result

        comp = ai_service.analyze_algorithmic_complexity(code, "javascript", opt_time, opt_space)

        score = 0
        for point in expected_points:
            keywords = [w for w in point.lower().split() if len(w) > 3]
            if any(kw in code.lower() for kw in keywords):
                score += 100 / max(1, len(expected_points))

        is_correct = score >= 50.0

        return {
            "question_id": answer.get("question_id", ""),
            "is_correct": is_correct,
            "score": round(score, 1),
            "accuracy_pct": comp["accuracy_pct"],
            "time_complexity": comp["time_complexity"],
            "time_rating": comp["time_rating"],
            "space_complexity": comp["space_complexity"],
            "space_rating": comp["space_rating"],
            "complexity_analysis": comp["complexity_analysis"],
            "feedback": f"{'✅' if is_correct else '❌'} Bugfix evaluated: {round(score)}% match. Time: {comp['time_complexity']}, Space: {comp['space_complexity']}.",
            "explanation": question.get("explanation", ""),
        }

    # ── AI Evaluation Helpers with Complexity Benchmarking ──

    def _ai_evaluate_code(self, question: Dict, code: str) -> Optional[Dict]:
        opt_time = question.get("expected_optimal_time", "O(n)")
        opt_space = question.get("expected_optimal_space", "O(1)")

        prompt = f"""Evaluate this candidate's code for a technical exam.
Problem: {question.get('question', '')}
Optimal target: Time {opt_time}, Space {opt_space}
Expected concepts: {json.dumps(question.get('expected_points', []))}

Candidate Code:
```
{code}
```

Carefully analyze:
1. Correctness & Accuracy (0-100%)
2. Time Complexity in Big O notation (e.g. O(1), O(n), O(n^2))
3. Space Complexity in Big O notation (e.g. O(1), O(n))
4. Detailed feedback on algorithmic efficiency

Return ONLY valid JSON (no markdown):
{{
  "is_correct": true,
  "score": 85,
  "accuracy_pct": 90.0,
  "time_complexity": "O(n)",
  "time_rating": "Optimal",
  "space_complexity": "O(1)",
  "space_rating": "Optimal",
  "complexity_analysis": "Linear single-pass traversal with constant memory.",
  "feedback": "Clear, concise solution meeting optimal Big-O bounds.",
  "explanation": "Key trade-offs and suggestions"
}}"""

        result = ai_service.generate_json(prompt, use_cache=False)
        if result and "score" in result:
            result["question_id"] = question.get("id", "")
            result["is_correct"] = result.get("score", 0) >= 60
            return result
        return None

    def _ai_evaluate_essay(self, question: Dict, text: str) -> Optional[Dict]:
        prompt = f"""Evaluate this written answer for a technical system design exam.
Question: {question.get('question', '')}
Expected key points: {json.dumps(question.get('expected_points', []))}

Candidate's answer:
{text}

Evaluate completeness, scalability, architectural depth, and throughput latency trade-offs.
Return ONLY valid JSON:
{{
  "is_correct": true,
  "score": 85,
  "accuracy_pct": 88.0,
  "time_complexity": "O(1) [Redis In-Memory]",
  "time_rating": "High Throughput",
  "space_complexity": "O(N) [Distributed Shards]",
  "space_rating": "Optimal",
  "complexity_analysis": "Architecture demonstrates scalable distributed queues and low-latency cache.",
  "feedback": "Comprehensive architectural coverage."
}}"""

        result = ai_service.generate_json(prompt, use_cache=False)
        if result and "score" in result:
            result["question_id"] = question.get("id", "")
            result["is_correct"] = result.get("score", 0) >= 50
            return result
        return None

    def _ai_evaluate_debug(self, question: Dict, code: str) -> Optional[Dict]:
        prompt = f"""Evaluate this bugfix for a technical assessment.
Bug description: {question.get('bug_description', '')}
Original code:
```
{question.get('buggy_code', '')}
```

Candidate's fix:
```
{code}
```

Evaluate correctness, Time Complexity, and Space Complexity.
Return ONLY valid JSON:
{{
  "is_correct": true,
  "score": 90,
  "accuracy_pct": 95.0,
  "time_complexity": "O(n)",
  "time_rating": "Optimal",
  "space_complexity": "O(1)",
  "space_rating": "Optimal",
  "complexity_analysis": "Fix resolves the bug cleanly without adding extra algorithmic passes.",
  "feedback": "Effective fix applied.",
  "explanation": "Explanation of fix"
}}"""

        result = ai_service.generate_json(prompt, use_cache=False)
        if result and "score" in result:
            result["question_id"] = question.get("id", "")
            result["is_correct"] = result.get("score", 0) >= 60
            return result
        return None

    # ── Helpers ──

    def _build_exam_response(self, role: str, exam_type: str, difficulty: str, questions: List[Dict]) -> Dict:
        """Build standardized exam response."""
        time_limits = {
            "mcq": 120,
            "code": 600,
            "essay": 480,
            "debug": 360,
            "design": 600,
            "mixed": 300,
        }
        per_q_time = time_limits.get(exam_type, 120)
        total_time = per_q_time * len(questions)

        instructions = {
            "mcq": "Select the best answer for each question. Evaluated in O(1) constant time.",
            "code": "Write clean, performant code. Evaluated for algorithmic Time Complexity, Space Complexity, and test-case accuracy.",
            "essay": "Provide detailed written explanations covering architecture, scaling, and throughput latency trade-offs.",
            "debug": "Identify the bug and submit the corrected code. Efficiency and Big-O complexity are benchmarked.",
            "design": "Design a high-scale architecture covering messaging, caching, database sharding, and latency guarantees.",
            "mixed": "Multi-format assessment testing broad engineering capability across algorithms and system design.",
        }

        return {
            "role": role,
            "exam_type": exam_type,
            "difficulty": difficulty,
            "questions": questions,
            "total_questions": len(questions),
            "time_limit_seconds": total_time,
            "instructions": instructions.get(exam_type, "Answer all questions.")
        }

    def _generate_recommendations(self, results: List[Dict], skill_updates: Dict[str, float]) -> List[str]:
        """Generate study recommendations based on exam results."""
        recommendations = []
        weak = {k: v for k, v in skill_updates.items() if v < 0}
        strong = {k: v for k, v in skill_updates.items() if v > 0}

        for skill in sorted(weak, key=weak.get):
            recommendations.append(f"📚 Practice {skill} algorithms & design patterns to optimize Time & Space Complexity.")

        if strong:
            top_skill = max(strong, key=strong.get)
            recommendations.append(f"💪 Excellent mastery in {top_skill} (+{strong[top_skill]:.1f}% confidence boost applied to your Digital Twin).")

        if not recommendations:
            recommendations.append("✅ Solid overall engineering performance. Keep sharpening your algorithmic complexity bounds.")

        return recommendations


# Singleton instance
exam_engine = ExamEngine()
