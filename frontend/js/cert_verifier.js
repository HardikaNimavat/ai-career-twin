/**
 * AI Career Twin — ATS Compatibility, Role Confidence, Job Matches & Certificate Verifier
 * 
 * Handles real-time ATS scoring updates, dynamic role coverage adjustments,
 * instant certificate verification, and cross-panel state synchronization.
 */

function renderATSAndJobs(atsData) {
  if (!atsData) return;

  const { ats_score, ats_rating, ats_breakdown, role_coverage, recommended_job_posts, verified_credentials, certificate_boost } = atsData;

  // 1. ATS Score Gauge & Rating
  const atsScoreVal = document.getElementById('atsScoreVal');
  const atsRatingBadge = document.getElementById('atsRatingBadge');
  const atsFmtScore = document.getElementById('atsFmtScore');
  const atsFmtFill = document.getElementById('atsFmtFill');
  const atsKeywordScore = document.getElementById('atsKeywordScore');
  const atsKeywordFill = document.getElementById('atsKeywordFill');
  const atsActionScore = document.getElementById('atsActionScore');
  const atsActionFill = document.getElementById('atsActionFill');
  const atsCertBadgeWrap = document.getElementById('atsCertificatesBadgeWrap');
  const atsCertBadgeText = document.getElementById('atsCertBadgeText');

  if (atsScoreVal) {
    atsScoreVal.textContent = ats_score;
    // Animate pulse
    atsScoreVal.style.transition = 'transform 0.2s ease';
    atsScoreVal.style.transform = 'scale(1.15)';
    setTimeout(() => { if (atsScoreVal) atsScoreVal.style.transform = 'scale(1)'; }, 250);
  }

  if (atsRatingBadge) {
    atsRatingBadge.textContent = ats_rating;
    atsRatingBadge.style.color = ats_score >= 80 ? "var(--accent)" : ats_score >= 65 ? "var(--blue)" : "var(--amber)";
    atsRatingBadge.style.borderColor = ats_score >= 80 ? "var(--accent-dim)" : "var(--border)";
    atsRatingBadge.style.background = ats_score >= 80 ? "var(--accent-soft)" : "rgba(255,255,255,0.05)";
  }

  if (ats_breakdown) {
    if (atsFmtScore) atsFmtScore.textContent = `${ats_breakdown.format_score}%`;
    if (atsFmtFill) atsFmtFill.style.width = `${ats_breakdown.format_score}%`;
    
    if (atsKeywordScore) atsKeywordScore.textContent = `${ats_breakdown.skill_density_score}%`;
    if (atsKeywordFill) atsKeywordFill.style.width = `${ats_breakdown.skill_density_score}%`;

    if (atsActionScore) atsActionScore.textContent = `${ats_breakdown.action_verbs_score}%`;
    if (atsActionFill) atsActionFill.style.width = `${ats_breakdown.action_verbs_score}%`;
  }

  // Certificate Boost Banner
  if (atsCertBadgeWrap) {
    const certs = verified_credentials || (window.STATE && window.STATE.verifiedCerts) || [];
    if (certs.length > 0) {
      atsCertBadgeWrap.style.display = 'flex';
      if (atsCertBadgeText) {
        atsCertBadgeText.textContent = `⭐ ${certs.length} Verified Credential(s) Active (+${certificate_boost || (certs.length * 6)} ATS Boost)`;
      }
    } else {
      atsCertBadgeWrap.style.display = 'none';
    }
  }

  // 2. Role Skill Coverage
  if (role_coverage) {
    const roleBadge = document.getElementById('atsRoleCoverageBadge');
    const covPct = document.getElementById('atsCoveragePct');
    const covSum = document.getElementById('atsCoverageSummaryText');
    const missingWrap = document.getElementById('atsMissingSkillsWrap');

    const roleName = (role_coverage.target_role || "FRONTEND").toUpperCase();
    if (roleBadge) roleBadge.textContent = roleName;
    
    if (covPct) {
      covPct.textContent = `${role_coverage.direct_coverage_pct}% Match`;
      covPct.style.color = role_coverage.direct_coverage_pct >= 65 ? "var(--accent)" : role_coverage.direct_coverage_pct >= 40 ? "var(--amber)" : "var(--coral)";
    }
    
    if (covSum) covSum.textContent = role_coverage.summary;

    if (missingWrap) {
      if (role_coverage.missing_skills && role_coverage.missing_skills.length > 0) {
        missingWrap.innerHTML = role_coverage.missing_skills.map(m => `
          <span class="missing-skill-pill">${m.skill} (w${m.weight})</span>
        `).join("");
      } else {
        missingWrap.innerHTML = `<span style="font-size:12.5px; color:var(--accent); font-weight:600;">✓ 100% Core Requirements Met!</span>`;
      }
    }
  }

  // 3. Recommended Related Job Posts with Interactive Filtering
  const jobsGrid = document.getElementById('jobPostsGrid');
  if (jobsGrid && recommended_job_posts) {
    window._currentJobPosts = recommended_job_posts;
    window._activeJobFilter = window._activeJobFilter || 'all';

    function renderFilteredJobs() {
      let filtered = window._currentJobPosts || [];
      if (window._activeJobFilter === 'high') {
        filtered = filtered.filter(j => (j.match_percentage || 0) >= 70);
      } else if (window._activeJobFilter === 'growth') {
        filtered = filtered.filter(j => (j.match_percentage || 0) < 70);
      }

      if (filtered.length === 0) {
        jobsGrid.innerHTML = `
          <div style="grid-column:1/-1; text-align:center; padding:30px; color:var(--text-dim);">
            No openings match the current filter. Try selecting "All Openings".
          </div>
        `;
        return;
      }

      jobsGrid.innerHTML = filtered.map(job => {
        const isRoadMatch = Boolean(job.is_selected_road);
        const matchPct = job.match_percentage || 50;
        const badgeColor = matchPct >= 75 ? "var(--accent)" : matchPct >= 50 ? "var(--amber)" : "var(--coral)";
        const badgeStatus = matchPct >= 75 ? "Qualified Match" : matchPct >= 50 ? "Good Fit" : "Growth Target";

        return `
          <div class="job-post-card ${isRoadMatch ? 'selected-road-job' : ''}">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; gap:8px;">
                <div>
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-size:11px; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-dim); font-weight:600;">${job.category || 'Tech'}</span>
                    ${isRoadMatch ? `<span class="badge" style="font-size:9.5px; padding:2px 7px; background:var(--accent-soft); color:var(--accent); border-color:var(--accent-dim);">🎯 TARGET POST</span>` : ''}
                  </div>
                  <h4 style="font-size:16px; color:var(--text); margin-top:4px; font-weight:700;">${job.title}</h4>
                </div>
                <span class="job-match-badge" style="color:${badgeColor}; border-color:${badgeColor}; background:rgba(0,0,0,0.3);">
                  ${matchPct}% Match &bull; ${badgeStatus}
                </span>
              </div>
              
              <div class="job-salary-meta" style="margin-bottom:10px;">
                <span style="font-weight:600; color:var(--text);">💰 ₹${job.avg_salary_lpa} LPA</span>
                <span>📍 ${job.experience_level || 'Entry-Level / Associate'}</span>
                <span>🏢 Tech Industry</span>
              </div>

              <p style="font-size:12.5px; color:var(--text-dim); line-height:1.5; margin-bottom:12px;">
                ${job.description}
              </p>

              <!-- Matched and Gap Skills -->
              <div class="job-skills-pill-wrap">
                ${(job.matched_skills || []).map(s => `
                  <span class="job-skill-tag matched">✓ ${s}</span>
                `).join('')}
                ${(job.missing_skills || []).map(s => `
                  <span class="job-skill-tag gap">⚡ ${s} needed</span>
                `).join('')}
              </div>
            </div>

            <button class="btn-job-apply" onclick="applyToJobRole('${job.title}', ${matchPct})">
              <span>🚀 Apply with Digital Twin Profile</span>
              <span>↗</span>
            </button>
          </div>
        `;
      }).join("");
    }

    renderFilteredJobs();

    // Setup filter pill listeners once
    document.querySelectorAll('#jobFilterPills .job-filter-pill').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('#jobFilterPills .job-filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        window._activeJobFilter = btn.dataset.filter;
        renderFilteredJobs();
      };
    });
  }
}

window.applyToJobRole = function(jobTitle, matchScore) {
  if (typeof showTwinToast === 'function') {
    showTwinToast(`🎉 Application submitted for "${jobTitle}" with ${matchScore}% Digital Twin match! Recruiter notified.`);
  } else {
    alert(`Application submitted for "${jobTitle}" with ${matchScore}% match!`);
  }
};

/**
 * Executes certificate verification pipeline and propagates updates across all twin models
 */
async function processCertificateVerification(filename) {
  const resultsContainer = document.getElementById('certResults');
  const targetRole = window.STATE ? (window.STATE.roleKey || "frontend") : "frontend";
  const currentSkills = (window.STATE && window.STATE.parsed) ? window.STATE.parsed.detected : {};
  const resumeText = document.getElementById('resumeInput') ? document.getElementById('resumeInput').value : "";
  const verifiedCerts = (window.STATE && window.STATE.verifiedCerts) ? window.STATE.verifiedCerts : [];

  // Call Backend API to verify certificate & recalculate ATS
  const resp = await API.verifyCertificate(filename, targetRole, currentSkills, resumeText, verifiedCerts);

  if (resultsContainer) {
    const row = document.createElement('div');
    if (resp && resp.verified) {
      row.className = 'cert-result match';
      row.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:2px;">
          <span class="fname">📄 ${filename}</span>
          <span style="font-size:11.5px; color:var(--text-dim);">Credential Level: <b>${resp.credential_level}</b></span>
        </div>
        <span class="verdict" style="color:var(--accent);">✓ Verified: ${resp.skill} (+${resp.score_boost}% proficiency &amp; +${resp.ats_boost_points} ATS Score)</span>
      `;
      resultsContainer.prepend(row);

      // Update state and resynchronize all panels
      if (window.STATE && window.STATE.parsed) {
        const skill = resp.skill;
        window.STATE.parsed.detected[skill] = Math.min(99.0, Math.max(88.0, (window.STATE.parsed.detected[skill] || 60.0) + resp.score_boost));
        window.STATE.parsed.skills_count = Object.keys(window.STATE.parsed.detected).length;
        window.STATE.verifiedCerts = resp.verified_certs || [...verifiedCerts, `${resp.skill} (${resp.credential_level})`];

        if (resp.updated_ats_analysis) {
          window.STATE.ats_analysis = resp.updated_ats_analysis;
        }

        // 1. Recalculate Gaps
        const gapRes = await API.analyzeGaps(window.STATE.roleKey, window.STATE.parsed.detected);
        if (gapRes) {
          window.STATE.gapAnalysis = {
            rows: gapRes.gap_rows,
            readiness: gapRes.readiness_percentage
          };

          // 2. Regenerate Roadmap
          const newRoadmap = await API.generateRoadmap(gapRes.gap_rows);
          if (newRoadmap) window.STATE.roadmap = newRoadmap;

          // 3. Re-estimate Salary
          const newSalary = await API.estimateSalary(
            window.STATE.roleKey,
            gapRes.readiness_percentage,
            window.STATE.parsed.expYears,
            window.STATE.selectedCity || "Ahmedabad",
            window.STATE.github.quality_score
          );
          if (newSalary) window.STATE.salary = newSalary;
        }

        // Re-render ALL Panels to stay in sync
        renderATSAndJobs(window.STATE.ats_analysis);
        renderProfile();
        renderGaps();
        renderRoadmap();
        renderMarket();
      }
    } else {
      row.className = 'cert-result nomatch';
      row.innerHTML = `<span class="fname">📄 ${filename}</span><span class="verdict" style="color:var(--coral);">No recognized technical skill keyword identified</span>`;
      resultsContainer.prepend(row);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const certInput = document.getElementById('certFile');

  if (certInput) {
    certInput.addEventListener('change', async (e) => {
      const files = Array.from(e.target.files);
      for (const file of files) {
        await processCertificateVerification(file.name);
      }
    });
  }

  // Preset One-Click Certificate Buttons
  document.querySelectorAll('.cert-preset-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const certName = btn.dataset.cert;
      if (certName) {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        await processCertificateVerification(certName);
        setTimeout(() => {
          btn.disabled = false;
          btn.style.opacity = '1';
        }, 600);
      }
    });
  });
});
