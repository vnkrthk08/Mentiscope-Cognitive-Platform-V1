const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/auth');
const { startAssessment, logEvent, completeAssessment } = require('../controllers/assessmentController');

router.use(protect);
router.use(authorize('student'));

router.post('/start', startAssessment);
router.post('/event', logEvent);
router.post('/complete', completeAssessment);

module.exports = router;
