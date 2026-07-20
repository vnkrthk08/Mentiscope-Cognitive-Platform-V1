import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class AttentionService {
  static readonly endpoint = "/api/modules/attention";

  static async start(sessionId: string) {
    return AssessmentService.startModule("attention", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("attention", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("attention", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("attention", sessionId);
  }
}
