import React, { useState, useEffect } from 'react';
import { ScreenId } from '../types';
import { Sliders, Cpu, CheckCircle2, AlertTriangle, Play, Waves, Info, Zap, Shield, HelpCircle } from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';
import { startAssessment, submitAnswer, finishAssessment, getResult } from '../services/assessmentApi';

export const DecisionCoreScreen: React.FC = () => {
  const { handleChallengeComplete: onComplete, logEvent: onLog, profile } = useAssessment();
  // Puck position ranges from 0 to 100. Target sweet spot representing Golden Ratio alignment is 62.
  const [puckPosition, setPuckPosition] = useState<number>(30);
  const [success, setSuccess] = useState<boolean>(false);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);

  // Backend integration state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questionId, setQuestionId] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [idleTimeMs] = useState(0);

  useEffect(() => {
    // Start an official backend session for standalone challenges
    if (profile) {
      startAssessment(profile.studentId, profile.level, 'GQ01', 'CompareBot')
        .then(res => {
          setSessionId(res.session_id);
          setQuestionId(res.question.question_id);
          onLog('DecisionCore Backend Connected', 'INFO', `Tracking session: ${res.session_id}`);
        })
        .catch(err => {
          onLog('DecisionCore Connection Error', 'ERROR', err.message);
        });
    }
  }, [profile, onLog]);

  const targetPosition = 62;
  const distance = Math.abs(puckPosition - targetPosition);
  
  // Calculate dynamic volumes
  const alphaVolume = Math.round(420 + puckPosition * 2.9);
  const betaVolume = Math.round(860 - puckPosition * 2.9);

  // Efficiency gain starts low and peaks at 100% when exactly aligned (distance === 0)
  const efficiencyGain = Math.max(0, Math.min(100, Math.round(100 - distance * 2.6)));
  const isAligned = efficiencyGain >= 95;

  const handleVerifyBalance = () => {
    if (isAligned) {
      setIsVerifying(true);
      onLog('Decision Core Balanced', 'SUCCESS', `Cores aligned successfully at efficiency: ${efficiencyGain}%`, { puckPosition, alphaVolume, betaVolume });
      
      setTimeout(() => {
        setSuccess(true);
        setIsVerifying(false);
        
        if (sessionId && questionId) {
          submitAnswer({
            session_id: sessionId,
            question_id: questionId,
            response: String(puckPosition),
            metrics: {
              reaction_time_ms: Date.now() - startTime,
              hover_duration_ms: 0,
              idle_time_ms: idleTimeMs,
              drag_distance: 0,
              answer_changes: 0,
              confidence_score: 5,
              attempt_number: 1,
              difficulty_level: 2,
              module_name: 'CompareBot',
              hint_used: false
            }
          }).then(() => {
            finishAssessment(sessionId).then(res => {
              getResult(res.assessment_id).then(backendRes => {
                onComplete('decision-core', 300, null, backendRes);
              });
            });
          });
        } else {
          onComplete('decision-core', 300);
        }
      }, 1200);
    } else {
      onLog('Decision Core alignment failed', 'WARNING', `Lock attempted at sub-optimal efficiency: ${efficiencyGain}%`);
    }
  };

  return (
    <div className="bg-[#020617] border border-slate-900 rounded-2xl p-6 md:p-8 shadow-2xl text-slate-100 font-sans flex flex-col h-full relative overflow-hidden max-w-4xl mx-auto">
      {/* High-tech grid background */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle, #22d3ee 1px, transparent 1px),
            linear-gradient(to right, #22d3ee 1px, transparent 1px),
            linear-gradient(to bottom, #22d3ee 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px, 32px 32px, 32px 32px',
        }}
      />

      <div className="border-b border-slate-900 pb-5 mb-8 relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
        <div>
          <span className="text-[9px] font-mono font-bold tracking-[0.25em] text-cyan-400 uppercase bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded">
            COGNITIVE CHALLENGE // CORE SEQUENCER
          </span>
          <h2 className="text-2xl font-black tracking-wider text-slate-100 mt-2 flex items-center gap-2 font-mono">
            <Sliders className="w-6 h-6 text-cyan-400 animate-pulse" />
            DECISION CORE
          </h2>
          <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mt-0.5">
            QUANTITATIVE DIFFERENTIAL ANALYSIS
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-[10px] text-slate-500 bg-[#070b13] border border-slate-900 px-3 py-1.5 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
          <span>CALIBRATION PROTOCOL ACTIVE</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch relative z-10">
        
        {/* LEFT REACTOR CYLINDER (ALPHA) - 4 COLS */}
        <div className="lg:col-span-4 bg-[#050811]/90 border border-slate-900 rounded-2xl p-6 flex flex-col items-center justify-between text-center relative shadow-lg">
          <div className="absolute top-2.5 left-3 font-mono text-[8px] text-slate-600 font-bold uppercase tracking-wider">
            SYSTEM_A_NODE
          </div>
          
          <div className="w-full flex flex-col items-center mt-2">
            <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-widest mb-1">
              REACTOR ALPHA
            </span>
            <span className="text-[10px] text-slate-500 font-mono">FLOW RATE CONTROL</span>
          </div>

          {/* Styled high-tech vertical fluid cylinder */}
          <div className="my-8 relative w-20 h-52 bg-[#02050c] border-2 border-slate-850 rounded-t-3xl rounded-b-2xl overflow-hidden shadow-[inset_0_4px_20px_rgba(0,0,0,0.9)] p-0.5 flex items-end">
            {/* Ambient inner glow lines */}
            <div className="absolute inset-y-0 left-1/2 w-[1px] bg-white/5 pointer-events-none"></div>
            
            {/* Cyan fluid volume fill */}
            <div 
              className="w-full bg-gradient-to-t from-cyan-600/90 via-cyan-500/80 to-cyan-400/95 transition-all duration-300 rounded-b-xl relative flex items-start justify-center"
              style={{ height: `${puckPosition * 0.8 + 15}%` }}
            >
              {/* Dynamic wave overlay */}
              <div className="absolute -top-1 left-0 right-0 h-2 bg-cyan-300/60 blur-[1px] rounded-full animate-pulse"></div>
              <Waves className="w-full text-cyan-200/20 absolute -top-4 left-0 animate-bounce" />
              
              {/* Internal vertical bubbling particles */}
              <div className="absolute bottom-4 left-1/4 w-1 h-8 bg-cyan-200/30 rounded-full blur-[1px] animate-pulse"></div>
              <div className="absolute bottom-8 right-1/4 w-1.5 h-6 bg-cyan-100/20 rounded-full blur-[1px] animate-pulse"></div>
            </div>
          </div>

          {/* Dynamic volume readout */}
          <div className="w-full bg-slate-950/80 border border-slate-900/60 rounded-xl py-3 px-4 font-mono">
            <span className="text-[9px] text-slate-500 block uppercase tracking-wider font-bold">ALPHA VOLUME</span>
            <span className="text-xl font-black text-cyan-400 tracking-wider">
              {alphaVolume} UNT
            </span>
          </div>
        </div>

        {/* CENTER CALIBRATION PANEL & PUCK CONTROL - 4 COLS */}
        <div className="lg:col-span-4 bg-[#050811]/90 border border-slate-900 rounded-2xl p-6 flex flex-col justify-between shadow-lg relative">
          <div className="absolute top-2.5 left-3 font-mono text-[8px] text-slate-600 font-bold uppercase tracking-wider">
            COMPLEMENTARY_RATIO_UNIT
          </div>

          {/* Efficiency Gain display */}
          <div className="text-center space-y-2 mt-4">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">
              EFFICIENCY GAIN
            </span>
            <div className="relative inline-block">
              <span className="text-5xl font-black font-mono text-rose-500 select-none drop-shadow-[0_0_12px_rgba(244,63,94,0.15)] animate-pulse">
                {efficiencyGain}%
              </span>
            </div>
            
            {/* Live Progress Bar for efficiency */}
            <div className="w-full bg-[#02050c] h-2 rounded-full overflow-hidden border border-slate-900/60 p-0.5 mt-2">
              <div 
                className={`h-full rounded-full transition-all duration-300 ${
                  isAligned 
                    ? 'bg-cyan-400 shadow-[0_0_8px_#22d3ee]' 
                    : efficiencyGain > 75 
                    ? 'bg-amber-400' 
                    : 'bg-rose-500'
                }`}
                style={{ width: `${efficiencyGain}%` }}
              />
            </div>
          </div>

          {/* High tech instruction & custom track slider */}
          <div className="my-8 space-y-4">
            <p className="text-[11px] text-slate-400 leading-relaxed text-center font-mono bg-slate-950/40 p-3.5 border border-slate-900 rounded-xl">
              Align the neural puck with the dominant energy signature to synchronize cores.
            </p>

            {/* HIGH-FIDELITY CUSTOM SLIDER representing the "neural puck" from Image 2 */}
            <div className="space-y-2 py-3">
              <div className="flex justify-between font-mono text-[8px] text-slate-500 font-bold tracking-widest px-1">
                <span>0.00λ</span>
                <span className="text-cyan-400/80 animate-pulse">ALIGN CORES</span>
                <span>1.00λ</span>
              </div>
              
              <div className="relative flex items-center h-6 select-none">
                {/* Visual ticks inside the slider track */}
                <div className="absolute inset-x-0 h-[2px] bg-slate-900 flex justify-between pointer-events-none">
                  {Array.from({ length: 9 }).map((_, i) => (
                    <div key={i} className="w-[1px] h-2 bg-slate-800 -translate-y-1"></div>
                  ))}
                </div>

                {/* Main Slider Input Override */}
                <input
                  type="range"
                  min="5"
                  max="95"
                  value={puckPosition}
                  disabled={success || isVerifying}
                  onChange={(e) => {
                    setPuckPosition(Number(e.target.value));
                  }}
                  className="w-full h-1.5 bg-gradient-to-r from-violet-950 via-cyan-900/40 to-violet-950 rounded-lg appearance-none cursor-pointer accent-cyan-400 relative z-10 focus:outline-none"
                />

                {/* Glowing target guide overlay */}
                <div 
                  className="absolute w-1 h-4 bg-rose-500/40 border border-rose-500/60 pointer-events-none rounded"
                  style={{ left: '62%' }}
                  title="Target Alignment"
                />
              </div>
              <div className="text-center font-mono text-[9px] text-slate-500">
                Current Alignment Delta: <span className="text-rose-400">{(distance * 0.01).toFixed(3)}λ</span>
              </div>
            </div>
          </div>

          {/* Validation Alerts */}
          <div className="w-full">
            {isVerifying ? (
              <div className="bg-cyan-950/20 border border-cyan-500/20 text-cyan-400 p-3 rounded-xl text-center text-[10px] font-mono animate-pulse">
                INITIALIZING COGNITIVE INJECTION SEQUENCE...
              </div>
            ) : success ? (
              <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 p-3 rounded-xl text-center text-[10px] font-mono">
                ✔ COGNITIVE ALIGNMENT VERIFIED
              </div>
            ) : isAligned ? (
              <div className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 p-3 rounded-xl text-center text-[10px] font-mono animate-pulse font-bold flex items-center justify-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>SYMMETRICAL EQUILIBRIUM ACTIVE</span>
              </div>
            ) : (
              <div className="bg-rose-500/5 border border-rose-500/10 text-rose-300 p-3 rounded-xl text-center text-[10px] font-mono">
                ⚠ MISALIGNED CORE DYNAMICS
              </div>
            )}
          </div>
        </div>

        {/* RIGHT REACTOR CYLINDER (BETA) - 4 COLS */}
        <div className="lg:col-span-4 bg-[#050811]/90 border border-slate-900 rounded-2xl p-6 flex flex-col items-center justify-between text-center relative shadow-lg">
          <div className="absolute top-2.5 left-3 font-mono text-[8px] text-slate-600 font-bold uppercase tracking-wider">
            SYSTEM_B_NODE
          </div>

          <div className="w-full flex flex-col items-center mt-2">
            <span className="text-xs font-mono font-bold text-violet-400 uppercase tracking-widest mb-1">
              REACTOR BETA
            </span>
            <span className="text-[10px] text-slate-500 font-mono">FLOW RATE CONTROL</span>
          </div>

          {/* Styled high-tech vertical fluid cylinder with purple/violet fluid */}
          <div className="my-8 relative w-20 h-52 bg-[#02050c] border-2 border-slate-850 rounded-t-3xl rounded-b-2xl overflow-hidden shadow-[inset_0_4px_20px_rgba(0,0,0,0.9)] p-0.5 flex items-end">
            {/* Ambient inner glow lines */}
            <div className="absolute inset-y-0 left-1/2 w-[1px] bg-white/5 pointer-events-none"></div>
            
            {/* Purple fluid volume fill */}
            <div 
              className="w-full bg-gradient-to-t from-violet-600/90 via-violet-500/80 to-violet-400/95 transition-all duration-300 rounded-b-xl relative flex items-start justify-center"
              style={{ height: `${(100 - puckPosition) * 0.8 + 15}%` }}
            >
              {/* Dynamic wave overlay */}
              <div className="absolute -top-1 left-0 right-0 h-2 bg-violet-300/60 blur-[1px] rounded-full animate-pulse"></div>
              <Waves className="w-full text-violet-200/20 absolute -top-4 left-0 animate-bounce" />
              
              {/* Internal bubbling particles */}
              <div className="absolute bottom-5 left-1/3 w-1 h-6 bg-violet-200/30 rounded-full blur-[1px] animate-pulse"></div>
              <div className="absolute bottom-10 right-1/3 w-1.5 h-8 bg-violet-100/20 rounded-full blur-[1px] animate-pulse"></div>
            </div>
          </div>

          {/* Dynamic volume readout */}
          <div className="w-full bg-slate-950/80 border border-slate-900/60 rounded-xl py-3 px-4 font-mono">
            <span className="text-[9px] text-slate-500 block uppercase tracking-wider font-bold">BETA VOLUME</span>
            <span className="text-xl font-black text-violet-400 tracking-wider">
              {betaVolume} UNT
            </span>
          </div>
        </div>

      </div>

      {/* Lock Control Action Trigger - Full Width */}
      <div className="mt-8 relative z-10">
        <button
          onClick={handleVerifyBalance}
          disabled={success || isVerifying || !isAligned}
          className={`w-full py-4 font-mono font-bold uppercase rounded-xl text-xs tracking-wider shadow-lg flex items-center justify-center gap-2 transition-all duration-300 cursor-pointer ${
            isAligned && !success && !isVerifying
              ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 hover:shadow-[0_0_15px_rgba(34,211,238,0.25)]'
              : 'bg-slate-900 text-slate-500 border border-slate-850 cursor-not-allowed opacity-60'
          }`}
        >
          <Play className="w-4 h-4 fill-current" />
          Lock Symmetrical Ratio
        </button>
      </div>
    </div>
  );
};
