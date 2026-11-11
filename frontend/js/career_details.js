/**
 * Career Details Module: Comprehensive Career Role Inspection with Student Alignment.
 */

let activeRoleKey = 'data_scientist';

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const qRole = urlParams.get('role');
  if (qRole) activeRoleKey = qRole;

  await loadCareerDetails(activeRoleKey);
});

async function loadCareerDetails(roleKey) {
  const loading = document.getElementById('career-loading');
  const content = document.getElementById('career-content');

  if (loading) loading.style.display = 'block';
  if (content) content.style.display = 'none';

  try {
    const res = await fetch(`/api/career/${roleKey}`);
    const data = await res.json();

    if (loading) loading.style.display = 'none';

    if (data.status === 'success' && data.career) {
      if (content) content.style.display = 'block';
      renderCareerDetails(data.career, data.has_student_context);
    } else {
      showToast(data.message || 'Error loading career details', 'error');
    }
  } catch (err) {
    if (loading) loading.style.display = 'none';
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderCareerDetails(career, hasContext) {
  // Title & Basic Badges
  document.getElementById('cd-title').textContent = career.title;
  document.getElementById('cd-domain').textContent = career.domain;
  document.getElementById('cd-salary').textContent = career.average_salary;
  document.getElementById('cd-demand').textContent = `Market Demand: ${career.market_demand}`;
  document.getElementById('cd-difficulty').textContent = `Difficulty: ${career.learning_difficulty || 'Intermediate'}`;
  document.getElementById('cd-desc').textContent = career.description;

  // Match Score Badge
  const scoreElem = document.getElementById('cd-match-score');
  if (scoreElem) {
    if (hasContext && career.match_score) {
      scoreElem.textContent = `${career.match_score}% Match`;
      scoreElem.style.display = 'inline-flex';
    } else {
      scoreElem.textContent = 'Explore Role';
      scoreElem.style.display = 'inline-flex';
    }
  }

  // Suitability Explanation
  const whyElem = document.getElementById('cd-why-matches');
  if (whyElem) {
    whyElem.textContent = career.why_matches || 'Matches industry requirements based on standard engineering competencies.';
  }

  // Next steps
  const nextElem = document.getElementById('cd-next-steps');
  if (nextElem) {
    nextElem.textContent = career.next_steps || 'Launch your personalized learning roadmap to target missing competencies.';
  }

  // Matched Skills (Green)
  const matchedContainer = document.getElementById('cd-matched-skills');
  if (matchedContainer) {
    matchedContainer.innerHTML = '';
    const matched = career.matched_skills || [];
    if (matched.length === 0) {
      matchedContainer.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">None matched yet. Complete your profile to verify skills.</span>`;
    } else {
      matched.forEach(s => {
        const badge = document.createElement('span');
        badge.style.cssText = 'background: var(--success-light); border: 1px solid #a7f3d0; color: #047857; padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;';
        badge.innerHTML = `<i class="fas fa-check-circle"></i> ${s}`;
        matchedContainer.appendChild(badge);
      });
    }
  }

  // Missing Skills (Red)
  const missingContainer = document.getElementById('cd-missing-skills');
  if (missingContainer) {
    missingContainer.innerHTML = '';
    const missing = career.missing_skills || [];
    if (missing.length === 0) {
      missingContainer.innerHTML = `<span style="color: #047857; font-size: 0.85rem; font-weight: 600;"><i class="fas fa-check"></i> All primary requirements covered!</span>`;
    } else {
      missing.forEach(s => {
        const badge = document.createElement('span');
        badge.style.cssText = 'background: var(--danger-light); border: 1px solid #fecaca; color: #b91c1c; padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;';
        badge.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${s}`;
        missingContainer.appendChild(badge);
      });
    }
  }

  // Required Skills (All)
  const reqContainer = document.getElementById('cd-required-skills');
  if (reqContainer) {
    reqContainer.innerHTML = '';
    (career.required_skills || []).forEach(s => {
      const badge = document.createElement('span');
      badge.style.cssText = 'background: var(--light-blue-surface); border: 1px solid #bae6fd; color: #0369a1; padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; font-weight: 600;';
      badge.textContent = s;
      reqContainer.appendChild(badge);
    });
  }

  // Preferred Skills (All)
  const prefContainer = document.getElementById('cd-preferred-skills');
  if (prefContainer) {
    prefContainer.innerHTML = '';
    (career.preferred_skills || []).forEach(s => {
      const badge = document.createElement('span');
      badge.style.cssText = 'background: var(--light-yellow-surface); border: 1px solid #fde68a; color: var(--yellow-dark); padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; font-weight: 600;';
      badge.textContent = s;
      prefContainer.appendChild(badge);
    });
  }

  // Recommended Projects
  const projContainer = document.getElementById('cd-projects-list');
  if (projContainer) {
    projContainer.innerHTML = '';
    const projs = career.recommended_projects || [];
    projs.forEach((p, idx) => {
      const card = document.createElement('div');
      card.className = 'project-card';
      card.innerHTML = `
        <div class="project-title">
          <i class="fas fa-laptop-code"></i> Project ${idx + 1}: ${p.title}
        </div>
        <p class="project-desc">${p.description}</p>
        <div class="project-deliverable">
          <strong>Deliverable:</strong> ${p.deliverable}
        </div>
      `;
      projContainer.appendChild(card);
    });
  }

  // Learning Resources
  const resContainer = document.getElementById('cd-resources-list');
  if (resContainer) {
    resContainer.innerHTML = '';
    const resList = career.learning_resources || [];
    resList.forEach(r => {
      const link = document.createElement('a');
      link.href = r.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.className = `btn btn-sm ${r.type === 'YouTube' ? 'btn-outline' : 'btn-secondary'}`;
      link.innerHTML = `<i class="${r.type === 'YouTube' ? 'fab fa-youtube' : 'fas fa-book-open'}"></i> ${r.name}`;
      resContainer.appendChild(link);
    });
  }

  // Action Buttons
  const gapBtn = document.getElementById('btn-cd-gap');
  const roadmapBtn = document.getElementById('btn-cd-roadmap');
  if (gapBtn) gapBtn.href = `/skill-gap?role=${career.id}`;
  if (roadmapBtn) roadmapBtn.href = `/roadmap?role=${career.id}`;
}
