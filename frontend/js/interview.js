let interviewState = {
  mcqs: [],
  currentIndex: 0,
  userAnswers: [], // Array of { id, skill, topic, question, selected_index, is_correct, deficiency_diagnostic }
  isCompleted: false,
  score: 0,
  totalQuestions: 5
};

async function initInterview(role, forceNew = false, preloadedMCQs = null) {
  const roleKey = role || (window.STATE ? window.STATE.roleKey : "frontend");
  const detectedSkills = (window.STATE && window.STATE.parsed) ? window.STATE.parsed.detected : {};
  const resumeText = document.getElementById('resumeInput') ? document.getElementById('resumeInput').value : "";

  // Reset state
  interviewState.currentIndex = 0;
  interviewState.userAnswers = [];
  interviewState.isCompleted = false;
  interviewState.score = 0;

  // Show Active Quiz Container, Hide Completion Card
  const activeContainer = document.getElementById('mcqActiveContainer');
  const completionCard = document.getElementById('mcqCompletionCard');
  if (activeContainer) activeContainer.style.display = 'block';
  if (completionCard) completionCard.style.display = 'none';

  // Use preloaded MCQs if present
  if (!forceNew && preloadedMCQs && preloadedMCQs.length) {
    interviewState.mcqs = preloadedMCQs;
    interviewState.totalQuestions = preloadedMCQs.length;
    loadCurrentQuestion();
    return;
  }
  if (!forceNew && window.STATE && window.STATE.mcqs && window.STATE.mcqs.length) {
    interviewState.mcqs = window.STATE.mcqs;
    interviewState.totalQuestions = window.STATE.mcqs.length;
    loadCurrentQuestion();
    return;
  }

  const qText = document.getElementById('mcqQuestionText');
  if (qText) qText.textContent = "Generating dynamic scenario questions tailored to your resume...";

  // Fetch dynamic resume-tailored MCQs
  const mcqs = await API.generateDynamicMCQs(roleKey, detectedSkills, 5, resumeText);
  if (mcqs && mcqs.length) {
    interviewState.mcqs = mcqs;
    interviewState.totalQuestions = mcqs.length;
    if (window.STATE) window.STATE.mcqs = mcqs;
  }

  loadCurrentQuestion();
}

function loadCurrentQuestion() {
  if (!interviewState.mcqs || !interviewState.mcqs.length) return;
  
  if (interviewState.currentIndex >= interviewState.mcqs.length) {
    finishAssessment();
    return;
  }

  const q = interviewState.mcqs[interviewState.currentIndex];
  const total = interviewState.mcqs.length;
  const currentNum = interviewState.currentIndex + 1;

  // Elements
  const topicBadge = document.getElementById('mcqTopicBadge');
  const skillBadge = document.getElementById('mcqSkillBadge');
  const progressInd = document.getElementById('mcqProgressIndicator');
  const currentScoreEl = document.getElementById('mcqCurrentScore');
  const trackFill = document.getElementById('mcqTrackFill');
  const qText = document.getElementById('mcqQuestionText');
  const optsGrid = document.getElementById('mcqOptionsGrid');
  const expBox = document.getElementById('mcqExplanationBox');
  const liveDiag = document.getElementById('mcqLiveDiagnostic');
  const nextBtn = document.getElementById('mcqNextBtn');

  // Set Top Meta
  if (topicBadge) topicBadge.textContent = q.topic || "Core Technical Architecture";
  if (skillBadge) skillBadge.textContent = `Skill: ${q.skill || "Technical"}`;
  if (progressInd) {
    progressInd.innerHTML = `Challenge <b>${currentNum} of ${total}</b> &middot; Score: <b id="mcqCurrentScore">${interviewState.score}</b>/${total}`;
  }
  if (trackFill) {
    const pct = Math.round((currentNum / total) * 100);
    trackFill.style.width = `${pct}%`;
  }

  // Question Text
  if (qText) qText.textContent = q.question;

  // Hide explanation and diagnostic
  if (expBox) expBox.classList.remove('show');
  if (liveDiag) liveDiag.style.display = 'none';

  // Disable Next Button
  if (nextBtn) {
    nextBtn.disabled = true;
    nextBtn.textContent = (currentNum === total) ? "Finish Assessment & View Report →" : "Next Challenge →";
  }

  // Render 4 Options
  const prefixes = ["A", "B", "C", "D"];
  if (optsGrid) {
    optsGrid.innerHTML = q.options.map((opt, i) => `
      <button class="mcq-opt-btn" data-opt-idx="${i}">
        <span class="opt-prefix">${prefixes[i]}</span>
        <span>${opt}</span>
      </button>
    `).join("");

    optsGrid.querySelectorAll('.mcq-opt-btn').forEach(btn => {
      btn.addEventListener('click', () => handleOptionSelection(parseInt(btn.dataset.optIdx)));
    });
  }
}

function handleOptionSelection(selectedIdx) {
  const q = interviewState.mcqs[interviewState.currentIndex];
  const btns = document.querySelectorAll('.mcq-opt-btn');
  const expBox = document.getElementById('mcqExplanationBox');
  const expText = document.getElementById('mcqExplanationText');
  const liveDiag = document.getElementById('mcqLiveDiagnostic');
  const nextBtn = document.getElementById('mcqNextBtn');
  const progressInd = document.getElementById('mcqProgressIndicator');

  const isCorrect = selectedIdx === q.correct_index;
  if (isCorrect) interviewState.score += 1;

  // Save answer record
  interviewState.userAnswers.push({
    id: q.id,
    skill: q.skill || "Technical",
    topic: q.topic || "General Concept",
    question: q.question,
    selected_index: selectedIdx,
    is_correct: isCorrect,
    deficiency_diagnostic: q.deficiency_diagnostic || `Lacking foundational knowledge in ${q.skill || 'this technical domain'}.`
  });

  // Update option styling
  btns.forEach((b, i) => {
    b.disabled = true;
    if (i === q.correct_index) {
      b.classList.add('correct');
    } else if (i === selectedIdx && !isCorrect) {
      b.classList.add('wrong');
    }
  });

  // Show explanation
  if (expBox && expText) {
    expText.textContent = q.explanation;
    expBox.classList.add('show');
  }

  // Show instant diagnostic feedback
  if (liveDiag) {
    liveDiag.style.display = 'block';
    if (isCorrect) {
      liveDiag.className = 'card mcq-clearance-card cleared';
      liveDiag.innerHTML = `
        <div style="font-weight:600; color:var(--accent); font-size:13.5px; margin-bottom:4px;">
          ✅ Verified Concept: ${q.skill} (${q.topic})
        </div>
        <div style="font-size:12.5px; color:var(--text-dim);">
          Correct response. Your answer aligns with industry production engineering standards.
        </div>
      `;
    } else {
      liveDiag.className = 'card mcq-clearance-card pending';
      liveDiag.innerHTML = `
        <div style="font-weight:600; color:var(--coral); font-size:13.5px; margin-bottom:4px;">
          ⚠️ Skill Gap Detected: ${q.skill} (${q.topic})
        </div>
        <div style="font-size:12.5px; color:var(--text-dim);">
          ${q.deficiency_diagnostic || 'Review this concept in your learning roadmap.'}
        </div>
      `;
    }
  }

  // Update score indicator
  if (progressInd) {
    const total = interviewState.mcqs.length;
    progressInd.innerHTML = `Challenge <b>${interviewState.currentIndex + 1} of ${total}</b> &middot; Score: <b id="mcqCurrentScore">${interviewState.score}</b>/${total}`;
  }

  if (nextBtn) nextBtn.disabled = false;
}

async function finishAssessment() {
  interviewState.isCompleted = true;
  const roleKey = window.STATE ? window.STATE.roleKey : "frontend";

  // Hide active container, Show completion card
  const activeContainer = document.getElementById('mcqActiveContainer');
  const completionCard = document.getElementById('mcqCompletionCard');
  if (activeContainer) activeContainer.style.display = 'none';
  if (completionCard) completionCard.style.display = 'block';

  // Call Backend API to evaluate round & generate detailed skill diagnostics
  const report = await API.evaluateMCQSession(roleKey, interviewState.userAnswers);

  const badgeEl = document.getElementById('mcqFinalClearanceBadge');
  const scoreEl = document.getElementById('mcqFinalScoreText');
  const sumEl = document.getElementById('mcqFinalSummary');
  const listEl = document.getElementById('mcqDiagnosticsList');

  const isCleared = report.is_cleared;
  const accuracy = report.accuracy_pct;

  if (badgeEl) {
    badgeEl.textContent = isCleared ? "✅ TECHNICAL ASSESSMENT CLEARANCE: GRANTED" : "⚠️ TECHNICAL ASSESSMENT CLEARANCE: BLOCKED";
    badgeEl.style.color = isCleared ? "var(--accent)" : "var(--coral)";
    badgeEl.style.borderColor = isCleared ? "var(--accent-dim)" : "rgba(255,90,110,0.3)";
    badgeEl.style.background = isCleared ? "var(--accent-soft)" : "rgba(255,90,110,0.1)";
  }

  if (scoreEl) {
    scoreEl.textContent = `${accuracy}%`;
    scoreEl.style.color = isCleared ? "var(--accent)" : (accuracy >= 40 ? "var(--amber)" : "var(--coral)");
  }

  if (sumEl) {
    sumEl.innerHTML = `You answered <b>${report.correct_count} of ${report.total_questions}</b> questions correctly. ${report.summary}`;
  }

  // Render Skill-by-Skill Diagnostics
  if (listEl && report.diagnostics) {
    listEl.innerHTML = report.diagnostics.map(d => {
      const isC = d.is_correct;
      const statusColor = isC ? "var(--accent)" : "var(--coral)";
      const statusIcon = isC ? "🟢" : "🔴";
      const statusText = isC ? "COMPETENCY VALIDATED" : "LACKING SKILL / DEFICIENCY";

      return `
        <div class="diagnostic-item ${isC ? 'passed' : 'failed'}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;">
            <div style="font-weight:600; font-size:13.5px; color:var(--text);">
              ${statusIcon} ${d.skill} &middot; <span style="color:var(--text-dim);">${d.topic}</span>
            </div>
            <span class="diag-badge" style="color:${statusColor}; border-color:${statusColor};">${statusText}</span>
          </div>
          <div style="font-size:12.5px; color:var(--text-dim); line-height:1.5;">
            ${d.diagnostic_message}
          </div>
        </div>
      `;
    }).join("");
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const mcqNextBtn = document.getElementById('mcqNextBtn');
  const mcqRestartBtn = document.getElementById('mcqRestartBtn');
  const mcqRestartTopBtn = document.getElementById('mcqRestartTopBtn');
  const mcqGoRoadmapBtn = document.getElementById('mcqGoRoadmapBtn');

  if (mcqNextBtn) {
    mcqNextBtn.addEventListener('click', () => {
      interviewState.currentIndex += 1;
      if (interviewState.currentIndex < interviewState.mcqs.length) {
        loadCurrentQuestion();
      } else {
        finishAssessment();
      }
    });
  }

  if (mcqRestartBtn) {
    mcqRestartBtn.addEventListener('click', () => {
      initInterview(window.STATE ? window.STATE.roleKey : "frontend", true);
    });
  }

  if (mcqRestartTopBtn) {
    mcqRestartTopBtn.addEventListener('click', () => {
      if (confirm("Generate fresh dynamic questions based on your resume?")) {
        initInterview(window.STATE ? window.STATE.roleKey : "frontend", true);
      }
    });
  }

  if (mcqGoRoadmapBtn) {
    mcqGoRoadmapBtn.addEventListener('click', () => {
      showPanel('roadmap');
    });
  }
});
