export interface GVProgressSnapshot {
  phase: "instructions" | "practice" | "assessment";
  practiceIndex: number;
  assessmentIndex: number;
  updatedAt: string;
}

function key(sessionId: string): string {
  return `mentiscope_gv_progress:${sessionId}`;
}

export function loadGVProgress(sessionId: string): GVProgressSnapshot | null {
  const raw = localStorage.getItem(key(sessionId));
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as GVProgressSnapshot;
    if (
      !["instructions", "practice", "assessment"].includes(parsed.phase) ||
      !Number.isInteger(parsed.practiceIndex) ||
      !Number.isInteger(parsed.assessmentIndex)
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function saveGVProgress(sessionId: string, progress: Omit<GVProgressSnapshot, "updatedAt">): void {
  localStorage.setItem(key(sessionId), JSON.stringify({ ...progress, updatedAt: new Date().toISOString() }));
}

export function clearGVProgress(sessionId: string): void {
  localStorage.removeItem(key(sessionId));
}
