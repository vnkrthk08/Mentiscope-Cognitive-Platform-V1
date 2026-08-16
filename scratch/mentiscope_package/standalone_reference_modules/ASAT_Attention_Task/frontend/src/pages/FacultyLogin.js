/* =====================================================
   ASAT – Faculty Login Page
   ===================================================== */
import { navigate } from '../router.js';
import { setState } from '../store.js';
import { api } from '../api.js';

export function FacultyLoginPage(container) {
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

        <div class="container" style="max-width:440px;position:relative;z-index:1;">
          <div class="animate-slide-up text-center" style="margin-bottom:28px;">
            <div style="font-size:44px;margin-bottom:10px;">🔑</div>
            <h1 style="font-size:28px;margin-bottom:6px;">Faculty Login</h1>
            <p style="color:var(--color-text-muted);">Sign in to access your dashboard</p>
          </div>

          <div class="glass-card card-padded animate-slide-up delay-100">
            <form id="faculty-login-form" novalidate>
              <div style="display:flex;flex-direction:column;gap:18px;">
                <div class="form-group">
                  <label class="form-label" for="flog-username">Username</label>
                  <input class="form-input" type="text" id="flog-username" placeholder="Your username" required autocomplete="username" />
                  <span class="form-error" id="flogerr-username"></span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="flog-password">Password</label>
                  <div style="position:relative;">
                    <input class="form-input" type="password" id="flog-password" placeholder="Your password" required autocomplete="current-password" style="padding-right:48px;" />
                    <button type="button" id="toggle-pw" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:var(--color-text-muted);font-size:18px;">👁</button>
                  </div>
                  <span class="form-error" id="flogerr-password"></span>
                </div>

                <div id="flog-alert"></div>

                <div style="display:flex;gap:12px;">
                  <button class="btn btn-primary" type="submit" id="flog-submit" style="flex:1;">
                    Login →
                  </button>
                </div>

                <p style="text-align:center;font-size:14px;color:var(--color-text-muted);">
                  Don't have an account?
                  <a href="#/faculty/register" style="color:var(--color-accent-1);font-weight:600;">Sign Up</a>
                </p>
              </div>
            </form>
          </div>

          <!-- Demo hint -->
          <div class="alert alert-info animate-slide-up delay-200" style="margin-top:20px;font-size:13px;">
            <strong>Demo:</strong> Register a faculty account to get started. 
            Credentials are stored securely on the local server.
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  const form   = document.getElementById('faculty-login-form');
  const submit = document.getElementById('flog-submit');
  const alert  = document.getElementById('flog-alert');

  // Toggle password visibility
  document.getElementById('toggle-pw').addEventListener('click', () => {
    const pw = document.getElementById('flog-password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('flog-username').value.trim();
    const password = document.getElementById('flog-password').value;

    document.getElementById('flogerr-username').textContent = '';
    document.getElementById('flogerr-password').textContent = '';
    alert.innerHTML = '';

    if (!username) { document.getElementById('flogerr-username').textContent = 'Username is required.'; return; }
    if (!password) { document.getElementById('flogerr-password').textContent = 'Password is required.'; return; }

    submit.disabled = true;
    submit.textContent = 'Signing in...';

    try {
      const res = await api.login({ username, password });
      setState({ faculty: res.faculty });
      navigate('/faculty/dashboard');
    } catch (err) {
      alert.innerHTML = `<div class="alert alert-error">❌ ${err.message || 'Invalid username or password.'}</div>`;
      submit.disabled = false;
      submit.textContent = 'Login →';
    }
  });
}
