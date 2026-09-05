import {
  AssessmentLaunchContext,
  GVAnswerRequest,
  GVAnswerResponse,
  GVClientEvent,
  GVFinalResult,
  GVStartResponse,
} from "../../modules/gv/types";
import { mockAnswer, mockFinish, mockResult, mockStart } from "../../modules/gv/mock/gvMockApi";

const API_BASE_URL = ((import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const MOCK_MODE = String((import.meta as any).env?.VITE_MOCK_DEMO_MODE || "false").toLowerCase() === "true";

export class GVApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly retryable: boolean,
  ) {
    super(message);
    this.name = "GVApiError";
  }
}

async function request<T>(path: string, init?: RequestInit, accessToken?: string): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/modules/gv${path}`, { ...init, headers });
  } catch {
    throw new GVApiError("The Visual Processing service could not be reached. Check the backend and try again.", 0, true);
  }
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // Keep the HTTP fallback when the response is not JSON.
    }
    throw new GVApiError(detail, response.status, response.status >= 500 || response.status === 408 || response.status === 429);
  }
  return (await response.json()) as T;
}

export const GVService = {
  isMockMode(): boolean {
    return MOCK_MODE;
  },

  async start(context: AssessmentLaunchContext): Promise<GVStartResponse> {
    const fullContext = {
      student_id: context.student_id || "student_candidate",
      session_id: context.session_id || `sess_${Date.now()}`,
      module_id: "GV_VISUAL_PROCESSING_BATTERY",
      module_name: "Visual Processing Battery",
      construct: "CHC_Gv_Visual_Processing",
      difficulty: context.difficulty || 1,
      ...context
    };
    if (MOCK_MODE) return mockStart(fullContext);
    return request<GVStartResponse>("/start", { method: "POST", body: JSON.stringify(fullContext) }, context.access_token);
  },

  async answer(payload: GVAnswerRequest, accessToken?: string): Promise<GVAnswerResponse> {
    if (MOCK_MODE) return mockAnswer(payload);
    return request<GVAnswerResponse>("/answer", { method: "POST", body: JSON.stringify(payload) }, accessToken);
  },

  async finish(sessionId: string, events: GVClientEvent[], accessToken?: string): Promise<GVFinalResult> {
    if (MOCK_MODE) return mockFinish(sessionId);
    return request<GVFinalResult>("/finish", { method: "POST", body: JSON.stringify({ session_id: sessionId, events }) }, accessToken);
  },

  async result(sessionId: string, accessToken?: string): Promise<GVFinalResult> {
    if (MOCK_MODE) return mockResult(sessionId);
    return request<GVFinalResult>(`/result/${encodeURIComponent(sessionId)}`, { method: "GET" }, accessToken);
  },
};
