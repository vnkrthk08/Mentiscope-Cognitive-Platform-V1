/* =====================================================
   ASAT – Instructions Page
   ===================================================== */

import { navigate } from '../router.js';
import { getState } from '../store.js';

export function InstructionsPage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">MentiScope</div></div>
          </a>
          <div class="badge badge-info">👤 ${student.fullName}</div>
        </div>
      </nav>

      <main style="flex:1;padding:var(--space-10) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-1" style="opacity:0.07;"></div>
        <div class="container" style="max-width:760px;position:relative;z-index:1;">

          <div class="animate-slide-up text-center" style="margin-bottom:40px;">
            <div style="font-size:52px;margin-bottom:12px;">📋</div>
            <h1 style="font-size:32px;margin-bottom:8px;">Assessment Instructions</h1>
            <p>Read carefully before starting. You cannot pause once a module begins.</p>
          </div>

          <!-- Module Overview -->
          <div class="glass-card card-padded animate-slide-up delay-100" style="margin-bottom:24px;">
            <h3 style="margin-bottom:20px;display:flex;align-items:center;gap:8px;">
              <span>🗺️</span> What You Will Do
            </h3>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
              ${[
                { num:'1', icon:'🔵', name:'Sustained', time:'~5 min', desc:'Watch for a blue triangle among shapes' },
                { num:'2', icon:'🎯', name:'Selective',  time:'~4 min', desc:'Click the target in a row of shapes' },
                { num:'3', icon:'⚡', name:'Divided',    time:'~4 min', desc:'Monitor two panels simultaneously' },
                { num:'4', icon:'🔄', name:'Executive',  time:'~5 min', desc:'Adapt to changing rules quickly' },
              ].map(m => `
                <div style="background:rgba(255,255,255,0.03);border:1px solid var(--color-border);border-radius:var(--radius-md);padding:14px;text-align:center;">
                  <div style="font-size:24px;margin-bottom:6px;">${m.icon}</div>
                  <div style="font-weight:700;font-size:13px;color:var(--color-accent-1);">Module ${m.num}</div>
                  <div style="font-weight:600;font-size:13px;color:var(--color-text-primary);margin:2px 0;">${m.name}</div>
                  <div style="font-size:11px;color:var(--color-text-muted);margin-bottom:6px;">${m.desc}</div>
                  <div class="badge badge-primary" style="font-size:10px;">${m.time}</div>
                </div>
              `).join('')}
            </div>
            <div class="alert alert-info">
              <strong>⏱️ Total time: approximately 20 minutes</strong>
            </div>
          </div>

          <!-- Key Rules -->
          <div class="glass-card card-padded animate-slide-up delay-200" style="margin-bottom:24px;">
            <h3 style="margin-bottom:20px;display:flex;align-items:center;gap:8px;"><span>⚡</span> Key Rules</h3>
            <div style="display:flex;flex-direction:column;gap:14px;">
              ${[
                ['⌨️', 'SPACEBAR or Click', 'Your primary response keys throughout the assessment'],
                ['🎯', 'Accuracy Matters', 'Think before responding — precision is more important than speed'],
                ['🔇', 'Quiet Environment', 'Find a quiet room with no distractions before starting'],
                ['💻', 'Full Screen Recommended', 'Maximize your browser for the best experience'],
                ['🚫', 'No Pausing', 'Each module runs continuously — plan accordingly'],
              ].map(([icon, title, desc]) => `
                <div style="display:flex;gap:14px;align-items:flex-start;padding:10px;border-radius:var(--radius-sm);background:rgba(255,255,255,0.02);">
                  <span style="font-size:20px;width:28px;flex-shrink:0;text-align:center;">${icon}</span>
                  <div>
                    <div style="font-weight:600;font-size:14px;color:var(--color-text-primary);">${title}</div>
                    <div style="font-size:13px;color:var(--color-text-secondary);">${desc}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Practice note -->
          <div class="glass-card card-padded animate-slide-up delay-300" style="margin-bottom:32px;">
            <h3 style="margin-bottom:12px;display:flex;align-items:center;gap:8px;"><span>🏋️</span> Practice Round</h3>
            <p style="font-size:14px;margin-bottom:8px;">Before the real assessment, you will complete a <strong style="color:var(--color-accent-1);">5-trial practice round</strong> to familiarize yourself with the task.</p>
            <p style="font-size:14px;">You need to score <strong style="color:var(--color-accent-2);">≥80% correct</strong> in the practice to proceed to the real assessment.</p>
          </div>

          <div class="animate-slide-up delay-400 text-center">
            <button class="btn btn-primary btn-lg" id="start-practice-btn" style="min-width:240px;">
              🏋️ Start Practice Round
            </button>
            <p style="font-size:13px;color:var(--color-text-muted);margin-top:16px;">
              The practice will guide you step-by-step before the real test begins.
            </p>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  document.getElementById('start-practice-btn').addEventListener('click', () => navigate('/practice'));
}
