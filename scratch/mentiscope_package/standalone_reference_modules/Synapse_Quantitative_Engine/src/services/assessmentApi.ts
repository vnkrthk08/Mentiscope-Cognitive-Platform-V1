/// <reference types="vite/client" />

export interface BackendQuestion {
  question_id: string;
  template_id: string;
  module: string;
  difficulty: number;
  story: string;
  question: string;
  options: string[];
  hint: string;
  correct_answer?: string;
  data?: any;
}

export interface StartAssessmentResponse {
  assessment_id: string;
  student_id: string;
  session_id: string;
  status: string;
  started_at: string;
  question: BackendQuestion;
}

export interface SubmitAnswerPayload {

  session_id: string;

  question_id: string;

  response: string;

  metrics: {

    reaction_time_ms: number;

    hover_duration_ms: number;

    idle_time_ms: number;

    drag_distance: number;

    answer_changes: number;

    confidence_score: number;

    attempt_number: number;

    difficulty_level: number;

    module_name: string;

    hint_used: boolean;

  };

}

export interface SubmitAnswerResponse {
  correct: boolean;
  next_level: number;
  next_question: BackendQuestion;
}

export interface FinishAssessmentResponse {
  status: string;
  assessment_id: string;
  student_id: string;
  completed_at: string;
}

export interface AssessmentResult {
  student_id: string;
  session_id: string;
  module_name: string;
  construct: string;
  status: string;
  start_time: string;
  end_time: string | null;
  completion_time: number;
  metrics: {
    questions_attempted: number;
    correct: number;
    accuracy: number;
    average_reaction_time: number;
    [key: string]: any;
  };
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function startAssessment(
  studentId: string,
  difficulty: number,
  moduleId: string = 'GQ01',
  construct: string = 'Gq'
): Promise<StartAssessmentResponse> {
  return request<StartAssessmentResponse>('/api/start', {
    method: 'POST',
    body: JSON.stringify({
      student_id: studentId,
      session_id: `gq-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      module_id: moduleId,
      construct,
      difficulty,
    }),
  });
}

export async function submitAnswer(payload: SubmitAnswerPayload): Promise<SubmitAnswerResponse> {
  return request<SubmitAnswerResponse>('/api/answer', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function finishAssessment(sessionId: string): Promise<FinishAssessmentResponse> {
  return request<FinishAssessmentResponse>('/api/finish', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function getResult(assessmentId: string): Promise<AssessmentResult> {
  return request<AssessmentResult>(`/api/result/${assessmentId.trim()}`);
}
