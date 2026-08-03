import React, { useState, useEffect, useRef } from 'react';
import { ScreenId, StudentProfile, AppEvent } from '../types';
import { type Question } from '../utils/itemGenerator';
import {
  startAssessment,
  submitAnswer,
  finishAssessment,
  getResult,
  type AssessmentResult,
  type SubmitAnswerPayload,
} from '../services/assessmentApi';
import {
  Play, Pause, Award, Brain, HelpCircle, ArrowRight, ShieldAlert,
  CheckCircle2, AlertTriangle, Eye, RefreshCw, Star, Info, Cpu, HelpCircle as HelpIcon
} from 'lucide-react';

import { useAssessment } from '../context/AssessmentContext';

export const GqAssessment: React.FC = () => {
  const { 
    profile, 
    handleCompleteSession: onCompleteSession, 
    logEvent: onLog, 
    handleNavigate: onNavigate,
    sessionId, setSessionId,
    assessmentId, setAssessmentId,
    backendResult: assessmentResult, setBackendResult: setAssessmentResult
  } = useAssessment();

  // Session parameters
  const [totalQuestions] = useState(8);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentLevel, setCurrentLevel] = useState<number>(() => {
    if (profile?.tier === 'Specialist') return 3;
    if (profile?.tier === 'Adept') return 2;
    return 1;
  });

  const [sessionEvents, setSessionEvents] = useState<AppEvent[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [submittedAnswer, setSubmittedAnswer] = useState<string>('');
  const [showHint, setShowHint] = useState<boolean>(false);
  const [attempts, setAttempts] = useState<number>(0);
  const [userConfidence, setUserConfidence] = useState<number>(4); // default 4/5 confidence
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [correctCount, setCorrectCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [apiStatus, setApiStatus] = useState<string>('idle');
  
  // Tracking metrics
  const questionLoadTime = useRef<number>(Date.now());
  const hoverStartTime = useRef<number | null>(null);
  const totalHoverDuration = useRef<number>(0);
  const totalDragDistance = useRef<number>(0);
  const answerChangesCount = useRef<number>(0);
  const idleTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastActiveTime = useRef<number>(Date.now());
  const [idleTimeMs, setIdleTimeMs] = useState<number>(0);


  const lastMousePosition = useRef<{ x: number; y: number } | null>(null);
  const handleMouseMove = (event: React.MouseEvent) => {
    recordActivity();
    if (lastMousePosition.current) {
      const dx = event.clientX - lastMousePosition.current.x;

      const dy = event.clientY - lastMousePosition.current.y;

      totalDragDistance.current += Math.sqrt(dx * dx + dy * dy);
    }

    lastMousePosition.current = {
      x: event.clientX,

      y: event.clientY,
    
    };
  };

  // For exposure control tracking (Deliverable 4)
  const previousTemplateId = useRef<string>('');
  const [moduleLevels, setModuleLevels] = useState<{ [key: string]: number }>({
    PatternBot: currentLevel,
    CompareBot: currentLevel,
    VisionBot: currentLevel,
    SolverBot: currentLevel
  });

  // Keep track of score outputs per question for the learning curve (Deliverable 6)
  const [historyPoints, setHistoryPoints] = useState<{
    index: number;
    moduleId: string;
    templateId: string;
    itemId: string;
    difficulty: number;
    correct: boolean;
    timeMs: number;
    perfScore: number;
    reactionTime: number,
    hoverTime: number,
    idleTime: number,
    answerChanges: number,
    confidence: number,
    hintUsed: boolean,
  }[]>([]);

  // Setup initial session event
  useEffect(() => {
    void initializeAssessment();
  }, [profile?.studentId]);

  // Idle timer check
  useEffect(() => {
    const checkIdle = setInterval(() => {
      if (isPaused) return;
      const diff = Date.now() - lastActiveTime.current;
      if (diff > 3000) { // idle after 3s
        setIdleTimeMs((prev) => prev + 1000);
      }
    }, 1000);
    return () => clearInterval(checkIdle);
  }, [isPaused]);

  const recordActivity = () => {
    lastActiveTime.current = Date.now();
  };

  // Log local events and stream them to App.tsx too
  const logLocalEvent = (
    action: string,
    status: 'SUCCESS' | 'INFO' | 'WARNING' | 'ERROR',
    details: string,
    payload?: any
  ): AppEvent => {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    const newEvent: AppEvent = {
      id: `evt-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: timeStr,
      screen: 'cognitive-analytics', // track under assessment screen
      action,
      status,
      details,
      payload
    };
    onLog(action, status, details, payload);
    setSessionEvents((prev) => [newEvent, ...prev]);
    return newEvent;
  };

  const resetQuestionState = () => {
    setSelectedAnswer('');
    setSubmittedAnswer('');
    setShowHint(false);
    setAttempts(0);
    setUserConfidence(4);
    setIdleTimeMs(0);
    totalHoverDuration.current = 0;
    totalDragDistance.current = 0;
    answerChangesCount.current = 0;
    questionLoadTime.current = Date.now();
  };

  const mapBackendQuestion = (payload: any, levelOverride?: number): Question => {
    const module = payload.module || 'PatternBot';
    const parsedSequence = (payload.question || '').match(/-?\d+/g)?.map(Number) || [];
    const difficultyLevel = payload.difficulty || levelOverride || 1;
    const normalizedOptions = (payload.options || []).map((option: unknown) => String(option));
    const normalizedCorrectAnswer = String(payload.correct_answer ?? normalizedOptions[0] ?? '');

    return {
      id: payload.question_id || `${module}-${Date.now()}`,
      templateId: payload.template_id || `${module}-T01`,
      module: module as Question['module'],
      templateName: module,
      difficultyLevel,
      calculatedDifficulty: Number((difficultyLevel * 0.8 + 1.2).toFixed(2)),
      calibration: {
        rc: difficultyLevel,
        cs: Math.max(1, difficultyLevel - 1),
        rp: Math.max(1, difficultyLevel - 2),
        wm: Math.max(1, difficultyLevel - 1),
        dc: Math.max(1, difficultyLevel - 2),
        vp: Math.max(1, difficultyLevel - 3),
        cl: Math.max(1, difficultyLevel),
        t: difficultyLevel,
      },
      storyTheme: payload.story || module,
      narrative: payload.story || `Adaptive ${module} question loaded from the backend.`,
      data: payload.data || {},
      questionText: payload.question || 'No question text returned by the backend.',
      options: normalizedOptions,
      correctAnswer: normalizedCorrectAnswer,
      hint: payload.hint || '',
      errorTypes: {},
    };
  };

  const initializeAssessment = async () => {
    setLoading(true);
    setApiStatus('loading');
    recordActivity();

    try {
      const response = await startAssessment(profile?.studentId || 'GUEST', currentLevel);
      setAssessmentId(response.assessment_id);
      setSessionId(response.session_id);
      const mappedQuestion = mapBackendQuestion(response.question, currentLevel);
      setCurrentQuestion(mappedQuestion);
      setApiStatus('ready');
      setCurrentIndex(0);
      resetQuestionState();
      setCurrentLevel(response.question.difficulty || currentLevel);

      logLocalEvent('SESSION_START', 'SUCCESS', 'Assessment session launched through the FastAPI backend.', {
        student_id: response.student_id,
        assessment_id: response.assessment_id,
        session_id: response.session_id,
        baseline_level: currentLevel,
      });

      logLocalEvent('QUESTION_LOADED', 'INFO', `Loaded backend item ${response.question.question_id} (level ${response.question.difficulty})`, {
        itemId: response.question.question_id,
        templateId: response.question.template_id,
      });
    } catch (error: any) {
      setApiStatus('error');
      logLocalEvent('ASSESSMENT_START_FAILED', 'ERROR', error?.message || 'Unable to start the assessment.', {
        error: error?.message,
      });
    } finally {
      setTimeout(() => setLoading(false), 300);
    }
  };

  // Interaction logs (hover/drags)
  const handleMouseEnterOption = () => {
    recordActivity();
    hoverStartTime.current = Date.now();
  };

  const handleMouseLeaveOption = () => {
    recordActivity();
    if (hoverStartTime.current) {
      const dur = Date.now() - hoverStartTime.current;
      totalHoverDuration.current += dur;
      hoverStartTime.current = null;
    }
  };

  const handleOptionChange = (ans: string) => {
    recordActivity();
    if (selectedAnswer && selectedAnswer !== ans) {
      answerChangesCount.current++;
      logLocalEvent('ANSWER_CHANGED', 'INFO', `User changed choice selection from ${selectedAnswer} to ${ans}`);
    } else {
      logLocalEvent('FIRST_RESPONSE', 'INFO', `User checked first choice: ${ans}`);
    }
    setSelectedAnswer(ans);
  };

  const handleToggleHint = () => {
    recordActivity();
    const nextState = !showHint;
    setShowHint(nextState);
    if (nextState) {
      logLocalEvent('HINT_OPENED', 'WARNING', `Student requested cognitive hint assistance for ${currentQuestion?.id}`);
    } else {
      logLocalEvent('HINT_CLOSED', 'INFO', 'Hint dialogue dismissed');
    }
  };

  const handlePauseToggle = () => {
    recordActivity();
    const nextState = !isPaused;
    setIsPaused(nextState);
    logLocalEvent(nextState ? 'PAUSE' : 'RESUME', 'WARNING', nextState ? 'Session execution suspended' : 'Session execution restored');
  };

  const handleSubmit = async () => {
    if (!selectedAnswer || !currentQuestion || !sessionId) return;
    recordActivity();

    const reactionTime = Date.now() - questionLoadTime.current;
    const nextAttempts = attempts + 1;
    setAttempts(nextAttempts);
    setSubmittedAnswer(selectedAnswer);

    const payload: SubmitAnswerPayload = {
      session_id: sessionId,
      question_id: currentQuestion.id,
      response: selectedAnswer,

      metrics: {
        
        reaction_time_ms: reactionTime,

        hover_duration_ms: totalHoverDuration.current,

        idle_time_ms: idleTimeMs,

        drag_distance: totalDragDistance.current,

        answer_changes: answerChangesCount.current,

        confidence_score: userConfidence,

        attempt_number: nextAttempts,

        difficulty_level: currentQuestion.difficultyLevel,

        module_name: currentQuestion.module,

        hint_used: showHint,
      }
    };

    try {
      const response = await submitAnswer(payload);
      const nextCorrectCount = correctCount + (response.correct ? 1 : 0);
      setCorrectCount(nextCorrectCount);
      setCurrentLevel(response.next_level);
      setModuleLevels(prev => ({
        ...prev,
        [currentQuestion.module]: response.next_level,
      }));

      logLocalEvent('ANSWER_SUBMITTED', response.correct ? 'SUCCESS' : 'ERROR',
        response.correct
          ? `Backend accepted the answer for item ${currentQuestion.id}`
          : `Backend marked the answer as incorrect for item ${currentQuestion.id}`,
        {
          item_id: currentQuestion.id,
          module: currentQuestion.module,
          template_id: currentQuestion.templateId,
          user_response: selectedAnswer,
          reaction_time_ms: reactionTime,
          hover_duration_ms: totalHoverDuration.current,
          idle_time_ms: idleTimeMs,
          drag_distance: totalDragDistance.current,
          answer_changes: answerChangesCount.current,
          confidence_score: userConfidence,
          hint_used: showHint,
          attempt_number: nextAttempts,
          difficulty_level: currentQuestion.difficultyLevel,
          correct: response.correct,
          next_level: response.next_level,
        }
      );

      const nextPoints = [
        ...historyPoints,
        {
          index: currentIndex,
          moduleId: currentQuestion.module,
          templateId: currentQuestion.templateId,
          itemId: currentQuestion.id,
          difficulty: currentQuestion.calculatedDifficulty,
          correct: response.correct,
          timeMs: reactionTime,
          perfScore: response.correct ? 100 : 20,
          reactionTime: reactionTime,
          hoverTime: totalHoverDuration.current,
          idleTime: idleTimeMs,
          answerChanges: answerChangesCount.current,
          confidence: userConfidence,
          hintUsed: showHint,
        }
      ];
      setHistoryPoints(nextPoints);

      if (currentIndex + 1 >= totalQuestions) {
        const finished = await finishAssessment(sessionId);
        const result = await getResult(finished.assessment_id);
        setAssessmentResult(result);
        logLocalEvent('SESSION_END', 'SUCCESS', 'Assessment completed and backend report loaded.', {
          assessment_id: finished.assessment_id,
          result,
        });

        // Calculate base score from correct answers
        const baseScore = (nextCorrectCount / totalQuestions) * 100;
        
        // Time bonus: avg target is ~4000ms per question. Faster = small boost
        const avgReactionTime = result?.metrics?.average_reaction_time || 4000;
        const timeBonusFactor = Math.max(0.9, Math.min(1.2, 4000 / avgReactionTime)); 
        
        // Final Normalized Score (max 100)
        const normalizedScore = Math.min(100, Math.round(baseScore * timeBonusFactor));
        
        const percentile = Math.round(70 + (normalizedScore / 100) * 28);
        const metrics = result?.metrics || {};
        
        const subScores = {
          PatternBot: metrics.pattern_recognition_score || normalizedScore,
          CompareBot: metrics.quantitative_comparison_score || normalizedScore,
          VisionBot: metrics.arithmetic_reasoning_score || normalizedScore,
          SolverBot: metrics.problem_solving_score || normalizedScore,
        };

        onCompleteSession({
          rawScore: nextCorrectCount,
          normalizedScore,
          percentile,
          subScores,
          confidenceScore: metrics.average_confidence ? Number((metrics.average_confidence / 5).toFixed(2)) : Number((0.7 + (nextCorrectCount / totalQuestions) * 0.28).toFixed(2)),
        }, sessionEvents, result);
        return;
      }

      setTimeout(() => {
        setCurrentQuestion(mapBackendQuestion(response.next_question, response.next_level));
        setCurrentIndex((prev) => prev + 1);
        resetQuestionState();
        setLoading(false);
        logLocalEvent('QUESTION_LOADED', 'INFO', `Advanced to backend item ${response.next_question.question_id}`, {
          itemId: response.next_question.question_id,
          templateId: response.next_question.template_id,
        });
      }, 1200);
    } catch (error: any) {
      logLocalEvent('ANSWER_SUBMISSION_FAILED', 'ERROR', error?.message || 'Unable to submit the answer.', {
        error: error?.message,
      });
    }
  };

  if (!currentQuestion) return null;

  return (
    <div className="max-w-4xl mx-auto bg-slate-950 border border-cyan-500/30 rounded-2xl p-6 shadow-2xl text-slate-100 font-sans flex flex-col relative overflow-hidden"
      onMouseMove={handleMouseMove}>
    
      {/* Visual cyber-grid layout */}
      <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>

      {/* Header bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800 pb-4 mb-6 gap-4 relative z-10">
        <div>
          <span className="text-[10px] font-mono font-bold tracking-widest text-cyan-400 uppercase flex items-center gap-1.5">
            <Brain className="w-3.5 h-3.5" /> MentiScope Gq Adaptive Engine // Bayesian Real-Time Calibrator
          </span>
          <h2 className="text-2xl font-black text-slate-100 flex items-center gap-2">
            ACTIVE ASSESSMENT CYCLE
            <span className="text-xs font-mono font-bold bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded">
              NODE {currentIndex + 1} OF {totalQuestions}
            </span>
          </h2>
        </div>

        <div className="flex items-center gap-3">
          {/* Pause Button */}
          <button
            onClick={handlePauseToggle}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-xs border transition duration-200 ${
              isPaused 
                ? 'bg-amber-500/20 border-amber-500 text-amber-300' 
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            {isPaused ? 'RESUME VECTORS' : 'PAUSE TELEMETRY'}
          </button>
        </div>
      </div>

      {/* Main question workspace */}
      {isPaused ? (
        <div className="py-20 text-center space-y-4">
          <ShieldAlert className="w-16 h-16 text-amber-500 mx-auto animate-pulse" />
          <h3 className="text-xl font-bold uppercase tracking-wider text-amber-400 font-mono">Telemetry Suspended</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
            All timers, mouse track matrices, and Bayesian neural estimation parameters are paused. Resume to continue the Gq evaluation.
          </p>
          <button
            onClick={handlePauseToggle}
            className="px-6 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-mono font-bold uppercase rounded text-xs transition"
          >
            RESUME SESSION
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10">
          
          {/* Left panel: Narrative, context, dynamic visual layout */}
          <div className="lg:col-span-7 space-y-5">
            
            {/* Story theme and narration card */}
            <div className="bg-slate-900/60 border border-slate-850 p-5 rounded-xl space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-mono font-bold text-violet-400 uppercase tracking-widest flex items-center gap-1.5">
                  THEME: {currentQuestion.storyTheme}
                </span>
                <span className="text-[10px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  ID: {currentQuestion.id}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed italic">
                "{currentQuestion.narrative}"
              </p>
            </div>

            {/* Interactive Question Core */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 relative">
              <div className="absolute top-3 right-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[9px] font-mono px-2 py-0.5 rounded">
                CALIBRATED DIFFICULTY: {currentQuestion.calculatedDifficulty} (L{currentQuestion.difficultyLevel})
              </div>

              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">COGNITIVE TASK OVERVIEW</span>
              
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-2">
                <span>Backend question payload</span>
                <span className={`px-2 py-0.5 rounded border ${apiStatus === 'ready' ? 'border-emerald-500/30 text-emerald-400' : apiStatus === 'loading' ? 'border-cyan-500/30 text-cyan-400' : 'border-rose-500/30 text-rose-400'}`}>
                  {apiStatus}
                </span>
              </div>
              <div className="text-sm font-semibold text-slate-200 bg-slate-950 border border-slate-850 p-4 rounded-lg leading-relaxed whitespace-pre-wrap font-sans">
                {currentQuestion.questionText}
              </div>

              {/* Dynamic visualizers if PatternBot (sequence layout) or VisionBot */}
              {currentQuestion.module === 'PatternBot' && currentQuestion.data.sequence && (
                <div className="flex justify-center gap-3 py-4">
                  {currentQuestion.data.sequence.map((s: number, idx: number) => (
                    <div key={idx} className="w-12 h-12 bg-slate-950 border border-cyan-500/20 text-cyan-400 font-bold font-mono text-sm flex items-center justify-center rounded-lg shadow">
                      {s}
                    </div>
                  ))}
                  <div className="w-12 h-12 bg-cyan-500/10 border-2 border-cyan-500 border-dashed text-cyan-300 font-bold font-mono text-sm flex items-center justify-center rounded-lg animate-pulse">
                    ?
                  </div>
                </div>
              )}

              {/* CompareBot progress visualizer if percentage comparison */}
              {currentQuestion.module === 'CompareBot' && currentQuestion.data.pct1 && (
                <div className="space-y-3 py-2 bg-slate-950 p-3 rounded-lg border border-slate-850">
                  <div>
                    <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                      <span>Vector A: {currentQuestion.data.pct1}% of {currentQuestion.data.amt1}</span>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded overflow-hidden">
                      <div className="bg-cyan-500 h-full animate-pulse" style={{ width: `${currentQuestion.data.pct1}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                      <span>Vector B: {currentQuestion.data.pct2}% of {currentQuestion.data.amt2}</span>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded overflow-hidden">
                      <div className="bg-violet-500 h-full animate-pulse" style={{ width: `${currentQuestion.data.pct2}%` }}></div>
                    </div>
                  </div>
                </div>
              )}

              {/* VisionBot chart simulator */}
              {currentQuestion.module === 'VisionBot' && currentQuestion.data.chartType === 'bar' && (
                <div className="bg-slate-950 border border-slate-850 p-3 rounded-lg flex items-end justify-center h-28 gap-4 pt-6">
                  {currentQuestion.data.values.map((v: number, i: number) => (
                    <div key={i} className="flex flex-col items-center flex-1">
                      <div className="text-[10px] font-mono text-slate-500 mb-1">{v}</div>
                      <div className="w-full bg-cyan-500/20 border border-cyan-500/40 rounded-t" style={{ height: `${v}%` }}></div>
                      <div className="text-[9px] font-mono text-slate-600 truncate max-w-full mt-1.5">{currentQuestion.data.labels[i]}</div>
                    </div>
                  ))}
                </div>
              )}

              {currentQuestion.module === 'VisionBot' && currentQuestion.data.chartType === 'line' && (
                <div className="bg-slate-950 border border-slate-850 p-3 rounded-lg flex items-center justify-center h-28">
                  <svg viewBox="0 0 100 30" className="w-full h-full text-cyan-400">
                    <polyline
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="1.5"
                      points={currentQuestion.data.points.map((p: number, i: number) => `${i * 18 + 10},${30 - (p / 90) * 30}`).join(' ')}
                    />
                    {currentQuestion.data.points.map((p: number, i: number) => (
                      <circle
                        key={i}
                        cx={i * 18 + 10}
                        cy={30 - (p / 90) * 30}
                        r="1.5"
                        fill="#f43f5e"
                      />
                    ))}
                  </svg>
                </div>
              )}

              {/* SolverBot Visual Router Simulator */}
              {currentQuestion.module === 'SolverBot' && (
                <div className="bg-slate-950 border border-slate-850 p-4 rounded-lg flex flex-col items-center justify-center gap-3">
                  <div className="flex justify-between w-full text-[10px] font-mono text-slate-500">
                    <span>SECTOR_A_GRID</span>
                    <span>TARGET: {currentQuestion.data?.capacityTarget?.beta || 40}MW</span>
                  </div>
                  <div className="grid grid-cols-4 gap-1 w-full max-w-[200px]">
                    {Array.from({ length: 16 }).map((_, i) => (
                      <div 
                        key={i} 
                        className={`w-10 h-10 border rounded flex items-center justify-center text-[8px] font-bold ${
                          i === 0 ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300' : 
                          i === 15 ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300' :
                          (i === 5 || i === 10) ? 'bg-rose-500/10 border-rose-500/30 text-rose-500/50' :
                          'bg-slate-900 border-slate-800 text-slate-600'
                        }`}
                      >
                        {i === 0 ? 'START' : i === 15 ? 'NODE' : (i === 5 || i === 10) ? 'BLOCK' : '01'}
                      </div>
                    ))}
                  </div>
                  <div className="text-[10px] font-mono text-cyan-400/60 text-center uppercase tracking-widest mt-2 animate-pulse">
                    Awaiting routing path injection...
                  </div>
                </div>
              )}
            </div>

            {/* Hint reveal block */}
            <div className="space-y-2">
              <button
                onClick={handleToggleHint}
                className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
              >
                <HelpCircle className="w-4 h-4" />
                {showHint ? 'Dismiss Hint Clue' : 'Request Cognitive Hint assistance (-Score multiplier)'}
              </button>

              {showHint && (
                <div className="bg-amber-500/10 border border-amber-500/20 text-amber-300 p-4 rounded-xl text-xs font-mono flex items-start gap-2.5">
                  <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="leading-relaxed">{currentQuestion.hint}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right panel: Option selection, submits */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Multiple Choice Options */}
            <div className="bg-slate-900 border border-slate-850 rounded-xl p-5 space-y-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block border-b border-slate-800 pb-2">
                STABILIZATION TARGET OPTIONS
              </span>

              <div className="space-y-3">
                {currentQuestion.options.map((option, idx) => {
                  const isSelected = selectedAnswer === option;
                  const isSubmitted = submittedAnswer === option;
                  const isCorrect = option === currentQuestion.correctAnswer;
                  
                  let borderClass = 'border-slate-800/80 hover:border-slate-700 hover:bg-slate-850';
                  let textClass = 'text-slate-300';
                  let iconBg = 'bg-slate-950 border-slate-800';

                  if (isSelected) {
                    borderClass = 'border-cyan-500 bg-cyan-500/5';
                    textClass = 'text-cyan-300 font-semibold';
                    iconBg = 'bg-cyan-500/10 border-cyan-500';
                  }

                  if (submittedAnswer) {
                    if (isSubmitted) {
                      if (isCorrect) {
                        borderClass = 'border-emerald-500 bg-emerald-500/10';
                        textClass = 'text-emerald-300 font-bold';
                        iconBg = 'bg-emerald-500 text-slate-950 border-emerald-400';
                      } else {
                        borderClass = 'border-rose-500 bg-rose-500/10';
                        textClass = 'text-rose-400 font-medium';
                        iconBg = 'bg-rose-500 text-slate-950 border-rose-400';
                      }
                    } else if (isSelected && isCorrect) {
                      borderClass = 'border-emerald-500 bg-emerald-500/10';
                      textClass = 'text-emerald-300 font-bold';
                    }
                  }

                  return (
                    <button
                      key={idx}
                      disabled={!!submittedAnswer && selectedAnswer === currentQuestion.correctAnswer}
                      onMouseEnter={handleMouseEnterOption}
                      onMouseLeave={handleMouseLeaveOption}
                      onClick={() => handleOptionChange(option)}
                      className={`w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between gap-3 text-xs md:text-sm ${borderClass}`}
                    >
                      <span className={textClass}>{option}</span>
                      <div className={`w-5 h-5 rounded-full border flex items-center justify-center font-bold text-[10px] font-mono ${iconBg}`}>
                        {submittedAnswer && isSubmitted ? (isCorrect ? '✓' : '✕') : (isSelected ? '●' : '')}
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Confidence self-rating (Deliverable 3 Confidence quality criteria) */}
              {!submittedAnswer && (
                <div className="space-y-2 border-t border-slate-800 pt-3">
                  <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 uppercase">
                    <span>Self-Rated Confidence Index</span>
                    <span className="text-cyan-400 font-bold">{userConfidence}/5 star</span>
                  </div>
                  <div className="flex justify-between gap-1.5">
                    {[1, 2, 3, 4, 5].map((stars) => (
                      <button
                        key={stars}
                        onClick={() => {
                          setUserConfidence(stars);
                          logLocalEvent('CONFIDENCE_RATED', 'INFO', `User checked confidence metric to ${stars}/5`);
                        }}
                        className={`flex-1 py-1.5 rounded border transition-colors ${
                          userConfidence >= stars
                            ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-400'
                            : 'bg-slate-950 border-slate-850 text-slate-600 hover:text-slate-400'
                        }`}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Error notifications */}
            {submittedAnswer && submittedAnswer !== currentQuestion.correctAnswer && (
              <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 p-4 rounded-xl text-xs font-mono flex items-start gap-2.5">
                <ShieldAlert className="w-4.5 h-4.5 text-rose-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold uppercase tracking-wider text-rose-400 mb-1">STABILIZATION VECTOR MISALIGNED</p>
                  <p className="leading-relaxed">
                    That calibration index failed to satisfy the numerical balance constraint. (Attempt {attempts}/3).
                  </p>
                </div>
              </div>
            )}

            {/* Correct verification notification */}
            {submittedAnswer && submittedAnswer === currentQuestion.correctAnswer && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 p-4 rounded-xl text-xs font-mono flex items-start gap-2.5">
                <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400 flex-shrink-0 mt-0.5 animate-bounce" />
                <div>
                  <p className="font-bold uppercase tracking-wider text-emerald-400 mb-1">STABILIZATION VERIFIED</p>
                  <p className="leading-relaxed">
                    Adaptive routing calculations updated in real time. Advancing to the next cognitive sequence vector...
                  </p>
                </div>
              </div>
            )}

            {/* Action Button */}
            {!submittedAnswer || submittedAnswer !== currentQuestion.correctAnswer ? (
              <button
                onClick={handleSubmit}
                disabled={!selectedAnswer}
                className="w-full py-4 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 disabled:from-slate-900 disabled:to-slate-900 border disabled:border-slate-850 border-cyan-400 disabled:text-slate-600 text-slate-950 font-mono font-bold uppercase rounded-xl shadow-lg hover:shadow-cyan-500/15 transition-all flex items-center justify-center gap-2"
              >
                <Cpu className="w-4.5 h-4.5" />
                <span>Verify Allocation Block</span>
              </button>
            ) : (
              <div className="py-2.5 text-center font-mono text-[11px] text-slate-500 animate-pulse uppercase">
                Synchronizing adaptive routing parameters...
              </div>
            )}

            {/* Difficulty calibration inspector */}
            <details className="bg-slate-900/40 border border-slate-850 rounded-lg p-3 text-xs font-mono cursor-pointer">
              <summary className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
                Inspect Cognitive Calibration Parameters
              </summary>
              <div className="mt-3 space-y-1.5 text-slate-400">
                <div className="flex justify-between">
                  <span>Rule Complexity (RC) (25%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.rc}</span>
                </div>
                <div className="flex justify-between">
                  <span>Cognitive Steps (CS) (20%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.cs}</span>
                </div>
                <div className="flex justify-between">
                  <span>Representation (RP) (15%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.rp}</span>
                </div>
                <div className="flex justify-between">
                  <span>Working Memory (WM) (10%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.wm}</span>
                </div>
                <div className="flex justify-between">
                  <span>Decision Complexity (DC) (10%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.dc}</span>
                </div>
                <div className="flex justify-between">
                  <span>Visual Processing (VP) (5%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.vp}</span>
                </div>
                <div className="flex justify-between">
                  <span>Constraint Load (CL) (10%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.cl}</span>
                </div>
                <div className="flex justify-between">
                  <span>Expected Duration (T) (5%):</span>
                  <span className="text-cyan-400 font-bold">{currentQuestion.calibration.t}</span>
                </div>
                <div className="border-t border-slate-800 pt-1.5 flex justify-between font-bold text-[11px] text-slate-200">
                  <span>Difficulty Score Formula:</span>
                  <span className="text-violet-400">{currentQuestion.calculatedDifficulty}</span>
                </div>
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  );
};
