import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class GSMService {
  static readonly endpoint = "/api/modules/gsm";

  static async start(sessionId: string) {
    return AssessmentService.startModule("gsm", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("gsm", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("gsm", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("gsm", sessionId);
  }
}
