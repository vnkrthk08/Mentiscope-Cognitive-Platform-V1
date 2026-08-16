/* =====================================================
   ASAT – Faculty Admin Dashboard
   ===================================================== */
import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { api } from '../api.js';

export function FacultyDashboardPage(container) {
  let allStudents  = [];
  let searchQuery  = '';

  container.innerHTML = `
    <div class="page-wrapper">
      <!-- Admin Navbar -->
      <nav class="navbar" style="background:rgba(10,10,15,0.95);">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT Admin</div><div class="navbar-subtitle">Faculty Dashboard</div></div>
          </a>
          <div class="navbar-nav">
            <span id="faculty-name-badge" class="badge badge-info" style="font-size:12px;">👤 Faculty</span>
            <button class="btn btn-secondary btn-sm" id="logout-btn">Logout</button>
          </div>
        </div>
      </nav>

      <main style="flex:1;padding:var(--space-8) 0;">
        <div class="container">

          <!-- Stats Row -->
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px;" id="stats-grid">
            ${['⏳', '⏳', '⏳', '⏳'].map(() => `
              <div class="stat-card">
                <div class="stat-value" style="font-size:28px;">—</div>
                <div class="stat-label">Loading…</div>
              </div>
            `).join('')}
          </div>

          <!-- Student Table -->
          <div class="glass-card" style="overflow:hidden;">
            <div style="padding:20px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;border-bottom:1px solid var(--color-border);">
              <h3 style="display:flex;align-items:center;gap:8px;"><span>👥</span> Student Assessments</h3>
              <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                <input class="form-input" type="search" id="student-search"
                  placeholder="🔍 Search by name or ID…"
                  style="width:220px;padding:8px 12px;" />
                <button class="btn btn-secondary btn-sm" id="export-csv-btn">📥 Export CSV</button>
              </div>
            </div>

            <div id="student-table-wrap" style="overflow-x:auto;">
              <div style="padding:40px;text-align:center;">
                <div class="spinner" style="margin:0 auto 16px;"></div>
                <p style="color:var(--color-text-muted);">Loading students…</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  // Check auth + load data
  async function init() {
    try {
      const me = await api.me();
      setState({ faculty: me.faculty });
      const nameEl = document.getElementById('faculty-name-badge');
      if (nameEl) nameEl.textContent = `👤 ${me.faculty.fullName}`;
    } catch (err) {
      console.error('[Dashboard] Auth check failed:', err);
      navigate('/faculty/login');
      return;
    }

    try {
      const data = await api.listStudents();
      console.log('[Dashboard] Loaded students:', data.students?.length);
      allStudents = data.students || [];
      renderStats(allStudents);
      renderTable(allStudents);
    } catch (err) {
      console.error('[Dashboard] Failed to load students:', err);
      const wrap = document.getElementById('student-table-wrap');
      if (wrap) wrap.innerHTML = `<div style="padding:40px;text-align:center;color:var(--color-accent-4);">❌ Failed to load students: ${err.message}. Is the backend running?</div>`;
    }
  }

  function renderStats(students) {
    const total      = students.length;
    const completed  = students.filter(s => s.overall !== null && s.overall !== undefined).length;
    const avgScore   = completed
      ? Math.round(students.filter(s => s.overall).reduce((a, s) => a + s.overall, 0) / completed)
      : 0;
    const recentDate = students.length ? students[0].completedAt?.split('T')[0] ?? '—' : '—';

    const statsGrid = document.getElementById('stats-grid');
    if (!statsGrid) return;
    statsGrid.innerHTML = [
      { icon: '👥', value: total,          label: 'Total Students' },
      { icon: '✅', value: completed,       label: 'Completed' },
      { icon: '📊', value: avgScore + '%',  label: 'Avg Score' },
      { icon: '📅', value: recentDate,      label: 'Last Assessment' },
    ].map(({ icon, value, label }) => `
      <div class="stat-card animate-slide-up">
        <div style="font-size:28px;margin-bottom:4px;">${icon}</div>
        <div class="stat-value" style="font-size:28px;">${value}</div>
        <div class="stat-label">${label}</div>
      </div>
    `).join('');
  }

  function renderTable(students) {
    const wrap = document.getElementById('student-table-wrap');
    if (!wrap) return;

    const filtered = students.filter(s => {
      const q = searchQuery.toLowerCase();
      return !q || s.fullName?.toLowerCase().includes(q) || s.studentIdNumber?.toLowerCase().includes(q);
    });

    if (filtered.length === 0) {
      wrap.innerHTML = `
        <div style="padding:60px;text-align:center;">
          <div style="font-size:48px;margin-bottom:16px;">📭</div>
          <p style="color:var(--color-text-muted);">
            ${searchQuery ? 'No students match your search.' : 'No student assessments found yet.'}
          </p>
          ${!searchQuery ? '<p style="color:var(--color-text-muted);font-size:13px;margin-top:8px;">Students will appear here after completing the assessment.</p>' : ''}
        </div>`;
      return;
    }

    wrap.innerHTML = `
      <table class="data-table" style="min-width:700px;">
        <thead>
          <tr>
            <th>Student</th>
            <th>ID</th>
            <th>Grade</th>
            <th>Overall Score</th>
            <th>Status</th>
            <th>Completed</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${filtered.map(s => {
            const score  = s.overall !== null && s.overall !== undefined ? Number(s.overall).toFixed(1) : null;
            const badge  = score === null ? '' : Number(score) >= 65 ? 'badge-success' : Number(score) >= 50 ? 'badge-warning' : 'badge-error';
            const label  = score === null ? '—' : Number(score) >= 80 ? 'Excellent' : Number(score) >= 65 ? 'Good' : Number(score) >= 50 ? 'Average' : 'Needs Work';
            const date   = s.completedAt ? new Date(s.completedAt).toLocaleDateString('en-IN') : '—';
            const navId  = s.studentId;  // Always use the DB primary key
            return `
              <tr>
                <td style="font-weight:600;color:var(--color-text-primary);">${s.fullName}</td>
                <td style="font-family:monospace;font-size:13px;">${s.studentIdNumber || '—'}</td>
                <td>Grade ${s.grade}</td>
                <td style="font-weight:700;">${score !== null ? score + '/100' : '—'}</td>
                <td>${score !== null ? `<span class="badge ${badge}">${label}</span>` : '<span class="badge badge-primary">Pending</span>'}</td>
                <td style="font-size:13px;color:var(--color-text-muted);">${date}</td>
                <td>
                  <button class="btn btn-outline btn-sm view-student-btn" data-id="${navId}">
                    View →
                  </button>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;

    // Attach view handlers
    wrap.querySelectorAll('.view-student-btn').forEach(btn => {
      btn.addEventListener('click', () => navigate(`/faculty/student/${btn.dataset.id}`));
    });
  }

  // Search
  document.getElementById('student-search').addEventListener('input', (e) => {
    searchQuery = e.target.value;
    renderTable(allStudents);
  });

  // Logout
  document.getElementById('logout-btn').addEventListener('click', async () => {
    try { await api.logout(); } catch {}
    setState({ faculty: null });
    navigate('/faculty');
  });

  // CSV Export
  document.getElementById('export-csv-btn').addEventListener('click', async () => {
    try {
      const res = await api.exportCSV();
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url;
      a.download = `ASAT_Students_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Export failed. Make sure the backend server is running.');
    }
  });

  init();
}
