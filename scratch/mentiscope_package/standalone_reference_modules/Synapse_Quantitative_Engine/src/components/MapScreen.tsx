import React, { useState, useEffect, useRef } from 'react';
import { ScreenId, StudentProfile } from '../types';
import { 
  Map, 
  ListTodo, 
  BarChart3, 
  Database, 
  ShieldAlert, 
  Cpu, 
  Lock, 
  Unlock, 
  Play, 
  ChevronRight, 
  Award, 
  Zap, 
  Clock, 
  Target as TargetIcon, 
  Users,
  Rocket,
  Microscope,
  Brain,
  Shield,
  AlertTriangle,
  Settings,
  Terminal,
  HelpCircle,
  Home
} from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';

export const MapScreen: React.FC = () => {
  const { profile, handleNavigate, completedScreens, logEvent } = useAssessment();
  const onSelectNode = handleNavigate;
  const onLog = logEvent;
  const [activeTab, setActiveTab] = useState<'map' | 'tasks' | 'stats' | 'logger'>('map');
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [hoveredSector, setHoveredSector] = useState<string | null>(null);
  
  // Real-time rolling tactical system logs
  const [logs, setLogs] = useState<string[]>([
    '> [LOG] Drone Unit-7 initialized.',
    '> [SCAN] Sector Alpha breach detected.',
    '> [INTEL] Level 1 protocols bypassed.',
    '> [WARN] Intrusion detected in Sector 2.',
    '> [LOG] Routing path to Neural Core...'
  ]);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // Periodic simulated realistic log generation
  useEffect(() => {
    const logPool = [
      '> [LOG] Synapse calibration complete.',
      '> [INTEL] Quantum tunnel stability at 99.8%.',
      '> [SCAN] Sub-neural pathways optimization ready.',
      '> [WARN] Cognitive latency spiked to 14ms.',
      '> [LOG] Synchronizing student status with academy.',
      '> [INTEL] Level 3 encryption protocol engaged.',
      '> [SCAN] Analytical matrix running core tests...',
      '> [LOG] Adaptive item response database compiled.',
      '> [LOG] Sector Alpha node status: ONLINE.',
      '> [WARN] Stress equilibrium fluctuation corrected.'
    ];

    const interval = setInterval(() => {
      const randomLog = logPool[Math.floor(Math.random() * logPool.length)];
      const timestamp = new Date().toLocaleTimeString();
      setLogs(prev => [...prev, `${randomLog} (${timestamp})`].slice(-15));
    }, 4500);

    return () => clearInterval(interval);
  }, []);

  // Map sector definitions that match screenshots 3 & 4
  const sectors = [
    {
      id: 'sector-alpha',
      name: 'Sector Alpha',
      missionCode: 'MISSION 01: RECURSIVE REPAIR',
      icon: Rocket,
      color: 'emerald',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      textColor: 'text-emerald-400',
      glowClass: 'shadow-[0_0_15px_rgba(16,185,129,0.3)]',
      glowingBg: 'bg-emerald-400',
      gridX: 50,
      gridY: 10,
      challenges: [
        { id: 'pattern-bot' as ScreenId, name: 'PatternBot Repair', desc: 'Recursive progression sequence solver' },
        { id: 'decision-core' as ScreenId, name: 'Decision Core Balance', desc: 'Calibrate reactor flow variables' }
      ]
    },
    {
      id: 'cryo-lab',
      name: 'Cryo Lab',
      missionCode: '02: Capacity Planning',
      icon: Microscope,
      color: 'cyan',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
      textColor: 'text-cyan-400',
      glowClass: 'shadow-[0_0_15px_rgba(6,182,212,0.3)]',
      glowingBg: 'bg-cyan-400',
      gridX: 75,
      gridY: 32,
      challenges: [
        { id: 'solver-capacity' as ScreenId, name: 'Capacity Planning', desc: 'Reactor core capacity allocation' }
      ]
    },
    {
      id: 'neural-core',
      name: 'Neural Core',
      missionCode: '03: Dual Dashboard',
      icon: Brain,
      color: 'purple',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30',
      textColor: 'text-purple-400',
      glowClass: 'shadow-[0_0_15px_rgba(168,85,247,0.3)]',
      glowingBg: 'bg-purple-500',
      gridX: 25,
      gridY: 52,
      challenges: [
        { id: 'neural-core' as ScreenId, name: 'Neural Core Repair', desc: 'SVG synapse logic path balancing' },
        { id: 'solver-route' as ScreenId, name: 'SolverBot Navigation', desc: 'Path routing spatial optimization' }
      ]
    },
    {
      id: 'vault-s9',
      name: 'Vault S-9',
      missionCode: '04: Resource Allocation',
      icon: Shield,
      color: 'amber',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      textColor: 'text-amber-400',
      glowClass: 'shadow-[0_0_15px_rgba(245,158,11,0.3)]',
      glowingBg: 'bg-amber-500',
      gridX: 75,
      gridY: 72,
      challenges: [
        { id: 'solver-resource' as ScreenId, name: 'Resource balancing', desc: 'Grid workload optimization' },
        { id: 'vision-bot' as ScreenId, name: 'VisionBot Attention', desc: 'Split attention real-time audit' }
      ]
    },
    {
      id: 'the-singularity',
      name: 'The Singularity',
      missionCode: 'MISSION 05: PROFILE SUMMARY',
      icon: AlertTriangle,
      color: 'rose',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/30',
      textColor: 'text-rose-400',
      glowClass: 'shadow-[0_0_20px_rgba(244,63,94,0.4)]',
      glowingBg: 'bg-rose-500',
      gridX: 50,
      gridY: 92,
      challenges: [
        { id: 'cognitive-analytics' as ScreenId, name: 'Wave Oscilloscope Tuning', desc: 'Fine-tune signal frequency limits' },
        { id: 'cognitive-profile' as ScreenId, name: 'Cognitive Profile', desc: 'Generate complete diagnostic signature' }
      ]
    }
  ];

  const handleChallengeLaunch = (challengeId: ScreenId, challengeName: string) => {
    onLog('Launch Challenge', 'SUCCESS', `Subject initiated challenge: ${challengeName}`, { challengeId });
    onSelectNode(challengeId);
  };

  // Dynamic calculations for Squad metrics panel
  const rawCompletedChallengeCount = completedScreens.filter(
    s => s !== 'splash' && s !== 'intake' && s !== 'map' && s !== 'gq-assessment'
  ).length;
  
  // Cap at 8 to prevent UI layout overflow
  const completedChallengeCount = Math.min(rawCompletedChallengeCount, 8);
  
  const nodesCleared = 12 + completedChallengeCount;
  const progressPercent = Math.min(100, Math.max(20, Math.round((completedChallengeCount / 8) * 100)));
  const rankScore = (8.4 + (profile?.xp || 0) / 1200).toFixed(1);

  return (
    <div className="bg-[#020617] text-slate-100 font-sans flex flex-col h-full relative overflow-hidden select-none">
      
      {/* Top Banner with Profile */}
      <div className="flex flex-col sm:flex-row items-center justify-between border-b border-slate-900 pb-5 mb-6 gap-4 font-mono">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center font-bold text-cyan-400 overflow-hidden shadow-lg">
            {/* Cool retro geometric avatar placeholder */}
            <svg viewBox="0 0 40 40" className="w-8 h-8 opacity-80">
              <rect x="10" y="10" width="20" height="20" fill="none" stroke="#22d3ee" strokeWidth="2" />
              <line x1="10" y1="10" x2="30" y2="30" stroke="#22d3ee" strokeWidth="1" />
              <circle cx="20" cy="20" r="4" fill="#22d3ee" />
            </svg>
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-200 tracking-wider">
              {profile?.fullName || 'GUEST_OPERATIVE'}
            </h2>
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-bold uppercase">
              <span className="text-cyan-400">LVL {profile?.level || 1}</span>
              <span>•</span>
              <span>XP {profile?.xp || 0}</span>
              <span>•</span>
              <span className="text-violet-400">{profile?.tier || 'Adept'}</span>
            </div>
          </div>
        </div>

        {/* Real-time System Load Status & Go to Home */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-4 bg-[#070b13] border border-slate-900 px-4 py-2.5 rounded-xl text-[10px]">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]"></span>
              <span className="text-emerald-400 font-black tracking-widest">SYNAPSE_LINK_ESTABLISHED</span>
            </div>
            <div className="text-slate-800">|</div>
            <div className="flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400 font-bold uppercase">COMPLETED: {completedChallengeCount}/8 CHALLENGES</span>
            </div>
          </div>

          <button
            onClick={() => {
              onLog('Return to Home Splash clicked', 'INFO', 'Operative initiated navigation to main portal splash.');
              onSelectNode('splash');
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#070b13] hover:bg-slate-900 border border-slate-900 hover:border-cyan-500/40 text-slate-400 hover:text-cyan-400 rounded-xl transition text-[10px] font-black tracking-wider uppercase cursor-pointer"
          >
            <Home className="w-3.5 h-3.5" />
            <span>Go To Home</span>
          </button>
        </div>
      </div>

      {/* Main Container Content based on Tab Selection */}
      <div className="flex-1 min-h-[500px] relative">
        
        {/* TAB 1: INTERACTIVE TACTICAL MAP SCREENS */}
        {activeTab === 'map' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-stretch">
              
              {/* COLUMN 1, 2, 3: MASSIVE INTERACTIVE TACTICAL MAP PATHWAY */}
              <div className="lg:col-span-3 h-[550px] border border-slate-900 rounded-2xl relative overflow-visible p-4 bg-[#050811] shadow-2xl flex flex-col">
                
                {/* Background Repeat Diamond Grid Pattern representing carbon grid */}
                <div 
                  className="absolute inset-0 opacity-[0.04] pointer-events-none"
                  style={{
                    backgroundImage: `
                      radial-gradient(circle, #22d3ee 1px, transparent 1px),
                      linear-gradient(45deg, transparent 49%, #22d3ee 49%, #22d3ee 51%, transparent 51%),
                      linear-gradient(-45deg, transparent 49%, #22d3ee 49%, #22d3ee 51%, transparent 51%)
                    `,
                    backgroundSize: '24px 24px, 48px 48px, 48px 48px',
                    backgroundPosition: '0 0, 0 0, 0 0'
                  }}
                />

                {/* Sector Labels background */}
                <div className="absolute top-4 left-6 text-slate-800 font-mono text-[9px] tracking-[0.25em] uppercase font-bold select-none">
                  SECTOR ALPHA // SYNAPSE ANTECHAMBER
                </div>
                <div className="absolute bottom-4 right-6 text-slate-800 font-mono text-[9px] tracking-[0.25em] uppercase font-bold select-none">
                  SECTOR OMEGA // THE SINGULARITY CORE
                </div>

                {/* The Winding Path Canvas Container */}
                <div className="relative w-full h-[850px] flex flex-col justify-between py-12 overflow-y-auto scrollbar-none rounded-xl">
                  
                  {/* Connecting lines SVG Canvas (Percentage coordinates scale seamlessly) */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="neonPathGlow" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#10b981" />
                        <stop offset="25%" stopColor="#06b6d4" />
                        <stop offset="50%" stopColor="#a855f7" />
                        <stop offset="75%" stopColor="#f59e0b" />
                        <stop offset="100%" stopColor="#f43f5e" />
                      </linearGradient>
                    </defs>

                    {/* High fidelity curved neon segmented trajectory */}
                    <path 
                      d="M 50 10 Q 75 22 75 32 T 25 52 T 75 72 T 50 92" 
                      fill="none" 
                      stroke="url(#neonPathGlow)" 
                      strokeWidth="1.2" 
                      strokeDasharray="2 1.5" 
                      className="opacity-70 animate-pulse"
                    />
                  </svg>

                  {/* Alternating Winding Nodes */}
                  {sectors.map((sec) => {
                    const IconComponent = sec.icon;
                    const isCompleted = sec.challenges.every(ch => completedScreens.includes(ch.id));
                    const isSelected = selectedSector === sec.id;
                    const isHovered = hoveredSector === sec.id;
                    const isMenuVisible = isSelected || isHovered;

                    // Compute clean menu alignments to avoid edges
                    const alignmentClass = sec.gridX > 60 ? 'right-0' : sec.gridX < 40 ? 'left-0' : 'left-1/2 -translate-x-1/2';

                    return (
                      <div 
                        key={sec.id}
                        style={{ 
                          position: 'absolute', 
                          left: `${sec.gridX}%`, 
                          top: `${sec.gridY}%`,
                          transform: 'translate(-50%, -50%)'
                        }}
                        className="flex flex-col items-center group z-10"
                        onMouseEnter={() => setHoveredSector(sec.id)}
                        onMouseLeave={() => setHoveredSector(null)}
                      >
                        {/* Special Robot Claw SVG above Sector Alpha to match Screenshot 3 */}
                        {sec.id === 'sector-alpha' && (
                          <div className="absolute -top-11 text-cyan-400 flex flex-col items-center select-none pointer-events-none animate-bounce">
                            <svg viewBox="0 0 24 24" className="w-6 h-6 stroke-cyan-400 fill-none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 2v8M8 6h8M6 10s1-3 6-3 6 3 6 3M9 14l3-3 3 3" />
                            </svg>
                            <div className="w-[1px] h-2 bg-cyan-400/40"></div>
                          </div>
                        )}

                        {/* Glowing Ring Background */}
                        <div className={`absolute -inset-4 rounded-full blur-lg transition-all duration-300 ${sec.bgColor} ${sec.glowClass} group-hover:scale-125`} />

                        {/* Tactical Node Trigger */}
                        <button
                          onClick={() => {
                            setSelectedSector(isSelected ? null : sec.id);
                            onLog('Inspected Sector Node', 'INFO', `Operative selected sector: ${sec.name}`);
                          }}
                          className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 border shadow-2xl relative cursor-pointer ${
                            isCompleted
                              ? 'bg-slate-900 border-emerald-400 text-emerald-300 shadow-emerald-950/40'
                              : isSelected || isHovered
                              ? 'bg-slate-900 border-cyan-400 text-cyan-300 scale-105 shadow-[0_0_20px_rgba(34,211,238,0.3)]'
                              : `bg-slate-950 border-slate-800 text-slate-400 hover:border-${sec.color}-400 hover:text-slate-200`
                          }`}
                        >
                          <IconComponent className={`w-6 h-6 ${(isSelected || isHovered) ? 'animate-spin-slow' : ''}`} />

                          {/* Lock / Unlock Mini Indicator Badge */}
                          <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-center text-[9px]">
                            {isCompleted ? (
                              <Unlock className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <Lock className="w-3 h-3 text-slate-500" />
                            )}
                          </div>
                        </button>

                        {/* Info Label Overlay */}
                        <div className="text-center mt-3.5 whitespace-nowrap">
                          <span className={`text-xs font-black uppercase tracking-widest ${sec.textColor} block drop-shadow-[0_0_8px_rgba(255,255,255,0.1)]`}>
                            {sec.name}
                          </span>
                          <span className="text-[8px] font-mono font-bold text-slate-500 uppercase block mt-0.5 tracking-wider">
                            {sec.missionCode}
                          </span>
                        </div>

                        {/* Hover / Selection Interactive Sub-Objective Dropdown */}
                        <div 
                          className={`absolute top-20 w-64 bg-[#090f1d]/98 border-2 border-cyan-500/30 rounded-xl p-3.5 shadow-[0_10px_30px_rgba(0,0,0,0.6)] transition-all duration-300 z-50 font-mono ${alignmentClass} ${
                            isMenuVisible 
                              ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto' 
                              : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'
                          }`}
                        >
                          <div className="text-[9px] text-cyan-400 font-bold uppercase tracking-widest border-b border-slate-900 pb-1.5 mb-2 flex justify-between items-center">
                            <span>COGNITIVE MODULES</span>
                            <span className="text-slate-600 animate-ping">●</span>
                          </div>
                          
                          <div className="space-y-2">
                            {sec.challenges.map((ch) => {
                              const done = completedScreens.includes(ch.id);
                              return (
                                <button
                                  key={ch.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleChallengeLaunch(ch.id, ch.name);
                                  }}
                                  className={`w-full p-2.5 rounded-lg border text-left transition flex items-center justify-between group/btn cursor-pointer ${
                                    done
                                      ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-400'
                                      : 'bg-slate-900/40 border-slate-800 hover:border-cyan-400/40 text-slate-300 hover:bg-slate-900/80'
                                  }`}
                                >
                                  <div className="pr-2">
                                    <span className="text-[10px] font-black block tracking-wide text-slate-100 group-hover/btn:text-cyan-400 transition">{ch.name}</span>
                                    <span className="text-[8px] text-slate-400 block leading-tight mt-0.5">{ch.desc}</span>
                                  </div>
                                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover/btn:translate-x-1 transition flex-shrink-0" />
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    );
                  })}

                </div>

              </div>

              {/* COLUMN 4: RIGHT SQUAD METRICS PANEL */}
              <div className="lg:col-span-1 bg-[#070b13]/60 border border-slate-900 rounded-2xl p-5 flex flex-col font-mono shadow-xl justify-between h-[550px]">
                
                <div className="space-y-5">
                  {/* Panel Title Header */}
                  <div className="flex items-center justify-between border-b border-slate-900 pb-3">
                    <h3 className="text-[11px] font-black uppercase tracking-[0.2em] text-cyan-400 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-cyan-400" />
                      <span>SQUAD_METRICS</span>
                    </h3>
                    <span className="text-[9px] text-slate-600 font-bold">SUB_SEC_09</span>
                  </div>

                  {/* Progress Bar Area */}
                  <div className="space-y-2 bg-[#050811] p-3.5 border border-slate-900 rounded-xl">
                    <div className="flex justify-between items-center text-[10px] font-bold text-slate-400">
                      <span>MISSION PROGRESS</span>
                      <span className="text-cyan-400 font-black">{progressPercent}%</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-900/60 p-0.5">
                      <div 
                        className="h-full bg-cyan-400 rounded-full shadow-[0_0_8px_#22d3ee] transition-all duration-500"
                        style={{ width: `${progressPercent}%` }}
                      />
                    </div>
                  </div>

                  {/* Grid stats */}
                  <div className="grid grid-cols-2 gap-3">
                    {/* Nodes Cleared Box */}
                    <div className="bg-[#050811] border border-slate-900 p-3 rounded-xl flex flex-col items-center justify-center text-center">
                      <span className="text-xl font-black text-cyan-400 tracking-wider">
                        {nodesCleared}
                      </span>
                      <span className="text-[8px] text-slate-500 font-bold uppercase mt-1 tracking-wide leading-tight">
                        Nodes Cleared
                      </span>
                    </div>

                    {/* Rank Score Box */}
                    <div className="bg-[#050811] border border-slate-900 p-3 rounded-xl flex flex-col items-center justify-center text-center">
                      <span className="text-xl font-black text-emerald-400 tracking-wider">
                        {rankScore}
                      </span>
                      <span className="text-[8px] text-slate-500 font-bold uppercase mt-1 tracking-wide leading-tight">
                        Rank Score
                      </span>
                    </div>
                  </div>

                  {/* Mini instruction notes */}
                  <div className="p-3 bg-cyan-950/10 border border-cyan-800/10 rounded-xl">
                    <div className="flex items-start gap-2">
                      <HelpCircle className="w-4 h-4 text-cyan-400/80 mt-0.5 flex-shrink-0" />
                      <span className="text-[9px] text-slate-400 leading-normal">
                        Select or hover over any node on the central trajectory map to reveal and start adaptive sub-challenges.
                      </span>
                    </div>
                  </div>
                </div>

                {/* Secure synced label */}
                <div className="border-t border-slate-900 pt-3 text-[9px] text-slate-600 font-bold flex justify-between items-center">
                  <span>SEC_CHANNEL: SYNCED</span>
                  <span>LATENCY: 12ms</span>
                </div>

              </div>

            </div>

            {/* HORIZONTAL WIDE SYSTEM LOGS TERMINAL PANEL AT THE BOTTOM */}
            <div className="bg-[#070b13]/60 border border-slate-900 rounded-2xl p-4 flex flex-col font-mono shadow-xl gap-3">
              <div className="flex items-center justify-between border-b border-slate-900 pb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                  <h3 className="text-[11px] font-black uppercase tracking-[0.2em] text-cyan-400">
                    REAL-TIME SYSTEM_LOGS_V3.0 // COMMUNICATIONS DEVIATION DEPLOYMENT
                  </h3>
                </div>
                <span className="text-[9px] text-slate-500 font-bold">MONITOR_CHANNEL: ACTIVE_SECURE</span>
              </div>

              {/* Multi-column Grid Stream representation of logs for wide look */}
              <div ref={logsContainerRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-1.5 h-20 overflow-y-auto pr-1 scrollbar-none text-[10px] text-slate-400 leading-normal">
                {logs.map((log, index) => {
                  const isWarn = log.includes('[WARN]');
                  const isScan = log.includes('[SCAN]');
                  const isIntel = log.includes('[INTEL]');
                  
                  let textColor = 'text-cyan-500/80';
                  if (isWarn) textColor = 'text-rose-400/90';
                  else if (isScan) textColor = 'text-amber-400/80';
                  else if (isIntel) textColor = 'text-violet-400/80';

                  return (
                    <div key={index} className="flex items-center gap-2 border-b border-slate-950/40 pb-0.5">
                      <span className="text-slate-600 text-[8px] font-mono font-bold uppercase select-none">STREAM_{index+1}:</span>
                      <p className={`${textColor} break-all font-mono truncate`}>
                        {log}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TASKS TAB Preserving original task functionality */}
        {activeTab === 'tasks' && (
          <div className="space-y-4 p-2 animate-fade-in font-mono">
            <h3 className="text-md font-bold text-cyan-400 tracking-wide uppercase">ACTIVE ACADEMY OBJECTIVES</h3>
            <p className="text-xs text-slate-400">Complete all modules to finalize your diagnostic signature run.</p>

            {/* Prominent Gq Adaptive Assessment Banner */}
            <div className="bg-gradient-to-r from-cyan-950/40 via-slate-900 to-violet-950/40 border-2 border-cyan-500/30 rounded-2xl p-5 mt-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative overflow-hidden shadow-cyan-950/30 shadow-lg">
              <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>
              <div className="space-y-1.5 relative z-10">
                <span className="text-[9px] font-bold text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                  CRITICAL MILESTONE // GQ ADAPTIVE ENGINE
                </span>
                <h4 className="text-base font-black text-slate-100 flex items-center gap-2">
                  OFFICIAL ADAPTIVE QUANTITATIVE RUN
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed max-w-xl">
                  Launches the continuous 8-node Item Response calibration loop. Adapts difficulty based on speed, hints, and accuracy to generate your detailed diagnostic dashboard.
                </p>
              </div>
              <button
                onClick={() => {
                  onLog('Launch Adaptive assessment clicked', 'SUCCESS', 'Official assessment execution sequence armed.');
                  onSelectNode('gq-assessment');
                }}
                className="px-6 py-3.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase rounded-xl border border-cyan-300 shadow-xl shadow-cyan-500/10 transition-all flex items-center gap-2 flex-shrink-0 animate-pulse relative z-10 cursor-pointer"
              >
                <Zap className="w-4 h-4 fill-current" />
                <span>LAUNCH Gq ASSESSMENT</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              {sectors.flatMap(sec => sec.challenges).map((ch) => {
                const done = completedScreens.includes(ch.id);
                return (
                  <div key={ch.id} className="bg-[#070b13] border border-slate-900 rounded-xl p-4 flex justify-between items-center hover:border-slate-800 transition">
                    <div>
                      <span className="text-[8px] text-slate-500 uppercase">SYS_NODE_CHALLENGE</span>
                      <h4 className="text-sm font-bold text-slate-200 mt-0.5">{ch.name}</h4>
                      <p className="text-xs text-slate-400 mt-1">{ch.desc}</p>
                    </div>
                    <button
                      onClick={() => handleChallengeLaunch(ch.id, ch.name)}
                      className={`px-3 py-1.5 rounded font-bold text-xs transition flex items-center gap-1.5 cursor-pointer ${
                        done
                          ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                          : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950'
                      }`}
                    >
                      {done ? 'RE-RUN' : 'DEPLOY'}
                      <Play className="w-3 h-3 fill-current" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 3: STATS PRESERVATION */}
        {activeTab === 'stats' && (
          <div className="space-y-6 p-2 animate-fade-in font-mono">
            <h3 className="text-sm font-bold text-cyan-400 tracking-wider uppercase">COGNITIVE DOMAIN MASTERY STATUS</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-4">
                <span className="text-xs text-slate-500 block">ADAPTIVITY XP</span>
                <span className="text-2xl font-black text-cyan-400">{profile?.xp || 150} pts</span>
              </div>
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-4">
                <span className="text-xs text-slate-500 block">COMPLETION RATE</span>
                <span className="text-2xl font-black text-emerald-400">
                  {Math.round((completedChallengeCount / 8) * 100)}%
                </span>
              </div>
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-4">
                <span className="text-xs text-slate-500 block">CURRENT SECTOR</span>
                <span className="text-2xl font-black text-purple-400">ALPHA-9</span>
              </div>
            </div>

            {/* Custom SVG Bar Chart for Cognitive domains */}
            <div className="bg-[#070b13] border border-slate-900 rounded-xl p-5">
              <h4 className="text-xs font-bold text-slate-400 mb-4 uppercase">Projected Mastery Scores</h4>
              <div className="space-y-4">
                {[
                  { domain: 'Logical Reasoning', value: 85, color: 'bg-cyan-400 shadow-[0_0_8px_#22d3ee]' },
                  { domain: 'Algorithmic Optimization', value: 72, color: 'bg-purple-500 shadow-[0_0_8px_#a855f7]' },
                  { domain: 'Attention & Focus', value: 91, color: 'bg-emerald-400 shadow-[0_0_8px_#34d399]' },
                ].map((d) => (
                  <div key={d.domain}>
                    <div className="flex justify-between text-xs text-slate-300 mb-1">
                      <span>{d.domain}</span>
                      <span className="font-bold">{d.value}%</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-900/60">
                      <div className={`h-full ${d.color}`} style={{ width: `${d.value}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: LOGGER DIAGNOSTICS */}
        {activeTab === 'logger' && (
          <div className="p-2 space-y-4 animate-fade-in font-mono">
            <h3 className="text-sm font-bold text-cyan-400 tracking-wider uppercase">SYSTEM INTEGRATION DIAGNOSTICS</h3>
            <p className="text-xs text-slate-400">Metric streams from active gaming variables to diagnostic models.</p>
            <div className="bg-slate-950 border border-slate-900 rounded-xl p-4 text-[11px] text-cyan-500 space-y-2 h-[300px] overflow-y-auto leading-relaxed">
              <p className="text-slate-500">[04:41:02] INITIALIZING COGNITIVE INTERACTIVE PORTAL...</p>
              <p className="text-slate-500">[04:42:01] IDENTIFYING STUDENT ADAPTIVE SIGNATURES...</p>
              <p className="text-emerald-400">✔ [04:43:05] SECURE METRIC WEBSOCKET HANDSHAKE CONNECTED</p>
              <p className="text-cyan-400">ℹ [04:44:12] ADAPTIVE COGNITIVE VECTOR STATUS: STANDBY</p>
              <p className="text-purple-400">ℹ [04:46:01] SECTORS ENCRYPTED & LOCALSTORAGE PIPELINE ARMED</p>
              <p className="text-amber-400">ℹ [04:48:19] LOCAL GAME ENGINE LINKED TO TEACHER AUDITING LOGS</p>
            </div>
          </div>
        )}

      </div>

      {/* Elegant Cyberpunk Bottom Tab Bar Navigator matching Screenshot 3 & 4 */}
      <div className="grid grid-cols-4 bg-[#070b13] border border-slate-900 rounded-xl p-1.5 mt-6 text-center text-xs font-mono">
        <button
          onClick={() => setActiveTab('map')}
          className={`py-2 rounded-lg transition flex flex-col items-center justify-center gap-1 font-bold ${
            activeTab === 'map'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Map className="w-4 h-4" />
          <span className="text-[10px] tracking-wide uppercase">Map</span>
        </button>

        <button
          onClick={() => setActiveTab('tasks')}
          className={`py-2 rounded-lg transition flex flex-col items-center justify-center gap-1 font-bold ${
            activeTab === 'tasks'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <ListTodo className="w-4 h-4" />
          <span className="text-[10px] tracking-wide uppercase">Tasks</span>
        </button>

        <button
          onClick={() => setActiveTab('stats')}
          className={`py-2 rounded-lg transition flex flex-col items-center justify-center gap-1 font-bold ${
            activeTab === 'stats'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span className="text-[10px] tracking-wide uppercase">Stats</span>
        </button>

        <button
          onClick={() => setActiveTab('logger')}
          className={`py-2 rounded-lg transition flex flex-col items-center justify-center gap-1 font-bold ${
            activeTab === 'logger'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Database className="w-4 h-4" />
          <span className="text-[10px] tracking-wide uppercase">Logger</span>
        </button>
      </div>

    </div>
  );
};
