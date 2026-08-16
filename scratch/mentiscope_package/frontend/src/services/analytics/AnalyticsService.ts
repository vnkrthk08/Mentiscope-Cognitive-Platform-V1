import { SystemLog } from "../../types";

export interface DashboardStats {
  totalStudents: number;
  totalInterns: number;
  totalSessions: number;
  completionRate: number; // e.g. 78%
  averageScore: number; // e.g. 74%
  averageDurationMin: number; // e.g. 21.5
}

export class AnalyticsService {
  static getStats(): DashboardStats {
    return {
      totalStudents: 1420,
      totalInterns: 18,
      totalSessions: 3845,
      completionRate: 84.5,
      averageScore: 73.8,
      averageDurationMin: 22.4
    };
  }

  static getCompletionRateData() {
    return [
      { name: "Mon", completed: 42, started: 50 },
      { name: "Tue", completed: 58, started: 65 },
      { name: "Wed", completed: 64, started: 72 },
      { name: "Thu", completed: 55, started: 68 },
      { name: "Fri", completed: 78, started: 90 },
      { name: "Sat", completed: 45, started: 52 },
      { name: "Sun", completed: 30, started: 35 }
    ];
  }

  static getModulePerformanceData() {
    return [
      { subject: "General Cognitive", score: 82, difficulty: 45, avgTimeSec: 210 },
      { subject: "Working Memory", score: 71, difficulty: 68, avgTimeSec: 285 },
      { subject: "Fluid Intelligence", score: 64, difficulty: 82, avgTimeSec: 310 },
      { subject: "Attention Control", score: 78, difficulty: 55, avgTimeSec: 165 },
      { subject: "Linguistic Logic", score: 85, difficulty: 40, avgTimeSec: 195 },
      { subject: "Executive Planning", score: 69, difficulty: 75, avgTimeSec: 290 },
      { subject: "Processing Speed", score: 74, difficulty: 60, avgTimeSec: 150 }
    ];
  }

  static getStateDistributionData() {
    return [
      { name: "California", value: 340 },
      { name: "Texas", value: 280 },
      { name: "New York", value: 220 },
      { name: "Florida", value: 180 },
      { name: "Illinois", value: 140 },
      { name: "Others", value: 260 }
    ];
  }

  static getGenderDistributionData() {
    return [
      { name: "Male", value: 680, percentage: 48 },
      { name: "Female", value: 710, percentage: 50 },
      { name: "Other / Non-binary", value: 30, percentage: 2 }
    ];
  }

  static getAgeDistributionData() {
    return [
      { name: "18-20", value: 420 },
      { name: "21-23", value: 580 },
      { name: "24-26", value: 290 },
      { name: "27-29", value: 90 },
      { name: "30+", value: 40 }
    ];
  }

  static getPerformanceTrendsData() {
    return [
      { month: "Jan", average: 68, activeStudents: 120 },
      { month: "Feb", average: 70, activeStudents: 150 },
      { month: "Mar", average: 71, activeStudents: 210 },
      { month: "Apr", average: 73, activeStudents: 280 },
      { month: "May", average: 72, activeStudents: 310 },
      { month: "Jun", average: 74, activeStudents: 350 }
    ];
  }

  static getRecentSessions() {
    return [
      { id: "sess_x8f19", name: "Sarah Jenkins", age: 22, score: 86, progress: "Completed", date: "July 12, 2026" },
      { id: "sess_a3m22", name: "David Kim", age: 20, score: 74, progress: "Completed", date: "July 12, 2026" },
      { id: "sess_w7c54", name: "Aisha Patel", age: 24, score: 91, progress: "Completed", date: "July 11, 2026" },
      { id: "sess_p2t10", name: "Marcus Brody", age: 19, score: 58, progress: "Completed", date: "July 11, 2026" },
      { id: "sess_n9v83", name: "Emily Watson", age: 25, score: 82, progress: "Completed", date: "July 10, 2026" }
    ];
  }

  static getSystemLogs(): SystemLog[] {
    return [
      {
        id: "log_1",
        timestamp: "2026-07-13 11:04:12",
        user: "System Daemon",
        action: "Hourly Database Backup",
        status: "success",
        details: "Automated incremental backup successfully verified (24.8MB compressed)"
      },
      {
        id: "log_2",
        timestamp: "2026-07-13 10:52:01",
        user: "clara@mentiscope.org",
        action: "Modified Attention Question",
        status: "info",
        details: "Updated task 'attn-2' Stroop font hex values from #00FF00 to #14B8A6"
      },
      {
        id: "log_3",
        timestamp: "2026-07-13 10:15:30",
        user: "System Firewall",
        action: "Blocked Origin Attempt",
        status: "warning",
        details: "Suppressed CORS request from unauthorised domain origin (192.168.1.104)"
      },
      {
        id: "log_4",
        timestamp: "2026-07-13 09:42:15",
        user: "admin@mentiscope.org",
        action: "Created New Intern Account",
        status: "success",
        details: "Provisioned intern ID 'intern_clara' assigned specifically to 'Attention & Control' module"
      },
      {
        id: "log_5",
        timestamp: "2026-07-13 08:12:00",
        user: "System Engine",
        action: "FastAPI Gateway Check",
        status: "success",
        details: "All seven assessment REST endpoints pinged and returned status code 200 (OK)"
      }
    ];
  }
}
