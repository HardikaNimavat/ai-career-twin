// In-memory token storage (NOT in localStorage)
let _inMemoryToken = null;

const API = {
  baseUrl: "/api/v1",

  setToken(token) {
    _inMemoryToken = token;
  },

  getToken() {
    return _inMemoryToken;
  },

  clearToken() {
    _inMemoryToken = null;
  },

  async _fetchWithAuth(url, options = {}) {
    const headers = Object.assign({}, options.headers || {});
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const fetchOptions = Object.assign({}, options, {
      headers,
      credentials: "include"
    });
    return fetch(url, fetchOptions);
  },

  async register(email, password, username = null) {
    const res = await this._fetchWithAuth(`${this.baseUrl}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, username })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Registration failed (${res.status})`);
    }
    const data = await res.json();
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  async login(email, password) {
    const res = await this._fetchWithAuth(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Login failed (${res.status})`);
    }
    const data = await res.json();
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  async logout() {
    try {
      await this._fetchWithAuth(`${this.baseUrl}/auth/logout`, { method: "POST" });
    } finally {
      this.clearToken();
    }
  },

  async getMe() {
    const res = await this._fetchWithAuth(`${this.baseUrl}/auth/me`);
    if (!res.ok) throw new Error("Not authenticated");
    return await res.json();
  },

  async deleteMyData() {
    const res = await this._fetchWithAuth(`${this.baseUrl}/profile/me`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete user profile data");
    return await res.json();
  },

  async exportMyData() {
    const res = await this._fetchWithAuth(`${this.baseUrl}/profile/me/export`);
    if (!res.ok) throw new Error("Failed to export user profile data");
    return await res.json();
  },


  _setOnlineStatus(isLive, message) {
    const badge = document.getElementById('apiStatusBadge');
    const banner = document.getElementById('offlineBanner');
    if (badge) {
      if (isLive) {
        badge.textContent = "FASTAPI • ML LIVE";
        badge.style.color = "var(--accent)";
        badge.style.borderColor = "var(--accent-dim)";
        badge.style.background = "var(--accent-soft)";
      } else {
        badge.textContent = "⚠️ OFFLINE PREVIEW (LOCAL FALLBACK)";
        badge.style.color = "var(--amber)";
        badge.style.borderColor = "var(--amber-dim)";
        badge.style.background = "var(--amber-soft)";
      }
    }
    if (banner) {
      if (isLive) {
        banner.style.display = 'none';
      } else {
        banner.style.display = 'flex';
        const msgEl = document.getElementById('offlineBannerMsg');
        if (msgEl && message) msgEl.textContent = message;
      }
    }
  },

  // ─── Text-based resume parsing (original) ───
  async parseAndGenerateTwin(resumeText, githubUsername, targetRole) {
    try {
      const response = await this._fetchWithAuth(`${this.baseUrl}/profile/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: resumeText,
          github_username: githubUsername,
          target_role: targetRole
        })
      });
      if (response.ok) {
        this._setOnlineStatus(true);
        return await response.json();
      }
      throw new Error(`Server status ${response.status}`);
    } catch (err) {
      console.warn("[API] Backend unavailable, activating local fallback preview:", err);
      this._setOnlineStatus(false, "Backend server (FastAPI) is offline or unreachable. Displaying local offline preview. Start backend with 'python run.py' for live ML predictions.");
      return this._clientFallback(resumeText, githubUsername, targetRole);
    }
  },

  // ─── File-based resume & multiple certificate upload (PDF/Image) ───
  async uploadResume(fileOrFiles, githubUsername, targetRole, resumeText = "") {
    try {
      const formData = new FormData();
      if (Array.isArray(fileOrFiles)) {
        if (fileOrFiles.length > 0) {
          formData.append("file", fileOrFiles[0]);
          fileOrFiles.forEach(f => formData.append("files", f));
        }
      } else if (fileOrFiles) {
        formData.append("file", fileOrFiles);
        formData.append("files", fileOrFiles);
      }
      formData.append("github_username", githubUsername || "");
      formData.append("target_role", targetRole || "frontend");
      if (resumeText && resumeText.trim()) {
        formData.append("resume_text", resumeText.trim());
      }

      const response = await this._fetchWithAuth(`${this.baseUrl}/resume/upload`, {
        method: "POST",
        body: formData
      });
      if (response.ok) {
        this._setOnlineStatus(true);
        return await response.json();
      }
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    } catch (err) {
      console.warn("[API] Resume upload error:", err);
      throw err;
    }
  },

  // ─── NEW: Multi-format exam generation ───
  async generateExam(role, examType = "mcq", count = 5, difficulty = "intermediate", detectedSkills = {}, weakSkills = [], profileId = null) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/exam/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profileId,
          role: role,
          exam_type: examType,
          count: count,
          difficulty: difficulty,
          detected_skills: detectedSkills,
          weak_skills: weakSkills
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Exam generation fallback:", e);
    }
    // ── CLIENT-SIDE FALLBACK: rich question bank ──
    return this._clientFallbackExam(role, examType, count, difficulty);
  },

  _clientFallbackExam(role, examType, count, difficulty) {
    const mcqBank = [
      {
        id: "fb_mcq_1", exam_type: "mcq", skill: "JavaScript", topic: "Event Loop & Async",
        question: "In JavaScript, which queue takes highest priority after the synchronous call stack empties?",
        options: [
          "Microtask Queue (Promise .then, queueMicrotask)",
          "Macrotask Queue (setTimeout, setInterval)",
          "I/O polling queue",
          "Rendering callback queue"
        ],
        correct_index: 0,
        explanation: "Microtasks (Promise callbacks) execute immediately after the call stack empties, before any macrotasks (setTimeout/setInterval)."
      },
      {
        id: "fb_mcq_2", exam_type: "mcq", skill: "React", topic: "Hooks & Closures",
        question: "Why does a useEffect callback sometimes read stale state values?",
        options: [
          "React compiles hooks into WebAssembly at build time",
          "JavaScript closures capture variable values from the render they were created in — unless listed in the dependency array",
          "useEffect only runs on server-side rendering workers",
          "React state is globally mutable across concurrent threads"
        ],
        correct_index: 1,
        explanation: "If a state variable is omitted from the dependency array, the effect holds a stale closure from a prior render cycle."
      },
      {
        id: "fb_mcq_3", exam_type: "mcq", skill: "HTML/CSS", topic: "CSS Layout",
        question: "What is the key architectural difference between CSS Flexbox and CSS Grid?",
        options: [
          "Flexbox is 1-dimensional (row OR column); Grid is 2-dimensional (rows AND columns simultaneously)",
          "Flexbox is only supported in Safari; Grid is Chrome-only",
          "Grid cannot align items along the cross-axis",
          "Flexbox does not support responsive breakpoints"
        ],
        correct_index: 0,
        explanation: "Flexbox manages layout along a single axis at a time. CSS Grid controls both row and column axes simultaneously."
      },
      {
        id: "fb_mcq_4", exam_type: "mcq", skill: "TypeScript", topic: "Type Safety",
        question: "Why is TypeScript's 'unknown' type preferred over 'any' for untrusted runtime data?",
        options: [
          "'unknown' disables all type-checking permanently",
          "'unknown' forces explicit type narrowing before the value can be used, making code type-safe",
          "'unknown' can only hold boolean primitive values",
          "'unknown' executes faster than 'any' at JavaScript runtime"
        ],
        correct_index: 1,
        explanation: "'unknown' requires type narrowing (typeof, instanceof) before any property access, preventing silent runtime errors."
      },
      {
        id: "fb_mcq_5", exam_type: "mcq", skill: "Git", topic: "Branch Management",
        question: "What is the core difference between 'git merge' and 'git rebase'?",
        options: [
          "Merge deletes the source branch; rebase duplicates the entire repository",
          "Merge creates a merge commit preserving full branch topology; rebase replays commits to produce a linear history",
          "Rebase is only used to push files to remote cloud servers",
          "Merge cannot resolve file conflicts"
        ],
        correct_index: 1,
        explanation: "Merge preserves the full branch graph with a merge commit. Rebase rewrites commit history linearly onto the target branch tip."
      },
      {
        id: "fb_mcq_6", exam_type: "mcq", skill: "Web Performance", topic: "Core Web Vitals",
        question: "Which Core Web Vital metric measures the time until the largest content element is rendered on screen?",
        options: [
          "CLS — Cumulative Layout Shift",
          "INP — Interaction to Next Paint",
          "LCP — Largest Contentful Paint",
          "FID — First Input Delay"
        ],
        correct_index: 2,
        explanation: "LCP (Largest Contentful Paint) measures how long until the most significant element (hero image or heading) is fully rendered."
      },
      {
        id: "fb_mcq_7", exam_type: "mcq", skill: "Node.js", topic: "Event-Driven Architecture",
        question: "What is the main reason Node.js can handle many concurrent connections with a single thread?",
        options: [
          "Node.js uses real OS threads for every incoming request",
          "Node.js uses a non-blocking, event-driven I/O model with a single event loop — long operations are offloaded to libuv",
          "Node.js runs on multi-core CPUs by default without any configuration",
          "Node.js holds all connections in RAM-based queues across multiple V8 processes"
        ],
        correct_index: 1,
        explanation: "Node.js delegates I/O to libuv's thread pool and returns immediately. The event loop picks up callbacks when operations complete."
      },
      {
        id: "fb_mcq_8", exam_type: "mcq", skill: "CSS", topic: "Specificity",
        question: "Which CSS selector has the HIGHEST specificity weight?",
        options: [
          "p { color: red; }  (element selector)",
          ".text { color: blue; }  (class selector)",
          "#header { color: green; }  (ID selector)",
          "* { color: yellow; }  (universal selector)"
        ],
        correct_index: 2,
        explanation: "ID selectors have a specificity value of (0,1,0,0) — far higher than classes (0,0,1,0) or elements (0,0,0,1)."
      },
      {
        id: "fb_mcq_9", exam_type: "mcq", skill: "Algorithms", topic: "Time Complexity",
        question: "What is the average-case time complexity of a Binary Search on a sorted array of N elements?",
        options: ["O(N)", "O(N²)", "O(log N)", "O(1)"],
        correct_index: 2,
        explanation: "Binary Search halves the search space at each step, giving O(log N) average and worst-case complexity."
      },
      {
        id: "fb_mcq_10", exam_type: "mcq", skill: "REST APIs", topic: "HTTP Methods",
        question: "Which HTTP method is idempotent and should be used to fully replace a resource?",
        options: ["POST", "PATCH", "PUT", "DELETE"],
        correct_index: 2,
        explanation: "PUT is idempotent — calling it multiple times with the same payload produces the same result (full resource replacement). POST is not idempotent."
      }
    ];

    const codeBank = [
      {
        id: "fb_code_1", exam_type: "code", skill: "JavaScript", topic: "Array Methods",
        question: "Write a function `findDuplicates(arr)` that returns an array of all duplicate values in the input array. Example: findDuplicates([1,2,3,2,4,1]) → [2,1]",
        language: "javascript",
        starter_code: "function findDuplicates(arr) {\n  // Write your solution here\n}",
        expected_points: ["Use a Map or Set to track counts", "Return only values appearing more than once"],
        expected_optimal_time: "O(n)",
        expected_optimal_space: "O(n)"
      }
    ];

    const essayBank = [
      {
        id: "fb_essay_1", exam_type: "essay", skill: "System Design", topic: "Scalability",
        question: "Explain how you would design a URL shortener service (like bit.ly). Describe the key components, database schema, and how you would handle 10 million daily requests.",
        max_word_count: 400,
        expected_points: ["Load balancer", "Key generation service", "Database (SQL or NoSQL)", "Caching layer (Redis)", "CDN for redirects"]
      }
    ];

    const debugBank = [
      {
        id: "fb_debug_1", exam_type: "debug", skill: "JavaScript", topic: "Async/Await",
        question: "The following code has a bug that causes it to always print 'undefined' instead of the fetched user name. Find and fix the bug.",
        language: "javascript",
        bug_description: "The function returns before the async fetch completes, so it always resolves to undefined.",
        buggy_code: `async function getUserName(id) {\n  let name;\n  fetch('/api/user/' + id)\n    .then(res => res.json())\n    .then(data => { name = data.name; });\n  return name;\n}`,
        starter_code: `async function getUserName(id) {\n  // Fix the bug here\n}`,
        expected_points: ["Use await before fetch", "Properly chain or await .json()"],
        expected_optimal_time: "O(1)",
        expected_optimal_space: "O(1)"
      }
    ];

    let bank;
    if (examType === "code") bank = codeBank;
    else if (examType === "essay" || examType === "design") bank = essayBank;
    else if (examType === "debug") bank = debugBank;
    else if (examType === "mixed") {
      bank = [...mcqBank.slice(0, 3), ...codeBank, ...essayBank];
    } else {
      bank = mcqBank;
    }

    const shuffled = [...bank].sort(() => Math.random() - 0.5);
    return { questions: shuffled.slice(0, Math.min(count, shuffled.length)) };
  },

  // ─── NEW: Submit exam answers for evaluation ───
  async submitExam(profileId, role, examType, answers, questions = [], totalTimeSeconds = 0) {
    try {
      // Enrich answers with question data for evaluation
      const enrichedAnswers = answers.map(a => {
        const question = questions.find(q => q.id === a.question_id) || {};
        return {
          ...a,
          skill: question.skill || a.skill || "General",
          topic: question.topic || a.topic || "",
          question_text: question.question || a.question_text || "",
          options: question.options || a.options || [],
          correct_index: question.correct_index !== undefined ? question.correct_index : a.correct_index,
          expected_points: question.expected_points || a.expected_points || [],
          buggy_code: question.buggy_code || a.buggy_code || "",
          bug_description: question.bug_description || a.bug_description || "",
          explanation: question.explanation || a.explanation || "",
          expected_optimal_time: question.expected_optimal_time || a.expected_optimal_time || "O(n)",
          expected_optimal_space: question.expected_optimal_space || a.expected_optimal_space || "O(1)"
        };
      });

      const res = await this._fetchWithAuth(`${this.baseUrl}/exam/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profileId,
          role: role,
          exam_type: examType,
          answers: enrichedAnswers,
          questions: questions,
          total_time_seconds: totalTimeSeconds
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Exam submission fallback:", e);
    }
    // Local fallback evaluation
    const total = answers.length || 1;
    const correct = answers.filter(a => a.is_correct).length;
    const accuracy = Math.round((correct / total) * 100);
    return {
      overall_score: accuracy,
      accuracy_pct: accuracy,
      total_questions: total,
      correct_count: correct,
      clearance_status: accuracy >= 60 ? "CLEARANCE GRANTED" : "CLEARANCE BLOCKED",
      is_cleared: accuracy >= 60,
      results: answers.map(a => ({
        question_id: a.question_id,
        skill: a.skill || "General",
        topic: a.topic || "",
        exam_type: a.exam_type || examType,
        is_correct: !!a.is_correct,
        score: a.is_correct ? 100 : 0,
        accuracy_pct: a.is_correct ? 100 : 30,
        time_complexity: "O(1)",
        space_complexity: "O(1)",
        feedback: a.is_correct ? "✅ Passed" : "❌ Gaps detected",
        skill_impact: a.is_correct ? 7.0 : -2.0
      })),
      skill_updates: {},
      twin_updated: false,
      overall_time_complexity: "O(1)",
      overall_space_complexity: "O(1)",
      summary: accuracy >= 60 ? "Exam cleared with optimal efficiency." : "Some conceptual gaps detected.",
      recommendations: ["Review weak skills in personalized roadmap"]
    };
  },

  // ─── NEW: Get skill progression timeline ───
  async getSkillProgression(profileId) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/exam/progression/${profileId}`);
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Skill progression fallback:", e);
    }
    return { history: [], total_exams_taken: 0, improvement_summary: "No data yet." };
  },

  // ─── NEW: Get exam history ───
  async getExamHistory(profileId) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/exam/history/${profileId}`);
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Exam history fallback:", e);
    }
    return { sessions: [], total_exams: 0 };
  },

  // ─── Existing endpoints (unchanged) ───
  async analyzeGitHub(username) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/github/analyze?username=${encodeURIComponent(username || '')}`);
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] GitHub API fallback:", e);
    }
    return null;
  },

  async analyzeGaps(targetRole, candidateSkills) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/gap/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_role: targetRole,
          candidate_skills: candidateSkills
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Gap analysis fallback:", e);
    }
    return null;
  },

  async generateRoadmap(gapRows) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/roadmap/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(gapRows)
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Roadmap fallback:", e);
    }
    return null;
  },

  async verifyCertificate(filename, targetRole = "frontend", currentSkills = {}, resumeText = "", verifiedCerts = []) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/certificate/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: filename,
          target_role: targetRole,
          current_skills: currentSkills,
          resume_text: resumeText,
          verified_certs: verifiedCerts
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Certificate API fallback:", e);
    }
    return null;
  },

  async estimateSalary(role, skillMatchPct, expYears, location, githubScore) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/salary/estimate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role,
          skill_match_pct: skillMatchPct,
          experience_years: expYears,
          location,
          github_score: githubScore
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Salary API fallback:", e);
    }
    return null;
  },

  async predictTrajectory(targetRole, currentReadiness, expYears, learningHours, githubScore) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/predictor/trajectory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_role: targetRole,
          current_readiness: currentReadiness,
          experience_years: expYears,
          learning_hours_weekly: learningHours,
          github_score: githubScore
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] Trajectory API fallback:", e);
    }
    return null;
  },

  async generateDynamicMCQs(role, detectedSkills = {}, count = 5, resumeText = "") {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/interview/generate-mcqs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: role,
          detected_skills: detectedSkills,
          count: count,
          resume_text: resumeText
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        const data = await res.json();
        return data.mcqs;
      }
    } catch (e) {
      console.warn("[API] Dynamic MCQ generation API fallback:", e);
    }
    return this._clientFallbackMCQs(role);
  },

  async evaluateMCQSession(role, answers) {
    try {
      const res = await this._fetchWithAuth(`${this.baseUrl}/interview/evaluate-mcq-session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: role,
          answers: answers
        })
      });
      if (res.ok) {
        this._setOnlineStatus(true);
        return await res.json();
      }
    } catch (e) {
      console.warn("[API] MCQ evaluation API fallback:", e);
    }
    
    // Client fallback evaluation
    const total = answers.length || 1;
    const correct = answers.filter(a => a.is_correct).length;
    const accuracy = Math.round((correct / total) * 100);
    const isCleared = accuracy >= 60;
    return {
      overall_score: accuracy,
      accuracy_pct: accuracy,
      total_questions: total,
      correct_count: correct,
      clearance_status: isCleared ? "CLEARANCE GRANTED" : "CLEARANCE BLOCKED",
      is_cleared: isCleared,
      diagnostics: answers.map(a => ({
        question_id: a.id,
        skill: a.skill || "Technical",
        topic: a.topic || "Core Concept",
        is_correct: a.is_correct,
        status_badge: a.is_correct ? "MASTERED" : "SKILL GAP DETECTED",
        diagnostic_message: a.is_correct ? `Solid understanding of ${a.skill}.` : `Lacking skill in ${a.skill}: ${a.deficiency_diagnostic || 'Review fundamentals.'}`
      })),
      summary: isCleared ? "Technical Clearance Granted for interview rounds." : "Critical Skill Deficiencies detected. Roadmap study recommended."
    };
  },

  _clientFallbackMCQs(role) {
    return [
      {
        id: "mcq_fb_1",
        skill: "JavaScript",
        topic: "Event Loop & Microtasks",
        question: "In the JavaScript Event Loop, which queue takes highest execution priority after the synchronous call stack empties?",
        options: [
          "Microtask Queue (Promise callbacks, queueMicrotask)",
          "Macrotask Queue (setTimeout, setInterval)",
          "I/O polling queue",
          "Rendering frame callback queue"
        ],
        correct_index: 0,
        explanation: "Microtasks (Promise handlers) execute immediately after the synchronous stack empties, prior to any Macrotasks.",
        deficiency_diagnostic: "Lacking understanding of JavaScript async event loop prioritization."
      },
      {
        id: "mcq_fb_2",
        skill: "React",
        topic: "Hooks & Stale Closures",
        question: "In React, why does a useEffect callback sometimes capture stale state variables?",
        options: [
          "Because React compiles components into WebAssembly at runtime",
          "Because JavaScript closures capture variables from the specific render cycle unless declared in the dependency array",
          "Because useEffect only executes on server workers",
          "Because React state is globally mutable across threads"
        ],
        correct_index: 1,
        explanation: "Omission of variables from dependency arrays causes effects to maintain stale closures from previous render cycles.",
        deficiency_diagnostic: "Weakness in React render lifecycles and hook dependency array state management."
      },
      {
        id: "mcq_fb_3",
        skill: "HTML/CSS",
        topic: "CSS Layout Systems",
        question: "What is the key difference between CSS Flexbox and CSS Grid?",
        options: [
          "Flexbox is designed for 1-dimensional layouts (rows OR columns), while Grid is 2-dimensional (rows AND columns)",
          "Flexbox works only in Safari, while Grid is a Chrome-only standard",
          "Grid cannot align items along the cross-axis",
          "Flexbox does not support responsive design breakpoints"
        ],
        correct_index: 0,
        explanation: "Flexbox handles 1D layout distribution; CSS Grid manages 2D grid matrix systems simultaneously.",
        deficiency_diagnostic: "Lacks practical distinction between 1D (Flexbox) and 2D (Grid) CSS layout architecture."
      },
      {
        id: "mcq_fb_4",
        skill: "TypeScript",
        topic: "Type Safety",
        question: "Why is the 'unknown' type preferred over 'any' for untrusted runtime data in TypeScript?",
        options: [
          "'unknown' disables all type checking permanently",
          "'unknown' is type-safe because it forces developers to perform type narrowing before operating on the value",
          "'unknown' can only hold boolean values",
          "'unknown' runs faster at JavaScript execution time"
        ],
        correct_index: 1,
        explanation: "'unknown' forces explicit type narrowing before property access, preventing unexpected runtime errors.",
        deficiency_diagnostic: "Lacks type safety rigor; unfamiliar with TypeScript type narrowing practices."
      },
      {
        id: "mcq_fb_5",
        skill: "Git",
        topic: "Branch Management",
        question: "What is the primary difference between 'git merge' and 'git rebase'?",
        options: [
          "Merge deletes the source branch, while rebase duplicates the repository",
          "Merge creates a 3-way merge commit preserving history topology, while rebase replays commits sequentially for a linear history",
          "Rebase is only used to push files to cloud servers",
          "Merge cannot resolve file conflicts"
        ],
        correct_index: 1,
        explanation: "Merge preserves branch graph topology; rebase replays commits linearly on top of the target base.",
        deficiency_diagnostic: "Lacks clarity on Git history topology and commit rebase mechanisms."
      }
    ];
  },

  _clientFallback(resumeText, githubUsername, targetRole) {
    const defaultDetected = { "HTML/CSS": 85.0, "JavaScript": 70.0, "Git": 75.0 };
    // Try to extract candidate name from resume text (first non-empty line)
    let candidateName = "Hardika";
    if (resumeText && resumeText.trim()) {
      const firstLine = resumeText.trim().split('\n')[0].trim();
      if (firstLine && firstLine.length < 60 && !/[{}[\]<>]/.test(firstLine)) {
        const namePart = firstLine.split(/[,|–\-]/)[0].trim();
        if (namePart && namePart.split(' ').length <= 4) {
          candidateName = namePart;
        }
      }
    }
    return {
      profile: {
        candidate_name: candidateName,
        detected_skills: defaultDetected,
        experience_years: 0.5,
        dominant_cluster: "Frontend",
        skills_count: 3
      },
      github: {
        username: githubUsername || "hardika-nimavat-dev",
        quality_score: 72.0,
        public_repos: 4,
        contributions_per_year: 140,
        top_languages: ["JavaScript", "HTML", "CSS"],
        language_weights: [50, 30, 20],
        diagnostic_notes: ["Good foundational repository layout.", "Consistent commit activity."]
      },
      target_role: targetRole,
      readiness_percentage: 48.0,
      profile_id: null,
      gap_analysis: [
        { skill: "HTML/CSS", match_pct: 100, weight: 3, badge_status: "met", match_via: "direct match" },
        { skill: "JavaScript", match_pct: 100, weight: 3, badge_status: "met", match_via: "direct match" },
        { skill: "Git", match_pct: 100, weight: 1, badge_status: "met", match_via: "direct match" },
        { skill: "React", match_pct: 35, weight: 3, badge_status: "gap", match_via: "prerequisite foundation (JS -> React)" },
        { skill: "TypeScript", match_pct: 40, weight: 2, badge_status: "gap", match_via: "prerequisite foundation (JS -> TS)" },
        { skill: "Tailwind CSS", match_pct: 40, weight: 2, badge_status: "gap", match_via: "prerequisite foundation (CSS -> Tailwind)" },
        { skill: "Next.js", match_pct: 25, weight: 2, badge_status: "gap", match_via: "language foundation" },
        { skill: "Redux", match_pct: 25, weight: 1, badge_status: "gap", match_via: "state management logic" },
        { skill: "Testing", match_pct: 20, weight: 1, badge_status: "gap", match_via: "scripting foundation" }
      ],
      roadmap: [
        { week_label: "Week 1", skill: "React", action: "Master React Core & Hooks", resource_title: "React Official Docs & Hands-on Projects", resource_platform: "react.dev & freeCodeCamp", resource_url: "https://react.dev/learn", estimated_hours: 14, current_match_pct: 35.0 },
        { week_label: "Week 2", skill: "TypeScript", action: "Learn Type-Safe Web Development", resource_title: "TypeScript for JavaScript Developers", resource_platform: "TypeScript Handbook", resource_url: "https://www.typescriptlang.org/docs/handbook/intro.html", estimated_hours: 10, current_match_pct: 40.0 },
        { week_label: "Week 3", skill: "Tailwind CSS", action: "Modern Responsive Styling", resource_title: "Tailwind CSS from Scratch", resource_platform: "Tailwind CSS Docs", resource_url: "https://tailwindcss.com/docs", estimated_hours: 8, current_match_pct: 40.0 },
        { week_label: "Week 4", skill: "Next.js", action: "Full-Stack React Framework & SSR", resource_title: "Next.js App Router Mastery", resource_platform: "nextjs.org/learn", resource_url: "https://nextjs.org/learn", estimated_hours: 12, current_match_pct: 25.0 }
      ],
      salary_estimate: {
        role: targetRole,
        min_lpa: 4.8,
        max_lpa: 6.2,
        median_lpa: 5.5,
        location: "Ahmedabad",
        demand_trend: "+15% YoY"
      },
      trajectory_prediction: {
        prob_3m: 0.58,
        prob_6m: 0.74,
        prob_12m: 0.92,
        readiness_3m: 58,
        readiness_6m: 74,
        readiness_12m: 92,
        summary: "Projected career progression with 14 hrs/week study commitment."
      },
      ats_analysis: {
        ats_score: 78,
        ats_rating: "ATS Compatible (Good)",
        ats_breakdown: { format_score: 85, skill_density_score: 75, action_verbs_score: 70 },
        role_coverage: {
          target_role: targetRole,
          total_required: 9,
          matched_count: 3,
          direct_coverage_pct: 33.3,
          summary: `You possess 3 out of 9 essential skills (33.3% direct match) for ${targetRole.toUpperCase()} Developer.`
        },
        recommended_job_posts: [
          {
            role_id: "junior_web_dev",
            title: "Junior Web Developer",
            match_percentage: 88,
            is_selected_road: false,
            category: "Web Development",
            badge_color: "var(--accent)",
            avg_salary_lpa: "4.5 – 6.8",
            experience_level: "Entry Level (0–2 yrs)",
            description: "Build and maintain responsive client-facing web interfaces using HTML5, CSS3 and vanilla JavaScript. Collaborate with senior engineers on UI components and contribute to design system libraries.",
            matched_skills: ["HTML/CSS", "JavaScript", "Git"],
            missing_skills: ["React", "TypeScript"]
          },
          {
            role_id: "ui_engineer",
            title: "UI Engineer — React & Design Systems",
            match_percentage: 62,
            is_selected_road: true,
            category: "Frontend Engineering",
            badge_color: "var(--amber)",
            avg_salary_lpa: "7.0 – 11.0",
            experience_level: "Associate (1–3 yrs)",
            description: "Design and implement scalable UI component libraries using React, TypeScript and Tailwind CSS. Collaborate with product and UX teams to translate Figma designs into production-grade code.",
            matched_skills: ["HTML/CSS", "JavaScript", "Git"],
            missing_skills: ["React", "TypeScript", "Tailwind CSS"]
          },
          {
            role_id: "react_developer",
            title: "React Developer (SPA & SSR)",
            match_percentage: 54,
            is_selected_road: false,
            category: "Frontend Engineering",
            badge_color: "var(--amber)",
            avg_salary_lpa: "8.0 – 13.5",
            experience_level: "Junior-Mid (1–4 yrs)",
            description: "Build performant single-page and server-rendered applications using React 18 + Next.js App Router. Own component state management, routing, and API integration.",
            matched_skills: ["JavaScript", "HTML/CSS"],
            missing_skills: ["React", "Next.js", "TypeScript"]
          },
          {
            role_id: "fullstack_dev",
            title: "Full Stack Developer (Node + React)",
            match_percentage: 38,
            is_selected_road: false,
            category: "Full Stack",
            badge_color: "var(--coral)",
            avg_salary_lpa: "9.0 – 16.0",
            experience_level: "Mid Level (2–5 yrs)",
            description: "Architect and deliver full-stack features across React frontend and Node.js/Express backend. Own database schema design, REST API development, and frontend state with Redux.",
            matched_skills: ["JavaScript", "Git"],
            missing_skills: ["React", "Node.js", "PostgreSQL", "Redux"]
          },
          {
            role_id: "frontend_intern",
            title: "Frontend Development Intern",
            match_percentage: 92,
            is_selected_road: false,
            category: "Internship",
            badge_color: "var(--accent)",
            avg_salary_lpa: "1.8 – 3.2",
            experience_level: "Student / Fresher",
            description: "Accelerated internship program for Computer Science students. Work on live product UI features, gain mentored exposure to modern frontend stacks, and build a verified project portfolio.",
            matched_skills: ["HTML/CSS", "JavaScript", "Git"],
            missing_skills: []
          },
          {
            role_id: "technical_writer_fe",
            title: "Frontend Technical Content Engineer",
            match_percentage: 72,
            is_selected_road: false,
            category: "DevRel / Content",
            badge_color: "var(--accent)",
            avg_salary_lpa: "5.0 – 8.5",
            experience_level: "Entry-Mid (0–3 yrs)",
            description: "Create interactive tutorials, code examples, and documentation for a developer-facing product. Leverage your coding skills to produce technically accurate and engaging frontend guides.",
            matched_skills: ["HTML/CSS", "JavaScript", "Git"],
            missing_skills: ["React"]
          }
        ]
      }
    };
  }
};
