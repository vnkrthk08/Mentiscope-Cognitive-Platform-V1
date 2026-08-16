/* =====================================================
   ASAT – Faculty Portal Home
   ===================================================== */
import { navigate } from '../router.js';

export function FacultyHomePage(container) {
  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">Faculty Portal</div></div>
          </a>
          <a href="#/" class="btn btn-secondary btn-sm">← Home</a>
        </div>
      </nav>

      <main class="hero-section" style="flex:1;display:flex;align-items:center;justify-content:center;">
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>

        <div class="container" style="max-width:620px;position:relative;z-index:1;">
          <div class="animate-slide-up text-center" style="margin-bottom:40px;">
            <div style="font-size:52px;margin-bottom:12px;">👨‍🏫</div>
            <h1 style="font-size:32px;margin-bottom:8px;">Faculty Portal</h1>
            <p style="color:var(--color-text-muted);">Access the ASAT Admin Dashboard to manage students and view analytics</p>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;" class="animate-slide-up delay-200">
            <!-- Login Card -->
            <div class="glass-card card-padded text-center" style="cursor:pointer;" id="faculty-login-card">
              <div style="font-size:44px;margin-bottom:16px;">🔑</div>
              <h3 style="margin-bottom:8px;">Login</h3>
              <p style="font-size:14px;color:var(--color-text-muted);margin-bottom:20px;min-height:40px;">
                I already have an account
              </p>
              <button class="btn btn-primary w-full" id="go-login-btn">Login →</button>
            </div>

            <!-- Sign Up Card -->
            <div class="glass-card card-padded text-center" style="cursor:pointer;" id="faculty-signup-card">
              <div style="font-size:44px;margin-bottom:16px;">📝</div>
              <h3 style="margin-bottom:8px;">Sign Up</h3>
              <p style="font-size:14px;color:var(--color-text-muted);margin-bottom:20px;min-height:40px;">
                Create a new faculty account
              </p>
              <button class="btn btn-secondary w-full" id="go-signup-btn">Sign Up →</button>
            </div>
          </div>

          <div class="alert alert-info animate-slide-up delay-300" style="margin-top:28px;">
            <strong>Faculty accounts</strong> provide access to student management, assessment analytics, and report generation.
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  document.getElementById('go-login-btn').addEventListener('click', () => navigate('/faculty/login'));
  document.getElementById('go-signup-btn').addEventListener('click', () => navigate('/faculty/register'));
  document.getElementById('faculty-login-card').addEventListener('click', () => navigate('/faculty/login'));
  document.getElementById('faculty-signup-card').addEventListener('click', () => navigate('/faculty/register'));
}
