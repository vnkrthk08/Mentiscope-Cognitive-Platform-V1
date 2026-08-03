const Event = require('../models/Event');
const Score = require('../models/Score');
const { WEIGHTS, THRESHOLDS } = require('../config/scoringConfig');

/**
 * Normalize a value inversely (lower is better) to 0-100 scale
 */
function inverseNormalize(value, ideal, worst) {
  if (value <= ideal) return 100;
  if (value >= worst) return 0;
  return Math.round(((worst - value) / (worst - ideal)) * 100);
}

/**
 * Normalize a value directly (higher is better) to 0-100 scale
 */
function directNormalize(value, min, max) {
  if (value >= max) return 100;
  if (value <= min) return 0;
  return Math.round(((value - min) / (max - min)) * 100);
}

/**
 * Calculate module-level score
 */
function calculateModuleScore(moduleEvents) {
  if (!moduleEvents.length) return 0;

  const decisions = moduleEvents.filter(e =>
    ['CORRECT_DECISION', 'WRONG_DECISION'].includes(e.eventType)
  );
  const correct = decisions.filter(e => e.eventType === 'CORRECT_DECISION').length;
  const accuracy = decisions.length > 0 ? (correct / decisions.length) * 100 : 0;

  const reactionTimes = moduleEvents
    .filter(e => (e.reactionTime && e.reactionTime > 0) || (e.decisionTime && e.decisionTime > 0))
    .map(e => e.reactionTime || e.decisionTime);
  const avgRT = reactionTimes.length > 0
    ? reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length
    : THRESHOLDS.maximumReactionTime;

  const rtScore = inverseNormalize(avgRT, THRESHOLDS.minimumReactionTime, THRESHOLDS.maximumReactionTime);

  return Math.round((accuracy * 0.6) + (rtScore * 0.4));
}

/**
 * Calculate Recovery & Resilience score (30%)
 * Based on: recovery latency, retry attempts, persistence after failure
 */
function calcRecoveryResilience(events) {
  // Recovery latency (from Module 3 primarily)
  const recoveryEvents = events.filter(e => e.recoveryLatency && e.recoveryLatency > 0);
  const avgRecoveryLatency = recoveryEvents.length > 0
    ? recoveryEvents.reduce((a, b) => a + b.recoveryLatency, 0) / recoveryEvents.length
    : THRESHOLDS.maximumRecoveryLatency;
  const recoveryScore = inverseNormalize(
    avgRecoveryLatency,
    3000, // Hardcoded ideal as per old value for calculation
    THRESHOLDS.maximumRecoveryLatency
  );

  // Persistence: did the student keep trying after failures?
  const module3Events = events.filter(e => e.module === 3);
  const wrongDecisions = module3Events.filter(e => e.eventType === 'WRONG_DECISION').length;
  const retries = module3Events.filter(e => e.retryCount > 0);
  const totalRetries = retries.reduce((sum, e) => sum + e.retryCount, 0);
  const persistenceScore = wrongDecisions > 0
    ? directNormalize(totalRetries / wrongDecisions, 0, 2)
    : 80; // Default if no failures occurred

  // Post-failure accuracy
  const postFailureDecisions = module3Events.filter(
    e => ['CORRECT_DECISION', 'WRONG_DECISION'].includes(e.eventType)
  );
  const postFailureCorrect = postFailureDecisions.filter(
    e => e.eventType === 'CORRECT_DECISION'
  ).length;
  const postFailureAccuracy = postFailureDecisions.length > 0
    ? (postFailureCorrect / postFailureDecisions.length) * 100
    : 50;

  return Math.round((recoveryScore * 0.4) + (persistenceScore * 0.3) + (postFailureAccuracy * 0.3));
}

/**
 * Calculate Stress Tolerance score (25%)
 * Based on: panic clicks, reaction time under stress, accuracy in Module 2
 */
function calcStressTolerance(events) {
  const module2Events = events.filter(e => e.module === 2);

  // Panic click frequency
  const panicEvents = module2Events.filter(e => e.eventType === 'PANIC_CLICK');
  const totalPanicClicks = panicEvents.reduce((sum, e) => sum + (e.panicClicks || 1), 0);
  const panicScore = inverseNormalize(totalPanicClicks, 0, THRESHOLDS.maximumPanicClicks);

  // Reaction time under stress
  const stressRT = module2Events
    .filter(e => (e.reactionTime && e.reactionTime > 0) || (e.decisionTime && e.decisionTime > 0))
    .map(e => e.reactionTime || e.decisionTime);
  const avgStressRT = stressRT.length > 0
    ? stressRT.reduce((a, b) => a + b, 0) / stressRT.length
    : THRESHOLDS.maximumReactionTime;
  const rtScore = inverseNormalize(avgStressRT, THRESHOLDS.minimumReactionTime, THRESHOLDS.maximumReactionTime);

  // Decision accuracy under stress
  const stressDecisions = module2Events.filter(
    e => ['CORRECT_DECISION', 'WRONG_DECISION'].includes(e.eventType)
  );
  const stressCorrect = stressDecisions.filter(e => e.eventType === 'CORRECT_DECISION').length;
  const stressAccuracy = stressDecisions.length > 0
    ? (stressCorrect / stressDecisions.length) * 100
    : 50;

  // Timeouts (penalty)
  const timeouts = module2Events.filter(e => e.eventType === 'TIMEOUT').length;
  const timeoutPenalty = Math.min(timeouts * 5, 25); // Max 25 point penalty

  const rawScore = (panicScore * 0.35) + (rtScore * 0.30) + (stressAccuracy * 0.35);
  return Math.max(0, Math.round(rawScore - timeoutPenalty));
}

/**
 * Calculate Adaptation & Persistence score (25%)
 * Based on: strategy changes, retry count, adaptation rate from Module 4
 */
function calcAdaptationPersistence(events) {
  const module4Events = events.filter(e => e.module === 4);

  // Adaptation rate
  const adaptationEvents = module4Events.filter(e => e.adaptationRate != null);
  const avgAdaptation = adaptationEvents.length > 0
    ? adaptationEvents.reduce((a, b) => a + b.adaptationRate, 0) / adaptationEvents.length
    : 0.5;
  const adaptationScore = directNormalize(avgAdaptation, 0, 1) ;

  // Strategic flexibility (strategy changes that led to correct decisions)
  const strategyChanges = events.filter(e => e.strategyChange);
  const successfulChanges = strategyChanges.filter(e => e.correct).length;
  const flexibilityScore = strategyChanges.length > 0
    ? (successfulChanges / strategyChanges.length) * 100
    : 50;

  // Overall retry persistence across all modules
  const allRetries = events.filter(e => e.retryCount > 0);
  const totalRetries = allRetries.reduce((sum, e) => sum + e.retryCount, 0);
  const persistScore = directNormalize(totalRetries, 0, 10);

  return Math.round((adaptationScore * 0.40) + (flexibilityScore * 0.35) + (persistScore * 0.25));
}

/**
 * Calculate Decision Stability score (20%)
 * Based on: decision consistency, error escalation, resource change frequency
 */
function calcDecisionStability(events) {
  // Decision stability from events
  const stabilityEvents = events.filter(e => e.decisionStability != null);
  const avgStability = stabilityEvents.length > 0
    ? stabilityEvents.reduce((a, b) => a + b.decisionStability, 0) / stabilityEvents.length
    : 0.5;
  const stabilityScore = directNormalize(avgStability, 0, 1);

  // Error escalation: are errors getting worse over time?
  const decisions = events
    .filter(e => ['CORRECT_DECISION', 'WRONG_DECISION'].includes(e.eventType))
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  let errorEscalation = 0;
  if (decisions.length >= 4) {
    const halfPoint = Math.floor(decisions.length / 2);
    const firstHalf = decisions.slice(0, halfPoint);
    const secondHalf = decisions.slice(halfPoint);

    const firstErrors = firstHalf.filter(e => e.eventType === 'WRONG_DECISION').length / firstHalf.length;
    const secondErrors = secondHalf.filter(e => e.eventType === 'WRONG_DECISION').length / secondHalf.length;

    errorEscalation = secondErrors - firstErrors; // Positive means more errors later
  }
  const escalationScore = inverseNormalize(Math.max(0, errorEscalation), 0, 0.5) ;

  // Resource change frequency (excessive changes indicate indecision)
  const resourceChanges = events.filter(e => e.eventType === 'RESOURCE_CHANGED').length;
  const totalDecisions = decisions.length || 1;
  const changeRatio = resourceChanges / totalDecisions;
  const consistencyScore = inverseNormalize(changeRatio, 0, 2);

  return Math.round((stabilityScore * 0.40) + (escalationScore * 0.30) + (consistencyScore * 0.30));
}

/**
 * Main scoring function - processes all events for a session
 * and generates the complete score breakdown
 */
async function calculateScore(sessionId, studentId) {
  const events = await Event.find({ sessionId }).sort({ timestamp: 1 });

  if (events.length === 0) {
    throw new Error('No events found for this session');
  }

  // Calculate dimension scores
  const recoveryResilience = calcRecoveryResilience(events);
  const stressTolerance = calcStressTolerance(events);
  const adaptationPersistence = calcAdaptationPersistence(events);
  const decisionStabilityScore = calcDecisionStability(events);

  // Weighted overall score
  const overallScore = Math.round(
    (recoveryResilience * WEIGHTS.recoveryResilience) +
    (stressTolerance * WEIGHTS.stressTolerance) +
    (adaptationPersistence * WEIGHTS.adaptationPersistence) +
    (decisionStabilityScore * WEIGHTS.decisionStability)
  );

  // Calculate raw metrics
  const allReactionTimes = events
    .filter(e => (e.reactionTime && e.reactionTime > 0) || (e.decisionTime && e.decisionTime > 0))
    .map(e => e.reactionTime || e.decisionTime);
  const avgReactionTime = allReactionTimes.length > 0
    ? Math.round(allReactionTimes.reduce((a, b) => a + b, 0) / allReactionTimes.length)
    : 0;

  const totalPanicClicks = events
    .filter(e => e.eventType === 'PANIC_CLICK')
    .reduce((sum, e) => sum + (e.panicClicks || 1), 0);
  const panicClickFrequency = events.length > 0
    ? Math.round((totalPanicClicks / events.length) * 100) / 100
    : 0;

  const recoveryLatencies = events
    .filter(e => e.recoveryLatency && e.recoveryLatency > 0)
    .map(e => e.recoveryLatency);
  const avgRecoveryLatency = recoveryLatencies.length > 0
    ? Math.round(recoveryLatencies.reduce((a, b) => a + b, 0) / recoveryLatencies.length)
    : 0;

  const strategyChanges = events.filter(e => e.strategyChange).length;

  const allDecisions = events.filter(
    e => ['CORRECT_DECISION', 'WRONG_DECISION'].includes(e.eventType)
  );
  const corrects = allDecisions.filter(e => e.eventType === 'CORRECT_DECISION').length;
  const decisionAccuracy = allDecisions.length > 0
    ? Math.round((corrects / allDecisions.length) * 100)
    : 0;

  // Error escalation rate
  let errorEscalationRate = 0;
  if (allDecisions.length >= 4) {
    const half = Math.floor(allDecisions.length / 2);
    const firstErrors = allDecisions.slice(0, half).filter(e => e.eventType === 'WRONG_DECISION').length / half;
    const secondErrors = allDecisions.slice(half).filter(e => e.eventType === 'WRONG_DECISION').length / (allDecisions.length - half);
    errorEscalationRate = Math.round((secondErrors - firstErrors) * 100) / 100;
  }

  const adaptationRates = events.filter(e => e.adaptationRate != null).map(e => e.adaptationRate);
  const avgAdaptationRate = adaptationRates.length > 0
    ? Math.round((adaptationRates.reduce((a, b) => a + b, 0) / adaptationRates.length) * 100) / 100
    : 0;

  const totalRetries = events.reduce((sum, e) => sum + (e.retryCount || 0), 0);
  const totalTimeouts = events.filter(e => e.eventType === 'TIMEOUT').length;

  // Calculate gameplayStats
  const incidentsResolved = events.filter(e => e.eventType === 'SCENARIO_COMPLETED').length;
  let citizensSaved = 0;
  let livesLost = 0;
  const resourcesUsed = events.filter(e => e.eventType === 'RESOURCE_DISPATCHED').length;

  events.forEach(e => {
    if (e.eventType === 'SCENARIO_COMPLETED') {
       citizensSaved += (e.metadata?.livesAtRisk || 10);
    } else if (e.eventType === 'TIMEOUT' || e.eventType === 'WRONG_DECISION') {
       if (e.metadata && e.metadata.livesAtRisk) {
         livesLost += Math.floor(e.metadata.livesAtRisk * 0.5); // Penalty
       }
    }
  });

  // Module scores
  const moduleScores = {};
  for (let m = 1; m <= 4; m++) {
    const moduleEvents = events.filter(e => e.module === m);
    moduleScores[`module${m}`] = calculateModuleScore(moduleEvents);
  }

  // Create/update score document
  const scoreData = {
    studentId,
    sessionId,
    overallScore: Math.max(0, Math.min(100, overallScore)),
    dimensions: {
      recoveryResilience,
      stressTolerance,
      adaptationPersistence,
      decisionStability: decisionStabilityScore,
    },
    gameplayStats: {
      incidentsResolved,
      citizensSaved,
      livesLost,
      resourcesUsed,
    },
    metrics: {
      avgReactionTime,
      panicClickFrequency,
      avgRecoveryLatency,
      strategyChanges,
      decisionAccuracy,
      errorEscalationRate,
      adaptationRate: avgAdaptationRate,
      totalRetries,
      totalTimeouts,
      totalDecisions: allDecisions.length,
      corrects,
    },
    moduleScores,
    completedAt: new Date(),
  };

  const score = await Score.findOneAndUpdate(
    { sessionId },
    scoreData,
    { upsert: true, new: true }
  );

  return score;
}

module.exports = { calculateScore };
