import React, { useState, useEffect } from 'react';
import { ScreenId } from '../types';
import { 
  Activity, 
  ShieldCheck, 
  AlertCircle, 
  Play, 
  Check, 
  Zap, 
  RefreshCw, 
  Cpu, 
  Flame, 
  GitMerge, 
  Thermometer, 
  ArrowRight 
} from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';
import { startAssessment, submitAnswer, finishAssessment, getResult } from '../services/assessmentApi';

export const NeuralCoreScreen: React.FC = () => {
  const { currentScreen, handleChallengeComplete: onComplete, logEvent: onLog, profile } = useAssessment();
  const [mode, setMode] = useState<'neural-core' | 'pattern-bot'>(
    (currentScreen === 'pattern-bot') ? 'pattern-bot' : 'neural-core'
  );

  // Backend integration state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questionId, setQuestionId] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [idleTimeMs] = useState(0);

  useEffect(() => {
    // Start an official backend session for standalone challenges
    if (profile) {
      startAssessment(profile.studentId, profile.level, 'GQ01', mode === 'neural-core' ? 'NeuralCore' : 'PatternBot')
        .then(res => {
          setSessionId(res.session_id);
          setQuestionId(res.question.question_id);
          onLog(`${mode} Backend Connected`, 'INFO', `Tracking session: ${res.session_id}`);
        })
        .catch(err => {
          onLog(`${mode} Connection Error`, 'ERROR', err.message);
        });
    }
  }, [profile, onLog, mode]);

  // --- COGNITIVE NEURAL CORE STATE ---
  const [selectedRepoNode, setSelectedRepoNode] = useState<string | null>(null);
  const [stability, setStability] = useState(64);
  const [isRepaired, setIsRepaired] = useState(false);
  const [coreTemp, setCoreTemp] = useState(42);
  const [feedback, setFeedback] = useState('');
  const [isRepairing, setIsRepairing] = useState(false);

  // --- PATTERNBOT SEQUENTIAL STATE ---
  const [selectedSequenceVal, setSelectedSequenceVal] = useState<number | null>(null);
  const [sequenceSuccess, setSequenceSuccess] = useState(false);
  const [sequenceFeedback, setSequenceFeedback] = useState('');

  // Slowly simulate stability falling prior to repair
  useEffect(() => {
    if (isRepaired || mode !== 'neural-core') return;
    const timer = setInterval(() => {
      setStability((prev) => {
        if (prev <= 42) return 42; // floor
        return parseFloat((prev - 0.4).toFixed(1));
      });
    }, 2000);
    return () => clearInterval(timer);
  }, [isRepaired, mode]);

  // Handle repair validation
  const handleRepairInterface = () => {
    if (!selectedRepoNode) {
      setFeedback('ERROR: Select an alignment node from Node Repository first.');
      onLog('Neural Core repair failed', 'WARNING', 'Attempted repair without selected node');
      return;
    }

    setIsRepairing(true);
    setFeedback('PATCH SYSTEM ENGAGED... STABILIZING COGNITIVE RELAYS...');

    setTimeout(() => {
      if (selectedRepoNode === 'NODE_Q') {
        setIsRepaired(true);
        setStability(100);
        setCoreTemp(32); // normal temperature
        setFeedback('CRITICAL ERROR PATCHED! Neural core logic synchronized. Synaptic relay at 100% stability.');
        onLog('Neural Core Gate repaired successfully', 'SUCCESS', 'Operative mapped NODE_Q (47) to the fractured synapse', { selectedRepoNode });
        
        if (sessionId && questionId) {
          submitAnswer({
            session_id: sessionId,
            question_id: questionId,
            response: selectedRepoNode,
            metrics: {
              reaction_time_ms: Date.now() - startTime,
              hover_duration_ms: 0,
              idle_time_ms: idleTimeMs,
              drag_distance: 0,
              answer_changes: 0,
              confidence_score: 5,
              attempt_number: 1,
              difficulty_level: 2,
              module_name: 'NeuralCore',
              hint_used: false
            }
          }).then(() => {
            finishAssessment(sessionId).then(res => {
              getResult(res.assessment_id).then(backendRes => {
                onComplete('neural-core', 450, null, backendRes);
              });
            });
          });
        } else {
          onComplete('neural-core', 450);
        }
      } else {
        setIsRepaired(false);
        setStability((prev) => Math.max(25, Math.round(prev - 12)));
        setCoreTemp((prev) => Math.min(85, prev + 8));
        setFeedback(`CRITICAL LOGIC DEVATION: ${selectedRepoNode} caused logic skew. Synaptic flow disrupted.`);
        onLog('Neural Core repair failed', 'ERROR', `Operative deployed incompatible ${selectedRepoNode}`, { selectedRepoNode });
      }
      setIsRepairing(false);
    }, 1200);
  };

  // --- PATTERNBOT SEQUENCE SUBMIT ---
  const handleVerifySequence = () => {
    if (selectedSequenceVal === null) {
      setSequenceFeedback('Please select a numeric sequence repair candidate.');
      return;
    }

    if (selectedSequenceVal === 63) {
      setSequenceSuccess(true);
      setSequenceFeedback('PATTERN RECOGNITION VALIDATED! Recursive rule [n = 2(n-1) + 1] satisfied.');
      onLog('PatternBot sequence solved', 'SUCCESS', 'User supplied correct recursive sequence value 63', { selectedSequenceVal });
      
      if (sessionId && questionId) {
        submitAnswer({
          session_id: sessionId,
          question_id: questionId,
          response: String(selectedSequenceVal),
          metrics: {
            reaction_time_ms: Date.now() - startTime,
            hover_duration_ms: 0,
            idle_time_ms: idleTimeMs,
            drag_distance: 0,
            answer_changes: 0,
            confidence_score: 5,
            attempt_number: 1,
            difficulty_level: 2,
            module_name: 'PatternBot',
            hint_used: false
          }
        }).then(() => {
          finishAssessment(sessionId).then(res => {
            getResult(res.assessment_id).then(backendRes => {
              onComplete('pattern-bot', 300, null, backendRes);
            });
          });
        });
      } else {
        onComplete('pattern-bot', 300);
      }
    } else {
      setSequenceFeedback(`NOMINAL OUT OF SYNC: Value ${selectedSequenceVal} does not repair the sequence.`);
      onLog('PatternBot sequence failed', 'WARNING', `User selected incorrect value ${selectedSequenceVal}`);
    }
  };

  const handleReset = () => {
    setSelectedRepoNode(null);
    setStability(64);
    setIsRepaired(false);
    setCoreTemp(42);
    setFeedback('');
    setIsRepairing(false);
    setSelectedSequenceVal(null);
    setSequenceSuccess(false);
    setSequenceFeedback('');
  };

  return (
    <div className="bg-[#020617] text-slate-100 font-sans flex flex-col h-full relative overflow-hidden select-none max-w-5xl mx-auto w-full gap-5">
      
      {/* Top High-Tech Indicator Bar */}
      <div className="flex items-center justify-between border-b border-slate-900 pb-4 font-mono text-xs">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_#22d3ee]"></span>
          <span className="text-cyan-400 font-black tracking-widest">MISSION_ID: SYNAPSE_01</span>
        </div>

        {/* Tab Switching controls in center */}
        <div className="flex gap-1 bg-slate-950 p-1 rounded-lg border border-slate-900">
          <button
            onClick={() => {
              setMode('neural-core');
              handleReset();
            }}
            className={`px-4 py-1.5 rounded-md text-[10px] font-black font-mono tracking-widest uppercase transition-all duration-300 ${
              mode === 'neural-core'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_8px_rgba(6,182,212,0.15)]'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            Neural Core
          </button>
          <button
            onClick={() => {
              setMode('pattern-bot');
              handleReset();
            }}
            className={`px-4 py-1.5 rounded-md text-[10px] font-black font-mono tracking-widest uppercase transition-all duration-300 ${
              mode === 'pattern-bot'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_8px_rgba(6,182,212,0.15)]'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            PatternBot Sequence
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">AWARD_SPEC:</span>
          <span className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-2.5 py-0.5 rounded-full font-black tracking-wider text-[10px]">
            +{mode === 'neural-core' ? '450' : '300'} XP
          </span>
        </div>
      </div>

      {/* MODE 1: NEURAL CORE (LOGIC GATE SYNAPSE RELAY) */}
      {mode === 'neural-core' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* LEFT SIDE COLUMN (Span 5) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            
            {/* Left Upper Card: Challenge details */}
            <div className="bg-[#070b13]/80 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between font-mono relative overflow-hidden shadow-xl min-h-[190px]">
              <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none"></div>
              <div>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">COGNITIVE TASK</span>
                  <span className="bg-purple-950/40 border border-purple-500/20 text-purple-400 font-bold px-2 py-0.5 rounded text-[8px] tracking-widest uppercase shadow-[0_0_8px_rgba(168,85,247,0.1)] animate-pulse">
                    EXPERT_TIER
                  </span>
                </div>
                <h3 className="text-xl font-black text-slate-100 tracking-tight mb-2">Neural Core Repair</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Identify and patch the fractured synapse in the cognitive relay. A logic deviation has been detected, causing core integrity deterioration. Select the perfect logical node below to restore synaptic flow.
                </p>
              </div>
            </div>

            {/* Left Lower Card: Core stability and interactive integrity indicator */}
            <div className="bg-[#070b13]/80 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between font-mono shadow-xl relative min-h-[180px]">
              <div>
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-widest block mb-4">SYSTEM CALIBRATION</span>
                
                <div className="flex items-baseline justify-between">
                  <span className="text-xs text-slate-400 font-bold">CORE STABILITY:</span>
                  <span className={`text-4xl font-black ${isRepaired ? 'text-emerald-400 shadow-[0_0_15px_#34d399]' : 'text-cyan-400 shadow-[0_0_15px_#22d3ee]'} transition-all duration-300 font-mono`}>
                    {stability}%
                  </span>
                </div>

                {/* Custom glowing progress bar slider */}
                <div className="w-full bg-slate-950 h-3 rounded-full mt-4 border border-slate-900 p-0.5 relative overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-300 shadow-md ${
                      isRepaired 
                        ? 'bg-emerald-400 shadow-[0_0_10px_#34d399]' 
                        : stability < 50 
                        ? 'bg-rose-500 animate-pulse shadow-[0_0_10px_#f43f5e]' 
                        : 'bg-cyan-400 shadow-[0_0_10px_#22d3ee]'
                    }`}
                    style={{ width: `${stability}%` }}
                  />
                </div>
              </div>

              <div className="border-t border-slate-900/60 pt-3 mt-4 flex items-center justify-between text-[9px]">
                <span className={`${isRepaired ? 'text-emerald-400 font-bold' : 'text-rose-400 animate-pulse'} uppercase tracking-wider`}>
                  {isRepaired ? 'INTEGRITY SECURED // NOMINAL' : 'INTEGRITY DECAYING: -1.2% / SEC'}
                </span>
                <span className="text-slate-600 font-bold">SYS_HEALTH_CHECK</span>
              </div>
            </div>

          </div>

          {/* RIGHT SIDE WORKSPACE COLUMN (Span 7) */}
          <div className="lg:col-span-7 bg-[#050811] border border-slate-900 rounded-3xl p-5 relative flex flex-col justify-between shadow-2xl min-h-[400px]">
            
            {/* Top Right Label showing temperature */}
            <div className="absolute top-4 right-4 z-20 font-mono">
              <div className="flex items-center gap-1.5 bg-rose-500/10 border border-rose-500/20 px-3 py-1 rounded-full text-rose-300 font-black text-[10px] tracking-wider uppercase animate-pulse">
                <Thermometer className="w-3.5 h-3.5" />
                <span>CORE_TEMP: {coreTemp}°C</span>
              </div>
            </div>

            {/* Left Top label within graph */}
            <div className="absolute top-4 left-4 z-20 font-mono text-[9px] text-slate-500 uppercase tracking-widest select-none">
              SYNAPSE INTERACTIVE SCHEMATIC // FEED
            </div>

            {/* Main SVG/Graph Workspace */}
            <div className="flex-1 w-full flex items-center justify-center relative mt-6 min-h-[260px]">
              
              {/* Decorative grid lines */}
              <div className="absolute inset-0 bg-cyber-grid opacity-[0.03] pointer-events-none"></div>

              {/* Holographic graph showing node repair */}
              <svg className="w-full h-full max-h-[280px]" viewBox="0 0 400 240">
                <defs>
                  <linearGradient id="neonCyanGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#0891b2" stopOpacity="0.4" />
                  </linearGradient>
                  <linearGradient id="neonPurpleGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#c084fc" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#a855f7" stopOpacity="0.4" />
                  </linearGradient>
                </defs>

                {/* Connecting Logic lines */}
                {/* Node 1 to Synapse Center */}
                <line x1="80" y1="60" x2="200" y2="120" stroke="#0891b2" strokeWidth="2" strokeDasharray="3 3" className="opacity-60" />
                {/* Node 2 to Synapse Center */}
                <line x1="80" y1="180" x2="200" y2="120" stroke="#0891b2" strokeWidth="2" strokeDasharray="3 3" className="opacity-60" />

                {/* Fractured core to right target path */}
                {isRepaired ? (
                  <path d="M 200 120 Q 280 90 320 120" fill="none" stroke="#34d399" strokeWidth="3" className="animate-pulse shadow-lg" />
                ) : (
                  <path d="M 200 120 Q 280 90 320 120" fill="none" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="4 4" className="animate-pulse" />
                )}

                {/* Vertical helper line descending from Synapse Core */}
                <line x1="200" y1="120" x2="200" y2="185" stroke="#a855f7" strokeWidth="1" strokeDasharray="2 3" className="opacity-60" />

                {/* Node: INPUT ALPHA-B (Upper Left) */}
                <circle cx="80" cy="60" r="16" fill="#020617" stroke="#22d3ee" strokeWidth="1.5" />
                <text x="80" y="64" fill="#22d3ee" fontSize="8" fontWeight="bold" fontFamily="monospace" textAnchor="middle">ALPHA-B</text>

                {/* Node: INPUT BETA-1 (Lower Left) */}
                <circle cx="80" cy="180" r="16" fill="#020617" stroke="#22d3ee" strokeWidth="1.5" />
                <text x="80" y="184" fill="#22d3ee" fontSize="8" fontWeight="bold" fontFamily="monospace" textAnchor="middle">BETA-1</text>

                {/* Central Fractured Core logic synapse gap */}
                <g transform="translate(200, 120)" className="cursor-pointer">
                  {isRepaired ? (
                    <>
                      <circle cx="0" cy="0" r="28" fill="#022c22" stroke="#34d399" strokeWidth="2.5" className="animate-pulse" />
                      <circle cx="0" cy="0" r="20" fill="#064e3b" stroke="#34d399" strokeWidth="1" />
                      <text x="0" y="4" fill="#a7f3d0" fontSize="10" fontWeight="black" fontFamily="monospace" textAnchor="middle">NODE_Q</text>
                    </>
                  ) : selectedRepoNode ? (
                    <>
                      {/* Temporary patched representation */}
                      <circle cx="0" cy="0" r="26" fill="#0f172a" stroke="#22d3ee" strokeWidth="1.5" className="animate-pulse" />
                      <text x="0" y="3" fill="#22d3ee" fontSize="8" fontWeight="black" fontFamily="monospace" textAnchor="middle">{selectedRepoNode}</text>
                    </>
                  ) : (
                    <>
                      {/* Fractured Synapse Placeholder */}
                      <circle cx="0" cy="0" r="24" fill="#1e1b4b" stroke="#a855f7" strokeWidth="2" strokeDasharray="3 3" />
                      <path d="M-6 -6 L6 6 M6 -6 L-6 6" stroke="#f43f5e" strokeWidth="2" />
                      <text x="0" y="35" fill="#a855f7" fontSize="8" fontWeight="bold" fontFamily="monospace" textAnchor="middle">FRACTURED SYNAPSE</text>
                    </>
                  )}
                </g>

                {/* Output node: COGNITIVE RELAY (Right side) */}
                <circle cx="320" cy="120" r="18" fill="#020617" stroke={isRepaired ? '#34d399' : '#f43f5e'} strokeWidth="1.5" />
                <text x="320" y="124" fill={isRepaired ? '#34d399' : '#f43f5e'} fontSize="7" fontWeight="bold" fontFamily="monospace" textAnchor="middle">RELAY_S1</text>
              </svg>
            </div>

            {/* Bottom Status feedback messaging inside graph board */}
            {feedback && (
              <div className={`mt-3 border p-3 rounded-xl text-[10px] font-mono flex items-center gap-2.5 transition-all duration-300 ${
                isRepaired 
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
                  : feedback.includes('ERROR') || feedback.includes('DEVATION')
                  ? 'bg-rose-500/10 border-rose-500/20 text-rose-300 animate-shake'
                  : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300'
              }`}>
                {isRepaired ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 animate-bounce" />
                ) : feedback.includes('ERROR') || feedback.includes('DEVATION') ? (
                  <AlertCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                ) : (
                  <Activity className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 animate-spin-slow" />
                )}
                <span>{feedback}</span>
              </div>
            )}
          </div>

          {/* BOTTOM FULL WIDTH NODE REPOSITORY PANEL */}
          <div className="lg:col-span-12 bg-[#070b13]/60 border border-slate-900 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between shadow-xl gap-4 font-mono">
            <div className="flex flex-col items-start gap-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">NODE REPOSITORY</span>
              <p className="text-[9px] text-slate-400 font-sans">Plug in a patch node candidate into the cognitive schematic buffer.</p>
            </div>

            {/* Hexagonal Selection chips with the exact data requested */}
            <div className="flex flex-wrap items-center gap-3">
              {[
                { key: 'NODE_A1', label: '35', title: 'NODE_A1' },
                { key: 'NODE_B7', label: '42', title: 'NODE_B7' },
                { key: 'NODE_Q', label: '47', title: 'NODE_Q', highlight: true },
                { key: 'NODE_E3', label: '88', title: 'NODE_E3' }
              ].map((item) => {
                const isSelected = selectedRepoNode === item.key;
                return (
                  <button
                    key={item.key}
                    onClick={() => {
                      if (isRepaired) return;
                      setSelectedRepoNode(item.key);
                      setFeedback(`PATCH BUFFER LOADED: MAPPED ${item.key} // LEVEL VALUE: ${item.label}`);
                    }}
                    disabled={isRepaired}
                    className={`px-4 py-2 border rounded-xl flex items-center gap-3 transition-all duration-300 cursor-pointer ${
                      isSelected
                        ? 'bg-cyan-500/10 border-cyan-400 text-cyan-300 scale-105 shadow-[0_0_12px_rgba(34,211,238,0.2)]'
                        : item.highlight && !isRepaired
                        ? 'bg-purple-950/20 border-purple-500/40 text-purple-400 hover:border-purple-400 hover:scale-102'
                        : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {/* Tiny visual hexagonal badge representation */}
                    <div className={`w-6 h-6 rounded flex items-center justify-center text-[10px] font-black ${
                      isSelected 
                        ? 'bg-cyan-500/20 text-cyan-300' 
                        : item.highlight
                        ? 'bg-purple-500/20 text-purple-300'
                        : 'bg-slate-900 text-slate-500'
                    }`}>
                      {item.label}
                    </div>
                    <span className="text-[10px] font-black tracking-wide">{item.title}</span>
                  </button>
                );
              })}
            </div>

            {/* Action Repair trigger button */}
            <button
              onClick={handleRepairInterface}
              disabled={isRepaired || isRepairing}
              className={`px-6 py-3 border-2 border-dashed font-bold text-xs uppercase tracking-widest rounded-xl transition-all duration-300 flex items-center gap-2 cursor-pointer ${
                isRepaired
                  ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10'
                  : isRepairing
                  ? 'border-cyan-500 text-cyan-400 bg-cyan-950/10 animate-pulse'
                  : 'border-cyan-400 text-cyan-400 hover:bg-cyan-950/20 hover:shadow-[0_0_12px_rgba(34,211,238,0.25)]'
              }`}
            >
              <Zap className="w-4 h-4 fill-current animate-bounce" />
              <span>{isRepaired ? 'NOMINAL CALIBRATED' : isRepairing ? 'REPAIRING...' : 'REPAIR INTERFACE'}</span>
            </button>
          </div>

        </div>
      )}

      {/* MODE 2: PATTERNBOT RECURSIVE SEQUENCE */}
      {mode === 'pattern-bot' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-900 rounded-2xl p-5 font-mono shadow-xl">
            <h3 className="text-sm font-black text-cyan-400 uppercase tracking-widest mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 animate-spin-slow" />
              <span>CHALLENGE: Recursive Sequence Repair</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-6 font-sans">
              Analyze the mathematical synapse vector alignment values. Discern the exact numeric outcome generated by the underlying recursive neural weights to restore target signal flow.
            </p>

            {/* Sequence block */}
            <div className="bg-slate-950 border border-slate-900 rounded-xl p-6 flex flex-col items-center mb-6">
              <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-4">SYNAPSE VECTOR PATHWAY</span>
              <div className="flex items-center gap-3 md:gap-5">
                {[3, 7, 15, 31].map((val, idx) => (
                  <React.Fragment key={val}>
                    <div className="bg-[#070b13] border border-slate-800 rounded-xl p-4 w-12 md:w-16 text-center font-mono font-black text-slate-300 text-sm shadow-md">
                      {val}
                    </div>
                    <span className="text-cyan-600 font-bold text-xs">➔</span>
                  </React.Fragment>
                ))}
                <div className={`border-2 rounded-xl p-4 w-12 md:w-16 text-center font-mono font-black text-sm transition-all duration-500 ${
                  sequenceSuccess 
                    ? 'bg-emerald-950/30 border-emerald-400 text-emerald-300 shadow-[0_0_10px_rgba(52,211,153,0.2)]' 
                    : selectedSequenceVal 
                    ? 'bg-cyan-950 border-cyan-400 text-cyan-300 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.2)]' 
                    : 'bg-[#070b13] border-rose-500/40 text-rose-400'
                }`}>
                  {selectedSequenceVal || '?'}
                </div>
              </div>
            </div>

            {/* Selection choices */}
            <div className="grid grid-cols-4 gap-3">
              {[45, 54, 63, 72].map((choice) => {
                const act = selectedSequenceVal === choice;
                return (
                  <button
                    key={choice}
                    onClick={() => {
                      if (sequenceSuccess) return;
                      setSelectedSequenceVal(choice);
                      setSequenceFeedback('');
                    }}
                    disabled={sequenceSuccess}
                    className={`py-3.5 rounded-xl border text-center transition font-mono font-bold text-xs cursor-pointer ${
                      act
                        ? 'bg-cyan-500/10 border-cyan-500 text-cyan-300 scale-102 shadow'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900'
                    }`}
                  >
                    {choice}
                  </button>
                );
              })}
            </div>
          </div>

          {sequenceFeedback && (
            <div className={`border px-4 py-3.5 rounded-xl text-xs font-mono flex items-center gap-2.5 ${
              sequenceSuccess 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}>
              {sequenceSuccess ? (
                <Check className="w-4 h-4 text-emerald-400 flex-shrink-0 animate-bounce" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              )}
              <span>{sequenceFeedback}</span>
            </div>
          )}

          <button
            onClick={handleVerifySequence}
            disabled={sequenceSuccess}
            className="w-full py-4 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold uppercase rounded-xl shadow-lg hover:shadow-cyan-400/25 disabled:opacity-50 transition-all duration-300 cursor-pointer"
          >
            Execute Repair Sequence
          </button>
        </div>
      )}
    </div>
  );
};
