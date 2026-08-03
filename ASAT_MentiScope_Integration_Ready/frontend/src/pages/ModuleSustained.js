/* =====================================================
   ASAT – Module 1: Sustained Attention
   28 trials | Target: Blue Triangle (15% = ~4 targets)
   Response: SPACEBAR
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { renderShape, randomNonTarget } from '../ShapeRenderer.js';
import { scoreSustained } from '../scoring.js';
import { api } from '../api.js';

const TOTAL_TRIALS      = 28;
const MIN_TARGETS       = 10;
const MAX_TARGETS       = 12;
const STIMULUS_DURATION = 1000; // ms shape shown
const ISI_DURATION      = 700;  // blank inter-stimulus interval

/** Build the 28-trial sequence with 10-12 targets */
function buildSequence() {
  const targetCount = Math.floor(Math.random() * (MAX_TARGETS - MIN_TARGETS + 1)) + MIN_TARGETS;
  let seq = [];
  
  // Create initial pool
  for (let i = 0; i < targetCount; i++) seq.push(true);
  for (let i = 0; i < TOTAL_TRIALS - targetCount; i++) seq.push(false);
  
  // Shuffle array using Fisher-Yates
  for (let i = seq.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [seq[i], seq[j]] = [seq[j], seq[i]];
  }

  // Ensure constraints: max 3 consecutive targets, max 5 consecutive distractors
  let valid = false;
  while (!valid) {
    valid = true;
    let consecutiveTargets = 0;
    let consecutiveDistractors = 0;
    
    for (let i = 0; i < seq.length; i++) {
      if (seq[i]) {
        consecutiveTargets++;
        consecutiveDistractors = 0;
      } else {
        consecutiveDistractors++;
        consecutiveTargets = 0;
      }
      
      if (consecutiveTargets > 3 || consecutiveDistractors > 5) {
        valid = false;
        // Swap with a random element of opposite type
        const typeNeeded = seq[i] ? false : true;
        let swapIdx = Math.floor(Math.random() * seq.length);
        while (seq[swapIdx] !== typeNeeded) {
          swapIdx = Math.floor(Math.random() * seq.length);
        }
        [seq[i], seq[swapIdx]] = [seq[swapIdx], seq[i]];
        break; // Re-evaluate
      }
    }
  }

  return seq.map(isTarget => {
    if (isTarget) {
      return { shape: 'triangle', color: 'blue', isTarget: true };
    } else {
      const s = randomNonTarget();
      return { ...s, isTarget: false };
    }
  });
}

export function ModuleSustainedPage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  const sequence = buildSequence();
  let trialIndex  = 0;
  let hits        = 0;
  let missed      = 0;
  let falseAlarms = 0;
  const rtList    = [];  // RTs for hit responses
  const trialRTs  = [];  // All per-trial RTs (0 if no response)
  const eventsLog = [];  // SDK Trial events
  const correctnessArray = []; // Tracks correctness per trial

  let stimStart   = 0;
  let responded   = false;
  let phase       = 'instructions'; // instructions | running | isi | done
  let stimTimer   = null;
  let isiTimer    = null;

  // Timer state
  let elapsedSeconds = 0;
  let clockInterval  = null;

  container.innerHTML = `
    <div class="page-wrapper">
      <!-- Module Header -->
      <div class="module-header">
        <div class="module-title">
          <span>🔵</span>
          <span>Module 1 – Sustained Attention</span>
          <div class="badge badge-primary">25% of score</div>
        </div>
        <div class="module-timer" id="mod-timer">⏱️ 0:00</div>
      </div>

      <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:var(--space-6) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-2" style="opacity:0.06;"></div>
        <div class="container" style="max-width:680px;position:relative;z-index:1;">
          <div id="sustained-stage"></div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  const stage = document.getElementById('sustained-stage');

  function showInstructions() {
    phase = 'instructions';
    stage.innerHTML = `
      <div class="glass-card card-padded animate-slide-up text-center">
        <div style="font-size:48px;margin-bottom:16px;">🔵</div>
        <h2 style="margin-bottom:8px;">Sustained Attention</h2>
        <p style="font-size:15px;color:var(--color-text-secondary);margin-bottom:24px;">
          Shapes will appear one at a time. Press <kbd style="background:rgba(255,255,255,0.1);border:1px solid var(--color-border);padding:2px 8px;border-radius:4px;font-weight:700;">SPACEBAR</kbd>
          only when you see a <strong style="color:#1E88E5;">Blue Triangle</strong>.
        </p>

        <div style="display:flex;justify-content:center;gap:32px;margin-bottom:28px;padding:20px;background:rgba(30,136,229,0.08);border-radius:var(--radius-lg);border:1px solid rgba(30,136,229,0.2);">
          <div style="text-align:center;">
            <div id="inst-shape" style="width:90px;height:90px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;"></div>
            <div style="font-weight:700;color:var(--color-accent-2);">✅ PRESS SPACEBAR</div>
          </div>
        </div>

        <div class="alert alert-info" style="text-align:left;margin-bottom:24px;">
          <strong>Remember:</strong> Only the <strong style="color:#1E88E5;">Blue Triangle</strong> requires a response.
          All other shapes — ignore them. Focus and stay alert for all ${TOTAL_TRIALS} trials.
        </div>

        <button class="btn btn-primary btn-lg" id="start-sustained" style="min-width:220px;">Begin Module 1 →</button>
      </div>
    `;

    const instSlot = document.getElementById('inst-shape');
    const instShape = renderShape('triangle', 'blue', 90);
    instShape.classList.add('animate-float');
    instSlot.appendChild(instShape);

    document.getElementById('start-sustained').addEventListener('click', startModule);
  }

  async function startModule() {
    document.getElementById('start-sustained').disabled = true;
    document.getElementById('start-sustained').textContent = 'Starting...';
    if (!student.sessionId && student.dbId) {
      try {
        const res = await api.createSession({ studentId: student.dbId });
        const updatedStudent = { ...student, sessionId: res.sessionId };
        setState({ student: updatedStudent });
      } catch (e) { console.error('Failed to create session:', e); }
    }
    trialIndex = 0;
    startClock();
    runTrial();
  }

  function startClock() {
    elapsedSeconds = 0;
    updateTimer();
    clockInterval = setInterval(() => {
      elapsedSeconds++;
      updateTimer();
    }, 1000);
  }

  function updateTimer() {
    const m = Math.floor(elapsedSeconds / 60);
    const s = elapsedSeconds % 60;
    const el = document.getElementById('mod-timer');
    if (el) el.textContent = `⏱️ ${m}:${String(s).padStart(2, '0')}`;
  }

  function runTrial() {
    if (trialIndex >= TOTAL_TRIALS) { finishModule(); return; }
    phase     = 'running';
    responded = false;
    stimStart = performance.now();

    const trial = sequence[trialIndex];
    const pct   = Math.round((trialIndex / TOTAL_TRIALS) * 100);

    stage.innerHTML = `
      <div class="glass-card" style="overflow:hidden;">
        <!-- Progress -->
        <div style="padding:16px 24px 0;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:13px;color:var(--color-text-muted);">Trial ${trialIndex + 1} / ${TOTAL_TRIALS}</span>
            <span style="font-size:13px;color:var(--color-text-muted);">${pct}% complete</span>
          </div>
          <div class="progress-container">
            <div class="progress-fill progress-fill-active" style="width:${pct}%;"></div>
          </div>
        </div>

        <!-- Arena -->
        <div id="sustained-arena" class="shape-arena" style="min-height:280px;margin:20px 24px;border-radius:var(--radius-lg);">
          <div id="sustained-shape" style="display:flex;align-items:center;justify-content:center;width:100%;height:280px;"></div>
        </div>

        <!-- Instruction -->
        <div style="padding:0 24px 16px;text-align:center;">
          <p style="font-size:14px;color:var(--color-text-muted);">
            Press <strong style="color:var(--color-text-primary);">SPACEBAR</strong> for 
            <strong style="color:#1E88E5;">Blue Triangle</strong>
          </p>
        </div>

        <!-- Stats -->
        <div style="padding:12px 24px;border-top:1px solid var(--color-border);">
          <div class="stats-row">
            <div class="stat-item">✅ Hits: <strong id="stat-hits">${hits}</strong></div>
            <div class="stat-item">❌ Missed: <strong id="stat-missed">${missed}</strong></div>
            <div class="stat-item">⚡ False: <strong id="stat-false">${falseAlarms}</strong></div>
            <div class="stat-item">⚡ Last RT: <strong id="stat-rt">${rtList.length ? rtList[rtList.length-1] + 'ms' : '—'}</strong></div>
          </div>
        </div>

        <!-- Feedback overlay -->
        <div id="sustained-feedback" style="min-height:36px;text-align:center;padding:0 24px 16px;"></div>
      </div>
    `;

    // Render shape
    const slot = document.getElementById('sustained-shape');
    const shapeEl = renderShape(trial.shape, trial.color, 120);
    shapeEl.classList.add('shape-enter');
    slot.appendChild(shapeEl);

    // Hide shape after stimulus duration
    stimTimer = setTimeout(() => {
      if (!responded) {
        let isCorrect = !trial.isTarget;
        if (trial.isTarget) missed++;
        trialRTs.push(0);
        correctnessArray.push(isCorrect);
        eventsLog.push({
          taskId: 'Module 1 - Sustained',
          itemId: trialIndex + 1,
          stimulus: trial.shape + '_' + trial.color,
          eventType: 'TRIAL',
          response: 'NONE',
          correct: isCorrect,
          reactionTimeMs: 0,
          errorType: trial.isTarget ? 'MISSED_TARGET' : null,
          difficultyLevel: 1
        });
        advanceTrial();
      }
    }, STIMULUS_DURATION);
  }

  function handleSpacebar() {
    if (phase !== 'running') return;
    responded = true;
    clearTimeout(stimTimer);

    const rt    = Math.round(performance.now() - stimStart);
    const trial = sequence[trialIndex];

    let errorType = null;
    let isCorrect = false;

    if (trial.isTarget) {
      hits++;
      rtList.push(rt);
      trialRTs.push(rt);
      isCorrect = true;
      correctnessArray.push(true);
      showFeedback('✅ Correct!', 'var(--color-accent-2)', 'flash-correct');
    } else {
      falseAlarms++;
      trialRTs.push(rt);
      isCorrect = false;
      correctnessArray.push(false);
      errorType = 'FALSE_ALARM';
      showFeedback('❌ False Alarm', 'var(--color-accent-4)', 'flash-incorrect');
    }

    eventsLog.push({
      taskId: 'Module 1 - Sustained',
      itemId: trialIndex + 1,
      stimulus: trial.shape + '_' + trial.color,
      eventType: 'TRIAL',
      response: 'SPACE',
      correct: isCorrect,
      reactionTimeMs: rt,
      errorType,
      difficultyLevel: 1
    });

    advanceTrial(350);
  }

  function showFeedback(msg, color, flashClass) {
    const fb = document.getElementById('sustained-feedback');
    const arena = document.getElementById('sustained-arena');
    if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:${color};font-weight:600;">${msg}</span>`;
    if (arena) {
      arena.classList.add(flashClass);
      setTimeout(() => arena.classList.remove(flashClass), 400);
    }
    updateStats();
  }

  function updateStats() {
    const h = document.getElementById('stat-hits');
    const m = document.getElementById('stat-missed');
    const f = document.getElementById('stat-false');
    const r = document.getElementById('stat-rt');
    if (h) h.textContent = hits;
    if (m) m.textContent = missed;
    if (f) f.textContent = falseAlarms;
    if (r) r.textContent = rtList.length ? rtList[rtList.length - 1] + 'ms' : '—';
  }

  function advanceTrial(delay = ISI_DURATION) {
    phase = 'isi';
    isiTimer = setTimeout(() => {
      trialIndex++;
      runTrial();
    }, delay);
  }

  async function finishModule() {
    clearInterval(clockInterval);
    phase = 'done';

    const totalTargets = sequence.filter(t => t.isTarget).length;
    const totalDistractors = TOTAL_TRIALS - totalTargets;

    const result = scoreSustained({
      hits,
      totalTargets,
      rtList,
      trialRTs,
      correctnessArray,
      falseAlarms,
      totalDistractors
    });

    const currentStudent = getState().student;
    if (currentStudent && currentStudent.sessionId) {
      api.saveEvents(currentStudent.sessionId, { events: eventsLog, studentId: currentStudent.dbId }).catch(console.error);
    }

    const prevResults = getState().moduleResults;
    setState({ moduleResults: { ...prevResults, sustained: { hits, missed, falseAlarms, rtList, trialRTs, ...result } } });

    const status = result.score >= 80 ? 'Excellent' : result.score >= 65 ? 'Good' : result.score >= 50 ? 'Average' : 'Needs Work';
    const statusColor = result.score >= 65 ? 'var(--color-accent-2)' : result.score >= 50 ? 'var(--color-accent-3)' : 'var(--color-accent-4)';

    stage.innerHTML = `
      <div class="glass-card card-padded animate-pop text-center">
        <div style="font-size:52px;margin-bottom:16px;">🎯</div>
        <h2 style="margin-bottom:8px;">Module 1 Complete!</h2>
        <div style="font-size:48px;font-weight:700;color:${statusColor};margin:16px 0;">${result.score}<span style="font-size:24px;">/100</span></div>
        <div class="badge" style="font-size:14px;padding:6px 16px;background:rgba(0,188,212,0.15);color:var(--color-accent-1);border:1px solid rgba(0,188,212,0.3);margin-bottom:24px;">${status}</div>

        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px;">
          ${[
            ['Hit Rate', result.hitRate + '%'],
            ['Avg RT', result.avgRT + 'ms'],
            ['RT Variability', Math.round(result.rtStdDev) + 'ms'],
          ].map(([label, val]) => `
            <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius-md);padding:14px;">
              <div style="font-size:20px;font-weight:700;color:var(--color-text-primary);">${val}</div>
              <div style="font-size:12px;color:var(--color-text-muted);">${label}</div>
            </div>
          `).join('')}
        </div>

        <button class="btn btn-primary btn-lg" id="next-selective" style="min-width:240px;">
          Next: Module 2 – Selective Attention →
        </button>
      </div>
    `;
    document.getElementById('next-selective').addEventListener('click', () => navigate('/module/selective'));
  }

  // Keyboard
  function onKeydown(e) {
    if (e.code === 'Space') {
      e.preventDefault();
      handleSpacebar();
    }
  }
  window.addEventListener('keydown', onKeydown);

  showInstructions();

  return () => {
    window.removeEventListener('keydown', onKeydown);
    clearTimeout(stimTimer);
    clearTimeout(isiTimer);
    clearInterval(clockInterval);
  };
}
