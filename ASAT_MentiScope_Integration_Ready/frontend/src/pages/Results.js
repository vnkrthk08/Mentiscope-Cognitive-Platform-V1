/* =====================================================
   ASAT – Results Dashboard
   Radar chart, module scores, recommendations, PDF
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState, resetAssessment } from '../store.js';
import { scoreOverall, estimatePercentile, getScoreStatus, getRecommendations } from '../scoring.js';
import { api } from '../api.js';
import Chart from 'chart.js/auto';

export function ResultsPage(container) {
  const { student, moduleResults } = getState();
  if (!student) { navigate('/register'); return; }
  if (!moduleResults.sustained && !moduleResults.selective && !moduleResults.divided && !moduleResults.executive) {
    navigate('/module/sustained'); return;
  }

  // Compute final scores (fall back gracefully if some modules missing)
  const s1 = moduleResults.sustained?.score ?? 60;
  const s2 = moduleResults.selective?.score ?? 60;
  const s3 = moduleResults.divided?.score   ?? 60;
  const s4 = moduleResults.executive?.score ?? 60;

  const overall   = scoreOverall({ sustained: s1, selective: s2, divided: s3, executive: s4 });
  const percentile = estimatePercentile(overall);
  const recs       = getRecommendations({ sustained: s1, selective: s2, divided: s3, executive: s4 });

  const moduleData = [
    { name: 'Sustained',  score: s1, icon: '🔵', weight: '25%', desc: 'Continuous focus',         raw: moduleResults.sustained },
    { name: 'Selective',  score: s2, icon: '🎯', weight: '25%', desc: 'Focus amid distractors',   raw: moduleResults.selective },
    { name: 'Divided',    score: s3, icon: '⚡', weight: '20%', desc: 'Dual-stream monitoring',   raw: moduleResults.divided },
    { name: 'Executive',  score: s4, icon: '🔄', weight: '30%', desc: 'Adaptive rule switching',  raw: moduleResults.executive },
  ];

  const overallStatus = getScoreStatus(overall);
  const today = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });

  // Save scores to state
  setState({ scores: { sustained: s1, selective: s2, divided: s3, executive: s4, overall, percentile } });

  // Persist to backend (best-effort)
  // We call the dedicated /api/scores endpoint which always uses student_id, never session_id.
  if (student.dbId) {
    (async () => {
      try {
        // Step 1: Ensure a session exists for this student. 
        // If ModuleSustained already created one it's in state; otherwise create it now.
        let sessionId = student.sessionId || null;
        if (!sessionId) {
          console.log(`[Results] No sessionId in state for student ${student.dbId} — creating one now.`);
          const sess = await api.createSession({ studentId: student.dbId });
          sessionId = sess.sessionId;
          console.log(`[Results] Created session ${sessionId} for student ${student.dbId}`);
          setState({ student: { ...student, sessionId } });
        } else {
          console.log(`[Results] Using existing sessionId ${sessionId} for student ${student.dbId}`);
        }

        // Step 2: Save final scores, emit to parent MentiScope frame
        console.log(`[Results] Emit scores to parent for ${student.dbId}:`, { s1, s2, s3, s4, overall });
        
        window.parent.postMessage({
          type: "ASAT_COMPLETED",
          payload: {
            scores: { sustained: s1, selective: s2, divided: s3, executive: s4, overall, percentile },
            moduleResults: getState().moduleResults
          }
        }, "*");
        
        console.log(`[Results] Scores emitted to parent window.`);
      } catch (err) {
        console.error('[Results] Failed to save scores to backend:', err);
      }
    })();
  }

  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">Results</div></div>
          </a>
          <div class="badge badge-info">👤 ${student.fullName}</div>
        </div>
      </nav>

      <main style="flex:1;padding:var(--space-10) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-1" style="opacity:0.06;"></div>
        <div class="container" style="max-width:880px;position:relative;z-index:1;">

          <!-- Header -->
          <div class="animate-slide-up text-center" style="margin-bottom:40px;">
            <div style="font-size:48px;margin-bottom:12px;">📊</div>
            <h1 style="font-size:32px;margin-bottom:8px;">Your Attention Profile</h1>
            <p style="color:var(--color-text-muted);">${student.fullName} · ${student.studentId} · Grade ${student.grade} · ${today}</p>
          </div>

          <!-- Overall Score Banner -->
          <div class="glass-card card-padded animate-slide-up delay-100" style="margin-bottom:24px;background:var(--gradient-card);">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
              <div>
                <div style="font-size:13px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Overall Score</div>
                <div style="display:flex;align-items:baseline;gap:8px;">
                  <span style="font-size:56px;font-weight:800;background:var(--gradient-primary);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;" id="overall-score-display">0</span>
                  <span style="font-size:24px;color:var(--color-text-muted);">/100</span>
                </div>
              </div>
              <div style="text-align:center;">
                <div style="font-size:13px;color:var(--color-text-muted);margin-bottom:6px;">Status</div>
                <span class="badge ${overallStatus.badge}" style="font-size:16px;padding:8px 20px;">${overallStatus.label} Attention</span>
              </div>
              <div style="text-align:center;">
                <div style="font-size:13px;color:var(--color-text-muted);margin-bottom:6px;">Percentile</div>
                <div style="font-size:32px;font-weight:700;color:var(--color-accent-1);">${percentile}th</div>
              </div>
            </div>
          </div>

          <!-- Radar + Module Scores Grid -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px;">

            <!-- Radar Chart -->
            <div class="glass-card card-padded animate-slide-up delay-200">
              <h3 style="margin-bottom:16px;">Attention Radar</h3>
              <canvas id="radar-chart" width="300" height="300"></canvas>
            </div>

            <!-- Module Scores -->
            <div class="glass-card card-padded animate-slide-up delay-200" style="display:flex;flex-direction:column;gap:16px;">
              <h3>Module Scores</h3>
              ${moduleData.map(m => {
                const st = getScoreStatus(m.score);
                return `
                  <div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                      <div style="display:flex;align-items:center;gap:8px;">
                        <span>${m.icon}</span>
                        <span style="font-weight:600;font-size:14px;">${m.name}</span>
                        <span class="badge badge-primary" style="font-size:10px;">${m.weight}</span>
                      </div>
                      <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-weight:700;font-size:16px;">${m.score}/100</span>
                        <span class="badge ${st.badge}" style="font-size:10px;">${st.label}</span>
                      </div>
                    </div>
                    <div class="score-bar-bg">
                      <div class="score-bar-fill ${st.cls}" style="width:0%;" data-target="${m.score}%"></div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>

          <!-- Strengths & Weaknesses -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px;">
            <div class="glass-card card-padded animate-slide-up delay-300">
              <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>💪</span>Strengths</h3>
              ${moduleData.filter(m => m.score >= 65).length === 0
                ? '<p style="color:var(--color-text-muted);font-size:14px;">Keep practicing — improvement is expected with time.</p>'
                : moduleData.filter(m => m.score >= 65).map(m => `
                  <div style="display:flex;gap:10px;margin-bottom:12px;padding:10px;background:rgba(76,175,80,0.08);border-radius:var(--radius-md);border:1px solid rgba(76,175,80,0.2);">
                    <span>${m.icon}</span>
                    <div>
                      <div style="font-weight:600;font-size:13px;color:var(--color-accent-2);">${m.name} Attention (${m.score}/100)</div>
                      <div style="font-size:12px;color:var(--color-text-muted);">${m.desc}</div>
                    </div>
                  </div>
                `).join('')
              }
            </div>
            <div class="glass-card card-padded animate-slide-up delay-300">
              <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>⚠️</span>Areas to Improve</h3>
              ${moduleData.filter(m => m.score < 65).length === 0
                ? '<p style="color:var(--color-text-secondary);font-size:14px;">Great work! All areas are performing well.</p>'
                : moduleData.filter(m => m.score < 65).map(m => `
                  <div style="display:flex;gap:10px;margin-bottom:12px;padding:10px;background:rgba(251,140,0,0.08);border-radius:var(--radius-md);border:1px solid rgba(251,140,0,0.2);">
                    <span>${m.icon}</span>
                    <div>
                      <div style="font-weight:600;font-size:13px;color:var(--color-accent-3);">${m.name} Attention (${m.score}/100)</div>
                      <div style="font-size:12px;color:var(--color-text-muted);">${m.desc} – needs improvement</div>
                    </div>
                  </div>
                `).join('')
              }
            </div>
          </div>

          <!-- Study Strategies -->
          <div class="glass-card card-padded animate-slide-up delay-400" style="margin-bottom:24px;">
            <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>📚</span>Study Strategies</h3>
            <div style="display:flex;flex-direction:column;gap:10px;">
              ${recs.strategies.map((s, i) => `
                <div style="display:flex;gap:12px;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:var(--radius-md);">
                  <span style="color:var(--color-accent-1);font-weight:700;min-width:20px;">${i+1}.</span>
                  <span style="font-size:14px;color:var(--color-text-secondary);">${s}</span>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Career Recommendations -->
          <div class="glass-card card-padded animate-slide-up delay-400" style="margin-bottom:24px;">
            <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>💼</span>Career Recommendations</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
              <div>
                <div style="font-weight:600;color:var(--color-accent-2);margin-bottom:10px;font-size:14px;">✅ Good Fit</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                  ${recs.careers.good.map(c => `<span class="badge badge-success">${c}</span>`).join('')}
                </div>
              </div>
              ${recs.careers.poor.length ? `
              <div>
                <div style="font-weight:600;color:var(--color-accent-4);margin-bottom:10px;font-size:14px;">⚠️ Challenging Fit</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                  ${recs.careers.poor.map(c => `<span class="badge badge-error">${c}</span>`).join('')}
                </div>
              </div>` : ''}
            </div>
          </div>

          <!-- Advanced Analytics -->
          <div class="glass-card card-padded animate-slide-up delay-400" style="margin-bottom:24px;">
            <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>🔬</span>Advanced Scientific Analytics</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(250px, 1fr));gap:16px;">
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">RT Variability</div>
                <div style="font-size:24px;font-weight:700;color:var(--color-accent-1);">${moduleResults.sustained?.rtVariabilityScore || 0}%</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Consistency of response times.</div>
              </div>
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">Fatigue Slope</div>
                <div style="font-size:24px;font-weight:700;color:var(--color-accent-2);">${moduleResults.sustained?.fatigueScore || 0}%</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Resistance to fatigue over time.</div>
              </div>
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">Adaptation Speed</div>
                <div style="font-size:24px;font-weight:700;color:var(--color-accent-3);">${moduleResults.executive?.recoveryTrials?.toFixed(1) || '0.0'}</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Trials to adapt to rule changes (Executive).</div>
              </div>
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">Impulsivity Index</div>
                <div style="font-size:24px;font-weight:700;color:var(--color-accent-4);">${moduleResults.sustained?.impulsivityIndex || 0}%</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Tendency for false alarms.</div>
              </div>
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">Attention Stability</div>
                <div style="font-size:24px;font-weight:700;color:#2196F3;">${moduleResults.sustained?.attentionStability || 0}%</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Overall consistency and accuracy.</div>
              </div>
              <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;margin-bottom:8px;">Recovery After Errors</div>
                <div style="font-size:24px;font-weight:700;color:#9C27B0;">${moduleResults.sustained?.recoveryAfterErrors || 0}%</div>
                <div style="font-size:12px;color:var(--color-text-secondary);margin-top:4px;">Ability to return to correct responses.</div>
              </div>
            </div>
          </div>

          <!-- Performance Table -->
          <div class="glass-card card-padded animate-slide-up delay-500" style="margin-bottom:32px;overflow-x:auto;">
            <h3 style="margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span>📋</span>Performance Details</h3>
            <table class="data-table" style="min-width:600px;">
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
                  ${moduleData.map(m => `<td>${m.score}/100</td>`).join('')}
                </tr>
                <tr>
                  <td style="font-weight:600;color:var(--color-text-primary);">Avg RT</td>
                  <td>${moduleResults.sustained?.avgRT ?? '—'}ms</td>
                  <td>${moduleResults.selective?.correctClicks > 0 ? Math.round((moduleResults.selective.hitRate || 0)) + '%' : '—'}</td>
                  <td>${moduleResults.divided?.splitCost ?? '—'}ms split</td>
                  <td>${moduleResults.executive?.switchCost ?? '—'}ms</td>
                </tr>
                <tr>
                  <td style="font-weight:600;color:var(--color-text-primary);">Hit Rate</td>
                  <td>${moduleResults.sustained?.hitRate ?? '—'}%</td>
                  <td>${moduleResults.selective?.hitRate ?? '—'}%</td>
                  <td>${moduleResults.divided?.hitRate ?? '—'}%</td>
                  <td>${moduleResults.executive ? Math.round((moduleResults.executive.correctCount / (moduleResults.executive.correctCount + moduleResults.executive.errorCount || 1)) * 100) : '—'}%</td>
                </tr>
                <tr>
                  <td style="font-weight:600;color:var(--color-text-primary);">Errors</td>
                  <td>${moduleResults.sustained?.missed ?? '—'} missed</td>
                  <td>${moduleResults.selective?.wrongClicks ?? '—'} false alarms</td>
                  <td>${moduleResults.divided?.falsePresses ?? '—'} false</td>
                  <td>${moduleResults.executive?.errorCount ?? '—'} errors</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Action Buttons -->
          <div class="animate-slide-up delay-500" style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
            <button class="btn btn-primary btn-lg" id="download-pdf-btn">📥 Download Report</button>
            <button class="btn btn-secondary" id="start-over-btn">🔄 Start Over</button>
          </div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  // Animate overall score counter
  let displayScore = 0;
  const scoreEl = document.getElementById('overall-score-display');
  const scoreInterval = setInterval(() => {
    displayScore = Math.min(displayScore + 1, overall);
    if (scoreEl) scoreEl.textContent = displayScore.toFixed(1);
    if (displayScore >= overall) clearInterval(scoreInterval);
  }, 20);

  // Animate progress bars
  setTimeout(() => {
    document.querySelectorAll('.score-bar-fill').forEach(el => {
      el.style.transition = 'width 1.2s cubic-bezier(0.4,0,0.2,1)';
      el.style.width = el.dataset.target;
    });
  }, 400);

  // Radar Chart
  const ctx = document.getElementById('radar-chart');
  if (ctx) {
    const chart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Sustained', 'Selective', 'Divided', 'Executive'],
        datasets: [{
          label: 'Attention Score',
          data: [s1, s2, s3, s4],
          backgroundColor: 'rgba(0,188,212,0.15)',
          borderColor: '#00BCD4',
          borderWidth: 2,
          pointBackgroundColor: '#00BCD4',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#00BCD4',
          pointRadius: 5,
        }],
      },
      options: {
        responsive: true,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            grid:    { color: 'rgba(255,255,255,0.1)' },
            angleLines: { color: 'rgba(255,255,255,0.1)' },
            pointLabels: { color: 'rgba(255,255,255,0.8)', font: { size: 13, weight: '600' } },
            ticks: { color: 'rgba(255,255,255,0.4)', stepSize: 25, backdropColor: 'transparent' },
          },
        },
        plugins: {
          legend: { display: false },
        },
        animation: { duration: 1200, easing: 'easeInOutQuart' },
      },
    });
  }

  // PDF Download
  document.getElementById('download-pdf-btn').addEventListener('click', async () => {
    const btn = document.getElementById('download-pdf-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Generating PDF...';
    try {
      const { generatePDF } = await import('../PDFGenerator.js');
      generatePDF({
        student,
        scores: { sustained: s1, selective: s2, divided: s3, executive: s4, overall, percentile },
        moduleResults,
        recs,
        today,
      });
    } catch (e) {
      alert('PDF generation failed: ' + e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = '📥 Download Report';
    }
  });

  // Start Over
  document.getElementById('start-over-btn').addEventListener('click', () => {
    resetAssessment();
    navigate('/');
  });

  return () => clearInterval(scoreInterval);
}
