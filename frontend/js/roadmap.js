/**
 * Learning Roadmap Module: Step-by-Step 4-Month Milestones, Curated Resources & Progress Checklist
 * across all 15 technology careers.
 */

let activeRoadmapRole = 'data_scientist';
let currentStudentId = null;

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
  if (qRole) activeRoadmapRole = qRole;

  renderRoadmapRoleTabs();
  await loadRoadmap(activeRoadmapRole);
});

function renderRoadmapRoleTabs() {
  const container = document.getElementById('roadmap-tabs-container');
  if (!container) return;
  container.innerHTML = '';

  ALL_15_ROLES.forEach(r => {
    const btn = document.createElement('button');
    btn.className = `gap-tab-btn ${r.id === activeRoadmapRole ? 'active' : ''}`;
    btn.textContent = r.title;
    btn.onclick = async () => {
      activeRoadmapRole = r.id;
      document.querySelectorAll('.gap-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      await loadRoadmap(activeRoadmapRole);
    };
    container.appendChild(btn);
  });
}

async function loadRoadmap(roleKey) {
  const loading = document.getElementById('roadmap-loading');
  const content = document.getElementById('roadmap-content');

  if (loading) loading.style.display = 'block';
  if (content) content.style.display = 'none';

  try {
    const res = await fetch(`/api/roadmap/${roleKey}`);
    const resData = await res.json();

    if (loading) loading.style.display = 'none';

    if (resData.status === 'success' && resData.data) {
      currentStudentId = resData.student_id;
      if (content) content.style.display = 'block';
      renderRoadmapView(resData.data);
    } else {
      showToast(resData.message || 'Error generating roadmap', 'error');
    }
  } catch (err) {
    if (loading) loading.style.display = 'none';
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderRoadmapView(roadmap) {
  // Update Header Elements
  document.getElementById('roadmap-role-title').textContent = roadmap.role_title;
  document.getElementById('roadmap-hours').textContent = `${roadmap.weekly_commitment_hours} hrs/week`;
  document.getElementById('overall-progress-text').textContent = `${roadmap.overall_progress_percentage}%`;
  document.getElementById('overall-progress-bar').style.width = `${roadmap.overall_progress_percentage}%`;
  document.getElementById('completed-tasks-count').textContent = `${roadmap.completed_tasks} of ${roadmap.total_tasks} Tasks Completed`;

  const timelineContainer = document.getElementById('roadmap-milestones-container');
  if (!timelineContainer) return;
  timelineContainer.innerHTML = '';

  roadmap.milestones.forEach(m => {
    const card = document.createElement('div');
    card.className = 'roadmap-card';
    card.style.borderTop = '4px solid var(--maroon)';

    // Skills to develop badges
    const skillsHtml = (m.skills_to_develop || []).map(s => `
      <span style="background: var(--maroon-subtle); border: 1px solid #fecaca; color: var(--maroon); padding: 3px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 700;">
        ${s}
      </span>
    `).join('');

    // Topics list
    const topicsHtml = (m.topics_to_cover || []).map(t => `
      <li style="margin-bottom: 0.35rem; color: var(--text-secondary);"><i class="fas fa-angle-right" style="color: var(--maroon); margin-right: 6px;"></i>${t}</li>
    `).join('');

    // Checklist tasks
    const tasksHtml = m.tasks.map(t => `
      <li class="checklist-item ${t.completed ? 'done' : ''}" id="item-${t.id}">
        <input 
          type="checkbox" 
          class="checklist-checkbox" 
          id="cb-${t.id}" 
          ${t.completed ? 'checked' : ''} 
          onchange="toggleTask('${roadmap.role_id}', '${t.id}', this.checked, ${m.month})"
        />
        <label for="cb-${t.id}" class="checklist-text" style="cursor: pointer;">
          ${t.text}
        </label>
      </li>
    `).join('');

    // Resources
    let resourcesHtml = '';
    if (m.resources && m.resources.length > 0) {
      resourcesHtml = `
        <div style="margin-top: 1.25rem;">
          <h5 style="color: var(--maroon); font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem;">
            <i class="fas fa-graduation-cap"></i> Curated Free Learning Resources:
          </h5>
          <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
            ${m.resources.map(r => `
              <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm ${r.type === 'YouTube Tutorial' ? 'btn-outline' : 'btn-secondary'}" style="font-size: 0.82rem;">
                <i class="${r.type === 'YouTube Tutorial' ? 'fab fa-youtube' : 'fas fa-book'}"></i>
                ${r.title}
              </a>
            `).join('')}
          </div>
        </div>
      `;
    }

    // Mini Project
    const proj = m.mini_project || {};

    card.innerHTML = `
      <div class="roadmap-card-header">
        <div>
          <span class="roadmap-month-pill">Month ${m.month} Milestone</span>
          <h3 class="roadmap-title">${m.title}</h3>
          <p class="roadmap-focus"><i class="fas fa-bullseye" style="color: var(--blue-primary);"></i> <strong>Objective:</strong> ${m.objectives}</p>
        </div>
        <span class="btn-yellow btn-sm" style="border-radius: 99px; font-weight: 700;">
          <i class="fas fa-clock"></i> ~${m.weekly_hours} hrs/week
        </span>
      </div>

      <!-- Topics Covered -->
      <div style="margin: 1rem 0; background: var(--bg-main); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
        <h5 style="font-size: 0.88rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.5rem;">
          <i class="fas fa-list-check" style="color: var(--purple-accent);"></i> Key Topics to Cover:
        </h5>
        <ul style="list-style: none; font-size: 0.88rem;">${topicsHtml}</ul>
      </div>

      ${m.skills_to_develop && m.skills_to_develop.length > 0 ? `
        <div style="margin-bottom: 1rem;">
          <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: 700;">Skills to Target & Develop:</span>
          <div class="roadmap-skills-tags">${skillsHtml}</div>
        </div>
      ` : ''}

      <!-- Interactive Checklist -->
      <div>
        <h5 style="color: var(--text-main); font-size: 0.92rem; font-weight: 800; margin: 1rem 0 0.5rem;">
          <i class="fas fa-tasks" style="color: var(--maroon);"></i> Milestone Progress Checklist:
        </h5>
        <ul class="roadmap-checklist">
          ${tasksHtml}
        </ul>
      </div>

      <!-- Practical Assignment & Mini-Project -->
      <div class="project-card">
        <div class="project-title">
          <i class="fas fa-laptop-code"></i> Practical Project: ${proj.title || 'Milestone Implementation'}
        </div>
        <p class="project-desc">${proj.description || m.practical_assignment}</p>
        <div class="project-deliverable">
          <i class="fas fa-box-check"></i> <strong>Deliverable:</strong> ${proj.deliverable || 'GitHub repository with clean documentation.'}
        </div>
      </div>

      ${resourcesHtml}
    `;

    timelineContainer.appendChild(card);
  });
}

// Toggle Task and persist state in SQLite
async function toggleTask(careerRole, taskId, isCompleted, milestoneMonth) {
  const itemElem = document.getElementById(`item-${taskId}`);
  if (itemElem) {
    if (isCompleted) itemElem.classList.add('done');
    else itemElem.classList.remove('done');
  }

  try {
    const res = await fetch('/api/roadmap/task/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentStudentId,
        career_role: careerRole,
        task_id: taskId,
        is_completed: isCompleted,
        milestone_month: milestoneMonth
      })
    });

    const data = await res.json();
    if (data.status === 'success') {
      const progressPercentText = document.getElementById('overall-progress-text');
      const progressBar = document.getElementById('overall-progress-bar');
      const completedStats = document.getElementById('completed-tasks-count');

      if (progressPercentText) progressPercentText.textContent = `${data.overall_progress_percentage}%`;
      if (progressBar) progressBar.style.width = `${data.overall_progress_percentage}%`;
      if (completedStats) completedStats.textContent = `${data.completed_tasks} Tasks Completed`;

      if (isCompleted) {
        showToast('Milestone task completed! Keep advancing!', 'success', 2500);
      }
    } else {
      showToast(data.message || 'Error updating task', 'error');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}
