const mongoose = require('mongoose');

const sessionSchema = new mongoose.Schema({
  studentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true,
  },
  startTime: {
    type: Date,
    default: Date.now,
  },
  endTime: {
    type: Date,
  },
  status: {
    type: String,
    enum: ['in-progress', 'completed', 'abandoned'],
    default: 'in-progress',
  },
  currentModule: {
    type: Number,
    min: 1,
    max: 4,
    default: 1,
  },
  modulesCompleted: [{
    module: { type: Number, min: 1, max: 4 },
    completedAt: { type: Date },
    scenariosCompleted: { type: Number, default: 0 },
  }],
}, {
  timestamps: true,
});

// Index for querying active sessions
sessionSchema.index({ studentId: 1, status: 1 });

module.exports = mongoose.model('Session', sessionSchema);
