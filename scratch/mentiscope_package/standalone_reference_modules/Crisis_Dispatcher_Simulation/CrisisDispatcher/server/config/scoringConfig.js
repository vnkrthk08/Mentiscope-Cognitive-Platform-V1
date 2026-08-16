// Dimension weights
const WEIGHTS = {
  recoveryResilience: 0.30,
  stressTolerance: 0.25,
  adaptationPersistence: 0.25,
  decisionStability: 0.20,
};

// Normalization thresholds
const THRESHOLDS = {
  minimumReactionTime: 2000,      // 2 seconds (ideal)
  maximumReactionTime: 15000,     // 15 seconds (worst case)
  maximumPanicClicks: 20,         // per module
  maximumRecoveryLatency: 30000,  // 30 seconds
  decisionStabilityThreshold: 0.5,
  adaptationThreshold: 0.5,
};

module.exports = {
  WEIGHTS,
  THRESHOLDS,
};
