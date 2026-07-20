import { AssessmentSession, AnswerPayload, ModuleConfig, Question } from "../../types";
import { MODULE_CONFIGS } from "../../config/moduleConfig";
import { QUESTIONS_DATA } from "../../config/questionsData";
import { ProcessingSpeedService } from "../modules/processingSpeed";

const SESSION_STORAGE_KEY = "mentiscope_assessment_session";

export class AssessmentService {
  /**
   * Initialises or retrieves the active assessment session.
   */
  static getOrCreateSession(studentId: string): AssessmentSession {
    const saved = localStorage.getItem(SESSION_STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as AssessmentSession;
        if (parsed.studentId === studentId && parsed.status === "ongoing") {
          return parsed;
        }
      } catch (e) {
        console.error("Failed to parse saved assessment session", e);
      }
    }

    const newSession: AssessmentSession = {
      sessionId: `sess_${Math.random().toString(36).substring(2, 11)}`,
      studentId,
      currentModuleIndex: 0,
      currentQuestionIndex: 0,
      answers: {},
      moduleScores: {},
      startTime: new Date().toISOString(),
      status: "ongoing"
    };

    this.saveSession(newSession);
    return newSession;
  }

  static getSession(): AssessmentSession | null {
    const saved = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!saved) return null;
    try {
      return JSON.parse(saved) as AssessmentSession;
    } catch {
      return null;
    }
  }

  static saveSession(session: AssessmentSession): void {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  }

  static clearSession(): void {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  /**
   * Simulates calling POST /start on the specific module endpoint.
   */
  static async startModule(moduleId: string, sessionId: string, studentId?: string): Promise<{ status: string; totalQuestions: number; question?: Question }> {
    if (moduleId === "processing-speed") return ProcessingSpeedService.start(sessionId, studentId);
    console.log(`[API Call] POST /modules/${moduleId}/start | Session: ${sessionId}`);
    // Simulate minor network delay
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    const questions = QUESTIONS_DATA[moduleId] || [];
    return {
      status: "success",
      totalQuestions: questions.length
    };
  }

  /**
   * Simulates calling POST /answer on the specific module endpoint.
   */
  static async submitAnswer(
    moduleId: string, 
    sessionId: string, 
    payload: AnswerPayload
  ): Promise<{ status: string; isCorrect: boolean; feedback?: string; nextQuestion?: Question }> {
    if (moduleId === "processing-speed") return ProcessingSpeedService.answer(sessionId, payload);
    console.log(`[API Call] POST /modules/${moduleId}/answer | Session: ${sessionId}`, payload);
    await new Promise((resolve) => setTimeout(resolve, 300));

    const questions = QUESTIONS_DATA[moduleId] || [];
    const question = questions.find(q => q.id === payload.questionId);
    
    const isCorrect = question 
      ? question.correctAnswer?.toLowerCase().trim() === payload.answer.toLowerCase().trim()
      : false;

    return {
      status: "success",
      isCorrect,
      feedback: isCorrect ? "Correct answer!" : `Incorrect. The correct answer was: ${question?.correctAnswer}`
    };
  }

  /**
   * Simulates calling POST /finish on the specific module endpoint.
   */
  static async finishModule(
    moduleId: string, 
    sessionId: string, 
    answers: AnswerPayload[]
  ): Promise<{ status: string; scorePercentage: number }> {
    if (moduleId === "processing-speed") return ProcessingSpeedService.finish(sessionId, answers);
    console.log(`[API Call] POST /modules/${moduleId}/finish | Session: ${sessionId} with ${answers.length} answers`);
    await new Promise((resolve) => setTimeout(resolve, 600));

    const questions = QUESTIONS_DATA[moduleId] || [];
    let correctCount = 0;

    answers.forEach(ans => {
      const q = questions.find(item => item.id === ans.questionId);
      if (q && q.correctAnswer?.toLowerCase().trim() === ans.answer.toLowerCase().trim()) {
        correctCount++;
      }
    });

    const scorePercentage = questions.length > 0 ? Math.round((correctCount / questions.length) * 100) : 0;

    return {
      status: "success",
      scorePercentage
    };
  }

  /**
   * Simulates calling GET /result on the specific module endpoint.
   */
  static async getModuleResult(moduleId: string, sessionId: string): Promise<{ moduleId: string; score: number }> {
    if (moduleId === "processing-speed") return ProcessingSpeedService.getResult(sessionId);
    console.log(`[API Call] GET /modules/${moduleId}/result | Session: ${sessionId}`);
    await new Promise((resolve) => setTimeout(resolve, 400));

    const session = this.getSession();
    const score = session?.moduleScores[moduleId] ?? 75; // Default fallback score

    return {
      moduleId,
      score
    };
  }
}
