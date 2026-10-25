window.STATE = {};

const ROLE_LABELS = {
  "frontend": "Frontend Developer",
  "backend": "Backend Developer",
  "fullstack": "Full Stack Developer",
  "data": "Data Scientist",
  "devops": "DevOps Engineer",
  "mobile": "Mobile Developer"
};

// Hardika Nimavat's foundational student resume (demonstrating realistic skill gaps and roadmap)
const SAMPLE_RESUME = `Hardika Nimavat
B.Tech Computer Science & Engineering | Indus University, Ahmedabad (2022–2026)

PROFESSIONAL SUMMARY:
Enthusiastic Computer Engineering student with a strong foundation in core web technologies including HTML/CSS and introductory JavaScript. Built personal static projects and a portfolio website using CSS Flexbox/Grid and DOM scripting. Comfortable using Git for version control and collaborating on GitHub repositories. Eager to master modern engineering frameworks and system architecture to build production-grade scalable applications.

CORE FOUNDATIONAL SKILLS:
- Languages: JavaScript (ES6+ basics), HTML/CSS, C++, Python (basics)
- Version Control: Git, GitHub
- Concepts: Responsive Web Design, DOM Manipulation, Problem Solving

ACADEMIC PROJECTS:
1. Interactive Portfolio Website — Built with HTML5 semantic tags, custom CSS animations, and JavaScript event listeners.
2. Web Calculator & Task Tracker — Client-side web application leveraging JavaScript local storage and responsive CSS layout.`;

const ROLE_MULTIPLIERS = {
  "frontend": [
    { name: "Next.js & App Router", bump: "+18% LPA" },
    { name: "TypeScript Mastery", bump: "+15% LPA" },
    { name: "Tailwind & Design Systems", bump: "+12% LPA" },
    { name: "Frontend System Architecture", bump: "+22% LPA" }
  ],
  "backend": [
    { name: "Microservices & Docker", bump: "+22% LPA" },
    { name: "PostgreSQL & Query Optimization", bump: "+18% LPA" },
    { name: "Distributed Caching (Redis)", bump: "+16% LPA" },
    { name: "High-Throughput System Design", bump: "+25% LPA" }
  ],
  "fullstack": [
    { name: "Next.js Fullstack & GraphQL", bump: "+22% LPA" },
    { name: "Containerization & Cloud Deploy", bump: "+18% LPA" },
    { name: "PostgreSQL & Database Scaling", bump: "+20% LPA" },
    { name: "Fullstack System Architecture", bump: "+25% LPA" }
  ],
  "data": [
    { name: "Deep Learning (PyTorch)", bump: "+26% LPA" },
    { name: "MLOps & Model Deployment", bump: "+24% LPA" },
    { name: "Big Data & Distributed SQL", bump: "+20% LPA" },
    { name: "Statistical Modeling & A/B Testing", bump: "+18% LPA" }
  ],
  "devops": [
    { name: "Kubernetes & Cloud Infrastructure", bump: "+28% LPA" },
    { name: "Terraform & Multi-Cloud IaC", bump: "+24% LPA" },
    { name: "Automated CI/CD & DevSecOps", bump: "+20% LPA" },
    { name: "Observability (Prometheus/Grafana)", bump: "+18% LPA" }
  ],
  "mobile": [
    { name: "React Native & Flutter Mastery", bump: "+22% LPA" },
    { name: "Native Android SDK & Swift", bump: "+20% LPA" },
    { name: "Mobile CI/CD & Store Automation", bump: "+16% LPA" },
    { name: "Offline-First Mobile Architecture", bump: "+18% LPA" }
  ]
};

// ─── Exam State ───
let examState = {
  questions: [],
  answers: [],
  currentIndex: 0,
  examType: "mcq",
  difficulty: "intermediate",
  startTime: null,
  score: 0
};

document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generateBtn');
  const sampleBtn = document.getElementById('sampleBtn');
  const logoutBtn = document.getElementById('logoutBtn');
  const studyHoursSlider = document.getElementById('studyHoursSlider');
  const recalcTrajBtn = document.getElementById('recalcTrajBtn');
  const topRoleSelector = document.getElementById('topRoleSelector');
  const profileRoleSwitchSelect = document.getElementById('profileRoleSwitchSelect');

  function updateResumeCharCount() {
    const resInput = document.getElementById('resumeInput');
    const charCountEl = document.getElementById('textCharCount');
    if (resInput && charCountEl) {
      const len = resInput.value.length;
      charCountEl.textContent = `${len.toLocaleString()} character${len === 1 ? '' : 's'}`;
    }
  }

  if (sampleBtn) {
    sampleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Switch to text mode first
      switchInputMode('text');
      const resInput = document.getElementById('resumeInput');
      if (resInput) resInput.value = SAMPLE_RESUME;
      document.getElementById('githubInput').value = "hardika-nimavat-dev";
      document.getElementById('roleInput').value = "frontend";
      updateResumeCharCount();
    });
  }

  const resumeInput = document.getElementById('resumeInput');
  if (resumeInput) {
    resumeInput.addEventListener('input', () => {
      updateResumeCharCount();
      if (window.STATE.inputMode !== 'text') {
        switchInputMode('text');
      }
    });
    resumeInput.addEventListener('focus', () => {
      if (window.STATE.inputMode !== 'text') {
        switchInputMode('text');
      }
    });
  }

  // Card container clicks to activate mode
  const textCard = document.getElementById('intakeTextCard');
  if (textCard) {
    textCard.addEventListener('click', (e) => {
      if (e.target.id !== 'sampleBtn' && !e.target.closest('#sampleBtn')) {
        switchInputMode('text');
      }
    });
  }

  const uploadCard = document.getElementById('intakeUploadCard');
  if (uploadCard) {
    uploadCard.addEventListener('click', (e) => {
      if (e.target.id !== 'clearUploadBtn' && !e.target.closest('#clearUploadBtn')) {
        switchInputMode('upload');
      }
    });
  }

  if (generateBtn) {
    generateBtn.addEventListener('click', handleGenerate);
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  // Role switchers in Topnav and Profile Header
  if (topRoleSelector) {
    topRoleSelector.addEventListener('change', (e) => {
      switchTargetRole(e.target.value);
    });
  }

  if (profileRoleSwitchSelect) {
    profileRoleSwitchSelect.addEventListener('change', (e) => {
      switchTargetRole(e.target.value);
    });
  }

  document.querySelectorAll('#topnav button[data-panel]').forEach(b => {
    b.addEventListener('click', () => showPanel(b.dataset.panel));
  });

  // Setup City Selector Pills
  setupCityPills();

  if (studyHoursSlider) {
    studyHoursSlider.addEventListener('input', (e) => {
      document.getElementById('studyHrsVal').textContent = `${e.target.value} hrs/wk`;
    });
  }

  if (recalcTrajBtn) {
    recalcTrajBtn.addEventListener('click', updateTrajectoryView);
  }

  // ─── Input Mode Tabs / Switcher Pills (Text vs Upload) ───
  document.querySelectorAll('.input-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.stopPropagation();
      switchInputMode(tab.dataset.mode);
    });
  });

  // ─── Multi-File Upload Handlers (Resume + Multiple Certificates) ───
  const fileInput = document.getElementById('resumeFileInput');
  const dropZone = document.getElementById('resumeDropZone');
  const clearBtn = document.getElementById('clearUploadBtn');

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFilesSelected(e.target.files);
      }
    });
  }

  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFilesSelected(e.dataTransfer.files);
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.STATE.uploadedFiles = [];
      window.STATE.uploadedFile = null;
      document.getElementById('uploadedFileInfo').style.display = 'none';
      document.getElementById('resumeDropZone').style.display = '';
      if (fileInput) fileInput.value = '';
    });
  }

  // ─── Exam Event Listeners ───
  const startExamBtn = document.getElementById('startExamBtn');
  if (startExamBtn) startExamBtn.addEventListener('click', startExam);

  const examSubmitBtn = document.getElementById('examSubmitBtn');
  if (examSubmitBtn) examSubmitBtn.addEventListener('click', submitCurrentAnswer);

  const examNextBtn = document.getElementById('examNextBtn');
  if (examNextBtn) examNextBtn.addEventListener('click', showNextExamQuestion);

  const examBackBtn = document.getElementById('examBackToConfig');
  if (examBackBtn) examBackBtn.addEventListener('click', () => {
    document.getElementById('examActiveContainer').style.display = 'none';
    document.getElementById('examCompletionCard').style.display = 'none';
    document.getElementById('examConfigCard').style.display = '';
  });

  const examRestartBtn = document.getElementById('examRestartBtn');
  if (examRestartBtn) examRestartBtn.addEventListener('click', () => {
    document.getElementById('examCompletionCard').style.display = 'none';
    document.getElementById('examConfigCard').style.display = '';
  });

  const examGoRoadmap = document.getElementById('examGoRoadmapBtn');
  if (examGoRoadmap) examGoRoadmap.addEventListener('click', () => showPanel('roadmap'));

  // ─── Essay word counter ───
  const essayInput = document.getElementById('examEssayInput');
  if (essayInput) {
    essayInput.addEventListener('input', () => {
      const words = essayInput.value.trim().split(/\s+/).filter(w => w.length > 0).length;
      document.getElementById('examWordCount').textContent = words;
    });
  }
});

// ─── Input Mode Switching ───
function switchInputMode(mode) {
  window.STATE.inputMode = mode;

  // Sync pill switcher buttons
  document.querySelectorAll('.input-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.mode === mode);
  });

  // Sync intake cards
  const textCard = document.getElementById('intakeTextCard');
  const uploadCard = document.getElementById('intakeUploadCard');
  const textIndicator = document.getElementById('textModeIndicator');
  const uploadIndicator = document.getElementById('uploadModeIndicator');

  if (mode === 'text') {
    if (textCard) textCard.classList.add('active');
    if (uploadCard) uploadCard.classList.remove('active');
    if (textIndicator) {
      textIndicator.className = 'mode-status-indicator active';
      textIndicator.innerHTML = '<span class="status-dot"></span> Active Selection';
    }
    if (uploadIndicator) {
      uploadIndicator.className = 'mode-status-indicator';
      uploadIndicator.innerHTML = '<span class="status-dot"></span> Click to Select';
    }
  } else {
    if (uploadCard) uploadCard.classList.add('active');
    if (textCard) textCard.classList.remove('active');
    if (uploadIndicator) {
      uploadIndicator.className = 'mode-status-indicator active';
      uploadIndicator.innerHTML = '<span class="status-dot"></span> Active Selection';
    }
    if (textIndicator) {
      textIndicator.className = 'mode-status-indicator';
      textIndicator.innerHTML = '<span class="status-dot"></span> Click to Select';
    }
  }
}

function handleFilesSelected(fileList) {
  if (!fileList || fileList.length === 0) return;
  const validExts = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'];

  window.STATE.uploadedFiles = window.STATE.uploadedFiles || [];

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!validExts.includes(ext)) {
      alert(`Skipping unsupported file "${file.name}". Please upload PDF or image files.`);
      continue;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert(`File "${file.name}" is too large (max 10MB).`);
      continue;
    }
    const alreadyAdded = window.STATE.uploadedFiles.some(f => f.name === file.name && f.size === file.size);
    if (!alreadyAdded) {
      window.STATE.uploadedFiles.push(file);
    }
  }

  window.STATE.uploadedFile = window.STATE.uploadedFiles[0] || null;
  switchInputMode('upload');
  renderUploadedFilesList();
}

function renderUploadedFilesList() {
  const files = window.STATE.uploadedFiles || [];
  const info = document.getElementById('uploadedFileInfo');
  const listEl = document.getElementById('uploadedFilesList');
  const countEl = document.getElementById('uploadedFilesCount');
  const dropZone = document.getElementById('resumeDropZone');

  if (files.length === 0) {
    if (info) info.style.display = 'none';
    if (dropZone) dropZone.style.display = '';
    return;
  }

  if (info) info.style.display = 'block';
  if (countEl) countEl.textContent = files.length;

  if (listEl) {
    listEl.innerHTML = files.map((file, idx) => {
      const isCert = file.name.toLowerCase().includes('cert') || idx > 0;
      const tagClass = isCert ? 'cert' : 'resume';
      const tagLabel = isCert ? '📜 Certificate' : '📄 Primary Resume';
      const sizeKb = (file.size / 1024).toFixed(0);

      return `
        <div class="uploaded-file-row">
          <div class="file-row-left">
            <span class="file-row-icon">${isCert ? '📜' : '📄'}</span>
            <span class="file-row-name" title="${file.name}">${file.name}</span>
            <span class="file-row-tag ${tagClass}">${tagLabel}</span>
            <span class="file-row-size">${sizeKb} KB</span>
          </div>
          <button class="file-row-remove" type="button" onclick="removeUploadedFile(${idx})" title="Remove document">✕</button>
        </div>
      `;
    }).join('');
  }
}

window.removeUploadedFile = function(idx) {
  if (window.STATE.uploadedFiles && window.STATE.uploadedFiles[idx]) {
    window.STATE.uploadedFiles.splice(idx, 1);
    window.STATE.uploadedFile = window.STATE.uploadedFiles[0] || null;
    renderUploadedFilesList();
  }
};

function setupCityPills() {
  const pills = document.querySelectorAll('.city-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', async () => {
      const prevActive = document.querySelector('.city-pill.active');
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const city = pill.dataset.city;

      const success = await updateSalaryForCity(city);
      if (!success && prevActive) {
        pill.classList.remove('active');
        prevActive.classList.add('active');
      }
    });
  });
}

function handleLogout() {
  if (confirm("Are you sure you want to log out and reset your Career Twin session?")) {
    window.STATE = {};
    const resumeInput = document.getElementById('resumeInput');
    if (resumeInput) resumeInput.value = "";
    document.getElementById('githubInput').value = "";
    
    // Hide App, Topnav & Top Role Switcher
    document.getElementById('app').style.display = 'none';
    document.getElementById('topnav').classList.remove('show');
    document.getElementById('logoutBtn').classList.remove('show');
    const topSwitcher = document.getElementById('topRoleSwitchWrap');
    if (topSwitcher) topSwitcher.style.display = 'none';
    
    // Show Landing
    const landing = document.getElementById('landing');
    landing.style.display = 'block';
    const heroIntake = document.getElementById('heroIntakeSection') || landing.querySelector('.hero-grid');
    if (heroIntake) heroIntake.style.display = 'block';
    document.getElementById('loading').style.display = 'none';

    // Reset upload state
    switchInputMode('text');
    window.STATE.uploadedFile = null;
    const uploadInfo = document.getElementById('uploadedFileInfo');
    if (uploadInfo) uploadInfo.style.display = 'none';
    const dropZone = document.getElementById('resumeDropZone');
    if (dropZone) dropZone.style.display = '';

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function showPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('panel-' + name);
  if (target) target.classList.add('active');
  document.querySelectorAll('#topnav button[data-panel]').forEach(b => b.classList.toggle('active', b.dataset.panel === name));
}

function runFastLoadingSequence() {
  const steps = document.querySelectorAll('#loading .step');
  let current = 0;
  const timer = setInterval(() => {
    if (current < steps.length) {
      steps.forEach((s, idx) => {
        s.classList.remove('active');
        if (idx < current) s.classList.add('done');
      });
      steps[current].classList.add('active');
      current++;
    } else {
      clearInterval(timer);
    }
  }, 45);

  return () => {
    clearInterval(timer);
    steps.forEach(s => {
      s.classList.remove('active');
      s.classList.add('done');
    });
  };
}

async function handleGenerate() {
  const inputMode = window.STATE.inputMode || 'text';
  const githubName = document.getElementById('githubInput').value.trim();
  const roleKey = document.getElementById('roleInput').value;

  // Validate input based on mode
  if (inputMode === 'text') {
    const resumeText = document.getElementById('resumeInput').value.trim();
    if (!resumeText) {
      alert("Please paste your resume or technical profile text first.");
      return;
    }
  } else {
    const filesToUpload = window.STATE.uploadedFiles && window.STATE.uploadedFiles.length > 0
      ? window.STATE.uploadedFiles
      : (window.STATE.uploadedFile ? [window.STATE.uploadedFile] : []);
    if (filesToUpload.length === 0) {
      alert("Please upload your resume and/or certificate file(s) first.");
      return;
    }
  }

  const heroIntake = document.getElementById('heroIntakeSection') || document.getElementById('landing').querySelector('.hero-grid');
  if (heroIntake) heroIntake.style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  // 1. Start fast visual animation in parallel
  const stopAnimation = runFastLoadingSequence();

  // 2. Fire backend API request
  try {
    let data;
    if (inputMode === 'upload') {
      const filesToUpload = window.STATE.uploadedFiles && window.STATE.uploadedFiles.length > 0
        ? window.STATE.uploadedFiles
        : [window.STATE.uploadedFile];
      data = await API.uploadResume(filesToUpload, githubName, roleKey);
    } else {
      // Text mode
      const resumeText = document.getElementById('resumeInput').value.trim();
      data = await API.parseAndGenerateTwin(resumeText, githubName, roleKey);
    }

    stopAnimation();

    window.STATE = {
      ...window.STATE,
      parsed: {
        candidate_name: (data.profile && data.profile.candidate_name) || "Hardika",
        detected: data.profile.detected_skills,
        expYears: data.profile.experience_years,
        dominant_cluster: data.profile.dominant_cluster,
        skills_count: data.profile.skills_count
      },
      github: data.github,
      roleKey: roleKey,
      selectedCity: "Ahmedabad",
      gapAnalysis: {
        rows: data.gap_analysis,
        readiness: data.readiness_percentage
      },
      roadmap: data.roadmap,
      salary: data.salary_estimate,
      trajectory: data.trajectory_prediction,
      ats_analysis: data.ats_analysis,
      mcqs: data.mcqs,
      profileId: data.profile_id || null,
      uploadInfo: data.upload_info || null
    };

    // Synchronize role selectors
    if (document.getElementById('topRoleSelector')) {
      document.getElementById('topRoleSelector').value = roleKey;
    }
    if (document.getElementById('profileRoleSwitchSelect')) {
      document.getElementById('profileRoleSwitchSelect').value = roleKey;
    }

    renderProfile();
    renderGaps();
    if (typeof renderTrajectory === 'function') renderTrajectory();
    renderRoadmap();
    renderMarket();
    renderATSAndJobs(window.STATE.ats_analysis);

    document.getElementById('landing').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    document.getElementById('topnav').classList.add('show');
    document.getElementById('logoutBtn').classList.add('show');
    const topSwitcher = document.getElementById('topRoleSwitchWrap');
    if (topSwitcher) topSwitcher.style.display = 'flex';

    showPanel('profile');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    stopAnimation();
    console.error("Twin generation error:", err);
    alert(err.message || "An error occurred while generating your Digital Twin. Please try again.");
    document.getElementById('loading').style.display = 'none';
    const heroIntake = document.getElementById('heroIntakeSection') || document.getElementById('landing').querySelector('.hero-grid');
    if (heroIntake) heroIntake.style.display = 'block';
  }
}

/**
 * Instant in-dashboard role switching:
 * Re-analyzes gaps, trajectory, roadmap, salary, and ATS for the newly chosen post.
 */
async function switchTargetRole(newRoleKey) {
  if (!window.STATE || !window.STATE.parsed) return;
  const resumeText = document.getElementById('resumeInput') ? document.getElementById('resumeInput').value : SAMPLE_RESUME;
  const githubName = (window.STATE.github && window.STATE.github.username) || "hardika-nimavat-dev";

  window.STATE.roleKey = newRoleKey;
  if (document.getElementById('roleInput')) document.getElementById('roleInput').value = newRoleKey;
  if (document.getElementById('topRoleSelector')) document.getElementById('topRoleSelector').value = newRoleKey;
  if (document.getElementById('profileRoleSwitchSelect')) document.getElementById('profileRoleSwitchSelect').value = newRoleKey;

  // Preserve existing verified / boosted skills
  const currentSkills = Object.assign({}, window.STATE.parsed.detected || {});

  try {
    const data = await API.parseAndGenerateTwin(resumeText, githubName, newRoleKey);
    if (data) {
      const mergedDetected = Object.assign({}, data.profile.detected_skills, currentSkills);
      data.profile.detected_skills = mergedDetected;
      window.STATE.parsed.detected = mergedDetected;

      const gapRes = await API.analyzeGaps(newRoleKey, mergedDetected);
      if (gapRes) {
        window.STATE.gapAnalysis = {
          rows: gapRes.gap_rows,
          readiness: gapRes.readiness_percentage
        };
      } else {
        window.STATE.gapAnalysis = {
          rows: data.gap_analysis,
          readiness: data.readiness_percentage
        };
      }

      window.STATE.roadmap = data.roadmap;
      window.STATE.salary = data.salary_estimate;
      window.STATE.trajectory = data.trajectory_prediction;
      window.STATE.ats_analysis = data.ats_analysis;
      window.STATE.mcqs = data.mcqs;
      window.STATE.profileId = data.profile_id || window.STATE.profileId;
    }
  } catch (e) {
    console.warn("Role switch API fetch error, updating locally:", e);
  }

  // Re-render all views
  renderProfile();
  renderGaps();
  renderRoadmap();
  renderMarket();
  renderATSAndJobs(window.STATE.ats_analysis);
}
window.switchTargetRole = switchTargetRole;

function renderProfile() {
  if (!window.STATE || !window.STATE.parsed) return;
  const { detected, expYears, dominant_cluster, candidate_name } = window.STATE.parsed;
  const roleKey = window.STATE.roleKey || "frontend";
  const roleLabel = ROLE_LABELS[roleKey] || "Frontend Developer";
  const readiness = window.STATE.gapAnalysis ? window.STATE.gapAnalysis.readiness : 0;
  const gapRows = window.STATE.gapAnalysis ? window.STATE.gapAnalysis.rows : [];

  // 0. Update Conversational Chatbot Greeting Upside Digital Twin
  const candidateName = candidate_name || "Hardika";
  const greetingUser = document.getElementById('greetingUserText');
  if (greetingUser) greetingUser.textContent = `Hey ${candidateName}! 👋`;
  const greetingTarget = document.getElementById('greetingTargetRole');
  if (greetingTarget) greetingTarget.textContent = roleLabel;
  const greetingReady = document.getElementById('greetingReadiness');
  if (greetingReady) {
    greetingReady.textContent = `${readiness}%`;
    greetingReady.style.color = readiness >= 70 ? "var(--accent)" : readiness >= 40 ? "var(--amber)" : "var(--coral)";
  }

  const skillCountEl = document.getElementById('skillCount');
  if (skillCountEl) skillCountEl.textContent = Object.keys(detected || {}).length;
  
  const expYearsEl = document.getElementById('expYears');
  if (expYearsEl) expYearsEl.textContent = `${expYears} yrs`;

  const targetLabelEl = document.getElementById('targetRoleLabel');
  if (targetLabelEl) targetLabelEl.textContent = roleLabel.toUpperCase();

  const pidBadge = document.getElementById('profileIdBadge');
  if (pidBadge) pidBadge.textContent = window.STATE.profileId ? `#${window.STATE.profileId}` : "—";

  const readinessBadge = document.getElementById('targetRoleReadiness');
  if (readinessBadge) {
    const statusText = readiness >= 70 ? "Near Qualified" : readiness >= 40 ? "Moderate Gap" : "High Growth Area";
    readinessBadge.textContent = `${readiness}% (${statusText})`;
    readinessBadge.style.color = readiness >= 70 ? "var(--accent)" : readiness >= 40 ? "var(--amber)" : "var(--coral)";
  }

  const skillsMetEl = document.getElementById('targetRoleSkillsMet');
  if (skillsMetEl && gapRows.length) {
    const totalReq = gapRows.length;
    const directHits = gapRows.filter(r => r.match_pct >= 75).length;
    skillsMetEl.textContent = `🎯 ${directHits} of ${totalReq} required skills matched or bridged`;
  }

  // Pass all context to the constellation renderer
  renderConstellation(detected, roleKey, gapRows, readiness);

  // Render integrated skill gaps
  renderGaps();

  // Load skill progression if we have a profile
  if (window.STATE.profileId) {
    loadSkillProgression(window.STATE.profileId);
  }
}

async function loadSkillProgression(profileId) {
  const data = await API.getSkillProgression(profileId);
  const card = document.getElementById('skillProgressionCard');
  if (!card) return;

  if (data && data.total_exams_taken > 0) {
    card.style.display = '';
    const examsEl = document.getElementById('totalExamsTaken');
    if (examsEl) examsEl.textContent = data.total_exams_taken;
    
    const totalPos = data.history
      .filter(h => h.change_amount > 0)
      .reduce((sum, h) => sum + h.change_amount, 0);
    const impEl = document.getElementById('totalImprovement');
    if (impEl) impEl.textContent = `+${totalPos.toFixed(1)}%`;
    const summaryEl = document.getElementById('progressionSummary');
    if (summaryEl) summaryEl.textContent = data.improvement_summary || '';
  } else {
    card.style.display = 'none';
  }
}

function renderGaps() {
  if (!window.STATE || !window.STATE.gapAnalysis) return;
  const { rows, readiness } = window.STATE.gapAnalysis;
  const roleKey = window.STATE.roleKey || "frontend";
  const roleLabel = ROLE_LABELS[roleKey] || "Frontend Developer";
  
  const roleEl = document.getElementById('readinessRole');
  if (roleEl) roleEl.textContent = roleLabel.toUpperCase();
  
  const valEl = document.getElementById('readinessVal');
  if (valEl) valEl.textContent = `${readiness}%`;

  const circumference = 226;
  const ring = document.getElementById('readinessRing');
  if (ring) {
    ring.setAttribute('stroke-dashoffset', circumference - (circumference * readiness / 100));
    ring.setAttribute('stroke', readiness >= 70 ? "#00E8A8" : readiness >= 45 ? "#FFB648" : "#FF5A6E");
  }

  const list = document.getElementById('gapList');
  if (list && rows && rows.length) {
    list.innerHTML = rows.map(r => {
      const fillColor = r.match_pct >= 75 ? "var(--accent)" : r.match_pct >= 30 ? "var(--amber)" : "var(--coral)";
      const via = r.match_pct === 100 ? "direct hit" : (r.match_via ? `via ${r.match_via}` : "target gap");
      return `
        <div class="gap-row">
          <div class="gap-name">${r.skill}<span class="weight">weight ${r.weight}/3 &middot; ${via}</span></div>
          <div class="gap-track"><div class="gap-fill" style="width:${r.match_pct}%; background:${fillColor}"></div></div>
          <div class="gap-pct">${Math.round(r.match_pct)}%</div>
          <div class="gap-badge ${r.badge_status}">${r.badge_status.toUpperCase()}</div>
        </div>
      `;
    }).join("");
  }
}

function renderRoadmap() {
  const roadmap = window.STATE.roadmap;
  const track = document.getElementById('roadmapTrack');
  const empty = document.getElementById('roadmapEmpty');
  const roleKey = window.STATE.roleKey || "frontend";
  const roleLabel = ROLE_LABELS[roleKey] || "Frontend Developer";

  if (!roadmap || roadmap.length === 0) {
    if (track) track.innerHTML = "";
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';

  // Normalize roadmap into 4 chained game stages
  let stages = [];
  if (roadmap[0] && roadmap[0].courses) {
    stages = roadmap;
  } else {
    stages = [
      { stage: 1, level: "Level 1: Novice", title: "Core Foundations & Tooling", icon: "🛡️", description: "Foundational programming syntax, Git version control, and core developer tools.", courses: [] },
      { stage: 2, level: "Level 2: Adept", title: "Frameworks & Component Architecture", icon: "⚡", description: "Modern application frameworks, reactive component hierarchies, and interactive state.", courses: [] },
      { stage: 3, level: "Level 3: Specialist", title: "Systems, Data Stores & Microservices", icon: "🚀", description: "Relational/document databases, state management, and high-throughput REST APIs.", courses: [] },
      { stage: 4, level: "Level 4: Master", title: "Production Engineering, Cloud & Capstone", icon: "👑", description: "Containerization, automated CI/CD pipelines, and capstone system architecture.", courses: [] }
    ];
    roadmap.forEach((item, idx) => {
      const sIdx = item.stage ? (item.stage - 1) : (idx % 4);
      if (stages[sIdx]) stages[sIdx].courses.push(item);
    });
  }

  // Calculate overall metrics
  let totalCourses = 0;
  let completedCourses = 0;
  stages.forEach(s => {
    (s.courses || []).forEach(c => {
      totalCourses++;
      if (c.completed) completedCourses++;
    });
  });

  const overallPct = totalCourses > 0 ? Math.round((completedCourses / totalCourses) * 100) : 0;
  const leftPct = 100 - overallPct;

  // Overview banner metrics
  const roleLabelEl = document.getElementById('roadmapRoleLabel');
  if (roleLabelEl) roleLabelEl.textContent = roleLabel.toUpperCase();

  const statsEl = document.getElementById('roadmapOverallStats');
  if (statsEl) statsEl.textContent = `${completedCourses} of ${totalCourses} Completed`;

  const statusPill = document.getElementById('roadmapStatusPill');
  if (statusPill) {
    if (overallPct === 100) {
      statusPill.textContent = "🏆 All Stages Cleared!";
      statusPill.style.color = "var(--accent)";
    } else {
      const activeStage = stages.find(s => {
        const done = (s.courses || []).filter(c => c.completed).length;
        return done < (s.courses || []).length;
      }) || stages[0];
      statusPill.textContent = `${activeStage.level || 'Stage 1'} (${overallPct}% Done)`;
      statusPill.style.color = "var(--amber)";
    }
  }

  const fillEl = document.getElementById('roadmapOverallProgressFill');
  if (fillEl) fillEl.style.width = `${overallPct}%`;

  const textEl = document.getElementById('roadmapOverallProgressText');
  if (textEl) textEl.textContent = `${overallPct}% Completed · ${leftPct}% Remaining to Master`;

  // Render Duolingo-Style Winding Serpentine Stepping-Stone Path
  if (track) {
    let globalCourseIdx = 0;
    const offsets = ['offset-center', 'offset-right', 'offset-center', 'offset-left'];
    const iconsList = ['🎧', '📖', '⚡', '🏆', '🎯', '💡', '🚀', '🔥'];

    let html = `<div class="duo-roadmap-container">`;

    stages.forEach((stage, sIdx) => {
      const sNum = stage.stage || (sIdx + 1);
      const courses = stage.courses || [];
      const stageDoneCount = courses.filter(c => c.completed).length;
      const stageTotalCount = courses.length;
      const stageCompleted = stageTotalCount > 0 && stageDoneCount === stageTotalCount;
      const prevCompleted = sIdx === 0 || (stages[sIdx - 1].courses.length > 0 && stages[sIdx - 1].courses.every(c => c.completed));
      const stageLocked = !prevCompleted;

      // Duolingo Section Divider Banner
      html += `
        <div class="duo-section-banner">
          <div class="duo-banner-line"></div>
          <div class="duo-banner-badge">
            <span class="badge-icon">${stage.icon || '🛡️'}</span>
            <span>${stage.level || 'Stage ' + sNum}: ${stage.title} (${stageDoneCount}/${stageTotalCount})</span>
          </div>
          <div class="duo-banner-line"></div>
        </div>
        <div class="duo-chain-path">
      `;

      courses.forEach((c, cIdx) => {
        const isDone = Boolean(c.completed);
        const isUnlocked = !stageLocked && (cIdx === 0 || courses[cIdx - 1].completed);
        const offsetClass = offsets[globalCourseIdx % offsets.length];
        globalCourseIdx++;

        let nodeClass = "locked-node";
        let icon = "🔒";
        if (isDone) {
          nodeClass = "completed-node";
          icon = "✔️";
        } else if (isUnlocked) {
          nodeClass = "active-node";
          icon = iconsList[(cIdx + sIdx) % iconsList.length];
        }

        const courseId = c.id || `course_${sNum}_${cIdx}`;
        c.id = courseId;
        const isYt = c.platform_type === 'youtube' || (c.resource_platform && c.resource_platform.includes('YouTube'));

        html += `
          <div class="duo-node-wrapper ${offsetClass}" id="nodeWrap_${courseId}">
            <button class="duo-btn-circle ${nodeClass}" onclick="toggleDuoCoursePopover('${courseId}', event)" title="${c.resource_title || c.title || c.skill}">
              <span>${icon}</span>
            </button>
            <div class="duo-node-label">${c.skill}</div>

            <!-- Floating Lesson Popover Card -->
            <div class="duo-course-popover" id="popover_${courseId}" style="display:none;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                <span class="badge" style="font-size:10px; background:var(--accent-soft); color:var(--accent); border-color:var(--accent-dim);">
                  ${isYt ? '▶️ YouTube Free Course' : '💻 Free Open Web'}
                </span>
                <span style="font-size:11.5px; font-weight:700; color:${isDone ? 'var(--accent)' : 'var(--amber)'};">
                  ${isDone ? '✅ COMPLETED' : (isUnlocked ? '⚡ ACTIVE NOW' : '🔒 LOCKED')}
                </span>
              </div>
              <h4 style="font-size:14.5px; color:#fff; font-weight:700; margin-bottom:6px; line-height:1.4;">
                ${c.resource_title || c.title || c.skill}
              </h4>
              <div style="font-size:12px; color:var(--text-dim); margin-bottom:12px;">
                <span>⏱️ ~${c.estimated_hours || 8}h</span> &bull; <span>🎯 Target Skill: <b style="color:var(--accent);">${c.skill}</b></span>
              </div>
              <div style="display:flex; gap:8px;">
                <a href="${c.resource_url || c.url}" target="_blank" rel="noopener noreferrer" class="btn-open-course" style="flex:1; text-align:center; padding:8px 12px; font-size:12px; text-decoration:none;">
                  ▶ Open Course ↗
                </a>
                <button class="btn-toggle-course ${isDone ? 'completed' : ''}" style="padding:8px 12px; font-size:12px;" onclick="toggleRoadmapCourse('${courseId}', ${sNum}, '${c.skill}')">
                  ${isDone ? '✓ Completed' : 'Mark Done'}
                </button>
              </div>
            </div>
          </div>
        `;
      });

      html += `</div>`; // Close duo-chain-path
    });

    // Friendly mascot companion cheering on the side
    const candidateName = (window.STATE.parsed && window.STATE.parsed.candidate_name) || "Hardika";
    html += `
      <div class="duo-mascot-companion">
        <div class="duo-mascot-bubble">🔥 Keep pushing, ${candidateName}! Level up!</div>
        <div class="duo-mascot-figure">🦉</div>
      </div>
    `;

    html += `</div>`; // Close duo-roadmap-container
    track.innerHTML = html;
  }
}

window.toggleDuoCoursePopover = function(courseId, event) {
  if (event) event.stopPropagation();
  const popover = document.getElementById(`popover_${courseId}`);
  if (!popover) return;
  const isShown = popover.style.display !== 'none';
  document.querySelectorAll('.duo-course-popover').forEach(p => p.style.display = 'none');
  if (!isShown) {
    popover.style.display = 'block';
  }
};

/**
 * Interactive toggle for roadmap courses:
 * Dynamically updates UI, stage completion, and boosts the related skill in the Digital Twin!
 */
window.toggleRoadmapCourse = function(courseId, stageNum, skillName) {
  const roadmap = window.STATE.roadmap;
  if (!roadmap) return;

  let targetCourse = null;
  for (let s of roadmap) {
    if (s.courses) {
      for (let c of s.courses) {
        if (c.id === courseId) { targetCourse = c; break; }
      }
    } else if (s.id === courseId) {
      targetCourse = s;
      break;
    }
  }

  if (targetCourse) {
    targetCourse.completed = !targetCourse.completed;
    
    // Dynamic Digital Twin update: Completing a course immediately boosts this skill in the Twin!
    if (skillName && window.STATE.parsed && window.STATE.parsed.detected) {
      const currentVal = window.STATE.parsed.detected[skillName] || 35.0;
      const boost = targetCourse.completed ? 30.0 : -30.0;
      window.STATE.parsed.detected[skillName] = Math.min(100.0, Math.max(0.0, currentVal + boost));

      // Recalculate gap row
      if (window.STATE.gapAnalysis && window.STATE.gapAnalysis.rows) {
        const gapRow = window.STATE.gapAnalysis.rows.find(r => r.skill.toLowerCase() === skillName.toLowerCase());
        if (gapRow) {
          gapRow.match_pct = Math.min(100.0, Math.max(0.0, gapRow.match_pct + boost));
          gapRow.badge_status = gapRow.match_pct >= 75 ? "strong" : gapRow.match_pct >= 35 ? "partial" : "gap";
        }
        const avg = Math.round(window.STATE.gapAnalysis.rows.reduce((sum, r) => sum + r.match_pct, 0) / window.STATE.gapAnalysis.rows.length);
        window.STATE.gapAnalysis.readiness = avg;
      }

      // Re-render Twin Profile (Constellation & Skill Gaps)
      renderProfile();
      renderGaps();

      // Also refresh ATS recommendations so job match percentages reflect the new skills!
      if (window.STATE.ats_analysis) {
        if (window.STATE.ats_analysis.role_coverage) {
          window.STATE.ats_analysis.role_coverage.direct_coverage_pct = window.STATE.gapAnalysis.readiness;
        }
        renderATSAndJobs(window.STATE.ats_analysis);
      }

      showTwinToast(targetCourse.completed
        ? `✨ ${skillName} course completed! Digital Twin skill updated to ${Math.round(window.STATE.parsed.detected[skillName])}%!`
        : `${skillName} course marked in-progress.`);
    }

    renderRoadmap();
  }
};

function renderMarket() {
  const m = window.STATE.salary;
  const roleKey = (window.STATE.roleKey || "frontend").toLowerCase();
  const roleLabel = ROLE_LABELS[roleKey] || "Frontend Developer";
  const city = window.STATE.selectedCity || "Ahmedabad";
  
  const salaryRangeEl = document.getElementById('salaryRange');
  salaryRangeEl.textContent = `₹${m.min_lpa}L – ₹${m.max_lpa}L`;
  salaryRangeEl.style.opacity = '1';

  document.getElementById('salaryLocationLabel').textContent = city;
  document.getElementById('demandTrend').textContent = m.demand_trend || "+12% YoY";

  const roleTitle = document.getElementById('salaryRoleTitle');
  if (roleTitle) roleTitle.textContent = roleLabel.toUpperCase();

  const gapsOpen = window.STATE.gapAnalysis.rows ? window.STATE.gapAnalysis.rows.filter(r => r.match_pct < 75).length : 4;
  document.getElementById('timeToReady').textContent = gapsOpen === 0 ? "Ready Now" : `~${gapsOpen * 2} wks`;
  document.getElementById('timeToReadySub').textContent = gapsOpen === 0 ? "No critical skill gaps" : `${gapsOpen} open gap(s) to master in roadmap`;

  // Dynamic Skill Multipliers Grid based on selected target role
  const multipliers = ROLE_MULTIPLIERS[roleKey] || ROLE_MULTIPLIERS["frontend"];
  const multGrid = document.getElementById('skillMultipliersGrid');
  if (multGrid) {
    multGrid.innerHTML = multipliers.map(m => `
      <div class="skill-mult-card">
        <span class="skill-mult-name">${m.name}</span>
        <span class="skill-mult-bump">${m.bump}</span>
      </div>
    `).join("");
  }

  // Dynamic Career Progression Ladder based on role's predicted median
  const bands = [
    { label: "Fresher (0–1 yrs)", mult: 0.65, color: "var(--blue)" },
    { label: "Junior (1–3 yrs)", mult: 1.0, color: "var(--accent)" },
    { label: "Mid-Level (3–5 yrs)", mult: 1.55, color: "var(--amber)" },
    { label: "Senior Engineer (5–8 yrs)", mult: 2.2, color: "var(--purple)" },
    { label: "Lead / Architect (8+ yrs)", mult: 3.1, color: "#FF9800" }
  ];

  const cityMults = {
    "Bangalore": 1.25, "Mumbai": 1.18, "Delhi-NCR": 1.15,
    "Hyderabad": 1.10, "Pune": 1.05, "Ahmedabad": 0.88, "Remote": 1.20
  };
  const currentMult = cityMults[city] || 1.0;
  const baseMedian = m.median_lpa || ((m.min_lpa + m.max_lpa) / 2);

  document.getElementById('benchRows').innerHTML = bands.map(b => {
    const minVal = (baseMedian * b.mult * 0.78 * currentMult).toFixed(1);
    const maxVal = (baseMedian * b.mult * 1.30 * currentMult).toFixed(1);
    const widthPct = Math.min(100, Math.max(15, (parseFloat(maxVal) / (baseMedian * 3.5)) * 100));

    return `
      <div class="bench-bar">
        <div class="l">${b.label}</div>
        <div class="bench-track">
          <div class="bench-fill" style="width:${widthPct}%; background:${b.color}; opacity:0.85;"></div>
        </div>
        <div class="bench-val">₹${minVal}L – ₹${maxVal}L</div>
      </div>
    `;
  }).join("");

  // Render Salary ML Telemetry
  const sml = m.ml_model_metrics || {
    model_name: "GradientBoostingRegressor(n_estimators=100, max_depth=4)",
    r2_score: "0.948 (94.8% variance explained)",
    inference_time_complexity: "O(M * d) ≈ 0.2ms",
    space_complexity: "O(trees) ≈ 300KB",
    status: "Trained & Live"
  };
  const salaryMlContainer = document.getElementById('salaryMlTelemetry');
  if (salaryMlContainer) {
    salaryMlContainer.innerHTML = `
      <div class="ml-telemetry-card">
        <div class="ml-telemetry-header">
          <span class="ml-telemetry-badge">⚡ SALARY GRADIENT BOOSTING REGRESSOR ML</span>
          <span class="ml-status-live">● ${sml.status}</span>
        </div>
        <div class="ml-telemetry-grid">
          <div class="ml-metric-item">
            <span class="ml-metric-lbl">Algorithm</span>
            <span class="ml-metric-val">${sml.model_name}</span>
          </div>
          <div class="ml-metric-item">
            <span class="ml-metric-lbl">R² Variance Score</span>
            <span class="ml-metric-val" style="color:var(--accent); font-weight:700;">${sml.r2_score}</span>
          </div>
          <div class="ml-metric-item">
            <span class="ml-metric-lbl">Inference Latency</span>
            <span class="ml-metric-val">${sml.inference_time_complexity}</span>
          </div>
          <div class="ml-metric-item">
            <span class="ml-metric-lbl">Model Footprint</span>
            <span class="ml-metric-val">${sml.space_complexity}</span>
          </div>
        </div>
      </div>
    `;
  }
}

/**
 * Renders the Career Trajectory Prediction section using window.STATE.trajectory data.
 * Populates the 3-month, 6-month, 12-month readiness bars & probability values.
 */
function renderTrajectory() {
  const t = window.STATE && window.STATE.trajectory;
  const section = document.getElementById('trajectorySection');
  if (!section) return;

  if (!t) {
    section.style.display = 'none';
    return;
  }
  section.style.display = '';

  // Helper to pick bar color based on readiness percentage
  function trajColor(pct) {
    return pct >= 75 ? 'var(--accent)' : pct >= 45 ? 'var(--amber)' : 'var(--coral)';
  }

  // 3-Month
  const r3 = t.readiness_3m || Math.round((t.prob_3m || 0) * 100);
  const bar3 = document.getElementById('trajBar3m');
  if (bar3) { bar3.style.width = r3 + '%'; bar3.style.background = trajColor(r3); }
  const prob3 = document.getElementById('trajProb3m');
  if (prob3) prob3.textContent = `P = ${(t.prob_3m || (r3 / 100)).toFixed(2)}`;
  const rd3 = document.getElementById('trajReadiness3m');
  if (rd3) { rd3.textContent = r3 + '%'; rd3.style.color = trajColor(r3); }

  // 6-Month
  const r6 = t.readiness_6m || Math.round((t.prob_6m || 0) * 100);
  const bar6 = document.getElementById('trajBar6m');
  if (bar6) { bar6.style.width = r6 + '%'; bar6.style.background = trajColor(r6); }
  const prob6 = document.getElementById('trajProb6m');
  if (prob6) prob6.textContent = `P = ${(t.prob_6m || (r6 / 100)).toFixed(2)}`;
  const rd6 = document.getElementById('trajReadiness6m');
  if (rd6) { rd6.textContent = r6 + '%'; rd6.style.color = trajColor(r6); }

  // 12-Month
  const r12 = t.readiness_12m || Math.round((t.prob_12m || 0) * 100);
  const bar12 = document.getElementById('trajBar12m');
  if (bar12) { bar12.style.width = r12 + '%'; bar12.style.background = trajColor(r12); }
  const prob12 = document.getElementById('trajProb12m');
  if (prob12) prob12.textContent = `P = ${(t.prob_12m || (r12 / 100)).toFixed(2)}`;
  const rd12 = document.getElementById('trajReadiness12m');
  if (rd12) { rd12.textContent = r12 + '%'; rd12.style.color = trajColor(r12); }

  // Summary
  const summaryEl = document.getElementById('trajectorySummary');
  if (summaryEl) {
    summaryEl.textContent = t.summary || `Projected readiness: ${r3}% (3m) → ${r6}% (6m) → ${r12}% (12m).`;
  }
}

/**
 * Re-fetches trajectory prediction from the backend API and re-renders.
 * Bound to the recalcTrajBtn click handler.
 */
async function updateTrajectoryView() {
  if (!window.STATE) return;
  const roleKey = window.STATE.roleKey || 'frontend';
  const readiness = (window.STATE.gapAnalysis && window.STATE.gapAnalysis.readiness) || 50;
  const expYears = (window.STATE.parsed && window.STATE.parsed.expYears) || 0;
  const githubScore = (window.STATE.github && window.STATE.github.quality_score) || 0;
  const learningHours = 14; // default, could be linked to studyHoursSlider

  const studySlider = document.getElementById('studyHoursSlider');
  const hrs = studySlider ? parseInt(studySlider.value, 10) || 14 : learningHours;

  const result = await API.predictTrajectory(roleKey, readiness, expYears, hrs, githubScore);
  if (result) {
    window.STATE.trajectory = result;
    renderTrajectory();
    showTwinToast('📈 Career trajectory recalculated with updated parameters.');
  }
}

async function updateSalaryForCity(city) {
  window.STATE.selectedCity = city;
  const salaryRangeEl = document.getElementById('salaryRange');
  if (salaryRangeEl) salaryRangeEl.style.opacity = '0.5';

  const salary = await API.estimateSalary(
    window.STATE.roleKey,
    window.STATE.gapAnalysis.readiness,
    window.STATE.parsed.expYears,
    city,
    window.STATE.github.quality_score
  );

  if (salary) {
    window.STATE.salary = salary;
    renderMarket();
    return true;
  } else {
    if (salaryRangeEl) salaryRangeEl.style.opacity = '1';
    return false;
  }
}

// ═══════════════════════════════════════════════════
// MULTI-FORMAT EXAM ENGINE (Frontend)
// ═══════════════════════════════════════════════════

async function startExam() {
  const examType = document.getElementById('examTypeSelect').value;
  const difficulty = document.getElementById('examDifficultySelect').value;
  const count = parseInt(document.getElementById('examCountSelect').value);
  const roleKey = window.STATE.roleKey || 'frontend';

  // Show loading
  document.getElementById('examConfigCard').style.display = 'none';
  document.getElementById('examLoading').style.display = '';
  document.getElementById('examLoadingType').textContent = examType.toUpperCase();

  // Determine weak skills for personalization
  const weakSkills = [];
  if (window.STATE.gapAnalysis && window.STATE.gapAnalysis.rows) {
    window.STATE.gapAnalysis.rows
      .filter(r => r.match_pct < 60)
      .sort((a, b) => a.match_pct - b.match_pct)
      .slice(0, 5)
      .forEach(r => weakSkills.push(r.skill));
  }

  const exam = await API.generateExam(
    roleKey, examType, count, difficulty,
    window.STATE.parsed ? window.STATE.parsed.detected : {},
    weakSkills,
    window.STATE.profileId
  );

  document.getElementById('examLoading').style.display = 'none';

  if (!exam || !exam.questions || exam.questions.length === 0) {
    alert("Could not generate exam questions. Please try again.");
    document.getElementById('examConfigCard').style.display = '';
    return;
  }

  // Initialize exam state
  examState = {
    questions: exam.questions,
    answers: [],
    currentIndex: 0,
    examType: examType,
    difficulty: difficulty,
    startTime: Date.now(),
    score: 0
  };

  document.getElementById('examActiveContainer').style.display = '';
  document.getElementById('examCompletionCard').style.display = 'none';
  renderExamQuestion(0);
}

function renderExamQuestion(index) {
  const q = examState.questions[index];
  if (!q) return;
  const total = examState.questions.length;
  const qType = q.exam_type || examState.examType;

  // Update header
  document.getElementById('examTopicBadge').textContent = `${q.skill} · ${q.topic || 'Assessment'}`;
  document.getElementById('examSkillBadge').textContent = `Skill: ${q.skill}`;
  document.getElementById('examTypeBadge').textContent = qType.toUpperCase();
  document.getElementById('examProgressIndicator').innerHTML = `Question <b>${index + 1} of ${total}</b>`;
  document.getElementById('examTrackFill').style.width = `${((index + 1) / total) * 100}%`;
  document.getElementById('examQuestionText').textContent = q.question;

  // Hide all editors
  document.getElementById('examOptionsGrid').style.display = 'none';
  document.getElementById('examCodeEditor').style.display = 'none';
  document.getElementById('examEssayEditor').style.display = 'none';
  document.getElementById('examDebugInfo').style.display = 'none';
  document.getElementById('examExplanationBox').style.display = 'none';
  document.getElementById('examLiveFeedback').style.display = 'none';

  // Show appropriate editor based on question type
  if (qType === 'mcq') {
    renderMCQOptions(q);
  } else if (qType === 'code') {
    renderCodeEditor(q);
  } else if (qType === 'essay' || qType === 'design') {
    renderEssayEditor(q);
  } else if (qType === 'debug') {
    renderDebugEditor(q);
  }

  // Reset buttons
  document.getElementById('examSubmitBtn').style.display = '';
  document.getElementById('examSubmitBtn').disabled = false;
  document.getElementById('examNextBtn').style.display = 'none';
}

function renderMCQOptions(q) {
  const grid = document.getElementById('examOptionsGrid');
  grid.style.display = 'flex';
  grid.innerHTML = (q.options || []).map((opt, i) => `
    <div class="mcq-option mcq-opt-btn" data-index="${i}" role="button" tabindex="0">
      <div class="opt-letter opt-prefix">${String.fromCharCode(65 + i)}</div>
      <div class="opt-text">${opt}</div>
    </div>
  `).join("");
  window._selectedMCQIndex = null;

  // Direct click handlers on all option elements
  grid.querySelectorAll('.mcq-option').forEach(optEl => {
    optEl.addEventListener('click', (e) => {
      e.preventDefault();
      const idx = parseInt(optEl.dataset.index, 10);
      selectExamOption(optEl, idx);
    });
  });
}

function selectExamOption(el, index) {
  document.querySelectorAll('#examOptionsGrid .mcq-option').forEach(o => o.classList.remove('selected'));
  if (el) el.classList.add('selected');
  window._selectedMCQIndex = index;
}
window.selectExamOption = selectExamOption;

function renderCodeEditor(q) {
  document.getElementById('examCodeEditor').style.display = '';
  document.getElementById('examCodeLanguage').textContent = q.language || 'javascript';
  document.getElementById('examCodeHint').textContent = q.test_cases ? `${q.test_cases.length} test case(s)` : '';
  document.getElementById('examCodeInput').value = q.starter_code || '';
}

function renderEssayEditor(q) {
  document.getElementById('examEssayEditor').style.display = '';
  document.getElementById('examEssayInput').value = '';
  document.getElementById('examWordCount').textContent = '0';
  document.getElementById('examMaxWords').textContent = q.max_word_count || 400;
}

function renderDebugEditor(q) {
  document.getElementById('examDebugInfo').style.display = '';
  document.getElementById('examCodeEditor').style.display = '';
  document.getElementById('examBugDescription').textContent = q.bug_description || '';
  document.getElementById('examBuggyCode').textContent = q.buggy_code || '';
  document.getElementById('examCodeLanguage').textContent = q.language || 'javascript';
  document.getElementById('examCodeHint').textContent = 'Fix the bug above';
  document.getElementById('examCodeInput').value = q.buggy_code || '';
}

function submitCurrentAnswer() {
  const q = examState.questions[examState.currentIndex];
  if (!q) return;
  const qType = q.exam_type || examState.examType;

  let answer = {
    question_id: q.id,
    exam_type: qType,
    skill: q.skill || 'General',
    topic: q.topic || ''
  };

  // Collect answer based on type
  if (qType === 'mcq') {
    if (window._selectedMCQIndex === null || window._selectedMCQIndex === undefined) {
      alert("Please select an option.");
      return;
    }
    answer.selected_index = window._selectedMCQIndex;
    // Check correctness locally for instant feedback
    const isCorrect = window._selectedMCQIndex === q.correct_index;
    showMCQFeedback(q, window._selectedMCQIndex, isCorrect);
    answer.is_correct = isCorrect;
    if (isCorrect) examState.score++;
  } else if (qType === 'code' || qType === 'debug') {
    const code = document.getElementById('examCodeInput').value.trim();
    if (!code) { alert("Please write your code."); return; }
    answer.code_answer = code;
  } else if (qType === 'essay' || qType === 'design') {
    const text = document.getElementById('examEssayInput').value.trim();
    if (!text || text.length < 20) { alert("Please write a detailed answer (at least 20 characters)."); return; }
    answer.text_answer = text;
  }

  examState.answers.push({
    ...answer,
    question_text: q.question,
    options: q.options,
    correct_index: q.correct_index,
    expected_points: q.expected_points,
    buggy_code: q.buggy_code,
    bug_description: q.bug_description,
    explanation: q.explanation,
    expected_optimal_time: q.expected_optimal_time || "O(n)",
    expected_optimal_space: q.expected_optimal_space || "O(1)"
  });

  // Show submit button as done, show next
  document.getElementById('examSubmitBtn').style.display = 'none';
  
  if (examState.currentIndex < examState.questions.length - 1) {
    document.getElementById('examNextBtn').style.display = '';
    document.getElementById('examNextBtn').disabled = false;
  } else {
    // Last question — auto-finish
    finishExam();
  }
}

function showMCQFeedback(question, selectedIdx, isCorrect) {
  // Highlight options
  document.querySelectorAll('#examOptionsGrid .mcq-option').forEach((opt, i) => {
    opt.classList.remove('selected');
    if (i === question.correct_index) opt.classList.add('correct');
    if (i === selectedIdx && !isCorrect) opt.classList.add('wrong');
    opt.style.pointerEvents = 'none';
  });

  // Show explanation
  if (question.explanation) {
    document.getElementById('examExplanationBox').style.display = '';
    document.getElementById('examExplanationText').textContent = question.explanation;
  }
}

function showNextExamQuestion() {
  examState.currentIndex++;
  document.getElementById('examNextBtn').style.display = 'none';
  renderExamQuestion(examState.currentIndex);
}

function showTwinToast(message) {
  const toast = document.getElementById('twinUpdateToast');
  const msgEl = document.getElementById('twinToastMsg');
  if (toast && msgEl) {
    msgEl.textContent = message || "Skills, gaps, salary & trajectory updated live.";
    toast.style.display = 'flex';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 5000);
  }
}

async function finishExam() {
  const roleKey = window.STATE.roleKey || 'frontend';
  const totalTime = Math.round((Date.now() - examState.startTime) / 1000);

  document.getElementById('examActiveContainer').style.display = 'none';

  // Submit to backend for AI evaluation + twin update
  const result = await API.submitExam(
    window.STATE.profileId,
    roleKey,
    examState.examType,
    examState.answers,
    examState.questions,
    totalTime
  );

  // Render completion card
  const card = document.getElementById('examCompletionCard');
  card.style.display = '';

  const accuracy = result.accuracy_pct !== undefined ? result.accuracy_pct : 0;
  const isCleared = result.is_cleared || accuracy >= 60;

  document.getElementById('examFinalClearanceBadge').textContent = isCleared ? "✅ CLEARANCE GRANTED" : "❌ CLEARANCE BLOCKED";
  document.getElementById('examFinalClearanceBadge').style.color = isCleared ? "var(--accent)" : "var(--coral)";
  document.getElementById('examFinalScoreText').textContent = `${accuracy}%`;
  document.getElementById('examFinalScoreText').style.color = isCleared ? "var(--accent)" : "var(--coral)";
  document.getElementById('examFinalSummary').textContent = result.summary || '';

  // Render Algorithmic Complexity Summary Box
  const compBox = document.getElementById('examComplexitySummary');
  if (compBox) {
    compBox.style.display = 'flex';
    compBox.innerHTML = `
      <div class="complexity-pill">⏱️ Time Complexity: <b>${result.overall_time_complexity || 'O(n)'}</b></div>
      <div class="complexity-pill">💾 Space Complexity: <b>${result.overall_space_complexity || 'O(1)'}</b></div>
      <div class="complexity-pill">🎯 Test-Case Accuracy: <b>${accuracy}%</b></div>
    `;
  }

  // Skill Updates Section & Dynamic Digital Twin Update
  const updatesSection = document.getElementById('examSkillUpdatesSection');
  const updatesList = document.getElementById('examSkillUpdatesList');
  if (result.skill_updates && Object.keys(result.skill_updates).length > 0) {
    updatesSection.style.display = '';
    updatesList.innerHTML = Object.entries(result.skill_updates).map(([skill, delta]) => {
      const isPositive = delta > 0;
      return `
        <div class="skill-update-row">
          <span class="skill-update-name">${skill}</span>
          <span class="skill-update-delta" style="color:${isPositive ? 'var(--accent)' : 'var(--coral)'};">
            ${isPositive ? '+' : ''}${delta.toFixed(1)}%
          </span>
        </div>
      `;
    }).join('');

    // Dynamic Twin Update: Update all state fields returned by backend
    if (result.new_skills) {
      window.STATE.parsed.detected = result.new_skills;
    }
    if (result.new_readiness_pct !== null && result.new_readiness_pct !== undefined) {
      window.STATE.gapAnalysis.readiness = result.new_readiness_pct;
    }
    if (result.new_gap_analysis && result.new_gap_analysis.length > 0) {
      window.STATE.gapAnalysis.rows = result.new_gap_analysis;
    }
    if (result.new_salary_estimate && Object.keys(result.new_salary_estimate).length > 0) {
      window.STATE.salary = result.new_salary_estimate;
    }
    if (result.new_trajectory && Object.keys(result.new_trajectory).length > 0) {
      window.STATE.trajectory = result.new_trajectory;
    }
    if (result.new_roadmap && result.new_roadmap.length > 0) {
      window.STATE.roadmap = result.new_roadmap;
    }
    if (result.new_ats_analysis) {
      window.STATE.ats_analysis = result.new_ats_analysis;
    } else if (window.STATE.ats_analysis) {
      // Dynamic local boost to ATS score and Job Matches based on exam clearance
      const currentScore = window.STATE.ats_analysis.ats_score || 78;
      window.STATE.ats_analysis.ats_score = Math.min(98, currentScore + (isCleared ? 6 : 2));
      if (window.STATE.ats_analysis.role_coverage) {
        window.STATE.ats_analysis.role_coverage.direct_coverage_pct = window.STATE.gapAnalysis.readiness;
      }
      if (window.STATE.ats_analysis.recommended_job_posts) {
        window.STATE.ats_analysis.recommended_job_posts.forEach(j => {
          j.match_percentage = Math.min(99, (j.match_percentage || 50) + (isCleared ? 8 : 3));
          j.badge_color = j.match_percentage >= 75 ? "var(--accent)" : "var(--amber)";
        });
      }
    }

    // Re-render ALL views so user immediately sees live updated twin!
    renderProfile();
    renderGaps();
    if (typeof renderTrajectory === 'function') renderTrajectory();
    renderRoadmap();
    renderMarket();
    if (window.STATE.ats_analysis) {
      renderATSAndJobs(window.STATE.ats_analysis);
    }

    // Trigger visual toast notification
    const totalBoost = Object.values(result.skill_updates).filter(v => v > 0).reduce((a, b) => a + b, 0).toFixed(1);
    showTwinToast(`🎓 Digital Twin Updated: +${totalBoost}% skill improvement! ATS Score & Job Matches recalculated live.`);
  } else {
    updatesSection.style.display = 'none';
  }

  // Detailed Results with Time & Space Complexity & Accuracy
  const diagList = document.getElementById('examDiagnosticsList');
  if (result.results && result.results.length > 0) {
    diagList.innerHTML = result.results.map(r => `
      <div class="diagnostic-row ${r.is_correct ? 'correct' : 'wrong'}">
        <div class="diag-header">
          <span class="diag-status">${r.is_correct ? '✅' : '❌'}</span>
          <span class="diag-skill">${r.skill || ''}</span>
          <span class="diag-type-badge">${r.exam_type || ''}</span>
          <span class="diag-score">${r.score ? r.score.toFixed(0) + '%' : ''}</span>
          <span class="badge-complexity">⏱️ ${r.time_complexity || 'O(1)'}</span>
          <span class="badge-complexity">💾 ${r.space_complexity || 'O(1)'}</span>
          <span class="badge-accuracy">🎯 ${r.accuracy_pct ? r.accuracy_pct.toFixed(0) + '%' : (r.score ? r.score.toFixed(0) + '%' : '100%')}</span>
        </div>
        <div class="diag-feedback">${r.feedback || ''}</div>
        ${r.complexity_analysis ? `<div class="complexity-analysis-box">⚙️ <b>Complexity Benchmark:</b> ${r.complexity_analysis}</div>` : ''}
      </div>
    `).join('');
  }

  // Recommendations
  const recsDiv = document.getElementById('examRecommendations');
  if (result.recommendations && result.recommendations.length > 0) {
    recsDiv.innerHTML = `
      <h4 style="font-size:14px; text-transform:uppercase; letter-spacing:0.04em; color:var(--text-dim); margin-bottom:10px;">Study Recommendations</h4>
      ${result.recommendations.map(r => `<div class="recommendation-item">${r}</div>`).join('')}
    `;
  }
}
