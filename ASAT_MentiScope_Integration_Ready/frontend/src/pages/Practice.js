/* =====================================================
   ASAT – Practice Round Page
   5 trials: Press SPACEBAR for BLUE TRIANGLE
   ≥80% → proceed, else retry or quit
   ===================================================== */

import { navigate } from '../router.js';
import { getState, setState } from '../store.js';
import { renderShape, randomNonTarget } from '../ShapeRenderer.js';

const PRACTICE_TRIALS = 5;
const STIMULUS_DURATION = 1200;  // ms shape shown
const ISI_DURATION      = 800;   // inter-stimulus interval

const PRACTICE_SEQUENCE = [
  { shape: 'triangle', color: 'blue',   isTarget: true  },
  { shape: 'circle',   color: 'red',    isTarget: false },
  { shape: 'triangle', color: 'blue',   isTarget: true  },
  { shape: 'square',   color: 'green',  isTarget: false },
  { shape: 'triangle', color: 'blue',   isTarget: true  },
];

export function PracticePage(container) {
  const { student } = getState();
  if (!student) { navigate('/register'); return; }

  let trialIndex   = 0;
  let correct      = 0;
  let responded    = false;
  let stimulusTimer = null;
  let isiTimer      = null;
  let phase = 'instructions'; // 'instructions' | 'running' | 'feedback' | 'done'

  container.innerHTML = `
    <div class="page-wrapper">
      <nav class="navbar">
        <div class="container navbar-inner">
          <a class="navbar-brand" href="#/">
            <div class="navbar-logo">🧠</div>
            <div><div class="navbar-title">ASAT</div><div class="navbar-subtitle">Practice</div></div>
          </a>
          <div class="badge badge-warning">Practice Round</div>
        </div>
      </nav>

      <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:var(--space-8) 0;">
        <div class="container" style="max-width:640px;">
          <div id="practice-stage"></div>
        </div>
      </main>

      <footer class="footer">
        <div class="container"><p>© 2026 ASAT | IIT Madras MentiScope Project</p></div>
      </footer>
    </div>
  `;

  const stage = document.getElementById('practice-stage');

  function showInstructions() {
    phase = 'instructions';
    stage.innerHTML = `
      <div class="glass-card card-padded animate-slide-up text-center">
        <div style="font-size:52px;margin-bottom:16px;">🏋️</div>
        <h2 style="margin-bottom:12px;">Practice Round</h2>
        <p style="margin-bottom:24px;font-size:15px;">
          You will see <strong>5 shapes</strong> appear one at a time.<br/>
          Press <kbd style="background:rgba(255,255,255,0.1);border:1px solid var(--color-border);padding:2px 8px;border-radius:4px;font-weight:700;">SPACEBAR</kbd>
          only when you see a <strong style="color:#1E88E5;">BLUE TRIANGLE</strong>.
        </p>

        <div style="display:flex;align-items:center;justify-content:center;gap:24px;margin-bottom:28px;padding:20px;background:rgba(0,188,212,0.06);border-radius:var(--radius-lg);border:1px solid rgba(0,188,212,0.2);">
          <div style="text-align:center;">
            <div id="demo-target" style="margin:0 auto 8px;width:80px;height:80px;display:flex;align-items:center;justify-content:center;"></div>
            <div style="font-size:13px;color:var(--color-accent-2);font-weight:600;">✅ PRESS SPACEBAR</div>
            <div style="font-size:12px;color:var(--color-text-muted);">Blue Triangle</div>
          </div>
          <div style="font-size:28px;color:var(--color-text-muted);">vs</div>
          <div style="text-align:center;">
            <div id="demo-distractor" style="margin:0 auto 8px;width:80px;height:80px;display:flex;align-items:center;justify-content:center;"></div>
            <div style="font-size:13px;color:var(--color-accent-4);font-weight:600;">❌ DO NOT PRESS</div>
            <div style="font-size:12px;color:var(--color-text-muted);">Anything else</div>
          </div>
        </div>

        <button class="btn btn-primary btn-lg" id="begin-practice-btn" style="min-width:200px;">
          Begin Practice →
        </button>
      </div>
    `;

    // Render demo shapes
    const demoTarget = renderShape('triangle', 'blue', 80);
    demoTarget.classList.add('animate-float');
    document.getElementById('demo-target').appendChild(demoTarget);

    const distractor = randomNonTarget();
    const demoNonTarget = renderShape(distractor.shape, distractor.color, 80);
    document.getElementById('demo-distractor').appendChild(demoNonTarget);

    document.getElementById('begin-practice-btn').addEventListener('click', startTrials);
  }

  function startTrials() {
    trialIndex = 0;
    correct    = 0;
    runTrial();
  }

  function runTrial() {
    if (trialIndex >= PRACTICE_TRIALS) {
      showResults();
      return;
    }

    phase     = 'running';
    responded = false;
    const trial = PRACTICE_SEQUENCE[trialIndex];

    stage.innerHTML = `
      <div class="glass-card card-padded animate-fade-in">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <span style="font-size:13px;color:var(--color-text-muted);">Trial ${trialIndex + 1} / ${PRACTICE_TRIALS}</span>
          <div style="display:flex;gap:6px;">
            ${Array.from({length: PRACTICE_TRIALS}, (_, i) => `
              <div style="width:10px;height:10px;border-radius:50%;background:${
                i < trialIndex ? 'var(--color-accent-2)' : i === trialIndex ? 'var(--color-accent-1)' : 'rgba(255,255,255,0.1)'
              };transition:background 0.3s;"></div>
            `).join('')}
          </div>
        </div>

        <div id="practice-arena" class="shape-arena" style="min-height:240px;margin-bottom:20px;">
          <div id="practice-shape-slot" style="display:flex;align-items:center;justify-content:center;width:100%;height:240px;"></div>
        </div>

        <div id="practice-feedback" style="min-height:48px;text-align:center;"></div>

        <div class="text-center" style="margin-top:16px;">
          <p style="font-size:13px;color:var(--color-text-muted);">
            Press <kbd style="background:rgba(255,255,255,0.1);border:1px solid var(--color-border);padding:1px 6px;border-radius:3px;font-weight:700;">SPACEBAR</kbd>
            when you see a <strong style="color:#1E88E5;">Blue Triangle</strong>
          </p>
        </div>
      </div>
    `;

    // Show shape
    const slot = document.getElementById('practice-shape-slot');
    const shapeEl = renderShape(trial.shape, trial.color, 110);
    shapeEl.classList.add('shape-enter');
    slot.appendChild(shapeEl);
    
    // Add click handler for mouse users
    const arena = document.getElementById('practice-arena');
    if (arena) {
      arena.onclick = () => {
        if (phase === 'running') {
          handleUserResponse(trial);
        }
      };
    }

    // Remove shape after duration
    stimulusTimer = setTimeout(() => {
      if (!responded) handleTimeout(trial);
    }, STIMULUS_DURATION);
  }

  function handleUserResponse(trial) {
    if (phase !== 'running') return;
    phase = 'feedback';
    responded = true;
    clearTimeout(stimulusTimer);

    const feedback = document.getElementById('practice-feedback');
    const arena = document.getElementById('practice-arena');

    // User pressed a button.
    if (trial.isTarget) {
      // Hit (Correct)
      correct++;
      feedback.innerHTML = `<div class="animate-slide-down" style="color:var(--color-accent-2);font-weight:700;font-size:16px;">✅ Correct!</div>`;
      arena.classList.add('flash-correct');
    } else {
      // False Alarm (Incorrect)
      feedback.innerHTML = `<div class="animate-slide-down" style="color:var(--color-accent-4);font-weight:700;font-size:14px;">❌ False Alarm! Do not press for this shape.</div>`;
      arena.classList.add('flash-incorrect');
    }

    advanceToNextTrial(arena);
  }

  function handleTimeout(trial) {
    if (phase !== 'running') return;
    phase = 'feedback';
    responded = true;

    const feedback = document.getElementById('practice-feedback');
    const arena = document.getElementById('practice-arena');

    if (trial.isTarget) {
      // OMISSION: User failed to press for a target — show miss feedback
      feedback.innerHTML = `<div class="animate-slide-down" style="color:var(--color-accent-4);font-weight:700;font-size:14px;">❌ Missed! Press SPACEBAR when you see a Blue Triangle.</div>`;
      arena.classList.add('flash-incorrect');
    } else {
      // CORRECT REJECTION: User correctly did nothing for a distractor.
      // This is expected behavior — do NOT award a point, just advance silently.
      feedback.innerHTML = `<div class="animate-slide-down" style="color:var(--color-text-muted);font-size:13px;">Good — no response needed for this shape.</div>`;
      // No arena flash, no score increment
    }

    advanceToNextTrial(arena);
  }

  function advanceToNextTrial(arena) {
    isiTimer = setTimeout(() => {
      if (arena) arena.classList.remove('flash-correct', 'flash-incorrect');
      trialIndex++;
      runTrial();
    }, ISI_DURATION);
  }

  let practiceAttempt = 0;

  function showResults() {
    phase = 'done';
    const totalTargets = PRACTICE_SEQUENCE.filter(t => t.isTarget).length;
    const pct = (correct / totalTargets) * 100;
    const passed = pct >= 80;
    practiceAttempt++;

    if (passed) {
      stage.innerHTML = `
        <div class="glass-card card-padded animate-pop text-center">
          <div style="font-size:64px;margin-bottom:16px;">🎉</div>
          <h2 style="color:var(--color-accent-2);margin-bottom:8px;">Excellent!</h2>
          <p style="font-size:16px;margin-bottom:8px;">You scored <strong>${correct}/${PRACTICE_TRIALS} (${Math.round(pct)}%)</strong></p>
          <p style="color:var(--color-text-muted);margin-bottom:28px;">You are ready for the real assessment!</p>
          <button class="btn btn-primary btn-lg" id="go-module1" style="min-width:240px;">
            🚀 Start Module 1 – Sustained Attention
          </button>
        </div>
      `;
      document.getElementById('go-module1').addEventListener('click', () => navigate('/module/sustained'));
    } else if (practiceAttempt < 2) {
      stage.innerHTML = `
        <div class="glass-card card-padded animate-slide-up text-center">
          <div style="font-size:52px;margin-bottom:16px;">😅</div>
          <h2 style="margin-bottom:8px;">Not Quite There</h2>
          <p style="font-size:16px;margin-bottom:6px;">You scored <strong>${correct}/${PRACTICE_TRIALS} (${Math.round(pct)}%)</strong></p>
          <p style="color:var(--color-text-muted);margin-bottom:24px;">You need ≥80% to proceed. Let's try a simpler version.</p>
          <div class="alert alert-warning" style="margin-bottom:24px;text-align:left;">
            <strong>Tip:</strong> Remember — only press SPACEBAR for a <strong style="color:#1E88E5;">Blue Triangle</strong>. Not for any other shape or color.
          </div>
          <button class="btn btn-primary" id="retry-practice" style="min-width:200px;">🔄 Try Again</button>
        </div>
      `;
      document.getElementById('retry-practice').addEventListener('click', () => {
        trialIndex = 0; correct = 0;
        startTrials();
      });
    } else {
      stage.innerHTML = `
        <div class="glass-card card-padded animate-slide-up text-center">
          <div style="font-size:52px;margin-bottom:16px;">💡</div>
          <h2 style="margin-bottom:8px;">That's Okay</h2>
          <p style="margin-bottom:6px;">Practice score: <strong>${correct}/${PRACTICE_TRIALS} (${Math.round(pct)}%)</strong></p>
          <p style="color:var(--color-text-muted);margin-bottom:28px;">
            Would you like to try the assessment later, or proceed anyway?
          </p>
          <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
            <a href="#/" class="btn btn-secondary">← Try Again Later</a>
            <button class="btn btn-primary" id="proceed-anyway">Proceed to Assessment →</button>
          </div>
        </div>
      `;
      document.getElementById('proceed-anyway').addEventListener('click', () => navigate('/module/sustained'));
    }
  }

  // Keyboard handler
  function onKeydown(e) {
    if (e.code === 'Space' && phase === 'running' && !e.repeat) {
      e.preventDefault();
      handleUserResponse(PRACTICE_SEQUENCE[trialIndex]);
    }
  }
  window.addEventListener('keydown', onKeydown);

  showInstructions();

  // Cleanup
  return () => {
    window.removeEventListener('keydown', onKeydown);
    clearTimeout(stimulusTimer);
    clearTimeout(isiTimer);
  };
}
