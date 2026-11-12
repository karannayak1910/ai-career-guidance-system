/**
 * Profile Module: Interactive Student Profile Form & Resume Parser Studio.
 * Handles resume file uploads, entity extraction reviews, interactive tag selections,
 * skill proficiencies, and SQLite persistence.
 */

// State Management
let selectedSkills = new Map(); // skill_name -> proficiency (Beginner, Intermediate, Advanced)
let selectedInterests = new Set();
let skillsCatalog = {};

// Comprehensive Presets across all 15 Tech Career Roles
const PRESET_PROGRAMMING = ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'HTML', 'CSS', 'SQL'];
const PRESET_FRAMEWORKS = ['React', 'Next.js', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Tailwind CSS', 'TensorFlow', 'PyTorch'];
const PRESET_DATABASES = ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Database Administration'];
const PRESET_TOOLS = ['Git', 'Docker', 'Kubernetes', 'Linux', 'AWS', 'GCP', 'Azure', 'CI/CD', 'Figma', 'Tableau', 'Power BI'];
const PRESET_TECH_SKILLS = [
  'Data Structures', 'Algorithms', 'Machine Learning', 'Deep Learning', 
  'Statistics', 'Mathematics', 'Networking', 'Cybersecurity', 'REST APIs', 
  'Cloud Computing', 'UI/UX Design', 'Database Design'
];

const PRESET_INTERESTS = [
  'Artificial Intelligence', 'Machine Learning', 'Web Development', 
  'Data Science', 'Cybersecurity', 'Cloud Computing', 
  'Software Development', 'Data Analytics'
];

// Initialize UI
document.addEventListener('DOMContentLoaded', async () => {
  await fetchSkillsCatalog();
  renderPresetTagButtons();
  setupResumeDropzone();
  setupEventListeners();
  loadCurrentProfileIfExists();
});

// Fetch Skills Catalog
async function fetchSkillsCatalog() {
  try {
    const res = await fetch('/api/skills/catalog');
    const data = await res.json();
    if (data.status === 'success') {
      skillsCatalog = data.catalog || {};
    }
  } catch (e) {
    console.warn('Failed to load skills catalog', e);
  }
}

// Render Tag Buttons
function renderPresetTagButtons() {
  renderTagGroup('tags-programming', PRESET_PROGRAMMING);
  renderTagGroup('tags-frameworks', PRESET_FRAMEWORKS);
  renderTagGroup('tags-databases', PRESET_DATABASES);
  renderTagGroup('tags-tools', PRESET_TOOLS);
  renderTagGroup('tags-tech-skills', PRESET_TECH_SKILLS);

  // Render Interests
  const interestContainer = document.getElementById('tags-interests');
  if (interestContainer) {
    interestContainer.innerHTML = '';
    PRESET_INTERESTS.forEach(interest => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `tag-btn ${selectedInterests.has(interest) ? 'interest-selected' : ''}`;
      btn.innerHTML = `<i class="fas fa-check-circle" style="font-size: 0.75rem; margin-right: 4px; display: ${selectedInterests.has(interest) ? 'inline-block' : 'none'};"></i>${interest}`;
      btn.onclick = () => toggleInterest(interest, btn);
      interestContainer.appendChild(btn);
    });
  }
}

function renderTagGroup(containerId, skillsList) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  skillsList.forEach(skill => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `tag-btn ${selectedSkills.has(skill) ? 'selected' : ''}`;
    btn.innerHTML = `<i class="fas fa-check" style="font-size: 0.75rem; margin-right: 4px; display: ${selectedSkills.has(skill) ? 'inline-block' : 'none'};"></i>${skill}`;
    btn.onclick = () => toggleSkill(skill, btn);
    container.appendChild(btn);
  });
}

function toggleSkill(skill, btnElement) {
  if (selectedSkills.has(skill)) {
    selectedSkills.delete(skill);
    if (btnElement) {
      btnElement.classList.remove('selected');
      const checkIcon = btnElement.querySelector('.fa-check');
      if (checkIcon) checkIcon.style.display = 'none';
    }
  } else {
    selectedSkills.set(skill, 'Intermediate');
    if (btnElement) {
      btnElement.classList.add('selected');
      const checkIcon = btnElement.querySelector('.fa-check');
      if (checkIcon) checkIcon.style.display = 'inline-block';
    }
  }
  renderSelectedSkillsList();
}

function toggleInterest(interest, btnElement) {
  if (selectedInterests.has(interest)) {
    selectedInterests.delete(interest);
    if (btnElement) {
      btnElement.classList.remove('interest-selected');
      const checkIcon = btnElement.querySelector('.fa-check-circle');
      if (checkIcon) checkIcon.style.display = 'none';
    }
  } else {
    selectedInterests.add(interest);
    if (btnElement) {
      btnElement.classList.add('interest-selected');
      const checkIcon = btnElement.querySelector('.fa-check-circle');
      if (checkIcon) checkIcon.style.display = 'inline-block';
    }
  }
}

// Custom skill adder
function addCustomSkill(inputElem) {
  const val = inputElem.value.trim();
  if (val && !selectedSkills.has(val)) {
    selectedSkills.set(val, 'Intermediate');
    inputElem.value = '';
    renderSelectedSkillsList();
    showToast(`Added custom skill: ${val}`, 'info');
  }
}

// Render Chosen Skills & Proficiency Selectors
function renderSelectedSkillsList() {
  const container = document.getElementById('selected-skills-container');
  const countBadge = document.getElementById('selected-skills-count');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${selectedSkills.size} Selected`;
  }

  if (selectedSkills.size === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 2rem 1.5rem; background: var(--bg-card-alt); border: 1px dashed var(--border-color); border-radius: 8px;">
        <i class="fas fa-layer-group" style="font-size: 1.8rem; color: var(--maroon); margin-bottom: 0.6rem; display: block;"></i>
        Click on skills in the categories above or type custom skills to configure individual proficiency levels.
      </div>
    `;
    return;
  }

  container.innerHTML = '';
  selectedSkills.forEach((prof, skill) => {
    const card = document.createElement('div');
    card.className = 'skill-row-card';
    card.innerHTML = `
      <span class="skill-row-name">
        <i class="fas fa-check-circle" style="color: var(--maroon); margin-right: 6px;"></i>${skill}
      </span>
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <select class="prof-select" onchange="updateSkillProficiency('${skill}', this.value)" aria-label="Proficiency for ${skill}">
          <option value="Beginner" ${prof === 'Beginner' ? 'selected' : ''}>Beginner</option>
          <option value="Intermediate" ${prof === 'Intermediate' ? 'selected' : ''}>Intermediate</option>
          <option value="Advanced" ${prof === 'Advanced' ? 'selected' : ''}>Advanced</option>
        </select>
        <button type="button" style="background: none; border: none; color: #ef4444; cursor: pointer; padding: 4px; font-size: 0.9rem;" title="Remove ${skill}" onclick="removeSkill('${skill}')">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

window.updateSkillProficiency = function(skill, newProf) {
  selectedSkills.set(skill, newProf);
};

window.removeSkill = function(skill) {
  selectedSkills.delete(skill);
  // Unselect corresponding button if present
  document.querySelectorAll('.tag-btn').forEach(btn => {
    if (btn.textContent.trim().endsWith(skill)) {
      btn.classList.remove('selected');
      const check = btn.querySelector('.fa-check');
      if (check) check.style.display = 'none';
    }
  });
  renderSelectedSkillsList();
};

// Global state for last extracted resume data
window._lastExtractedData = null;
window._currentResumeFile = null;

// Tab Switching (File Upload vs. Paste Text)
window.switchResumeTab = function(tab) {
  const fileTab = document.getElementById('resume-tab-file');
  const textTab = document.getElementById('resume-tab-text');
  const btnFile = document.getElementById('tab-btn-file');
  const btnText = document.getElementById('tab-btn-text');

  if (tab === 'file') {
    if (fileTab) fileTab.style.display = 'block';
    if (textTab) textTab.style.display = 'none';
    if (btnFile) { btnFile.className = 'btn btn-sm btn-primary'; }
    if (btnText) { btnText.className = 'btn btn-sm btn-secondary'; }
  } else {
    if (fileTab) fileTab.style.display = 'none';
    if (textTab) textTab.style.display = 'block';
    if (btnFile) { btnFile.className = 'btn btn-sm btn-secondary'; }
    if (btnText) { btnText.className = 'btn btn-sm btn-primary'; }
    const pasteArea = document.getElementById('resume-paste-area');
    if (pasteArea) pasteArea.focus();
  }
};

window.triggerResumeBrowse = function(e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const fileInput = document.getElementById('resume-file-input');
  if (fileInput) fileInput.click();
};

window.clearPastedResume = function() {
  const pasteArea = document.getElementById('resume-paste-area');
  if (pasteArea) {
    pasteArea.value = '';
    pasteArea.focus();
  }
};

window.reExtractCurrentFile = function() {
  if (window._currentResumeFile) {
    uploadAndParseResume(window._currentResumeFile);
  } else {
    window.triggerResumeBrowse();
  }
};

// Resume Upload & Drag-and-Drop Setup
function setupResumeDropzone() {
  const dropzone = document.getElementById('resume-dropzone');
  const fileInput = document.getElementById('resume-file-input');
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', (e) => {
    // If the click originated from an explicit button inside, don't double trigger
    if (e.target.closest('button')) return;
    fileInput.click();
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      window._currentResumeFile = files[0];
      handleResumeFile(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      const file = fileInput.files[0];
      window._currentResumeFile = file;
      handleResumeFile(file);
      // Reset input value so selecting the same file again triggers change
      fileInput.value = '';
    }
  });
}

async function handleResumeFile(file) {
  const allowed = ['.pdf', '.docx', '.doc', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showToast('Only PDF, DOCX, and TXT resume formats are supported.', 'error');
    return;
  }

  const statusBox = document.getElementById('file-status-box');
  const fileNameText = document.getElementById('file-status-name');
  const reExtractBtn = document.getElementById('btn-re-extract');

  if (statusBox && fileNameText) {
    statusBox.classList.add('active');
    fileNameText.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    if (reExtractBtn) reExtractBtn.style.display = 'inline-flex';
  }

  // Auto trigger upload & parse
  await uploadAndParseResume(file);
}

async function uploadAndParseResume(file) {
  const formData = new FormData();
  formData.append('resume', file);

  showToast('Analyzing and extracting resume data...', 'info');

  const uploadIndicator = document.getElementById('upload-indicator');
  if (uploadIndicator) uploadIndicator.style.display = 'block';

  try {
    const res = await fetch('/api/resume/parse', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    if (uploadIndicator) uploadIndicator.style.display = 'none';

    if (result.status === 'success' && result.data) {
      // 1. Immediately apply the extracted data into the form fields
      applyExtractedData(result.data);

      // 2. Display success banner and toast
      showToast('Resume extracted! Your profile form has been populated.', 'success');

      // 3. Prepare review modal
      showResumeReviewModal(result.data, false);
    } else {
      showToast(result.message || 'Error parsing resume', 'error');
    }
  } catch (err) {
    if (uploadIndicator) uploadIndicator.style.display = 'none';
    showToast(`Network error: ${err.message}`, 'error');
  }
}

// Handle Pasted Resume Text Extraction
window.handlePastedResumeExtract = async function() {
  const pasteArea = document.getElementById('resume-paste-area');
  const parseBtn = document.getElementById('btn-parse-text');
  if (!pasteArea) return;

  const text = pasteArea.value.trim();
  if (!text || text.length < 20) {
    showToast('Please paste your resume contents (skills, education, or experience) before extracting.', 'warning');
    pasteArea.focus();
    return;
  }

  if (parseBtn) {
    parseBtn.disabled = true;
    parseBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Extracting...';
  }

  showToast('Parsing resume text and extracting skills...', 'info');

  try {
    const res = await fetch('/api/resume/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: text })
    });

    const result = await res.json();
    if (parseBtn) {
      parseBtn.disabled = false;
      parseBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Extract & Populate Form';
    }

    if (result.status === 'success' && result.data) {
      // 1. Immediately populate form
      applyExtractedData(result.data);

      // 2. Show toast & banner
      showToast('Resume text extracted! Profile form has been populated.', 'success');

      // 3. Prepare review modal
      showResumeReviewModal(result.data, false);
    } else {
      showToast(result.message || 'Failed to extract from resume text', 'error');
    }
  } catch (err) {
    if (parseBtn) {
      parseBtn.disabled = false;
      parseBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Extract & Populate Form';
    }
    showToast(`Error: ${err.message}`, 'error');
  }
};

// Show Extraction Preview Modal
function showResumeReviewModal(extracted, openModalDirectly = true) {
  window._lastExtractedData = extracted;
  const modal = document.getElementById('review-modal');
  const body = document.getElementById('review-modal-body');
  if (!modal || !body) return;

  const allParsedSkills = [
    ...(extracted.programming_languages || []),
    ...(extracted.frameworks || []),
    ...(extracted.databases || []),
    ...(extracted.tools_technologies || []),
    ...(extracted.technical_skills || [])
  ];

  body.innerHTML = `
    <div style="margin-bottom: 1.5rem; background: var(--light-blue-surface); border: 1px solid #bae6fd; border-radius: 8px; padding: 1.25rem;">
      <h4 style="color: var(--blue-dark); font-weight: 700; margin-bottom: 0.6rem; font-size: 1.05rem;">
        <i class="fas fa-id-card"></i> Candidate Summary
      </h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.6rem; font-size: 0.9rem;">
        <p><strong>Name:</strong> ${extracted.full_name || 'Not detected (please enter below)'}</p>
        <p><strong>College:</strong> ${extracted.college_name || 'Not detected (please enter below)'}</p>
        <p><strong>Branch:</strong> ${extracted.branch || 'Computer Science'}</p>
        <p><strong>Semester:</strong> Semester ${extracted.current_semester || 6} | <strong>Graduation:</strong> ${extracted.graduation_year || 2026}</p>
      </div>
    </div>

    <div style="margin-bottom: 1.5rem;">
      <h4 style="color: var(--maroon); font-weight: 700; margin-bottom: 0.6rem; font-size: 1.05rem;">
        <i class="fas fa-code"></i> Detected Technical Skills (${allParsedSkills.length})
      </h4>
      <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        ${allParsedSkills.length > 0 ? allParsedSkills.map(s => `
          <span style="background: var(--light-blue); border: 1px solid #bae6fd; padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; color: var(--blue-dark); font-weight: 600;">
            ${s} (${extracted.skill_proficiencies ? (extracted.skill_proficiencies[s] || 'Intermediate') : 'Intermediate'})
          </span>
        `).join('') : '<span style="color: var(--text-muted); font-size: 0.85rem;">None detected</span>'}
      </div>
    </div>

    <div>
      <h4 style="color: var(--purple-accent); font-weight: 700; margin-bottom: 0.6rem; font-size: 1.05rem;">
        <i class="fas fa-compass"></i> Detected Interests (${(extracted.interest_areas || []).length})
      </h4>
      <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        ${(extracted.interest_areas || []).length > 0 ? (extracted.interest_areas || []).map(i => `
          <span style="background: var(--light-yellow); border: 1px solid #fde68a; padding: 4px 12px; border-radius: 99px; font-size: 0.82rem; color: var(--yellow-dark); font-weight: 600;">
            ${i}
          </span>
        `).join('') : '<span style="color: var(--text-muted); font-size: 0.85rem;">None detected</span>'}
      </div>
    </div>
  `;

  // Attach apply button action
  const applyBtn = document.getElementById('btn-apply-extracted');
  if (applyBtn) {
    applyBtn.onclick = () => {
      applyExtractedData(extracted);
      modal.classList.remove('active');
      showToast('Resume data confirmed and populated into profile form!', 'success');
      const nameInput = document.getElementById('full_name');
      if (nameInput) nameInput.focus();
    };
  }

  if (openModalDirectly) {
    modal.classList.add('active');
  }
}

window.openReviewModalFromBanner = function() {
  if (window._lastExtractedData) {
    showResumeReviewModal(window._lastExtractedData, true);
  } else {
    showToast('Please upload or paste a resume first.', 'info');
  }
};

function closeReviewModal() {
  const modal = document.getElementById('review-modal');
  if (modal) modal.classList.remove('active');
}

// Apply extracted values directly to form
function applyExtractedData(data) {
  if (!data) return;
  window._lastExtractedData = data;

  if (data.full_name) {
    const nameElem = document.getElementById('full_name');
    if (nameElem) nameElem.value = data.full_name;
  }
  if (data.college_name) {
    const colElem = document.getElementById('college_name');
    if (colElem) colElem.value = data.college_name;
  }
  if (data.branch) {
    const branchElem = document.getElementById('branch');
    if (branchElem) {
      // Find matching branch option
      let matched = false;
      for (let opt of branchElem.options) {
        if (opt.value.toLowerCase() === data.branch.toLowerCase()) {
          branchElem.value = opt.value;
          matched = true;
          break;
        }
      }
      if (!matched && data.branch) branchElem.value = data.branch;
    }
  }
  if (data.current_semester) {
    const semElem = document.getElementById('current_semester');
    if (semElem) semElem.value = String(data.current_semester);
  }
  if (data.graduation_year) {
    const gradElem = document.getElementById('graduation_year');
    if (gradElem) gradElem.value = String(data.graduation_year);
  }

  // Aggregate all parsed skills
  const allParsedSkills = [
    ...(data.programming_languages || []),
    ...(data.frameworks || []),
    ...(data.databases || []),
    ...(data.tools_technologies || []),
    ...(data.technical_skills || [])
  ];

  allParsedSkills.forEach(skill => {
    const prof = data.skill_proficiencies ? (data.skill_proficiencies[skill] || 'Intermediate') : 'Intermediate';
    selectedSkills.set(skill, prof);
  });

  // Aggregate extracted interests
  (data.interest_areas || []).forEach(i => selectedInterests.add(i));

  // Refresh UI badges & list
  renderPresetTagButtons();
  renderSelectedSkillsList();

  // Populate In-Page Banner
  const banner = document.getElementById('extraction-result-banner');
  const bannerTitle = document.getElementById('extract-banner-title');
  const bannerSummary = document.getElementById('extract-banner-summary');
  const bannerSkills = document.getElementById('extract-banner-skills');

  if (banner) {
    banner.style.display = 'block';
    if (bannerTitle) {
      bannerTitle.textContent = `${data.full_name ? data.full_name + ' — ' : ''}Resume Extracted Successfully!`;
    }
    if (bannerSummary) {
      const skillsCount = allParsedSkills.length;
      const interestsCount = (data.interest_areas || []).length;
      bannerSummary.innerHTML = `
        Identified <strong>${skillsCount} technical skills</strong>, <strong>${interestsCount} interest areas</strong>, 
        and academic details (${data.branch || 'Engineering'}, Semester ${data.current_semester || 6}). 
        All fields have been filled into the form below.
      `;
    }
    if (bannerSkills) {
      bannerSkills.innerHTML = allParsedSkills.slice(0, 12).map(s => `
        <span style="background: var(--light-blue); color: var(--blue-dark); font-size: 0.78rem; font-weight: 700; padding: 2px 10px; border-radius: 99px; border: 1px solid #bae6fd;">
          <i class="fas fa-check" style="font-size: 0.7rem; margin-right: 3px;"></i>${s}
        </span>
      `).join('') + (allParsedSkills.length > 12 ? `<span style="font-size: 0.78rem; color: var(--text-muted); align-self: center;">+${allParsedSkills.length - 12} more</span>` : '');
    }
  }
}

// Event Listeners
function setupEventListeners() {
  const form = document.getElementById('profile-form');
  if (form) {
    form.addEventListener('submit', handleProfileSubmission);
  }

  // Hours per week slider display sync
  const hoursSlider = document.getElementById('hours_per_week');
  const hoursVal = document.getElementById('hours_val');
  if (hoursSlider && hoursVal) {
    hoursSlider.addEventListener('input', () => {
      hoursVal.textContent = `${hoursSlider.value} hrs/week`;
    });
  }

  // Custom skill input on Enter
  const customInput = document.getElementById('custom-skill-input');
  if (customInput) {
    customInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addCustomSkill(customInput);
      }
    });
  }
}

// Form Submission & SQLite Persistence
async function handleProfileSubmission(e) {
  e.preventDefault();

  const full_name = document.getElementById('full_name').value.trim();
  const college_name = document.getElementById('college_name').value.trim();
  const branch = document.getElementById('branch').value;
  const current_semester = parseInt(document.getElementById('current_semester').value);
  const graduation_year = parseInt(document.getElementById('graduation_year').value);
  const preferred_work_area = document.getElementById('preferred_work_area').value;
  const preferred_career_type = document.getElementById('preferred_career_type').value;
  const hours_per_week = parseInt(document.getElementById('hours_per_week').value);

  // Group skills back into categories
  const progLangs = [];
  const frameworks = [];
  const databases = [];
  const tools = [];
  const techSkills = [];
  const proficiencies = {};

  selectedSkills.forEach((prof, skill) => {
    proficiencies[skill] = prof;
    const cat = (skillsCatalog[skill] && skillsCatalog[skill].category) || '';

    if (cat === 'Programming Languages' || PRESET_PROGRAMMING.includes(skill)) {
      progLangs.push(skill);
    } else if (cat === 'Frameworks' || PRESET_FRAMEWORKS.includes(skill)) {
      frameworks.push(skill);
    } else if (cat === 'Databases' || PRESET_DATABASES.includes(skill)) {
      databases.push(skill);
    } else if (cat === 'Tools' || PRESET_TOOLS.includes(skill)) {
      tools.push(skill);
    } else {
      techSkills.push(skill);
    }
  });

  const payload = {
    full_name,
    college_name,
    branch,
    current_semester,
    graduation_year,
    programming_languages: progLangs,
    frameworks,
    databases,
    tools_technologies: tools,
    technical_skills: techSkills,
    skill_proficiencies: proficiencies,
    interest_areas: Array.from(selectedInterests),
    preferred_work_area,
    preferred_career_type,
    hours_per_week
  };

  // Validation
  if (!full_name) {
    showToast('Please enter your full name.', 'warning');
    return;
  }
  if (!branch) {
    showToast('Please select your college branch.', 'warning');
    return;
  }
  if (selectedSkills.size === 0 && selectedInterests.size === 0) {
    showToast('Please select at least 1 technical skill or interest area.', 'warning');
    return;
  }

  showToast('Saving profile to database...', 'info');
  const submitBtn = document.getElementById('btn-submit-profile');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving Profile...';
  }

  try {
    const res = await fetch('/api/profile/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-rocket"></i> Submit Profile & Run AI Recommendation Engine';
    }

    if (data.status === 'success') {
      showSuccessModal(data.student_id, full_name);
    } else {
      showToast(data.message || 'Error saving profile', 'error');
    }
  } catch (err) {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-rocket"></i> Submit Profile & Run AI Recommendation Engine';
    }
    showToast(`Error: ${err.message}`, 'error');
  }
}

// Success Modal
function showSuccessModal(studentId, studentName) {
  const modal = document.getElementById('success-modal');
  const body = document.getElementById('success-modal-body');
  if (!modal || !body) {
    window.location.href = '/recommendations';
    return;
  }

  body.innerHTML = `
    <div style="text-align: center; padding: 1.5rem 1rem;">
      <div style="width: 72px; height: 72px; border-radius: 50%; background: var(--success-light); color: var(--success); font-size: 2.2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem; border: 2px solid #86efac;">
        <i class="fas fa-check"></i>
      </div>
      <h3 style="color: var(--maroon); margin-bottom: 0.6rem; font-size: 1.45rem; font-weight: 800;">Profile Successfully Registered!</h3>
      <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.75rem; max-width: 480px; margin-left: auto; margin-right: auto;">
        Welcome, <strong>${studentName}</strong>! Your technical competencies, academic profile, and preferences have been securely saved to the database.
      </p>
      <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <a href="/recommendations" class="btn btn-primary btn-lg">
          <i class="fas fa-chart-pie"></i> View AI Career Recommendations
        </a>
        <a href="/dashboard" class="btn btn-secondary btn-lg">
          <i class="fas fa-th-large"></i> Go to Student Dashboard
        </a>
      </div>
    </div>
  `;

  modal.classList.add('active');
}

// Load current profile if exists
async function loadCurrentProfileIfExists() {
  try {
    const res = await fetch('/api/profile/current');
    const data = await res.json();
    if (data.status === 'success' && data.profile) {
      const p = data.profile;
      document.getElementById('full_name').value = p.full_name || '';
      document.getElementById('college_name').value = p.college_name || '';
      if (p.branch) document.getElementById('branch').value = p.branch;
      if (p.current_semester) document.getElementById('current_semester').value = p.current_semester;
      if (p.graduation_year) document.getElementById('graduation_year').value = p.graduation_year;
      if (p.preferred_work_area) document.getElementById('preferred_work_area').value = p.preferred_work_area;
      if (p.preferred_career_type) document.getElementById('preferred_career_type').value = p.preferred_career_type;
      if (p.hours_per_week) {
        document.getElementById('hours_per_week').value = p.hours_per_week;
        const hoursVal = document.getElementById('hours_val');
        if (hoursVal) hoursVal.textContent = `${p.hours_per_week} hrs/week`;
      }

      // Populate skills
      const profs = p.skill_proficiencies || {};
      const allSkills = [
        ...(p.programming_languages || []),
        ...(p.frameworks || []),
        ...(p.databases || []),
        ...(p.tools_technologies || []),
        ...(p.technical_skills || [])
      ];

      allSkills.forEach(s => {
        selectedSkills.set(s, profs[s] || 'Intermediate');
      });

      // Populate interests
      (p.interest_areas || []).forEach(i => selectedInterests.add(i));

      renderPresetTagButtons();
      renderSelectedSkillsList();
    }
  } catch (e) {
    // Fresh profile
  }
}
