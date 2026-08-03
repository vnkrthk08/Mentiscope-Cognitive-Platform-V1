const mongoose = require('mongoose');

const scoreSchema = new mongoose.Schema({
  studentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true,
  },
  sessionId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Session',
    required: true,
    unique: true,
  },
  overallScore: {
    type: Number,
    min: 0,
    max: 100,
    required: true,
  },
  dimensions: {
    recoveryResilience: { type: Number, min: 0, max: 100, default: 0 },
    stressTolerance: { type: Number, min: 0, max: 100, default: 0 },
    adaptationPersistence: { type: Number, min: 0, max: 100, default: 0 },
    decisionStability: { type: Number, min: 0, max: 100, default: 0 },
  },
  gameplayStats: {
    incidentsResolved: { type: Number, default: 0 },
    citizensSaved: { type: Number, default: 0 },
    livesLost: { type: Number, default: 0 },
    resourcesUsed: { type: Number, default: 0 },
  },
  metrics: {
    avgReactionTime: { type: Number, default: 0 },
    panicClickFrequency: { type: Number, default: 0 },
    avgRecoveryLatency: { type: Number, default: 0 },
    strategyChanges: { type: Number, default: 0 },
    decisionAccuracy: { type: Number, default: 0 },
    errorEscalationRate: { type: Number, default: 0 },
    adaptationRate: { type: Number, default: 0 },
    totalRetries: { type: Number, default: 0 },
    totalTimeouts: { type: Number, default: 0 },
    totalDecisions: { type: Number, default: 0 },
    corrects: { type: Number, default: 0 },
  },
  moduleScores: {
    module1: { type: Number, min: 0, max: 100, default: 0 },
    module2: { type: Number, min: 0, max: 100, default: 0 },
    module3: { type: Number, min: 0, max: 100, default: 0 },
    module4: { type: Number, min: 0, max: 100, default: 0 },
  },
  completedAt: {
    type: Date,
    default: Date.now,
  },
}, {
  timestamps: true,
});

// Index for leaderboard queries
scoreSchema.index({ overallScore: -1 });
scoreSchema.index({ studentId: 1, completedAt: -1 });

module.exports = mongoose.model('Score', scoreSchema);
