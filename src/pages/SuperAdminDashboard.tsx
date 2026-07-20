import React, { useState } from "react";
import { User, ModuleConfig, SystemLog } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { AnalyticsService } from "../services/analytics/AnalyticsService";
import { ModuleDifficultyChart } from "../components/Charts";
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
  FileSpreadsheet
} from "lucide-react";

interface SuperAdminDashboardProps {
  user: User;
  onNavigate: (page: string) => void;
}

export default function SuperAdminDashboard({ user, onNavigate }: SuperAdminDashboardProps) {
  // Configurable REST Gateway URLs State
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>(MODULE_CONFIGS);
  const [logs, setLogs] = useState<SystemLog[]>(AnalyticsService.getSystemLogs());
  const [editingModule, setEditingModule] = useState<ModuleConfig | null>(null);
  const [newApiUrl, setNewApiUrl] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

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

  // Analytics datasets
  const difficultyData = AnalyticsService.getModulePerformanceData();

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      
      {/* 1. Metric Overview Panels */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        
        <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-2 shadow-sm">
          <div className="flex items-center gap-2 text-slate-400">
            <Users className="h-4.5 w-4.5" />
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Total Cohort</span>
          </div>
          <p className="text-2xl font-black text-slate-900 font-mono tracking-tight">{totalStudents}</p>
          <p className="text-[10px] text-slate-400">Registered participants</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-2 shadow-sm">
          <div className="flex items-center gap-2 text-slate-400">
            <Cpu className="h-4.5 w-4.5 animate-pulse" />
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Active Tests</span>
          </div>
          <p className="text-2xl font-black text-blue-600 font-mono tracking-tight">{activeSessions}</p>
          <p className="text-[10px] text-blue-500">Live sessions ongoing</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-2 shadow-sm">
          <div className="flex items-center gap-2 text-slate-400">
            <Globe className="h-4.5 w-4.5 text-emerald-500" />
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">API Health</span>
          </div>
          <p className="text-2xl font-black text-emerald-600 font-mono tracking-tight">{apiStatus}</p>
          <p className="text-[10px] text-emerald-500">FastAPI Gateway online</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-2 shadow-sm">
          <div className="flex items-center gap-2 text-slate-400">
            <RefreshCw className="h-4.5 w-4.5" />
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">System Uptime</span>
          </div>
          <p className="text-2xl font-black text-slate-900 font-mono tracking-tight">{systemUptime}</p>
          <p className="text-[10px] text-slate-400">Server instance status</p>
        </div>

      </div>

      {/* 2. Main Dashboard Split Layout */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        
        {/* Left Side: API Router Manager */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* FastAPI Routing endpoints list */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-900">API Gateway Router configurations</h2>
                <span className="text-[9px] font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 font-bold uppercase">
                  Fully API-Driven
                </span>
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
                  className="rounded-xl border border-slate-100 bg-slate-50/50 p-4 space-y-2.5 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800 flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                      M{idx+1}: {mod.name}
                    </span>
                    
                    <button
                      onClick={() => handleEditApiUrl(mod)}
                      className="text-blue-600 hover:underline font-bold text-[11px]"
                    >
                      Update Router Base
                    </button>
                  </div>

                  <div className="bg-slate-950 rounded-lg p-2.5 font-mono text-[10px] text-slate-300 flex items-center justify-between gap-4 overflow-hidden">
                    <span className="truncate text-blue-400">{mod.apiBaseUrl}</span>
                    <span className="text-slate-500 shrink-0 uppercase tracking-wide">POST/GET</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance chart visualizers */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Task Performance Metrics</h2>
              <p className="text-xs text-slate-400">Average failure thresholds and user latency metrics compiled per capsule paradigm.</p>
            </div>

            <div className="border border-slate-100 rounded-2xl bg-slate-50/40 p-4">
              <ModuleDifficultyChart data={difficultyData} />
            </div>
          </div>

        </div>

        {/* Right Side: Audit Logs & System Reset Database controls */}
        <div className="lg:col-span-5 space-y-8">
          
          {/* Systems Database Command Card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Database className="h-4.5 w-4.5 text-blue-600" />
              <span>Diagnostic System Utilities</span>
            </h2>
            <p className="text-xs text-slate-400 leading-normal">
              Quick commands to clean up local sandbox environments during active quality assurance evaluation:
            </p>

            <div className="space-y-2 pt-2 text-xs">
              <button
                onClick={handleFlushDb}
                className="w-full flex items-center justify-between rounded-xl border border-rose-100 bg-rose-50/20 text-rose-800 p-3 hover:bg-rose-50 transition-colors"
              >
                <div className="text-left">
                  <p className="font-bold">Flush Testing Database</p>
                  <p className="text-[10px] text-rose-500/80">Clear and reset active student sessions</p>
                </div>
                <Trash2 className="h-4.5 w-4.5 text-rose-600" />
              </button>

              <button
                onClick={handleExportLogs}
                className="w-full flex items-center justify-between rounded-xl border border-blue-100 bg-blue-50/20 text-blue-800 p-3 hover:bg-blue-50 transition-colors"
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
          <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Terminal className="h-4.5 w-4.5 text-slate-500" />
              <span>Active System Audit Logs</span>
            </h2>

            <div className="divide-y divide-slate-100 font-mono text-[10px] text-slate-500 max-h-[36vh] overflow-y-auto pr-1">
              {logs.map((log) => (
                <div key={log.id} className="py-2.5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-800 text-[11px]">{log.action}</span>
                    <span className={`text-[8px] font-bold px-1.5 rounded uppercase ${
                      log.status === "success" ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"
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

      {/* API Router Editing Modal */}
      {editingModule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm">
          <form onSubmit={handleSaveApiUrl} className="w-full max-w-md bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-slate-900">
              Update Gateway Endpoint Base
            </h3>
            <p className="text-xs text-slate-500">
              Set custom FastAPI server target microservice URL for <span className="font-semibold text-slate-800">{editingModule.name}</span>.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">FastAPI REST Endpoint URL</label>
              <input
                type="url"
                required
                value={newApiUrl}
                onChange={(e) => setNewApiUrl(e.target.value)}
                placeholder="http://fastapi-service/modules/gq"
                className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-blue-500 focus:outline-none font-mono"
              />
            </div>

            <div className="flex gap-2.5 pt-2 justify-end">
              <button
                type="button"
                onClick={() => setEditingModule(null)}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
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

    </div>
  );
}
