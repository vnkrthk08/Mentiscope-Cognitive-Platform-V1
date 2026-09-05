export const GV_MODULE_ID = "GV_VISUAL_PROCESSING_BATTERY" as const;
export const GV_CONSTRUCT = "CHC_Gv_Visual_Processing" as const;

export interface AssessmentLaunchContext {
  student_id: string;
  session_id: string;
  module_id: typeof GV_MODULE_ID;
  module_name: "Visual Processing Battery";
  construct: typeof GV_CONSTRUCT;
  difficulty: number;
  access_token?: string;
}

export type GVEventType =
  | "session_started"
  | "instructions_viewed"
  | "practice_started"
  | "practice_answered"
  | "practice_completed"
  | "subtest_started"
  | "item_presented"
  | "option_selected"
  | "piece_selected"
  | "distractor_selected"
  | "piece_rotated"
  | "piece_placed"
  | "answer_submitted"
  | "item_completed"
  | "navigation_attempted"
  | "subtest_completed"
  | "assessment_finished"
  | "result_viewed"
  | "session_abandoned";

export interface GVClientEvent {
  event_id: string;
  student_id: string;
  session_id: string;
  module_id: typeof GV_MODULE_ID;
  subtest_id: string | null;
  item_id: string | null;
  event_type: GVEventType;
  response: Record<string, unknown>;
  correct: boolean | null;
  time_taken: number;
  time_since_session_start: number;
  attempt_number: number;
  difficulty_level: number;
  timestamp: string;
}

export interface GVOption {
  option_id: string;
  payload: Record<string, unknown>;
}

export interface GVItem {
  item_id: string;
  subtest_id: "mental_rotation" | "paper_folding" | "hidden_figures" | "mystery_map";
  subtest_name: string;
  prompt: string;
  difficulty_level: number;
  primary_ability: string;
  secondary_ability: string | null;
  expected_time_seconds: number;
  response_type: "single_choice" | "map_placement";
  practice: boolean;
  stimulus: Record<string, unknown>;
  options: GVOption[];
}

export interface GVStartResponse {
  status: "new" | "resumed" | "completed";
  student_id: string;
  session_id: string;
  module_id: string;
  module_name: string;
  construct: string;
  version: string;
  difficulty: number;
  start_time: string;
  current_item_index: number;
  practice_items: GVItem[];
  assessment_items: GVItem[];
  completed_result: GVFinalResult | null;
}

export interface GVAnswerRequest {
  submission_id: string;
  session_id: string;
  item_id: string;
  response: Record<string, unknown>;
  practice: boolean;
  time_taken_ms: number;
  attempt_number: number;
  selection_changes: number;
  rotation_attempts: number;
  placement_attempts: number;
  time_to_first_interaction_ms: number | null;
  device_metadata: Record<string, unknown>;
  events: GVClientEvent[];
}

export interface GVAnswerResponse {
  accepted: boolean;
  duplicate: boolean;
  practice_feedback: { correct: boolean; message: string } | null;
  next_step: "next_item" | "finish" | "already_completed";
  current_item_index: number;
}

export interface GVMetrics {
  raw_score: number;
  accuracy: number;
  visualization_vz: number | null;
  spatial_relations_sr: number | null;
  visual_closure_cs: number | null;
  flexibility_of_closure_cf: number | null;
  spatial_scanning_ss: number | null;
  visual_memory_mv: number | null;
  mental_rotation_accuracy: number | null;
  paper_folding_accuracy: number | null;
  hidden_figures_accuracy: number | null;
  mystery_map_accuracy: number | null;
  first_attempt_accuracy: number;
  correction_count: number;
  average_response_time: number;
  distractor_selection_rate: number;
  rotation_attempts_total: number;
  mirror_confusion_rate: number | null;
  strategy_error_control: number;
  efficiency_score: number;
  confidence_score: number;
}

export interface GVFinalResult {
  student_id: string;
  session_id: string;
  module_id: string;
  module_name: string;
  construct: string;
  status: "Completed";
  start_time: string;
  end_time: string;
  completion_time: number;
  timestamp: string;
  metrics: GVMetrics;
}

export interface GVResponseState {
  response: Record<string, unknown> | null;
  selectionChanges: number;
  rotationAttempts: number;
  placementAttempts: number;
  timeToFirstInteractionMs: number | null;
}
