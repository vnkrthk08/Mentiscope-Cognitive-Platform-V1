export enum UserRole {
  STUDENT = "student",
  INTERN = "intern",
  SUPER_ADMIN = "super_admin"
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  token?: string;
  // Student registration details
  age?: number;
  gender?: string;
  state?: string;
  district?: string;
  education?: string;
  course?: string;
  specialization?: string;
  previousExamPercentage?: number;
  collegeType?: string;
}

export interface ModuleConfig {
  id: string;
  name: string;
  description: string;
  icon: string; // Lucide icon name
  apiBaseUrl: string;
  estimatedTime: string; // e.g. "5 mins"
  color: string; // Tailwind color class prefix (e.g. "blue", "teal", "amber")
  enabled: boolean;
}

export interface Question {
  id: string;
  text: string;
  story?: string;
  image?: string; // Optional image URL or vector description
  options?: string[]; // Multiple choice options
  correctAnswer?: string;
  hint?: string;
  type?: "choice" | "memory-span" | "stroop" | "grid-pattern" | "speed-match";
  // Extra properties for special cognitive tasks
  sequence?: (string | number)[]; // For Working Memory
  targetColor?: string; // For Stroop
  textColor?: string; // For Stroop
  gridSize?: number; // For pattern tests
  activeGridCells?: number[]; // For working memory grid
}

export interface AnswerPayload {
  questionId: string;
  answer: string;
  durationMs: number; // For processing speed or analytics
}

export interface AssessmentSession {
  sessionId: string;
  studentId: string;
  currentModuleIndex: number;
  currentQuestionIndex: number;
  answers: { [moduleId: string]: AnswerPayload[] };
  moduleScores: { [moduleId: string]: number };
  startTime: string;
  endTime?: string;
  status: "idle" | "ongoing" | "completed";
}

export interface CognitiveReport {
  sessionId: string;
  studentName: string;
  studentAge: number;
  studentGender: string;
  date: string;
  durationMinutes: number;
  overallScore: number; // 0-100 scale
  moduleScores: { [moduleId: string]: number }; // percentage 0-100
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  isAiGenerated?: boolean;
}

export interface Intern {
  id: string;
  name: string;
  email: string;
  assignedModuleId: string; // Can only access this module's config, questions, and analytics
}

export interface SystemLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  status: "info" | "warning" | "error" | "success";
  details: string;
}
