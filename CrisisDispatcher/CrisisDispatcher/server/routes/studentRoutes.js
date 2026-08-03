const express = require('express');
const router = express.Router();
const { protect, authorize } = require('../middleware/auth');
const { getProfile, getResult } = require('../controllers/studentController');

router.use(protect);
router.use(authorize('student'));

router.get('/profile', getProfile);
router.get('/result', getResult);

module.exports = router;
