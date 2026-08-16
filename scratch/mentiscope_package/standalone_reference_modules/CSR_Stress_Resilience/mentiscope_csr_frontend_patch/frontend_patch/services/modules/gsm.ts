import { AnswerPayload, Question } from "../../types";

/**
 * Frontend client for the Classroom Scenario Recall (CSR) — Working Memory (Gsm)
 * backend microservice. Mirrors ProcessingSpeedService's pattern: calls the real
 * FastAPI module directly instead of going through AssessmentService's mock branch.
 */
export class GSMService {
  static readonly endpoint = "/api/modules/csr";

  private static async request<T>(path: string, init: RequestInit): Promise<T> {
    const response = await fetch(`${this.endpoint}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init.headers }
    });
    if (!response.ok) throw new Error(`CSR (Gsm) API failed (${response.status})`);
    return response.json() as Promise<T>;
  }

  static async start(sessionId: string, studentId?: string): Promise<{ status: string; totalQuestions: number; question: Question }> {
    return this.request("/start", { method: "POST", body: JSON.stringify({ session_id: sessionId, student_id: studentId }) });
  }

  static async answer(sessionId: string, payload: AnswerPayload): Promise<{ status: string; isCorrect: boolean; feedback?: string; nextQuestion: Question | null }> {
    return this.request(`/answer`, { method: "POST", body: JSON.stringify({ session_id: sessionId, question_id: payload.questionId, answer: payload.answer, duration_ms: payload.durationMs }) });
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return this.request<{ status: string; scorePercentage: number }>(`/finish`, { method: "POST", body: JSON.stringify({ session_id: sessionId, answers }) });
  }

  static async getResult(sessionId: string) {
    return this.request<{ moduleId: string; score: number }>(`/result?session_id=${encodeURIComponent(sessionId)}`, { method: "GET" });
  }
}
