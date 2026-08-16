import { AssessmentService } from "../assessment/AssessmentService";
import { AnswerPayload } from "../../types";

export class ExecutiveService {
  static readonly endpoint = "/api/modules/executive";

  static async start(sessionId: string) {
    return AssessmentService.startModule("executive", sessionId);
  }

  static async answer(sessionId: string, payload: AnswerPayload) {
    return AssessmentService.submitAnswer("executive", sessionId, payload);
  }

  static async finish(sessionId: string, answers: AnswerPayload[]) {
    return AssessmentService.finishModule("executive", sessionId, answers);
  }

  static async getResult(sessionId: string) {
    return AssessmentService.getModuleResult("executive", sessionId);
  }
}
