import { AssessmentSession, AnswerPayload, ModuleConfig, Question } from "../../types";
import { MODULE_CONFIGS } from "../../config/moduleConfig";
import { QUESTIONS_DATA } from "../../config/questionsData";
import { ProcessingSpeedService } from "../modules/processingSpeed";

const SESSION_STORAGE_KEY = "mentiscope_assessment_session";

export class AssessmentService {
  private static readonly dedicatedModulePages: Record<string, string> = {
    gv: "gv-assessment"
  };

  static getRunnerPage(moduleId: string): string {
    return this.dedicatedModulePages[moduleId] || "assessment";
  }

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
      moduleMetrics: {},
      startTime: new Date().toISOString(),
      status: "ongoing"
    };

    this.saveSession(newSession);
    return newSession;
  }

  static getSessionHistory(studentId: string): AssessmentSession[] {
    const saved = localStorage.getItem("mentiscope_session_history");
    let localHistory: AssessmentSession[] = [];
    if (saved) {
      try {
        localHistory = (JSON.parse(saved) as AssessmentSession[]).filter((s) => s.studentId === studentId);
      } catch {
        localHistory = [];
      }
    }
    
    // Asynchronously fetch from SQLite backend to ensure persistent data recovery
    fetch(`/api/sessions/history?student_id=${encodeURIComponent(studentId)}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && Array.isArray(data.sessions) && data.sessions.length > 0) {
          const merged = [...data.sessions];
          localStorage.setItem("mentiscope_session_history", JSON.stringify(merged));
        }
      })
      .catch(() => {});

    return localHistory;
  }

  static archiveSession(session: AssessmentSession): void {
    if (!session || Object.keys(session.moduleScores).length === 0) return;
    const history = this.getSessionHistory(session.studentId);
    const existingIdx = history.findIndex((s) => s.sessionId === session.sessionId);
    if (existingIdx >= 0) {
      history[existingIdx] = session;
    } else {
      history.unshift(session);
    }
    localStorage.setItem("mentiscope_session_history", JSON.stringify(history));

    // Persist session payload into backend SQLite database (ROM storage)
    fetch("/api/sessions/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(session)
    }).catch(err => console.warn("Backend session archive warning:", err));
  }

  static deleteSessionFromHistory(sessionId: string): void {
    const saved = localStorage.getItem("mentiscope_session_history");
    if (saved) {
      try {
        const history = JSON.parse(saved) as AssessmentSession[];
        const updated = history.filter((s) => s.sessionId !== sessionId);
        localStorage.setItem("mentiscope_session_history", JSON.stringify(updated));
      } catch (e) {
        console.error("Failed to delete session from history:", e);
      }
    }

    // Delete session record from backend SQLite DB
    fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, {
      method: "DELETE"
    }).catch(err => console.warn("Backend session delete warning:", err));
  }

  static createNewSession(studentId: string): AssessmentSession {
    const current = this.getSession();
    if (current && Object.keys(current.moduleScores).length > 0) {
      this.archiveSession(current);
    }

    this.clearSession();
    this.setViewingSession(null);

    const newSession: AssessmentSession = {
      sessionId: `sess_${Math.random().toString(36).substring(2, 11)}`,
      studentId,
      currentModuleIndex: 0,
      currentQuestionIndex: 0,
      answers: {},
      moduleScores: {},
      moduleMetrics: {},
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
    if (session && Object.keys(session.moduleScores).length > 0) {
      this.archiveSession(session);
    }
  }

  static clearSession(): void {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  static setViewingSession(session: AssessmentSession | null): void {
    if (session) {
      localStorage.setItem("mentiscope_viewing_session", JSON.stringify(session));
    } else {
      localStorage.removeItem("mentiscope_viewing_session");
    }
  }

  static getViewingSession(): AssessmentSession | null {
    const saved = localStorage.getItem("mentiscope_viewing_session");
    if (!saved) return null;
    try {
      return JSON.parse(saved) as AssessmentSession;
    } catch {
      return null;
    }
  }

  static async startModule(moduleId: string, sessionId: string, studentId?: string): Promise<{ status: string; totalQuestions: number; questions?: Question[]; question?: Question; seed?: number }> {
    if (moduleId === "processing-speed" || moduleId === "gs") return ProcessingSpeedService.start(sessionId, studentId);
    console.log(`[API Call] POST /api/modules/${moduleId}/start | Session: ${sessionId}`);
    try {
      const res = await fetch(`/api/modules/${moduleId}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, studentId })
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Backend start endpoint fallback:", e);
    }
    
    const questions = QUESTIONS_DATA[moduleId] || [];
    return {
      status: "success",
      totalQuestions: questions.length,
      questions
    };
  }

  static async submitAnswer(
    moduleId: string, 
    sessionId: string, 
    payload: AnswerPayload
  ): Promise<{ status: string; isCorrect: boolean; feedback?: string; nextQuestion?: Question }> {
    if (moduleId === "processing-speed" || moduleId === "gs") return ProcessingSpeedService.answer(sessionId, payload);
    console.log(`[API Call] POST /api/modules/${moduleId}/answer | Session: ${sessionId}`, payload);
    try {
      const res = await fetch(`/api/modules/${moduleId}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId,
          questionId: payload.questionId,
          answer: payload.answer,
          durationMs: payload.durationMs
        })
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Backend answer endpoint fallback:", e);
    }

    const questions = QUESTIONS_DATA[moduleId] || [];
    const question = questions.find(q => q.id === payload.questionId);
    
    const isCorrect = question 
      ? question.correctAnswer?.toLowerCase().trim() === payload.answer.toLowerCase().trim()
      : false;

    return {
      status: "success",
      isCorrect,
      feedback: isCorrect ? "Correct answer!" : `Incorrect. The correct answer was ${question?.correctAnswer || "the target option"}.`
    };
  }

  static async finishModule(
    moduleId: string, 
    sessionId: string, 
    answers: AnswerPayload[],
    seed?: number
  ): Promise<{ status: string; scorePercentage: number; metrics?: any; analytics?: any }> {
    if (moduleId === "processing-speed" || moduleId === "gs") return ProcessingSpeedService.finish(sessionId, answers);
    console.log(`[API Call] POST /api/modules/${moduleId}/finish | Session: ${sessionId} with ${answers.length} answers`);
    try {
      const res = await fetch(`/api/modules/${moduleId}/finish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, answers, seed })
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Backend finish endpoint fallback:", e);
    }

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

  static async getModuleResult(moduleId: string, sessionId: string, studentId?: string): Promise<{ moduleId: string; score: number; metrics?: any }> {
    if (moduleId === "processing-speed") return ProcessingSpeedService.getResult(sessionId);
    console.log(`[API Call] GET /api/modules/${moduleId}/result | Session: ${sessionId}`);
    try {
      let res = await fetch(`/api/modules/${moduleId}/result?session_id=${encodeURIComponent(sessionId)}`);
      if (!res.ok && studentId) {
        res = await fetch(`/api/modules/${moduleId}/result/student/${encodeURIComponent(studentId)}`);
      }
      if (res.ok) {
        const data = await res.json();
        if (data && data.score !== undefined) {
          return {
            moduleId,
            score: data.score,
            metrics: data.metrics
          };
        }
      }
    } catch (e) {
      console.warn("Backend getModuleResult endpoint error, fallback to session:", e);
    }

    const session = this.getSession();
    const score = session?.moduleScores[moduleId] ?? 75;
    const metrics = session?.moduleMetrics?.[moduleId];

    return {
      moduleId,
      score,
      metrics
    };
  }
}
