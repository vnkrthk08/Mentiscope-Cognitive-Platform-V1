import React, { useState } from 'react';
import { ScreenId } from '../types';
import { Layers, Menu, X, Landmark, Compass, Brain, Activity, Sliders, Layout, Award, HelpCircle, Shield, Code, ChevronRight, BarChart2, Radio, Database } from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';

export const QuickNavigator: React.FC = () => {
  const { currentScreen, handleNavigate: onNavigate, completedScreens } = useAssessment();
  const [isOpen, setIsOpen] = useState(false);

  const screens: { id: ScreenId; label: string; group: 'Setup' | 'Assess' | 'Analyze' | 'Admin'; icon: any; desc: string }[] = [
    { id: 'splash', label: 'Splash Screen', group: 'Setup', icon: Landmark, desc: 'Intro terminal with load metrics' },
    { id: 'intake', label: 'Student Intake', group: 'Setup', icon: Compass, desc: 'Initialize neural profile identity' },
    { id: 'map', label: 'Mission Map', group: 'Setup', icon: Brain, desc: 'Isometric interactive cognitive paths' },
    
    { id: 'gq-assessment', label: 'Gq Adaptive Assessment', group: 'Assess', icon: Brain, desc: 'Official 8-question item response adaptive loop' },
    { id: 'neural-core', label: 'Neural Core Repair', group: 'Assess', icon: Activity, desc: 'SVG-based synapse logic gate connector' },
    { id: 'pattern-bot', label: 'PatternBot Repair', group: 'Assess', icon: Code, desc: 'Recursive sequence prediction challenge' },
    { id: 'decision-core', label: 'Decision Core Balance', group: 'Assess', icon: Sliders, desc: 'Sliders balancing golden ratios of reactors' },
    { id: 'solver-capacity', label: 'SolverBot Capacity', group: 'Assess', icon: Layout, desc: 'Distributing reactor power demands' },
    { id: 'solver-resource', label: 'SolverBot Resource', group: 'Assess', icon: Layers, desc: 'Power cell configuration for districts' },
    { id: 'solver-route', label: 'SolverBot Route', group: 'Assess', icon: Compass, desc: 'Grid path navigation avoiding obstacle nodes' },
    { id: 'vision-bot', label: 'VisionBot Dashboard', group: 'Assess', icon: Radio, desc: 'Split-attention live metrics dashboard' },
    { id: 'analytics-core', label: 'Analytics Core Wave', group: 'Assess', icon: Activity, desc: 'Oscilloscope sine-wave phase matching' },
    { id: 'success', label: 'Mission Success', group: 'Assess', icon: Award, desc: 'Congratulatory XP & title milestone unlocks' },

    { id: 'cognitive-analytics', label: 'Cognitive Analytics', group: 'Analyze', icon: BarChart2, desc: 'Interactive Radar and trajectories' },
    { id: 'cognitive-profile', label: 'Cognitive Profile', group: 'Analyze', icon: Brain, desc: 'Bot-specific diagnostic report & traits' },
    { id: 'event-logger', label: 'Telemetry Event Log', group: 'Analyze', icon: Database, desc: 'Real-time JSON action log viewer' },
    
    { id: 'item-exposure', label: 'Item Exposure', group: 'Admin', icon: Shield, desc: 'Question frequency heatmap control' },
    { id: 'admin-control', label: 'Admin Mission Control', group: 'Admin', icon: Shield, desc: 'Universal parameter settings console' },
  ];

  const visibleGroups = ['Setup', 'Assess', 'Analyze'];
  if (useAssessment().profile?.role === 'admin') {
    visibleGroups.push('Admin');
  }

  const visibleScreens = screens.filter(s => visibleGroups.includes(s.group));

  return (
    <>
      {/* Floating Button to Open Quick Navigator */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-slate-900 font-mono font-bold text-xs rounded-full shadow-lg shadow-cyan-500/20 transition duration-300 border-2 border-cyan-300 select-none animate-bounce"
        id="quick-nav-btn"
      >
        <Menu className="w-4 h-4 animate-spin-slow" />
        CONSOLE DOCK ({screens.findIndex(s => s.id === currentScreen) + 1}/19)
      </button>

      {/* Slide-out Sidebar Overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex justify-end">
          <div 
            className="w-full max-w-md bg-slate-900 border-l border-cyan-500/30 h-full flex flex-col shadow-2xl animate-slide-in font-sans"
            id="quick-nav-panel"
          >
            {/* Panel Header */}
            <div className="p-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold tracking-widest text-cyan-400 font-mono">SYNAPSE PROTOTYPE ENGINE</h3>
                <p className="text-[10px] text-slate-500">Fast-navigate all 19 target simulation screens</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded border border-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* List of Screens divided by groups */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {visibleGroups.map((grp) => {
                const groupScreens = screens.filter((s) => s.group === grp);
                return (
                  <div key={grp} className="space-y-2">
                    <h4 className="text-[10px] font-bold tracking-widest text-slate-500 uppercase font-mono border-b border-slate-800 pb-1">
                      {grp} MODULES
                    </h4>
                    <div className="grid grid-cols-1 gap-2">
                      {groupScreens.map((s) => {
                        const Icon = s.icon;
                        const isCurrent = currentScreen === s.id;
                        const isCompleted = completedScreens.includes(s.id);
                        
                        return (
                          <button
                            key={s.id}
                            onClick={() => {
                              onNavigate(s.id);
                              setIsOpen(false);
                            }}
                            className={`flex items-start text-left p-2 rounded transition border ${
                              isCurrent
                                ? 'bg-cyan-500/10 border-cyan-500/60 shadow-md shadow-cyan-950/20'
                                : 'bg-slate-950/40 border-slate-800/60 hover:bg-slate-800 hover:border-slate-700'
                            }`}
                          >
                            <div className={`p-2 rounded mt-0.5 mr-3 ${
                              isCurrent 
                                ? 'bg-cyan-500/20 text-cyan-400' 
                                : isCompleted 
                                ? 'bg-emerald-500/10 text-emerald-400' 
                                : 'bg-slate-900 text-slate-500'
                            }`}>
                              <Icon className="w-4 h-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-1">
                                <span className={`text-xs font-semibold ${isCurrent ? 'text-cyan-300 font-bold' : 'text-slate-300'}`}>
                                  {s.label}
                                </span>
                                {isCompleted && (
                                  <span className="text-[9px] bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-1 rounded uppercase font-mono">
                                    Done
                                  </span>
                                )}
                              </div>
                              <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">{s.desc}</p>
                            </div>
                            <ChevronRight className="w-4 h-4 text-slate-600 mt-2 self-start" />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick Stats in Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-950 text-[11px] font-mono text-slate-400 flex items-center justify-between">
              <span>PROTOTYPE INTEGRITY: 100%</span>
              <span className="text-cyan-400">BUILD v3.5-FLASH</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
