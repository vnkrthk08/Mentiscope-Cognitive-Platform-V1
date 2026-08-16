import api from './axios';

// ===== Auth =====
export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// ===== Student =====
export const studentService = {
  getProfile: () => api.get('/student/profile'),
  getResult: () => api.get('/student/result'),
};

// ===== Assessment =====
export const assessmentService = {
  start: () => api.post('/assessment/start'),
  logEvent: (data) => api.post('/assessment/event', data),
  complete: (data) => api.post('/assessment/complete', data),
};

// ===== Admin =====
export const adminService = {
  getDashboard: () => api.get('/admin/dashboard'),
  getStudents: (params) => api.get('/admin/students', { params }),
  getEvents: (params) => api.get('/admin/events', { params }),
  getResults: (params) => api.get('/admin/results', { params }),
};
