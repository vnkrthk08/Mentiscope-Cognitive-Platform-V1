const User = require('../models/User');
const Score = require('../models/Score');
const Session = require('../models/Session');

/**
 * GET /api/student/profile
 * Get student profile
 */
const getProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    const sessions = await Session.find({ studentId: req.user._id })
      .sort({ createdAt: -1 });

    const latestScore = await Score.findOne({ studentId: req.user._id })
      .sort({ completedAt: -1 });

    const activeSession = sessions.find(s => s.status === 'in-progress');

    res.json({
      success: true,
      data: {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
        },
        assessmentStatus: activeSession ? 'in-progress' : 'idle',
        activeSession: activeSession || null,
        totalAssessments: sessions.filter(s => s.status === 'completed').length,
        latestScore: latestScore ? {
          overallScore: latestScore.overallScore,
          completedAt: latestScore.completedAt,
          dimensions: latestScore.dimensions,
        } : null,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * GET /api/student/result
 * Get assessment results for the student
 */
const getResult = async (req, res) => {
  try {
    const scores = await Score.find({ studentId: req.user._id })
      .sort({ completedAt: -1 })
      .populate('sessionId', 'startTime endTime status');

    res.json({
      success: true,
      data: scores,
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

module.exports = { getProfile, getResult };
