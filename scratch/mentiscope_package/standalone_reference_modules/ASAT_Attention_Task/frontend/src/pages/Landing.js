/* =====================================================
   ASAT – Landing Page
   ===================================================== */

import { navigate } from '../router.js';

export function LandingPage(container) {
  container.innerHTML = `
    <div class="page-wrapper">
      <!-- Navbar -->
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div>
              <div class="navbar-title">ASAT</div>
              <div class="navbar-subtitle">MentiScope · IIT Madras</div>
            </div>
          </a>
          <nav class="navbar-nav">
            <a href="#/about" class="btn btn-secondary btn-sm" id="nav-about">About</a>
          </nav>
        </div>
      </nav>

      <!-- Hero -->
      <main class="hero-section" style="flex:1; position:relative; overflow:hidden;">
        <!-- Background orbs -->
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>
        <div class="bg-orb bg-orb-3"></div>

        <div class="container" style="position:relative;z-index:1;">

          <!-- Hero Text -->
          <div class="text-center animate-slide-up" style="margin-bottom:56px;">
            <div style="font-size:72px;margin-bottom:16px;animation:float 3s ease-in-out infinite;">🧠</div>
            <h1 class="gradient-text" style="margin-bottom:16px;">
              Adaptive Shape Attention Task
            </h1>
            <p style="font-size:18px;color:var(--color-text-secondary);max-width:540px;margin:0 auto 8px;">
              Cognitive Attention Assessment Platform
            </p>
            <p style="font-size:15px;color:var(--color-text-muted);font-style:italic;max-width:460px;margin:0 auto;">
              "Measure your attention. Unlock your potential."
            </p>
          </div>

          <!-- Portal Cards -->
          <div class="animate-slide-up delay-200" style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:640px;margin:0 auto 56px;">

            <!-- Student Card -->
            <div class="glass-card card-padded" style="text-align:center;cursor:pointer;" id="landing-student-card">
              <div style="font-size:48px;margin-bottom:16px;">🎓</div>
              <h3 style="margin-bottom:8px;">Student</h3>
              <p style="font-size:14px;margin-bottom:20px;min-height:40px;">Take the attention assessment and get your cognitive profile</p>
              <button class="btn btn-primary w-full" id="landing-student-btn">Start Assessment</button>
            </div>

            <!-- Faculty Card -->
            <div class="glass-card card-padded" style="text-align:center;cursor:pointer;" id="landing-faculty-card">
              <div style="font-size:48px;margin-bottom:16px;">👨‍🏫</div>
              <h3 style="margin-bottom:8px;">Faculty</h3>
              <p style="font-size:14px;margin-bottom:20px;min-height:40px;">Access admin dashboard, manage students & view analytics</p>
              <button class="btn btn-secondary w-full" id="landing-faculty-btn">Login / Signup</button>
            </div>
          </div>

          <!-- Divider -->
          <div class="divider animate-fade-in delay-300"></div>

          <!-- About Section -->
          <div class="animate-slide-up delay-400" style="max-width:800px;margin:0 auto;">
            <h2 class="text-center" style="margin-bottom:32px;">About this Assessment</h2>

            <div class="glass-card card-padded" style="margin-bottom:32px;">
              <p style="font-size:15px;line-height:1.8;margin-bottom:20px;">
                ASAT is a <strong style="color:var(--color-accent-1);">scientifically validated</strong> attention assessment
                based on the <strong style="color:var(--color-accent-1);">CHC (Cattell-Horn-Carroll) Cognitive Ability Framework</strong>.
                Developed at IIT Madras as part of the MentiScope research internship program,
                ASAT measures four dimensions of attention with research-grade precision.
              </p>

              <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                ${[
                  ['🎯', '4 Attention Modules', 'Sustained, Selective, Divided & Executive'],
                  ['⏱️', '~20 Minutes Total', 'Efficient, non-fatiguing assessment'],
                  ['📊', 'Adaptive Difficulty', 'Algorithm adjusts to your performance'],
                  ['📄', 'Research-grade Scoring', 'CHC framework validated metrics'],
                ].map(([icon, title, desc]) => `
                  <div style="display:flex;gap:12px;align-items:flex-start;">
                    <span style="font-size:24px;flex-shrink:0;">${icon}</span>
                    <div>
                      <div style="font-weight:600;font-size:14px;color:var(--color-text-primary);margin-bottom:2px;">${title}</div>
                      <div style="font-size:13px;color:var(--color-text-muted);">${desc}</div>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- Module Preview Cards -->
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
              ${[
                { icon:'🔵', name:'Sustained', desc:'Continuous focus over time', pct:'25%' },
                { icon:'🎯', name:'Selective', desc:'Focus amid distractors',     pct:'25%' },
                { icon:'⚡', name:'Divided',   desc:'Dual-stream monitoring',     pct:'20%' },
                { icon:'🔄', name:'Executive', desc:'Adaptive rule switching',    pct:'30%' },
              ].map(m => `
                <div class="glass-card" style="padding:16px;text-align:center;">
                  <div style="font-size:28px;margin-bottom:8px;">${m.icon}</div>
                  <div style="font-weight:600;font-size:13px;color:var(--color-text-primary);margin-bottom:4px;">${m.name}</div>
                  <div style="font-size:11px;color:var(--color-text-muted);margin-bottom:8px;">${m.desc}</div>
                  <div class="badge badge-info" style="font-size:10px;">${m.pct} weight</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="footer">
        <div class="container">
          <p>© 2026 ASAT &nbsp;|&nbsp; IIT Madras MentiScope Project &nbsp;|&nbsp; Internship Research Platform</p>
        </div>
      </footer>
    </div>
  `;

  // Events
  document.getElementById('landing-student-btn').addEventListener('click', () => navigate('/register'));
  document.getElementById('landing-student-card').addEventListener('click', () => navigate('/register'));
  document.getElementById('landing-faculty-btn').addEventListener('click', () => navigate('/faculty'));
  document.getElementById('landing-faculty-card').addEventListener('click', () => navigate('/faculty'));
}
