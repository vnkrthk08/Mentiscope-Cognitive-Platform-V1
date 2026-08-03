const User = require('../models/User');
const Session = require('../models/Session');
const Event = require('../models/Event');
const Score = require('../models/Score');

/**
 * GET /api/admin/dashboard
 * Aggregated dashboard stats
 */
const getDashboard = async (req, res) => {
  try {
    const totalStudents = await User.countDocuments({ role: 'student' });
    const totalAssessments = await Session.countDocuments({ status: 'completed' });

    const scoreAgg = await Score.aggregate([
      {
        $group: {
          _id: null,
          avgScore: { $avg: '$overallScore' },
          highestScore: { $max: '$overallScore' },
        },
      },
    ]);

    const avgScore = scoreAgg.length > 0 ? Math.round(scoreAgg[0].avgScore) : 0;
    const highestScore = scoreAgg.length > 0 ? scoreAgg[0].highestScore : 0;

    // Recent assessments
    const recentAssessments = await Score.find()
      .sort({ completedAt: -1 })
      .limit(10)
      .populate('studentId', 'name email')
      .populate('sessionId', 'startTime endTime');

    // Score distribution for charts
    const scoreDistribution = await Score.aggregate([
      {
        $bucket: {
          groupBy: '$overallScore',
          boundaries: [0, 20, 40, 60, 80, 100, 101],
          default: 'Other',
          output: { count: { $sum: 1 } },
        },
      },
    ]);

    // Average module scores
    const moduleAvg = await Score.aggregate([
      {
        $group: {
          _id: null,
          module1: { $avg: '$moduleScores.module1' },
          module2: { $avg: '$moduleScores.module2' },
          module3: { $avg: '$moduleScores.module3' },
          module4: { $avg: '$moduleScores.module4' },
        },
      },
    ]);

    res.json({
      success: true,
      data: {
        stats: {
          totalStudents,
          totalAssessments,
          avgScore,
          highestScore,
        },
        recentAssessments,
        scoreDistribution,
        moduleAvg: moduleAvg.length > 0 ? moduleAvg[0] : { module1: 0, module2: 0, module3: 0, module4: 0 },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * GET /api/admin/students
 * List all students with their latest scores
 */
const getStudents = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const search = req.query.search || '';

    const query = { role: 'student' };
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
      ];
    }

    const total = await User.countDocuments(query);
    const students = await User.find(query)
      .skip((page - 1) * limit)
      .limit(limit)
      .sort({ createdAt: -1 });

    // Get latest scores for each student
    const studentData = await Promise.all(
      students.map(async (student) => {
        const latestScore = await Score.findOne({ studentId: student._id })
          .sort({ completedAt: -1 });
        const totalSessions = await Session.countDocuments({
          studentId: student._id,
          status: 'completed',
        });

        return {
          id: student._id,
          name: student.name,
          email: student.email,
          createdAt: student.createdAt,
          totalAssessments: totalSessions,
          latestScore: latestScore || null,
        };
      })
    );

    res.json({
      success: true,
      data: {
        students: studentData,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
        },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * GET /api/admin/events
 * Paginated and filterable event logs
 */
const getEvents = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;
    const { studentId, module, eventType, sessionId } = req.query;

    const query = {};
    if (studentId) query.studentId = studentId;
    if (module) query.module = parseInt(module);
    if (eventType) query.eventType = eventType;
    if (sessionId) query.sessionId = sessionId;

    const total = await Event.countDocuments(query);
    const events = await Event.find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .populate('studentId', 'name email')
      .populate('sessionId', 'status currentModule');

    res.json({
      success: true,
      data: {
        events,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
        },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * GET /api/admin/results
 * All assessment results with analytics
 */
const getResults = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;

    const total = await Score.countDocuments();
    const results = await Score.find()
      .sort({ completedAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .populate('studentId', 'name email')
      .populate('sessionId', 'startTime endTime modulesCompleted');

    // Analytics aggregations
    const analytics = await Score.aggregate([
      {
        $group: {
          _id: null,
          avgOverall: { $avg: '$overallScore' },
          avgRecovery: { $avg: '$dimensions.recoveryResilience' },
          avgStress: { $avg: '$dimensions.stressTolerance' },
          avgAdaptation: { $avg: '$dimensions.adaptationPersistence' },
          avgDecision: { $avg: '$dimensions.decisionStability' },
          avgReactionTime: { $avg: '$metrics.avgReactionTime' },
          avgRecoveryLatency: { $avg: '$metrics.avgRecoveryLatency' },
          avgAccuracy: { $avg: '$metrics.decisionAccuracy' },
        },
      },
    ]);

    // Trend data (last 30 assessments)
    const trend = await Score.find()
      .sort({ completedAt: -1 })
      .limit(30)
      .select('overallScore completedAt dimensions.stressTolerance dimensions.decisionStability metrics.avgReactionTime')
      .lean();

    res.json({
      success: true,
      data: {
        results,
        analytics: analytics.length > 0 ? analytics[0] : {},
        trend: trend.reverse(),
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
        },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

module.exports = { getDashboard, getStudents, getEvents, getResults };
