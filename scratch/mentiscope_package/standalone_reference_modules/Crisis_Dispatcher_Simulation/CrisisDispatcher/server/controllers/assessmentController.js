const Session = require('../models/Session');
const Event = require('../models/Event');
const { calculateScore } = require('../services/scoringEngine');
const { ALL_SCENARIOS } = require('../seed/scenarioData');

/**
 * POST /api/assessment/start
 * Start a new assessment session
 */
const startAssessment = async (req, res) => {
  try {
    // Check for existing in-progress session
    const existingSession = await Session.findOne({
      studentId: req.user._id,
      status: 'in-progress',
    });

    if (existingSession) {
      // Return existing session with current module scenarios
      const scenarios = ALL_SCENARIOS[existingSession.currentModule] || ALL_SCENARIOS[1];
      return res.json({
        success: true,
        data: {
          session: existingSession,
          scenarios,
          currentModule: existingSession.currentModule,
          resumed: true,
        },
      });
    }

    // Create new session
    const session = await Session.create({
      studentId: req.user._id,
      startTime: new Date(),
      currentModule: 1,
    });

    // Log ASSESSMENT_STARTED event
    await Event.create({
      studentId: req.user._id,
      sessionId: session._id,
      eventType: 'ASSESSMENT_STARTED',
      timestamp: new Date(),
    });

    res.status(201).json({
      success: true,
      data: {
        session,
        scenarios: ALL_SCENARIOS[1],
        currentModule: 1,
        resumed: false,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * POST /api/assessment/event
 * Log a single event during the assessment
 */
const logEvent = async (req, res) => {
  try {
    const {
      sessionId, module, scenarioId, eventType, reactionTime,
      decisionTime, selectedResource, dispatchedUnits, resourceChange, scenarioOutcome, timeout,
      decision, correct, panicClicks, retryCount,
      strategyChange, recoveryLatency, decisionStability, adaptationRate,
      metadata,
    } = req.body;

    if (!sessionId || !eventType) {
      return res.status(400).json({
        success: false,
        message: 'sessionId and eventType are required',
      });
    }

    // Verify session belongs to user
    const session = await Session.findOne({
      _id: sessionId,
      studentId: req.user._id,
      status: 'in-progress',
    });

    if (!session) {
      return res.status(404).json({
        success: false,
        message: 'Active session not found',
      });
    }

    const event = await Event.create({
      studentId: req.user._id,
      sessionId,
      module,
      scenarioId,
      eventType,
      timestamp: new Date(),
      reactionTime,
      decisionTime,
      selectedResource,
      decision,
      dispatchedUnits,
      correct,
      panicClicks,
      retryCount,
      strategyChange,
      resourceChange,
      recoveryLatency,
      decisionStability,
      adaptationRate,
      scenarioOutcome,
      timeout,
      metadata,
    });

    // If module completed, update session
    if (eventType === 'MODULE_COMPLETED' && module) {
      session.modulesCompleted.push({
        module,
        completedAt: new Date(),
        scenariosCompleted: (ALL_SCENARIOS[module] || []).length,
      });

      if (module < 4) {
        session.currentModule = module + 1;
      }

      await session.save();
    }

    res.status(201).json({
      success: true,
      data: {
        eventId: event._id,
        nextModule: eventType === 'MODULE_COMPLETED' && module < 4
          ? { module: module + 1, scenarios: ALL_SCENARIOS[module + 1] }
          : null,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

/**
 * POST /api/assessment/complete
 * Complete the assessment and calculate scores
 */
const completeAssessment = async (req, res) => {
  try {
    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({
        success: false,
        message: 'sessionId is required',
      });
    }

    const session = await Session.findOne({
      _id: sessionId,
      studentId: req.user._id,
    });

    if (!session) {
      return res.status(404).json({
        success: false,
        message: 'Session not found',
      });
    }

    // Mark session as completed
    session.status = 'completed';
    session.endTime = new Date();
    await session.save();

    // Log ASSESSMENT_COMPLETED event
    await Event.create({
      studentId: req.user._id,
      sessionId: session._id,
      eventType: 'ASSESSMENT_COMPLETED',
      timestamp: new Date(),
    });

    // Calculate scores
    const score = await calculateScore(session._id, req.user._id);

    res.json({
      success: true,
      data: {
        session,
        score,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

module.exports = { startAssessment, logEvent, completeAssessment };
