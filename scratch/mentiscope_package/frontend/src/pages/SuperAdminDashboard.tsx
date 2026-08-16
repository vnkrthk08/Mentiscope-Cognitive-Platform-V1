import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, ModuleConfig, SystemLog, Question } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { QUESTIONS_DATA } from "../config/questionsData";
import { AnalyticsService } from "../services/analytics/AnalyticsService";
import { ModuleDifficultyChart } from "../components/Charts";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { 
  Settings, 
  Database, 
  Terminal, 
  TrendingUp, 
  Users, 
  Cpu, 
  Globe, 
  RefreshCw, 
  Trash2, 
  Save, 
  CheckCircle,
  FileSpreadsheet,
  Plus,
  Edit3,
  ListOrdered,
  Layers,
  Lock,
  FileText,
  ExternalLink
} from "lucide-react";

interface SuperAdminDashboardProps {
  user: User;
  onNavigate?: (page: string, targetTab?: string) => void;
}

export default function SuperAdminDashboard({ user, onNavigate }: SuperAdminDashboardProps) {
  const navigate = useNavigate();

  // Navigation Tab State
  const [activeTab, setActiveTab] = useState<"system" | "questions">("system");

  // Configurable REST Gateway URLs State
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>(MODULE_CONFIGS);
  const [logs, setLogs] = useState<SystemLog[]>(AnalyticsService.getSystemLogs());
  const [editingModule, setEditingModule] = useState<ModuleConfig | null>(null);
  const [newApiUrl, setNewApiUrl] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Question Bank State
  const [questionsData, setQuestionsData] = useState<Record<string, Question[]>>(QUESTIONS_DATA);
  const [selectedModuleId, setSelectedModuleId] = useState<string>("gq");

  // Question editing modal states
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [newQuestionText, setNewQuestionText] = useState("");
  const [newQuestionStory, setNewQuestionStory] = useState("");
  const [newQuestionAnswer, setNewQuestionAnswer] = useState("");
  const [newQuestionHint, setNewQuestionHint] = useState("");
  const [newQuestionOptions, setNewQuestionOptions] = useState<string[]>([]);
  const [optionInput, setOptionInput] = useState("");

  // Stats Counters
  const totalStudents = 148;
  const activeSessions = 12;
  const systemUptime = "99.98%";
  const apiStatus = "Operational";

  const handleEditApiUrl = (mod: ModuleConfig) => {
    setEditingModule(mod);
    setNewApiUrl(mod.apiBaseUrl);
  };

  const handleSaveApiUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingModule) return;

    const updated = moduleConfigs.map((m) => {
      if (m.id === editingModule.id) {
        return { ...m, apiBaseUrl: newApiUrl };
      }
      return m;
    });

    setModuleConfigs(updated);
    setEditingModule(null);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 4000);

    // Append Audit Log
    const newAuditLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Modified Gateway Routing URL",
      status: "success",
      details: `Updated active REST API address for Module ${editingModule.id} to '${newApiUrl}'`
    };
    setLogs([newAuditLog, ...logs]);
  };

  const handleFlushDb = () => {
    if (!confirm("Are you sure you want to flush all transient candidate testing sessions? This cannot be undone.")) return;
    localStorage.clear();
    
    const flushLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Flushed Systems Storage",
      status: "warning",
      details: "Cleared all active and completed candidate sessions from local mock cloud databases."
    };
    setLogs([flushLog, ...logs]);
  };

  const handleExportLogs = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(logs, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "mentiscope_audit_logs.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Question Bank Actions
  const handleEditQuestionClick = (q: Question) => {
    setEditingQuestion(q);
    setNewQuestionText(q.text);
    setNewQuestionStory(q.story || "");
    setNewQuestionAnswer(q.correctAnswer || "");
    setNewQuestionHint(q.hint || "");
    setNewQuestionOptions(q.options || []);
  };

  const handleSaveQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingQuestion) return;

    const updatedModuleQs = (questionsData[selectedModuleId] || []).map(q => {
      if (q.id === editingQuestion.id) {
        return {
          ...q,
          text: newQuestionText,
          story: newQuestionStory,
          correctAnswer: newQuestionAnswer,
          hint: newQuestionHint,
          options: newQuestionOptions.length > 0 ? newQuestionOptions : undefined
        };
      }
      return q;
    });

    setQuestionsData({
      ...questionsData,
      [selectedModuleId]: updatedModuleQs
    });
    setEditingQuestion(null);

    // Append log
    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Modified Question Parameters",
      status: "success",
      details: `Updated question parameters for task ID ${editingQuestion.id} in module ${selectedModuleId}`
    };
    setLogs([newLog, ...logs]);
  };

  const handleDeleteQuestion = (id: string) => {
    if (!confirm("Are you sure you want to remove this question from the active research pool?")) return;
    const filtered = (questionsData[selectedModuleId] || []).filter(q => q.id !== id);
    
    setQuestionsData({
      ...questionsData,
      [selectedModuleId]: filtered
    });

    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Removed Question from Bank",
      status: "warning",
      details: `Deleted task ID ${id} from active question pool in module ${selectedModuleId}`
    };
    setLogs([newLog, ...logs]);
  };

  const handleAddQuestion = () => {
    const newId = `${selectedModuleId}-new-${Math.random().toString(36).substring(2, 7)}`;
    const newQ: Question = {
      id: newId,
      text: "New diagnostic stimulus prompt goes here.",
      story: "Standardized evaluation stimulus paradigm.",
      options: ["Option A", "Option B", "Option C", "Option D"],
      correctAnswer: "Option A",
      hint: "Select Option A.",
      type: "choice"
    };

    setQuestionsData({
      ...questionsData,
      [selectedModuleId]: [...(questionsData[selectedModuleId] || []), newQ]
    });

    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Added Question to Bank",
      status: "success",
      details: `Appended task ID ${newId} to ${selectedModuleId} evaluation bank`
    };
    setLogs([newLog, ...logs]);
  };

  const handleAddOption = () => {
    if (!optionInput.trim()) return;
    setNewQuestionOptions([...newQuestionOptions, optionInput.trim()]);
    setOptionInput("");
  };

  const handleRemoveOption = (index: number) => {
    setNewQuestionOptions(newQuestionOptions.filter((_, i) => i !== index));
  };

  // Analytics datasets
  const difficultyData = AnalyticsService.getModulePerformanceData();
  const currentModule = MODULE_CONFIGS.find(m => m.id === selectedModuleId) || MODULE_CONFIGS[0];
  const activeQuestions = questionsData[selectedModuleId] || [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      
      {/* 1. Header & Terminal Info */}
      <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-sm">
        <div>
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-605 bg-blue-50 dark:text-blue-400 dark:bg-blue-950/40 px-2.5 py-1 rounded-md border border-blue-150 dark:border-blue-900/40">
            Root Control Center
          </span>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mt-2">
            Administrator Terminal: {user.name}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Access Level: Root System Administration & Database management.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <a
            href="http://localhost:8000/docs#/processing-speed/start_api_modules_processing_speed_start_post"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98]"
            title="Open Mentiscope FastAPI Swagger Documentation"
          >
            <FileText className="h-3.5 w-3.5" />
            <span>API Docs</span>
            <ExternalLink className="h-3 w-3 opacity-80" />
          </a>
          <button
            onClick={() => setActiveTab("system")}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === "system"
                ? "bg-slate-900 dark:bg-blue-600 text-white shadow-sm"
                : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50"
            }`}
          >
            System Overview
          </button>
          <button
            onClick={() => setActiveTab("questions")}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === "questions"
                ? "bg-slate-900 dark:bg-blue-600 text-white shadow-sm"
                : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50"
            }`}
          >
            Question Bank Manager
          </button>
        </div>
      </div>

      {activeTab === "system" ? (
        <>
          {/* Metric Overview Panels */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <Users className="h-4.5 w-4.5" />
                <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Total Cohort</span>
              </div>
              <p className="text-2xl font-black text-slate-900 dark:text-white font-mono tracking-tight">{totalStudents}</p>
              <p className="text-[10px] text-slate-400">Registered participants</p>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <Cpu className="h-4.5 w-4.5 animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Active Tests</span>
              </div>
              <p className="text-2xl font-black text-blue-600 font-mono tracking-tight">{activeSessions}</p>
              <p className="text-[10px] text-blue-500">Live sessions ongoing</p>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <Globe className="h-4.5 w-4.5 text-emerald-500" />
                <span className="text-[10px] font-bold uppercase tracking-wider font-mono">API Health</span>
              </div>
              <p className="text-2xl font-black text-emerald-600 font-mono tracking-tight">{apiStatus}</p>
              <p className="text-[10px] text-emerald-500">FastAPI Gateway online</p>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <RefreshCw className="h-4.5 w-4.5" />
                <span className="text-[10px] font-bold uppercase tracking-wider font-mono">System Uptime</span>
              </div>
              <p className="text-2xl font-black text-slate-900 dark:text-white font-mono tracking-tight">{systemUptime}</p>
              <p className="text-[10px] text-slate-400">Server instance status</p>
            </div>

          </div>

          {/* Main Dashboard Split Layout */}
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
            
            {/* Left Side: API Router Manager */}
            <div className="lg:col-span-7 space-y-8">
              
              {/* FastAPI Routing endpoints list */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4">
                <div>
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <h2 className="text-base font-bold text-slate-900 dark:text-white">API Gateway Router configurations</h2>
                    <div className="flex items-center gap-2">
                      <a
                        href="http://localhost:8000/docs#/processing-speed/start_api_modules_processing_speed_start_post"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50 hover:bg-blue-100 dark:hover:bg-blue-900/60 px-2.5 py-1 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors"
                      >
                        <FileText className="h-3 w-3" />
                        <span>Swagger Docs</span>
                        <ExternalLink className="h-2.5 w-2.5" />
                      </a>
                      <span className="text-[9px] font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 font-bold uppercase">
                        Fully API-Driven
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Each cognitive module communicates via isolated REST microservices. Update target URLs below without editing UI code.
                  </p>
                </div>

                {saveSuccess && (
                  <div className="rounded-xl bg-emerald-50 border border-emerald-100 p-4 text-xs font-semibold text-emerald-800 flex items-center gap-2">
                    <CheckCircle className="h-4.5 w-4.5 text-emerald-600" />
                    <span>Microservice endpoint routing parameters updated successfully!</span>
                  </div>
                )}

                <div className="space-y-3.5 pt-2">
                  {moduleConfigs.map((mod, idx) => (
                    <div 
                      key={mod.id}
                      className="rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/20 p-4 space-y-2.5 hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                          M{idx+1}: {mod.name}
                        </span>
                        
                        <button
                          onClick={() => handleEditApiUrl(mod)}
                          className="text-blue-650 dark:text-blue-400 hover:underline font-bold text-[11px]"
                        >
                          Update Router Base
                        </button>
                      </div>

                      <div className="bg-slate-950 rounded-lg p-2.5 font-mono text-[10px] text-slate-355 flex items-center justify-between gap-4 overflow-hidden">
                        <span className="truncate text-blue-400">{mod.apiBaseUrl}</span>
                        <span className="text-slate-500 shrink-0 uppercase tracking-wide">POST/GET</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* End of Left Side APIs configurations */}
            </div>

            {/* Right Side: Audit Logs & System Reset Database controls */}
            <div className="lg:col-span-5 space-y-8">
              
              {/* Data Export Hub (Phase 3) */}
              <div className="rounded-2xl border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/30 dark:bg-emerald-950/20 p-5 space-y-4 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <FileSpreadsheet className="h-24 w-24 text-emerald-600" />
                </div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5 relative z-10">
                  <FileSpreadsheet className="h-4.5 w-4.5 text-emerald-600 dark:text-emerald-400" />
                  <span>Clinical Data Export Hub</span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal relative z-10 pr-6">
                  Export anonymized participant datasets for deep psychometric clinical research and validation.
                </p>
                <div className="space-y-2 relative z-10">
                  <button className="w-full flex justify-between items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-3 rounded-xl hover:border-emerald-400 dark:hover:border-emerald-600 transition-colors shadow-sm">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Raw Assessment JSON</span>
                    <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-900/30 dark:text-emerald-400 px-2 rounded">Download</span>
                  </button>
                  <button className="w-full flex justify-between items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-3 rounded-xl hover:border-emerald-400 dark:hover:border-emerald-600 transition-colors shadow-sm">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Aggregated CSV (Cohort A)</span>
                    <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-900/30 dark:text-emerald-400 px-2 rounded">Download</span>
                  </button>
                </div>
              </div>
              
              {/* Systems Database Command Card */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-sm">
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Database className="h-4.5 w-4.5 text-blue-600" />
                  <span>Diagnostic System Utilities</span>
                </h2>
                <p className="text-xs text-slate-400 leading-normal">
                  Quick commands to clean up local sandbox environments during active quality assurance evaluation:
                </p>

                <div className="space-y-2 pt-2 text-xs">
                  <button
                    onClick={handleFlushDb}
                    className="w-full flex items-center justify-between rounded-xl border border-rose-100 dark:border-rose-950 bg-rose-50/20 dark:bg-rose-950/10 text-rose-800 dark:text-rose-400 p-3 hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-colors"
                  >
                    <div className="text-left">
                      <p className="font-bold">Flush Testing Database</p>
                      <p className="text-[10px] text-rose-500/80">Clear and reset active student sessions</p>
                    </div>
                    <Trash2 className="h-4.5 w-4.5 text-rose-600" />
                  </button>

                  <button
                    onClick={handleExportLogs}
                    className="w-full flex items-center justify-between rounded-xl border border-blue-100 dark:border-blue-955 bg-blue-50/20 dark:bg-blue-950/10 text-blue-800 dark:text-blue-400 p-3 hover:bg-blue-50 dark:hover:bg-blue-950/20 transition-colors"
                  >
                    <div className="text-left">
                      <p className="font-bold">Export Live Audit Trail</p>
                      <p className="text-[10px] text-blue-500/80">Retrieve logs stream inside JSON backup</p>
                    </div>
                    <FileSpreadsheet className="h-4.5 w-4.5 text-blue-600" />
                  </button>
                </div>
              </div>

              {/* Audit Logs Stream */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-sm">
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Terminal className="h-4.5 w-4.5 text-slate-500" />
                  <span>Active System Audit Logs</span>
                </h2>

                <div className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[10px] text-slate-505 max-h-[36vh] overflow-y-auto pr-1">
                  {logs.map((log) => (
                    <div key={log.id} className="py-2.5 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-850 dark:text-slate-350 text-[11px]">{log.action}</span>
                        <span className={`text-[8px] font-bold px-1.5 rounded uppercase ${
                          log.status === "success" ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400" : "bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400"
                        }`}>
                          {log.status}
                        </span>
                      </div>
                      <p className="text-slate-400 leading-normal">{log.details}</p>
                      <div className="flex items-center justify-between text-[9px] text-slate-400">
                        <span>Operator: {log.user}</span>
                        <span>{log.timestamp}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>

          {/* Performance chart visualizers (Side-by-Side Analytics) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
            {/* Task Performance Metrics */}
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Task Performance Metrics</h2>
                <p className="text-xs text-slate-400">Average failure thresholds and user latency metrics compiled per capsule paradigm.</p>
              </div>

              <div className="border border-slate-100 dark:border-slate-800 rounded-2xl bg-slate-50/40 dark:bg-slate-950/10 p-4">
                <ModuleDifficultyChart data={difficultyData} />
              </div>
            </div>

            {/* Global Heatmap Analytics (Phase 3) */}
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Globe className="h-5 w-5 text-indigo-500" />
                  Global Cognitive Density Heatmap
                </h2>
                <p className="text-xs text-slate-400">Distribution of General Intelligence (g) baseline scores across active demographic regions.</p>
              </div>
              <div className="h-[200px] border border-slate-100 dark:border-slate-800 rounded-2xl bg-slate-50/40 dark:bg-slate-950/10 p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { region: 'NA', score: 82 },
                    { region: 'EU', score: 79 },
                    { region: 'APAC', score: 85 },
                    { region: 'LATAM', score: 74 },
                    { region: 'MENA', score: 76 }
                  ]} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="region" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94A3B8' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94A3B8' }} />
                    <Tooltip cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                    <Bar dataKey="score" fill="#6366F1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* Question Bank Manager Dashboard View */
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          
          {/* Left Panel: Module Selector List */}
          <div className="lg:col-span-4 space-y-8">
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-sm">
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                <Layers className="h-4.5 w-4.5 text-blue-600" />
                <span>Select Cognitive Paradigm</span>
              </h2>

              <div className="space-y-1.5 pt-1">
                {moduleConfigs.map((mod, idx) => (
                  <button
                    key={mod.id}
                    onClick={() => setSelectedModuleId(mod.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                      selectedModuleId === mod.id
                        ? "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 text-blue-900 dark:text-blue-300"
                        : "bg-slate-50/50 dark:bg-slate-950/20 border-slate-100 dark:border-slate-800/80 text-slate-600 dark:text-slate-400 hover:bg-slate-50"
                    }`}
                  >
                    <span className="truncate">M{idx+1}: {mod.name}</span>
                    <span className="text-[9px] font-mono opacity-80 uppercase">
                      {questionsData[mod.id]?.length || 0} Stimuli
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Selected Module Settings */}
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-sm">
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                <Settings className="h-4.5 w-4.5 text-slate-500" />
                <span>Module Parameters</span>
              </h2>

              <div className="rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20 p-4 space-y-3 text-xs text-slate-500 dark:text-slate-400">
                <div>
                  <p className="text-[10px] font-mono font-bold text-blue-500 uppercase">Description</p>
                  <p className="leading-relaxed mt-0.5 text-slate-650 dark:text-slate-350">{currentModule.description}</p>
                </div>
                <div>
                  <p className="text-[10px] font-mono font-bold text-blue-500 uppercase">Estimated Time Limit</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">{currentModule.estimatedTime}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Selected Module Question List */}
          <div className="lg:col-span-8 space-y-8">
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4">
              
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">Manage Stimulus Question Bank</h2>
                  <p className="text-xs text-slate-400">Configure visual shapes, colors, and choice options for active candidate sessions.</p>
                </div>

                <button
                  onClick={handleAddQuestion}
                  className="flex items-center gap-1 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Question</span>
                </button>
              </div>

              {activeQuestions.length === 0 ? (
                <div className="rounded-xl border-2 border-dashed border-slate-200 p-12 text-center text-slate-400">
                  <Database className="h-8 w-8 mx-auto text-slate-300 mb-2" />
                  <p className="text-xs font-semibold">No custom questions created for this capsule yet.</p>
                  <p className="text-[10px] text-slate-400 mt-1">This module uses server-side Python bridge generated datasets by default.</p>
                </div>
              ) : (
                <div className="space-y-4 pt-2">
                  {activeQuestions.map((q) => (
                    <div key={q.id} className="rounded-xl border border-slate-100 dark:border-slate-800 p-4 space-y-3 bg-slate-50/30 dark:bg-slate-950/20 hover:bg-slate-50 transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <span className="font-mono text-[9px] font-bold text-slate-400 uppercase">
                            Task ID: {q.id}
                          </span>
                          <p className="text-xs font-semibold text-slate-850 dark:text-slate-200 leading-normal mt-0.5">
                            {q.text}
                          </p>
                        </div>

                        <div className="flex gap-1.5 shrink-0">
                          <button
                            onClick={() => handleEditQuestionClick(q)}
                            className="rounded p-1 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-700"
                            title="Edit question parameters"
                          >
                            <Edit3 className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteQuestion(q.id)}
                            className="rounded p-1 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                            title="Remove question"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>

                      {q.story && (
                        <div className="text-[10px] text-slate-500 leading-relaxed pl-3 border-l-2 border-slate-200 dark:border-slate-700">
                          <span className="font-semibold block text-slate-600 dark:text-slate-400">Cognitive Paradigm:</span>
                          {q.story}
                        </div>
                      )}

                      {q.options && q.options.length > 0 && (
                        <div className="grid grid-cols-2 gap-2 text-[10px] pl-3">
                          {q.options.map((opt, i) => (
                            <div key={i} className="text-slate-405 dark:text-slate-500 truncate">
                              {String.fromCharCode(65 + i)}. {opt}
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-[10px] pl-3 text-slate-400">
                        <span>Correct Answer: <span className="font-bold text-slate-700 dark:text-slate-350">{q.correctAnswer}</span></span>
                        {q.hint && <span>Hint: <span className="font-medium text-slate-600 dark:text-slate-400">{q.hint}</span></span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>
      )}

      {/* API Router Editing Modal */}
      {editingModule && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm animate-fade-in">
          <form onSubmit={handleSaveApiUrl} className="w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Update Gateway Endpoint Base
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Set custom FastAPI server target microservice URL for <span className="font-semibold text-slate-800 dark:text-slate-200">{editingModule.name}</span>.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">FastAPI REST Endpoint URL</label>
              <input
                type="url"
                required
                value={newApiUrl}
                onChange={(e) => setNewApiUrl(e.target.value)}
                placeholder="http://fastapi-service/modules/gq"
                className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none font-mono"
              />
            </div>

            <div className="flex gap-2.5 pt-2 justify-end">
              <button
                type="button"
                onClick={() => setEditingModule(null)}
                className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-650 dark:text-slate-350 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save Endpoint</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Question Bank Editing Modal */}
      {editingQuestion && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm animate-fade-in">
          <form onSubmit={handleSaveQuestion} className="w-full max-w-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Edit Stimulus Parameters: {editingQuestion.id}
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Stimulus Text Prompt</label>
                <textarea
                  rows={2}
                  required
                  value={newQuestionText}
                  onChange={(e) => setNewQuestionText(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Cognitive Paradigm Instructions</label>
                <textarea
                  rows={2}
                  value={newQuestionStory}
                  onChange={(e) => setNewQuestionStory(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Correct Answer</label>
                  <input
                    type="text"
                    required
                    value={newQuestionAnswer}
                    onChange={(e) => setNewQuestionAnswer(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Stimulus Hint</label>
                  <input
                    type="text"
                    value={newQuestionHint}
                    onChange={(e) => setNewQuestionHint(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Options Config (Choice type only) */}
              {editingQuestion.options && (
                <div className="space-y-2">
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Stimulus Options</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={optionInput}
                      onChange={(e) => setOptionInput(e.target.value)}
                      placeholder="Add choice option text"
                      className="flex-grow rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={handleAddOption}
                      className="rounded-xl bg-slate-900 dark:bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-850"
                    >
                      Add Option
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-2 max-h-36 overflow-y-auto pt-1">
                    {newQuestionOptions.map((opt, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between p-2 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/20 text-xs text-slate-700 dark:text-slate-300"
                      >
                        <span className="truncate">{String.fromCharCode(65 + index)}. {opt}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveOption(index)}
                          className="text-rose-500 hover:text-rose-700 text-xs px-1"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2.5 pt-4 border-t border-slate-100 dark:border-slate-800 justify-end">
              <button
                type="button"
                onClick={() => setEditingQuestion(null)}
                className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-650 dark:text-slate-350 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save Question</span>
              </button>
            </div>
          </form>
        </div>
      )}

    </div>
  );
}
