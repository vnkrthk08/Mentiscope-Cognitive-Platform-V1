export enum UserRole {
  STUDENT = "student",
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
  taskName?: string; // Student research task name
  researcher?: string; // Intern researcher attribution
  description: string;
  icon: string; // Lucide icon name
  apiBaseUrl: string;
  estimatedTime: string; // e.g. "5 mins"
  color: string; // Tailwind color class prefix (e.g. "blue", "teal", "amber")
  enabled: boolean;
  externalUrl?: string;
}

export interface Question {
  id: string;
  text: string;
  story?: string;
  image?: string; // Optional image URL or vector description
  options?: string[]; // Multiple choice options
  correctAnswer?: string;
  hint?: string;
  type?: "choice" | "memory-span" | "stroop" | "grid-pattern" | "speed-match" | "svg-matrix";
  // Extra properties for special cognitive tasks
  sequence?: (string | number)[]; // For Working Memory
  targetColor?: string; // For Stroop
  textColor?: string; // For Stroop
  gridSize?: number; // For pattern tests
  activeGridCells?: number[]; // For working memory grid
  
  // For SVG matrix puzzles
  svgContent?: string;
  examples?: { inputSvg: string; outputSvg: string }[];
  svgOptions?: { id: string; svgContent: string }[];
}

export interface AnswerPayload {
  questionId: string;
  answer: string;
  durationMs: number; // For processing speed or analytics
  isCorrect?: boolean;
}

export interface AssessmentSession {
  sessionId: string;
  studentId: string;
  currentModuleIndex: number;
  currentQuestionIndex: number;
  answers: { [moduleId: string]: AnswerPayload[] };
  moduleScores: { [moduleId: string]: number };
  moduleMetrics?: Record<string, any>;
  startTime: string;
  endTime?: string;
  status: "idle" | "ongoing" | "completed";
  seed?: number;
}

export interface StreamRecommendation {
  streamId: "engineering" | "medicine" | "law" | "commerce_arts";
  streamTitle: string;
  tagline: string;
  matchPercentage: number;
  fitLevel: "Exceptional Fit" | "High Alignment" | "Moderate Alignment" | "Exploratory";
  rationale: string;
  primaryDrivers: string[];
  degreePathways: string[];
  targetCareers: string[];
  entranceExams: string[];
  color: string;
}

export interface ExamReadinessTip {
  examName: string;
  stream: string;
  cognitiveStrength: string;
  actionableStrategy: string;
}

export interface InstitutionalVerification {
  institution: string;
  center: string;
  verifiedOn: string;
  verificationCode: string;
  status: "Verified & Immutable";
}

export interface CognitiveReport {
  sessionId: string;
  studentId?: string;
  studentName: string;
  studentAge: number;
  studentGender: string;
  date: string;
  durationMinutes: number;
  overallScore: number; // 0-100 scale
  moduleScores: { [moduleId: string]: number }; // percentage 0-100
  moduleMetrics?: Record<string, any>;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  isAiGenerated?: boolean;
  streamRecommendations?: StreamRecommendation[];
  primaryStream?: StreamRecommendation;
  examReadiness?: ExamReadinessTip[];
  parentTips?: string[];
  institutionalVerification?: InstitutionalVerification;
}


export interface SystemLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  status: "info" | "warning" | "error" | "success";
  details: string;
}
