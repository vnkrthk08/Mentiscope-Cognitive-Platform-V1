import React, { useState } from "react";
import { User, Question, SystemLog } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { QUESTIONS_DATA } from "../config/questionsData";
import { AnalyticsService } from "../services/analytics/AnalyticsService";
import { ModuleDifficultyChart } from "../components/Charts";
import { 
  Lock, 
  Settings, 
  Activity, 
  Layers, 
  ListOrdered, 
  TrendingUp, 
  CheckSquare, 
  Plus, 
  Trash2, 
  Edit3, 
  ShieldAlert,
  Save,
  Database
} from "lucide-react";

interface InternDashboardProps {
  user: User;
  onNavigate: (page: string) => void;
}

export default function InternDashboard({ user, onNavigate }: InternDashboardProps) {
  // Mock Intern Assignment (Assigned to Module 4: Attention & Cognitive Control)
  const assignedModuleId = "attention";
  const assignedModule = MODULE_CONFIGS.find(m => m.id === assignedModuleId)!;

  // Active Intern Local State
  const [questions, setQuestions] = useState<Question[]>(QUESTIONS_DATA[assignedModuleId] || []);
  const [logs, setLogs] = useState<SystemLog[]>(
    AnalyticsService.getSystemLogs().filter(log => log.details.toLowerCase().includes("attention") || log.user === user.email)
  );

  // Question editing modal states
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [newQuestionText, setNewQuestionText] = useState("");
  const [newQuestionStory, setNewQuestionStory] = useState("");
  const [newQuestionAnswer, setNewQuestionAnswer] = useState("");
  const [newQuestionHint, setNewQuestionHint] = useState("");

  const handleEditQuestionClick = (q: Question) => {
    setEditingQuestion(q);
    setNewQuestionText(q.text);
    setNewQuestionStory(q.story || "");
    setNewQuestionAnswer(q.correctAnswer || "");
    setNewQuestionHint(q.hint || "");
  };

  const handleSaveQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingQuestion) return;

    const updated = questions.map(q => {
      if (q.id === editingQuestion.id) {
        return {
          ...q,
          text: newQuestionText,
          story: newQuestionStory,
          correctAnswer: newQuestionAnswer,
          hint: newQuestionHint
        };
      }
      return q;
    });

    setQuestions(updated);
    setEditingQuestion(null);

    // Append log
    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Modified Question Parameters",
      status: "success",
      details: `Updated question parameters for task ID ${editingQuestion.id}`
    };
    setLogs([newLog, ...logs]);
  };

  const handleDeleteQuestion = (id: string) => {
    if (!confirm("Are you sure you want to remove this question from the active research pool?")) return;
    const filtered = questions.filter(q => q.id !== id);
    setQuestions(filtered);

    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Removed Question from Bank",
      status: "warning",
      details: `Deleted task ID ${id} from active question pool`
    };
    setLogs([newLog, ...logs]);
  };

  const handleAddQuestion = () => {
    const newId = `attn-new-${Math.random().toString(36).substring(2, 7)}`;
    const newQ: Question = {
      id: newId,
      text: "New diagnostic Attention stimulus prompt goes here.",
      story: "Attentional Conflict: Respond as fast as possible to verify focus indicators.",
      options: ["Alpha Option", "Beta Option", "Gamma Option", "Delta Option"],
      correctAnswer: "Alpha Option",
      hint: "Select Alpha Option.",
      type: "choice"
    };

    setQuestions([...questions, newQ]);

    const newLog: SystemLog = {
      id: `log_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      user: user.email,
      action: "Added Question to Bank",
      status: "success",
      details: `Appended task ID ${newId} to Attention evaluation bank`
    };
    setLogs([newLog, ...logs]);
  };

  // Performance stats for Recharts
  const filteredPerformanceData = AnalyticsService.getModulePerformanceData().filter(
    item => item.subject.toLowerCase().includes("attention") || item.subject.toLowerCase().includes("focus")
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      
      {/* 1. Header & Restricted Warning */}
      <div className="rounded-3xl border border-amber-100 bg-amber-50/20 p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-amber-600 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-100">
            Assigned Workspace Scope
          </span>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mt-1">
            Intern Terminal: {user.name}
          </h1>
          <p className="text-xs text-slate-500">
            Access Level: Restricted to assigned capsule: <span className="font-semibold text-slate-800">{assignedModule.name}</span>.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600">
          <Lock className="h-4 w-4 text-amber-500" />
          <span>Restricted Sandbox Protocol</span>
        </div>
      </div>

      {/* 2. Grid Dashboard Content */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        
        {/* Left Side: Modules Grid with Locked Badges & Assigned Config */}
        <div className="lg:col-span-4 space-y-8">
          
          {/* Active Assigned Capsule Details */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Layers className="h-4.5 w-4.5 text-blue-600" />
              <span>Assigned Module Settings</span>
            </h2>

            <div className="rounded-xl border border-blue-50 bg-blue-50/20 p-4 space-y-3">
              <div>
                <p className="text-[10px] font-mono font-bold text-blue-500 uppercase">Module Name</p>
                <p className="text-sm font-bold text-slate-800">{assignedModule.name}</p>
              </div>

              <div>
                <p className="text-[10px] font-mono font-bold text-blue-500 uppercase">Description</p>
                <p className="text-xs text-slate-500 leading-relaxed mt-0.5">{assignedModule.description}</p>
              </div>

              <div className="flex items-center justify-between text-xs pt-1.5 border-t border-blue-100/60 text-slate-500">
                <span>Time Limit: {assignedModule.estimatedTime}</span>
                <span className="font-mono text-blue-600 bg-blue-50 px-1.5 rounded text-[10px] font-bold uppercase">
                  ACTIVE_REST_API
                </span>
              </div>
            </div>

            {/* Other Locked Modules List */}
            <div className="space-y-2 pt-2">
              <p className="text-[10px] font-mono font-bold text-slate-400 uppercase">Other Research Modules (Locked)</p>
              
              {MODULE_CONFIGS.filter(m => m.id !== assignedModuleId).map(m => (
                <div key={m.id} className="flex items-center justify-between p-2.5 rounded-xl border border-slate-100 bg-slate-50 text-xs text-slate-400">
                  <span className="truncate">{m.name}</span>
                  <Lock className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                </div>
              ))}
            </div>
          </div>

          {/* Filtered Diagnostic Metrics */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <TrendingUp className="h-4.5 w-4.5 text-slate-500" />
              <span>Performance Indicator</span>
            </h3>

            <div className="space-y-4 text-xs">
              <div className="rounded-xl bg-slate-50 border border-slate-100 p-3.5 space-y-1.5">
                <div className="flex items-center justify-between text-slate-500">
                  <span>Average Score Baseline</span>
                  <span className="font-bold text-blue-600">78%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
                  <div className="h-2 rounded-full bg-blue-600" style={{ width: "78%" }} />
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 border border-slate-100 p-3.5 space-y-1.5">
                <div className="flex items-center justify-between text-slate-500">
                  <span>Relative Task Difficulty</span>
                  <span className="font-bold text-amber-500">55%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
                  <div className="h-2 rounded-full bg-amber-500" style={{ width: "55%" }} />
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Right Side: Active Question Bank Manager & Logs */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Question Bank Manager Card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">Manage Stimulus Question Bank</h2>
                <p className="text-xs text-slate-400">Configure visual shapes, colors, and choice options for active candidate sessions.</p>
              </div>

              <button
                onClick={handleAddQuestion}
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Question</span>
              </button>
            </div>

            {/* Editable Question list */}
            <div className="space-y-4 pt-2">
              {questions.map((q, idx) => (
                <div 
                  key={q.id}
                  className="rounded-xl border border-slate-200 bg-white p-4.5 space-y-3 transition-colors hover:border-slate-300"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase bg-slate-100 px-1.5 rounded">
                      ID: {q.id}
                    </span>
                    
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleEditQuestionClick(q)}
                        className="p-1 rounded text-blue-600 hover:bg-blue-50"
                        title="Edit question text and hint"
                      >
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteQuestion(q.id)}
                        className="p-1 rounded text-red-600 hover:bg-red-50"
                        title="Delete question"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-slate-800 leading-tight">
                      Q{idx + 1}: {q.text}
                    </p>
                    {q.story && (
                      <p className="text-[11px] text-slate-400 leading-relaxed mt-1">
                        Context: {q.story}
                      </p>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-1.5 text-[10px]">
                    <span className="font-semibold text-slate-400 bg-slate-50 border border-slate-100 px-1.5 py-0.5 rounded">
                      Correct Answer: {q.correctAnswer}
                    </span>
                    {q.hint && (
                      <span className="font-semibold text-amber-600 bg-amber-50/50 border border-amber-100 px-1.5 py-0.5 rounded">
                        Hint: {q.hint}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Filtered Assessment Attempts Logs */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-1.5">
              <Database className="h-4.5 w-4.5 text-blue-600" />
              <span>Assigned Module Logs</span>
            </h2>

            <div className="divide-y divide-slate-100 font-mono text-[11px] text-slate-500 overflow-x-auto">
              {logs.map((log) => (
                <div key={log.id} className="py-2.5 flex items-start justify-between gap-4">
                  <div className="space-y-0.5">
                    <p className="text-slate-800 font-semibold">{log.action}</p>
                    <p className="text-slate-400 text-[10px]">{log.details}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <span className={`inline-block text-[9px] px-1.5 py-0.5 rounded font-bold uppercase mb-0.5 ${
                      log.status === "success" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                    }`}>
                      {log.status}
                    </span>
                    <p className="text-[9px] text-slate-400">{log.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Editing Modal Dialog */}
      {editingQuestion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm">
          <form onSubmit={handleSaveQuestion} className="w-full max-w-lg bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-slate-900">
              Edit Stimulus Parameters: {editingQuestion.id}
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Stimulus Context Story</label>
                <textarea
                  rows={2}
                  value={newQuestionStory}
                  onChange={(e) => setNewQuestionStory(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Stimulus Question Statement</label>
                <textarea
                  rows={3}
                  required
                  value={newQuestionText}
                  onChange={(e) => setNewQuestionText(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Programmed Correct Answer</label>
                <input
                  type="text"
                  required
                  value={newQuestionAnswer}
                  onChange={(e) => setNewQuestionAnswer(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Assistance Hint</label>
                <input
                  type="text"
                  value={newQuestionHint}
                  onChange={(e) => setNewQuestionHint(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex gap-2.5 pt-2 justify-end">
              <button
                type="button"
                onClick={() => setEditingQuestion(null)}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save Changes</span>
              </button>
            </div>
          </form>
        </div>
      )}

    </div>
  );
}
