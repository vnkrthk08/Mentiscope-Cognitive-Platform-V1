import React, { useState, useEffect } from 'react';
import { ScreenId, StudentProfile, SessionScores } from '../types';
import { 
  BarChart, Compass, Award, Activity, Radio, AlertOctagon, Heart, Cpu, 
  Sparkles, Check, RefreshCw, BarChart2, ShieldAlert, Waves, Info, Download, 
  FileText, Star, Eye, Calendar, UserCheck, HelpCircle, Layers, Clipboard, CheckCircle2, ChevronRight, BookOpen, ExternalLink
} from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';
import { startAssessment, submitAnswer, finishAssessment, getResult } from '../services/assessmentApi';

export const AnalyticsScreen: React.FC = () => {
  const { currentScreen, completedScreens, sessionScores, profile, handleChallengeComplete: onComplete, logEvent: onLog } = useAssessment();
  const initialTab = (currentScreen === 'vision-bot' || currentScreen === 'cognitive-analytics' || currentScreen === 'cognitive-profile' || currentScreen === 'analytics-core' || currentScreen === 'item-exposure') ? currentScreen : 'cognitive-analytics';
  const [activeTab, setActiveTab] = useState<'cognitive-analytics' | 'cognitive-profile' | 'vision-bot' | 'analytics-core' | 'item-exposure' | 'pilot-dataset' | 'technical-blueprint'>(initialTab as any);

  // Backend integration state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questionId, setQuestionId] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [idleTimeMs] = useState(0);

  useEffect(() => {
    if (profile && (activeTab === 'vision-bot' || activeTab === 'analytics-core')) {
      const construct = activeTab === 'vision-bot' ? 'VisionBot' : 'CompareBot';
      startAssessment(profile.studentId, profile.level, 'GQ01', construct)
        .then(res => {
          setSessionId(res.session_id);
          setQuestionId(res.question.question_id);
          onLog(`${activeTab} Backend Connected`, 'INFO', `Tracking session: ${res.session_id}`);
        })
        .catch(err => {
          onLog(`${activeTab} Connection Error`, 'ERROR', err.message);
        });
    }
  }, [profile, activeTab, onLog]);

  // Fallback / default scores if the user hasn't completed the adaptive assessment yet
  const scores: SessionScores = sessionScores || profile?.lastSessionScores || {
    rawScore: 0,
    normalizedScore: 0,
    percentile: 0,
    subScores: {
      PatternBot: 0,
      CompareBot: 0,
      VisionBot: 0,
      SolverBot: 0
    },
    confidenceScore: 0
  };

  // --- VISIONBOT STATE ---
  const [neuralLoad, setNeuralLoad] = useState<number[]>([44, 52, 61, 48]);
  const [synapticVariance, setSynapticVariance] = useState<number[]>([12, 18, 15, 24, 30, 22, 28]);
  const [anomalyTriggered, setAnomalyTriggered] = useState(false);
  const [quarantined, setQuarantined] = useState(false);

  // --- ANALYTICS CORE WAVE PUZZLE STATE ---
  const [amplitude, setAmplitude] = useState(50);
  const [frequency, setFrequency] = useState(40);
  const targetWave = { amp: 70, freq: 65 };
  const waveAligned = Math.abs(amplitude - targetWave.amp) <= 5 && Math.abs(frequency - targetWave.freq) <= 5;
  const [waveSuccess, setWaveSuccess] = useState(false);

  // --- ADAPTIVE ITEM EXPOSURE SIMULATION ---
  const [simIndex, setSimIndex] = useState(0);
  const [selectedSimQuestion, setSelectedSimQuestion] = useState<number | null>(null);



  // Chapter state for technical-blueprint e-reader
  const [selectedChapter, setSelectedChapter] = useState<number>(1);

  // Export PDF simulation state
  const [pdfGenerating, setPdfGenerating] = useState<boolean>(false);
  const [pdfSuccess, setPdfSuccess] = useState<string>('');

  // Live intervals for VisionBot telemetry simulation
  useEffect(() => {
    const int = setInterval(() => {
      setNeuralLoad((prev) => prev.map((l) => Math.max(10, Math.min(100, l + Math.floor(Math.random() * 9 - 4)))));
      setSynapticVariance((prev) => {
        const next = [...prev.slice(1), Math.max(5, Math.min(60, prev[prev.length - 1] + Math.floor(Math.random() * 11 - 5)))];
        return next;
      });
      if (Math.random() < 0.15 && !quarantined) {
        setAnomalyTriggered(true);
      }
    }, 1500);
    return () => clearInterval(int);
  }, [quarantined]);

  const handleQuarantine = () => {
    setQuarantined(true);
    setAnomalyTriggered(false);
    onLog('VisionBot Sector Quarantined', 'SUCCESS', 'Anomalous load vectors bypassed and filtered.', { neuralLoad });
    
    if (sessionId && questionId) {
      submitAnswer({
        session_id: sessionId,
        question_id: questionId,
        response: 'quarantine',
        metrics: {
          reaction_time_ms: Date.now() - startTime,
          hover_duration_ms: 0,
          idle_time_ms: idleTimeMs,
          drag_distance: 0,
          answer_changes: 0,
          confidence_score: 5,
          attempt_number: 1,
          difficulty_level: 2,
          module_name: 'VisionBot',
          hint_used: false
        }
      }).then(() => {
        finishAssessment(sessionId).then(res => {
          getResult(res.assessment_id).then(backendRes => {
            if (onComplete) onComplete('vision-bot', 200, null, backendRes);
          });
        });
      });
    } else {
      if (onComplete) onComplete('vision-bot', 200);
    }
  };

  const handleVerifyWave = () => {
    if (waveAligned) {
      setWaveSuccess(true);
      onLog('Analytics Core Wave aligned', 'SUCCESS', 'Oscilloscope sine wave phase matching satisfied', { amplitude, frequency });
      
      if (sessionId && questionId) {
        submitAnswer({
          session_id: sessionId,
          question_id: questionId,
          response: `${amplitude},${frequency}`,
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
              if (onComplete) onComplete('analytics-core', 300, null, backendRes);
            });
          });
        });
      } else {
        if (onComplete) onComplete('analytics-core', 300);
      }
    } else {
      onLog('Analytics Core Wave alignment failed', 'WARNING', `Current: Amp=${amplitude}, Freq=${frequency}. Target: Amp=${targetWave.amp}, Freq=${targetWave.freq}`);
    }
  };

  // PDF Export Simulator (Deliverable 7 Session Summary PDF Export)
  const handleExportPDF = () => {
    setPdfGenerating(true);
    onLog('PDF Report Generation Initialized', 'INFO', `Generating diagnostic Gq assessment dossier for ${profile?.fullName || 'GUEST'}`);
    
    setTimeout(() => {
      setPdfGenerating(false);
      setPdfSuccess(`MentiScope-Gq-Report-${profile?.studentId || 'GUEST'}.pdf successfully compiled and downloaded.`);
      onLog('PDF Report Export Complete', 'SUCCESS', `Gq session PDF generated for ${profile?.studentId || 'GUEST'}`);
      
      // Simulate real download
      const content = `MENTISCOPE GQ ASSESSMENT SUMMARY REPORT\n=========================================\nStudent: ${profile?.fullName || 'Guest Student'}\nAcademy: ${profile?.academy || 'Sector Delta'}\nOverall Gq Score: ${scores.normalizedScore}/100\nConfidence Score: ${scores.confidenceScore * 100}%\nPercentile Rank: ${scores.percentile}th\n\nSUB-SCORES:\n- PatternBot (Arithmetic Reasoning): ${scores.subScores.PatternBot}%\n- CompareBot (Quantitative Comparison): ${scores.subScores.CompareBot}%\n- VisionBot (Data Interpretation): ${scores.subScores.VisionBot}%\n- SolverBot (Applied Problem Solving): ${scores.subScores.SolverBot}%\n\nGenerated on: ${new Date().toLocaleDateString()}`;
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `MentiScope-Gq-Report-${profile?.studentId || 'GUEST'}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => setPdfSuccess(''), 5000);
    }, 1800);
  };



  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl text-slate-100 font-sans flex flex-col h-full relative overflow-hidden">
      
      {/* Background ambient light */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Tab select bar */}
      <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-6 relative z-10">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-cyan-400 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 animate-pulse" />
            MENTISCOPE GQ MISSION ANALYSIS & SPEC CENTER
          </h2>
          <p className="text-xs text-slate-400">Quantitative Ability (Gq) Complete Blueprint Diagnostics</p>
        </div>

        <div className="flex flex-wrap gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-800 text-xs">
          {[
            { id: 'cognitive-analytics', label: 'Diagnostic Dashboard' },
            { id: 'technical-blueprint', label: 'Blueprint Documentation' },
            { id: 'vision-bot', label: 'VisionBot Sandbox' },
            { id: 'analytics-core', label: 'Oscilloscope' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any);
                onLog('Analytics view updated', 'INFO', `Navigated specification sub-portal to: ${tab.label}`);
              }}
              className={`px-2.5 py-1.5 rounded transition font-mono tracking-wide uppercase ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* --- DELIVERABLE 7: ANALYTICS DASHBOARD --- */}
      {activeTab === 'cognitive-analytics' && (
        <div className="space-y-6 relative z-10">
          
          {/* Section 1: Overall Performance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Overall Gq Score</span>
              <div className="mt-2 flex items-baseline gap-1.5">
                <span className="text-2xl font-black font-mono text-cyan-400">{scores.normalizedScore}/100</span>
                <span className="text-xs text-slate-500 uppercase font-mono">index</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-2">Combined raw accuracy performance score.</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-500 block font-mono">CONFIDENCE SCORE</span>
              <span className="text-2xl font-black font-mono text-emerald-400">
                {Math.round((sessionScores?.confidenceScore || 0.91) * 100)}%
              </span>
              <p className="text-[10px] text-slate-400 mt-1 font-mono">Weighted calibration index</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-500 block">PERCENTILE RANK</span>
              <span className="text-2xl font-bold font-mono text-violet-400">
                {sessionScores?.percentile || 88}th percentile
              </span>
              <p className="text-[10px] text-slate-400 mt-1">Relative to pilot database</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-500 block">CURRENT ADAPTIVE LEVEL</span>
              <span className="text-2xl font-bold font-mono text-rose-400">Level {profile?.level || 4}</span>
              <p className="text-[10px] text-slate-400 mt-1">High-ability discrimination</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-500 block">SESSION DURATION</span>
              <span className="text-2xl font-bold font-mono text-cyan-400">24.6 seconds</span>
              <p className="text-[10px] text-slate-500 mt-1">Average response time</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Centerpiece: CHC-Gq Radar Chart & Module Performances */}
            <div className="lg:col-span-8 space-y-6">
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">CHC-Gq Multidimensional Profile (Calibration Report)</h3>
                  <span className="text-[10px] font-mono text-cyan-400">Active Fingerprint</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
                  {/* Radar Canvas */}
                  <div className="md:col-span-5 flex flex-col items-center">
                    <div className="relative w-44 h-44">
                      <svg viewBox="0 0 100 100" className="w-full h-full">
                        {/* Grid rings */}
                        <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="#334155" strokeWidth="0.5" />
                        <polygon points="50,25 75,50 50,75 25,50" fill="none" stroke="#334155" strokeWidth="0.5" />
                        <polygon points="50,40 60,50 50,60 40,50" fill="none" stroke="#1e293b" strokeWidth="0.5" />
                        {/* Axis */}
                        <line x1="50" y1="10" x2="50" y2="90" stroke="#334155" strokeWidth="0.5" />
                        <line x1="10" y1="50" x2="90" y2="50" stroke="#334155" strokeWidth="0.5" />

                        {/* Polygon derived from actual module sub scores */}
                        {/* 50 is center. up=Arithmetic, right=Comparison, down=Interpretation, left=Applied */}
                        {/* Normalized out of 100 */}
                        <polygon 
                          points={`
                            50,${50 - (scores.subScores.PatternBot / 100) * 40} 
                            ${50 + (scores.subScores.CompareBot / 100) * 40},50 
                            50,${50 + (scores.subScores.VisionBot / 100) * 40} 
                            ${50 - (scores.subScores.SolverBot / 100) * 40},50
                          `} 
                          fill="rgba(6, 182, 212, 0.2)" 
                          stroke="#22d3ee" 
                          strokeWidth="2" 
                        />

                        {/* Dots */}
                        <circle cx="50" cy={50 - (scores.subScores.PatternBot / 100) * 40} r="2" fill="#22d3ee" />
                        <circle cx={50 + (scores.subScores.CompareBot / 100) * 40} cy="50" r="2" fill="#22d3ee" />
                        <circle cx="50" cy={50 + (scores.subScores.VisionBot / 100) * 40} r="2" fill="#22d3ee" />
                        <circle cx={50 - (scores.subScores.SolverBot / 100) * 40} cy="50" r="2" fill="#22d3ee" />

                        {/* Axis Labels */}
                        <text x="50" y="7" textAnchor="middle" fill="#94a3b8" fontSize="5" fontWeight="bold">ARITHMETIC ({scores.subScores.PatternBot}%)</text>
                        <text x="92" y="52" textAnchor="start" fill="#94a3b8" fontSize="5" fontWeight="bold">COMPARE ({scores.subScores.CompareBot}%)</text>
                        <text x="50" y="97" textAnchor="middle" fill="#94a3b8" fontSize="5" fontWeight="bold">INTERPRET ({scores.subScores.VisionBot}%)</text>
                        <text x="8" y="52" textAnchor="end" fill="#94a3b8" fontSize="5" fontWeight="bold">APPLIED ({scores.subScores.SolverBot}%)</text>
                      </svg>
                    </div>
                  </div>

                  {/* Module Table (Deliverable 7 Page 41) */}
                  <div className="md:col-span-7 font-mono text-xs text-slate-300">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-500 text-[10px] text-left">
                          <th className="py-2 uppercase">Module</th>
                          <th className="py-2 text-center uppercase">Score</th>
                          <th className="py-2 text-center uppercase">Avg Time</th>
                          <th className="py-2 text-right uppercase">Accuracy</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          { id: 'PatternBot', score: scores.subScores.PatternBot, time: '18 s', acc: '95%' },
                          { id: 'CompareBot', score: scores.subScores.CompareBot, time: '22 s', acc: '83%' },
                          { id: 'VisionBot', score: scores.subScores.VisionBot, time: '20 s', acc: '91%' },
                          { id: 'SolverBot', score: scores.subScores.SolverBot, time: '31 s', acc: '76%' },
                        ].map((item) => (
                          <tr key={item.id} className="border-b border-slate-850 hover:bg-slate-900/30">
                            <td className="py-2.5 font-bold text-slate-200">{item.id}</td>
                            <td className="py-2.5 text-center text-cyan-400 font-bold">{item.score}</td>
                            <td className="py-2.5 text-center text-slate-400">{item.time}</td>
                            <td className="py-2.5 text-right text-emerald-400 font-semibold">{item.acc}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Dynamic Adaptive Learning Curve (Deliverable 7 Page 41) */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-3">Adaptive Learning Curve Progress</h3>
                <p className="text-xs text-slate-400 mb-4 font-mono leading-normal">
                  Traces item difficulty adjustments decided by the Item Response adaptive routing heuristic over successive question loads.
                </p>

                <div className="h-32 bg-slate-950/80 rounded-xl border border-slate-850 p-4 flex items-end justify-between gap-2 relative">
                  {/* Grid Lines */}
                  <div className="absolute inset-x-0 top-1/4 border-b border-slate-900/60"></div>
                  <div className="absolute inset-x-0 top-2/4 border-b border-slate-900/60"></div>
                  <div className="absolute inset-x-0 top-3/4 border-b border-slate-900/60"></div>

                  {[
                    { itemId: 'PB-L1', difficulty: 1.2, correct: true, timeMs: 14000 },
                    { itemId: 'CB-L2', difficulty: 2.1, correct: true, timeMs: 18000 },
                    { itemId: 'VB-L3', difficulty: 3.2, correct: false, timeMs: 40000 },
                    { itemId: 'SB-L2', difficulty: 2.4, correct: true, timeMs: 31000 },
                    { itemId: 'PB-L3', difficulty: 3.1, correct: true, timeMs: 19000 },
                    { itemId: 'CB-L4', difficulty: 4.2, correct: true, timeMs: 25000 },
                    { itemId: 'VB-L5', difficulty: 4.8, correct: false, timeMs: 55000 },
                    { itemId: 'SB-L4', difficulty: 3.9, correct: true, timeMs: 30000 },
                  ].map((pt, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center h-full justify-end group cursor-pointer relative">
                      {/* Bar representing difficulty */}
                      <div 
                        className={`w-4 bg-gradient-to-t rounded-t hover:brightness-125 transition-all ${pt.correct ? 'from-cyan-600/70 to-cyan-400/90' : 'from-rose-600/70 to-rose-400/90'}`}
                        style={{ height: `${(pt.difficulty / 5.0) * 100}%` }}
                      ></div>
                      
                      {/* Circle tooltip on hover */}
                      <div className="absolute bottom-12 hidden group-hover:block bg-slate-900 border border-slate-800 text-[10px] font-mono p-2 rounded shadow-2xl w-32 z-30">
                        <div className="text-cyan-400 font-bold">{pt.itemId || `Q-${i+1}`}</div>
                        <div>Diff: {pt.difficulty}</div>
                        <div>Correct: {pt.correct ? 'YES' : 'NO'}</div>
                        <div>Time: {pt.timeMs ? (pt.timeMs/1000).toFixed(1)+'s' : '22s'}</div>
                      </div>

                      <span className="text-[9px] font-mono text-slate-500 mt-2">Q{i+1}</span>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2">
                  <span>Start (Baseline L1-L2)</span>
                  <span>Sequential Progression</span>
                  <span>End (Stabilized Level L4-L5)</span>
                </div>
              </div>
            </div>

            {/* Right Panel: Error Patterns, Strategy Shifts & PDF export */}
            <div className="lg:col-span-4 space-y-6">
              
              {/* Error pattern heatmap */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">Error Pattern Analysis</h3>
                
                <div className="space-y-3 font-mono text-[11px]">
                  {[
                    { label: 'Percentage Conversion Error', count: 5, color: 'bg-rose-500/20 text-rose-400 border-rose-500/30' },
                    { label: 'Recursive Sequence Missed', count: 2, color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
                    { label: 'Graph Trend Interpretation', count: 1, color: 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20' },
                    { label: 'Non-optimal Constraint Flow', count: 4, color: 'bg-rose-500/20 text-rose-400 border-rose-500/30' },
                  ].map((err, idx) => (
                    <div key={idx} className={`p-2.5 border rounded-lg flex justify-between items-center ${err.color}`}>
                      <span>{err.label}</span>
                      <span className="font-bold px-2 py-0.5 rounded bg-slate-950">{err.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hint dependency gauge */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3.5">
                <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">Hint Dependency</h3>
                
                <div className="space-y-1.5 font-mono">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Hints Leveraged</span>
                    <span className="text-cyan-400 font-bold">18%</span>
                  </div>
                  <div className="w-full bg-slate-950 h-3 border border-slate-800 rounded-full p-0.5 overflow-hidden">
                    <div className="bg-cyan-500 h-full rounded-full" style={{ width: '18%' }}></div>
                  </div>
                  <span className="text-[10px] text-slate-500 block leading-normal">
                    Low dependency index indicates student executes calculations independently without assistive logic.
                  </span>
                </div>
              </div>

              {/* Strategy Shifts timeline */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">Strategy Shift Timeline</h3>
                
                <div className="space-y-4 relative pl-4 border-l border-slate-800 text-xs">
                  <div className="relative">
                    <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                    <div className="font-bold text-slate-200">Phase 1: Guessing & Trial</div>
                    <p className="text-[10px] text-slate-400 mt-1">High frequency choice jumps, brief option hover time.</p>
                  </div>

                  <div className="relative">
                    <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                    <div className="font-bold text-slate-200">Phase 2: Analytical Transition</div>
                    <p className="text-[10px] text-slate-400 mt-1">Stabilized mouse motion, lengthy calculation pauses.</p>
                  </div>

                  <div className="relative">
                    <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                    <div className="font-bold text-slate-200">Phase 3: Fast Analytical / Efficient</div>
                    <p className="text-[10px] text-slate-400 mt-1">First-attempt correct answers completed under 15 seconds.</p>
                  </div>
                </div>
              </div>

              {/* Export Dossier section */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center space-y-3">
                <h4 className="text-xs font-mono font-bold text-slate-300 uppercase">Assessment Dossier Summary</h4>
                <p className="text-[11px] text-slate-400">Compile official diagnostic assessment and stream JSON dataset records.</p>
                
                <button
                  onClick={handleExportPDF}
                  disabled={pdfGenerating}
                  className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold text-xs uppercase rounded-lg flex items-center justify-center gap-2 transition"
                >
                  {pdfGenerating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      COMPILING DATA MATRIX...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      EXPORT SESSION SUMMARY (.TXT)
                    </>
                  )}
                </button>

                {pdfSuccess && (
                  <p className="text-[10px] font-mono text-emerald-400 animate-pulse mt-2">{pdfSuccess}</p>
                )}

                <div className="border-t border-slate-800/80 pt-3 mt-3 text-left space-y-2">
                  <span className="text-[10px] font-mono text-slate-500 block uppercase tracking-wider font-bold">Stitch Design Reference</span>
                  <div className="flex items-center justify-between bg-slate-950 p-2 rounded-lg border border-slate-850">
                    <span className="text-[10px] font-mono text-cyan-400 truncate max-w-[170px]" title="https://stitch.withgoogle.com/projects/10807521546649880478">
                      stitch.withgoogle.com...10807521546649880478
                    </span>
                    <a
                      href="https://stitch.withgoogle.com/projects/10807521546649880478"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] font-mono font-bold text-slate-300 hover:text-cyan-400 flex items-center gap-1 uppercase transition shrink-0"
                    >
                      <span>OPEN</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      )}



      {/* --- DELIVERABLE 8: TECHNICAL BLUEPRINT DOCUMENTATION --- */}
      {activeTab === 'technical-blueprint' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10">
          
          {/* Chapter navigation left */}
          <div className="lg:col-span-4 space-y-2">
            <span className="text-[9px] font-mono text-slate-500 block uppercase tracking-widest mb-1 pl-1">SPECIFICATION ARCHITECTURE</span>
            {[
              { id: 1, title: '1. Introduction & CHC Gq Theory' },
              { id: 2, title: '2. Cognitive Calibration Framework' },
              { id: 3, title: '3. Master Item Generation Pool' },
              { id: 4, title: '4. Bayesian Adaptive Routing Engine' },
              { id: 5, title: '5. Behavioral Telemetry Logging' },
              { id: 6, title: '6. Live Analytics Scoring Intelligence' },
              { id: 7, title: '7. Suggested Gq Pilot Study Plan' },
              { id: 8, title: '8. Future Enhancements' },
            ].map((ch) => (
              <button
                key={ch.id}
                onClick={() => setSelectedChapter(ch.id)}
                className={`w-full p-3 rounded-lg text-left text-xs font-mono border transition flex items-center justify-between ${
                  selectedChapter === ch.id
                    ? 'bg-cyan-500/10 border-cyan-500 text-cyan-300 font-bold'
                    : 'bg-slate-900/60 border-slate-850 hover:bg-slate-800/60 text-slate-400'
                }`}
              >
                <span>{ch.title}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            ))}
          </div>

          {/* Chapter Content right */}
          <div className="lg:col-span-8 bg-slate-900/60 border border-slate-800 rounded-xl p-6 min-h-[400px] flex flex-col justify-between">
            <div className="space-y-4 font-sans text-xs md:text-sm text-slate-300 leading-relaxed">
              
              {selectedChapter === 1 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2 flex items-center gap-1.5">
                    <BookOpen className="w-4.5 h-4.5" /> 1. Introduction & CHC Quantitative Gq Theory
                  </h3>
                  <p>
                    <strong>MentiScope</strong> is a state-of-the-art cognitive adaptive testing platform designed specifically around the Cattell-Horn-Carroll (CHC) theory of cognitive abilities.
                  </p>
                  <p>
                    Our focal dimension is <strong>Quantitative Ability (Gq)</strong>, defined as the store of acquired quantitative knowledge and the ability to manipulate numerical symbols, reason logically, analyze visual dashboard trends, and solve optimization constraints.
                  </p>
                  <p>
                    Unlike traditional tests, the MentiScope engine believes score is only 10% of the value. The remaining 90% is extracted directly from the student's interaction behaviors (hesitation times, attempts, hint usage, slider moves).
                  </p>
                </>
              )}

              {selectedChapter === 2 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    2. Cognitive Calibration Framework
                  </h3>
                  <p>
                    Traditional testing platforms arbitrarily classify item difficulty as 'easy', 'medium', or 'hard'. MentiScope calculates item difficulty dynamically on a continuous scale from <strong>1.0 to 5.0</strong> using 8 weighted parameters:
                  </p>
                  <div className="bg-slate-950 p-3 rounded-lg font-mono text-xs border border-slate-850 space-y-1.5 text-slate-400">
                    <div>1. Rule Complexity (RC): 25% weight</div>
                    <div>2. Cognitive Steps (CS): 20% weight</div>
                    <div>3. Representation Complexity (RP): 15% weight</div>
                    <div>4. Working Memory Load (WM): 10% weight</div>
                    <div>5. Decision Complexity (DC): 10% weight</div>
                    <div>6. Visual Processing Load (VP): 5% weight</div>
                    <div>7. Constraint Load (CL): 10% weight</div>
                    <div>8. Expected Solve Time (T): 5% weight</div>
                  </div>
                  <p>
                    Every generated question is calibrated in real-time. This provides unified, psychometrically consistent item difficulty independent of numerical coefficients.
                  </p>
                </>
              )}

              {selectedChapter === 3 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    3. Master 300-Item Question Pool Design
                  </h3>
                  <p>
                    The Gq assessment is divided across 4 specialized autonomous agent modules:
                  </p>
                  <ul className="list-disc pl-4 space-y-1.5 font-mono text-xs text-slate-400">
                    <li><strong>PatternBot</strong> (Sequence progression repairs: arithmetic, geometric, second-order, Fibonacci, matrix logical patterns).</li>
                    <li><strong>CompareBot</strong> (Magnitude comparison, mixed percentages, ratios, fractions, and units comparison).</li>
                    <li><strong>VisionBot</strong> (Visual attention chart and dashboard data trends interpretation).</li>
                    <li><strong>SolverBot</strong> (Linear programming allocations, reactor capacities, load balances, route optimization constraints).</li>
                  </ul>
                  <p>
                    Every item is generated using a pipeline: Select Template &rarr; Generate Random Parameters &rarr; Assemble Story Context &rarr; Randomize Distractors &rarr; Assign Variant ID.
                  </p>
                </>
              )}

              {selectedChapter === 4 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    4. Bayesian Adaptive Routing Engine
                  </h3>
                  <p>
                    The adaptive routing engine calculates a <strong>Performance Score</strong> after every question using:
                  </p>
                  <div className="bg-slate-950 p-3 rounded-lg font-mono text-xs border border-slate-850 text-slate-400 text-center">
                    Score = 50% Accuracy + 20% Speed + 10% Hints + 10% Attempts + 10% Confidence
                  </div>
                  <p>
                    <strong>Routing Thresholds:</strong>
                  </p>
                  <ul className="list-disc pl-4 space-y-1 font-mono text-[11px] text-slate-400">
                    <li>Score &ge; 90% &rarr; Jump +2 Difficulty</li>
                    <li>Score 75% to 89% &rarr; Up +1 Difficulty</li>
                    <li>Score 50% to 74% &rarr; Stay Same Level</li>
                    <li>Score 35% to 49% &rarr; Drop -1 Difficulty</li>
                    <li>Score &lt; 35% &rarr; Drop -2 (min L1)</li>
                  </ul>
                  <p>
                    <strong>Exposure Control:</strong> Tracks template frequency to avoid repeat fatigue, ensures a cooldown period, and rotates narrative story themes.
                  </p>
                </>
              )}

              {selectedChapter === 5 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    5. Behavioral Telemetry Logging
                  </h3>
                  <p>
                    The SDK captures 11 distinct event types sorted into 6 core taxonomies: Session Events, Navigation Events, Interactive Moves (slid, hover, drag), Response changes, Hint logs, and Timing triggers.
                  </p>
                  <p>
                    Our SDK-Compliant Event Schema captures: <code>student_id</code>, <code>session_id</code>, <code>item_id</code>, <code>event_type</code>, <code>reaction_time_ms</code>, <code>correct</code>, <code>hover_duration_ms</code>, and <code>drag_distance_px</code>. This outputs clean telemetry streams ready to upload to secure data warehouses.
                  </p>
                </>
              )}

              {selectedChapter === 6 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    6. AI Analytics & Scoring Intelligence
                  </h3>
                  <p>
                    MentiScope doesn't just log "correct" or "incorrect". The AI engine categorizes incorrect choices to detect underlying conceptual weaknesses, such as:
                  </p>
                  <ul className="list-disc pl-4 space-y-1 font-mono text-xs text-slate-400">
                    <li><strong>PatternBot:</strong> AP_ERROR, treated geometric as arithmetic (GP_ERROR), missed recursive rule (REC_ERROR).</li>
                    <li><strong>CompareBot:</strong> Decimal confusion, ratio misunderstanding, percentage calculation error.</li>
                    <li><strong>VisionBot:</strong> Misread graph bounds, wrong average sum.</li>
                    <li><strong>SolverBot:</strong> Ignored constraint boundary, non-optimal route path.</li>
                  </ul>
                  <p>
                    We compute student Persistence metrics, Strategy shifts (Guessing &rarr; Analytical), and generate automated AI recommendations for customized training routines.
                  </p>
                </>
              )}

              {selectedChapter === 7 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    7. Suggested Gq Pilot Study Plan
                  </h3>
                  <p>
                    To validate the item generation calibration, we suggest launching a pilot program targeting:
                  </p>
                  <div className="bg-slate-950 p-4 border border-slate-850 rounded-xl space-y-1.5 font-mono text-xs text-slate-400">
                    <div>- Cohort Size: 30 to 50 active students</div>
                    <div>- Grade Bracket: Grade 11-12</div>
                    <div>- Assessment duration: 20-30 minutes per student</div>
                    <div>- Objective: Confirm item difficulty calibrations, estimate reliability, and evaluate adaptivity convergence.</div>
                  </div>
                </>
              )}

              {selectedChapter === 8 && (
                <>
                  <h3 className="text-md font-bold text-cyan-400 font-mono border-b border-slate-800 pb-2">
                    8. Future Work & Enhancements
                  </h3>
                  <p>
                    Future updates to the Gq Assessment Engine will include:
                  </p>
                  <ul className="list-decimal pl-4 space-y-1.5 font-mono text-xs text-slate-400">
                    <li>Bayesian Item Response Theory (IRT) estimation (theta calibrations based on larger sample pilot datasets).</li>
                    <li>Real-time LLM-driven feedback (generating specific plain-english remediation explanations during retries).</li>
                    <li>Multilingual support for global student origin matrix regional servers.</li>
                    <li>Expansion of assessment constructs to verbal Gv and memory Gsm frameworks.</li>
                  </ul>
                </>
              )}

            </div>

            <div className="border-t border-slate-800 pt-4 mt-6 flex justify-between items-center text-xs text-slate-500 font-mono">
              <span>MentiScope Blueprint // Gq Spec Portal</span>
              <span>Chapter {selectedChapter} of 8</span>
            </div>
          </div>
        </div>
      )}

      {/* --- OLD VISIONBOT SIMULATION (Retained for backwards compatibility) --- */}
      {activeTab === 'vision-bot' && (
        <div className="space-y-6 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl col-span-1">
              <h3 className="text-xs font-mono font-bold text-slate-400 mb-4 uppercase">Live Neural Load Gauge</h3>
              <div className="space-y-3">
                {neuralLoad.map((val, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-[11px] font-mono text-slate-300 mb-1">
                      <span>Secteur {idx + 1} Load</span>
                      <span>{val}%</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded overflow-hidden">
                      <div className={`h-full transition-all duration-300 ${val > 80 ? 'bg-rose-500 animate-pulse' : val > 55 ? 'bg-amber-400' : 'bg-cyan-500'}`} style={{ width: `${val}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl col-span-2 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-mono font-bold text-slate-400 mb-2 uppercase">Synaptic Signal Variance (Live Feed)</h3>
                <p className="text-[11px] text-slate-500 leading-normal mb-4">Continuous delta tracing of pupil-cognitive oscillations.</p>
              </div>

              <div className="h-20 bg-slate-950 rounded-lg p-2 border border-slate-800 relative flex items-end">
                <svg className="w-full h-full pointer-events-none" viewBox="0 0 140 30" preserveAspectRatio="none">
                  <polyline
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                    points={synapticVariance.map((val, idx) => `${idx * 20 + 10},${30 - val / 2.5}`).join(' ')}
                  />
                  {synapticVariance.map((val, idx) => (
                    <circle key={idx} cx={idx * 20 + 10} cy={30 - val / 2.5} r="1.5" fill="#34d399" />
                  ))}
                </svg>
              </div>

              <div className="flex justify-between items-center mt-4">
                {anomalyTriggered ? (
                  <div className="flex items-center gap-1.5 text-rose-400 font-mono text-[10px] font-bold animate-pulse">
                    <ShieldAlert className="w-4 h-4 text-rose-500" />
                    CRITICAL SIGNAL ANOMALY DETECTED
                  </div>
                ) : (
                  <div className="text-emerald-400 font-mono text-[10px] flex items-center gap-1">
                    <Check className="w-3 h-3" /> Nominal Wave Signature
                  </div>
                )}

                <button
                  onClick={handleQuarantine}
                  disabled={quarantined}
                  className={`px-3 py-1 text-[11px] font-mono font-bold rounded border ${
                    quarantined
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      : 'bg-rose-500/10 border-rose-500 hover:bg-rose-500 hover:text-white text-rose-300'
                  }`}
                >
                  {quarantined ? 'ISOLATED' : 'Quarantine Sector'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- SINE OSCILLOSCOPE TUNING --- */}
      {activeTab === 'analytics-core' && (
        <div className="space-y-6 relative z-10">
          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl">
            <h3 className="text-sm font-bold text-slate-200 mb-2">CHALLENGE: Sine Oscilloscope Tuning</h3>
            <p className="text-xs text-slate-400 mb-6">
              Match the target frequency and amplitude parameters to propagate standard neural resonance patterns.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="bg-slate-950 border-2 border-slate-800 rounded-xl p-4 h-48 relative overflow-hidden flex items-center">
                <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
                <div className="absolute top-1/2 left-0 w-full border-t border-dashed border-slate-800"></div>
                <div className="absolute left-1/2 top-0 h-full border-l border-dashed border-slate-800"></div>

                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
                  <path
                    d={Array.from({ length: 40 }).map((_, i) => {
                      const x = (i * 200) / 39;
                      const y = 50 + Math.sin((i / 1.5) * (targetWave.freq / 10)) * (targetWave.amp / 2.5);
                      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                    }).join(' ')}
                    fill="none"
                    stroke="#8b5cf6"
                    strokeWidth="1.5"
                    strokeDasharray="3 3"
                  />

                  <path
                    d={Array.from({ length: 40 }).map((_, i) => {
                      const x = (i * 200) / 39;
                      const y = 50 + Math.sin((i / 1.5) * (frequency / 10)) * (amplitude / 2.5);
                      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                    }).join(' ')}
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="2.5"
                  />
                </svg>

                <div className="absolute top-2 left-2 bg-slate-900/90 border border-slate-800 px-2 py-0.5 rounded text-[9px] font-mono flex gap-3 text-slate-400">
                  <span>Target: {targetWave.amp}/{targetWave.freq}</span>
                  <span className="text-cyan-400">Current: {amplitude}/{frequency}</span>
                </div>
              </div>

              <div className="space-y-5">
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-300">
                    <span>Wave Amplitude</span>
                    <span className="font-mono text-cyan-400">{amplitude}mV</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={amplitude}
                    disabled={waveSuccess}
                    onChange={(e) => {
                      setAmplitude(Number(e.target.value));
                    }}
                    className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-300">
                    <span>Wave Frequency</span>
                    <span className="font-mono text-cyan-400">{frequency}Hz</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={frequency}
                    disabled={waveSuccess}
                    onChange={(e) => {
                      setFrequency(Number(e.target.value));
                    }}
                    className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                </div>

                {waveSuccess && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-2 rounded-lg text-xs font-mono">
                    SUCCESS: Wave pattern matched and synchronized! Challenge cleared.
                  </div>
                )}

                <button
                  onClick={handleVerifyWave}
                  disabled={waveSuccess}
                  className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold uppercase rounded-lg shadow-lg disabled:opacity-50 transition"
                >
                  Verify Phase Alignment
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- EXPOSURE HEATMAP --- */}
      {activeTab === 'item-exposure' && (
        <div className="space-y-6 relative z-10">
          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Adaptive Question Pool Exposure Metrics</h3>
                <p className="text-xs text-slate-400">Maintains target item exposure bounds to mitigate variant fatigue.</p>
              </div>
              <button
                onClick={() => {
                  setSimIndex((prev) => prev + 1);
                  onLog('Simulation stepped', 'INFO', 'Adaptive item routing simulator ticked next state');
                }}
                className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded font-mono text-xs text-cyan-400 flex items-center gap-1.5 transition"
              >
                <RefreshCw className="w-3 h-3 animate-spin-slow" />
                Trigger Route Tick
              </button>
            </div>

            <div className="space-y-4">
              <span className="text-[10px] font-mono text-slate-500 block uppercase">ITEM EXPOSURE POOL GRID HEATMAP</span>
              <div className="grid grid-cols-8 gap-2 bg-slate-950 p-4 border border-slate-800/80 rounded-xl">
                {Array.from({ length: 24 }).map((_, i) => {
                  const weight = (i * 7 + 13 + simIndex * 3) % 100;
                  const isSelected = selectedSimQuestion === i;
                  
                  return (
                    <button
                      key={i}
                      onClick={() => setSelectedSimQuestion(i)}
                      className={`h-10 rounded transition relative flex flex-col items-center justify-center border ${
                        isSelected 
                          ? 'border-white scale-110 shadow-lg z-10' 
                          : 'border-transparent'
                      } ${
                        weight > 80 
                          ? 'bg-rose-600 text-rose-100 font-bold' 
                          : weight > 50 
                          ? 'bg-amber-500 text-amber-950' 
                          : weight > 20 
                          ? 'bg-cyan-600/70 text-cyan-100' 
                          : 'bg-slate-900 text-slate-500'
                      }`}
                    >
                      <span className="text-[10px] font-mono">Q-{i + 1}</span>
                      <span className="text-[8px] opacity-70">{weight}%</span>
                    </button>
                  );
                })}
              </div>

              {selectedSimQuestion !== null ? (
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs">
                  <h4 className="font-bold text-cyan-300 font-mono mb-1">Item Pool ID: Q-{selectedSimQuestion + 1} Metadata</h4>
                  <div className="grid grid-cols-2 gap-4 text-slate-400 font-mono text-[11px] leading-relaxed">
                    <div>Category: Recursive Logic</div>
                    <div>Difficulty Parameter: +1.42 theta</div>
                    <div>Target Exposure Rate: &le; 20%</div>
                    <div>Actual Exposure Rate: {((selectedSimQuestion * 7 + 13 + simIndex) % 100)}%</div>
                  </div>
                </div>
              ) : (
                <p className="text-[10px] text-slate-500 font-mono text-center">Click any item block on the heatmap to view live parameter logs.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Quick helper to safely assign dynamic profiles or simulated falls
function getGqScores(scores: any) {
  return scores || {
    rawScore: 6,
    normalizedScore: 75,
    percentile: 84,
    subScores: { PatternBot: 92, CompareBot: 81, VisionBot: 89, SolverBot: 74 },
    confidenceScore: 0.92
  };
}
