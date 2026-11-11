/**
 * Recommendations Module: Top 3 Matches, Disagreement Explanations,
 * Scoring Breakdown & Chart.js Radar Visualization across all 15 roles.
 */

let radarChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadRecommendations();
});

async function loadRecommendations() {
  const loadingContainer = document.getElementById('loading-state');
  const resultsContainer = document.getElementById('results-state');
  const emptyContainer = document.getElementById('empty-state');

  try {
    const res = await fetch('/api/recommendations/latest');
    const data = await res.json();

    if (loadingContainer) loadingContainer.style.display = 'none';

    if (data.status === 'success' && data.top_3 && data.top_3.length > 0) {
      if (resultsContainer) resultsContainer.style.display = 'block';
      if (emptyContainer) emptyContainer.style.display = 'none';

      // Disagreement note
      const disContainer = document.getElementById('disagreement-banner');
      if (disContainer) {
        if (data.disagreement_explanation) {
          disContainer.style.display = 'block';
          disContainer.innerHTML = `
            <div style="background: var(--light-yellow-surface); border: 1px solid #fde68a; border-left: 5px solid var(--yellow-accent); border-radius: var(--radius-sm); padding: 1rem 1.25rem; display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 2rem;">
              <i class="fas fa-balance-scale" style="color: var(--yellow-dark); font-size: 1.3rem; margin-top: 2px;"></i>
              <div style="font-size: 0.92rem; color: var(--yellow-dark); line-height: 1.5;">
                <strong>Transparent AI Model Comparison:</strong> ${data.disagreement_explanation}
              </div>
            </div>
          `;
        } else {
          disContainer.style.display = 'none';
        }
      }

      renderTop3Cards(data.top_3);
      renderRadarChart(data.radar_chart);
      renderAllRankedTable(data.all_ranked_roles);
    } else {
      if (resultsContainer) resultsContainer.style.display = 'none';
      if (emptyContainer) emptyContainer.style.display = 'block';
    }
  } catch (err) {
    if (loadingContainer) loadingContainer.style.display = 'none';
    showToast(`Error fetching recommendations: ${err.message}`, 'error');
  }
}

// Render Top 3 Recommendation Cards
function renderTop3Cards(top3) {
  const container = document.getElementById('top-3-cards-container');
  if (!container) return;
  container.innerHTML = '';

  const rankLabels = ['Top Recommendation', 'Strong Fit', 'Solid Alternative'];

  top3.forEach((role, idx) => {
    const score = role.match_score;
    const isTop = idx === 0;

    const card = document.createElement('div');
    card.className = `career-card ${isTop ? 'rank-1' : ''}`;
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
          <span style="font-size: 0.8rem; font-weight: 800; color: ${isTop ? 'var(--maroon)' : 'var(--text-muted)'}; text-transform: uppercase;">
            #${idx + 1} ${rankLabels[idx]}
          </span>
          <h3 class="career-role-title">${role.title}</h3>
          <span class="career-domain">${role.domain}</span>
        </div>
        <div class="match-score-badge high">
          ${score}%
        </div>
      </div>

      <div style="margin-bottom: 0.75rem; display: flex; gap: 0.4rem; flex-wrap: wrap;">
        <span class="career-salary">
          <i class="fas fa-coins"></i> ${role.average_salary}
        </span>
        <span class="btn-yellow btn-sm" style="border-radius: 99px; padding: 2px 8px; font-size: 0.78rem;">
          <i class="fas fa-chart-line"></i> ${role.market_demand} Demand
        </span>
      </div>

      <p class="career-desc">${role.description}</p>

      <div style="background: var(--light-blue-surface); border: 1px solid #bae6fd; border-radius: 8px; padding: 0.85rem; margin-bottom: 1.25rem;">
        <strong style="font-size: 0.82rem; color: var(--blue-dark); display: block; margin-bottom: 0.25rem;">
          <i class="fas fa-check-circle" style="color: var(--blue-primary);"></i> Why This Matches You:
        </strong>
        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45; margin: 0;">
          ${role.why_matches}
        </p>
      </div>

      <div class="score-breakdown-bar">
        <div class="breakdown-row">
          <span>Required Skill Coverage</span>
          <span>${role.breakdown.skill_coverage}%</span>
        </div>
        <div class="progress-container" style="margin-bottom: 0.5rem;">
          <div class="progress-fill" style="width: ${role.breakdown.skill_coverage}%;"></div>
        </div>

        <div class="breakdown-row">
          <span>Rule-Based Deduction</span>
          <span>${role.breakdown.rule_score}%</span>
        </div>
        <div class="progress-container" style="margin-bottom: 0.5rem;">
          <div class="progress-fill" style="width: ${role.breakdown.rule_score}%; background: linear-gradient(90deg, var(--maroon), #b91c1c);"></div>
        </div>

        <div class="breakdown-row">
          <span>Decision Tree Confidence</span>
          <span>${role.breakdown.ml_confidence}%</span>
        </div>
        <div class="progress-container" style="margin-bottom: 0.5rem;">
          <div class="progress-fill" style="width: ${role.breakdown.ml_confidence}%; background: linear-gradient(90deg, var(--purple-accent), #9333ea);"></div>
        </div>

        <div class="breakdown-row">
          <span>Interest Match</span>
          <span>${role.breakdown.interest_alignment}%</span>
        </div>
        <div class="progress-container">
          <div class="progress-fill" style="width: ${role.breakdown.interest_alignment}%; background: linear-gradient(90deg, var(--blue-primary), #0369a1);"></div>
        </div>
      </div>

      <div style="margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border-color); display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem;">
        <a href="/career-details?role=${role.id}" class="btn btn-sm btn-secondary" style="width: 100%; padding: 0.45rem 0.35rem; font-size: 0.82rem;">
          <i class="fas fa-info-circle"></i> Details
        </a>
        <a href="/skill-gap?role=${role.id}" class="btn btn-sm btn-primary" style="width: 100%; padding: 0.45rem 0.35rem; font-size: 0.82rem;">
          <i class="fas fa-puzzle-piece"></i> Skill Gap
        </a>
        <a href="/roadmap?role=${role.id}" class="btn btn-sm btn-accent" style="width: 100%; padding: 0.45rem 0.35rem; font-size: 0.82rem;">
          <i class="fas fa-road"></i> Roadmap
        </a>
      </div>
    `;

    container.appendChild(card);
  });
}

// Render Chart.js Radar Chart
function renderRadarChart(chartData) {
  const canvas = document.getElementById('career-radar-chart');
  if (!canvas || !chartData) return;

  const ctx = canvas.getContext('2d');
  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Career Match Score (%)',
        data: chartData.data,
        backgroundColor: 'rgba(128, 0, 32, 0.15)',
        borderColor: '#800020',
        borderWidth: 2.5,
        pointBackgroundColor: '#7c3aed',
        pointBorderColor: '#ffffff',
        pointHoverBackgroundColor: '#800020',
        pointHoverBorderColor: '#ffffff',
        pointRadius: 4.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(0, 0, 0, 0.08)' },
          grid: { color: 'rgba(0, 0, 0, 0.06)' },
          pointLabels: {
            color: '#1e293b',
            font: { family: 'Inter', size: 11, weight: '700' }
          },
          ticks: {
            backdropColor: 'transparent',
            color: '#64748b',
            beginAtZero: true,
            max: 100,
            stepSize: 20
          }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#0f172a', font: { family: 'Inter', size: 12, weight: '700' } }
        },
        tooltip: {
          backgroundColor: '#ffffff',
          titleColor: '#800020',
          bodyColor: '#0f172a',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          boxShadow: '0 4px 14px rgba(0,0,0,0.1)'
        }
      }
    }
  });
}

// Render Complete 15-Role Ranking Table
function renderAllRankedTable(roles) {
  const tbody = document.getElementById('all-roles-table-body');
  if (!tbody || !roles) return;
  tbody.innerHTML = '';

  roles.forEach((r, i) => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--border-color)';
    tr.innerHTML = `
      <td style="padding: 0.85rem 1rem; color: var(--text-muted); font-weight: 700;">#${i + 1}</td>
      <td style="padding: 0.85rem 1rem; font-weight: 700; color: var(--text-main);">
        <a href="/career-details?role=${r.id}" style="color: var(--maroon); text-decoration: underline;">
          ${r.title}
        </a>
      </td>
      <td style="padding: 0.85rem 1rem; color: var(--blue-primary); font-size: 0.9rem; font-weight: 600;">${r.domain}</td>
      <td style="padding: 0.85rem 1rem; font-size: 0.85rem; color: var(--yellow-dark); font-weight: 600;">${r.average_salary}</td>
      <td style="padding: 0.85rem 1rem;">
        <span style="font-weight: 800; color: ${r.match_score >= 70 ? 'var(--maroon)' : 'var(--yellow-dark)'}; font-size: 1.1rem;">
          ${r.match_score}%
        </span>
      </td>
      <td style="padding: 0.85rem 1rem; text-align: right;">
        <a href="/career-details?role=${r.id}" class="btn btn-sm btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.78rem; margin-right: 0.3rem;">
          Details
        </a>
        <a href="/skill-gap?role=${r.id}" class="btn btn-sm btn-outline" style="padding: 0.3rem 0.65rem; font-size: 0.78rem; margin-right: 0.3rem;">
          Gap
        </a>
        <a href="/roadmap?role=${r.id}" class="btn btn-sm btn-primary" style="padding: 0.3rem 0.65rem; font-size: 0.78rem;">
          Roadmap
        </a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}
