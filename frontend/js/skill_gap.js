/**
 * Skill Gap Analysis Module: Known vs Partially Matched vs Missing Skills Breakdown
 * with Chart.js Skill Coverage Visualization across all 15 roles.
 */

let activeRoleKey = 'data_scientist';
let gapCoverageChartInstance = null;

const ALL_15_ROLES = [
  { id: 'data_analyst', title: 'Data Analyst' },
  { id: 'data_scientist', title: 'Data Scientist' },
  { id: 'ml_engineer', title: 'ML Engineer' },
  { id: 'ai_engineer', title: 'AI Engineer' },
  { id: 'frontend_developer', title: 'Frontend Developer' },
  { id: 'backend_developer', title: 'Backend Developer' },
  { id: 'fullstack_developer', title: 'Full Stack Developer' },
  { id: 'python_developer', title: 'Python Developer' },
  { id: 'java_developer', title: 'Java Developer' },
  { id: 'software_engineer', title: 'Software Engineer' },
  { id: 'cybersecurity_analyst', title: 'Cybersecurity Analyst' },
  { id: 'cloud_engineer', title: 'Cloud Engineer' },
  { id: 'devops_engineer', title: 'DevOps Engineer' },
  { id: 'database_administrator', title: 'Database Admin (DBA)' },
  { id: 'ui_ux_developer', title: 'UI/UX Developer' }
];

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const qRole = urlParams.get('role');
  if (qRole) activeRoleKey = qRole;

  renderRoleTabs();
  await loadSkillGapData(activeRoleKey);
});

function renderRoleTabs() {
  const container = document.getElementById('role-tabs-container');
  if (!container) return;
  container.innerHTML = '';

  ALL_15_ROLES.forEach(r => {
    const btn = document.createElement('button');
    btn.className = `gap-tab-btn ${r.id === activeRoleKey ? 'active' : ''}`;
    btn.textContent = r.title;
    btn.onclick = async () => {
      activeRoleKey = r.id;
      document.querySelectorAll('.gap-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      await loadSkillGapData(activeRoleKey);
    };
    container.appendChild(btn);
  });
}

async function loadSkillGapData(roleKey) {
  const loading = document.getElementById('gap-loading');
  const content = document.getElementById('gap-content');

  if (loading) loading.style.display = 'block';
  if (content) content.style.display = 'none';

  try {
    const res = await fetch(`/api/skill-gap/${roleKey}`);
    const resData = await res.json();

    if (loading) loading.style.display = 'none';

    if (resData.status === 'success' && resData.data) {
      if (content) content.style.display = 'block';
      renderGapView(resData.data);
    } else {
      showToast(resData.message || 'Unable to load skill gap analysis', 'error');
    }
  } catch (err) {
    if (loading) loading.style.display = 'none';
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderGapView(gap) {
  // Update Header Summary
  const titleElem = document.getElementById('target-role-title');
  const readinessElem = document.getElementById('readiness-badge');
  const readinessBar = document.getElementById('readiness-progress-bar');
  const summaryElem = document.getElementById('gap-summary-text');
  const roadmapBtn = document.getElementById('btn-go-roadmap');
  const detailsBtn = document.getElementById('btn-go-details');

  if (titleElem) titleElem.textContent = gap.role_title;
  if (readinessElem) readinessElem.textContent = `${gap.summary.readiness_percentage}% Skill Coverage`;
  if (readinessBar) readinessBar.style.width = `${gap.summary.readiness_percentage}%`;
  
  if (summaryElem) {
    summaryElem.textContent = `You possess ${gap.summary.known_count} verified skills, have ${gap.summary.partial_count} partially matched / transferrable skills, and need ${gap.summary.missing_count} additional skills to achieve industry production-readiness.`;
  }

  if (roadmapBtn) roadmapBtn.href = `/roadmap?role=${gap.role_id}`;
  if (detailsBtn) detailsBtn.href = `/career-details?role=${gap.role_id}`;

  // Render Chart.js Coverage Chart
  renderCoverageChart(gap.chart_data);

  // 1. Render Known Skills (Green)
  const knownCol = document.getElementById('col-known-list');
  const knownCount = document.getElementById('known-count-badge');
  if (knownCount) knownCount.textContent = gap.known_skills.length;
  if (knownCol) {
    knownCol.innerHTML = '';
    if (gap.known_skills.length === 0) {
      knownCol.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">No core skills matched yet.</div>`;
    } else {
      gap.known_skills.forEach(s => {
        const item = document.createElement('div');
        item.className = 'skill-item-card';
        item.style.borderLeft = '4px solid var(--success)';
        item.innerHTML = `
          <div class="item-top">
            <span class="item-title"><i class="fas fa-check-circle" style="color: var(--success); margin-right: 6px;"></i>${s.name}</span>
            <span style="font-size: 0.75rem; background: var(--success-light); color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 700;">
              ${s.proficiency}
            </span>
          </div>
          <div class="item-why">${s.why_it_matters}</div>
        `;
        knownCol.appendChild(item);
      });
    }
  }

  // 2. Render Partially Matched Skills (Orange)
  const partialCol = document.getElementById('col-partial-list');
  const partialCount = document.getElementById('partial-count-badge');
  if (partialCount) partialCount.textContent = gap.partially_matched_skills.length;
  if (partialCol) {
    partialCol.innerHTML = '';
    if (gap.partially_matched_skills.length === 0) {
      partialCol.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">No partially matched skills found.</div>`;
    } else {
      gap.partially_matched_skills.forEach(s => {
        const item = document.createElement('div');
        item.className = 'skill-item-card';
        item.style.borderLeft = '4px solid var(--warning)';
        item.innerHTML = `
          <div class="item-top">
            <span class="item-title"><i class="fas fa-adjust" style="color: var(--warning); margin-right: 6px;"></i>${s.name}</span>
            <span style="font-size: 0.75rem; background: var(--warning-light); color: #b45309; padding: 2px 8px; border-radius: 4px; font-weight: 700;">
              ${s.status}
            </span>
          </div>
          <div style="font-size: 0.82rem; color: #b45309; margin-bottom: 0.4rem; font-weight: 600;">
            ${s.reason}
          </div>
          <div class="item-why">${s.why_it_matters}</div>
          <div class="item-links">
            <a href="${s.documentation}" target="_blank" rel="noopener noreferrer" class="item-link">
              <i class="fas fa-book-open"></i> Docs
            </a>
            <a href="${s.youtube}" target="_blank" rel="noopener noreferrer" class="item-link" style="color: #b91c1c;">
              <i class="fab fa-youtube"></i> Tutorial
            </a>
          </div>
        `;
        partialCol.appendChild(item);
      });
    }
  }

  // 3. Render Missing Skills (Red)
  const missingCol = document.getElementById('col-missing-list');
  const missingCount = document.getElementById('missing-count-badge');
  if (missingCount) missingCount.textContent = gap.missing_skills.length;
  if (missingCol) {
    missingCol.innerHTML = '';
    if (gap.missing_skills.length === 0) {
      missingCol.innerHTML = `<div style="color: var(--success); font-size: 0.85rem; padding: 1rem 0; font-weight: 700;"><i class="fas fa-check"></i> All required skills are covered! Great job!</div>`;
    } else {
      gap.missing_skills.forEach(s => {
        const isCritical = s.priority === 'Critical';
        const item = document.createElement('div');
        item.className = 'skill-item-card';
        item.style.borderLeft = '4px solid var(--danger)';
        item.innerHTML = `
          <div class="item-top">
            <span class="item-title"><i class="fas fa-times-circle" style="color: var(--danger); margin-right: 6px;"></i>${s.name}</span>
            <span class="priority-tag ${isCritical ? 'priority-critical' : 'priority-recommended'}">
              ${s.priority} Priority
            </span>
          </div>
          <div class="item-why">${s.why_it_matters}</div>
          ${s.project_idea ? `
            <div style="background: var(--light-yellow-surface); border: 1px solid #fde68a; padding: 0.6rem; border-radius: 4px; font-size: 0.8rem; color: var(--yellow-dark); margin-bottom: 0.6rem;">
              <strong><i class="fas fa-laptop-code"></i> Recommended Project:</strong> ${s.project_idea}
            </div>
          ` : ''}
          <div class="item-links">
            <a href="${s.documentation}" target="_blank" rel="noopener noreferrer" class="item-link">
              <i class="fas fa-book-open"></i> Official Docs
            </a>
            <a href="${s.youtube}" target="_blank" rel="noopener noreferrer" class="item-link" style="color: #b91c1c;">
              <i class="fab fa-youtube"></i> YouTube Crash Course
            </a>
          </div>
        `;
        missingCol.appendChild(item);
      });
    }
  }
}

// Render Doughnut Chart for Skill Coverage
function renderCoverageChart(chartData) {
  const canvas = document.getElementById('gap-coverage-chart');
  if (!canvas || !chartData) return;

  const ctx = canvas.getContext('2d');
  if (gapCoverageChartInstance) {
    gapCoverageChartInstance.destroy();
  }

  gapCoverageChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: chartData.labels,
      datasets: [{
        data: chartData.data,
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#1e293b', font: { family: 'Inter', size: 12, weight: '700' } }
        }
      }
    }
  });
}
