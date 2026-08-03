/* =====================================================
   ASAT – Student Registration Page
   ===================================================== */

import { navigate } from '../router.js';
import { setState } from '../store.js';
import { api } from '../api.js';

export function StudentRegisterPage(container) {
  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">MentiScope</div></div>
          </a>
          <a href="#/" class="btn btn-secondary btn-sm">← Back</a>
        </div>
      </nav>

      <main class="hero-section" style="flex:1;display:flex;align-items:center;justify-content:center;">
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>

        <div class="container" style="max-width:520px;position:relative;z-index:1;">
          <div class="animate-slide-up">
            <div class="text-center" style="margin-bottom:32px;">
              <div style="font-size:48px;margin-bottom:12px;">📝</div>
              <h1 style="font-size:32px;margin-bottom:8px;">Student Registration</h1>
              <p style="color:var(--color-text-muted);">Fill in your details to begin the assessment</p>
            </div>

            <div class="glass-card card-padded">
              <form id="register-form" novalidate>
                <div style="display:flex;flex-direction:column;gap:20px;">

                  <div class="form-group">
                    <label class="form-label" for="reg-name">Full Name *</label>
                    <input class="form-input" type="text" id="reg-name" placeholder="e.g. Rahul Kumar" required autocomplete="name" />
                    <span class="form-error" id="err-name"></span>
                  </div>

                  <div class="form-group">
                    <label class="form-label" for="reg-id">Student ID *</label>
                    <input class="form-input" type="text" id="reg-id" placeholder="RA2411026010977" required />
                    <span class="form-error" id="err-id"></span>
                  </div>

                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                    <div class="form-group">
                      <label class="form-label" for="reg-age">Age *</label>
                      <input class="form-input" type="number" id="reg-age" placeholder="16" min="14" max="18" required />
                      <span class="form-error" id="err-age"></span>
                    </div>
                    <div class="form-group">
                      <label class="form-label" for="reg-grade">Grade *</label>
                      <select class="form-select" id="reg-grade" required>
                        <option value="">Select Grade</option>
                        <option value="11">Grade 11</option>
                        <option value="12">Grade 12</option>
                      </select>
                      <span class="form-error" id="err-grade"></span>
                    </div>
                  </div>

                  <div class="form-group">
                    <label class="form-label" for="reg-school">School (Optional)</label>
                    <input class="form-input" type="text" id="reg-school" placeholder="Your school name" />
                  </div>

                  <div id="register-alert"></div>

                  <button class="btn btn-primary" type="submit" id="register-submit" style="margin-top:4px;">
                    🚀 Start Assessment
                  </button>
                </div>
              </form>
            </div>

            <!-- Info box -->
            <div class="alert alert-info animate-slide-up delay-300" style="margin-top:20px;">
              <strong>📋 Before you begin:</strong> Find a quiet environment, ensure stable internet, 
              and allow ~20 minutes of uninterrupted time.
            </div>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container">
          <p>© 2026 ASAT | IIT Madras MentiScope Project</p>
        </div>
      </footer>
    </div>
  `;

  const form   = document.getElementById('register-form');
  const submit = document.getElementById('register-submit');

  function validate() {
    const name  = document.getElementById('reg-name').value.trim();
    const id    = document.getElementById('reg-id').value.trim();
    const age   = parseInt(document.getElementById('reg-age').value);
    const grade = document.getElementById('reg-grade').value;

    let valid = true;

    const setErr = (fieldId, msg) => {
      const el = document.getElementById(fieldId);
      if (el) { el.textContent = msg; }
      if (msg) valid = false;
    };

    setErr('err-name',  !name ? 'Full name is required.' : '');
    setErr('err-id',    !id   ? 'Student ID is required.' :
      !/^[A-Z0-9]+$/.test(id) ? 'Must contain only uppercase letters and numbers.' : '');
    setErr('err-age',   !age  ? 'Age is required.' :
      age < 14 || age > 18  ? 'Age must be between 14-18.' : '');
    setErr('err-grade', !grade ? 'Please select your grade.' : '');

    return valid;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const student = {
      fullName:  document.getElementById('reg-name').value.trim(),
      studentId: document.getElementById('reg-id').value.trim(),
      age:       parseInt(document.getElementById('reg-age').value),
      grade:     document.getElementById('reg-grade').value,
      school:    document.getElementById('reg-school').value.trim(),
    };

    submit.disabled = true;
    submit.textContent = 'Registering...';

    try {
      const res = await api.createStudent(student);
      setState({ student: { ...student, dbId: res.studentId } });
      navigate('/instructions');
    } catch (err) {
      // If backend is unavailable, store locally and proceed
      setState({ student: { ...student, dbId: null } });
      navigate('/instructions');
    }
  });
}
