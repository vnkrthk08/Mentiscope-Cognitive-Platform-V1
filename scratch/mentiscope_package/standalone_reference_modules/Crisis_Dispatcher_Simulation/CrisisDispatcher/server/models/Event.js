const mongoose = require('mongoose');

const EVENT_TYPES = [
  'ASSESSMENT_STARTED',
  'MODULE_STARTED',
  'SCENARIO_CREATED',
  'SCENARIO_UPDATED',
  'SCENARIO_COMPLETED',
  'INCIDENT_SELECTED',
  'RESOURCE_SELECTED',
  'RESOURCE_CHANGED',
  'RESOURCE_DISPATCHED',
  'CORRECT_DECISION',
  'WRONG_DECISION',
  'PANIC_CLICK',
  'TIMEOUT',
  'FAILURE_OCCURRED',
  'RECOVERY_STARTED',
  'RECOVERY_COMPLETED',
  'ADAPTATION_EVENT',
  'MODULE_COMPLETED',
  'ASSESSMENT_COMPLETED',
];

const eventSchema = new mongoose.Schema({
  studentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  sessionId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Session',
    required: true,
  },
  module: {
    type: Number,
    min: 1,
    max: 4,
  },
  scenarioId: {
    type: String,
  },
  eventType: {
    type: String,
    enum: EVENT_TYPES,
    required: true,
  },
  timestamp: {
    type: Date,
    default: Date.now,
  },
  reactionTime: {
    type: Number, // milliseconds
    default: null,
  },
  decisionTime: {
    type: Number,
    default: null,
  },
  selectedResource: {
    type: String,
    default: null,
  },
  decision: {
    type: [String],
    default: [],
  },
  dispatchedUnits: {
    type: [String],
    default: [],
  },
  correct: {
    type: Boolean,
    default: null,
  },
  panicClicks: {
    type: Number,
    default: 0,
  },
  retryCount: {
    type: Number,
    default: 0,
  },
  strategyChange: {
    type: Boolean,
    default: false,
  },
  resourceChange: {
    type: Boolean,
    default: false,
  },
  recoveryLatency: {
    type: Number, // milliseconds
    default: null,
  },
  decisionStability: {
    type: Number, // 0-1 score
    default: null,
  },
  adaptationRate: {
    type: Number, // 0-1 score
    default: null,
  },
  scenarioOutcome: {
    type: String,
    default: null,
  },
  timeout: {
    type: Boolean,
    default: false,
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {},
  },
}, {
  timestamps: true,
  toJSON: {
    virtuals: true,
    transform: (doc, ret) => {
      ret.id = ret._id;
      delete ret._id;
      delete ret.__v;
    }
  }
});

// Compound indexes for efficient querying
eventSchema.index({ studentId: 1, sessionId: 1 });
eventSchema.index({ sessionId: 1, module: 1 });
eventSchema.index({ eventType: 1, timestamp: -1 });

module.exports = mongoose.model('Event', eventSchema);
module.exports.EVENT_TYPES = EVENT_TYPES;
