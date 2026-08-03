/* =====================================================
   ASAT – Module 4: Executive Attention
   28 trials | Adaptive rule switching | Click target shape
   Rules: click CIRCLES | SQUARES | TRIANGLES | STARS | DIAMONDS
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { renderShape, SHAPES, randomColor } from '../ShapeRenderer.js';
import { scoreExecutive } from '../scoring.js';
import { api } from '../api.js';

const TOTAL_TRIALS = 28;
const SHAPES_LIST  = SHAPES; // ['circle','triangle','square','star','diamond']

// Build rule sequence: 4-5 switches total
function buildRuleSequence() {
  const switchPoints = [0, 7, 14, 21]; // switch at these trial indices
  const rules = [];
  let prevRule = null;

  switchPoints.forEach((start, si) => {
    let rule;
    do { rule = SHAPES_LIST[Math.floor(Math.random() * SHAPES_LIST.length)]; }
    while (rule === prevRule);
    prevRule = rule;

    const end = si < switchPoints.length - 1 ? switchPoints[si + 1] : TOTAL_TRIALS;
    for (let i = start; i < end; i++) rules.push({ rule, switched: i === start && si > 0, switchIndex: si });
  });
  return rules;
}

function buildTrialShapes() {
  return Array.from({ length: TOTAL_TRIALS }, () => ({
    shape: SHAPES_LIST[Math.floor(Math.random() * SHAPES_LIST.length)],
    color: randomColor(),
  }));
}

const SHAPE_LABELS = {
  circle:   'CIRCLES',
  triangle: 'TRIANGLES',
  square:   'SQUARES',
  star:     'STARS',
  diamond:  'DIAMONDS',
};

export function ModuleExecutivePage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  const ruleSeq   = buildRuleSequence();
  const stimuli   = buildTrialShapes();

  let trialIndex      = 0;
  let correctCount    = 0;
  let errorCount      = 0;
  let switchCount     = 0;
  let currentRule     = ruleSeq[0]?.rule || 'circle';

  // Switch cost and adaptation tracking
  const rtBeforeSwitch = [];
  const rtAfterSwitch  = [];
  const rtList         = [];
  let switchErrors     = 0;
  let totalAfterSwitch = 0;
  
  // Adaptation Speed: number of trials required to achieve the first correct response after a rule switch.
  // 1st correct trial = 1.
  let adaptationSum    = 0;
  let inRecovery       = false;
  let trialsSinceSwitch = 0;

  const eventsLog      = []; // SDK Trial events
  const correctnessArray = [];


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
          <span>🔄</span>
          <span>Module 4 – Executive Attention</span>
          <div class="badge badge-primary">30% of score</div>
        </div>
        <div class="module-timer" id="mod-timer">⏱️ 0:00</div>
      </div>
      <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:var(--space-6) 0;position:relative;overflow:hidden;">
        <div class="bg-orb bg-orb-1" style="opacity:0.05;"></div>
        <div class="container" style="max-width:680px;position:relative;z-index:1;">
          <div id="executive-stage"></div>
        </div>
      </main>
      <footer class="footer"><div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div></footer>
    </div>
  `;

  const stage = document.getElementById('executive-stage');

  function showInstructions() {
    stage.innerHTML = `
      <div class="glass-card card-padded animate-slide-up text-center">
        <div style="font-size:48px;margin-bottom:16px;">🔄</div>
        <h2 style="margin-bottom:8px;">Executive Attention</h2>
        <p style="font-size:15px;color:var(--color-text-secondary);margin-bottom:20px;">
          A shape appears. <strong>Click on it if it matches the current rule</strong>.
          The rule changes periodically — watch for the alert!
        </p>
        <div class="alert alert-info" style="text-align:left;margin-bottom:16px;">
          <strong>Rules you may see:</strong> Click CIRCLES · Click SQUARES · Click TRIANGLES · Click STARS · Click DIAMONDS
        </div>
        <div class="alert alert-warning" style="text-align:left;margin-bottom:24px;">
          <strong>⚠️ Watch out!</strong> When the rule changes, adapt immediately.
          The first rule is revealed at the start of the module.
        </div>
        <button class="btn btn-primary btn-lg" id="start-executive" style="min-width:220px;">Begin Module 4 →</button>
      </div>
    `;
    document.getElementById('start-executive').addEventListener('click', () => {
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

    const trialRule = ruleSeq[trialIndex];
    const switched  = trialRule.switched;
    const stimulus  = stimuli[trialIndex];
    const isTarget  = stimulus.shape === trialRule.rule;
    const pct       = Math.round((trialIndex / TOTAL_TRIALS) * 100);

    if (switched) {
      switchCount++;
      currentRule = trialRule.rule;
      totalAfterSwitch = TOTAL_TRIALS - trialIndex; // track remaining after switch
      inRecovery = true;
      trialsSinceSwitch = 1;
    } else if (inRecovery) {
      trialsSinceSwitch++;
    }

    stage.innerHTML = `
      <div class="glass-card" style="overflow:hidden;">
        <!-- Rule Banner -->
        <div id="rule-banner" style="padding:14px 24px;background:${switched ? 'rgba(251,140,0,0.15)' : 'rgba(26,35,126,0.2)'};border-bottom:1px solid ${switched ? 'rgba(251,140,0,0.4)' : 'rgba(26,35,126,0.4)'};text-align:center;transition:background 0.3s;">
          ${switched ? '<span style="font-size:12px;color:var(--color-accent-3);font-weight:700;letter-spacing:1px;display:block;margin-bottom:4px;">🔄 RULE CHANGE!</span>' : ''}
          <span style="font-size:16px;font-weight:700;color:var(--color-text-primary);">
            📋 CURRENT RULE: Click on <span style="color:var(--color-accent-1);">${SHAPE_LABELS[trialRule.rule]}</span>
          </span>
        </div>

        <!-- Progress -->
        <div style="padding:14px 24px 0;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:13px;color:var(--color-text-muted);">Trial ${trialIndex+1}/${TOTAL_TRIALS}</span>
          <div style="display:flex;gap:8px;align-items:center;">
            <span style="font-size:13px;color:var(--color-text-muted);">🔄 Switches: ${switchCount}/3</span>
            <span style="font-size:13px;color:var(--color-text-muted);">${pct}% done</span>
          </div>
        </div>
        <div style="padding:8px 24px 0;">
          <div class="progress-container"><div class="progress-fill" style="width:${pct}%;"></div></div>
        </div>

        <!-- Arena -->
        <div id="exec-arena" class="shape-arena" style="min-height:260px;margin:20px 24px;border-radius:var(--radius-lg);cursor:pointer;" id="exec-arena">
          <div id="exec-shape" style="display:flex;align-items:center;justify-content:center;width:100%;height:260px;"></div>
        </div>

        <div style="text-align:center;padding:0 24px 12px;">
          <p style="font-size:13px;color:var(--color-text-muted);">
            Click the shape if it matches the rule. Ignore it otherwise.
          </p>
        </div>

        <div style="padding:10px 24px;border-top:1px solid var(--color-border);">
          <div class="stats-row">
            <div class="stat-item">✅ Correct: <strong id="exec-correct">${correctCount}</strong></div>
            <div class="stat-item">❌ Errors: <strong id="exec-errors">${errorCount}</strong></div>
            <div class="stat-item">🔄 Switches: <strong>${switchCount}/3</strong></div>
          </div>
        </div>
        <div id="exec-feedback" style="min-height:36px;text-align:center;padding:0 24px 14px;"></div>
      </div>
    `;

    // Inject shape
    const slot    = document.getElementById('exec-shape');
    const shapeEl = renderShape(stimulus.shape, stimulus.color, 120);
    shapeEl.classList.add('shape-enter');
    shapeEl.style.cursor = 'pointer';
    slot.appendChild(shapeEl);

    // Animate rule banner if switched
    if (switched) {
      const banner = document.getElementById('rule-banner');
      if (banner) banner.classList.add('rule-switch-alert');
    }

    // Click on arena
    const arena = document.getElementById('exec-arena');
    if (arena) {
      arena.addEventListener('click', () => handleClick(isTarget, stimulus, arena));
    }

    stimTimer = setTimeout(() => {
      if (!responded) {
        let isCorrect = !isTarget;
        let errorType = null;
        if (isTarget) {
          errorCount++;
          errorType = 'MISSED_TARGET';
        }
        if (inRecovery) {
          if (!isCorrect) {
            switchErrors++;
          } else {
            adaptationSum += trialsSinceSwitch;
            inRecovery = false;
          }
        }
        correctnessArray.push(isCorrect);
        eventsLog.push({
          taskId: 'Module 4 - Executive',
          itemId: trialIndex + 1,
          stimulus: stimulus.shape + '_' + stimulus.color + '_' + trialRule.rule,
          eventType: 'TRIAL',
          response: 'NONE',
          correct: isCorrect,
          reactionTimeMs: 0,
          errorType: errorType,
          difficultyLevel: switchCount + 1
        });
        advanceTrial();
      }
    }, 1500);
  }

  function handleClick(isTarget, stimulus, arenaEl) {
    if (phase !== 'running') return;
    phase     = 'feedback';
    responded = true;
    clearTimeout(stimTimer);

    const rt  = Math.round(performance.now() - stimStart);
    const fb  = document.getElementById('exec-feedback');
    const trialRule = ruleSeq[trialIndex];

    let errorType = null;
    let isCorrect = false;

    if (isTarget) {
      correctCount++;
      isCorrect = true;
      rtList.push(rt);
      correctnessArray.push(true);
      // Switch cost tracking
      if (trialIndex < 7 || (trialIndex >= 7 && trialIndex < 14 && !ruleSeq[trialIndex].switched)) {
        rtBeforeSwitch.push(rt);
      }
      if (trialRule.switched || (switchCount > 0 && inRecovery)) {
        rtAfterSwitch.push(rt);
        if (inRecovery && isCorrect) {
          adaptationSum += trialsSinceSwitch;
          inRecovery = false; // Successfully adapted (either hit or correct rejection)
        }
      }
      if (arenaEl) arenaEl.style.outline = '3px solid #4CAF50';
      if (fb) fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-2);font-weight:700;">✅ Correct! (${rt}ms)</span>`;
    } else {
      errorCount++;
      isCorrect = false;
      correctnessArray.push(false);
      errorType = 'WRONG_RULE';
      if (inRecovery) { switchErrors++; }
      if (arenaEl) arenaEl.style.outline = '3px solid #E53935';
      if (fb) {
        const expected = SHAPE_LABELS[trialRule.rule];
        fb.innerHTML = `<span class="animate-slide-down" style="color:var(--color-accent-4);font-weight:700;">❌ Wrong! Rule is: Click ${expected}</span>`;
      }
    }

    eventsLog.push({
      taskId: 'Module 4 - Executive',
      itemId: trialIndex + 1,
      stimulus: stimulus.shape + '_' + stimulus.color + '_' + trialRule.rule,
      eventType: 'TRIAL',
      response: 'CLICK',
      correct: isCorrect,
      reactionTimeMs: rt,
      errorType: errorType,
      difficultyLevel: switchCount + 1
    });

    updateStats();
    setTimeout(() => { if (arenaEl) arenaEl.style.outline = ''; }, 400);
    advanceTrial(500);
  }

  function updateStats() {
    const c = document.getElementById('exec-correct');
    const e = document.getElementById('exec-errors');
    if (c) c.textContent = correctCount;
    if (e) e.textContent = errorCount;
  }

  function advanceTrial(delay = 600) {
    phase = 'isi';
    isiTimer = setTimeout(() => { trialIndex++; runTrial(); }, delay);
  }

  function finishModule() {
    clearInterval(clockInt);
    phase = 'done';

    const avgBefore = rtBeforeSwitch.length ? rtBeforeSwitch.reduce((a,b)=>a+b,0)/rtBeforeSwitch.length : 400;
    const avgAfter  = rtAfterSwitch.length  ? rtAfterSwitch.reduce((a,b)=>a+b,0)/rtAfterSwitch.length  : 500;
    
    // Average adaptation speed (trials) across all rule switches
    const avgRecoveryTrials = switchCount > 0 ? (adaptationSum / switchCount) : 0;
    const totalDistractors = TOTAL_TRIALS - ruleSeq.filter((r, i) => stimuli[i].shape === r.rule).length;

    const result = scoreExecutive({
      rtBeforeSwitch: avgBefore,
      rtAfterSwitch:  avgAfter,
      switchErrors,
      totalAfterSwitch,
      recoveryTrials: avgRecoveryTrials,
      rtList,
      correctnessArray,
      totalDistractors,
      falseAlarms: errorCount
    });

    const currentStudent = getState().student;
    if (currentStudent && currentStudent.sessionId) {
      api.saveEvents(currentStudent.sessionId, { events: eventsLog, studentId: currentStudent.dbId }).catch(console.error);
    }

    const prev = getState().moduleResults;
    setState({ moduleResults: { ...prev, executive: { correctCount, errorCount, switchCount, switchErrors, ...result } } });

    const statusColor = result.score >= 65 ? 'var(--color-accent-2)' : result.score >= 50 ? 'var(--color-accent-3)' : 'var(--color-accent-4)';

    stage.innerHTML = `
      <div class="glass-card card-padded animate-pop text-center">
        <div style="font-size:52px;margin-bottom:16px;">🔄</div>
        <h2 style="margin-bottom:8px;">Module 4 Complete!</h2>
        <div style="font-size:48px;font-weight:700;color:${statusColor};margin:16px 0;">${result.score}<span style="font-size:24px;">/100</span></div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px;">
          ${[
            ['Switch Cost', result.switchCost + 'ms'],
            ['Switch Errors', result.switchErrorRate + '%'],
            ['Recovery', result.recoveryTrials + ' trials'],
          ].map(([l,v]) => `
            <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius-md);padding:14px;">
              <div style="font-size:20px;font-weight:700;color:var(--color-text-primary);">${v}</div>
              <div style="font-size:12px;color:var(--color-text-muted);">${l}</div>
            </div>
          `).join('')}
        </div>
        <div class="alert alert-info" style="margin-bottom:24px;text-align:left;">
          🎉 You have completed all 4 modules! Calculating your results...
        </div>
        <button class="btn btn-primary btn-lg" id="go-results" style="min-width:240px;">
          📊 View My Results →
        </button>
      </div>
    `;
    document.getElementById('go-results').addEventListener('click', () => navigate('/results'));
  }

  showInstructions();

  return () => {
    clearTimeout(stimTimer);
    clearTimeout(isiTimer);
    clearInterval(clockInt);
  };
}
