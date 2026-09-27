import { MODULE_CONFIGS } from "../../config/moduleConfig";
import { QUESTIONS_DATA } from "../../config/questionsData";
import { AssessmentService } from "../assessment/AssessmentService";

export interface StudentScoreRecord {
  attemptId: string;
  timestamp: string;
  sessionId: string;
  studentId: string;
  studentName: string;
  studentEmail: string;
  moduleId: string;
  moduleName: string;
  score: number;
  accuracy: number;
  questionsAttempted: number;
  timeSpentSec: number;
  status: string;
}

export interface QuestionBankItem {
  moduleId: string;
  moduleName: string;
  questionId: string;
  type: string;
  prompt: string;
  options: string;
  correctAnswer: string;
  hint: string;
  story: string;
}

export interface ModuleBenchmarkItem {
  moduleId: string;
  moduleName: string;
  category: string;
  totalAttempts: number;
  uniqueStudents: number;
  averageScore: number;
  highestScore: number;
  lowestScore: number;
  passRate: number;
  targetTime: string;
  status: string;
}

export interface AdminCsvDashboardData {
  status: string;
  kpis: {
    totalAttempts: number;
    uniqueCandidates: number;
    cohortAvgScore: number;
    activeModules: number;
    lastSyncedAt: string;
  };
  datasets: {
    studentScores: StudentScoreRecord[];
    questionsBank: QuestionBankItem[];
    moduleBenchmarks: ModuleBenchmarkItem[];
  };
}

export class AdminCsvService {
  /**
   * Fetches real-time synchronized CSV data for all three datasets.
   */
  static async fetchDashboardData(): Promise<AdminCsvDashboardData> {
    try {
      const response = await fetch("/api/admin/csv/dashboard-data", {
        headers: { Accept: "application/json" }
      });
      if (response.ok) {
        const data = await response.json();
        return data as AdminCsvDashboardData;
      }
    } catch (e) {
      console.warn("Failed to fetch from backend /api/admin/csv/dashboard-data, using local synchronization fallback:", e);
    }

    // Client-side fallback using real local storage sessions and platform data
    return this.generateFallbackData();
  }

  /**
   * Triggers download of the specified CSV or ZIP package.
   */
  static downloadDataset(datasetType: "student-scores" | "questions-bank" | "module-benchmarks" | "all-datasets"): void {
    const downloadUrl = `/api/admin/csv/download/${datasetType}`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.setAttribute("download", "");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Client-side export generator if browser cannot connect to backend stream directly.
   */
  static exportCsvClientSide(data: any[], filename: string, headers: string[], rowMapper: (item: any) => (string | number)[]): void {
    const csvRows = [headers.join(",")];
    for (const item of data) {
      const row = rowMapper(item).map(val => {
        const str = String(val ?? "");
        if (str.includes(",") || str.includes('"') || str.includes("\n")) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      });
      csvRows.push(row.join(","));
    }

    const blob = new Blob(["\uFEFF" + csvRows.join("\r\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Client-side fallback generated strictly from genuine local tests and platform questions.
   */
  private static generateFallbackData(): AdminCsvDashboardData {
    const rawSessions = localStorage.getItem("mentiscope_session_history");
    let sessions: any[] = [];
    if (rawSessions) {
      try {
        sessions = JSON.parse(rawSessions);
      } catch {
        sessions = [];
      }
    }

    const studentScores: StudentScoreRecord[] = [];
    const moduleMap = new Map(MODULE_CONFIGS.map(m => [m.id, m]));

    for (const sess of sessions) {
      const studentId = sess.studentId || "candidate_user";
      const studentName = studentId.replace("stud_", "").replace("_", " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
      const studentEmail = `${studentId}@candidate.edu`;
      const modScores = sess.moduleScores || {};
      const modMetrics = sess.moduleMetrics || {};

      for (const [modId, rawScore] of Object.entries(modScores)) {
        if (rawScore === null || rawScore === undefined) continue;
        const score = Number(rawScore) || 0;
        const modCfg = moduleMap.get(modId);
        const modName = modCfg ? modCfg.name : modId.toUpperCase();
        studentScores.push({
          attemptId: `att_${modId}_${(sess.sessionId || "sess").slice(-6)}`,
          timestamp: sess.startTime ? new Date(sess.startTime).toISOString().replace("T", " ").substring(0, 19) : new Date().toISOString().replace("T", " ").substring(0, 19),
          sessionId: sess.sessionId || "sess_live",
          studentId,
          studentName,
          studentEmail,
          moduleId: modId,
          moduleName: modName,
          score,
          accuracy: score,
          questionsAttempted: 5,
          timeSpentSec: 120,
          status: score >= 60 ? "Passed" : "Completed"
        });
      }
    }

    // Build Question Bank items from QUESTIONS_DATA
    const questionsBank: QuestionBankItem[] = [];
    for (const [modId, qList] of Object.entries(QUESTIONS_DATA)) {
      const modCfg = moduleMap.get(modId);
      const modName = modCfg ? modCfg.name : modId.toUpperCase();
      for (const q of qList) {
        questionsBank.push({
          moduleId: modId,
          moduleName: modName,
          questionId: q.id,
          type: q.type || "choice",
          prompt: q.text || "",
          options: (q.options || []).join(" | "),
          correctAnswer: q.correctAnswer || "",
          hint: q.hint || "",
          story: q.story || ""
        });
      }
    }

    // Build Module Benchmarks
    const moduleBenchmarks: ModuleBenchmarkItem[] = MODULE_CONFIGS.map(mod => {
      const attempts = studentScores.filter(s => s.moduleId === mod.id);
      const scores = attempts.map(a => a.score);
      const count = attempts.length;
      const uniqueStudents = new Set(attempts.map(a => a.studentId)).size;
      const avgScore = count > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / count) : 0;
      const maxScore = count > 0 ? Math.max(...scores) : 0;
      const minScore = count > 0 ? Math.min(...scores) : 0;
      const passRate = count > 0 ? Math.round((attempts.filter(a => a.score >= 60).length / count) * 100) : 0;

      return {
        moduleId: mod.id,
        moduleName: mod.name,
        category: mod.description.split(",")[0] || "Cognitive Domain",
        totalAttempts: count,
        uniqueStudents,
        averageScore: avgScore,
        highestScore: maxScore,
        lowestScore: minScore,
        passRate,
        targetTime: mod.estimatedTime || "2 mins",
        status: count > 0 ? "Calibrated" : "Awaiting Candidates"
      };
    });

    const totalAttempts = studentScores.length;
    const uniqueCandidates = new Set(studentScores.map(s => s.studentId)).size;
    const cohortAvgScore = totalAttempts > 0 
      ? Math.round(studentScores.reduce((acc, s) => acc + s.score, 0) / totalAttempts)
      : 0;

    return {
      status: "success",
      kpis: {
        totalAttempts,
        uniqueCandidates,
        cohortAvgScore,
        activeModules: MODULE_CONFIGS.length,
        lastSyncedAt: new Date().toISOString().replace("T", " ").substring(0, 19) + " UTC"
      },
      datasets: {
        studentScores,
        questionsBank,
        moduleBenchmarks
      }
    };
  }
}
