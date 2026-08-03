import React, { useState, useEffect } from 'react';
import { ScreenId } from '../types';
import { Cpu, Zap, Sliders, ChevronRight, CheckCircle2, AlertTriangle, ShieldCheck, Compass, Play, RefreshCw, RefreshCwIcon, Target } from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';
import { startAssessment, submitAnswer, finishAssessment, getResult } from '../services/assessmentApi';

export const SolverBotScreen: React.FC = () => {
  const { currentScreen, handleChallengeComplete: onComplete, logEvent: onLog, profile } = useAssessment();
  const initialSubMode = currentScreen === 'solver-capacity' ? 'capacity' : currentScreen === 'solver-resource' ? 'resource' : 'route';
  const [subMode, setSubMode] = useState<'capacity' | 'resource' | 'route'>(initialSubMode);

  // Backend integration state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questionId, setQuestionId] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [idleTimeMs] = useState(0);

  useEffect(() => {
    // Start an official backend session for SolverBot standalone challenges
    if (profile) {
      startAssessment(profile.studentId, profile.level, 'GQ01', 'SolverBot')
        .then(res => {
          setSessionId(res.session_id);
          setQuestionId(res.question.question_id);
          onLog('SolverBot Backend Connected', 'INFO', `Tracking session: ${res.session_id}`);
        })
        .catch(err => {
          onLog('SolverBot Connection Error', 'ERROR', err.message);
        });
    }
  }, [profile, onLog]);

  // --- CAPACITY PLANNING STATE ---
  const [capacityTarget, setCapacityTarget] = useState({ alpha: 45, beta: 30, gamma: 25 });
  const [capacityUser, setCapacityUser] = useState({ alpha: 33, beta: 33, gamma: 34 });
  const [capacityError, setCapacityError] = useState('');
  const [capacitySuccess, setCapacitySuccess] = useState(false);

  // --- DRONE LOGISTICS BAY STATE (Screenshot 6) ---
  const [bays, setBays] = useState<{ [key: string]: { name: string; mass: number; icon: string } | null }>({
    BAY_ALPHA: null,
    BAY_BETA: null,
    BAY_GAMMA: null,
    BAY_DELTA: null,
  });
  const [selectedItem, setSelectedItem] = useState<{ id: string; name: string; mass: number; icon: string } | null>(null);
  const [logisticsError, setLogisticsError] = useState('');
  const [logisticsSuccess, setLogisticsSuccess] = useState(false);

  // --- RESOURCE ALLOCATION STATE ---
  const [totalCells] = useState(12);
  const [allocated, setAllocated] = useState({ sectorA: 0, sectorB: 0, sectorC: 0 });
  const [resourceSuccess, setResourceSuccess] = useState(false);
  const [resourceMessage, setResourceMessage] = useState('');

  // --- ROUTE OPTIMIZATION STATE ---
  // Grid size 5x5. 0 = path, 1 = obstacle, 2 = start, 3 = target, 4 = user path
  const [grid, setGrid] = useState<number[][]>([
    [2, 0, 1, 0, 0],
    [0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 3],
  ]);
  const [userPath, setUserPath] = useState<[number, number][]>([]);
  const [routeAnimStep, setRouteAnimStep] = useState(-1);
  const [routeSuccess, setRouteSuccess] = useState(false);
  const [routeError, setRouteError] = useState('');

  // Generate new capacity target
  const handleRandomizeCapacity = () => {
    const a = Math.floor(20 + Math.random() * 40);
    const b = Math.floor(20 + Math.random() * 30);
    const c = 100 - a - b;
    setCapacityTarget({ alpha: a, beta: b, gamma: c });
    setCapacitySuccess(false);
    setCapacityError('');
    onLog('Capacity Targets Re-randomized', 'INFO', `New Targets - Alpha: ${a}%, Beta: ${b}%, Gamma: ${c}%`);
  };

  const handleVerifyCapacity = () => {
    const total = capacityUser.alpha + capacityUser.beta + capacityUser.gamma;
    if (total !== 100) {
      setCapacityError(`Total energy must equal exactly 100% (Current: ${total}%)`);
      onLog('Capacity verification failed', 'WARNING', `User allocated total of ${total}% instead of 100%`);
      return;
    }

    const diffA = Math.abs(capacityUser.alpha - capacityTarget.alpha);
    const diffB = Math.abs(capacityUser.beta - capacityTarget.beta);
    const diffC = Math.abs(capacityUser.gamma - capacityTarget.gamma);

    if (diffA <= 3 && diffB <= 3 && diffC <= 3) {
      setCapacitySuccess(true);
      setCapacityError('');
      onLog('Capacity Planning Verified', 'SUCCESS', 'All reactors stabilized within target tolerance', { capacityUser, capacityTarget });
      
      if (sessionId && questionId) {
        submitAnswer({
          session_id: sessionId,
          question_id: questionId,
          response: JSON.stringify(capacityUser),
          metrics: {
            reaction_time_ms: Date.now() - startTime,
            hover_duration_ms: 0,
            idle_time_ms: idleTimeMs,
            drag_distance: 0,
            answer_changes: 0,
            confidence_score: 5,
            attempt_number: 1,
            difficulty_level: 2,
            module_name: 'SolverBot',
            hint_used: false
          }
        }).then(() => {
          finishAssessment(sessionId).then(res => {
            getResult(res.assessment_id).then(backendRes => {
              onComplete('solver-capacity', 250, null, backendRes);
            });
          });
        });
      } else {
        onComplete('solver-capacity', 250);
      }
    } else {
      setCapacityError('Stabilization ratio outside nominal boundaries (±3% variance threshold). Adjust reactors.');
      onLog('Capacity Planning failed bounds check', 'WARNING', 'Reactor deviation exceeds ±3% tolerance limit');
    }
  };

  // --- RESOURCE ALLOCATION HANDLERS ---
  const remainingCells = totalCells - (allocated.sectorA + allocated.sectorB + allocated.sectorC);

  const handleAdjustResource = (sector: 'sectorA' | 'sectorB' | 'sectorC', amount: number) => {
    const current = allocated[sector];
    const next = current + amount;
    if (next < 0) return;
    if (amount > 0 && remainingCells <= 0) return;

    setAllocated((prev) => ({ ...prev, [sector]: next }));
    setResourceSuccess(false);
    setResourceMessage('');
  };

  const handleVerifyResources = () => {
    if (remainingCells !== 0) {
      setResourceMessage('All 12 Power Cells must be distributed.');
      return;
    }

    // Constraints:
    // Sector A (Neural Hub): needs >= 4 cells
    // Sector B (Cryo Lab): needs <= 5 cells
    // Sector C (Biosphere): needs exactly 3 cells
    const condA = allocated.sectorA >= 4;
    const condB = allocated.sectorB <= 5;
    const condC = allocated.sectorC === 3;

    if (condA && condB && condC) {
      setResourceSuccess(true);
      setResourceMessage('Power grid successfully stabilized. Constraints validated!');
      onLog('Resource allocation constraints satisfied', 'SUCCESS', `Distributed cells - Hub: ${allocated.sectorA}, Cryo: ${allocated.sectorB}, Bio: ${allocated.sectorC}`, allocated);
      if (sessionId && questionId) {
        submitAnswer({
          session_id: sessionId,
          question_id: questionId,
          response: JSON.stringify(allocated),
          metrics: {
            reaction_time_ms: Date.now() - startTime,
            hover_duration_ms: 0,
            idle_time_ms: idleTimeMs,
            drag_distance: 0,
            answer_changes: 0,
            confidence_score: 5,
            attempt_number: 1,
            difficulty_level: 2,
            module_name: 'SolverBot',
            hint_used: false
          }
        }).then(() => {
          finishAssessment(sessionId).then(res => {
            getResult(res.assessment_id).then(backendRes => {
              onComplete('solver-resource', 300, null, backendRes);
            });
          });
        });
      } else {
        onComplete('solver-resource', 300);
      }
    } else {
      let issues = [];
      if (!condA) issues.push('Neural Hub requires at least 4 cells.');
      if (!condB) issues.push('Cryo Lab cannot exceed 5 cells.');
      if (!condC) issues.push('Biosphere Gate requires exactly 3 cells.');
      setResourceMessage(`STABILITY FAILED: ${issues.join(' ')}`);
      onLog('Resource allocation failed constraints', 'WARNING', `Failed to meet criteria: ${issues.join('; ')}`);
    }
  };

  // --- ROUTE OPTIMIZATION HANDLERS ---
  const handleCellClick = (r: number, c: number) => {
    if (routeSuccess) return;
    const cell = grid[r][c];
    if (cell === 1) {
      onLog('Grid path click blocked', 'WARNING', `Clicked obstacle cell at [${r}, ${c}]`);
      return; // obstacle
    }

    // Check if cell is already in userPath
    const isAlreadyInPath = userPath.some(([pr, pc]) => pr === r && pc === c);
    let nextPath: [number, number][] = [];

    if (isAlreadyInPath) {
      nextPath = userPath.filter(([pr, pc]) => !(pr === r && pc === c));
    } else {
      // Must be adjacent to start or the last item in the path
      if (userPath.length === 0) {
        // Must be adjacent to start node [0, 0]
        if (Math.abs(r - 0) + Math.abs(c - 0) !== 1) {
          setRouteError('Direct path link must start adjacent to start node');
          return;
        }
      } else {
        const [lastR, lastC] = userPath[userPath.length - 1];
        if (Math.abs(r - lastR) + Math.abs(c - lastC) !== 1) {
          setRouteError('Direct path link must connect adjacently');
          return;
        }
      }
      nextPath = [...userPath, [r, c]];
    }

    setUserPath(nextPath);
    setRouteError('');
    onLog('Path vector modified', 'INFO', `User route coordinates updated to ${JSON.stringify(nextPath)}`);
  };

  const handleVerifyRoute = () => {
    if (userPath.length === 0) {
      setRouteError('Please construct a path from Start (Top-Left) to Target (Bottom-Right)');
      return;
    }

    // Must end adjacent to Target [4, 4]
    const [lastR, lastC] = userPath[userPath.length - 1];
    if (Math.abs(lastR - 4) + Math.abs(lastC - 4) !== 1) {
      setRouteError('Constructed route does not connect to Target Core (Bottom-Right)');
      onLog('Route verification failed', 'WARNING', 'Route does not terminate at target');
      return;
    }

    // Success! Animate route
    setRouteError('');
    setRouteAnimStep(0);
  };

  useEffect(() => {
    if (routeAnimStep >= 0 && routeAnimStep <= userPath.length) {
      const interval = setTimeout(() => {
        setRouteAnimStep((prev) => prev + 1);
      }, 300);
      return () => clearTimeout(interval);
    } else if (routeAnimStep > userPath.length) {
      setRouteSuccess(true);
      onLog('Route navigation completed successfully', 'SUCCESS', 'Navigation drone reached Target Core with nominal efficiency', { userPath });
      if (sessionId && questionId) {
        submitAnswer({
          session_id: sessionId,
          question_id: questionId,
          response: JSON.stringify(userPath),
          metrics: {
            reaction_time_ms: Date.now() - startTime,
            hover_duration_ms: 0,
            idle_time_ms: idleTimeMs,
            drag_distance: 0,
            answer_changes: 0,
            confidence_score: 5,
            attempt_number: 1,
            difficulty_level: 2,
            module_name: 'SolverBot',
            hint_used: false
          }
        }).then(() => {
          finishAssessment(sessionId).then(res => {
            getResult(res.assessment_id).then(backendRes => {
              onComplete('solver-route', 350, null, backendRes);
            });
          });
        });
      } else {
        onComplete('solver-route', 350);
      }
    }
  }, [routeAnimStep, userPath, onComplete, onLog, sessionId, questionId, startTime, idleTimeMs]);

  const handleResetRoute = () => {
    setUserPath([]);
    setRouteAnimStep(-1);
    setRouteSuccess(false);
    setRouteError('');
    onLog('Route planner purged', 'INFO', 'Clean grid initialized');
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl text-slate-100 font-sans flex flex-col h-full">
      {/* Sub-modes selection header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-cyan-400 flex items-center gap-2">
            <Cpu className="w-5 h-5 animate-pulse" />
            SOLVERBOT OPTIMIZATION CONSOLE
          </h2>
          <p className="text-xs text-slate-400">Tactical mathematical and spatial network challenges</p>
        </div>

        <div className="flex gap-1.5 bg-slate-900/60 p-1 rounded-lg border border-slate-800">
          {(['capacity', 'resource', 'route'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => {
                setSubMode(mode);
                onLog('SolverBot Challenge mode changed', 'INFO', `Switched SolverBot to ${mode} mode`);
              }}
              className={`px-3 py-1.5 rounded text-xs font-semibold font-mono tracking-wide uppercase transition ${
                subMode === mode
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Mode 1: CAPACITY PLANNING (Logistics Bay Drone Cargo Optimization - Screenshot 6) */}
      {subMode === 'capacity' && (
        <div className="space-y-6">
          {/* Header Block matching Screenshot 6 */}
          <div className="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
            <div>
              <h1 className="text-xl font-black text-slate-100 tracking-widest font-mono">
                OPTIMIZATION COMPLETE
              </h1>
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                AWAITING MANUAL VERIFICATION
              </span>
            </div>
            <div className="text-right font-mono text-[10px] text-slate-500">
              <div>PROTOCOL_SEC_20</div>
              <div className="text-cyan-400 font-bold">GRID_LINK_READY</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Card: Active Drone Bays (Col span 7) */}
            <div className="lg:col-span-7 bg-slate-900/40 border border-slate-800/80 p-5 rounded-xl flex flex-col font-mono relative">
              <div className="flex justify-between items-center mb-5 border-b border-slate-850 pb-2">
                <h3 className="text-xs font-black uppercase tracking-widest text-slate-200">
                  DRONE BAYS
                </h3>
                <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                  LIVE_FEED: SEC_LOG_01
                </span>
              </div>

              {/* 4 bays list */}
              <div className="space-y-3 flex-1">
                {[
                  { key: 'BAY_ALPHA', label: 'BAY_ALPHA', expected: 'ISOTOPE_V8', hint: 'Requires High Mass Reactor Source' },
                  { key: 'BAY_BETA', label: 'BAY_BETA', expected: 'CRYO_SAMP_A', hint: 'Requires Low Temp Biological Specimen' },
                  { key: 'BAY_GAMMA', label: 'BAY_GAMMA', expected: 'CORE_LINK_09', hint: 'Requires Neural Link Module' },
                  { key: 'BAY_DELTA', label: 'BAY_DELTA', expected: 'ISOTOPE_V8', hint: 'Requires High Mass Reactor Source' },
                ].map((bay) => {
                  const assigned = bays[bay.key];
                  const isCorrect = assigned?.name === bay.expected;
                  
                  return (
                    <div 
                      key={bay.key}
                      onClick={() => {
                        if (logisticsSuccess) return;
                        if (selectedItem) {
                          // Assign selected item to this bay
                          setBays(prev => ({ ...prev, [bay.key]: selectedItem }));
                          setSelectedItem(null);
                          setLogisticsError('');
                          onLog('Cargo Assigned to Bay', 'INFO', `Placed ${selectedItem.name} into ${bay.label}`);
                        } else if (assigned) {
                          // Clear this bay
                          setBays(prev => ({ ...prev, [bay.key]: null }));
                          onLog('Cargo Removed from Bay', 'INFO', `Cleared cargo from ${bay.label}`);
                        }
                      }}
                      className={`p-3.5 rounded-lg border text-left transition cursor-pointer flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 ${
                        assigned 
                          ? isCorrect 
                            ? 'bg-emerald-950/20 border-emerald-500/40 hover:border-emerald-400' 
                            : 'bg-rose-950/10 border-rose-500/30 hover:border-rose-400'
                          : selectedItem 
                          ? 'bg-cyan-950/15 border-cyan-500/30 border-dashed hover:border-cyan-400 animate-pulse'
                          : 'bg-slate-950/60 border-slate-850 hover:border-slate-800'
                      }`}
                    >
                      <div>
                        <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">{bay.label}</span>
                        {assigned ? (
                          <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                            <span className="text-xs font-bold text-slate-200 uppercase">
                              {assigned.name}
                            </span>
                            <span className="text-[10px] text-slate-500 font-mono">
                              / MASS: {assigned.mass}KG
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-600 block mt-1 italic uppercase">
                            {selectedItem ? 'Click here to allocate selected cargo' : 'Empty - Click component to assign'}
                          </span>
                        )}
                      </div>
                      
                      <div className="sm:text-right">
                        {assigned ? (
                          <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                            isCorrect 
                              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                              : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
                          }`}>
                            {isCorrect ? 'READY_TO_DEPLOY' : 'CALIBRATION_MISMATCH'}
                          </span>
                        ) : (
                          <span className="text-[9px] text-slate-500 italic block">{bay.hint}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Carrier Efficiency Progress Bar matching Screenshot 6 */}
              {(() => {
                // Calculate efficiency
                let correctCount = 0;
                if (bays.BAY_ALPHA?.name === 'ISOTOPE_V8') correctCount++;
                if (bays.BAY_BETA?.name === 'CRYO_SAMP_A') correctCount++;
                if (bays.BAY_GAMMA?.name === 'CORE_LINK_09') correctCount++;
                if (bays.BAY_DELTA?.name === 'ISOTOPE_V8') correctCount++;
                
                // Base is 35%. 3 correct is exactly 84.2%. 4 is 100%.
                const efficiency = correctCount === 4 ? 100 : 35 + (correctCount * 16.4);
                
                return (
                  <div className="mt-6 border-t border-slate-850 pt-5">
                    <div className="flex justify-between text-xs mb-2">
                      <span className="text-slate-400 font-bold uppercase tracking-wider">CARRIER EFFICIENCY</span>
                      <span className={`font-black ${efficiency === 100 ? 'text-emerald-400' : 'text-cyan-400'}`}>
                        {efficiency.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 p-0.5">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${
                          efficiency === 100 ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-cyan-400'
                        }`} 
                        style={{ width: `${efficiency}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Right Card: Cargo Manifest (Col span 5) */}
            <div className="lg:col-span-5 bg-slate-900/40 border border-slate-800/80 p-5 rounded-xl flex flex-col font-mono">
              <div className="flex justify-between items-center mb-5 border-b border-slate-850 pb-2">
                <h3 className="text-xs font-black uppercase tracking-widest text-slate-200">
                  CARGO MANIFEST
                </h3>
                <span className="text-[10px] text-slate-500">REF_ID: CT-42</span>
              </div>

              {/* Items List matching Screenshot 6 */}
              <div className="space-y-3 flex-1">
                {[
                  { id: 'item_1', name: 'ISOTOPE_V8', mass: 48, icon: '📦', description: 'Heavy nuclear reactor payload' },
                  { id: 'item_2', name: 'CRYO_SAMP_A', mass: 25, icon: '🧪', description: 'Low temperature biosphere capsule' },
                  { id: 'item_3', name: 'CORE_LINK_09', mass: 15, icon: '💾', description: 'Central algorithmic synapse processor' },
                ].map((item) => {
                  const isSelected = selectedItem?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        if (logisticsSuccess) return;
                        setSelectedItem(isSelected ? null : item);
                        setLogisticsError('');
                      }}
                      className={`w-full p-3 rounded-lg border text-left transition ${
                        isSelected 
                          ? 'bg-cyan-500/10 border-cyan-400 text-cyan-300' 
                          : 'bg-slate-950/80 border-slate-850 hover:border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <span className="text-base">{item.icon}</span>
                          <div>
                            <span className="text-xs font-bold block text-slate-200">{item.name}</span>
                            <span className="text-[9px] text-slate-500 block">{item.description}</span>
                          </div>
                        </div>
                        <span className="text-[10px] font-bold text-slate-400">
                          MASS: {item.mass}KG
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Cargo Remaining calculations */}
              {(() => {
                let totalAssignedMass = 0;
                Object.values(bays).forEach(v => { if (v) totalAssignedMass += v.mass; });
                const remainingCargo = 160 - totalAssignedMass;

                return (
                  <div className="mt-6 space-y-4 border-t border-slate-850 pt-4">
                    <div className="flex justify-between items-center text-xs font-bold">
                      <span className="text-slate-500">CARGO REMAINING:</span>
                      <span className="text-cyan-400 bg-cyan-950/40 px-2 py-0.5 border border-cyan-800/30 rounded">
                        {remainingCargo} KG
                      </span>
                    </div>

                    {/* Drag and Drop instructions warning block matching Screenshot 6 */}
                    <div className="bg-slate-950/80 border border-slate-850 p-3 rounded-lg text-[10px] text-slate-500 leading-relaxed uppercase">
                      Drag components or select a manifest component on the right, then click a target bay on the left to finalize drone distribution.
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>

          {/* Feedback messages */}
          {logisticsError && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4.5 h-4.5 text-rose-400 flex-shrink-0" />
              <span>{logisticsError}</span>
            </div>
          )}

          {logisticsSuccess && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400 flex-shrink-0" />
              <span>LOGISTICS DISTRIBUTION VERIFIED. Optimal drone loading efficiency achieved!</span>
            </div>
          )}

          {/* Bottom Bar Controls matching Screenshot 6 */}
          <div className="flex justify-between items-center border-t border-slate-800/80 pt-5 mt-6 font-mono">
            {/* Skip Step on Left */}
            <button
              onClick={() => {
                // Auto solve and advance
                setBays({
                  BAY_ALPHA: { name: 'ISOTOPE_V8', mass: 48, icon: '📦' },
                  BAY_BETA: { name: 'CRYO_SAMP_A', mass: 25, icon: '🧪' },
                  BAY_GAMMA: { name: 'CORE_LINK_09', mass: 15, icon: '💾' },
                  BAY_DELTA: { name: 'ISOTOPE_V8', mass: 48, icon: '📦' },
                });
                setLogisticsSuccess(true);
                setLogisticsError('');
                onLog('Drone Logistics Bay Bypassed', 'WARNING', 'Logistics planning manual verification auto-solved.');
                onComplete('solver-capacity', 150);
                setSubMode('resource');
              }}
              className="px-4 py-2 border border-slate-800 hover:border-slate-700 rounded-lg text-xs font-bold text-slate-500 hover:text-slate-300 transition"
            >
              [ SKIP_STEP ]
            </button>

            {/* Stepper Dots in Center */}
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#22d3ee]"></span>
              <button onClick={() => setSubMode('resource')} className="w-2 h-2 rounded-full bg-slate-800 hover:bg-slate-600 transition"></button>
              <button onClick={() => setSubMode('route')} className="w-2 h-2 rounded-full bg-slate-800 hover:bg-slate-600 transition"></button>
            </div>

            {/* Submit Calc Glowing Button on Right */}
            <button
              onClick={() => {
                let correctCount = 0;
                if (bays.BAY_ALPHA?.name === 'ISOTOPE_V8') correctCount++;
                if (bays.BAY_BETA?.name === 'CRYO_SAMP_A') correctCount++;
                if (bays.BAY_GAMMA?.name === 'CORE_LINK_09') correctCount++;
                if (bays.BAY_DELTA?.name === 'ISOTOPE_V8') correctCount++;

                if (correctCount === 4) {
                  setLogisticsSuccess(true);
                  setLogisticsError('');
                  onLog('Drone Cargo Optimization Complete', 'SUCCESS', 'All bays loaded with optimal components and verified.');
                  onComplete('solver-capacity', 250);
                  // Advance to next challenge
                  setTimeout(() => {
                    setSubMode('resource');
                  }, 1200);
                } else {
                  setLogisticsError(`UNBALANCED DISTRIBUTION. Carrier efficiency at ${(35 + correctCount * 16.4).toFixed(1)}% / 100%. Adjust cargo components.`);
                  onLog('Logistics validation failed', 'WARNING', 'Efficiency below nominal thresholds.');
                }
              }}
              className="px-6 py-2.5 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold uppercase tracking-widest rounded-lg transition-all duration-300 text-xs shadow-[0_0_12px_rgba(34,211,238,0.25)] hover:shadow-[0_0_20px_rgba(34,211,238,0.4)]"
            >
              SUBMIT_CALC →
            </button>
          </div>
        </div>
      )}

      {/* Mode 2: RESOURCE ALLOCATION */}
      {subMode === 'resource' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-200">CHALLENGE: Multi-Secteur Power Grid</h3>
              <p className="text-xs text-slate-400">
                You must distribute exactly 12 power cells according to the strict network constraints below.
              </p>
            </div>

            {/* Constraints display */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] font-mono text-cyan-400 block">Secteur A: Neural Hub</span>
                <span className="text-xs font-semibold block text-slate-300 mt-1">Needs &ge; 4 Cells</span>
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] font-mono text-violet-400 block">Secteur B: Cryo Lab</span>
                <span className="text-xs font-semibold block text-slate-300 mt-1">Needs &le; 5 Cells</span>
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] font-mono text-emerald-400 block">Secteur C: Biosphere</span>
                <span className="text-xs font-semibold block text-slate-300 mt-1">Needs EXACTLY 3 Cells</span>
              </div>
            </div>

            {/* Sliders / Counters */}
            <div className="space-y-4">
              {[
                { key: 'sectorA', label: 'Secteur A: Neural Hub Cells', color: 'text-cyan-400' },
                { key: 'sectorB', label: 'Secteur B: Cryo Lab Cells', color: 'text-violet-400' },
                { key: 'sectorC', label: 'Secteur C: Biosphere Cells', color: 'text-emerald-400' },
              ].map((sect) => (
                <div key={sect.key} className="bg-slate-950 border border-slate-800/80 p-4 rounded-xl flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-300">{sect.label}</h4>
                    <span className="text-[10px] text-slate-500 font-mono block">Status: Nominally Calibrated</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleAdjustResource(sect.key as 'sectorA' | 'sectorB' | 'sectorC', -1)}
                      disabled={resourceSuccess}
                      className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-white disabled:opacity-30"
                    >
                      -
                    </button>
                    <span className={`font-mono text-lg font-bold w-6 text-center ${sect.color}`}>
                      {allocated[sect.key as 'sectorA' | 'sectorB' | 'sectorC']}
                    </span>
                    <button
                      onClick={() => handleAdjustResource(sect.key as 'sectorA' | 'sectorB' | 'sectorC', 1)}
                      disabled={resourceSuccess || remainingCells <= 0}
                      className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-white disabled:opacity-30"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center text-xs font-mono border-t border-slate-800 pt-4 mt-6">
              <span className="text-slate-400">DISTRIBUTED: {12 - remainingCells} / 12 CELLS</span>
              <span className={`font-bold ${remainingCells === 0 ? 'text-emerald-400' : 'text-cyan-400'}`}>
                CELLS REMAINING: {remainingCells}
              </span>
            </div>
          </div>

          {resourceMessage && (
            <div className={`border px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2 ${
              resourceSuccess 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}>
              {resourceSuccess ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              )}
              <span>{resourceMessage}</span>
            </div>
          )}

          <button
            onClick={handleVerifyResources}
            disabled={resourceSuccess}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold uppercase rounded-lg shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50 transition"
          >
            Apply Energy Distribution Load
          </button>
        </div>
      )}

      {/* Mode 3: ROUTE OPTIMIZATION */}
      {subMode === 'route' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-200">CHALLENGE: Micro-Drone Mapping</h3>
                <p className="text-xs text-slate-400">
                  Construct a path from start <span className="text-cyan-400 font-bold">▲ (Top Left)</span> to target <span className="text-rose-400 font-bold">◆ (Bottom Right)</span> without hitting critical network blockages.
                </p>
              </div>
              <button
                onClick={handleResetRoute}
                className="p-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs font-mono text-cyan-400 flex items-center gap-1.5 transition"
              >
                <RefreshCwIcon className="w-3.5 h-3.5" />
                Reset Route
              </button>
            </div>

            {/* 5x5 Grid mapping */}
            <div className="flex justify-center my-6">
              <div className="grid grid-cols-5 gap-2 bg-slate-950 p-4 border border-slate-800/80 rounded-xl">
                {grid.map((row, r) =>
                  row.map((cell, c) => {
                    const isStart = r === 0 && c === 0;
                    const isTarget = r === 4 && c === 4;
                    const isObstacle = cell === 1;
                    const isInUserPath = userPath.some(([pr, pc]) => pr === r && pc === c);
                    
                    // Determine if currently animated
                    const isCurrentDronePos = routeAnimStep >= 0 && (
                      routeAnimStep < userPath.length 
                        ? userPath[routeAnimStep][0] === r && userPath[routeAnimStep][1] === c
                        : r === 4 && c === 4
                    );

                    return (
                      <button
                        key={`${r}-${c}`}
                        onClick={() => handleCellClick(r, c)}
                        disabled={routeSuccess || isStart || isTarget}
                        className={`w-12 h-12 rounded-lg flex items-center justify-center font-mono font-bold text-sm transition relative ${
                          isCurrentDronePos
                            ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-500/40 border-2 border-white scale-105 animate-pulse'
                            : isStart
                            ? 'bg-cyan-500/20 border border-cyan-500 text-cyan-300'
                            : isTarget
                            ? 'bg-rose-500/20 border border-rose-500 text-rose-300'
                            : isObstacle
                            ? 'bg-slate-800 text-slate-600 border border-transparent'
                            : isInUserPath
                            ? 'bg-cyan-600/60 border border-cyan-400 text-cyan-100 shadow-inner'
                            : 'bg-slate-900 hover:bg-slate-850 border border-slate-800/80 text-slate-500'
                        }`}
                      >
                        {isCurrentDronePos ? (
                          <Target className="w-5 h-5 animate-spin-slow" />
                        ) : isStart ? (
                          'START'
                        ) : isTarget ? (
                          'TGT'
                        ) : isObstacle ? (
                          '✕'
                        ) : isInUserPath ? (
                          userPath.findIndex(([pr, pc]) => pr === r && pc === c) + 1
                        ) : (
                          ''
                        )}
                      </button>
                    );
                  })
                )}
              </div>
            </div>

            <p className="text-[10px] text-slate-500 text-center font-mono uppercase">
              Click consecutive adjacent grid cells to construct path routing.
            </p>
          </div>

          {routeError && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{routeError}</span>
            </div>
          )}

          {routeSuccess && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>NAVIGATION COMPLETE. Drone vector alignment achieved. Challenge stabilized.</span>
            </div>
          )}

          <button
            onClick={handleVerifyRoute}
            disabled={routeSuccess || routeAnimStep >= 0}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold uppercase rounded-lg shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50 transition flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-current" />
            Execute Path Optimization Route
          </button>
        </div>
      )}
    </div>
  );
};
