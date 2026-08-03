/* =====================================================
   ASAT – Scientific Scoring Engine
   All formulas exactly as specified.
   28 trials per module.
   ===================================================== */

/** Clamp a number to [min, max] */
function clamp(val, min = 0, max = 100) {
  return Math.min(max, Math.max(min, val));
}

/** Standard deviation of an array */
function stdDev(arr) {
  if (!arr || arr.length < 2) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  const variance = arr.reduce((a, b) => a + (b - mean) ** 2, 0) / arr.length;
  return Math.sqrt(variance);
}

/** Linear regression slope (for fatigue) */
function linearSlope(arr) {
  if (!arr || arr.length < 2) return 0;
  const n = arr.length;
  const xs = arr.map((_, i) => i);
  const meanX = (n - 1) / 2;
  const meanY = arr.reduce((a, b) => a + b, 0) / n;
  const num = xs.reduce((acc, x, i) => acc + (x - meanX) * (arr[i] - meanY), 0);
  const den = xs.reduce((acc, x) => acc + (x - meanX) ** 2, 0);
  return den === 0 ? 0 : num / den;
}

/** Calculate Fatigue Slope Score based on 3 blocks of RTs */
export function calculateFatigueScore(rtList) {
  if (!rtList || rtList.length < 3) return { slope: 0, score: 100 };
  const blockSize = Math.ceil(rtList.length / 3);
  const blocks = [0, 1, 2].map(i => rtList.slice(i * blockSize, (i + 1) * blockSize));
  const blockMeans = blocks.map(b => b.length ? b.reduce((a, c) => a + c, 0) / b.length : 0);
  const fatigueSlope = linearSlope(blockMeans);
  const fatigueScore = clamp(100 - (Math.max(0, fatigueSlope) / 400) * 100);
  return { slope: fatigueSlope, score: fatigueScore };
}

/** Attention Stability Index */
export function calculateAttentionStability(hitRate, rtVariabilityScore, fatigueScore) {
  return clamp((hitRate * 0.40) + (rtVariabilityScore * 0.30) + (fatigueScore * 0.30));
}

/** Impulsivity Index */
export function calculateImpulsivityIndex(falseAlarms, totalDistractors) {
  if (totalDistractors === 0) return 0;
  return clamp((falseAlarms / totalDistractors) * 100);
}

/** Recovery After Errors */
export function calculateRecoveryAfterErrors(correctnessArray) {
  if (!correctnessArray || correctnessArray.length === 0) return 0;
  let errorCount = 0;
  let totalRecoveryTrials = 0;
  let inErrorState = false;
  let trialsSinceError = 0;

  for (let i = 0; i < correctnessArray.length; i++) {
    const isCorrect = correctnessArray[i];
    if (!isCorrect) {
      if (!inErrorState) {
        inErrorState = true;
        errorCount++;
        trialsSinceError = 0;
      }
      trialsSinceError++;
    } else {
      if (inErrorState) {
        totalRecoveryTrials += trialsSinceError;
        inErrorState = false;
      }
    }
  }
  return errorCount > 0 ? (totalRecoveryTrials / errorCount) : 0;
}

/* ────────────────────────────────────────────────────
   MODULE 1 – SUSTAINED ATTENTION (weight: 25%)
   ──────────────────────────────────────────────────── */
export function scoreSustained({ hits, totalTargets, rtList, trialRTs, correctnessArray = [], falseAlarms = 0, totalDistractors = 0 }) {
  const missed = totalTargets - hits;
  const omissionRate = totalTargets > 0 ? (missed / totalTargets) * 100 : 100;
  const hitRate = 100 - omissionRate;

  const rtStdDev = stdDev(rtList);
  const rtVariabilityScore = clamp(100 - (rtStdDev / 500) * 100);

  const fatigue = calculateFatigueScore(rtList);
  const fatigueSlope = fatigue.slope;
  const fatigueScore = fatigue.score;

  const attentionStability = calculateAttentionStability(hitRate, rtVariabilityScore, fatigueScore);
  const impulsivityIndex = calculateImpulsivityIndex(falseAlarms, totalDistractors);
  const recoveryTrials = calculateRecoveryAfterErrors(correctnessArray);

  const score = clamp(hitRate * 0.80 + clamp(100 - (falseAlarms / (totalDistractors || 1)) * 100) * 0.20);

  return {
    score: Math.round(score * 10) / 10,
    hitRate: Math.round(hitRate * 10) / 10,
    omissionRate: Math.round(omissionRate * 10) / 10,
    rtVariabilityScore: Math.round(rtVariabilityScore * 10) / 10,
    fatigueScore: Math.round(fatigueScore * 10) / 10,
    rtStdDev: Math.round(rtStdDev),
    avgRT: rtList.length ? Math.round(rtList.reduce((a, b) => a + b, 0) / rtList.length) : 0,
    attentionStability: Math.round(attentionStability * 10) / 10,
    impulsivityIndex: Math.round(impulsivityIndex * 10) / 10,
    recoveryTrials: Math.round(recoveryTrials * 10) / 10,
    fatigueSlope: Math.round(fatigueSlope * 10) / 10,
  };
}


/* ────────────────────────────────────────────────────
   MODULE 2 – SELECTIVE ATTENTION (weight: 25%)
   ──────────────────────────────────────────────────── */
export function scoreSelective({ correctClicks, totalTargets, wrongClicks, totalDistractors, rtHigh, rtLow, rtList = [], correctnessArray = [] }) {
  const hitRate = totalTargets > 0 ? (correctClicks / totalTargets) * 100 : 0;
  const falseAlarmRate = totalDistractors > 0 ? (wrongClicks / totalDistractors) * 100 : 0;
  const falseAlarmScore = clamp(100 - falseAlarmRate);

  const distractorCost = Math.max(0, (rtHigh || 0) - (rtLow || 0));
  const distractorScore = clamp(100 - (distractorCost / 300) * 100);

  const rtStdDev = stdDev(rtList);
  const rtVariabilityScore = clamp(100 - (rtStdDev / 500) * 100);

  const fatigue = calculateFatigueScore(rtList);
  const attentionStability = calculateAttentionStability(hitRate, rtVariabilityScore, fatigue.score);
  const impulsivityIndex = calculateImpulsivityIndex(wrongClicks, totalDistractors);
  const recoveryTrials = calculateRecoveryAfterErrors(correctnessArray);

  const score = clamp(hitRate * 0.50 + falseAlarmScore * 0.50);

  return {
    score: Math.round(score * 10) / 10,
    hitRate: Math.round(hitRate * 10) / 10,
    falseAlarmRate: Math.round(falseAlarmRate * 10) / 10,
    falseAlarmScore: Math.round(falseAlarmScore * 10) / 10,
    distractorScore: Math.round(distractorScore * 10) / 10,
    distractorCost: Math.round(distractorCost),
    rtStdDev: Math.round(rtStdDev),
    fatigueSlope: Math.round(fatigue.slope * 10) / 10,
    attentionStability: Math.round(attentionStability * 10) / 10,
    impulsivityIndex: Math.round(impulsivityIndex * 10) / 10,
    recoveryTrials: Math.round(recoveryTrials * 10) / 10,
  };
}

/* ────────────────────────────────────────────────────
   MODULE 3 – DIVIDED ATTENTION (weight: 20%)
   ──────────────────────────────────────────────────── */
export function scoreDivided({ correctPresses, totalTargets, falsePresses, totalNonTargets, rtDual, rtSingle, rtList = [], correctnessArray = [] }) {
  const hitRate = totalTargets > 0 ? (correctPresses / totalTargets) * 100 : 0;
  const falseAlarmRate = totalNonTargets > 0 ? (falsePresses / totalNonTargets) * 100 : 0;
  const falseAlarmScore = clamp(100 - falseAlarmRate);

  const splitCost = Math.max(0, (rtDual || 0) - (rtSingle || 0));
  const splitScore = clamp(100 - (splitCost / 300) * 100);

  const rtStdDev = stdDev(rtList);
  const rtVariabilityScore = clamp(100 - (rtStdDev / 500) * 100);

  const fatigue = calculateFatigueScore(rtList);
  const attentionStability = calculateAttentionStability(hitRate, rtVariabilityScore, fatigue.score);
  const impulsivityIndex = calculateImpulsivityIndex(falsePresses, totalNonTargets);
  const recoveryTrials = calculateRecoveryAfterErrors(correctnessArray);

  const score = clamp(hitRate * 0.50 + falseAlarmScore * 0.50);

  return {
    score: Math.round(score * 10) / 10,
    hitRate: Math.round(hitRate * 10) / 10,
    falseAlarmRate: Math.round(falseAlarmRate * 10) / 10,
    falseAlarmScore: Math.round(falseAlarmScore * 10) / 10,
    splitScore: Math.round(splitScore * 10) / 10,
    splitCost: Math.round(splitCost),
    rtStdDev: Math.round(rtStdDev),
    fatigueSlope: Math.round(fatigue.slope * 10) / 10,
    attentionStability: Math.round(attentionStability * 10) / 10,
    impulsivityIndex: Math.round(impulsivityIndex * 10) / 10,
    recoveryTrials: Math.round(recoveryTrials * 10) / 10,
  };
}

/* ────────────────────────────────────────────────────
   MODULE 4 – EXECUTIVE ATTENTION (weight: 30%)
   ──────────────────────────────────────────────────── */
export function scoreExecutive({ rtBeforeSwitch, rtAfterSwitch, switchErrors, totalAfterSwitch, recoveryTrials, rtList = [], correctnessArray = [], totalDistractors = 0, falseAlarms = 0 }) {
  const switchCost = Math.max(0, (rtAfterSwitch || 0) - (rtBeforeSwitch || 0));
  const switchCostScore = clamp(100 - (switchCost / 400) * 100);

  const switchErrorRate = totalAfterSwitch > 0
    ? (switchErrors / totalAfterSwitch) * 100
    : 0;
  const switchErrorScore = clamp(100 - switchErrorRate);

  const recoveryTimeScore = clamp(100 - (recoveryTrials / 10) * 100);

  const rtStdDev = stdDev(rtList);
  const rtVariabilityScore = clamp(100 - (rtStdDev / 500) * 100);
  
  const fatigue = calculateFatigueScore(rtList);
  const hitRate = 100 - switchErrorRate; // Approximation for Executive
  const attentionStability = calculateAttentionStability(hitRate, rtVariabilityScore, fatigue.score);
  const impulsivityIndex = calculateImpulsivityIndex(falseAlarms, totalDistractors);
  
  // Overall recovery across the entire module (not just rule switches)
  const generalRecoveryTrials = calculateRecoveryAfterErrors(correctnessArray);

  const score = clamp(
    switchCostScore * 0.20 + switchErrorScore * 0.50 + recoveryTimeScore * 0.30
  );

  return {
    score: Math.round(score * 10) / 10,
    switchCost: Math.round(switchCost),
    switchCostScore: Math.round(switchCostScore * 10) / 10,
    switchErrorRate: Math.round(switchErrorRate * 10) / 10,
    switchErrorScore: Math.round(switchErrorScore * 10) / 10,
    recoveryTimeScore: Math.round(recoveryTimeScore * 10) / 10,
    recoveryTrials: Math.round(recoveryTrials * 10) / 10, // Switch-specific recovery
    adaptationSpeed: Math.round(recoveryTrials * 10) / 10, // Adaptation Speed = Trials to correct after switch
    rtStdDev: Math.round(rtStdDev),
    fatigueSlope: Math.round(fatigue.slope * 10) / 10,
    attentionStability: Math.round(attentionStability * 10) / 10,
    impulsivityIndex: Math.round(impulsivityIndex * 10) / 10,
    generalRecoveryTrials: Math.round(generalRecoveryTrials * 10) / 10,
  };
}

/* ────────────────────────────────────────────────────
   OVERALL SCORE
   ──────────────────────────────────────────────────── */
export function scoreOverall({ sustained, selective, divided, executive }) {
  const overall = clamp(
    sustained * 0.25 + selective * 0.25 + divided * 0.20 + executive * 0.30
  );
  return Math.round(overall * 10) / 10;
}

/** Derive a simple percentile from overall score (normative approximation) */
export function estimatePercentile(overall) {
  if (overall >= 90) return 95;
  if (overall >= 80) return 82;
  if (overall >= 70) return 68;
  if (overall >= 60) return 52;
  if (overall >= 50) return 38;
  if (overall >= 40) return 25;
  return 12;
}

/** Get status label and color class from score */
export function getScoreStatus(score) {
  if (score >= 80) return { label: 'Excellent', cls: 'high',   badge: 'badge-success' };
  if (score >= 65) return { label: 'Good',      cls: 'high',   badge: 'badge-success' };
  if (score >= 50) return { label: 'Average',   cls: 'medium', badge: 'badge-warning' };
  return               { label: 'Needs Work', cls: 'low',    badge: 'badge-error' };
}

/** Generate study strategies based on weakest module */
export function getRecommendations(scores) {
  const { sustained, selective, divided, executive } = scores;

  const strategies = [];
  const careers = { good: [], poor: [] };

  // Sustained recommendations
  if (sustained < 65) {
    strategies.push('Use a timer (Pomodoro: 25 min on, 5 min off) to build focus endurance');
    strategies.push('Eliminate background distractions before study sessions');
    careers.poor.push('Air Traffic Control', 'Emergency Dispatch');
  } else {
    careers.good.push('Research', 'Engineering', 'Data Analysis');
  }

  // Selective recommendations
  if (selective < 65) {
    strategies.push('Practice selective reading — highlight only key phrases');
    strategies.push('Create a distraction-free environment for studying');
  } else {
    careers.good.push('Law', 'Medicine', 'Quality Assurance');
  }

  // Divided recommendations
  if (divided < 65) {
    strategies.push('Use single-tasking — focus on ONE subject at a time');
    strategies.push('Take deliberate breaks when switching between tasks');
    careers.poor.push('Emergency Medicine', 'Stock Trading');
  } else {
    careers.good.push('Management', 'Teaching', 'Project Management');
  }

  // Executive recommendations
  if (executive < 65) {
    strategies.push('Practice mental flexibility: switch between topics deliberately');
    strategies.push('Use checklists to structure task-switching');
    careers.poor.push('Fast-paced Trading', 'Crisis Management');
  } else {
    careers.good.push('Strategy Consulting', 'Leadership', 'Entrepreneurship');
  }

  // Deduplicate
  const uniqueGood = [...new Set(careers.good)].slice(0, 5);
  const uniquePoor = [...new Set(careers.poor)].slice(0, 3);
  const uniqueStrategies = [...new Set(strategies)].slice(0, 5);

  return {
    strategies: uniqueStrategies,
    careers: { good: uniqueGood, poor: uniquePoor },
  };
}
