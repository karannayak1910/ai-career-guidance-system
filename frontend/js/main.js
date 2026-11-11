/**
 * Main Global Utility Module for AI Career Guidance System.
 * Manages Toast Notifications, Session-aware Navbar Sync, and Navigation.
 */

// Toast Notification System
function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    info: 'fa-info-circle',
    warning: 'fa-exclamation-triangle'
  };

  const icon = iconMap[type] || 'fa-info-circle';
  toast.innerHTML = `
    <i class="fas ${icon}" style="font-size: 1.1rem;"></i>
    <span style="flex: 1; font-size: 0.9rem;">${message}</span>
    <button style="background: none; border: none; color: inherit; cursor: pointer; opacity: 0.6;" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// User Logout action
window.logoutUser = async function() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    showToast('Signed out successfully.', 'info');
    setTimeout(() => {
      window.location.href = '/login';
    }, 600);
  } catch (e) {
    window.location.href = '/login';
  }
};

// Check and display active student or user account in navbar
async function updateNavbarStudentStatus() {
  const badgeContainer = document.getElementById('nav-student-badge');
  if (!badgeContainer) return;

  try {
    // 1. Check user authentication
    const authRes = await fetch('/api/auth/me');
    const authData = await authRes.json();

    if (authData.status === 'success' && authData.authenticated && authData.user) {
      const u = authData.user;
      const p = authData.profile;
      const displayName = p ? p.full_name : u.username;
      const subtitle = p ? `(${p.branch})` : '';

      badgeContainer.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.6rem;">
          <div class="user-badge" title="Logged in as ${u.email}">
            <i class="fas fa-user-circle" style="color: var(--maroon);"></i>
            <span>${displayName} ${subtitle}</span>
          </div>
          <button class="btn btn-sm btn-outline" onclick="logoutUser()" title="Sign Out" aria-label="Sign Out" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
            <i class="fas fa-sign-out-alt"></i> Sign Out
          </button>
        </div>
      `;
      return;
    }

    // 2. Fallback to guest profile if saved locally
    const profRes = await fetch('/api/profile/current');
    const profData = await profRes.json();
    if (profData.status === 'success' && profData.profile) {
      badgeContainer.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.6rem;">
          <div class="user-badge">
            <i class="fas fa-user-graduate" style="color: var(--maroon);"></i>
            <span>${profData.profile.full_name} (${profData.profile.branch})</span>
          </div>
          <a href="/login" class="btn btn-sm btn-primary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
            <i class="fas fa-sign-in-alt"></i> Sign In
          </a>
        </div>
      `;
    } else {
      badgeContainer.innerHTML = `
        <a href="/login" class="btn btn-sm btn-primary">
          <i class="fas fa-user-circle"></i> Sign In / Register
        </a>
      `;
    }
  } catch (err) {
    badgeContainer.innerHTML = `
      <a href="/login" class="btn btn-sm btn-primary">
        <i class="fas fa-user-circle"></i> Sign In / Register
      </a>
    `;
  }
}

// Highlight active navbar link
function highlightActiveNav() {
  const path = window.location.pathname;
  const links = document.querySelectorAll('.nav-link');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (path === '/' && href === '/')) {
      link.classList.add('active');
    } else if (href && href !== '/' && !href.startsWith('javascript') && path.startsWith(href)) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// Mobile Access Modal
window.openMobileModal = async function() {
  let modal = document.getElementById('mobile-access-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mobile-access-modal';
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div class="modal-box" style="max-width: 440px; text-align: center;">
        <div class="modal-header">
          <h3 class="modal-title" style="display: flex; align-items: center; gap: 0.5rem; justify-content: center; width: 100%;">
            <i class="fas fa-mobile-screen" style="color: var(--maroon);"></i> Open on Mobile Phone
          </h3>
          <button class="modal-close" onclick="closeMobileModal()">&times;</button>
        </div>
        <div class="modal-body" style="padding: 1.5rem;">
          <p style="color: var(--text-secondary); font-size: 0.92rem; margin-bottom: 1rem;">
            Scan this QR code with your phone camera or use the links below:
          </p>
          <div id="mobile-qr-loading" style="padding: 1.5rem; color: var(--text-muted);">
            <i class="fas fa-spinner fa-spin fa-2x" style="color: var(--maroon);"></i>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">Generating QR Code...</p>
          </div>
          <div id="mobile-qr-wrapper" style="display: none; margin-bottom: 1.25rem;">
            <img id="mobile-qr-img" src="" alt="Mobile QR Code" style="width: 200px; height: 200px; border-radius: 12px; border: 2px solid var(--border-color); box-shadow: var(--shadow-sm); margin: 0 auto; display: block;" />
          </div>
          <div style="background: var(--bg-main); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem; text-align: left; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--maroon); margin-bottom: 0.25rem;">
              <i class="fas fa-globe"></i> Direct Mobile Link (Works on Any Network / 4G / 5G)
            </div>
            <a id="mobile-tunnel-link" href="#" target="_blank" style="font-family: monospace; font-size: 0.82rem; color: var(--blue-primary); word-break: break-all; font-weight: 600;">
              Loading...
            </a>
          </div>
          <div style="background: var(--light-yellow-surface); border: 1px solid #fde68a; border-radius: 8px; padding: 0.75rem; text-align: left; margin-bottom: 1.25rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--yellow-dark); margin-bottom: 0.25rem;">
              <i class="fas fa-wifi"></i> Local Wi-Fi Link
            </div>
            <a id="mobile-lan-link" href="#" target="_blank" style="font-family: monospace; font-size: 0.82rem; color: var(--yellow-dark); word-break: break-all; font-weight: 600;">
              Loading...
            </a>
          </div>
          <button class="btn btn-primary" style="width: 100%;" onclick="copyMobileLink()">
            <i class="fas fa-copy"></i> Copy Mobile Link
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  modal.classList.add('active');
  try {
    const res = await fetch('/api/system/network-info');
    const data = await res.json();
    if (data.status === 'success') {
      const qrImg = document.getElementById('mobile-qr-img');
      const tunnelLink = document.getElementById('mobile-tunnel-link');
      const lanLink = document.getElementById('mobile-lan-link');
      const loading = document.getElementById('mobile-qr-loading');
      const wrapper = document.getElementById('mobile-qr-wrapper');

      const preferredUrl = data.tunnel_url || data.lan_url;
      qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(preferredUrl)}`;
      qrImg.onload = () => {
        if (loading) loading.style.display = 'none';
        if (wrapper) wrapper.style.display = 'block';
      };
      qrImg.onerror = () => {
        if (loading) loading.style.display = 'none';
        if (wrapper) wrapper.style.display = 'none';
      };
      if (tunnelLink) {
        tunnelLink.href = data.tunnel_url;
        tunnelLink.textContent = data.tunnel_url;
      }
      if (lanLink) {
        lanLink.href = data.lan_url;
        lanLink.textContent = data.lan_url;
      }
      window._activeMobileUrl = preferredUrl;
    }
  } catch (e) {
    console.error(e);
  }
};

window.closeMobileModal = function() {
  const modal = document.getElementById('mobile-access-modal');
  if (modal) modal.classList.remove('active');
};

window.copyMobileLink = function() {
  const url = window._activeMobileUrl || window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    showToast('Mobile link copied to clipboard!', 'success');
  }).catch(() => {
    prompt('Copy link:', url);
  });
};

// Add Mobile Connect link to nav-links if not already present
function ensureMobileNavLink() {
  const navLinks = document.querySelector('.nav-links');
  if (navLinks && !document.getElementById('mobile-nav-item')) {
    const li = document.createElement('li');
    li.id = 'mobile-nav-item';
    li.innerHTML = `
      <a href="javascript:void(0)" onclick="openMobileModal()" class="nav-link" title="Open on Mobile Phone" style="color: var(--blue-primary); font-weight: 700;">
        <i class="fas fa-mobile-screen"></i> Mobile
      </a>
    `;
    navLinks.appendChild(li);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ensureMobileNavLink();
  highlightActiveNav();
  updateNavbarStudentStatus();
});
