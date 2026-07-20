import React from "react";
import { User, AssessmentSession } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { AssessmentService } from "../services/assessment/AssessmentService";
import { 
  Play, 
  RotateCcw, 
  FileText, 
  CheckCircle, 
  Circle, 
  User as UserIcon, 
  Calendar, 
  Award, 
  ShieldCheck 
} from "lucide-react";

interface StudentDashboardProps {
  user: User;
  onNavigate: (page: string) => void;
  onStartAssessment: () => void;
}

export default function StudentDashboard({ user, onNavigate, onStartAssessment }: StudentDashboardProps) {
  // Query active session state
  const session = AssessmentService.getSession();
  const isSessionOngoing = session && session.status === "ongoing";
  
  // Calculate module progress
  const totalModules = MODULE_CONFIGS.length;
  const completedCount = session ? Object.keys(session.moduleScores).length : 0;
  const progressPercent = Math.round((completedCount / totalModules) * 100);

  // Simulated previous reports list
  const previousReports = [
    {
      id: "report_94a82",
      date: "May 14, 2026",
      score: 82,
      duration: "21 mins",
      status: "Verified",
      examiner: "Dr. Clara Oswald"
    },
    {
      id: "report_72b31",
      date: "December 08, 2025",
      score: 75,
      duration: "24 mins",
      status: "Archived",
      examiner: "System Gateway"
    }
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 transition-colors duration-300">
      
      {/* 1. Header Welcome Card */}
      <div className="relative overflow-hidden rounded-3xl border border-blue-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 sm:p-8 shadow-sm">
        <div className="absolute right-0 top-0 -mr-16 -mt-16 h-48 w-48 rounded-full bg-blue-50/50 dark:bg-blue-900/10 blur-3xl" />
        
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between relative z-10">
          <div className="space-y-2">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-3xl">
              Welcome back, {user.name}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-xl leading-relaxed">
              You are signed in to the Candidate Cognitive Portal. Complete the sequential assessment capsule to generate your certified psychological profile report.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 shrink-0">
            {isSessionOngoing ? (
              <button
                onClick={onStartAssessment}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all hover:bg-blue-700 hover:shadow shadow-blue-500/20 active:scale-[0.98]"
              >
                <Play className="h-4 w-4 fill-white" />
                <span>Resume Cognitive Assessment</span>
              </button>
            ) : (
              <button
                onClick={onStartAssessment}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all hover:bg-blue-700 hover:shadow shadow-blue-500/20 active:scale-[0.98]"
              >
                <Play className="h-4 w-4 fill-white" />
                <span>Start Baseline Cognitive Test</span>
              </button>
            )}
            
            {session && (
              <button
                onClick={() => {
                  AssessmentService.clearSession();
                  onStartAssessment();
                }}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 text-sm font-medium text-slate-650 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                <RotateCcw className="h-4 w-4" />
                <span>Reset Progress</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Main Content Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        
        {/* Left Side: Demographic Profile & Progress Checklist */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Active Testing Capsule Progress Bar */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4 hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Baseline Assessment Progress</h2>
                <p className="text-xs text-slate-400 dark:text-slate-500">All 7 modules must be cleared sequentially in one testing run.</p>
              </div>
              <span className="text-xs font-mono font-bold text-blue-650 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded-full border border-blue-100 dark:border-blue-900/40">
                {completedCount} / {totalModules} Cleared
              </span>
            </div>

            <div className="relative pt-1">
              <div className="mb-2 flex items-center justify-between text-xs font-bold text-slate-600 dark:text-slate-400">
                <span>Overall Session Progress</span>
                <span>{progressPercent}%</span>
              </div>
              <div className="h-3.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden border border-slate-200/40 dark:border-slate-700/40">
                <div 
                  className="h-full rounded-full bg-blue-600 transition-all duration-500" 
                  style={{ width: `${progressPercent}%` }} 
                />
              </div>
            </div>

            {/* Checklist of 7 modules */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-4 border-t border-slate-100 dark:border-slate-800/80">
              {MODULE_CONFIGS.map((mod, index) => {
                const isCompleted = session && session.moduleScores[mod.id] !== undefined;
                const isCurrent = session && index === session.currentModuleIndex && isSessionOngoing;
                
                return (
                  <div 
                    key={mod.id} 
                    className={`flex items-center justify-between p-3 rounded-xl border text-xs font-semibold transition-colors ${
                      isCompleted 
                        ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-100 dark:border-emerald-900/40 text-slate-800 dark:text-emerald-300"
                        : isCurrent 
                          ? "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 text-blue-900 dark:text-blue-305"
                          : "bg-slate-50/60 dark:bg-slate-900/40 border-slate-100 dark:border-slate-800/80 text-slate-400 dark:text-slate-500"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      {isCompleted ? (
                        <CheckCircle className="h-4.5 w-4.5 text-emerald-500 shrink-0" />
                      ) : (
                        <Circle className="h-4.5 w-4.5 text-slate-350 dark:text-slate-700 shrink-0" />
                      )}
                      <span className="truncate">
                        {index + 1}. {mod.name}
                      </span>
                    </div>

                    <span className="text-[10px] font-mono shrink-0 uppercase tracking-wider">
                      {isCompleted ? "Done" : isCurrent ? "Active" : "Locked"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Demographic Baseline Profile Card */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm hover-lift">
            <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-1.5">
              <UserIcon className="h-4.5 w-4.5 text-slate-550 dark:text-slate-400" />
              <span>Candidate Demographic Profile</span>
            </h2>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 text-xs border-t border-slate-100 dark:border-slate-800 pt-4">
              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Registered Name</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.name}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Email Address</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5 truncate">{user.email}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Candidate Age</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.age || "Not specified"}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Gender Category</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.gender || "Not specified"}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Academic Specialization</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.specialization || "Psychology"}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">Institutional College Type</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.collegeType || "Private"}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">District</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.district || "Chennai"}</p>
              </div>

              <div>
                <p className="font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide text-[10px]">State / Region</p>
                <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{user.state || "Tamil Nadu"}</p>
              </div>
            </div>
          </div>

        </div>

        {/* Right Side: Historical Assessments & Verified Certificates */}
        <div className="lg:col-span-4 space-y-8">
          
          {/* Verified Cognitive Scores History */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4 hover-lift">
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
              <Award className="h-4.5 w-4.5 text-blue-600 dark:text-blue-500" />
              <span>Assessment History</span>
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 leading-normal">
              Download historical diagnostic reports reviewed by accredited lab proctors:
            </p>

            <div className="space-y-3.5 pt-2">
              {previousReports.map((rep) => (
                <div 
                  key={rep.id} 
                  className="rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 p-3.5 space-y-2.5 transition-colors hover:border-slate-200 dark:hover:border-slate-700"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />
                      {rep.date}
                    </span>
                    <span className="font-mono text-[10px] font-bold text-blue-650 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-900/30">
                      ID: {rep.id.split("_")[1]}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-semibold text-slate-650 dark:text-slate-350">
                    <span>Overall Score Index:</span>
                    <span className="text-blue-600 dark:text-blue-450 font-bold">{rep.score}%</span>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-450 dark:text-slate-500">
                    <span>Time: {rep.duration}</span>
                    <span className="truncate max-w-[120px]">Proctor: {rep.examiner}</span>
                  </div>

                  <button
                    onClick={() => {
                      const dummyScores: { [key: string]: number } = {
                        gq: rep.score + 5,
                        gsm: rep.score - 4,
                        gf: rep.score - 10,
                        attention: rep.score + 2,
                        language: rep.score + 6,
                        executive: rep.score - 8,
                        "processing-speed": rep.score
                      };
                      const dummySession: AssessmentSession = {
                        sessionId: rep.id,
                        studentId: user.id,
                        currentModuleIndex: 7,
                        currentQuestionIndex: 0,
                        answers: {},
                        moduleScores: dummyScores,
                        startTime: new Date().toISOString(),
                        status: "completed"
                      };
                      AssessmentService.saveSession(dummySession);
                      onNavigate("report");
                    }}
                    className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                  >
                    <FileText className="h-3.5 w-3.5 text-slate-500 dark:text-slate-400" />
                    <span>Download Report PDF</span>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Secure Institutional Guidelines */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-3 shadow-sm hover-lift">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
              <ShieldCheck className="h-4.5 w-4.5 text-emerald-600 dark:text-emerald-500" />
              <span>Assessment Safe Room</span>
            </h3>
            <p className="text-[11px] text-slate-550 dark:text-slate-450 leading-normal">
              This system tracks screen-focus intervals and active response latencies. Leaving the browser tab or closing the window repeatedly will flag the session as "Interrupted" for review by clinical supervisors.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
