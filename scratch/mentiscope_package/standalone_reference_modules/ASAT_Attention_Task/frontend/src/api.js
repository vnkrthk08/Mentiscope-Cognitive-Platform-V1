/* =====================================================
   ASAT – API Wrapper
   ===================================================== */

const BASE = '/api';

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(BASE + path, opts);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const err = new Error(data.error || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  // Auth
  register:  (payload) => request('POST', '/auth/register', payload),
  login:     (payload) => request('POST', '/auth/login', payload),
  logout:    ()        => request('POST', '/auth/logout'),
  me:        ()        => request('GET',  '/auth/me'),

  // Students
  createStudent:  (payload) => request('POST', '/students', payload),
  listStudents:   ()        => request('GET',  '/students'),
  getStudent:     (id)      => request('GET',  `/students/${id}`),

  // Sessions
  createSession:  (payload) => request('POST', '/sessions', payload),
  updateSession:  (id, payload) => request('PATCH', `/sessions/${id}`, payload),
  saveModule:     (id, payload) => request('POST', `/sessions/${id}/modules`, payload),
  saveEvents:     (id, payload) => request('POST', `/sessions/${id}/events`, payload),

  // Reports
  exportCSV: () => fetch('/api/reports/csv', { credentials: 'include' }),
};
