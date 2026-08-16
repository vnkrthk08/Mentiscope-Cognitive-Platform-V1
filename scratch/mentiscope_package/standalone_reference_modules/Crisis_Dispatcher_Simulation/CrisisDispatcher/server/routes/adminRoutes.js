const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/auth');
const { getDashboard, getStudents, getEvents, getResults } = require('../controllers/adminController');

router.use(protect);
router.use(authorize('admin'));

router.get('/dashboard', getDashboard);
router.get('/students', getStudents);
router.get('/events', getEvents);
router.get('/results', getResults);

module.exports = router;
