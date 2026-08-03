/* =====================================================
   ASAT – Faculty Registration Page
   ===================================================== */
import { navigate } from '../router.js';
import { api } from '../api.js';

export function FacultyRegisterPage(container) {
  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">Faculty Portal</div></div>
          </a>
          <a href="#/faculty" class="btn btn-secondary btn-sm">← Back</a>
        </div>
      </nav>

      <main class="hero-section" style="flex:1;display:flex;align-items:center;justify-content:center;">
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>

        <div class="container" style="max-width:500px;position:relative;z-index:1;">
          <div class="animate-slide-up text-center" style="margin-bottom:28px;">
            <div style="font-size:44px;margin-bottom:10px;">📝</div>
            <h1 style="font-size:28px;margin-bottom:6px;">Faculty Registration</h1>
            <p style="color:var(--color-text-muted);">Create your ASAT faculty account</p>
          </div>

          <div class="glass-card card-padded animate-slide-up delay-100">
            <form id="faculty-reg-form" novalidate>
              <div style="display:flex;flex-direction:column;gap:18px;">
                <div class="form-group">
                  <label class="form-label" for="freg-name">Full Name *</label>
                  <input class="form-input" type="text" id="freg-name" placeholder="e.g. Dr. Priya Sharma" required autocomplete="name" />
                  <span class="form-error" id="ferr-name"></span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="freg-email">Email *</label>
                  <input class="form-input" type="email" id="freg-email" placeholder="faculty@school.edu" required autocomplete="email" />
                  <span class="form-error" id="ferr-email"></span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="freg-username">Username *</label>
                  <input class="form-input" type="text" id="freg-username" placeholder="Choose a username" required autocomplete="username" />
                  <span class="form-error" id="ferr-username"></span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="freg-password">Password *</label>
                  <input class="form-input" type="password" id="freg-password" placeholder="Min 8 characters" required autocomplete="new-password" />
                  <span class="form-error" id="ferr-password"></span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="freg-confirm">Confirm Password *</label>
                  <input class="form-input" type="password" id="freg-confirm" placeholder="Repeat password" required autocomplete="new-password" />
                  <span class="form-error" id="ferr-confirm"></span>
                </div>

                <div id="freg-alert"></div>

                <button class="btn btn-primary" type="submit" id="freg-submit">
                  Create Account →
                </button>

                <p style="text-align:center;font-size:14px;color:var(--color-text-muted);">
                  Already have an account?
                  <a href="#/faculty/login" style="color:var(--color-accent-1);font-weight:600;">Login</a>
                </p>
              </div>
            </form>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  const form   = document.getElementById('faculty-reg-form');
  const submit = document.getElementById('freg-submit');
  const alert  = document.getElementById('freg-alert');

  function setErr(id, msg) {
    const el = document.getElementById(id);
    if (el) el.textContent = msg;
  }

  function validate() {
    const name     = document.getElementById('freg-name').value.trim();
    const email    = document.getElementById('freg-email').value.trim();
    const username = document.getElementById('freg-username').value.trim();
    const password = document.getElementById('freg-password').value;
    const confirm  = document.getElementById('freg-confirm').value;
    let valid = true;

    const fail = (id, msg) => { setErr(id, msg); valid = false; };

    setErr('ferr-name', ''); setErr('ferr-email', ''); setErr('ferr-username', '');
    setErr('ferr-password', ''); setErr('ferr-confirm', '');

    if (!name)    fail('ferr-name', 'Full name is required.');
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
                  fail('ferr-email', 'Valid email address required.');
    if (!username || username.length < 3)
                  fail('ferr-username', 'Username must be at least 3 characters.');
    if (!password || password.length < 8)
                  fail('ferr-password', 'Password must be at least 8 characters.');
    if (password !== confirm)
                  fail('ferr-confirm', 'Passwords do not match.');

    return valid;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validate()) return;

    submit.disabled = true;
    submit.textContent = 'Creating account...';
    alert.innerHTML = '';

    try {
      await api.register({
        fullName: document.getElementById('freg-name').value.trim(),
        email:    document.getElementById('freg-email').value.trim(),
        username: document.getElementById('freg-username').value.trim(),
        password: document.getElementById('freg-password').value,
      });
      alert.innerHTML = `<div class="alert alert-success">✅ Account created! Redirecting to login...</div>`;
      setTimeout(() => navigate('/faculty/login'), 1200);
    } catch (err) {
      alert.innerHTML = `<div class="alert alert-error">❌ ${err.message || 'Registration failed. Username or email may already exist.'}</div>`;
      submit.disabled = false;
      submit.textContent = 'Create Account →';
    }
  });
}
