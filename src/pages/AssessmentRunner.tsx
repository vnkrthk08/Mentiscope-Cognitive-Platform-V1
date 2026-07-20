import React, { useState, useEffect, useRef } from "react";
import { User, AssessmentSession, AnswerPayload, Question, ModuleConfig } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { QUESTIONS_DATA } from "../config/questionsData";
import { AssessmentService } from "../services/assessment/AssessmentService";
import { motion, AnimatePresence } from "motion/react";
import { 
  Brain, 
  Hourglass, 
  HelpCircle, 
  ArrowRight, 
  Sparkles, 
  Timer, 
  Play, 
  CheckCircle, 
  ArrowUpRight 
} from "lucide-react";

interface AssessmentRunnerProps {
  user: User;
  onNavigate: (page: string) => void;
  soundEnabled: boolean;
}

export default function AssessmentRunner({ user, onNavigate, soundEnabled }: AssessmentRunnerProps) {
  // Session State
  const [session, setSession] = useState<AssessmentSession | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Active Assessment Status
  const [activeModule, setActiveModule] = useState<ModuleConfig | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  
  // Selection States
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [selectedAnswerIndex, setSelectedAnswerIndex] = useState<number>(-1);
  const [hintOpen, setHintOpen] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);
  const [feedback, setFeedback] = useState<{ isCorrect: boolean; text: string } | null>(null);

  // Active Memory Span State
  const [showSequence, setShowSequence] = useState(false);
  const [sequenceIndex, setSequenceIndex] = useState(-1);
  const [userSequenceInput, setUserSequenceInput] = useState("");

  // Spatial Grid State
  const [showGridTarget, setShowGridTarget] = useState(false);
  const [gridSelectedCells, setGridSelectedCells] = useState<number[]>([]);

  // Processing Speed State
  const [processingSpeedSelectedIndices, setProcessingSpeedSelectedIndices] = useState<number[]>([]);
  const [rowTimer, setRowTimer] = useState<number>(8.0);
  const rowTimerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Time & Tracking
  const [timeLeft, setTimeLeft] = useState<number>(180); // 3 minutes per module
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Transition Splashes
  const [transitioningModule, setTransitioningModule] = useState<ModuleConfig | null>(null);
  const [transitionCountdown, setTransitionCountdown] = useState(5);

  // 1. Initialise / Load Session
  useEffect(() => {
    const activeSess = AssessmentService.getOrCreateSession(user.id);
    setSession(activeSess);
    loadModuleIndex(activeSess.currentModuleIndex, activeSess);
  }, [user.id]);

  // 2. Timer management
  useEffect(() => {
    if (activeModule && !transitioningModule && timeLeft > 0) {
      timerIntervalRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timerIntervalRef.current!);
            handleModuleTimeout();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [activeModule, transitioningModule, timeLeft]);

  // 2.1 Row-level timer for Stage 3 of Processing Speed module
  useEffect(() => {
    const stage = (currentQuestion as any)?.stage;
    if (activeModule?.id === "processing-speed" && stage === 3 && !transitioningModule && !isAnswering) {
      setRowTimer(8.0);
      if (rowTimerIntervalRef.current) clearInterval(rowTimerIntervalRef.current);
      
      rowTimerIntervalRef.current = setInterval(() => {
        setRowTimer((prev) => {
          if (prev <= 0.1) {
            if (rowTimerIntervalRef.current) clearInterval(rowTimerIntervalRef.current);
            rowTimerIntervalRef.current = null;
            handleRowTimeout();
            return 0.0;
          }
          return parseFloat((prev - 0.1).toFixed(1));
        });
      }, 100);
    } else {
      if (rowTimerIntervalRef.current) {
        clearInterval(rowTimerIntervalRef.current);
        rowTimerIntervalRef.current = null;
      }
    }
    return () => {
      if (rowTimerIntervalRef.current) {
        clearInterval(rowTimerIntervalRef.current);
        rowTimerIntervalRef.current = null;
      }
    };
  }, [currentQuestion, activeModule, transitioningModule, isAnswering]);

  // 3. Load active module
  const loadModuleIndex = async (index: number, currentSess: AssessmentSession) => {
    if (index >= MODULE_CONFIGS.length) {
      // Completed all modules! Generate final scores & navigate
      completeAssessmentSession(currentSess);
      return;
    }

    setLoading(true);
    const mod = MODULE_CONFIGS[index];
    setActiveModule(mod);
    setTimeLeft(mod.id === "processing-speed" || mod.id === "attention" ? 120 : 180); // shorter timers for speed tests
    
    // Call /start API
    const startResponse = await AssessmentService.startModule(mod.id, currentSess.sessionId, currentSess.studentId);
    
    const modQuestions = startResponse.question ? [startResponse.question] : (QUESTIONS_DATA[mod.id] || []);
    setQuestions(modQuestions);
    setTotalQuestions(startResponse.totalQuestions || modQuestions.length);
    
    // Resume at question index or reset
    let qIndex = currentSess.currentQuestionIndex;
    if (startResponse.question && qIndex > 0) {
      // Dynamic modules do not support mid-way resuming via /start; reset to 0
      qIndex = 0;
      currentSess.currentQuestionIndex = 0;
      setSession({ ...currentSess });
      AssessmentService.saveSession(currentSess);
    }

    if (qIndex < modQuestions.length) {
      loadQuestion(modQuestions[qIndex]);
    } else {
      // Completed this module somehow, load next
      transitionToNextModule(index + 1, currentSess);
    }
    setLoading(false);
  };

  // 4. Load a question
  const loadQuestion = (q: Question) => {
    setCurrentQuestion(q);
    setSelectedAnswer("");
    setSelectedAnswerIndex(-1);
    setHintOpen(false);
    setFeedback(null);
    setQuestionStartTime(Date.now());

    // Reset task structures
    setUserSequenceInput("");
    setGridSelectedCells([]);
    setProcessingSpeedSelectedIndices([]);

    // Custom Working Memory Flashing Routine
    if (q.type === "memory-span" && q.sequence) {
      setShowSequence(true);
      setSequenceIndex(0);
    } else {
      setShowSequence(false);
    }

    // Custom Spatial Grid Flashing Routine
    if (q.type === "grid-pattern" && q.activeGridCells) {
      setShowGridTarget(true);
      setTimeout(() => setShowGridTarget(false), 2200); // flash for 2.2 seconds
    } else {
      setShowGridTarget(false);
    }
  };

  // 5. Working Memory Digit/Letter Flashing Loop
  useEffect(() => {
    if (showSequence && currentQuestion && currentQuestion.sequence && sequenceIndex >= 0) {
      if (sequenceIndex < currentQuestion.sequence.length) {
        const timer = setTimeout(() => {
          setSequenceIndex(prev => prev + 1);
        }, 1100); // flash every 1.1s
        return () => clearTimeout(timer);
      } else {
        // finished showing sequence
        setShowSequence(false);
      }
    }
  }, [showSequence, sequenceIndex, currentQuestion]);

  // 6. Timeout Handler
  const handleModuleTimeout = () => {
    if (!session || !activeModule) return;
    console.warn(`Time ran out for module ${activeModule.name}`);
    // Auto-complete module with what we have
    const updatedSess = { ...session };
    if (!updatedSess.answers[activeModule.id]) {
      updatedSess.answers[activeModule.id] = [];
    }
    // Calculate final module score & transit
    finishActiveModule(updatedSess);
  };

  // 7. Click Cell in Grid-Pattern memory game
  const handleGridCellClick = (index: number) => {
    if (showGridTarget) return; // cannot select while flashing
    setGridSelectedCells(prev => {
      if (prev.includes(index)) {
        return prev.filter(cell => cell !== index);
      } else {
        return [...prev, index];
      }
    });
  };

  // 8. Core Answer Submission Utility
  const submitAnswer = async (answerString: string, overrideDurationMs?: number) => {
    if (!session || !currentQuestion || !activeModule || isAnswering) return;

    setIsAnswering(true);

    // Clear any active row timers
    if (rowTimerIntervalRef.current) {
      clearInterval(rowTimerIntervalRef.current);
      rowTimerIntervalRef.current = null;
    }

    const durationMs = overrideDurationMs !== undefined ? overrideDurationMs : (Date.now() - questionStartTime);

    const payload: AnswerPayload = {
      questionId: currentQuestion.id,
      answer: answerString,
      durationMs
    };

    // Call /answer API
    const response = await AssessmentService.submitAnswer(activeModule.id, session.sessionId, payload);

    // Save response in session state
    const updatedAnswers = { ...session.answers };
    if (!updatedAnswers[activeModule.id]) {
      updatedAnswers[activeModule.id] = [];
    }
    updatedAnswers[activeModule.id].push(payload);

    const nextQIndex = session.currentQuestionIndex + 1;
    const isModuleComplete = nextQIndex >= totalQuestions;

    const updatedSess: AssessmentSession = {
      ...session,
      answers: updatedAnswers,
      currentQuestionIndex: isModuleComplete ? 0 : nextQIndex
    };

    setSession(updatedSess);
    AssessmentService.saveSession(updatedSess);

    // Show instant visual response feedback shortly (helps the SaaS premium feel)
    setFeedback({
      isCorrect: response.isCorrect,
      text: response.feedback || ""
    });

    if (soundEnabled) {
      playFeedbackTone(response.isCorrect ? "correct" : "wrong");
    }

    setTimeout(() => {
      setIsAnswering(false);
      setFeedback(null);
      
      if (isModuleComplete) {
        finishActiveModule(updatedSess);
      } else {
        if (response.nextQuestion) {
          setQuestions((existing) => [...existing, response.nextQuestion!]);
          loadQuestion(response.nextQuestion);
        } else {
          loadQuestion(questions[nextQIndex]);
        }
      }
    }, 1200);
  };

  // 8.1 Submit Question Response (standard modules)
  const handleSubmit = async () => {
    if (!session || !currentQuestion || !activeModule || isAnswering) return;

    let answerString = selectedAnswer;

    // Handle memory span typed input
    if (currentQuestion.type === "memory-span") {
      answerString = userSequenceInput.trim();
    }

    // Handle spatial grid selected coordinates
    if (currentQuestion.type === "grid-pattern") {
      answerString = [...gridSelectedCells].sort((a,b) => a-b).join(",");
    }

    if (!answerString && currentQuestion.type !== "grid-pattern") {
      alert("Please provide an answer to proceed.");
      return;
    }

    await submitAnswer(answerString);
  };

  // 8.2 Click Processing Speed identical pair cards
  const handleProcessingSpeedCardClick = (idx: number) => {
    if (isAnswering) return;

    // Quick audio click feedback
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(320, ctx.currentTime);
      gain.gain.setValueAtTime(0.03, ctx.currentTime);
      osc.start();
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.stop(ctx.currentTime + 0.05);
    } catch {}

    const prev = processingSpeedSelectedIndices;
    let next: number[];
    if (prev.includes(idx)) {
      next = prev.filter((i) => i !== idx);
    } else {
      next = [...prev, idx];
    }

    setProcessingSpeedSelectedIndices(next);

    // Auto submit once 2 items are selected (pure side-effect executed once outside state callback)
    if (next.length === 2) {
      setTimeout(() => {
        triggerProcessingSpeedSubmit(next);
      }, 100);
    }
  };

  // 8.3 Auto-submit Processing Speed card matching selection
  const triggerProcessingSpeedSubmit = async (indices: number[]) => {
    if (!currentQuestion) return;
    const idx1 = indices[0];
    const idx2 = indices[1];
    const val1 = currentQuestion.options?.[idx1] ?? "";
    const val2 = currentQuestion.options?.[idx2] ?? "";
    
    // If they match, send val1. If they don't match, send mismatch.
    const answerString = (val1 === val2) ? val1 : `${val1}_mismatch_${val2}`;
    await submitAnswer(answerString);
  };

  // 8.4 Enforce Row Timeout (Module 7, Stage 3)
  const handleRowTimeout = async () => {
    if (!session || !currentQuestion || !activeModule || isAnswering) return;

    if (rowTimerIntervalRef.current) {
      clearInterval(rowTimerIntervalRef.current);
      rowTimerIntervalRef.current = null;
    }

    // Set feedback warning for omission error
    setFeedback({
      isCorrect: false,
      text: "Time ran out for this row! (Omission Error)"
    });

    if (soundEnabled) {
      playFeedbackTone("wrong");
    }

    await submitAnswer("TIMEOUT", 8000);
  };

  // 9. Finish Active Module
  const finishActiveModule = async (currentSess: AssessmentSession) => {
    if (!activeModule) return;
    
    setLoading(true);
    const moduleAnswers = currentSess.answers[activeModule.id] || [];
    
    // Call /finish API
    const res = await AssessmentService.finishModule(activeModule.id, currentSess.sessionId, moduleAnswers);
    
    const updatedSess = {
      ...currentSess,
      moduleScores: {
        ...currentSess.moduleScores,
        [activeModule.id]: res.scorePercentage
      },
      currentModuleIndex: currentSess.currentModuleIndex + 1,
      currentQuestionIndex: 0
    };

    setSession(updatedSess);
    AssessmentService.saveSession(updatedSess);

    // Trigger transition countdown splash
    transitionToNextModule(updatedSess.currentModuleIndex, updatedSess);
  };

  // 10. Transition module splash screen
  const transitionToNextModule = (nextIndex: number, currentSess: AssessmentSession) => {
    if (nextIndex >= MODULE_CONFIGS.length) {
      completeAssessmentSession(currentSess);
      return;
    }

    const nextMod = MODULE_CONFIGS[nextIndex];
    setTransitioningModule(nextMod);
    setTransitionCountdown(4);

    const interval = setInterval(() => {
      setTransitionCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setTransitioningModule(null);
          loadModuleIndex(nextIndex, currentSess);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // 11. Final completion routine
  const completeAssessmentSession = (currentSess: AssessmentSession) => {
    const finalSess: AssessmentSession = {
      ...currentSess,
      status: "completed",
      endTime: new Date().toISOString()
    };
    setSession(finalSess);
    AssessmentService.saveSession(finalSess);
    onNavigate("report");
  };

  // Formatted Timer Label helper
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  if (loading && !transitioningModule) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
        <p className="text-xs font-semibold text-slate-500 animate-pulse">
          Retrieving capsule parameters from API Gateway...
        </p>
      </div>
    );
  }

  // A. Transition Splash Interface
  if (transitioningModule) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 flex flex-col items-center justify-center text-center space-y-8 min-h-[70vh]">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-emerald-50 text-emerald-600 border border-emerald-100 shadow-md">
          <CheckCircle className="h-8 w-8" />
        </div>

        <div className="space-y-3">
          <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
            Module Complete
          </span>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight sm:text-3xl">
            Success! Preparing Next Assessment
          </h2>
          <p className="text-sm text-slate-500 max-w-sm">
            Your scores have been transmitted securely to the psychometric databases. Take a short breath before the next capsule starts.
          </p>
        </div>

        {/* Transition Preview Card */}
        <div className="w-full rounded-2xl border border-slate-200 bg-white p-5 text-left space-y-3 shadow-sm">
          <p className="text-[10px] font-mono font-bold text-blue-600 uppercase">Up Next</p>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-50 text-blue-600">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800">{transitioningModule.name}</p>
              <p className="text-xs text-slate-400">{transitioningModule.description}</p>
            </div>
          </div>
        </div>

        <div className="space-y-1">
          <p className="text-xs text-slate-400 font-medium">Automatic gateway redirection in</p>
          <p className="text-4xl font-black text-blue-600 animate-bounce">{transitionCountdown}</p>
        </div>
      </div>
    );
  }

  if (!activeModule || !currentQuestion || !session) return null;

  const currentQIndex = session.currentQuestionIndex;
  const totalQs = totalQuestions;
  const questionPercent = Math.round(((currentQIndex) / totalQs) * 100);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      
      {/* Top Banner Status Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-2xl border border-slate-200 bg-white p-4 sm:px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-700 font-semibold border border-blue-100">
            {session.currentModuleIndex + 1}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 leading-tight">
              {activeModule.name}
            </h3>
            <p className="text-[11px] text-slate-500 line-clamp-1">
              {activeModule.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold text-slate-600 shrink-0">
          {/* Row Timer for Stage 3 of Processing Speed */}
          {activeModule.id === "processing-speed" && (currentQuestion as any).stage === 3 && (
            <div className="flex items-center gap-1.5 bg-amber-50 border border-amber-200 px-2.5 py-1.5 rounded-lg text-amber-700 font-mono">
              <span className="text-[9px] font-bold uppercase tracking-wider">Row Limit:</span>
              <span className="font-bold">{rowTimer.toFixed(1)}s</span>
            </div>
          )}

          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200/60 px-2.5 py-1.5 rounded-lg text-slate-500 font-mono">
            <Timer className="h-3.5 w-3.5" />
            <span>{formatTime(timeLeft)}</span>
          </div>

          <div className="text-slate-400">
            Question <span className="text-slate-800 font-bold">{currentQIndex + 1}</span> of <span className="text-slate-800 font-bold">{totalQs}</span>
          </div>

          {session.currentModuleIndex < 6 && (
            <button
              onClick={() => {
                const updatedSess = {
                  ...session,
                  currentModuleIndex: 6,
                  currentQuestionIndex: 0
                };
                setSession(updatedSess);
                AssessmentService.saveSession(updatedSess);
                loadModuleIndex(6, updatedSess);
              }}
              className="text-[10px] font-bold text-amber-600 bg-amber-50 hover:bg-amber-100 px-2.5 py-1.5 rounded-lg border border-amber-200 transition-all active:scale-95 cursor-pointer"
            >
              Skip to Module 7
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar of active Module */}
      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200/30">
        <div 
          className="h-full bg-blue-600 transition-all duration-300" 
          style={{ width: `${questionPercent}%` }} 
        />
      </div>

      {/* Center Assessment Question Card */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-10 shadow-sm relative overflow-hidden">
        
        {/* Loading overlay during submitting feedback */}
        <AnimatePresence>
          {isAnswering && feedback && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-white/90 backdrop-blur-sm z-20 flex flex-col items-center justify-center text-center p-6"
            >
              <div className={`flex h-12 w-12 items-center justify-center rounded-2xl mb-4 border ${
                feedback.isCorrect 
                  ? "bg-emerald-50 text-emerald-600 border-emerald-100" 
                  : "bg-amber-50 text-amber-600 border-amber-100"
              }`}>
                <Sparkles className="h-6 w-6 animate-pulse" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-1">
                {feedback.isCorrect ? "Answer Logged Successfully" : "Processing Response..."}
              </h4>
              <p className="text-xs text-slate-400 max-w-xs">{feedback.text}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Question Content */}
        <div className="space-y-6">
          
          {/* Story Prompt Box */}
          {currentQuestion.story && (
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-4 text-xs text-slate-600 leading-relaxed font-sans">
              <span className="font-bold text-blue-600 uppercase tracking-wide text-[10px] block mb-1">
                Task Guide
              </span>
              {currentQuestion.story}
            </div>
          )}

          {/* Primary Question Statement */}
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight sm:text-xl md:text-2xl leading-snug">
            {currentQuestion.text}
          </h2>

          {/* DYNAMIC COGNITIVE INTERFACES */}
          <div className="pt-4 border-t border-slate-100">
            
            {/* 1. STROOP TASK VIEW */}
            {currentQuestion.type === "stroop" && currentQuestion.textColor && (
              <div className="flex flex-col items-center justify-center py-8 space-y-3">
                <span className="text-[10px] font-mono tracking-widest text-slate-400 font-bold uppercase">
                  Resolve Conflict Color
                </span>
                <span 
                  className="text-5xl font-black tracking-widest uppercase transition-all duration-300"
                  style={{ 
                    color: currentQuestion.targetColor === "GREEN" ? "#14B8A6" : 
                           currentQuestion.targetColor === "RED" ? "#EF4444" : 
                           currentQuestion.targetColor === "BLUE" ? "#3B82F6" : 
                           currentQuestion.targetColor === "YELLOW" ? "#EAB308" : "#0F172A"
                  }}
                >
                  {currentQuestion.textColor}
                </span>
              </div>
            )}

            {/* 2. WORKING MEMORY AUDITORY/DIGIT SEQUENCE VIEW */}
            {currentQuestion.type === "memory-span" && currentQuestion.sequence && (
              <div className="flex flex-col items-center justify-center py-6">
                {showSequence ? (
                  <div className="text-center space-y-4">
                    <p className="text-xs font-mono font-bold text-blue-600 tracking-wider uppercase animate-pulse">
                      Focus - Recall Sequence Flashing
                    </p>
                    <div className="h-20 w-20 flex items-center justify-center rounded-2xl bg-blue-50 text-3xl font-black text-blue-700 border border-blue-200">
                      {currentQuestion.sequence[sequenceIndex]}
                    </div>
                  </div>
                ) : (
                  <div className="w-full max-w-sm space-y-3 text-center">
                    <p className="text-xs font-semibold text-slate-500">
                      Now type the sequence as requested:
                    </p>
                    <input
                      type="text"
                      required
                      value={userSequenceInput}
                      onChange={(e) => setUserSequenceInput(e.target.value.toUpperCase())}
                      placeholder="Type sequence without spaces (e.g. 48291)"
                      className="w-full rounded-xl border-2 border-slate-200 bg-white px-4 py-3 text-center text-lg font-mono font-bold tracking-widest text-slate-900 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                )}
              </div>
            )}

            {/* 3. VISUAL-SPATIAL GRID RECALL VIEW */}
            {currentQuestion.type === "grid-pattern" && currentQuestion.activeGridCells && (
              <div className="flex flex-col items-center justify-center py-4 space-y-4">
                <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest">
                  {showGridTarget ? "Memorise Shaded Blocks" : "Select Highlighted Blocks"}
                </span>

                <div className="grid grid-cols-4 gap-3 w-64 h-64">
                  {Array.from({ length: 16 }).map((_, idx) => {
                    const isTarget = currentQuestion.activeGridCells?.includes(idx);
                    const isSelected = gridSelectedCells.includes(idx);

                    let bgClass = "bg-slate-50 hover:bg-slate-100 border-slate-200";
                    if (showGridTarget && isTarget) {
                      bgClass = "bg-blue-600 border-blue-700 text-white animate-pulseScale";
                    } else if (!showGridTarget && isSelected) {
                      bgClass = "bg-emerald-500 border-emerald-600 text-white";
                    }

                    return (
                      <button
                        key={idx}
                        onClick={() => handleGridCellClick(idx)}
                        disabled={showGridTarget}
                        className={`aspect-square rounded-xl border-2 font-mono text-xs font-bold transition-all focus:outline-none active:scale-95 ${bgClass}`}
                      >
                        {isSelected && !showGridTarget ? "✓" : ""}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 4. COGNITIVE PROCESSING SPEED IDENTICAL PAIR GRID */}
            {activeModule.id === "processing-speed" && currentQuestion.options && (
              <div className="flex flex-col items-center justify-center py-6 space-y-4">
                <span className="text-[10px] font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                  Select the two identical matching cards below:
                </span>

                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 w-full max-w-lg">
                  {currentQuestion.options.map((item, idx) => {
                    const isSelected = processingSpeedSelectedIndices.includes(idx);
                    
                    // Determine correctness feedback colors
                    let btnColorClass = "bg-slate-50 border-slate-200 hover:bg-slate-100/70 text-slate-700 dark:bg-slate-900/60 dark:border-slate-850 dark:hover:bg-slate-850 dark:text-slate-200";
                    
                    if (feedback) {
                      const correctIndices = currentQuestion.options 
                        ? currentQuestion.options.reduce((acc: number[], optItem: string, i: number) => {
                            if (optItem === (currentQuestion.correct_answer || (currentQuestion as any).correctAnswer)) {
                              acc.push(i);
                            }
                            return acc;
                          }, [])
                        : [];
                      
                      const isCorrectChoice = feedback.isCorrect;
                      
                      if (isSelected) {
                        if (isCorrectChoice) {
                          // Green/Emerald for correct choice
                          btnColorClass = "bg-emerald-50 border-emerald-500 text-emerald-700 dark:bg-emerald-950/30 dark:border-emerald-500 dark:text-emerald-300 ring-2 ring-emerald-500/20";
                        } else {
                          // Red/Rose for wrong choice
                          btnColorClass = "bg-rose-50 border-rose-500 text-rose-700 dark:bg-rose-950/30 dark:border-rose-500 dark:text-rose-300 ring-2 ring-rose-500/20";
                        }
                      } else if (correctIndices.includes(idx)) {
                        // Reveal correct duplicate pair in emerald if user got it wrong
                        btnColorClass = "bg-emerald-50/50 border-emerald-400 text-emerald-600 dark:bg-emerald-950/20 dark:border-emerald-600 dark:text-emerald-400 border-dashed animate-pulseScale";
                      }
                    } else if (isSelected) {
                      btnColorClass = "bg-blue-50/70 border-blue-500 text-blue-700 dark:bg-blue-950/40 dark:border-blue-400 dark:text-blue-300 shadow-md shadow-blue-500/10";
                    }

                    return (
                      <button
                        key={idx}
                        onClick={() => handleProcessingSpeedCardClick(idx)}
                        disabled={isAnswering}
                        className={`h-24 rounded-2xl border-2 font-mono text-lg font-black transition-all flex items-center justify-center cursor-pointer select-none relative group active:scale-95 ${btnColorClass}`}
                      >
                        <span className="tracking-widest">{item}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* DEFAULT MULTIPLE CHOICE BUTTONS */}
            {(!showSequence && !showGridTarget && currentQuestion.options && activeModule.id !== "processing-speed") && (
              <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 pt-2">
                {currentQuestion.options.map((opt, idx) => (
                  <button
                    key={`${opt}-${idx}`}
                    onClick={() => {
                      setSelectedAnswer(opt);
                      setSelectedAnswerIndex(idx);
                    }}
                    className={`text-left rounded-2xl border px-5 py-4 text-xs font-semibold transition-all focus:outline-none ${
                      selectedAnswerIndex === idx
                        ? "bg-blue-50 border-blue-500 text-blue-900 ring-2 ring-blue-500/20"
                        : "bg-white border-slate-200 hover:bg-slate-50 text-slate-700"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`h-4.5 w-4.5 rounded-full border flex items-center justify-center shrink-0 ${
                        selectedAnswerIndex === idx ? "border-blue-600 bg-blue-600 text-white" : "border-slate-300"
                      }`}>
                        {selectedAnswerIndex === idx && <span className="h-1.5 w-1.5 rounded-full bg-white" />}
                      </div>
                      <span>{opt}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}

          </div>

          {/* Hint Disclosure Section */}
          {currentQuestion.hint && (
            <div className="border-t border-slate-100 pt-4">
              {hintOpen ? (
                <div className="rounded-xl bg-amber-50/60 border border-amber-100 p-3.5 text-xs text-amber-900 space-y-1">
                  <span className="font-bold block">Assistance Tip:</span>
                  <p>{currentQuestion.hint}</p>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setHintOpen(true)}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-600 hover:text-amber-700"
                >
                  <HelpCircle className="h-3.5 w-3.5" />
                  <span>Request Cognitive Hint</span>
                </button>
              )}
            </div>
          )}

        </div>
      </div>

      <div className="flex items-center justify-between">
        <button
          disabled
          className="rounded-xl border border-slate-100 bg-slate-50 px-4.5 py-2.5 text-xs font-bold text-slate-400 cursor-not-allowed"
          title="Sequential evaluation prohibits backtracking to preserve statistical accuracy."
        >
          Previous Disabled
        </button>

        {activeModule.id !== "processing-speed" ? (
          <button
            onClick={handleSubmit}
            disabled={showSequence || showGridTarget || isAnswering}
            className={`flex items-center gap-1.5 rounded-xl bg-blue-600 px-6 py-3 text-xs font-bold text-white transition-all hover:bg-blue-700 shadow-md shadow-blue-500/15 ${
              showSequence || showGridTarget ? "opacity-40 cursor-not-allowed" : ""
            }`}
          >
            <span>Submit Response</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        ) : (
          <div className="text-[10px] font-mono font-bold text-slate-400 dark:text-slate-500 tracking-wider">
            Select 2 identical cards to submit automatically
          </div>
        )}
      </div>

    </div>
  );
}

const playFeedbackTone = (type: "correct" | "wrong") => {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === "correct") {
      // Pleasant double-beep (C5 -> E5)
      osc.type = "sine";
      osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      osc.start();
      
      osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.08); // E5
      gain.gain.setValueAtTime(0.08, ctx.currentTime + 0.08);
      
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      osc.stop(ctx.currentTime + 0.35);
    } else {
      // Low failure buzz (A2)
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(110.00, ctx.currentTime); // A2
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      osc.start();
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.stop(ctx.currentTime + 0.4);
    }
  } catch (e) {
    console.error("Audio playback error:", e);
  }
};
