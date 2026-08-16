import { AssessmentLaunchContext, GVClientEvent, GVEventType, GVItem } from "./types";

export function createGVEvent(
  context: AssessmentLaunchContext,
  sessionStartedAt: number,
  eventType: GVEventType,
  options: {
    item?: GVItem | null;
    response?: Record<string, unknown>;
    correct?: boolean | null;
    timeTaken?: number;
    attemptNumber?: number;
  } = {},
): GVClientEvent {
  const now = Date.now();
  return {
    event_id: crypto.randomUUID(),
    student_id: context.student_id,
    session_id: context.session_id,
    module_id: context.module_id,
    subtest_id: options.item?.subtest_id ?? null,
    item_id: options.item?.item_id ?? null,
    event_type: eventType,
    response: options.response ?? {},
    correct: options.correct ?? null,
    time_taken: Math.max(0, options.timeTaken ?? 0),
    time_since_session_start: Math.max(0, (now - sessionStartedAt) / 1000),
    attempt_number: Math.max(1, options.attemptNumber ?? 1),
    difficulty_level: options.item?.difficulty_level ?? context.difficulty,
    timestamp: new Date(now).toISOString(),
  };
}
