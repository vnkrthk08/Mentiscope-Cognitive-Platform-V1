import React, { useState, useEffect, useMemo } from "react";
import { 
  FileSpreadsheet, 
  Download, 
  RefreshCw, 
  Search, 
  Filter, 
  Users, 
  Award, 
  Clock, 
  CheckCircle2, 
  Layers, 
  FileDown, 
  ChevronLeft, 
  ChevronRight,
  TrendingUp,
  Cpu,
  Globe,
  SlidersHorizontal,
  Check,
  AlertCircle
} from "lucide-react";
import { 
  AdminCsvService, 
  AdminCsvDashboardData, 
  StudentScoreRecord, 
  QuestionBankItem, 
  ModuleBenchmarkItem 
} from "../services/admin/AdminCsvService";
import { MODULE_CONFIGS } from "../config/moduleConfig";

interface AdminCsvHubProps {
  onBackToSystem?: () => void;
}

export const AdminCsvHub: React.FC<AdminCsvHubProps> = ({ onBackToSystem }) => {
  const [data, setData] = useState<AdminCsvDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [subTab, setSubTab] = useState<"studentScores" | "questionsBank" | "moduleBenchmarks">("studentScores");

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState("");
  const [moduleFilter, setModuleFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Pagination
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Success Notification
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const loadData = async (manual = false) => {
    if (manual) setIsSyncing(true);
    try {
      const res = await AdminCsvService.fetchDashboardData();
      setData(res);
    } catch (e) {
      console.error("Failed to load CSV dashboard data:", e);
    } finally {
      setLoading(false);
      if (manual) setTimeout(() => setIsSyncing(false), 500);
    }
  };

  useEffect(() => {
    loadData();
    let interval: any = null;
    if (autoSync) {
      interval = setInterval(() => {
        loadData(false);
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoSync]);

  // Reset page on filter changes
  useEffect(() => {
    setPage(1);
  }, [searchQuery, moduleFilter, statusFilter, subTab]);

  const handleDownload = (type: "student-scores" | "questions-bank" | "module-benchmarks" | "all-datasets", label: string) => {
    AdminCsvService.downloadDataset(type);
    setDownloadSuccess(`Export initiated: ${label}`);
    setTimeout(() => setDownloadSuccess(null), 4000);
  };

  // Filtered Student Scores
  const filteredScores = useMemo(() => {
    if (!data?.datasets.studentScores) return [];
    return data.datasets.studentScores.filter(s => {
      const matchSearch = searchQuery.trim() === "" ||
        s.studentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.studentEmail.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.studentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.attemptId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.moduleName.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchMod = moduleFilter === "all" || s.moduleId.toLowerCase() === moduleFilter.toLowerCase();
      const matchStatus = statusFilter === "all" || s.status.toLowerCase() === statusFilter.toLowerCase();

      return matchSearch && matchMod && matchStatus;
    });
  }, [data, searchQuery, moduleFilter, statusFilter]);

  // Filtered Questions Bank
  const filteredQuestions = useMemo(() => {
    if (!data?.datasets.questionsBank) return [];
    return data.datasets.questionsBank.filter(q => {
      const matchSearch = searchQuery.trim() === "" ||
        q.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.questionId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.moduleName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.correctAnswer.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchMod = moduleFilter === "all" || q.moduleId.toLowerCase() === moduleFilter.toLowerCase();
      return matchSearch && matchMod;
    });
  }, [data, searchQuery, moduleFilter]);

  // Filtered Module Benchmarks
  const filteredBenchmarks = useMemo(() => {
    if (!data?.datasets.moduleBenchmarks) return [];
    return data.datasets.moduleBenchmarks.filter(b => {
      const matchSearch = searchQuery.trim() === "" ||
        b.moduleName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.moduleId.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchMod = moduleFilter === "all" || b.moduleId.toLowerCase() === moduleFilter.toLowerCase();
      return matchSearch && matchMod;
    });
  }, [data, searchQuery, moduleFilter]);

  // Pagination slice for active subTab
  const activeDatasetCount = subTab === "studentScores" 
    ? filteredScores.length 
    : subTab === "questionsBank" 
      ? filteredQuestions.length 
      : filteredBenchmarks.length;

  const totalPages = Math.max(1, Math.ceil(activeDatasetCount / rowsPerPage));
  const startIndex = (page - 1) * rowsPerPage;
  const endIndex = Math.min(startIndex + rowsPerPage, activeDatasetCount);

  const paginatedScores = useMemo(() => {
    return filteredScores.slice(startIndex, endIndex);
  }, [filteredScores, startIndex, endIndex]);

  const paginatedQuestions = useMemo(() => {
    return filteredQuestions.slice(startIndex, endIndex);
  }, [filteredQuestions, startIndex, endIndex]);

  const paginatedBenchmarks = useMemo(() => {
    return filteredBenchmarks.slice(startIndex, endIndex);
  }, [filteredBenchmarks, startIndex, endIndex]);

  const kpis = data?.kpis || {
    totalAttempts: 0,
    uniqueCandidates: 0,
    cohortAvgScore: 0,
    activeModules: 10,
    lastSyncedAt: "Live"
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Banner & Real-Time Sync Controller */}
      <div className="rounded-3xl border border-emerald-200 dark:border-emerald-900/60 bg-gradient-to-br from-emerald-50/50 via-white to-teal-50/30 dark:from-slate-900 dark:via-slate-900 dark:to-emerald-950/20 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Real-Time CSV Sync Active
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                Zero Dummy Data • Genuine Student ROM Registry
              </span>
            </div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight mt-2 flex items-center gap-2">
              <FileSpreadsheet className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              Multi-Module CSV & Psychometric Data Console
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-3xl leading-relaxed">
              Every time a candidate attempts any of the 10 cognitive modules, scores and timestamps append in real time. 
              Review, filter, and stream all three production CSV datasets across the entire cohort.
            </p>
          </div>

          {/* Sync actions & ZIP Export */}
          <div className="flex flex-wrap items-center gap-2.5">
            <label className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm cursor-pointer select-none">
              <input 
                type="checkbox"
                checked={autoSync}
                onChange={(e) => setAutoSync(e.target.checked)}
                className="rounded text-emerald-600 focus:ring-emerald-500"
              />
              <span>Live Auto-Sync (5s)</span>
            </label>

            <button
              onClick={() => loadData(true)}
              disabled={isSyncing}
              className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 shadow-sm transition-all"
              title="Force synchronize database with CSV files"
            >
              <RefreshCw className={`h-3.5 w-3.5 text-emerald-600 ${isSyncing ? "animate-spin" : ""}`} />
              <span>{isSyncing ? "Syncing..." : "Sync Now"}</span>
            </button>

            <button
              onClick={() => handleDownload("all-datasets", "All Datasets ZIP Archive")}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-sm hover:from-emerald-500 hover:to-teal-500 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Download All 3 CSVs (ZIP)</span>
            </button>
          </div>
        </div>

        {downloadSuccess && (
          <div className="mt-4 rounded-xl bg-emerald-100/80 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 p-3 text-xs font-bold text-emerald-900 dark:text-emerald-200 flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
            <span>{downloadSuccess} — downloaded directly to your machine.</span>
          </div>
        )}
      </div>

      {/* Real Data KPI Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Exam Attempts</span>
            <Award className="h-4 w-4 text-emerald-500" />
          </div>
          <p className="text-3xl font-black text-slate-900 dark:text-white font-mono tracking-tight">
            {kpis.totalAttempts}
          </p>
          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Appended in real-time
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Tested Candidates</span>
            <Users className="h-4 w-4 text-blue-500" />
          </div>
          <p className="text-3xl font-black text-blue-600 dark:text-blue-400 font-mono tracking-tight">
            {kpis.uniqueCandidates}
          </p>
          <p className="text-[10px] text-slate-400">
            Unique candidate IDs
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Cohort Average</span>
            <TrendingUp className="h-4 w-4 text-teal-500" />
          </div>
          <p className="text-3xl font-black text-slate-900 dark:text-white font-mono tracking-tight">
            {kpis.cohortAvgScore}%
          </p>
          <p className="text-[10px] text-slate-400">
            Calculated across all tests
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Active Pillars</span>
            <Layers className="h-4 w-4 text-indigo-500" />
          </div>
          <p className="text-3xl font-black text-indigo-600 dark:text-indigo-400 font-mono tracking-tight">
            10
          </p>
          <p className="text-[10px] text-slate-400">
            Cognitive assessment batteries
          </p>
        </div>

      </div>

      {/* 3 CSV Datasets Tab Selector Bar */}
      <div className="border-b border-slate-200 dark:border-slate-800 flex flex-wrap gap-2 pt-2">
        <button
          onClick={() => setSubTab("studentScores")}
          className={`px-5 py-3 text-xs font-bold rounded-t-xl transition-all border-b-2 flex items-center gap-2 ${
            subTab === "studentScores"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/50 dark:bg-emerald-950/30"
              : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          <Award className="h-4 w-4" />
          <span>1. Student Scores & Exam Attempts</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {data?.datasets.studentScores.length || 0}
          </span>
        </button>

        <button
          onClick={() => setSubTab("questionsBank")}
          className={`px-5 py-3 text-xs font-bold rounded-t-xl transition-all border-b-2 flex items-center gap-2 ${
            subTab === "questionsBank"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/50 dark:bg-emerald-950/30"
              : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>2. Cognitive Questions Bank Dataset</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {data?.datasets.questionsBank.length || 0}
          </span>
        </button>

        <button
          onClick={() => setSubTab("moduleBenchmarks")}
          className={`px-5 py-3 text-xs font-bold rounded-t-xl transition-all border-b-2 flex items-center gap-2 ${
            subTab === "moduleBenchmarks"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/50 dark:bg-emerald-950/30"
              : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          <span>3. Module Benchmarks & Psychometrics</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {data?.datasets.moduleBenchmarks.length || 0}
          </span>
        </button>
      </div>

      {/* Dataset Filter & Export Toolbar */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        
        {/* Left: Search & Filters */}
        <div className="flex flex-wrap items-center gap-2.5 flex-1">
          <div className="relative min-w-[220px] max-w-sm flex-1">
            <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text"
              placeholder={
                subTab === "studentScores" 
                  ? "Search by student name, ID, or email..." 
                  : subTab === "questionsBank"
                    ? "Search questions prompt or answer..."
                    : "Search modules or category..."
              }
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          {/* Module Selector Filter */}
          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 focus:outline-none"
          >
            <option value="all">All Cognitive Modules</option>
            {MODULE_CONFIGS.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>

          {/* Status filter (only relevant for student scores) */}
          {subTab === "studentScores" && (
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              <option value="all">All Statuses</option>
              <option value="passed">Passed (&gt;=60%)</option>
              <option value="completed">Completed (&lt;60%)</option>
            </select>
          )}

          {(searchQuery || moduleFilter !== "all" || statusFilter !== "all") && (
            <button
              onClick={() => {
                setSearchQuery("");
                setModuleFilter("all");
                setStatusFilter("all");
              }}
              className="text-[11px] font-bold text-rose-600 hover:underline px-2"
            >
              Clear filters
            </button>
          )}
        </div>

        {/* Right: Direct Download Button for currently active tab */}
        <div className="flex items-center gap-2">
          {subTab === "studentScores" && (
            <button
              onClick={() => handleDownload("student-scores", "student_performance_records.csv")}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all"
            >
              <FileDown className="h-3.5 w-3.5" />
              <span>Export Scores CSV ({filteredScores.length})</span>
            </button>
          )}

          {subTab === "questionsBank" && (
            <button
              onClick={() => handleDownload("questions-bank", "cognitive_questions_bank.csv")}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all"
            >
              <FileDown className="h-3.5 w-3.5" />
              <span>Export Questions CSV ({filteredQuestions.length})</span>
            </button>
          )}

          {subTab === "moduleBenchmarks" && (
            <button
              onClick={() => handleDownload("module-benchmarks", "module_benchmarks_analytics.csv")}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all"
            >
              <FileDown className="h-3.5 w-3.5" />
              <span>Export Benchmarks CSV ({filteredBenchmarks.length})</span>
            </button>
          )}
        </div>

      </div>

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 1: Real-Time Student Scores & Exam Logs Table */}
      {/* ------------------------------------------------------------- */}
      {subTab === "studentScores" && (
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>Real-Time Student Performance Records</span>
                <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded font-bold uppercase">
                  student_performance_records.csv
                </span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Showing {filteredScores.length === 0 ? 0 : startIndex + 1}–{endIndex} of {filteredScores.length} recorded exam attempts.
              </p>
            </div>
            
            <div className="text-[11px] font-mono text-slate-400">
              Synced: {kpis.lastSyncedAt}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-950/40 text-[10px] uppercase font-mono text-slate-400 border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-bold">Attempt ID</th>
                  <th className="py-3 px-4 font-bold">Timestamp</th>
                  <th className="py-3 px-4 font-bold">Candidate</th>
                  <th className="py-3 px-4 font-bold">Module Evaluated</th>
                  <th className="py-3 px-4 font-bold text-center">Score (%)</th>
                  <th className="py-3 px-4 font-bold text-center">Questions</th>
                  <th className="py-3 px-4 font-bold text-center">Duration</th>
                  <th className="py-3 px-4 font-bold text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {paginatedScores.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400">
                      <FileSpreadsheet className="h-8 w-8 mx-auto text-slate-300 dark:text-slate-600 mb-2" />
                      <p className="text-xs font-semibold">No student exam attempts found.</p>
                      <p className="text-[10px] text-slate-400 mt-1">
                        As students anywhere take tests, their scores will append to this table and CSV in real time.
                      </p>
                    </td>
                  </tr>
                ) : (
                  paginatedScores.map((record) => {
                    const isHigh = record.score >= 70;
                    const isPass = record.score >= 60;
                    const scoreColor = isHigh 
                      ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800" 
                      : isPass 
                        ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800"
                        : "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800";

                    return (
                      <tr key={record.attemptId} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4 font-mono text-[10px] text-slate-500 font-bold truncate max-w-[140px]" title={record.attemptId}>
                          {record.attemptId}
                        </td>
                        <td className="py-3 px-4 font-mono text-[10px] text-slate-400 whitespace-nowrap">
                          {record.timestamp}
                        </td>
                        <td className="py-3 px-4">
                          <p className="font-bold text-slate-800 dark:text-slate-200 text-xs">{record.studentName}</p>
                          <p className="text-[10px] text-slate-400 font-mono truncate max-w-[180px]">{record.studentEmail}</p>
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-semibold text-slate-700 dark:text-slate-300 block">{record.moduleName}</span>
                          <span className="text-[9px] font-mono text-slate-400 uppercase">ID: {record.moduleId}</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`inline-block font-mono font-black text-xs px-2.5 py-1 rounded-lg border ${scoreColor}`}>
                            {record.score.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center font-mono text-[11px] text-slate-600 dark:text-slate-400">
                          {record.questionsAttempted} items
                        </td>
                        <td className="py-3 px-4 text-center font-mono text-[11px] text-slate-500">
                          {record.timeSpentSec}s
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                            isPass
                              ? "bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300"
                              : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                          }`}>
                            {isPass ? <Check className="h-2.5 w-2.5" /> : null}
                            {record.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {filteredScores.length > 0 && (
            <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-slate-500 text-[11px]">
                <span>Rows per page:</span>
                <select
                  value={rowsPerPage}
                  onChange={(e) => setRowsPerPage(Number(e.target.value))}
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2 py-1 text-xs"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="p-1 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-30"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-1 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-30"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 2: Cognitive Questions Bank Table */}
      {/* ------------------------------------------------------------- */}
      {subTab === "questionsBank" && (
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>Active Cognitive Stimuli Dataset</span>
                <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded font-bold uppercase">
                  cognitive_questions_bank.csv
                </span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Showing {filteredQuestions.length === 0 ? 0 : startIndex + 1}–{endIndex} of {filteredQuestions.length} stimuli items.
              </p>
            </div>
            
            <button
              onClick={() => handleDownload("questions-bank", "cognitive_questions_bank.csv")}
              className="text-xs text-emerald-600 dark:text-emerald-400 font-bold hover:underline flex items-center gap-1"
            >
              <Download className="h-3 w-3" /> Download CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-950/40 text-[10px] uppercase font-mono text-slate-400 border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-bold">Module</th>
                  <th className="py-3 px-4 font-bold">Question ID</th>
                  <th className="py-3 px-4 font-bold">Type</th>
                  <th className="py-3 px-4 font-bold">Stimulus Prompt</th>
                  <th className="py-3 px-4 font-bold">Target Answer</th>
                  <th className="py-3 px-4 font-bold">Paradigm Hint</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {paginatedQuestions.map((q) => (
                  <tr key={q.questionId} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">{q.moduleName}</span>
                      <span className="text-[9px] font-mono text-slate-400 uppercase">ID: {q.moduleId}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500 font-semibold">
                      {q.questionId}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[9px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {q.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 max-w-md">
                      <p className="font-semibold text-slate-800 dark:text-slate-200 text-xs leading-normal">{q.prompt}</p>
                      {q.options && (
                        <p className="text-[10px] text-slate-400 font-mono mt-1 truncate" title={q.options}>
                          Options: {q.options}
                        </p>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-600 dark:text-emerald-400 text-xs">
                      {q.correctAnswer}
                    </td>
                    <td className="py-3 px-4 text-[10px] text-slate-400 max-w-xs">
                      {q.hint || q.story || "Standard paradigm"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredQuestions.length > 0 && (
            <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
              <span className="text-[11px] text-slate-400">Page {page} of {totalPages}</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="p-1 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-30"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-1 rounded border border-slate-200 dark:border-slate-700 disabled:opacity-30"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 3: Module Benchmarks & Psychometrics Table */}
      {/* ------------------------------------------------------------- */}
      {subTab === "moduleBenchmarks" && (
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>Real-Time Module Benchmarks & Calibration Analytics</span>
                <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded font-bold uppercase">
                  module_benchmarks_analytics.csv
                </span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Aggregated dynamically from real candidate submissions across all 10 cognitive pillars.
              </p>
            </div>
            
            <button
              onClick={() => handleDownload("module-benchmarks", "module_benchmarks_analytics.csv")}
              className="text-xs text-emerald-600 dark:text-emerald-400 font-bold hover:underline flex items-center gap-1"
            >
              <Download className="h-3 w-3" /> Download CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-950/40 text-[10px] uppercase font-mono text-slate-400 border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-bold">Module Pillar</th>
                  <th className="py-3 px-4 font-bold">Cognitive Domain</th>
                  <th className="py-3 px-4 font-bold text-center">Total Attempts</th>
                  <th className="py-3 px-4 font-bold text-center">Unique Students</th>
                  <th className="py-3 px-4 font-bold text-center">Avg Score</th>
                  <th className="py-3 px-4 font-bold text-center">Max / Min</th>
                  <th className="py-3 px-4 font-bold text-center">Pass Rate (&gt;=60%)</th>
                  <th className="py-3 px-4 font-bold text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {paginatedBenchmarks.map((b) => (
                  <tr key={b.moduleId} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-800 dark:text-slate-200 text-xs block">{b.moduleName}</span>
                      <span className="text-[9px] font-mono text-slate-400 uppercase">ID: {b.moduleId} • Time: {b.targetTime}</span>
                    </td>
                    <td className="py-3 px-4 text-xs text-slate-600 dark:text-slate-400 max-w-[200px]">
                      {b.category}
                    </td>
                    <td className="py-3 px-4 text-center font-mono font-bold text-xs text-slate-800 dark:text-slate-200">
                      {b.totalAttempts}
                    </td>
                    <td className="py-3 px-4 text-center font-mono text-xs text-slate-600 dark:text-slate-400">
                      {b.uniqueStudents}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex flex-col items-center">
                        <span className="font-mono font-black text-xs text-slate-800 dark:text-slate-200">
                          {b.averageScore.toFixed(1)}%
                        </span>
                        <div className="w-16 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden mt-1">
                          <div 
                            className="h-full bg-emerald-500 rounded-full"
                            style={{ width: `${Math.min(100, b.averageScore)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center font-mono text-[10px] text-slate-500">
                      {b.highestScore.toFixed(0)}% / {b.lowestScore.toFixed(0)}%
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400">
                        {b.passRate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        b.totalAttempts > 0 
                          ? "bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-500"
                      }`}>
                        {b.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};
