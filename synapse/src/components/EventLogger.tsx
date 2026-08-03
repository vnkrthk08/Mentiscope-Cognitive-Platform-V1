import React, { useState } from 'react';
import { AppEvent } from '../types';
import { Terminal, Shield, Cpu, RefreshCw, FileText, CheckCircle2, AlertTriangle, Info, Play } from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';

export const EventLogger: React.FC = () => {
  const { events, handleClearLogs: onClear } = useAssessment();
  const [filter, setFilter] = useState<string>('all');
  const [selectedEvent, setSelectedEvent] = useState<AppEvent | null>(null);

  const filteredEvents = events.filter((ev) => {
    if (filter === 'all') return true;
    return ev.status.toLowerCase() === filter;
  });

  return (
    <div className="bg-slate-950 border border-cyan-500/30 rounded-xl p-6 shadow-xl shadow-cyan-950/20 text-slate-100 font-sans h-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-cyan-400 flex items-center gap-2">
            <Terminal className="w-5 h-5 animate-pulse" />
            SYNAPTIC EVENT TELEMETRY
          </h2>
          <p className="text-xs text-slate-400">Real-time adaptive system interaction log & JSON pipeline</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onClear}
            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 rounded text-xs transition duration-200"
          >
            Purge Logs
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Event Log Feed */}
        <div className="lg:col-span-2 flex flex-col h-[550px] bg-slate-900/60 border border-slate-800 rounded-lg overflow-hidden">
          {/* Filters */}
          <div className="flex gap-2 p-3 bg-slate-900 border-b border-slate-800 text-xs overflow-x-auto">
            {['all', 'success', 'info', 'warning', 'error'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded-full transition-colors uppercase font-mono ${
                  filter === f
                    ? 'bg-cyan-500/20 border border-cyan-500 text-cyan-300 font-bold'
                    : 'bg-slate-800/50 border border-transparent text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* List of events */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-xs">
            {filteredEvents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                <Shield className="w-8 h-8 opacity-40 animate-pulse" />
                <p>No telemetry events detected on this vector</p>
              </div>
            ) : (
              filteredEvents.map((ev) => (
                <div
                  key={ev.id}
                  onClick={() => setSelectedEvent(ev)}
                  className={`p-2.5 rounded border transition-all cursor-pointer flex items-start gap-3 hover:bg-slate-800/60 ${
                    selectedEvent?.id === ev.id
                      ? 'bg-slate-800 border-cyan-500/50 shadow-inner'
                      : 'bg-slate-950/40 border-slate-800/80'
                  }`}
                >
                  <div className="mt-0.5">
                    {ev.status === 'SUCCESS' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {ev.status === 'INFO' && <Info className="w-4 h-4 text-cyan-400" />}
                    {ev.status === 'WARNING' && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                    {ev.status === 'ERROR' && <Shield className="w-4 h-4 text-rose-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 text-[10px] text-slate-500 mb-1">
                      <span className="font-semibold text-slate-400 bg-slate-900 px-1 py-0.5 rounded border border-slate-800">
                        {ev.screen.toUpperCase()}
                      </span>
                      <span>{ev.timestamp}</span>
                    </div>
                    <p className="text-slate-200 font-medium truncate">{ev.action}</p>
                    <p className="text-slate-400 text-[11px] truncate mt-0.5">{ev.details}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right column: JSON Schema Preview & Real-time Metrics */}
        <div className="flex flex-col h-[550px] bg-slate-900/60 border border-slate-800 rounded-lg p-4 overflow-hidden">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2 mb-3 text-sm font-semibold tracking-wide text-cyan-300">
            <Cpu className="w-4 h-4 text-cyan-400" />
            TELEMETRY NODE DATA
          </div>

          {selectedEvent ? (
            <div className="flex-1 flex flex-col min-h-0">
              <div className="text-xs text-slate-400 mb-2 font-mono">
                Selected Event ID: <span className="text-cyan-400 font-bold">{selectedEvent.id.slice(0, 8)}</span>
              </div>
              <div className="flex-1 overflow-y-auto bg-slate-950/80 border border-slate-800/80 rounded p-3 font-mono text-[11px] text-emerald-400 leading-relaxed scrollbar-thin">
                <pre>{JSON.stringify(selectedEvent, null, 2)}</pre>
              </div>
              <div className="mt-3 bg-cyan-500/10 border border-cyan-500/20 rounded p-2.5 text-[11px] text-cyan-300">
                <div className="font-bold flex items-center gap-1 mb-1">
                  <Play className="w-3 h-3 fill-cyan-400 text-cyan-400" /> Active Schema Pipeline
                </div>
                Ready to stream to live MongoDB/SQL clusters via webhook pipeline.
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 p-4">
              <FileText className="w-12 h-12 stroke-[1.2] mb-3 text-cyan-500/30 animate-pulse" />
              <p className="text-xs font-mono">Select an interaction event from the telemetry log to view live JSON payload structure.</p>
            </div>
          )}

          {/* Behavior Statistics block */}
          <div className="mt-4 border-t border-slate-800 pt-3 text-[11px] font-mono">
            <span className="text-slate-400 block mb-1">DUMMY TELEMETRY STATS:</span>
            <div className="grid grid-cols-2 gap-2 text-slate-300">
              <div className="bg-slate-950 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-500 text-[9px] block">TOTAL EVENTS</span>
                <span className="text-cyan-400 font-bold text-sm">{events.length}</span>
              </div>
              <div className="bg-slate-950 p-1.5 rounded border border-slate-800/80">
                <span className="text-slate-500 text-[9px] block">ERRORS ENCOUNTERED</span>
                <span className="text-rose-400 font-bold text-sm">
                  {events.filter((e) => e.status === 'ERROR').length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
