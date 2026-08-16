/* =====================================================
   ASAT – Module 2: Selective Attention
   28 trials | Row of 5 shapes | Click on Blue Triangle
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { renderShape, buildSelectiveRow, COLORS } from '../ShapeRenderer.js';
import { scoreSelective } from '../scoring.js';
import { api } from '../api.js';

const TOTAL_TRIALS       = 28;
const TARGET_FREQUENCY   = 0.65; // ~65% of trials have a target
const ROW_COUNT_EASY     = 5;
const ROW_COUNT_MEDIUM   = 8;
const ROW_COUNT_HARD     = 12;
const DISPLAY_DURATION   = 2500; // ms per trial
const ISI_DURATION       = 600;

function buildTrialSequence() {
  const trials = [];
  let lowDensityRT = 0;  // tracked across low-density (5 items) trials
  let highDensityRT = 0; // tracked across high-density (12 items) trials

  for (let i = 0; i < TOTAL_TRIALS; i++) {
    const hasTarget = Math.random() < TARGET_FREQUENCY;
    let count;
    if (i < 10)       count = ROW_COUNT_EASY;
    else if (i < 20)  count = ROW_COUNT_MEDIUM;
    else               count = ROW_COUNT_HARD;

    const { shapes, targetIndex } = buildSelectiveRow(count, hasTarget);
    trials.push({ shapes, targetIndex, hasTarget, count, density: count <= 5 ? 'low' : 'high' });
  }
  return trials;
}

export function ModuleSelectivePage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  const sequence = buildTrialSequence();
  let trialIndex  = 0;
  let correctClicks    = 0;
  let wrongClicks      = 0;
  let totalTargets     = 0;
  let totalDistractors = 0;
  const rtLowDensity   = [];
  const rtHighDensity  = [];
  const rtTargetHits   = [];
  const eventsLog      = [];
  const correctnessArray = []; // SDK Trial events


  let stimStart  = 0;
  let responded  = false;
  let phase      = 'instructions';
  let stimTimer  = null;
  let isiTimer   = null;
  let elapsedSec = 0;
  let clockInt   = null;

  container.innerHTML = `
    <div class="page-wrapper">
      <div class="module-header">
        <div class="module-title">
          <span>🎯</span>
          <span>Module 2 – Selective Attention</span>
          <div class="badge badge-primary">25% of score</div>
        </div>
        <div class="module-timer" id="mod-timer">⏱️ 0:00</div>
      </div>
      <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:var(--space-6) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-1" style="opacity:0.05;"></div>
        <div class="container" style="max-width:800px;position:relative;z-index:1;">
          <div id="selective-stage"></div>
        </div>
      </main>
      <footer class="footer"><div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div></footer>
    </div>
  `;

  const stage = document.getElementById('selective-stage');

  function showInstructions() {
    stage.innerHTML = `
      <div class="glass-card card-padded animate-slide-up text-center">
        <div style="font-size:48px;margin-bottom:16px;">🎯</div>
        <h2 style="margin-bottom:8px;">Selective Attention</h2>
        <p style="font-size:15px;color:var(--color-text-secondary);margin-bottom:24px;">
          A row of shapes will appear. <strong>Click on the Blue Triangle</strong> if it is present.
          If there is no Blue Triangle, do nothing.
        </p>
        <div class="alert alert-info" style="text-align:left;margin-bottom:24px;">
          <strong>Difficulty increases:</strong> The number of distractors grows over time (5 → 8 → 12 shapes).
          Work quickly but accurately!
        </div>
        <button class="btn btn-primary btn-lg" id="start-selective" style="min-width:220px;">Begin Module 2 →</button>
      </div>
    `;
    document.getElementById('start-selective').addEventListener('click', () => {
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

    const trial = sequence[trialIndex];
    const pct   = Math.round((trialIndex / TOTAL_TRIALS) * 100);
    if (trial.hasTarget) totalTargets++;
    totalDistractors += trial.shapes.filter((_, i) => i !== trial.targetIndex).length;

    // Density label
    const densityLabel = trial.count <= 5 ? 'Easy' : trial.count <= 8 ? 'Medium' : 'Hard';
    const densityColor = trial.count <= 5 ? 'var(--color-accent-2)' : trial.count <= 8 ? 'var(--color-accent-3)' : 'var(--color-accent-4)';

    stage.innerHTML = `
      <div class="glass-card" style="overflow:hidden;">
        <div style="padding:16px 24px 0;display:flex;align-items:center;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:13px;color:var(--color-text-muted);">Trial ${trialIndex+1}/${TOTAL_TRIALS}</span>
            <span class="badge" style="background:rgba(0,0,0,0.2);border:1px solid ${densityColor};color:${densityColor};font-size:11px;">${densityLabel}</span>
          </div>
          <span style="font-size:13px;color:var(--color-text-muted);">${pct}% complete</span>
        </div>
        <div style="padding:8px 24px 0;">
          <div class="progress-container">
            <div class="progress-fill" style="width:${pct}%;"></div>
          </div>
        </div>

        <!-- Shape Row -->
        <div id="selective-arena" class="shape-arena" style="min-height:180px;margin:20px 24px;border-radius:var(--radius-lg);flex-direction:row;gap:12px;flex-wrap:wrap;padding:20px;cursor:default;">
          ${trial.shapes.map((s, idx) => `
            <div class="shape-slot shape-enter"
              data-idx="${idx}"
              data-is-target="${idx === trial.targetIndex}"
              style="cursor:pointer;width:${trial.count <= 5 ? 90 : trial.count <= 8 ? 72 : 60}px;height:${trial.count <= 5 ? 90 : trial.count <= 8 ? 72 : 60}px;display:flex;align-items:center;justify-content:center;border-radius:var(--radius-md);transition:background 0.15s;"
              title="${s.color} ${s.shape}">
            </div>
          `).join('')}
        </div>

        <div style="text-align:center;padding:0 24px 12px;">
          <p style="font-size:13px;color:var(--color-text-muted);">
            Click on the <strong style="color:#1E88E5;">Blue Triangle</strong>
            ${trial.hasTarget ? '— it IS present' : '— it may or may not be present'}
          </p>
        </div>

        <div style="padding:10px 24px;border-top:1px solid var(--color-border);">
          <div class="stats-row">
            <div class="stat-item">✅ Hits: <strong id="sel-hits">${correctClicks}</strong></div>
            <div class="stat-item">❌ False: <strong id="sel-false">${wrongClicks}</strong></div>
            <div class="stat-item">⚡ Last RT: <strong id="sel-rt">${rtTargetHits.length ? rtTargetHits[rtTargetHits.length-1]+'ms' : '—'}</strong></div>
          </div>
        </div>
        <div id="selective-feedback" style="min-height:36px;text-align:center;padding:0 24px 14px;"></div>
      </div>
    `;

    // Inject shapes into slots
    const slots = stage.querySelectorAll('.shape-slot');
    slots.forEach((slot, i) => {
      const s = trial.shapes[i];
      const sz = trial.count <= 5 ? 70 : trial.count <= 8 ? 56 : 48;
      const svg = renderShape(s.shape, s.color, sz);
      slot.appendChild(svg);

      slot.addEventListener('click', () => handleClick(i, trial, slot));
      slot.addEventListener('mouseenter', () => { slot.style.background = 'rgba(255,255,255,0.07)'; });
      slot.addEventListener('mouseleave', () => { slot.style.background = ''; });
    });

    // Auto-advance if no click
    stimTimer = setTimeout(() => {
      if (!responded) {
        let isCorrect = !trial.hasTarget;
        let errorType = null;
        // Miss — target was there but not clicked
        if (trial.hasTarget) {
          wrongClicks++; // counted as missed (commission error if they click wrong thing — here it's omission)
          errorType = 'MISSED_TARGET';
        }
        correctnessArray.push(isCorrect);
        const stimulusDesc = trial.shapes.map(s => s.shape + '_' + s.color).join(',').substring(0, 250);
        eventsLog.push({
          taskId: 'Module 2 - Selective',
          itemId: trialIndex + 1,
          stimulus: stimulusDesc,
          eventType: 'TRIAL',
          response: 'NONE',
          correct: isCorrect,
          reactionTimeMs: 0,
          errorType: errorType,
          difficultyLevel: trial.count <= 5 ? 1 : trial.count <= 8 ? 2 : 3
        });
        advanceTrial();
      }
    }, DISPLAY_DURATION);
  }

  function handleClick(idx, trial, slotEl) {
    if (phase !== 'running') return;
    phase     = 'feedback';
    responded = true;
    clearTimeout(stimTimer);

    const rt      = Math.round(performance.now() - stimStart);
    const isHit   = idx === trial.targetIndex && trial.hasTarget;
    const isFalse = !trial.hasTarget || idx !== trial.targetIndex;

    const arena = document.getElementById('selective-arena');
    const fb    = document.getElementById('selective-feedback');

    if (isHit) {
      correctClicks++;
      rtTargetHits.push(rt);
      if (trial.count <= 5)        rtLowDensity.push(rt);
      else if (trial.count >= 12)  rtHighDensity.push(rt);
      slotEl.style.background = 'rgba(76,175,80,0.2)';
      slotEl.style.border     = '2px solid #4CAF50';
      correctnessArray.push(true);
      if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-2);font-weight:700;">✅ Correct! (${rt}ms)</span>`;
      if (arena) arena.classList.add('flash-correct');
    } else {
      wrongClicks++;
      slotEl.style.background = 'rgba(229,57,53,0.2)';
      slotEl.style.border     = '2px solid #E53935';
      correctnessArray.push(false);
      if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-4);font-weight:700;">❌ False Alarm!</span>`;
      if (arena) arena.classList.add('flash-incorrect');
    }

    const stimulusDesc = trial.shapes.map(s => s.shape + '_' + s.color).join(',').substring(0, 250);
    eventsLog.push({
      taskId: 'Module 2 - Selective',
      itemId: trialIndex + 1,
      stimulus: stimulusDesc,
      eventType: 'TRIAL',
      response: 'CLICK',
      correct: isHit,
      reactionTimeMs: rt,
      errorType: isHit ? null : 'FALSE_ALARM',
      difficultyLevel: trial.count <= 5 ? 1 : trial.count <= 8 ? 2 : 3
    });

    updateStats();

    setTimeout(() => { if (arena) arena.classList.remove('flash-correct','flash-incorrect'); }, 400);
    advanceTrial(500);
  }

  function updateStats() {
    const h = document.getElementById('sel-hits');
    const f = document.getElementById('sel-false');
    const r = document.getElementById('sel-rt');
    if (h) h.textContent = correctClicks;
    if (f) f.textContent = wrongClicks;
    if (r) r.textContent = rtTargetHits.length ? rtTargetHits[rtTargetHits.length-1]+'ms' : '—';
  }

  function advanceTrial(delay = ISI_DURATION) {
    phase = 'isi';
    isiTimer = setTimeout(() => { trialIndex++; runTrial(); }, delay);
  }

  function finishModule() {
    clearInterval(clockInt);
    phase = 'done';

    const rtLowAvg  = rtLowDensity.length  ? rtLowDensity.reduce((a,b)=>a+b,0)/rtLowDensity.length   : 0;
    const rtHighAvg = rtHighDensity.length ? rtHighDensity.reduce((a,b)=>a+b,0)/rtHighDensity.length : 0;

    const result = scoreSelective({
      correctClicks,
      totalTargets,
      wrongClicks,
      totalDistractors,
      rtHigh: rtHighAvg,
      rtLow:  rtLowAvg,
      rtList: rtTargetHits,
      correctnessArray
    });

    const currentStudent = getState().student;
    if (currentStudent && currentStudent.sessionId) {
      api.saveEvents(currentStudent.sessionId, { events: eventsLog, studentId: currentStudent.dbId }).catch(console.error);
    }

    const prev = getState().moduleResults;
    setState({ moduleResults: { ...prev, selective: { correctClicks, wrongClicks, totalTargets, totalDistractors, ...result } } });

    const statusColor = result.score >= 65 ? 'var(--color-accent-2)' : result.score >= 50 ? 'var(--color-accent-3)' : 'var(--color-accent-4)';

    stage.innerHTML = `
      <div class="glass-card card-padded animate-pop text-center">
        <div style="font-size:52px;margin-bottom:16px;">🎯</div>
        <h2 style="margin-bottom:8px;">Module 2 Complete!</h2>
        <div style="font-size:48px;font-weight:700;color:${statusColor};margin:16px 0;">${result.score}<span style="font-size:24px;">/100</span></div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px;">
          ${[
            ['Hit Rate', result.hitRate + '%'],
            ['False Alarms', result.falseAlarmRate + '%'],
            ['Distractor Cost', result.distractorCost + 'ms'],
          ].map(([l,v]) => `
            <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius-md);padding:14px;">
              <div style="font-size:20px;font-weight:700;color:var(--color-text-primary);">${v}</div>
              <div style="font-size:12px;color:var(--color-text-muted);">${l}</div>
            </div>
          `).join('')}
        </div>
        <button class="btn btn-primary btn-lg" id="next-divided" style="min-width:240px;">Next: Module 3 – Divided Attention →</button>
      </div>
    `;
    document.getElementById('next-divided').addEventListener('click', () => navigate('/module/divided'));
  }

  showInstructions();

  return () => {
    clearTimeout(stimTimer);
    clearTimeout(isiTimer);
    clearInterval(clockInt);
  };
}
