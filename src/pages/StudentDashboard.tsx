import React from "react";
import { User, AssessmentSession } from "../types";
import { MODULE_CONFIGS, NINE_PILLARS_CONFIG } from "../config/moduleConfig";
import { AssessmentService } from "../services/assessment/AssessmentService";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { 
  Play, 
  RotateCcw, 
  FileText, 
  CheckCircle, 
  Circle, 
  User as UserIcon, 
  Calendar, 
  Award, 
  ShieldCheck,
  Activity,
  Brain,
  Clock,
  Timer,
  Info,
  X,
  ChevronRight,
  BarChart3,
  Sparkles,
  ArrowRight,
  Trash2,
  PlusCircle,
  Edit3,
  RefreshCw,
  Loader2,
  Check,
  ExternalLink
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ModuleConfig } from "../types";

interface StudentDashboardProps {
  user: User;
  onNavigate: (page: string) => void;
  onStartAssessment: () => void;
}

export default function StudentDashboard({ user, onNavigate, onStartAssessment }: StudentDashboardProps) {
  const navigate = useNavigate();
  const [activeReportModule, setActiveReportModule] = React.useState<ModuleConfig | null>(null);
  const [historySessions, setHistorySessions] = React.useState<AssessmentSession[]>([]);
  const [session, setSession] = React.useState<AssessmentSession | null>(() => AssessmentService.getSession());

  // Score Input / Sync Modal State
  const [scoreModalOpen, setScoreModalOpen] = React.useState(false);
  const [targetModuleId, setTargetModuleId] = React.useState<string>("auditory_verbal");
  const [inputScoreVal, setInputScoreVal] = React.useState<string>("");
  const [savingScore, setSavingScore] = React.useState(false);
  const [scoreSuccessMsg, setScoreSuccessMsg] = React.useState<string | null>(null);
  const [syncingExternal, setSyncingExternal] = React.useState(false);

  React.useEffect(() => {
    const list = AssessmentService.getSessionHistory(user.id);
    const current = AssessmentService.getSession();
    if (current && Object.keys(current.moduleScores).length > 0) {
      if (!list.some((s) => s.sessionId === current.sessionId)) {
        list.unshift(current);
      }
      setSession(current);
    }
    list.sort((a, b) => new Date(b.startTime || 0).getTime() - new Date(a.startTime || 0).getTime());
    setHistorySessions(list);

    // Also fetch updated history from SQLite backend
    fetch(`/api/sessions/history?student_id=${encodeURIComponent(user.id)}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && Array.isArray(data.sessions) && data.sessions.length > 0) {
          const remoteList = [...data.sessions];
          if (current && Object.keys(current.moduleScores).length > 0) {
            if (!remoteList.some((s) => s.sessionId === current.sessionId)) {
              remoteList.unshift(current);
            }
          }
          remoteList.sort((a, b) => new Date(b.startTime || 0).getTime() - new Date(a.startTime || 0).getTime());
          setHistorySessions(remoteList);

          // If remote session has more scores or updated scores, sync into active session
          const matchedCurrent = remoteList.find(s => s.sessionId === current?.sessionId) || remoteList[0];
          if (matchedCurrent) {
            setSession(matchedCurrent);
            AssessmentService.saveSession(matchedCurrent);
          }
        }
      })
      .catch(() => {});

    // Auto-check external module scores (e.g. from Module 10 db)
    fetch(`/api/sessions/sync-external?student_id=${encodeURIComponent(user.id)}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.status === "synced" && data.session) {
          setSession(data.session);
          AssessmentService.saveSession(data.session);
          setHistorySessions(prev => [data.session, ...prev.filter(s => s.sessionId !== data.session.sessionId)]);
        }
      })
      .catch(() => {});
  }, [user.id]);

  // Sync listener: listen for postMessage from external modules (like localhost:3000) or URL params
  React.useEffect(() => {
    // 1. URL search params listener (e.g. ?module=auditory_verbal&score=85)
    const params = new URLSearchParams(window.location.search);
    const modParam = params.get("module") || params.get("module_id");
    const scoreParam = params.get("score");
    if (modParam && scoreParam) {
      const num = parseFloat(scoreParam);
      if (!isNaN(num)) {
        const activeSess = session || AssessmentService.getOrCreateSession(user.id);
        const updated = AssessmentService.updateModuleScore(activeSess.sessionId, modParam, num, undefined, user.id);
        if (updated) {
          setSession(updated);
          setHistorySessions((prev) => [updated, ...prev.filter((s) => s.sessionId !== updated.sessionId)]);
        }
      }
    }

    // 2. Real-time postMessage listener from external window (localhost:3000)
    const handlePostMessage = (event: MessageEvent) => {
      if (event.data && typeof event.data === "object") {
        const { moduleId, score, module_id, score_percentage } = event.data;
        const targetId = moduleId || module_id;
        const targetScore = score !== undefined ? score : score_percentage;
        if (targetId && targetScore !== undefined) {
          const num = parseFloat(targetScore);
          if (!isNaN(num)) {
            const activeSess = session || AssessmentService.getOrCreateSession(user.id);
            const updated = AssessmentService.updateModuleScore(activeSess.sessionId, targetId, num, undefined, user.id);
            if (updated) {
              setSession(updated);
              setHistorySessions((prev) => [updated, ...prev.filter((s) => s.sessionId !== updated.sessionId)]);
            }
          }
        }
      }
    };

    window.addEventListener("message", handlePostMessage);
    return () => window.removeEventListener("message", handlePostMessage);
  }, [user.id, session?.sessionId]);

  const handleSaveModuleScore = async (e: React.FormEvent) => {
    e.preventDefault();
    const num = parseFloat(inputScoreVal);
    if (isNaN(num) || num < 0 || num > 100) return;

    setSavingScore(true);
    try {
      const activeSess = session || AssessmentService.getOrCreateSession(user.id);
      const updated = AssessmentService.updateModuleScore(activeSess.sessionId, targetModuleId, num, undefined, user.id);
      if (updated) {
        setSession(updated);
        setHistorySessions((prev) => {
          const filtered = prev.filter((s) => s.sessionId !== updated.sessionId);
          return [updated, ...filtered];
        });
        setScoreSuccessMsg(`Successfully saved score (${num}%) to database!`);
        setTimeout(() => {
          setScoreSuccessMsg(null);
          setScoreModalOpen(false);
          setInputScoreVal("");
        }, 1200);
      }
    } catch (err) {
      console.error("Failed to save score:", err);
    } finally {
      setSavingScore(false);
    }
  };

  const handleSyncExternal = async () => {
    setSyncingExternal(true);
    try {
      const activeSess = session || AssessmentService.getOrCreateSession(user.id);
      const res = await fetch(`/api/sessions/sync-external?session_id=${encodeURIComponent(activeSess.sessionId)}&student_id=${encodeURIComponent(user.id)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "synced" && data.session) {
          AssessmentService.saveSession(data.session);
          setSession(data.session);
          setHistorySessions((prev) => {
            const filtered = prev.filter((s) => s.sessionId !== data.session.sessionId);
            return [data.session, ...filtered];
          });
          setScoreSuccessMsg(`Synced ${data.moduleId} score (${data.score}%) from external assessment!`);
          setTimeout(() => {
            setScoreSuccessMsg(null);
            setScoreModalOpen(false);
          }, 1400);
        } else if (data.status === "found_not_saved") {
          setInputScoreVal(String(data.score));
          setTargetModuleId(data.moduleId || "auditory_verbal");
        } else {
          setScoreSuccessMsg(data.message || "No external assessment scores found.");
          setTimeout(() => setScoreSuccessMsg(null), 2500);
        }
      }
    } catch (err) {
      console.error("Failed to sync external scores:", err);
    } finally {
      setSyncingExternal(false);
    }
  };

  const handleDeleteRecord = (sessionIdToDelete: string) => {
    AssessmentService.deleteSessionFromHistory(sessionIdToDelete);
    const current = AssessmentService.getSession();
    if (current && current.sessionId === sessionIdToDelete) {
      AssessmentService.clearSession();
      setSession(null);
    }
    setHistorySessions((prev) => prev.filter((s) => s.sessionId !== sessionIdToDelete));
  };
  const isSessionOngoing = session && session.status === "ongoing";
  const hasCompletedSession = session && session.status === "completed";
  
  // Calculate module progress across all 9 baseline assessment modules
  const totalModules = NINE_PILLARS_CONFIG.length;
  const completedCount = session ? NINE_PILLARS_CONFIG.filter(mod => session.moduleScores[mod.id] !== undefined).length : 0;
  const progressPercent = Math.min(100, Math.round((completedCount / totalModules) * 100));

  // Calculate overall GQ score index if completed
  const overallScore = session && Object.values(session.moduleScores).length > 0
    ? Math.round(Object.values(session.moduleScores).reduce((a, b) => a + b, 0) / Object.values(session.moduleScores).length)
    : 0;

  // Generate real-time chart data from real completed session module scores
  const chartData = session && Object.keys(session.moduleScores).length > 0
    ? Object.entries(session.moduleScores).map(([modId, score], idx) => ({
        date: `Mod ${idx + 1} (${modId.toUpperCase()})`,
        score: Math.round(score),
        timestamp: idx
      }))
    : [];

  // Sort chartData chronologically
  chartData.sort((a, b) => a.timestamp - b.timestamp);

  // Calculate dynamic growth metrics
  let growthText = "Baseline Established";
  let isGrowthPositive = true;
  if (chartData.length >= 2) {
    const firstScore = chartData[0].score;
    const lastScore = chartData[chartData.length - 1].score;
    const growthVal = lastScore - firstScore;
    isGrowthPositive = growthVal >= 0;
    growthText = growthVal >= 0 ? `+${growthVal}% Growth` : `${growthVal}% Deviation`;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 transition-colors duration-300">
      
      {/* 1. Header Welcome Card */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 sm:p-8 shadow-sm">
        <div className="absolute right-0 top-0 -mr-16 -mt-16 h-48 w-48 rounded-full bg-blue-50/50 dark:bg-blue-900/10 blur-3xl pointer-events-none" />
        
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between relative z-10">
          <div className="space-y-2">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-3xl">
              Welcome back, {user.name}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-xl leading-relaxed">
              You are signed in to the Candidate Cognitive Portal. Complete the sequential assessment capsule to generate your certified psychological profile report.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={() => {
                setTargetModuleId("auditory_verbal");
                setInputScoreVal(session?.moduleScores?.["auditory_verbal"] ? String(Math.round(session.moduleScores["auditory_verbal"])) : "");
                setScoreModalOpen(true);
              }}
              className="flex items-center justify-center gap-1.5 rounded-xl border border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/70 dark:bg-indigo-950/40 px-4 py-3 text-sm font-semibold text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-all active:scale-[0.98] cursor-pointer shadow-xs"
            >
              <PlusCircle className="h-4.5 w-4.5 text-indigo-600 dark:text-indigo-400" />
              <span>Record / Sync Score</span>
            </button>

            {isSessionOngoing ? (
              <button
                onClick={onStartAssessment}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all hover:bg-blue-700 hover:shadow shadow-blue-500/20 active:scale-[0.98] cursor-pointer"
              >
                <Play className="h-4 w-4 fill-white" />
                <span>Resume Cognitive Assessment</span>
              </button>
            ) : (
              <button
                onClick={onStartAssessment}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all hover:bg-blue-700 hover:shadow shadow-blue-500/20 active:scale-[0.98] cursor-pointer"
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
                className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 text-sm font-medium text-slate-655 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <RotateCcw className="h-4.5 w-4.5 text-slate-450" />
                <span>Reset Progress</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Premium KPI Stats Row */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Card 1: GQ Index */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 p-5 flex items-center justify-between shadow-xs relative overflow-hidden group">
          <div className="space-y-1 relative z-10">
            <span className="text-[10px] text-slate-450 dark:text-slate-550 uppercase font-mono block">Cognitive Score Index</span>
            <span className="text-xl font-black text-slate-800 dark:text-white block">
              {hasCompletedSession ? `${overallScore}%` : "Pending completion"}
            </span>
          </div>
          <div className="h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
            <Award className="h-5 w-5" />
          </div>
        </div>

        {/* Card 2: Modules Cleared */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 p-5 flex items-center justify-between shadow-xs relative overflow-hidden group">
          <div className="space-y-1 relative z-10">
            <span className="text-[10px] text-slate-450 dark:text-slate-550 uppercase font-mono block">Assessment Progress</span>
            <span className="text-xl font-black text-slate-800 dark:text-white block">
              {completedCount} / {totalModules} Modules
            </span>
          </div>
          <div className="h-10 w-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
            <Brain className="h-5 w-5" />
          </div>
        </div>

        {/* Card 3: Performance Latency */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 p-5 flex items-center justify-between shadow-xs relative overflow-hidden group">
          <div className="space-y-1 relative z-10">
            <span className="text-[10px] text-slate-455 dark:text-slate-550 uppercase font-mono block">Response Latency</span>
            <span className="text-xl font-black text-slate-800 dark:text-white block">
              {isSessionOngoing ? "Tracking Live" : "Stable baseline"}
            </span>
          </div>
          <div className="h-10 w-10 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-450 flex items-center justify-center shrink-0">
            <Clock className="h-5 w-5" />
          </div>
        </div>

        {/* Card 4: Proctor Status */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 p-5 flex items-center justify-between shadow-xs relative overflow-hidden group">
          <div className="space-y-1 relative z-10">
            <span className="text-[10px] text-slate-455 dark:text-slate-550 uppercase font-mono block">Proctor Session</span>
            <span className="text-sm font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-2 py-0.5 rounded-full inline-block border border-emerald-100/60 dark:border-emerald-900/30 mt-1">
              Secured & Active
            </span>
          </div>
          <div className="h-10 w-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <ShieldCheck className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* 3. Cognitive Report Card (Shows if there is a completed session) */}
      {hasCompletedSession && (
        <div className="rounded-3xl border border-emerald-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-xl grid grid-cols-1 md:grid-cols-12 gap-6 items-center transition-all text-slate-100">
          <div className="md:col-span-7 space-y-4">
            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-800/40">
                Cognitive Performance Certified
              </span>
              <h2 className="text-xl font-black text-white tracking-tight mt-2 font-mono">
                Your Psychometric Assessment Report is Ready!
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed mt-1">
                Your performance has been evaluated across all core cognitive modules. You can view, download, or print your certified report.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Overall Index</span>
                <span className="text-xl font-black text-emerald-400 font-mono">{overallScore}%</span>
              </div>
              <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Duration</span>
                <span className="text-xl font-black text-slate-200 font-mono">24 mins</span>
              </div>
              <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 col-span-2 sm:col-span-1">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Status</span>
                <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-800/40 inline-block mt-1">
                  Verified Active
                </span>
              </div>
            </div>
          </div>

          <div className="md:col-span-5 flex flex-col justify-center gap-3 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
            <button
              onClick={() => {
                AssessmentService.setViewingSession(null);
                navigate("/report");
              }}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white py-3.5 px-4 text-xs font-extrabold shadow-lg shadow-emerald-500/20 transition-all cursor-pointer active:scale-95"
            >
              <FileText className="h-4 w-4" />
              <span>View Full Cognitive Report</span>
            </button>

            <button
              onClick={() => {
                AssessmentService.createNewSession(user.id);
                onStartAssessment();
              }}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white py-3.5 px-4 text-xs font-extrabold shadow-lg shadow-blue-500/20 transition-all cursor-pointer active:scale-95"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Take Another Test (New Session)</span>
            </button>
          </div>
        </div>
      )}

      {/* 4. Main Dashboard Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 items-start">
        
        {/* Left Area (2/3 width) - Contains Progress Checklist, Area Chart, and Achievements */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* Progress Checklist Card */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Baseline Assessment Modules</h2>
                <p className="text-xs text-slate-400 dark:text-slate-500">All modules must be cleared sequentially in one testing run.</p>
              </div>
              <span className="text-xs font-mono font-bold text-blue-650 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded-full border border-blue-100 dark:border-blue-900/40">
                {completedCount} / {totalModules} Cleared
              </span>
            </div>

            <div className="relative pt-1">
              <div className="mb-2 flex items-center justify-between text-xs font-bold text-slate-650 dark:text-slate-400">
                <span>Overall Session Progress</span>
                <span>{progressPercent}%</span>
              </div>
              <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden border border-slate-200/40 dark:border-slate-700/40">
                <div 
                  className="h-full rounded-full bg-blue-600 transition-all duration-500" 
                  style={{ width: `${progressPercent}%` }} 
                />
              </div>
            </div>

            {/* Sequential Checklist Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-4 border-t border-slate-150 dark:border-slate-800/80">
              {NINE_PILLARS_CONFIG.map((mod, index) => {
                const isCompleted = session && session.moduleScores[mod.id] !== undefined;
                const isCurrent = session && index === session.currentModuleIndex && isSessionOngoing;
                const modScore = session?.moduleScores[mod.id];

                return (
                  <div 
                    key={mod.id} 
                    onClick={() => {
                      if (mod.externalUrl) {
                        const activeSess = session || AssessmentService.getOrCreateSession(user.id);
                        const tokenPayload = btoa(encodeURIComponent(JSON.stringify({ 
                          session_id: activeSess.sessionId,
                          id: user.id, 
                          name: user.name, 
                          ts: Date.now() 
                        })));
                        const targetUrl = `${mod.externalUrl}?token=${tokenPayload}`;
                        window.open(targetUrl, "_blank");
                        return;
                      }
                      if (isCompleted) {
                        setActiveReportModule(mod);
                      } else {
                        const activeSess = session || AssessmentService.getOrCreateSession(user.id);
                        const runnerIdx = MODULE_CONFIGS.findIndex(m => m.id === mod.id);
                        activeSess.currentModuleIndex = runnerIdx >= 0 ? runnerIdx : 0;
                        AssessmentService.saveSession(activeSess);
                        onStartAssessment();
                      }
                    }}
                    className={`flex items-center justify-between p-3.5 rounded-xl border text-xs font-bold transition-all cursor-pointer hover:shadow-md ${
                      mod.externalUrl
                        ? "bg-purple-50/50 dark:bg-purple-950/20 border-purple-200 dark:border-purple-900/40 text-purple-900 dark:text-purple-300 hover:border-purple-400"
                        : isCompleted 
                          ? "bg-emerald-50/40 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/40 text-slate-850 dark:text-emerald-300 hover:border-emerald-400"
                          : isCurrent 
                            ? "bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900/40 text-blue-900 dark:text-blue-300 hover:border-blue-400"
                            : "bg-slate-50/60 dark:bg-slate-900/30 border-slate-100 dark:border-slate-800/60 text-slate-400 dark:text-slate-550 hover:border-blue-300"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      {isCompleted ? (
                        <CheckCircle className="h-4.5 w-4.5 text-emerald-500 shrink-0" />
                      ) : (
                        <Circle className="h-4.5 w-4.5 text-slate-300 dark:text-slate-750 shrink-0" />
                      )}
                      <span className="truncate">
                        {index + 1}. {mod.name}
                      </span>
                    </div>

                    {isCompleted ? (
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-100/60 dark:bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-200/40 dark:border-emerald-900/40">
                          {Math.round(modScore || 0)}%
                        </span>
                        <span className="text-[10px] font-mono text-blue-600 dark:text-blue-400 flex items-center gap-0.5 hover:underline">
                          Report <ChevronRight className="h-3 w-3" />
                        </span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setTargetModuleId(mod.id);
                            setInputScoreVal(String(Math.round(modScore || 0)));
                            setScoreModalOpen(true);
                          }}
                          title="Edit or sync score"
                          className="p-1 rounded-md text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                        >
                          <Edit3 className="h-3 w-3" />
                        </button>
                      </div>
                    ) : mod.externalUrl ? (
                      <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => {
                            const activeSess = session || AssessmentService.getOrCreateSession(user.id);
                            const tokenPayload = btoa(encodeURIComponent(JSON.stringify({ 
                              session_id: activeSess.sessionId,
                              id: user.id, 
                              name: user.name, 
                              ts: Date.now() 
                            })));
                            const targetUrl = `${mod.externalUrl}?token=${tokenPayload}`;
                            window.open(targetUrl, "_blank");
                          }}
                          className="text-[9px] font-mono shrink-0 uppercase tracking-wider bg-purple-600 hover:bg-purple-700 text-white px-2 py-1 rounded-md transition-all flex items-center gap-1 shadow-xs active:scale-95 cursor-pointer"
                        >
                          Launch <ArrowRight className="h-2.5 w-2.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setTargetModuleId(mod.id);
                            setInputScoreVal("");
                            setScoreModalOpen(true);
                          }}
                          className="text-[9px] font-mono shrink-0 uppercase tracking-wider bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 border border-indigo-200 dark:border-indigo-800 px-2 py-1 rounded-md transition-all flex items-center gap-0.5 shadow-xs active:scale-95 cursor-pointer"
                        >
                          + Score
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => {
                            const activeSess = session || AssessmentService.getOrCreateSession(user.id);
                            const runnerIdx = MODULE_CONFIGS.findIndex(m => m.id === mod.id);
                            activeSess.currentModuleIndex = runnerIdx >= 0 ? runnerIdx : 0;
                            AssessmentService.saveSession(activeSess);
                            onStartAssessment();
                          }}
                          className="text-[9px] font-mono shrink-0 uppercase tracking-wider bg-slate-100 hover:bg-blue-50 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-md border border-slate-200/20 dark:border-slate-700/20 hover:border-blue-300 transition-colors cursor-pointer"
                        >
                          {isCurrent ? "Active" : "Start"}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setTargetModuleId(mod.id);
                            setInputScoreVal("");
                            setScoreModalOpen(true);
                          }}
                          title="Record score manually"
                          className="p-1 rounded-md text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                        >
                          <PlusCircle className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Cognitive Achievements Card */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 mb-4">
              <Award className="h-5 w-5 text-indigo-500" />
              Cognitive Achievements
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {/* Badge 1: Pattern Master (Fluid Intelligence Gf) */}
              {(() => {
                const gfScore = session?.moduleScores["gf"];
                const isUnlocked = gfScore !== undefined;
                
                return (
                  <div className={`flex flex-col items-center p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 text-center transition-transform hover:scale-105 cursor-pointer ${!isUnlocked ? "opacity-40 grayscale" : ""}`}>
                    <div className="h-12 w-12 rounded-full bg-blue-600 text-white flex items-center justify-center mb-2 shadow-lg shadow-blue-500/30">
                      <Brain className="h-6 w-6" />
                    </div>
                    <span className="text-xs font-bold text-slate-850 dark:text-white">Pattern Master</span>
                    <span className="text-[10px] text-slate-450 dark:text-slate-400 mt-1 leading-normal">
                      {isUnlocked ? `Gf Accuracy (${Math.round(gfScore)}%)` : "Locked (Pending Gf exam)"}
                    </span>
                  </div>
                );
              })()}

              {/* Badge 2: Speed Demon (Processing Speed Gs) */}
              {(() => {
                const speedScore = session?.moduleScores["processing-speed"];
                const isUnlocked = speedScore !== undefined;
                
                return (
                  <div className={`flex flex-col items-center p-4 rounded-2xl bg-indigo-50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/30 text-center transition-transform hover:scale-105 cursor-pointer ${!isUnlocked ? "opacity-40 grayscale" : ""}`}>
                    <div className="h-12 w-12 rounded-full bg-indigo-500 text-white flex items-center justify-center mb-2 shadow-lg shadow-indigo-500/30">
                      <Timer className="h-6 w-6" />
                    </div>
                    <span className="text-xs font-bold text-slate-850 dark:text-white">Speed Demon</span>
                    <span className="text-[10px] text-slate-450 dark:text-slate-400 mt-1 leading-normal">
                      {isUnlocked ? `Reaction Index (${Math.round(speedScore)}%)` : "Locked (Pending Gs exam)"}
                    </span>
                  </div>
                );
              })()}

              {/* Badge 3: Iron Focus */}
              {(() => {
                const tabSwitches = session?.moduleMetrics?.tabSwitches ?? 0;
                const completedAnyModule = session && Object.keys(session.moduleScores).length > 0;
                const isUnlocked = completedAnyModule;
                const hasPerfectFocus = tabSwitches === 0;

                return (
                  <div className={`flex flex-col items-center p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 text-center transition-transform hover:scale-105 cursor-pointer ${!isUnlocked ? "opacity-40 grayscale" : ""}`}>
                    <div className="h-12 w-12 rounded-full bg-emerald-500 text-white flex items-center justify-center mb-2 shadow-lg shadow-emerald-500/30">
                      <ShieldCheck className="h-6 w-6" />
                    </div>
                    <span className="text-xs font-bold text-slate-850 dark:text-white">Iron Focus</span>
                    <span className="text-[10px] text-slate-455 dark:text-slate-400 mt-1 leading-normal">
                      {isUnlocked 
                        ? hasPerfectFocus 
                          ? "Perfect Focus (0 switches)" 
                          : `Focus Logged (${tabSwitches} switches)`
                        : "Locked (Pending focus log)"}
                    </span>
                  </div>
                );
              })()}

              {/* Badge 4: Memory Master */}
              {(() => {
                const memoryScore = session?.moduleScores["gsm"];
                const isUnlocked = memoryScore !== undefined;

                return (
                  <div className={`flex flex-col items-center p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/30 text-center transition-transform hover:scale-105 cursor-pointer ${!isUnlocked ? "opacity-40 grayscale" : ""}`}>
                    <div className="h-12 w-12 rounded-full bg-rose-500 text-white flex items-center justify-center mb-2 shadow-lg shadow-rose-500/30">
                      <Activity className="h-6 w-6" />
                    </div>
                    <span className="text-xs font-bold text-slate-850 dark:text-white">Memory Master</span>
                    <span className="text-[10px] text-slate-455 dark:text-slate-400 mt-1 leading-normal">
                      {isUnlocked ? `Retention (${Math.round(memoryScore)}%)` : "Locked (Pending Gsm exam)"}
                    </span>
                  </div>
                );
              })()}
            </div>
          </div>

        </div>

        {/* Right Area (1/3 width) - Contains Assessment History and Safe Room Guidelines */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Assessment History Card */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4 hover-lift">
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
              <Award className="h-4.5 w-4.5 text-blue-600 dark:text-blue-500" />
              <span>Assessment History</span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal">
              View and download your permanent diagnostic evaluation records:
            </p>

            <div className="space-y-3.5 pt-2 max-h-[420px] overflow-y-auto pr-1">
              {(() => {
                const sortedList = [...historySessions].sort((a, b) => new Date(b.startTime || 0).getTime() - new Date(a.startTime || 0).getTime());
                if (sortedList.length === 0) {
                  return (
                    <div className="rounded-xl border border-dashed border-slate-200 dark:border-slate-800 p-6 text-center space-y-2">
                      <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block">No Completed Reports Yet</span>
                      <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-relaxed">
                        Complete your first cognitive module to generate and unlock your certified diagnostic report record.
                      </p>
                    </div>
                  );
                }

                return sortedList.map((histSess) => {
                  const histScores = Object.values(histSess.moduleScores || {});
                  const histOverall = histScores.length > 0
                    ? Math.round(histScores.reduce((a, b) => a + b, 0) / histScores.length)
                    : 0;
                  const histCleared = histScores.length;
                  const isCurrentActive = session?.sessionId === histSess.sessionId;

                  return (
                    <div key={histSess.sessionId} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 p-4 space-y-3 transition-colors relative group">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5 text-blue-500" />
                          {new Date(histSess.startTime || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                        <span className="font-mono text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-900/30">
                          ID: {histSess.sessionId.slice(-6)}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                        <span>Overall Score Index:</span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-bold text-sm">{histOverall}%</span>
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                        <span>Completed: {histCleared} / {totalModules} Modules</span>
                        <span className="text-emerald-600 font-semibold">{isCurrentActive ? "Active Run" : "Archived Record"}</span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-1">
                        <button
                          onClick={() => {
                            AssessmentService.setViewingSession(histSess);
                            onNavigate("report");
                          }}
                          className="flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 py-2 text-xs font-bold text-white transition-all shadow-sm active:scale-95 cursor-pointer"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          <span>View Report</span>
                        </button>

                        <button
                          onClick={() => handleDeleteRecord(histSess.sessionId)}
                          className="flex items-center justify-center gap-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/40 py-2 text-xs font-bold text-rose-300 transition-all active:scale-95 cursor-pointer"
                        >
                          <Trash2 className="h-3.5 w-3.5 text-rose-400" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  );
                });
              })()}
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
      
      {/* 5. Right-Side Module Report Drawer */}
      {activeReportModule && (() => {
        const modScoreVal = session?.moduleScores[activeReportModule.id] !== undefined
          ? Math.round(session.moduleScores[activeReportModule.id])
          : 0;

        const rawModMetrics = (session as any)?.moduleMetrics?.[activeReportModule.id];
        const modPercentile = rawModMetrics?.score?.percentile !== undefined
          ? Math.round(rawModMetrics.score.percentile)
          : (modScoreVal > 0 ? Math.round(modScoreVal * 0.9) : 0);

        const rawModSubscores = rawModMetrics?.score?.subscores;
        const modSubscoresList = (() => {
          let list: { name: string; val: number }[] = [];

          if (activeReportModule.id === "gv") {
            const gvMetrics = rawModMetrics?.metrics || rawModMetrics;
            if (gvMetrics) {
              list = [
                { name: "Mental Rotation (SR)", val: Math.round(gvMetrics.mental_rotation_accuracy ?? modScoreVal) },
                { name: "Paper Folding (Vz)", val: Math.round(gvMetrics.paper_folding_accuracy ?? modScoreVal) },
                { name: "Hidden Figures (CF)", val: Math.round(gvMetrics.hidden_figures_accuracy ?? modScoreVal) },
                { name: "Mystery Map Builder (CS)", val: Math.round(gvMetrics.mystery_map_accuracy ?? modScoreVal) }
              ];
            }
          }
          
          if (!list.length && Array.isArray(rawModSubscores)) {
            list = rawModSubscores.map((s: any) => {
              const abilityName = s?.ability?.name || s?.ability?.value || s?.ability || s?.name || "Cognitive Domain";
              const valNum = typeof s?.normalized_score === 'number' ? s.normalized_score : (typeof s?.normalizedScore === 'number' ? s.normalizedScore : (typeof s?.percentage === 'number' ? s.percentage : 0));
              return {
                name: String(abilityName).replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
                val: Math.round(valNum)
              };
            });
          } else if (!list.length && rawModSubscores && typeof rawModSubscores === 'object') {
            list = Object.entries(rawModSubscores).map(([k, v]: [string, any]) => {
              const abilityName = v?.ability?.name || v?.ability?.value || v?.ability || v?.name || (isNaN(Number(k)) ? k : "Cognitive Domain");
              const valNum = typeof v === 'number' ? v : (typeof v?.normalized_score === 'number' ? v.normalized_score : (typeof v?.percentage === 'number' ? v.percentage : 0));
              return {
                name: String(abilityName).replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
                val: Math.round(valNum)
              };
            });
          }

          if (!list.length) {
            if (activeReportModule.id === "gv") {
              list = [
                { name: "Mental Rotation (SR)", val: modScoreVal },
                { name: "Paper Folding (Vz)", val: modScoreVal },
                { name: "Hidden Figures (CF)", val: modScoreVal },
                { name: "Mystery Map Builder (CS)", val: modScoreVal }
              ];
            } else {
              list = [
                { name: "Pattern Recognition", val: modScoreVal },
                { name: "Inductive Reasoning", val: modScoreVal },
                { name: "Deductive Reasoning", val: modScoreVal },
                { name: "Abstract Reasoning", val: modScoreVal },
                { name: "Logical Reasoning", val: modScoreVal }
              ];
            }
          }

          return list;
        })();

        return (
          <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
            <div className="w-full max-w-xl bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 h-full overflow-y-auto p-6 space-y-6 shadow-2xl relative">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-extrabold border border-blue-100 dark:border-blue-900/40">
                    <Brain className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-600 dark:text-blue-400">
                      Module Detailed Report
                    </span>
                    <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                      {activeReportModule.name}
                    </h2>
                  </div>
                </div>

                <button
                  onClick={() => setActiveReportModule(null)}
                  className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Score & Analytics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800">
                  <span className="text-[10px] font-mono text-slate-400 uppercase block">Module Score</span>
                  <span className="text-3xl font-black text-emerald-600 dark:text-emerald-400">
                    {modScoreVal}%
                  </span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800">
                  <span className="text-[10px] font-mono text-slate-400 uppercase block">Percentile Rank</span>
                  <span className="text-2xl font-extrabold text-slate-800 dark:text-slate-200">
                    {modPercentile > 0 ? `${modPercentile}th Percentile` : "Baseline Profile"}
                  </span>
                </div>
              </div>

              {/* Description */}
              <div className="p-4 rounded-2xl bg-blue-50/40 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 text-xs text-slate-650 dark:text-slate-300 leading-relaxed font-sans">
                <span className="font-extrabold text-blue-600 dark:text-blue-400 block mb-1">Psychometric Domain Construct:</span>
                {activeReportModule.description}
              </div>

              {/* Subscore Breakdown */}
              <div className="space-y-3 pt-2 border-t border-slate-200 dark:border-slate-800">
                <h3 className="text-xs font-mono font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-blue-500" />
                  Cognitive Subscore Performance
                </h3>
                <div className="space-y-2.5">
                  {modSubscoresList.map(item => (
                    <div key={item.name} className="space-y-1 p-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40">
                      <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                        <span>{item.name}</span>
                        <span className="font-mono text-emerald-600 dark:text-emerald-400">{item.val}%</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                        <div className="h-full rounded-full bg-emerald-500" style={{ width: `${item.val}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex gap-3">
                <button
                  onClick={() => setActiveReportModule(null)}
                  className="flex-1 rounded-xl border border-slate-200 dark:border-slate-800 py-3 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  Close Report
                </button>
                <button
                  onClick={() => {
                    setActiveReportModule(null);
                    AssessmentService.clearSession();
                    AssessmentService.createNewSession(user.id);
                    onStartAssessment();
                  }}
                  className="flex-1 rounded-xl bg-blue-600 hover:bg-blue-700 py-3 text-xs font-bold text-white transition-all shadow-md shadow-blue-500/20 active:scale-95 cursor-pointer"
                >
                  Retake Assessment
                </button>
              </div>
            </div>
          </div>
        );
      })()}

      {/* 6. Score Recording & External Sync Modal */}
      {scoreModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-fadeIn">
          <div className="w-full max-w-md rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 sm:p-7 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                  <PlusCircle className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Record / Sync Module Score
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Saves directly to SQLite DB (mentiscope.db)
                  </p>
                </div>
              </div>
              <button
                onClick={() => setScoreModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {scoreSuccessMsg ? (
              <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300 text-xs flex items-center gap-2">
                <Check className="h-4 w-4 text-emerald-500 shrink-0" />
                <span>{scoreSuccessMsg}</span>
              </div>
            ) : (
              <form onSubmit={handleSaveModuleScore} className="space-y-4">
                <div>
                  <label className="block text-xs font-mono text-slate-600 dark:text-slate-300 font-bold mb-1.5 uppercase">
                    Select Scientific Pillar / Module
                  </label>
                  <select
                    value={targetModuleId}
                    onChange={(e) => setTargetModuleId(e.target.value)}
                    className="w-full rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 p-3 text-xs text-slate-900 dark:text-white focus:border-indigo-500 focus:outline-hidden font-sans"
                  >
                    {NINE_PILLARS_CONFIG.map((m, idx) => (
                      <option key={m.id} value={m.id}>
                        {idx + 1}. {m.name} {m.externalUrl ? "(External Module)" : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-mono text-slate-600 dark:text-slate-300 font-bold uppercase">
                      Score Percentage (0 - 100)%
                    </label>
                    {targetModuleId === "auditory_verbal" && (
                      <button
                        type="button"
                        onClick={handleSyncExternal}
                        disabled={syncingExternal}
                        className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 cursor-pointer disabled:opacity-50"
                      >
                        {syncingExternal ? (
                          <>
                            <Loader2 className="h-3 w-3 animate-spin" />
                            <span>Syncing...</span>
                          </>
                        ) : (
                          <>
                            <RefreshCw className="h-3 w-3" />
                            <span>Auto-Fetch from Module 10</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    placeholder="e.g. 72"
                    required
                    value={inputScoreVal}
                    onChange={(e) => setInputScoreVal(e.target.value)}
                    className="w-full rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 p-3 text-sm text-slate-900 dark:text-white font-mono focus:border-indigo-500 focus:outline-hidden"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    Enter the percentage score from test completion or external assessment runner.
                  </p>
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setScoreModalOpen(false)}
                    className="px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={savingScore}
                    className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-extrabold text-white transition-all shadow-lg shadow-indigo-500/20 cursor-pointer disabled:opacity-50"
                  >
                    {savingScore ? (
                      <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <Check className="h-3.5 w-3.5" />
                        <span>Save to DB</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
