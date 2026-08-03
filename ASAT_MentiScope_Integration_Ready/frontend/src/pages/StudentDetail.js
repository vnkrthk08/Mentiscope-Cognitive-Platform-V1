/* =====================================================
   ASAT – Student Detail View (Faculty)
   ===================================================== */
import { navigate } from '../router.js';
import { api } from '../api.js';
import { getScoreStatus, getRecommendations } from '../scoring.js';
import { generatePDF } from '../PDFGenerator.js';
import Chart from 'chart.js/auto';

export function StudentDetailPage(container, params) {
  const { id } = params;

  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar" style="background:rgba(10,10,15,0.95);">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT Admin</div><div class="navbar-subtitle">Student Detail</div></div>
          </a>
          <div class="navbar-nav">
            <button class="btn btn-secondary btn-sm" id="back-btn">← Back</button>
            <button class="btn btn-secondary btn-sm" id="logout-btn2">Logout</button>
          </div>
        </div>
      </nav>

      <main style="flex:1;padding:var(--space-8) 0;">
        <div class="container" style="max-width:900px;" id="detail-container">
          <div style="padding:60px;text-align:center;">
            <div class="spinner" style="margin:0 auto 16px;"></div>
            <p style="color:var(--color-text-muted);">Loading student data…</p>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  document.getElementById('back-btn').addEventListener('click', () => navigate('/faculty/dashboard'));
  document.getElementById('logout-btn2').addEventListener('click', async () => {
    try { await api.logout(); } catch {}
    navigate('/faculty');
  });

  async function loadStudent() {
    let student, scores, moduleResults;

    try {
      const data = await api.getStudent(id);
      student       = data.student;
      scores        = data.scores;
      moduleResults = data.moduleResults || {};
    } catch {
      document.getElementById('detail-container').innerHTML = `
        <div class="glass-card card-padded text-center">
          <div style="font-size:48px;margin-bottom:16px;">❌</div>
          <h3>Student Not Found</h3>
          <p style="color:var(--color-text-muted);margin-bottom:20px;">The student data could not be loaded.</p>
          <button class="btn btn-secondary" id="back-btn2">← Back to Dashboard</button>
        </div>`;
      document.getElementById('back-btn2')?.addEventListener('click', () => navigate('/faculty/dashboard'));
      return;
    }

    const s1 = scores?.sustainedScore  ?? 0;
    const s2 = scores?.selectiveScore  ?? 0;
    const s3 = scores?.dividedScore    ?? 0;
    const s4 = scores?.executiveScore  ?? 0;
    const overall = scores?.overallScore ?? 0;
    const percentile = scores?.percentile ?? 0;
    const recs = getRecommendations({ sustained: s1, selective: s2, divided: s3, executive: s4 });
    const overallStatus = getScoreStatus(overall);
    const today = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
    const completedDate = student.completedAt
      ? new Date(student.completedAt).toLocaleDateString('en-IN')
      : today;

    const moduleData = [
      { name: 'Sustained', icon: '🔵', score: s1, weight: '25%' },
      { name: 'Selective',  icon: '🎯', score: s2, weight: '25%' },
      { name: 'Divided',    icon: '⚡', score: s3, weight: '20%' },
      { name: 'Executive',  icon: '🔄', score: s4, weight: '30%' },
    ];

    document.getElementById('detail-container').innerHTML = `
      <!-- Student Header -->
      <div class="animate-slide-up" style="margin-bottom:24px;display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:16px;">
        <div>
          <h2 style="font-size:28px;margin-bottom:4px;">${student.fullName}</h2>
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;">
            <span class="badge badge-primary">🪪 ${student.studentIdNumber || '—'}</span>
            <span class="badge badge-info">🎓 Grade ${student.grade}</span>
            <span class="badge badge-info">📅 ${completedDate}</span>
            ${student.school ? `<span class="badge badge-primary">🏫 ${student.school}</span>` : ''}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px;color:var(--color-text-muted);margin-bottom:4px;">OVERALL</div>
          <div style="font-size:40px;font-weight:800;background:var(--gradient-primary);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${overall.toFixed(1)}<span style="font-size:20px;">/100</span></div>
          <span class="badge ${overallStatus.badge}">${overallStatus.label} Attention</span>
        </div>
      </div>

      <!-- Module Scores + Radar -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
        <div class="glass-card card-padded animate-slide-up delay-100">
          <h3 style="margin-bottom:16px;">Radar Chart</h3>
          <canvas id="student-radar" width="280" height="280"></canvas>
        </div>
        <div class="glass-card card-padded animate-slide-up delay-100" style="display:flex;flex-direction:column;gap:14px;">
          <h3>Module Scores</h3>
          ${moduleData.map(m => {
            const st = getScoreStatus(m.score);
            return `
              <div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                  <span style="font-weight:600;font-size:14px;">${m.icon} ${m.name}</span>
                  <div style="display:flex;gap:8px;align-items:center;">
                    <span style="font-weight:700;">${m.score}/100</span>
                    <span class="badge ${st.badge}" style="font-size:10px;">${st.label}</span>
                  </div>
                </div>
                <div class="score-bar-bg">
                  <div class="score-bar-fill ${st.cls}" style="width:${m.score}%;transition:width 1s ease;"></div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- RT Line Chart -->
      <div class="glass-card card-padded animate-slide-up delay-200" style="margin-bottom:20px;">
        <h3 style="margin-bottom:16px;">Reaction Time Across Modules</h3>
        <canvas id="rt-chart" height="100"></canvas>
      </div>

      <!-- Advanced Analytics -->
      <div class="glass-card card-padded animate-slide-up delay-200" style="margin-bottom:20px;">
        <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>🔬</span>Advanced Scientific Analytics</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;">
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">RT Variability</div>
            <div style="font-size:20px;font-weight:700;color:var(--color-accent-1);">${moduleResults.sustained?.rtVariabilityScore || 0}%</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">Fatigue Slope</div>
            <div style="font-size:20px;font-weight:700;color:var(--color-accent-2);">${moduleResults.sustained?.fatigueScore || 0}%</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">Adaptation Speed</div>
            <div style="font-size:20px;font-weight:700;color:var(--color-accent-3);">${moduleResults.executive?.recoveryTrials?.toFixed(1) || '0.0'}</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">Impulsivity Index</div>
            <div style="font-size:20px;font-weight:700;color:var(--color-accent-4);">${moduleResults.sustained?.impulsivityIndex || 0}%</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">Attention Stability</div>
            <div style="font-size:20px;font-weight:700;color:#2196F3;">${moduleResults.sustained?.attentionStability || 0}%</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:4px;">Recovery After Errors</div>
            <div style="font-size:20px;font-weight:700;color:#9C27B0;">${moduleResults.sustained?.recoveryAfterErrors || 0}%</div>
          </div>
        </div>
      </div>

      <!-- Performance Table -->
      <div class="glass-card card-padded animate-slide-up delay-300" style="margin-bottom:20px;overflow-x:auto;">
        <h3 style="margin-bottom:16px;">Performance Details</h3>
        <table class="data-table" style="min-width:560px;">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Sustained</th>
              <th>Selective</th>
              <th>Divided</th>
              <th>Executive</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight:600;color:var(--color-text-primary);">Score</td>
              ${moduleData.map(m => {
                const displayScore = typeof m.score === 'number' ? Number(m.score).toFixed(2).replace(/\.00$/, '') : m.score;
                return `<td style="font-weight:700;">${displayScore}/100</td>`;
              }).join('')}
            </tr>
            <tr>
              <td style="font-weight:600;color:var(--color-text-primary);">Hit Rate</td>
              <td>${moduleResults.sustained?.hitRate ? moduleResults.sustained.hitRate + '%' : (moduleResults.sustainedHitRate ? moduleResults.sustainedHitRate + '%' : '—')}</td>
              <td>${moduleResults.selective?.hitRate ? moduleResults.selective.hitRate + '%' : (moduleResults.selectiveHitRate ? moduleResults.selectiveHitRate + '%' : '—')}</td>
              <td>${moduleResults.divided?.hitRate   ? moduleResults.divided.hitRate   + '%' : (moduleResults.dividedHitRate   ? moduleResults.dividedHitRate   + '%' : '—')}</td>
              <td>${moduleResults.executive ? Math.round((moduleResults.executive.correctCount / ((moduleResults.executive.correctCount + moduleResults.executive.errorCount) || 1)) * 100) + '%' : '—'}</td>
            </tr>
            <tr>
              <td style="font-weight:600;color:var(--color-text-primary);">Errors</td>
              <td>${moduleResults.sustained?.falseAlarmRate ?? moduleResults.sustainedMissed ?? '—'}</td>
              <td>${moduleResults.selective?.wrongClicks ?? moduleResults.selectiveFalseAlarms ?? '—'}</td>
              <td>${moduleResults.divided?.falsePresses ?? moduleResults.dividedFalse ?? '—'}</td>
              <td>${moduleResults.executive?.errorCount ?? moduleResults.executiveErrors ?? '—'}</td>
            </tr>
            <tr>
              <td style="font-weight:600;color:var(--color-text-primary);">Key Metric</td>
              <td>RT: ${moduleResults.sustained?.avgRT ? moduleResults.sustained.avgRT + 'ms' : (moduleResults.sustainedRtSd ? moduleResults.sustainedRtSd + 'ms' : '—')}</td>
              <td>—</td>
              <td>Split: ${moduleResults.divided?.splitCost ? moduleResults.divided.splitCost + 'ms' : (moduleResults.dividedSplitCost ? moduleResults.dividedSplitCost + 'ms' : '—')}</td>
              <td>Switch: ${moduleResults.executive?.switchCost ? moduleResults.executive.switchCost + 'ms' : (moduleResults.executiveSwitchCost ? moduleResults.executiveSwitchCost + 'ms' : '—')}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Recommendations -->
      <div class="glass-card card-padded animate-slide-up delay-300" style="margin-bottom:24px;">
        <h3 style="margin-bottom:16px;">Recommendations</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div>
            <h4 style="font-size:14px;color:var(--color-text-muted);margin-bottom:10px;">Study Strategies</h4>
            ${recs.strategies.slice(0,3).map(s => `
              <div style="font-size:13px;color:var(--color-text-secondary);padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                • ${s}
              </div>
            `).join('')}
          </div>
          <div>
            <h4 style="font-size:14px;color:var(--color-accent-2);margin-bottom:10px;">✅ Career Fit</h4>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
              ${recs.careers.good.map(c => `<span class="badge badge-success">${c}</span>`).join('')}
            </div>
            ${recs.careers.poor.length ? `
              <h4 style="font-size:14px;color:var(--color-accent-4);margin-top:12px;margin-bottom:10px;">⚠️ Challenging</h4>
              <div style="display:flex;flex-wrap:wrap;gap:6px;">
                ${recs.careers.poor.map(c => `<span class="badge badge-error">${c}</span>`).join('')}
              </div>
            ` : ''}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="animate-slide-up delay-400" style="display:flex;gap:12px;flex-wrap:wrap;">
        <button class="btn btn-primary" id="dl-report-btn">📥 Download Report</button>
        <button class="btn btn-secondary btn-sm" id="back-btn3">← Back to Dashboard</button>
      </div>
    `;

    // Radar chart
    const radarCtx = document.getElementById('student-radar');
    if (radarCtx) {
      new Chart(radarCtx, {
        type: 'radar',
        data: {
          labels: ['Sustained', 'Selective', 'Divided', 'Executive'],
          datasets: [{
            data: [s1, s2, s3, s4],
            backgroundColor: 'rgba(0,188,212,0.15)',
            borderColor: '#00BCD4',
            borderWidth: 2,
            pointBackgroundColor: '#00BCD4',
            pointRadius: 5,
          }],
        },
        options: {
          responsive: true,
          scales: {
            r: {
              beginAtZero: true, max: 100,
              grid:       { color: 'rgba(255,255,255,0.08)' },
              angleLines: { color: 'rgba(255,255,255,0.08)' },
              pointLabels: { color: 'rgba(255,255,255,0.7)', font: { size: 12 } },
              ticks: { color: 'rgba(255,255,255,0.4)', stepSize: 25, backdropColor: 'transparent' },
            },
          },
          plugins: { legend: { display: false } },
        },
      });
    }

    // RT line chart
    const rtCtx = document.getElementById('rt-chart');
    if (rtCtx) {
      new Chart(rtCtx, {
        type: 'bar',
        data: {
          labels: ['Sustained', 'Selective', 'Divided', 'Executive'],
          datasets: [{
            label: 'Avg Reaction Time (ms)',
            data: [
              moduleResults.sustainedAvgRt ?? 450,
              moduleResults.selectiveAvgRt ?? 420,
              moduleResults.dividedAvgRt   ?? 480,
              moduleResults.executiveAvgRt ?? 430,
            ],
            backgroundColor: [
              'rgba(30,136,229,0.6)',
              'rgba(0,188,212,0.6)',
              'rgba(251,140,0,0.6)',
              'rgba(142,36,170,0.6)',
            ],
            borderColor: [
              '#1E88E5', '#00BCD4', '#FB8C00', '#8E24AA',
            ],
            borderWidth: 2,
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { labels: { color: 'rgba(255,255,255,0.7)' } } },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: 'rgba(255,255,255,0.6)' } },
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(255,255,255,0.06)' },
              ticks: { color: 'rgba(255,255,255,0.6)' },
              title: { display: true, text: 'RT (ms)', color: 'rgba(255,255,255,0.5)' },
            },
          },
        },
      });
    }

    document.getElementById('back-btn3')?.addEventListener('click', () => navigate('/faculty/dashboard'));
    document.getElementById('dl-report-btn')?.addEventListener('click', () => {
      generatePDF({
        student: {
          fullName: student.fullName,
          studentId: student.studentIdNumber,
          age: student.age,
          grade: student.grade,
          school: student.school,
        },
        scores: { sustained: s1, selective: s2, divided: s3, executive: s4, overall, percentile },
        moduleResults: {},
        recs,
        today: completedDate,
      });
    });
  }

  loadStudent();
}
