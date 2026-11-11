/**
 * Login & Registration Controller for CareerAI System.
 * Handles client-side validation, authentication requests, and session establishment.
 */

function switchTab(tab) {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const loginTabBtn = document.getElementById('tab-login-btn');
  const registerTabBtn = document.getElementById('tab-register-btn');
  const alertBox = document.getElementById('auth-alert');

  if (alertBox) {
    alertBox.style.display = 'none';
  }

  if (tab === 'login') {
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
    loginTabBtn.classList.add('active');
    registerTabBtn.classList.remove('active');
  } else {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    loginTabBtn.classList.remove('active');
    registerTabBtn.classList.add('active');
  }
}

function showAlert(message, type = 'error') {
  const alertBox = document.getElementById('auth-alert');
  if (!alertBox) return;

  alertBox.className = `auth-alert alert-${type}`;
  alertBox.innerHTML = `
    <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
    <span>${message}</span>
  `;
  alertBox.style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', () => {
  // Check if already logged in
  checkExistingAuth();

  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  if (loginForm) {
    loginForm.addEventListener('submit', handleLoginSubmit);
  }

  if (registerForm) {
    registerForm.addEventListener('submit', handleRegisterSubmit);
  }
});

async function checkExistingAuth() {
  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    if (data.status === 'success' && data.authenticated && data.user) {
      // User is already signed in
      showToast(`Signed in as ${data.user.username}. Redirecting...`, 'info');
      setTimeout(() => {
        window.location.href = data.has_profile ? '/dashboard' : '/profile';
      }, 800);
    }
  } catch (e) {
    // Guest
  }
}

// 1. Handle Sign In
async function handleLoginSubmit(e) {
  e.preventDefault();

  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const btn = document.getElementById('btn-login-submit');

  if (!username || !password) {
    showAlert('Please fill in both your username/email and password.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In to CareerAI';

    if (data.status === 'success') {
      showAlert(data.message, 'success');
      showToast(data.message, 'success');
      setTimeout(() => {
        window.location.href = data.has_profile ? '/dashboard' : '/profile';
      }, 700);
    } else {
      showAlert(data.message || 'Authentication failed. Please verify your credentials.');
    }
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In to CareerAI';
    showAlert(`Network error: ${err.message}`);
  }
}

// 2. Handle Registration
async function handleRegisterSubmit(e) {
  e.preventDefault();

  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const dob = document.getElementById('reg-dob').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirmPassword = document.getElementById('reg-password-confirm').value;
  const btn = document.getElementById('btn-register-submit');

  // Validations
  if (!username || username.length < 3) {
    showAlert('User name must be at least 3 characters long.');
    return;
  }

  if (!email || !email.includes('@')) {
    showAlert('Please enter a valid email address.');
    return;
  }

  if (!dob) {
    showAlert('Please enter your Date of Birth (D.O.B).');
    return;
  }

  if (!password || password.length < 6) {
    showAlert('Password must be at least 6 characters long.');
    return;
  }

  if (password !== confirmPassword) {
    showAlert('Passwords do not match. Please re-enter your password.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        dob,
        password
      })
    });

    const data = await res.json();
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-user-check"></i> Register & Continue';

    if (data.status === 'success') {
      showAlert(data.message, 'success');
      showToast('Registration successful! Redirecting to setup your student profile...', 'success');
      setTimeout(() => {
        window.location.href = '/profile';
      }, 800);
    } else {
      showAlert(data.message || 'Registration failed.');
    }
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-user-check"></i> Register & Continue';
    showAlert(`Network error: ${err.message}`);
  }
}
