import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class LanguageService {
  static readonly endpoint = "/api/modules/language";

  static async start(sessionId: string) {
    return AssessmentService.startModule("language", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("language", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("language", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("language", sessionId);
  }
}
