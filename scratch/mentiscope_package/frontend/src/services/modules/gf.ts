import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class GFService {
  static readonly endpoint = "/api/modules/gf";

  static async start(sessionId: string) {
    return AssessmentService.startModule("gf", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("gf", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("gf", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("gf", sessionId);
  }
}
