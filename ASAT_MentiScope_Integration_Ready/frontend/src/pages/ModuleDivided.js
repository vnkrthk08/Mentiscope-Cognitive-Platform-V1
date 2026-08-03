/* =====================================================
   ASAT – Module 3: Divided Attention
   28 trials | Dual-stream: Left Panel (shape) + Right Panel (word)
   Target: Left=Blue Triangle AND Right="BLUE"
   Response: SPACEBAR
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { renderShape, randomNonTarget, COLORS } from '../ShapeRenderer.js';
import { scoreDivided } from '../scoring.js';
import { api } from '../api.js';

const TOTAL_TRIALS = 28;
const TARGET_COUNT = 6;  // ~21% of trials are targets (both match)
const COLOR_WORDS  = ['RED', 'BLUE', 'GREEN', 'YELLOW', 'PURPLE', 'ORANGE'];

// Timing changes with difficulty
const TIMINGS = [
  { display: 1500, label: 'Easy'   },  // trials 0–9
  { display: 1200, label: 'Medium' },  // trials 10–19
  { display:  800, label: 'Hard'   },  // trials 20–27
];

function buildSequence() {
  const seq      = [];
  const targetAt = new Set();
  while (targetAt.size < TARGET_COUNT) targetAt.add(Math.floor(Math.random() * TOTAL_TRIALS));

  for (let i = 0; i < TOTAL_TRIALS; i++) {
    const isTarget = targetAt.has(i);
    if (isTarget) {
      seq.push({
        left:  { shape: 'triangle', color: 'blue' },
        right: 'BLUE',
        isTarget: true,
      });
    } else {
      // Ensure NOT both blue-triangle + BLUE
      let left, right;
      do {
        left  = randomNonTarget();
        right = COLOR_WORDS[Math.floor(Math.random() * COLOR_WORDS.length)];
      } while (left.shape === 'triangle' && left.color === 'blue' && right === 'BLUE');
      seq.push({ left, right, isTarget: false });
    }
  }
  return seq;
}

const WORD_COLORS = {
  RED:    '#E53935',
  BLUE:   '#1E88E5',
  GREEN:  '#43A047',
  YELLOW: '#FFB300',
  PURPLE: '#8E24AA',
  ORANGE: '#FB8C00',
};

export function ModuleDividedPage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  const sequence = buildSequence();
  let trialIndex      = 0;
  let correctPresses  = 0;
  let falsePresses    = 0;
  let totalTargets    = TARGET_COUNT;
  let totalNonTargets = TOTAL_TRIALS - TARGET_COUNT;

  // For split cost: track RT in single-focus (easy) vs dual-task (hard)
  const rtDualList   = [];  // all correct press RTs (dual condition)
  const rtSingleBase = [];  // easy phase RTs
  const eventsLog    = [];  // SDK Trial events
  const correctnessArray = [];


  let stimStart = 0;
  let responded = false;
  let phase     = 'instructions';
  let stimTimer = null;
  let isiTimer  = null;
  let elapsedSec = 0;
  let clockInt   = null;

  container.innerHTML = `
    <div class="page-wrapper">
      <div class="module-header">
        <div class="module-title">
          <span>⚡</span>
          <span>Module 3 – Divided Attention</span>
          <div class="badge badge-primary">20% of score</div>
        </div>
        <div class="module-timer" id="mod-timer">⏱️ 0:00</div>
      </div>
      <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:var(--space-6) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-2" style="opacity:0.05;"></div>
        <div class="container" style="max-width:800px;position:relative;z-index:1;">
          <div id="divided-stage"></div>
        </div>
      </main>
      <footer class="footer"><div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div></footer>
    </div>
  `;

  const stage = document.getElementById('divided-stage');

  function showInstructions() {
    stage.innerHTML = `
      <div class="glass-card card-padded animate-slide-up text-center">
        <div style="font-size:48px;margin-bottom:16px;">⚡</div>
        <h2 style="margin-bottom:8px;">Divided Attention</h2>
        <p style="font-size:15px;color:var(--color-text-secondary);margin-bottom:20px;">
          You will see <strong>TWO panels</strong> simultaneously. Monitor BOTH at the same time.
        </p>

        <!-- Dual panel demo -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:20px;text-align:center;">
            <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">LEFT PANEL</div>
            <div style="font-size:13px;color:var(--color-text-secondary);">A shape in a color</div>
            <div style="font-size:13px;color:var(--color-accent-1);font-weight:600;margin-top:8px;">(e.g. Blue Triangle)</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:20px;text-align:center;">
            <div style="font-size:12px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">RIGHT PANEL</div>
            <div style="font-size:13px;color:var(--color-text-secondary);">A color word</div>
            <div style="font-size:13px;color:var(--color-accent-1);font-weight:600;margin-top:8px;">(e.g. "BLUE")</div>
          </div>
        </div>

        <div class="alert alert-info" style="text-align:left;margin-bottom:16px;">
          <strong style="display:block;margin-bottom:6px;">✅ Press SPACEBAR when BOTH match:</strong>
          Left shows a <strong style="color:#1E88E5;">Blue Triangle</strong> AND Right shows <strong style="color:#1E88E5;">"BLUE"</strong>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:12px;margin-bottom:20px;">
          ${[
            ['🔵 Blue Triangle', '"BLUE"', '✅ PRESS'],
            ['🔵 Blue Triangle', '"GREEN"', '❌ DON\'T'],
            ['🟢 Green Circle',  '"BLUE"', '❌ DON\'T'],
          ].map(([l, r, act]) => `
            <div style="background:rgba(255,255,255,0.03);border-radius:var(--radius-md);padding:10px;border:1px solid var(--color-border);">
              <div style="color:var(--color-text-secondary);">L: ${l}</div>
              <div style="color:var(--color-text-secondary);">R: ${r}</div>
              <div style="font-weight:700;color:${act.includes('✅') ? 'var(--color-accent-2)' : 'var(--color-accent-4)'};margin-top:4px;">${act}</div>
            </div>
          `).join('')}
        </div>

        <button class="btn btn-primary btn-lg" id="start-divided" style="min-width:220px;">Begin Module 3 →</button>
      </div>
    `;
    document.getElementById('start-divided').addEventListener('click', () => {
      startClock();
      runTrial();
    });
  }

  function startClock() {
    elapsedSec = 0;
    clockInt = setInterval(() => {
      elapsedSec++;
      const m = Math.floor(elapsedSec / 60);
      const s = elapsedSec % 60;
      const el = document.getElementById('mod-timer');
      if (el) el.textContent = `⏱️ ${m}:${String(s).padStart(2,'0')}`;
    }, 1000);
  }

  function runTrial() {
    if (trialIndex >= TOTAL_TRIALS) { finishModule(); return; }
    phase     = 'running';
    responded = false;
    stimStart = performance.now();

    const trial   = sequence[trialIndex];
    const timingI = trialIndex < 10 ? 0 : trialIndex < 20 ? 1 : 2;
    const timing  = TIMINGS[timingI];
    const pct     = Math.round((trialIndex / TOTAL_TRIALS) * 100);

    stage.innerHTML = `
      <div class="glass-card" style="overflow:hidden;">
        <div style="padding:14px 24px 0;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:13px;color:var(--color-text-muted);">Trial ${trialIndex+1}/${TOTAL_TRIALS}</span>
          <div style="display:flex;gap:8px;align-items:center;">
            <span class="badge" style="background:rgba(0,0,0,0.2);border:1px solid ${timingI===0?'var(--color-accent-2)':timingI===1?'var(--color-accent-3)':'var(--color-accent-4)'};color:${timingI===0?'var(--color-accent-2)':timingI===1?'var(--color-accent-3)':'var(--color-accent-4)'};font-size:11px;">${timing.label}</span>
            <span style="font-size:13px;color:var(--color-text-muted);">${pct}% complete</span>
          </div>
        </div>
        <div style="padding:8px 24px 0;">
          <div class="progress-container"><div class="progress-fill" style="width:${pct}%;"></div></div>
        </div>

        <!-- Dual Panel -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 24px;" id="dual-panels">
          <!-- Left -->
          <div style="background:rgba(26,35,126,0.2);border:1px solid rgba(26,35,126,0.4);border-radius:var(--radius-lg);padding:24px;text-align:center;">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;">LEFT PANEL</div>
            <div id="left-shape-slot" style="display:flex;align-items:center;justify-content:center;height:120px;"></div>
            <div style="font-size:12px;color:var(--color-text-muted);margin-top:8px;">Shape</div>
          </div>
          <!-- Right -->
          <div style="background:rgba(0,188,212,0.08);border:1px solid rgba(0,188,212,0.2);border-radius:var(--radius-lg);padding:24px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <div style="font-size:11px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;">RIGHT PANEL</div>
            <div id="right-word" style="font-size:40px;font-weight:800;letter-spacing:2px;"></div>
            <div style="font-size:12px;color:var(--color-text-muted);margin-top:8px;">Color Word</div>
          </div>
        </div>

        <div style="text-align:center;padding:0 24px 12px;">
          <p style="font-size:14px;color:var(--color-text-muted);">
            Press <strong style="color:var(--color-text-primary);">SPACEBAR</strong> when
            <strong style="color:#1E88E5;">Blue Triangle</strong> + <strong style="color:#1E88E5;">"BLUE"</strong>
          </p>
        </div>

        <div style="padding:10px 24px;border-top:1px solid var(--color-border);">
          <div class="stats-row">
            <div class="stat-item">✅ Correct: <strong id="div-correct">${correctPresses}</strong></div>
            <div class="stat-item">❌ False: <strong id="div-false">${falsePresses}</strong></div>
            <div class="stat-item">⚡ Last RT: <strong id="div-rt">${rtDualList.length ? rtDualList[rtDualList.length-1]+'ms' : '—'}</strong></div>
          </div>
        </div>
        <div id="divided-feedback" style="min-height:36px;text-align:center;padding:0 24px 14px;"></div>
      </div>
    `;

    // Inject left shape
    const leftSlot = document.getElementById('left-shape-slot');
    const shapeEl  = renderShape(trial.left.shape, trial.left.color, 100);
    shapeEl.classList.add('shape-enter');
    leftSlot.appendChild(shapeEl);

    // Inject right word
    const wordEl = document.getElementById('right-word');
    wordEl.textContent = trial.right;
    wordEl.style.color = WORD_COLORS[trial.right] || '#fff';
    wordEl.classList.add('animate-scale-in');

    stimTimer = setTimeout(() => {
      if (!responded) {
        let isCorrect = !trial.isTarget;
        let errorType = null;
        if (trial.isTarget) {
          // Missed target
          errorType = 'MISSED_TARGET';
        }
        correctnessArray.push(isCorrect);
        eventsLog.push({
          taskId: 'Module 3 - Divided',
          itemId: trialIndex + 1,
          stimulus: trial.left.shape + '_' + trial.left.color + '|' + trial.right,
          eventType: 'TRIAL',
          response: 'NONE',
          correct: isCorrect,
          reactionTimeMs: 0,
          errorType: errorType,
          difficultyLevel: timingI + 1
        });
        advanceTrial();
      }
    }, timing.display);
  }

  function handleSpacebar() {
    if (phase !== 'running') return;
    phase     = 'feedback';
    responded = true;
    clearTimeout(stimTimer);

    const rt    = Math.round(performance.now() - stimStart);
    const trial = sequence[trialIndex];
    const fb    = document.getElementById('divided-feedback');
    const panels = document.getElementById('dual-panels');
    
    let isCorrect = false;
    let errorType = null;

    if (trial.isTarget) {
      correctPresses++;
      rtDualList.push(rt);
      if (trialIndex < 10) rtSingleBase.push(rt);
      isCorrect = true;
      correctnessArray.push(true);
      if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-2);font-weight:700;">✅ Correct! Both match! (${rt}ms)</span>`;
      if (panels) { panels.style.outline = '2px solid #4CAF50'; setTimeout(() => { if(panels) panels.style.outline=''; }, 400); }
    } else {
      falsePresses++;
      isCorrect = false;
      correctnessArray.push(false);
      errorType = 'FALSE_ALARM';
      if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-4);font-weight:700;">❌ False Alarm! Both didn't match.</span>`;
      if (panels) { panels.style.outline = '2px solid #E53935'; setTimeout(() => { if(panels) panels.style.outline=''; }, 400); }
    }

    const timingI = trialIndex < 10 ? 0 : trialIndex < 20 ? 1 : 2;
    eventsLog.push({
      taskId: 'Module 3 - Divided',
      itemId: trialIndex + 1,
      stimulus: trial.left.shape + '_' + trial.left.color + '|' + trial.right,
      eventType: 'TRIAL',
      response: 'SPACE',
      correct: isCorrect,
      reactionTimeMs: rt,
      errorType: errorType,
      difficultyLevel: timingI + 1
    });

    updateStats();
    advanceTrial(500);
  }

  function updateStats() {
    const c = document.getElementById('div-correct');
    const f = document.getElementById('div-false');
    const r = document.getElementById('div-rt');
    if (c) c.textContent = correctPresses;
    if (f) f.textContent = falsePresses;
    if (r) r.textContent = rtDualList.length ? rtDualList[rtDualList.length-1]+'ms' : '—';
  }

  function advanceTrial(delay = 600) {
    phase = 'isi';
    isiTimer = setTimeout(() => { trialIndex++; runTrial(); }, delay);
  }

  function finishModule() {
    clearInterval(clockInt);
    phase = 'done';

    const rtDualAvg   = rtDualList.length ? rtDualList.reduce((a,b)=>a+b,0)/rtDualList.length : 0;
    const rtSingleAvg = rtSingleBase.length ? rtSingleBase.reduce((a,b)=>a+b,0)/rtSingleBase.length : rtDualAvg * 0.85;

    const result = scoreDivided({
      correctPresses,
      totalTargets,
      falsePresses,
      totalNonTargets,
      rtDual:   rtDualAvg,
      rtSingle: rtSingleAvg,
      rtList:   rtDualList,
      correctnessArray,
    });

    const currentStudent = getState().student;
    if (currentStudent && currentStudent.sessionId) {
      api.saveEvents(currentStudent.sessionId, { events: eventsLog, studentId: currentStudent.dbId }).catch(console.error);
    }

    const prev = getState().moduleResults;
    setState({ moduleResults: { ...prev, divided: { correctPresses, falsePresses, totalTargets, totalNonTargets, ...result } } });

    const statusColor = result.score >= 65 ? 'var(--color-accent-2)' : result.score >= 50 ? 'var(--color-accent-3)' : 'var(--color-accent-4)';

    stage.innerHTML = `
      <div class="glass-card card-padded animate-pop text-center">
        <div style="font-size:52px;margin-bottom:16px;">⚡</div>
        <h2 style="margin-bottom:8px;">Module 3 Complete!</h2>
        <div style="font-size:48px;font-weight:700;color:${statusColor};margin:16px 0;">${result.score}<span style="font-size:24px;">/100</span></div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px;">
          ${[
            ['Hit Rate', result.hitRate + '%'],
            ['False Alarm', result.falseAlarmRate + '%'],
            ['Split Cost', result.splitCost + 'ms'],
          ].map(([l,v]) => `
            <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius-md);padding:14px;">
              <div style="font-size:20px;font-weight:700;color:var(--color-text-primary);">${v}</div>
              <div style="font-size:12px;color:var(--color-text-muted);">${l}</div>
            </div>
          `).join('')}
        </div>
        <button class="btn btn-primary btn-lg" id="next-executive" style="min-width:240px;">Next: Module 4 – Executive Attention →</button>
      </div>
    `;
    document.getElementById('next-executive').addEventListener('click', () => navigate('/module/executive'));
  }

  function onKeydown(e) {
    if (e.code === 'Space') { e.preventDefault(); handleSpacebar(); }
  }
  window.addEventListener('keydown', onKeydown);

  showInstructions();

  return () => {
    window.removeEventListener('keydown', onKeydown);
    clearTimeout(stimTimer);
    clearTimeout(isiTimer);
    clearInterval(clockInt);
  };
}
