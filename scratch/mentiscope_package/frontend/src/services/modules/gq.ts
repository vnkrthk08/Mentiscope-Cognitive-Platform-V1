import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class GQService {
  static readonly endpoint = "/api/modules/gq";

  static async start(sessionId: string) {
    return AssessmentService.startModule("gq", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("gq", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("gq", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("gq", sessionId);
  }
}
