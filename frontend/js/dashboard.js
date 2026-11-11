/**
 * Student Dashboard Module: Profile Summary, Top 3 Recommendations,
 * Skill Coverage Chart & Learning Progress Overview.
 */

let dashChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboardData();
});

async function loadDashboardData() {
  const loading = document.getElementById('dash-loading');
  const empty = document.getElementById('dash-empty');
  const content = document.getElementById('dash-content');

  try {
    const res = await fetch('/api/profile/current');
    const data = await res.json();

    if (loading) loading.style.display = 'none';

    if (data.status === 'success' && data.profile) {
      if (empty) empty.style.display = 'none';
      if (content) content.style.display = 'block';

      renderProfileSummary(data.profile);
      await loadRecommendationsAndProgress(data.profile);
    } else {
      if (empty) empty.style.display = 'block';
      if (content) content.style.display = 'none';
    }
  } catch (err) {
    if (loading) loading.style.display = 'none';
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderProfileSummary(profile) {
  document.getElementById('dash-student-name').textContent = profile.full_name;
  document.getElementById('dash-student-branch').textContent = profile.branch;
  document.getElementById('dash-student-college').textContent = profile.college_name || 'Not Specified';
  document.getElementById('dash-student-sem').textContent = `Semester ${profile.current_semester}`;
  document.getElementById('dash-student-grad').textContent = `Class of ${profile.graduation_year}`;
  document.getElementById('dash-student-pref').textContent = `${profile.preferred_work_area} • ${profile.preferred_career_type} • ${profile.hours_per_week} hrs/wk`;

  const allSkills = [
    ...(profile.programming_languages || []),
    ...(profile.frameworks || []),
    ...(profile.databases || []),
    ...(profile.tools_technologies || []),
    ...(profile.technical_skills || [])
  ];

  const skillsListElem = document.getElementById('dash-skills-chips');
  if (skillsListElem) {
    skillsListElem.innerHTML = '';
    const profs = profile.skill_proficiencies || {};
    allSkills.forEach(s => {
      const chip = document.createElement('span');
      chip.style.cssText = 'background: var(--light-blue-surface); border: 1px solid #bae6fd; color: #0369a1; padding: 3px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 600;';
      chip.textContent = `${s} (${profs[s] || 'Int'})`;
      skillsListElem.appendChild(chip);
    });
  }

  const interestsListElem = document.getElementById('dash-interests-chips');
  if (interestsListElem) {
    interestsListElem.innerHTML = '';
    (profile.interest_areas || []).forEach(i => {
      const chip = document.createElement('span');
      chip.style.cssText = 'background: var(--purple-light); border: 1px solid #e9d5ff; color: var(--purple-accent); padding: 3px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 700;';
      chip.textContent = i;
      interestsListElem.appendChild(chip);
    });
  }
}

async function loadRecommendationsAndProgress(profile) {
  try {
    const res = await fetch(`/api/recommendations/latest?student_id=${profile.id}`);
    const data = await res.json();
    if (data.status === 'success' && data.top_3 && data.top_3.length > 0) {
      const top3 = data.top_3;
      renderTop3CardsSnippet(top3);

      // Load skill gap for the #1 role to render skill coverage chart
      const primaryRole = top3[0];
      await loadSkillCoverageSnippet(profile.id, primaryRole.id);
      await loadRoadmapProgressSnippet(profile.id, primaryRole.id);
    }
  } catch (e) {
    console.warn('Could not load recommendation telemetry', e);
  }
}

function renderTop3CardsSnippet(top3) {
  const container = document.getElementById('dash-top3-grid');
  if (!container) return;
  container.innerHTML = '';

  top3.forEach((role, idx) => {
    const card = document.createElement('div');
    card.className = `career-card ${idx === 0 ? 'rank-1' : ''}`;
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
        <div>
          <span style="font-size: 0.78rem; font-weight: 800; color: ${idx === 0 ? 'var(--maroon)' : 'var(--text-muted)'}; text-transform: uppercase;">
            #${idx + 1} Recommendation
          </span>
          <h4 style="font-size: 1.25rem; font-weight: 800; color: var(--text-main); margin-top: 2px;">${role.title}</h4>
          <span class="career-domain">${role.domain}</span>
        </div>
        <div class="match-score-badge high" style="font-size: 1.5rem;">
          ${role.match_score}%
        </div>
      </div>

      <div style="margin-bottom: 0.75rem;">
        <span class="career-salary" style="font-size: 0.78rem;">
          <i class="fas fa-coins"></i> ${role.average_salary}
        </span>
      </div>

      <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.45; margin-bottom: 1rem; flex: 1;">
        ${role.description}
      </p>

      <div class="progress-container" style="margin-bottom: 1rem;">
        <div class="progress-fill" style="width: ${role.match_score}%;"></div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: auto;">
        <a href="/career-details?role=${role.id}" class="btn btn-sm btn-secondary" style="width: 100%;">
          <i class="fas fa-info-circle"></i> Details
        </a>
        <a href="/skill-gap?role=${role.id}" class="btn btn-sm btn-primary" style="width: 100%;">
          <i class="fas fa-puzzle-piece"></i> Skill Gap
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

async function loadSkillCoverageSnippet(studentId, roleId) {
  try {
    const res = await fetch(`/api/skill-gap/${roleId}?student_id=${studentId}`);
    const resData = await res.json();
    if (resData.status === 'success' && resData.data) {
      const summary = resData.data.summary;
      document.getElementById('dash-known-count').textContent = summary.known_count;
      document.getElementById('dash-partial-count').textContent = summary.partial_count;
      document.getElementById('dash-missing-count').textContent = summary.missing_count;

      // Render chart
      const canvas = document.getElementById('dash-coverage-chart');
      if (canvas) {
        if (dashChartInstance) dashChartInstance.destroy();
        dashChartInstance = new Chart(canvas.getContext('2d'), {
          type: 'doughnut',
          data: {
            labels: ['Known', 'Partially Matched', 'Missing'],
            datasets: [{
              data: [summary.known_count, summary.partial_count, summary.missing_count],
              backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { color: '#1e293b', font: { family: 'Inter', weight: '700', size: 11 } } }
            }
          }
        });
      }
    }
  } catch (e) {
    console.warn('Skill coverage snippet error', e);
  }
}

async function loadRoadmapProgressSnippet(studentId, roleId) {
  try {
    const res = await fetch(`/api/roadmap/${roleId}?student_id=${studentId}`);
    const data = await res.json();
    if (data.status === 'success' && data.data) {
      const road = data.data;
      document.getElementById('dash-roadmap-role-title').textContent = road.role_title;
      document.getElementById('dash-roadmap-pct').textContent = `${road.overall_progress_percentage}%`;
      document.getElementById('dash-roadmap-bar').style.width = `${road.overall_progress_percentage}%`;
      document.getElementById('dash-roadmap-tasks').textContent = `${road.completed_tasks} of ${road.total_tasks} Tasks Completed`;
      document.getElementById('dash-btn-roadmap').href = `/roadmap?role=${road.role_id}`;
    }
  } catch (e) {
    console.warn('Roadmap snippet error', e);
  }
}
