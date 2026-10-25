import re
import random
import json
import logging
from typing import Dict, Any, List, Optional
from backend.app.services.gemini_service import gemini_service
from backend.app.services.skill_extractor import TAXONOMY

logger = logging.getLogger(__name__)

ROLE_REQUIREMENTS = TAXONOMY["role_requirements"]

# Comprehensive Skill-Categorized Technical Question Bank covering all 50+ taxonomy skills
TECH_MCQ_BANK = {
    # 1. FRONTEND
    "JavaScript": [
        {
            "id": "js_mcq_1",
            "skill": "JavaScript",
            "topic": "Event Loop & Microtasks",
            "question": "In the JavaScript Event Loop, which queue takes highest execution priority after the synchronous call stack empties?",
            "options": [
                "Microtask Queue (Promise callbacks, queueMicrotask)",
                "Macrotask Queue (setTimeout, setInterval)",
                "I/O polling queue",
                "Rendering frame callback queue"
            ],
            "correct_index": 0,
            "explanation": "Microtasks (such as Promise .then() handlers and queueMicrotask) are processed immediately after the current synchronous stack empties, before any Macrotasks (like setTimeout or setInterval) are executed.",
            "deficiency_diagnostic": "Lacking core understanding of JavaScript asynchronous execution, event loop phases, and Microtask vs Macrotask prioritization."
        },
        {
            "id": "js_mcq_2",
            "skill": "JavaScript",
            "topic": "Closures & Scope",
            "question": "What happens when a function references a variable from its outer lexical scope after that outer function has already returned?",
            "options": [
                "A ReferenceError is thrown at runtime",
                "The inner function retains access to the variable via a closure",
                "The variable is garbage-collected and replaced with undefined",
                "The variable becomes a global property on the window object"
            ],
            "correct_index": 1,
            "explanation": "A closure is created whenever an inner function retains a lexical reference to variables in its outer enclosing scope, preventing those variables from being garbage collected even after the outer function finishes executing.",
            "deficiency_diagnostic": "Struggles with JavaScript lexical scoping and closure memory retention mechanisms."
        }
    ],
    "React": [
        {
            "id": "react_mcq_1",
            "skill": "React",
            "topic": "Hooks & Dependency Arrays",
            "question": "In React, why does a useEffect callback sometimes capture stale state variables?",
            "options": [
                "Because React compiles components into WebAssembly at runtime",
                "Because JavaScript closures capture variables from the specific render cycle unless declared in the dependency array",
                "Because useEffect only executes on server workers",
                "Because React state is globally mutable across threads"
            ],
            "correct_index": 1,
            "explanation": "In React, every render has its own props and state closures. Omitting state variables from the useEffect dependency array forces the callback to refer to stale values captured in earlier render closures.",
            "deficiency_diagnostic": "Weakness in React render lifecycle closures, leading to stale state bugs in production React hooks."
        },
        {
            "id": "react_mcq_2",
            "skill": "React",
            "topic": "Performance Optimization",
            "question": "When should you use React.useCallback() instead of an inline function?",
            "options": [
                "On every single function in every component without exception",
                "When passing function references to memoized child components (React.memo) to prevent unnecessary child re-renders",
                "Only when executing synchronous calculations inside render",
                "To make API calls without using promises"
            ],
            "correct_index": 1,
            "explanation": "useCallback returns a memoized function reference that only changes if dependencies change, preventing memoized child components (wrapped in React.memo) from breaking their prop equality checks.",
            "deficiency_diagnostic": "Lacking understanding of React memoization boundaries and reference equality optimization."
        }
    ],
    "HTML/CSS": [
        {
            "id": "css_mcq_1",
            "skill": "HTML/CSS",
            "topic": "CSS Layout Systems",
            "question": "What is the core structural difference between CSS Flexbox and CSS Grid?",
            "options": [
                "Flexbox is designed for 1-dimensional layouts (row OR column), while Grid is designed for 2-dimensional layouts (rows AND columns)",
                "Flexbox only works in Chrome, while Grid works only in Safari",
                "Grid does not support gap or alignment properties",
                "Flexbox requires JavaScript to calculate element dimensions"
            ],
            "correct_index": 0,
            "explanation": "Flexbox is fundamentally a 1D layout model (distributing space along a main axis), whereas CSS Grid is a 2D layout model designed to control rows and columns simultaneously.",
            "deficiency_diagnostic": "Lacks practical distinction between 1D (Flexbox) and 2D (Grid) modern CSS layout architecture."
        }
    ],
    "TypeScript": [
        {
            "id": "ts_mcq_1",
            "skill": "TypeScript",
            "topic": "Type Safety & Any vs Unknown",
            "question": "Why is the 'unknown' type preferred over 'any' for untrusted runtime data in TypeScript?",
            "options": [
                "'unknown' disables all compilation checks permanently",
                "'unknown' is type-safe because it forces developers to perform type narrowing before operating on the value",
                "'unknown' can only hold boolean values",
                "'unknown' runs faster at JavaScript execution time"
            ],
            "correct_index": 1,
            "explanation": "'any' disables type checking completely, while 'unknown' forces explicit type narrowing (using typeof, instanceof, or type guards) before allowing any property access or operations.",
            "deficiency_diagnostic": "Lacks type safety rigor; does not know when to apply TypeScript type narrowing instead of escaping with 'any'."
        }
    ],
    "Next.js": [
        {
            "id": "nextjs_mcq_1",
            "skill": "Next.js",
            "topic": "Rendering Paradigms (SSR vs SSG)",
            "question": "In Next.js App Router, what is the default rendering model for components inside the /app directory?",
            "options": [
                "Client Components with 'use client'",
                "React Server Components (RSC) rendered exclusively on the server",
                "Pure static HTML files with zero JavaScript capability",
                "Web Worker background threads"
            ],
            "correct_index": 1,
            "explanation": "In Next.js App Router, all components are React Server Components (RSC) by default, keeping large dependencies on the server and sending minimal zero-bundle HTML/payloads to the client.",
            "deficiency_diagnostic": "Lacks mastery of Next.js Server Components vs Client Components boundaries in full-stack frontend architecture."
        }
    ],
    "Redux": [
        {
            "id": "redux_mcq_1",
            "skill": "Redux",
            "topic": "State Immutability & Reducers",
            "question": "Why must Redux reducer functions remain strictly pure and immutable?",
            "options": [
                "Because JavaScript engines throw memory leaks if objects are mutated",
                "To allow predictable state transitions, time-travel debugging, and shallow equality checks in UI subscriptions",
                "Because Redux stores state on hard disk drives",
                "Because Redux does not support arrays or objects"
            ],
            "correct_index": 1,
            "explanation": "Pure reducers without side effects ensure that new state objects are created on changes, allowing React-Redux to perform rapid shallow equality comparisons (===) to know when components need to re-render.",
            "deficiency_diagnostic": "Weakness in state immutability principles and predictable state management architecture."
        }
    ],

    # 2. BACKEND & DATABASES
    "Node.js": [
        {
            "id": "node_mcq_1",
            "skill": "Node.js",
            "topic": "Non-blocking I/O & Libuv",
            "question": "How does Node.js handle thousands of concurrent I/O operations despite having a single-threaded JavaScript execution engine?",
            "options": [
                "By spawning a new operating system process for every incoming HTTP request",
                "By delegating asynchronous file and network I/O to the multi-threaded Libuv thread pool and OS kernel epoll/kqueue event demultiplexers",
                "By compiling JavaScript directly into GPU shaders",
                "By running multiple copies of the V8 engine in shared memory"
            ],
            "correct_index": 1,
            "explanation": "Node.js offloads asynchronous I/O tasks to Libuv, which leverages OS-level non-blocking primitives (epoll/kqueue) and a background thread pool, notifying the single main event loop thread via callbacks upon completion.",
            "deficiency_diagnostic": "Lacking understanding of Node.js Libuv architecture, non-blocking I/O, and event-driven concurrency."
        }
    ],
    "Express.js": [
        {
            "id": "express_mcq_1",
            "skill": "Express.js",
            "topic": "Middleware Execution Order",
            "question": "In Express.js, what happens if a middleware function performs asynchronous operations but forgets to call next() or return a response?",
            "options": [
                "Express automatically redirects the client to the homepage",
                "The HTTP request hangs indefinitely until the client or server times out",
                "The server crashes immediately with an UnhandledPromiseRejection",
                "Express skips to the next route handler automatically"
            ],
            "correct_index": 1,
            "explanation": "Express middleware pipeline relies on explicit next() invocation or terminating the response (res.send/res.json). Omitting both leaves the connection open until socket timeout.",
            "deficiency_diagnostic": "Lacking understanding of Express middleware request-response pipelines and error handling."
        }
    ],
    "REST APIs": [
        {
            "id": "rest_mcq_1",
            "skill": "REST APIs",
            "topic": "HTTP Status & Idempotency",
            "question": "Which HTTP methods are defined as idempotent according to the HTTP/1.1 specification?",
            "options": [
                "POST and PATCH",
                "GET, PUT, DELETE, and HEAD",
                "POST and CONNECT",
                "Only GET is idempotent"
            ],
            "correct_index": 1,
            "explanation": "An HTTP method is idempotent if executing it N > 0 times produces the exact same side-effects as executing it once. GET, PUT, DELETE, and HEAD are idempotent.",
            "deficiency_diagnostic": "Misunderstands RESTful HTTP protocol specifications and idempotent API design."
        }
    ],
    "SQL": [
        {
            "id": "sql_mcq_1",
            "skill": "SQL",
            "topic": "Indexing & Query Optimization",
            "question": "How does a B-Tree index accelerate SQL SELECT queries containing WHERE clauses?",
            "options": [
                "By compressing table rows into gzip archives",
                "By enabling O(log N) logarithmic binary search traversals instead of O(N) full table scans",
                "By storing all database columns in browser local storage",
                "By converting SQL queries into NoSQL JSON documents"
            ],
            "correct_index": 1,
            "explanation": "A B-Tree index maintains a self-balancing ordered tree on the indexed column values, allowing the query engine to seek specific rows in O(log N) time rather than scanning every page in the table.",
            "deficiency_diagnostic": "Lacks fundamental knowledge of SQL database indexing and performance optimization."
        }
    ],
    "PostgreSQL": [
        {
            "id": "pg_mcq_1",
            "skill": "PostgreSQL",
            "topic": "ACID & MVCC",
            "question": "How does PostgreSQL implement Multi-Version Concurrency Control (MVCC) to allow readers and writers to operate concurrently without locking?",
            "options": [
                "By locking the entire database table during every UPDATE",
                "By maintaining row versions with xmin/xmax transaction visibility IDs so readers see consistent snapshots without blocking writes",
                "By storing all database tables in RAM memory only",
                "By converting all transactions to single-threaded operations"
            ],
            "correct_index": 1,
            "explanation": "PostgreSQL MVCC assigns transaction IDs to row versions (tuples). When a row is modified, a new tuple is written with xmin/xmax timestamps, allowing active transactions to read the snapshot corresponding to their start time without locking table writes.",
            "deficiency_diagnostic": "Lacking understanding of PostgreSQL MVCC, transaction isolation, and database concurrency."
        }
    ],
    "System Design": [
        {
            "id": "sys_mcq_1",
            "skill": "System Design",
            "topic": "Database Sharding vs Replication",
            "question": "When scaling a database layer, what is the primary distinction between Read Replication and Horizontal Sharding?",
            "options": [
                "Read Replication splits writes across partitions, while Sharding copies all data to replicas",
                "Read Replication distributes read traffic by duplicating data across slave nodes, whereas Sharding partitions dataset rows across multiple physical databases based on a shard key to scale write throughput and storage",
                "Sharding is only used for caching, while Replication is used for DNS",
                "Replication requires NoSQL, while Sharding works only with SQLite"
            ],
            "correct_index": 1,
            "explanation": "Read replicas clone master data to serve read-heavy queries. Horizontal sharding breaks huge tables into independent chunks (partitions) across servers by shard key to scale both write volume and dataset size.",
            "deficiency_diagnostic": "Weakness in distributed system design, horizontal data partitioning, and database scaling architectures."
        }
    ],

    # 3. DATA SCIENCE & MACHINE LEARNING
    "Python": [
        {
            "id": "py_mcq_1",
            "skill": "Python",
            "topic": "GIL & Memory Management",
            "question": "What is the primary constraint imposed by Python's Global Interpreter Lock (GIL) on CPU-bound multithreaded programs?",
            "options": [
                "It disables memory garbage collection completely",
                "It restricts pure CPython execution to a single thread at a time, preventing CPU-bound threads from running in parallel on multi-core processors",
                "It prevents Python from reading CSV files larger than 1GB",
                "It forces all variables to be statically typed"
            ],
            "correct_index": 1,
            "explanation": "CPython's GIL is a mutex protecting internal reference counts. Only one native thread can execute Python bytecode at a time, making multiprocessing or C-extensions necessary for parallel CPU tasks.",
            "deficiency_diagnostic": "Lacking understanding of Python memory model, CPython GIL constraints, and multiprocessing vs multithreading."
        }
    ],
    "Pandas": [
        {
            "id": "pd_mcq_1",
            "skill": "Pandas",
            "topic": "Vectorization & Memory Optimization",
            "question": "Why is vectorized computation in Pandas/NumPy substantially faster than iterating through rows with Python for-loops or df.iterrows()?",
            "options": [
                "Because Pandas compiles code to WebAssembly in the cloud",
                "Because vectorized operations execute in compiled C/Fortran routines with contiguous memory layout and CPU SIMD instructions",
                "Because for-loops convert numbers into strings at runtime",
                "Because Pandas creates new threads for every integer"
            ],
            "correct_index": 1,
            "explanation": "Vectorized operations operate on contiguous arrays directly in low-level compiled C code, leveraging CPU caches and SIMD instructions, avoiding Python interpreter overhead per item.",
            "deficiency_diagnostic": "Lacks understanding of data processing vectorization, memory layout, and computational efficiency in Pandas/NumPy."
        }
    ],
    "Machine Learning": [
        {
            "id": "ml_mcq_1",
            "skill": "Machine Learning",
            "topic": "Bias-Variance Tradeoff",
            "question": "If a model achieves 99.8% accuracy on the training set but only 62.4% on the cross-validation set, what problem is occurring and how is it addressed?",
            "options": [
                "High Bias (Underfitting) &rarr; Address by removing features",
                "High Variance (Overfitting) &rarr; Address with L1/L2 regularization, dropout, feature reduction, or more training data",
                "Data Leakage in validation set only",
                "Learning rate is set to zero"
            ],
            "correct_index": 1,
            "explanation": "A massive gap between high training accuracy and low validation score indicates High Variance (Overfitting). Regularization penalties, pruning, dropout, and cross-validation mitigate this.",
            "deficiency_diagnostic": "Struggles with diagnosing model overfitting/underfitting and applying regularization techniques."
        }
    ],
    "Statistics": [
        {
            "id": "stat_mcq_1",
            "skill": "Statistics",
            "topic": "P-Value & Hypothesis Testing",
            "question": "In statistical hypothesis testing, what does a p-value of 0.03 indicate when testing against a significance threshold of alpha = 0.05?",
            "options": [
                "There is a 97% probability that the null hypothesis is definitely true",
                "The probability of observing data at least as extreme as the sample data, assuming the null hypothesis is true, is 3%, leading to rejection of the null hypothesis",
                "The experimental effect size is exactly 0.03 units",
                "The test failed due to insufficient sample size"
            ],
            "correct_index": 1,
            "explanation": "The p-value is the probability of obtaining test results at least as extreme as the observed data under the assumption that the null hypothesis is true. Since p (0.03) < alpha (0.05), we reject the null hypothesis.",
            "deficiency_diagnostic": "Lacks clarity on statistical hypothesis testing, p-values, and statistical significance interpretation."
        }
    ],

    # 4. DEVOPS & CLOUD
    "Docker": [
        {
            "id": "docker_mcq_1",
            "skill": "Docker",
            "topic": "Containerization & Layer Caching",
            "question": "How should a Dockerfile be structured to maximize Docker build layer caching for a Node.js / Python application?",
            "options": [
                "Copy all source code files before copying package.json or requirements.txt",
                "Copy dependency manifest files (package.json / requirements.txt) and run dependency installs BEFORE copying application source code",
                "Combine all commands into a single RUN instruction on line 1",
                "Disable Docker layer caching with --no-cache on every build"
            ],
            "correct_index": 1,
            "explanation": "Placing infrequently changed steps (like package manifest copies and dependency installations) before frequently modified source code ensures Docker reuses cached dependency layers on subsequent builds.",
            "deficiency_diagnostic": "Unfamiliar with containerization best practices and CI/CD image build acceleration."
        }
    ],
    "Kubernetes": [
        {
            "id": "k8s_mcq_1",
            "skill": "Kubernetes",
            "topic": "Workload Controllers & Probes",
            "question": "What is the critical difference between a Kubernetes 'Liveness Probe' and a 'Readiness Probe'?",
            "options": [
                "Liveness probes check disk space, while readiness probes check CPU usage",
                "A failed Liveness Probe causes Kubernetes to restart the container, while a failed Readiness Probe removes the Pod from Service endpoints so it stops receiving client traffic",
                "Readiness probes only execute inside CI/CD pipelines",
                "Liveness probes work only with AWS EKS"
            ],
            "correct_index": 1,
            "explanation": "Liveness probes detect deadlocks/crashes (triggering container restart). Readiness probes detect when an app is temporarily overloaded or warming up caches, stopping traffic routing without destroying the container.",
            "deficiency_diagnostic": "Lacking understanding of Kubernetes container lifecycle management, health probes, and service traffic routing."
        }
    ],
    "CI/CD": [
        {
            "id": "cicd_mcq_1",
            "skill": "CI/CD",
            "topic": "Zero Downtime Deployments",
            "question": "In automated CI/CD releases, how does a Blue-Green deployment strategy eliminate downtime during production updates?",
            "options": [
                "By shutting down all servers for 5 minutes during database migrations",
                "By maintaining two identical environments (Blue active, Green new release), deploying and verifying the update on Green, and atomically switching the load balancer router to Green",
                "By compiling code directly on production edge nodes",
                "By running containers without health checks"
            ],
            "correct_index": 1,
            "explanation": "Blue-Green deployment runs two production environments. Traffic remains on Blue while Green is upgraded and tested. Once verified, router traffic is switched instantly to Green with instant rollback capability.",
            "deficiency_diagnostic": "Unfamiliar with modern CI/CD deployment strategies (Blue-Green, Canary, Rolling updates)."
        }
    ],
    "Linux": [
        {
            "id": "linux_mcq_1",
            "skill": "Linux",
            "topic": "Process Signals & File Descriptors",
            "question": "What is the difference between sending SIGTERM (signal 15) and SIGKILL (signal 9) to a running Linux process?",
            "options": [
                "SIGTERM and SIGKILL are identical in modern Linux kernels",
                "SIGTERM allows the process to catch the signal, flush buffers, close database connections, and terminate gracefully; SIGKILL immediately terminates the process by the kernel without allowing cleanup",
                "SIGKILL is only used for web servers",
                "SIGTERM restarts the process automatically"
            ],
            "correct_index": 1,
            "explanation": "SIGTERM (15) requests graceful shutdown, allowing the application to handle cleanup handlers. SIGKILL (9) cannot be caught, blocked, or ignored, causing the kernel to unceremoniously kill process memory.",
            "deficiency_diagnostic": "Lacking fundamental Linux process management, signal handling, and graceful container termination knowledge."
        }
    ],

    # 5. MOBILE
    "React Native": [
        {
            "id": "rn_mcq_1",
            "skill": "React Native",
            "topic": "Bridge & New Architecture (JSI / Fabric)",
            "question": "How does the React Native New Architecture (Fabric / JSI) improve UI performance over the legacy bridge?",
            "options": [
                "By running all JavaScript inside native Android Dalvik bytecode",
                "By replacing asynchronous JSON serialization over the asynchronous bridge with direct synchronous C++ JavaScript Interface (JSI) invocation of native methods",
                "By removing all mobile operating system dependencies",
                "By converting React Native into a static WebAssembly bundle"
            ],
            "correct_index": 1,
            "explanation": "The legacy bridge serialized JSON asynchronously across threads. JSI (JavaScript Interface) exposes native C++ host objects directly to JavaScript, enabling synchronous, high-speed native UI rendering without serialization overhead.",
            "deficiency_diagnostic": "Lacking knowledge of React Native runtime internals, JSI architecture, and mobile rendering thread synchronization."
        }
    ],
    "Git": [
        {
            "id": "git_mcq_1",
            "skill": "Git",
            "topic": "Version Control & Branching",
            "question": "What is the primary difference between 'git merge' and 'git rebase' when integrating branch changes?",
            "options": [
                "Merge deletes the source branch, while rebase duplicates the repository",
                "Merge creates a 3-way merge commit preserving history topology, while rebase replays commits sequentially onto the target base creating a linear history",
                "Rebase is only used to push files to cloud servers",
                "Merge cannot resolve file conflicts"
            ],
            "correct_index": 1,
            "explanation": "Git merge preserves full historical branch context by creating a dedicated merge commit. Git rebase rewrites project history by replaying local commits one-by-one on top of the target branch tip for a clean linear log.",
            "deficiency_diagnostic": "Lacks clear mental model of Git history manipulation, merge strategies, and conflict rebase workflows."
        }
    ]
}

class InterviewService:
    """
    Dynamic resume-tailored technical MCQ generator, quiz simulator,
    and skill deficiency diagnostic engine.
    """

    def generate_dynamic_mcqs(
        self, 
        role: str, 
        detected_skills: Dict[str, float], 
        count: int = 5,
        resume_text: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Dynamically generates/selects fresh MCQs tailored to the candidate's
        resume skills and target role.
        """
        # 1. Try Gemini AI generation if API key is active
        if gemini_service.is_available and resume_text:
            try:
                ai_mcqs = self._generate_ai_mcqs(role, detected_skills, count, resume_text)
                if ai_mcqs and len(ai_mcqs) >= count:
                    return ai_mcqs
            except Exception as e:
                logger.warning(f"Gemini MCQ dynamic generation fallback: {e}")

        # 2. Intelligent Role-Specific Dynamic Selection from Question Bank
        return self._select_randomized_skill_mcqs(role, detected_skills, count)

    def _generate_ai_mcqs(self, role: str, detected_skills: Dict[str, float], count: int, resume_text: str) -> Optional[List[Dict[str, Any]]]:
        if not gemini_service._client:
            return None

        skills_list = list(detected_skills.keys())
        prompt = f"""You are a Principal Technical Interviewer conducting a rigorous technical assessment for a {role.upper()} DEVELOPER position.
The candidate's resume includes the following detected skills: {', '.join(skills_list)}.

Generate {count} unique, high-quality multiple choice technical questions (MCQs) tailored specifically for the {role.upper()} role, testing both their stated skills and critical industry knowledge for {role.upper()}.

Output ONLY valid JSON in this exact structure without markdown backticks:
[
  {{
    "id": "ai_q_1",
    "skill": "SkillName (e.g. Node.js, React, SQL, Docker)",
    "topic": "Specific Topic",
    "question": "Clear technical question scenario",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Detailed technical explanation of why this answer is correct",
    "deficiency_diagnostic": "Actionable feedback explaining what technical deficiency a candidate has if they answer this wrong"
  }}
]
"""
        try:
            response = gemini_service._client.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            parsed = json.loads(raw_text.strip())
            if isinstance(parsed, list) and len(parsed) > 0:
                for q in parsed:
                    self._shuffle_mcq_options(q)
                return parsed[:count]
        except Exception as e:
            logger.warning(f"Error parsing Gemini generated MCQs: {e}")
            return None

    def _select_randomized_skill_mcqs(self, role: str, detected_skills: Dict[str, float], count: int = 5) -> List[Dict[str, Any]]:
        """
        Picks questions strictly tailored to the selected target role and candidate skills.
        """
        norm_role = (role or "frontend").lower().strip()
        candidate_skills = list(detected_skills.keys())

        # Extract role-specific skills from taxonomy
        role_data = ROLE_REQUIREMENTS.get(norm_role, ROLE_REQUIREMENTS.get("frontend", {}))
        if isinstance(role_data, dict):
            req_items = role_data.get("requirements", [])
        else:
            req_items = role_data

        target_role_skills = []
        for item in req_items:
            if isinstance(item, (list, tuple)):
                target_role_skills.append(item[0])
            elif isinstance(item, dict):
                target_role_skills.append(item.get("skill"))
            else:
                target_role_skills.append(str(item))

        # Priority 1: Questions matching skills that belong to the target role
        role_specific_pool = []
        candidate_match_pool = []
        general_pool = []

        for skill, questions in TECH_MCQ_BANK.items():
            for q in questions:
                q_copy = dict(q)
                q_copy["options"] = list(q["options"])

                if skill in target_role_skills:
                    if skill in candidate_skills:
                        candidate_match_pool.append(q_copy)
                    else:
                        role_specific_pool.append(q_copy)
                else:
                    general_pool.append(q_copy)

        random.shuffle(candidate_match_pool)
        random.shuffle(role_specific_pool)
        random.shuffle(general_pool)

        selected = []
        # Add candidate skills that are relevant to this role first (e.g. 2 questions)
        selected.extend(candidate_match_pool[:2])
        # Add required gap skills for this target role (e.g. 3 questions)
        remaining = count - len(selected)
        selected.extend(role_specific_pool[:remaining])

        # If still short, backfill from candidate match, then general
        if len(selected) < count:
            for q in candidate_match_pool:
                if len(selected) >= count: break
                if not any(s["id"] == q["id"] for s in selected):
                    selected.append(q)

        if len(selected) < count:
            for q in general_pool:
                if len(selected) >= count: break
                if not any(s["id"] == q["id"] for s in selected):
                    selected.append(q)

        random.shuffle(selected)
        for q in selected:
            self._shuffle_mcq_options(q)

        return selected[:count]

    def _shuffle_mcq_options(self, q: Dict[str, Any]):
        """Randomly shuffles the 4 options and updates correct_index accordingly."""
        opts = q.get("options", [])
        if len(opts) < 2:
            return
        
        correct_answer = opts[q["correct_index"]]
        shuffled = list(opts)
        random.shuffle(shuffled)
        
        q["options"] = shuffled
        q["correct_index"] = shuffled.index(correct_answer)

    def evaluate_mcq_session(self, role: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates the completed MCQ round, generates detailed skill-by-skill
        deficiency diagnostics, and determines formal Technical Clearance status.
        """
        total = len(answers)
        if total == 0:
            return {
                "overall_score": 0,
                "accuracy_pct": 0,
                "total_questions": 0,
                "correct_count": 0,
                "clearance_status": "PENDING",
                "is_cleared": False,
                "diagnostics": [],
                "summary": "No questions answered."
            }

        correct_count = sum(1 for a in answers if a.get("is_correct", False))
        accuracy_pct = int(round((correct_count / total) * 100))
        is_cleared = accuracy_pct >= 60

        diagnostics = []
        for a in answers:
            is_c = a.get("is_correct", False)
            skill = a.get("skill", "General")
            topic = a.get("topic", "Core Technical")
            diagnostic_msg = a.get("deficiency_diagnostic", f"Review core principles of {skill}.")

            diagnostics.append({
                "question_id": a.get("id"),
                "skill": skill,
                "topic": topic,
                "is_correct": is_c,
                "status_badge": "MASTERED" if is_c else "SKILL GAP DETECTED",
                "diagnostic_message": f"Solid conceptual mastery in {skill} ({topic})." if is_c else f"Lacking Skill in {skill} ({topic}): {diagnostic_msg}"
            })

        clearance_badge = "CLEARANCE GRANTED" if is_cleared else "CLEARANCE BLOCKED"
        summary = (
            f"Technical Assessment for {role.upper()} Completed. "
            f"Candidate achieved {correct_count}/{total} ({accuracy_pct}%). "
            f"{'Demonstrated sufficient conceptual foundation to proceed to live technical interviews.' if is_cleared else 'Critical conceptual skill deficiencies detected. Review the diagnosed areas below and complete the recommended roadmap milestones.'}"
        )

        return {
            "overall_score": accuracy_pct,
            "accuracy_pct": accuracy_pct,
            "total_questions": total,
            "correct_count": correct_count,
            "clearance_status": clearance_badge,
            "is_cleared": is_cleared,
            "diagnostics": diagnostics,
            "summary": summary
        }

interview_service = InterviewService()
