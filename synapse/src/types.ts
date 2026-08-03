export type ScreenId =
  | 'splash'
  | 'intake'
  | 'map'
  | 'gq-assessment'
  | 'neural-core'
  | 'pattern-bot'
  | 'decision-core'
  | 'solver-capacity'
  | 'solver-resource'
  | 'solver-route'
  | 'vision-bot'
  | 'success'
  | 'cognitive-analytics'
  | 'cognitive-profile'
  | 'analytics-core'
  | 'item-exposure'
  | 'admin-control'
  | 'event-logger';

export interface SessionScores {
  rawScore: number;
  normalizedScore: number;
  percentile: number;
  subScores: { [key: string]: number };
  confidenceScore: number;
}

export interface StudentProfile {
  studentId: string;
  fullName: string;
  age: number;
  tier: 'Novice' | 'Adept' | 'Specialist';
  academy: string;
  xp: number;
  level: number;
  role: 'user' | 'admin';
  completedNodes: string[];
  lastSessionScores?: SessionScores;
}

export interface AppEvent {
  id: string;
  timestamp: string;
  screen: ScreenId;
  action: string;
  status: 'SUCCESS' | 'INFO' | 'WARNING' | 'ERROR';
  details: string;
  payload?: any;
}
