import {
  AssessmentLaunchContext,
  GVAnswerRequest,
  GVAnswerResponse,
  GVFinalResult,
  GVItem,
  GVStartResponse,
} from "../types";

const mockSessions = new Map<string, { context: AssessmentLaunchContext; started: string; answered: Set<string> }>();

const shape = { cells: [[0, 0], [1, 0], [0, 1], [0, 2]], notch: [1, 0], color: "#0d9488" };
const targetSegments = [[[10, 80], [40, 20]], [[40, 20], [70, 80]], [[25, 55], [55, 55]]];
const complexSegments = [
  [[5, 10], [95, 90]], [[5, 90], [95, 15]], [[10, 50], [90, 50]],
  [[50, 5], [50, 95]], ...targetSegments,
];

function choiceItem(
  itemId: string,
  subtestId: GVItem["subtest_id"],
  subtestName: string,
  practice: boolean,
  responseTypeData: Pick<GVItem, "stimulus" | "options">,
): GVItem {
  return {
    item_id: itemId,
    subtest_id: subtestId,
    subtest_name: subtestName,
    prompt: practice ? "Practice this visual relationship before the scored items begin." : "Select the option that best completes the visual task.",
    difficulty_level: practice ? 1 : 2,
    primary_ability: subtestId === "mental_rotation" ? "SR" : subtestId === "paper_folding" ? "Vz" : "CF",
    secondary_ability: "SS",
    expected_time_seconds: 35,
    response_type: "single_choice",
    practice,
    ...responseTypeData,
  };
}

function mapItem(itemId: string, practice: boolean): GVItem {
  const map = [
    ["grass", "road", "water", "water"],
    ["park", "road", "grass", "building"],
    ["sand", "road", "grass", "park"],
    ["sand", "road", "building", "park"],
  ];
  const pieces = [0, 1, 2, 3].map((slot) => ({
    piece_id: `${itemId}_P${slot + 1}`,
    cells: [[map[Math.floor(slot / 2) * 2][(slot % 2) * 2], map[Math.floor(slot / 2) * 2][(slot % 2) * 2 + 1]], [map[Math.floor(slot / 2) * 2 + 1][(slot % 2) * 2], map[Math.floor(slot / 2) * 2 + 1][(slot % 2) * 2 + 1]]],
    glyphs: [[null, null], [null, null]],
    initial_rotation: slot * 90,
  }));
  return {
    item_id: itemId,
    subtest_id: "mystery_map",
    subtest_name: "Mystery Map Builder",
    prompt: "Study the map, then rebuild it using all four pieces.",
    difficulty_level: practice ? 1 : 2,
    primary_ability: "CS",
    secondary_ability: "SR,Vz,CF,SS",
    expected_time_seconds: 75,
    response_type: "map_placement",
    practice,
    stimulus: { map, glyphs: map.map((row) => row.map(() => null)), cols: 2, rows: 2, piece_size: 2, study_seconds: 5, pieces },
    options: [],
  };
}

function items(practice: boolean): GVItem[] {
  const suffix = practice ? "PRACTICE" : "DEMO";
  return [
    choiceItem(`GV_MR_${suffix}`, "mental_rotation", "Mental Rotation", practice, {
      stimulus: { shape, rotation: 0, mirror: false },
      options: [0, 90, 180, 270].slice(0, practice ? 3 : 4).map((rotation, index) => ({ option_id: `MOCK_MR_${index + 1}`, payload: { shape, rotation, mirror: index === 2 } })),
    }),
    choiceItem(`GV_PF_${suffix}`, "paper_folding", "Paper Folding", practice, {
      stimulus: { folds: [{ axis: "vertical", direction: "right" }], punched: [[0, 1]], grid_size: 4 },
      options: [
        { option_id: "MOCK_PF_1", payload: { holes: [[0, 1], [3, 1]] } },
        { option_id: "MOCK_PF_2", payload: { holes: [[0, 1]] } },
        { option_id: "MOCK_PF_3", payload: { holes: [[0, 2], [3, 2]] } },
      ],
    }),
    choiceItem(`GV_HF_${suffix}`, "hidden_figures", "Hidden Figures", practice, {
      stimulus: { target_segments: targetSegments },
      options: [0, 1, 2].map((index) => ({ option_id: `MOCK_HF_${index + 1}`, payload: { segments: index === 1 ? complexSegments : complexSegments.slice(0, 5) } })),
    }),
    mapItem(`GV_MM_${suffix}`, practice),
  ];
}

export async function mockStart(context: AssessmentLaunchContext): Promise<GVStartResponse> {
  let session = mockSessions.get(context.session_id);
  if (!session) {
    session = { context, started: new Date().toISOString(), answered: new Set() };
    mockSessions.set(context.session_id, session);
  }
  return {
    status: session.answered.size ? "resumed" : "new",
    student_id: context.student_id,
    session_id: context.session_id,
    module_id: context.module_id,
    module_name: context.module_name,
    construct: context.construct,
    version: "1.0.0-demo",
    difficulty: context.difficulty,
    start_time: session.started,
    current_item_index: Math.min(session.answered.size, 4),
    practice_items: items(true),
    assessment_items: items(false),
    completed_result: null,
  };
}

export async function mockAnswer(request: GVAnswerRequest): Promise<GVAnswerResponse> {
  const session = mockSessions.get(request.session_id);
  if (!session) throw new Error("Demo session not found. Restart the assessment.");
  const duplicate = session.answered.has(`${request.practice}:${request.item_id}`);
  session.answered.add(`${request.practice}:${request.item_id}`);
  return {
    accepted: true,
    duplicate,
    practice_feedback: request.practice ? { correct: true, message: "Practice response recorded. This feedback is for demonstration only." } : null,
    next_step: "next_item",
    current_item_index: session.answered.size,
  };
}

export async function mockFinish(sessionId: string): Promise<GVFinalResult> {
  const session = mockSessions.get(sessionId);
  if (!session) throw new Error("Demo session not found. Restart the assessment.");
  const end = new Date();
  const completed = [...session.answered].filter((key) => key.startsWith("false:")).length;
  const demonstrationScore = Math.min(100, 55 + completed * 8);
  return {
    student_id: session.context.student_id,
    session_id: sessionId,
    module_id: session.context.module_id,
    module_name: session.context.module_name,
    construct: session.context.construct,
    status: "Completed",
    start_time: session.started,
    end_time: end.toISOString(),
    completion_time: Math.max(0, (end.getTime() - new Date(session.started).getTime()) / 1000),
    timestamp: end.toISOString(),
    metrics: {
      raw_score: demonstrationScore,
      accuracy: demonstrationScore,
      visualization_vz: demonstrationScore,
      spatial_relations_sr: demonstrationScore,
      visual_closure_cs: demonstrationScore,
      flexibility_of_closure_cf: demonstrationScore,
      spatial_scanning_ss: demonstrationScore,
      visual_memory_mv: null,
      mental_rotation_accuracy: demonstrationScore,
      paper_folding_accuracy: demonstrationScore,
      hidden_figures_accuracy: demonstrationScore,
      mystery_map_accuracy: demonstrationScore,
      first_attempt_accuracy: demonstrationScore,
      correction_count: 0,
      average_response_time: 0,
      distractor_selection_rate: 0,
      rotation_attempts_total: 0,
      mirror_confusion_rate: null,
      strategy_error_control: demonstrationScore,
      efficiency_score: demonstrationScore,
      confidence_score: 50,
    },
  };
}

export async function mockResult(sessionId: string): Promise<GVFinalResult> {
  return mockFinish(sessionId);
}
