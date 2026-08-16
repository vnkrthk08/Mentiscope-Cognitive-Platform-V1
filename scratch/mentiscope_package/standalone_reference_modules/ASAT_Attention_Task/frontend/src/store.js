/* =====================================================
   ASAT – In-memory State Store
   ===================================================== */

const state = {
  // Student registration
  student: null,         // { fullName, studentId, age, grade, school }

  // Session
  sessionId: null,
  sessionUuid: null,

  // Module results (filled as modules complete)
  moduleResults: {
    sustained: null,
    selective: null,
    divided:   null,
    executive: null,
  },

  // Scores computed after each module
  scores: {
    sustained: null,
    selective: null,
    divided:   null,
    executive: null,
    overall:   null,
    percentile: null,
  },

  // Faculty auth
  faculty: null,         // { facultyId, username, fullName, email }

  // Practice state
  practiceAttempts: 0,
  practiceScore: 0,
};

const listeners = new Set();

export function getState() {
  return { ...state };
}

export function setState(partial) {
  Object.assign(state, partial);
  listeners.forEach(fn => fn({ ...state }));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function resetAssessment() {
  state.sessionId = null;
  state.sessionUuid = null;
  state.moduleResults = { sustained: null, selective: null, divided: null, executive: null };
  state.scores = { sustained: null, selective: null, divided: null, executive: null, overall: null, percentile: null };
  state.practiceAttempts = 0;
  state.practiceScore = 0;
}
