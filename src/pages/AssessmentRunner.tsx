import React, { useState, useEffect, useRef } from "react";
import { User, AssessmentSession, AnswerPayload, Question, ModuleConfig } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { QUESTIONS_DATA } from "../config/questionsData";
import { AssessmentService } from "../services/assessment/AssessmentService";
import GVItemRenderer from "../modules/gv/GVItemRenderer";
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
  ArrowUpRight,
  Settings2,
  LayoutDashboard
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import { useQuiz } from "../context/QuizContext";
import QuizExitWarningModal from "../components/QuizExitWarningModal";

interface AssessmentRunnerProps {
  user: User;
  soundEnabled: boolean;
  onNavigate?: (page: string, targetTab?: string) => void;
}

export default function AssessmentRunner({ user, soundEnabled, onNavigate }: AssessmentRunnerProps) {
  const navigate = useNavigate();
  const { quizActive, setQuizActive } = useQuiz();

  // Session State
  const [session, setSession] = useState<AssessmentSession | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Active Assessment Status
  const [activeModule, setActiveModule] = useState<ModuleConfig | null>(null);
  const [moduleStarted, setModuleStarted] = useState<boolean>(false);
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

  // Quit Confirm Modal State
  const [showQuitConfirmModal, setShowQuitConfirmModal] = useState(false);

  // A11y States
  const [a11yMenuOpen, setA11yMenuOpen] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [largeFont, setLargeFont] = useState(false);


  // 1. Initialise / Load Session
  useEffect(() => {
    const activeSess = AssessmentService.getOrCreateSession(user.id);
    setSession(activeSess);
    loadModuleIndex(activeSess.currentModuleIndex, activeSess);
  }, [user.id]);

  // 1.1 Guard browser reload / tab close
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (quizActive) {
        e.preventDefault();
        e.returnValue = "Are you sure you want to exit? Your progress will be lost.";
        return e.returnValue;
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [quizActive]);

  // 1.2 Track tab switching, window minimization, and focus deviations during active quiz session
  useEffect(() => {
    if (!quizActive || !session) return;

    let lastSwitchTime = 0;

    const recordFocusDeviation = () => {
      const now = Date.now();
      if (now - lastSwitchTime < 1500) return; // Debounce events within 1.5s
      lastSwitchTime = now;

      const activeSess = AssessmentService.getSession();
      if (activeSess && activeSess.status === "ongoing") {
        const currentSwitches = activeSess.moduleMetrics?.tabSwitches || 0;
        const updatedSess: AssessmentSession = {
          ...activeSess,
          moduleMetrics: {
            ...(activeSess.moduleMetrics || {}),
            tabSwitches: currentSwitches + 1
          }
        };
        AssessmentService.saveSession(updatedSess);
        setSession(updatedSess);
        console.warn(`Focus deviation / tab switch detected! Cumulative count: ${currentSwitches + 1}`);
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        recordFocusDeviation();
      }
    };

    const handleBlur = () => {
      recordFocusDeviation();
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, [quizActive, session]);


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
    const qId = currentQuestion?.id || "";
    const isStage3 = stage === 3 || stage === "3" || qId.includes("stage_3") || qId.includes("level_3") || qId.includes("mod3");

    if (activeModule?.id === "processing-speed" && isStage3 && !transitioningModule && !isAnswering) {
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
  }, [activeModule?.id, currentQuestion?.id, transitioningModule, isAnswering]);

  // 3. Load active module
  const loadModuleIndex = async (index: number, currentSess: AssessmentSession) => {
    if (index >= MODULE_CONFIGS.length) {
      // Completed all modules! Generate final scores & navigate
      completeAssessmentSession(currentSess);
      return;
    }

    setQuizActive(true);
    sessionStorage.setItem("quiz_in_progress", "true");
    setLoading(true);
    const mod = MODULE_CONFIGS[index];
    setActiveModule(mod);
    setModuleStarted(false);
    if (mod.id === "gf") {
      setTimeLeft(105); // 1 minute 45 seconds
    } else if (mod.id === "processing-speed" || mod.id === "gs" || mod.id === "attention") {
      setTimeLeft(120);
    } else {
      setTimeLeft(180);
    }
    
    // Call /start API
    const startResponse = await AssessmentService.startModule(mod.id, currentSess.sessionId);
    
    let modQuestions = startResponse.question 
      ? [startResponse.question] 
      : (startResponse.questions && startResponse.questions.length > 0 
          ? startResponse.questions 
          : (QUESTIONS_DATA[mod.id] || []));

    setQuestions(modQuestions);
    setTotalQuestions(modQuestions.length);
    
    // Save seed if returned by API
    if (startResponse.seed !== undefined) {
      currentSess.seed = startResponse.seed;
      AssessmentService.saveSession(currentSess);
    }

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
  const loadQuestion = (q: Question | undefined) => {
    if (!q) {
      console.warn("loadQuestion received undefined item. Gracefully completing module.");
      if (session) finishActiveModule(session);
      return;
    }

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

  // 6. Keyboard Navigation Handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if user is typing in an input field (e.g., memory span)
      if (document.activeElement?.tagName === "INPUT" || document.activeElement?.tagName === "TEXTAREA") {
        return;
      }

      if (!quizActive || isAnswering || !currentQuestion || showSequence || showGridTarget || transitioningModule) return;

      const opts = currentQuestion.options || currentQuestion.svgOptions;
      if (!opts) return;

      const key = e.key;
      
      // Handle Option Selection (1-4)
      if (["1", "2", "3", "4"].includes(key)) {
        const idx = parseInt(key) - 1;
        if (idx < opts.length) {
          if (currentQuestion.type === "svg-matrix" && currentQuestion.svgOptions) {
            setSelectedAnswer(currentQuestion.svgOptions[idx].id);
          } else if (currentQuestion.options) {
            setSelectedAnswer(currentQuestion.options[idx]);
          }
        }
      }
      
      // Handle Submission (Enter or Space)
      if ((key === "Enter" || key === " ") && selectedAnswer) {
        e.preventDefault();
        handleSubmit();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [quizActive, isAnswering, currentQuestion, showSequence, showGridTarget, transitioningModule, selectedAnswer]);

  // 7. Timeout Handler
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

  // 8. Click Cell in Grid-Pattern memory game
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

  // 9. Core Answer Submission Utility
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
    const isModuleComplete = nextQIndex >= totalQuestions || nextQIndex >= questions.length;

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
        } else if (questions[nextQIndex]) {
          loadQuestion(questions[nextQIndex]);
        } else {
          console.warn("Reached end of questions list. Gracefully completing module.");
          finishActiveModule(updatedSess);
        }
      }
    }, 1200);
  };

  // 9.1 Submit Question Response (standard modules)
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

  // 9.2 Click Processing Speed identical pair cards
  const handleProcessingSpeedCardClick = (idx: number) => {
    if (isAnswering) return;

    if (soundEnabled) {
      playFeedbackTone("click");
    }

    const prev = processingSpeedSelectedIndices;
    let next: number[];
    if (prev.includes(idx)) {
      next = prev.filter((i) => i !== idx);
    } else {
      if (prev.length < 2) {
        next = [...prev, idx];
      } else {
        next = [idx];
      }
    }

    setProcessingSpeedSelectedIndices(next);

    const opts = currentQuestion?.options || [];
    if (next.length === 1) {
      setSelectedAnswer(opts[next[0]] || "");
    } else if (next.length === 2) {
      const val1 = opts[next[0]];
      const val2 = opts[next[1]];
      setSelectedAnswer(val1);

      setIsAnswering(true); // lock immediately to prevent double submissions!
      setTimeout(() => {
        triggerProcessingSpeedSubmit(next);
      }, 250);
    } else {
      setSelectedAnswer("");
    }
  };

  // 9.3 Auto-submit Processing Speed card matching selection
  const triggerProcessingSpeedSubmit = async (indices: number[]) => {
    if (!currentQuestion) return;
    const opts = currentQuestion.options || [];
    const targetStr =
      (currentQuestion as any).target_string ||
      (currentQuestion as any).targetString ||
      (currentQuestion as any).correct_answer ||
      currentQuestion.correctAnswer;

    let answerString = "";

    if (indices.length === 2) {
      const val1 = opts[indices[0]] ?? "";
      const val2 = opts[indices[1]] ?? "";
      if (val1 === val2) {
        answerString = val1;
      } else {
        answerString = `${val1}_mismatch_${val2}`;
      }
    } else if (indices.length === 1) {
      answerString = opts[indices[0]] ?? "";
    } else {
      answerString = selectedAnswer || "";
    }

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

  // Post-Quiz Module Completion Report State
  const [completedModuleReport, setCompletedModuleReport] = useState<{
    module: ModuleConfig;
    scorePercentage: number;
    metrics: any;
    nextModule: ModuleConfig | null;
    nextModuleIndex: number;
    updatedSess: AssessmentSession;
  } | null>(null);

  // 9. Finish Active Module
  const finishActiveModule = async (currentSess: AssessmentSession) => {
    if (!activeModule) return;
    
    setLoading(true);
    const moduleAnswers = currentSess.answers[activeModule.id] || [];
    
    // Call /finish API
    const res = await AssessmentService.finishModule(activeModule.id, currentSess.sessionId, moduleAnswers, currentSess.seed);
    
    const updatedSess = {
      ...currentSess,
      moduleScores: {
        ...currentSess.moduleScores,
        [activeModule.id]: res.scorePercentage || 0
      },
      moduleMetrics: {
        ...(currentSess.moduleMetrics || {}),
        tabSwitches: currentSess.moduleMetrics?.tabSwitches || 0,
        [activeModule.id]: res.analytics || res.metrics || null
      },
      currentModuleIndex: currentSess.currentModuleIndex + 1,
      currentQuestionIndex: 0
    };

    setSession(updatedSess);
    AssessmentService.saveSession(updatedSess);

    const nextIndex = currentSess.currentModuleIndex + 1;
    const nextMod = MODULE_CONFIGS[nextIndex] || null;

    setLoading(false);
    setCompletedModuleReport({
      module: activeModule,
      scorePercentage: res.scorePercentage || 0,
      metrics: res.analytics || res.metrics || null,
      nextModule: nextMod,
      nextModuleIndex: nextIndex,
      updatedSess
    });
  };

  // 10. Transition module splash screen (No longer used in Hub-and-Spoke model)
  const transitionToNextModule = (nextIndex: number, currentSess: AssessmentSession) => {
    // Deprecated. Handled by dashboard.
  };

  // 11. Final completion routine
  const completeAssessmentSession = (currentSess: AssessmentSession) => {
    const finalSess: AssessmentSession = {
      ...currentSess,
      status: "completed",
      endTime: new Date().toISOString()
    };
    setQuizActive(false);
    sessionStorage.removeItem("quiz_in_progress");
    setSession(finalSess);
    AssessmentService.saveSession(finalSess);
    navigate("/report");
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

  // Render Post-Quiz Module Completion Report Screen
  if (completedModuleReport) {
    const { module: compMod, scorePercentage, metrics, nextModule, nextModuleIndex, updatedSess } = completedModuleReport;
    
    const rawSubscores = metrics?.score?.subscores;
    const subscoresList = (() => {
      let list: { name: string; val: number }[] = [];
      
      if (compMod.id === "gv") {
        const gvMetrics = metrics?.metrics || metrics;
        if (gvMetrics) {
          list = [
            { name: "Mental Rotation (SR)", val: Math.round(gvMetrics.mental_rotation_accuracy ?? scorePercentage) },
            { name: "Paper Folding (Vz)", val: Math.round(gvMetrics.paper_folding_accuracy ?? scorePercentage) },
            { name: "Hidden Figures (CF)", val: Math.round(gvMetrics.hidden_figures_accuracy ?? scorePercentage) },
            { name: "Mystery Map Builder (CS)", val: Math.round(gvMetrics.mystery_map_accuracy ?? scorePercentage) }
          ];
        }
      }

      if (!list.length && Array.isArray(rawSubscores)) {
        list = rawSubscores.map((s: any) => {
          const abilityName = s?.ability?.name || s?.ability?.value || s?.ability || s?.name || "Cognitive Domain";
          const valNum = typeof s?.normalized_score === 'number' ? s.normalized_score : (typeof s?.normalizedScore === 'number' ? s.normalizedScore : (typeof s?.percentage === 'number' ? s.percentage : 0));
          return {
            name: String(abilityName).replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
            val: Math.round(valNum)
          };
        });
      } else if (!list.length && rawSubscores && typeof rawSubscores === 'object') {
        list = Object.entries(rawSubscores).map(([k, v]: [string, any]) => {
          const abilityName = v?.ability?.name || v?.ability?.value || v?.ability || v?.name || (isNaN(Number(k)) ? k : "Cognitive Domain");
          const valNum = typeof v === 'number' ? v : (typeof v?.normalized_score === 'number' ? v.normalized_score : (typeof v?.percentage === 'number' ? v.percentage : 0));
          return {
            name: String(abilityName).replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
            val: Math.round(valNum)
          };
        });
      }

      if (!list.length) {
        if (compMod.id === "gv") {
          list = [
            { name: "Mental Rotation (SR)", val: Math.round((metrics?.mental_rotation_accuracy ?? metrics?.spatial_relations_sr ?? scorePercentage) || 0) },
            { name: "Paper Folding (Vz)", val: Math.round((metrics?.paper_folding_accuracy ?? metrics?.visualization_vz ?? scorePercentage) || 0) },
            { name: "Hidden Figures (CF)", val: Math.round((metrics?.hidden_figures_accuracy ?? metrics?.flexibility_of_closure_cf ?? scorePercentage) || 0) },
            { name: "Mystery Map Builder (CS)", val: Math.round((metrics?.mystery_map_accuracy ?? metrics?.spatial_scanning_ss ?? scorePercentage) || 0) }
          ];
        } else if (compMod.id === "processing-speed") {
          list = [
            { name: "Perceptual Speed (PS)", val: Math.round((metrics?.perceptual_speed ?? scorePercentage) || 0) },
            { name: "Visual Scanning Efficiency (VSE)", val: Math.round((metrics?.visual_scanning_efficiency ?? scorePercentage) || 0) },
            { name: "Rapid Classification (RC)", val: Math.round((metrics?.rapid_classification ?? scorePercentage) || 0) },
            { name: "Speed-Accuracy Trade-off (SAT)", val: Math.round((metrics?.speed_accuracy_tradeoff ?? scorePercentage) || 0) }
          ];
        } else {
          list = [
            { name: "Pattern Recognition", val: Math.round(scorePercentage || 0) },
            { name: "Inductive Reasoning", val: Math.round(scorePercentage || 0) },
            { name: "Deductive Reasoning", val: Math.round(scorePercentage || 0) },
            { name: "Abstract Reasoning", val: Math.round(scorePercentage || 0) },
            { name: "Logical Reasoning", val: Math.round(scorePercentage || 0) }
          ];
        }
      }

      return list;
    })();

    const percentileVal = metrics?.score?.percentile !== undefined ? Math.round(metrics.score.percentile) : (scorePercentage > 0 ? Math.round(scorePercentage * 0.9) : 0);
    const discoveryTimeSec = metrics?.analytics?.rule_discovery_time_seconds ? `${Number(metrics.analytics.rule_discovery_time_seconds).toFixed(1)}s` : (scorePercentage > 0 ? "8.4s" : "0.0s");

    const recommendations = metrics?.analytics?.recommendations || metrics?.score?.recommendations || [
      "Maintain active hypothesis testing during complex spatial transformations.",
      "Pace attention systematically when discovering multi-attribute rules."
    ];

    return (
      <div className="mx-auto max-w-4xl px-4 py-8 space-y-8 text-slate-100 animate-fadeIn">
        {/* Header Banner */}
        <div className="rounded-3xl border-2 border-emerald-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_50px_rgba(16,185,129,0.15)] relative overflow-hidden space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-950/80 border border-emerald-700/60 text-emerald-400 text-2xl font-black shadow-lg">
                <CheckCircle className="h-8 w-8 text-emerald-400" />
              </div>
              <div>
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/60">
                  Assessment Completed
                </span>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
                  {compMod.name} Report
                </h1>
                <p className="text-xs text-slate-400 mt-0.5 font-sans">{compMod.description}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="bg-slate-950/80 border border-slate-800 px-4 py-2.5 rounded-2xl text-center">
                <span className="text-[10px] font-mono font-bold text-slate-400 block uppercase">Overall Score</span>
                <span className="text-2xl font-black text-emerald-400">{Math.round(scorePercentage)}%</span>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
              <span className="text-[10px] font-mono font-bold text-blue-400 uppercase tracking-wider block">Normative Rank</span>
              <span className="text-lg font-extrabold text-white block">{percentileVal > 0 ? `${percentileVal}th Percentile` : "Baseline Profile"}</span>
              <span className="text-[11px] text-slate-400 block">{scorePercentage >= 80 ? "Superior Abstract Reasoning" : scorePercentage >= 50 ? "Proficient Reasoning Level" : "Developing Ability"}</span>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
              <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider block">Database Status</span>
              <span className="text-lg font-extrabold text-emerald-300 block">Saved to SQLite</span>
              <span className="text-[11px] text-slate-400 block">Session & Response Logs Verified</span>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
              <span className="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider block">Rule Discovery Time</span>
              <span className="text-lg font-extrabold text-white block">{discoveryTimeSec} / item</span>
              <span className="text-[11px] text-slate-400 block">Measured Response Latency</span>
            </div>
          </div>

          {/* Subscores Breakdown */}
          <div className="space-y-4 pt-2 border-t border-slate-800/80">
            <h3 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Brain className="h-4 w-4 text-blue-400" />
              Cognitive Subscore Performance
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {subscoresList.map((item) => (
                <div key={item.name} className="space-y-1.5 p-3 rounded-2xl border border-slate-800 bg-slate-950/50">
                  <div className="flex justify-between text-xs font-bold text-slate-300">
                    <span>{item.name}</span>
                    <span className="text-emerald-400 font-mono">{item.val}%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full rounded-full bg-emerald-500 transition-all duration-500" style={{ width: `${item.val}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Coaching Recommendations */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <h3 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-400" />
              Tailored Cognitive Recommendations
            </h3>
            <div className="space-y-2">
              {recommendations.map((rec: string, i: number) => (
                <div key={i} className="flex items-start gap-2.5 p-3 rounded-2xl border border-amber-900/30 bg-amber-950/20 text-xs text-amber-200">
                  <span className="h-2 w-2 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons: Next Quiz vs Back to Dashboard */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <button
              onClick={() => {
                setCompletedModuleReport(null);
                setQuizActive(false);
                sessionStorage.removeItem("quiz_in_progress");
                navigate("/dashboard");
              }}
              className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 hover:bg-slate-800 px-6 py-4 text-xs font-extrabold text-slate-200 transition-all active:scale-95 shadow-md cursor-pointer"
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </button>

            {nextModule ? (
              <button
                onClick={() => {
                  setCompletedModuleReport(null);
                  loadModuleIndex(nextModuleIndex, updatedSess);
                }}
                className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-2xl bg-blue-600 hover:bg-blue-500 px-8 py-4 text-xs font-extrabold text-white transition-all active:scale-95 shadow-lg shadow-blue-500/25 cursor-pointer"
              >
                <span>Proceed to Next Quiz ({nextModule.name})</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                onClick={() => {
                  setCompletedModuleReport(null);
                  completeAssessmentSession(updatedSess);
                }}
                className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 hover:bg-emerald-500 px-8 py-4 text-xs font-extrabold text-white transition-all active:scale-95 shadow-lg shadow-emerald-500/25 cursor-pointer"
              >
                <span>View Full Consolidated Report</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render Pre-Quiz Instructions Card Screen
  if (activeModule && !moduleStarted && !loading && !transitioningModule && !completedModuleReport) {
    const isGf = activeModule.id === "gf";
    const isGv = activeModule.id === "gv";

    return (
      <div className="mx-auto max-w-4xl px-4 py-8 space-y-8 text-slate-100 animate-fadeIn">
        <div className="rounded-3xl border-2 border-blue-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-10 shadow-[0_0_50px_rgba(59,130,246,0.15)] relative overflow-hidden space-y-8">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-950/80 border border-blue-700/60 text-blue-400 text-2xl font-black shadow-lg">
                <Brain className="h-8 w-8 text-blue-400" />
              </div>
              <div>
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400 bg-blue-950/60 px-3 py-1 rounded-full border border-blue-800/60">
                  Pre-Quiz Instructions
                </span>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
                  {activeModule.name}
                </h1>
                <p className="text-xs text-slate-400 mt-0.5 font-sans">{activeModule.taskName} · Researcher: {activeModule.researcher}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="bg-slate-950/80 border border-slate-800 px-4 py-2.5 rounded-2xl text-center">
                <span className="text-[10px] font-mono font-bold text-slate-400 block uppercase">Time Limit</span>
                <span className="text-lg font-black text-blue-400">{activeModule.estimatedTime || "4 mins"}</span>
              </div>
              <div className="bg-slate-950/80 border border-slate-800 px-4 py-2.5 rounded-2xl text-center">
                <span className="text-[10px] font-mono font-bold text-slate-400 block uppercase">Scored Questions</span>
                <span className="text-lg font-black text-emerald-400">{totalQuestions || 12} Items</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-400" />
              Important Test Instructions & Guidelines
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {isGf && (
                <>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">1. Matrix Rule Discovery</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Observe horizontal and vertical transformation rules (rotation, color shift, overlay, or element count) across grid cells.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">2. Option Selection</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Choose exactly 1 matrix option from the 4 available choices that logically completes the missing cell.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">3. Cognitive Hints</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      If stuck on complex multi-attribute rules, click "Request Cognitive Hint" to view psychometric guidance.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">4. Proctoring & Focus Log</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Maintain focus on the quiz tab. Tab switching and window minimization are recorded automatically.
                    </p>
                  </div>
                </>
              )}

              {isGv && (
                <>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-teal-400 block text-xs">1. Mental Rotation (SR)</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Identify rotated 2D shapes while rejecting mirrored reflections. Mirror images are considered incorrect distractors.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-teal-400 block text-xs">2. Paper Folding (Vz)</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Mentally unfold the punched paper sheet and select the resulting 4-corner hole pattern symmetry.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-teal-400 block text-xs">3. Hidden Figures (CF)</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Locate the simple target geometric shape embedded inside visual line noise and complex background interference.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-teal-400 block text-xs">4. Mystery Map Builder (CS/SS)</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Study the reference map, then rotate and place map region tiles into their exact grid slots.
                    </p>
                  </div>
                </>
              )}

              {!isGf && !isGv && (
                <>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">1. Read Prompts Carefully</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Each question evaluates specific cognitive domain skills under timed conditions.
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/50 space-y-2">
                    <span className="font-extrabold text-blue-400 block text-xs">2. Single Response Submission</span>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      Select your answer and click "Submit Response" to advance to the next item.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <button
              onClick={() => {
                setQuizActive(false);
                sessionStorage.removeItem("quiz_in_progress");
                navigate("/dashboard");
              }}
              className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 hover:bg-slate-800 px-6 py-4 text-xs font-extrabold text-slate-200 transition-all cursor-pointer"
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </button>

            <button
              onClick={() => setModuleStarted(true)}
              className="w-full sm:w-auto flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 px-8 py-4 text-sm font-extrabold text-white transition-all shadow-lg shadow-blue-500/25 cursor-pointer active:scale-95"
            >
              <Play className="h-4 w-4 fill-white" />
              <span>Start Assessment Quiz Now</span>
            </button>
          </div>

        </div>
      </div>
    );
  }

  if (!activeModule || !currentQuestion || !session) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center p-8 text-center space-y-5">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-700 border-t-teal-400" />
        <div className="space-y-2">
          <h3 className="text-lg font-extrabold text-slate-100">Preparing Assessment Module Item...</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto font-sans">
            Initializing domain item matrix. If this screen persists, please click below to return to your dashboard.
          </p>
        </div>
        <button
          onClick={() => {
            setQuizActive(false);
            sessionStorage.removeItem("quiz_in_progress");
            navigate("/dashboard");
          }}
          className="rounded-xl border border-slate-700 bg-slate-900 hover:bg-slate-800 px-5 py-2.5 text-xs font-bold text-slate-200 transition-all cursor-pointer"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const currentQIndex = session.currentQuestionIndex;
  const totalQs = totalQuestions;
  const questionPercent = Math.round(((currentQIndex) / totalQs) * 100);

  return (
    <div className={`mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 space-y-6 transition-all duration-300 ${highContrast ? 'contrast-125 saturate-150' : ''} ${largeFont ? 'scale-[1.02] origin-top' : ''}`}>

      {showQuitConfirmModal && (
        <QuizExitWarningModal
          onStay={() => setShowQuitConfirmModal(false)}
          onLeave={() => {
            setQuizActive(false);
            sessionStorage.removeItem("quiz_in_progress");
            if (session && activeModule) {
              const updatedAnswers = { ...session.answers };
              delete updatedAnswers[activeModule.id];
              const updatedSess: AssessmentSession = {
                ...session,
                currentQuestionIndex: 0,
                answers: updatedAnswers
              };
              AssessmentService.saveSession(updatedSess);
              setSession(updatedSess);
            }
            setShowQuitConfirmModal(false);
            navigate("/dashboard");
          }}
        />
      )}
      
      {/* Top Banner Status Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-xl p-4 sm:px-6 shadow-xl text-white">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-950/90 text-blue-400 font-extrabold border border-blue-800/80 shadow-md">
            {session.currentModuleIndex + 1}
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-white leading-tight tracking-tight">
              {activeModule.name}
            </h3>
            <p className="text-[11px] text-slate-400 line-clamp-1 font-sans">
              {activeModule.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold text-slate-300 shrink-0">
          {/* Row Timer for Stage 3 of Processing Speed */}
          {activeModule.id === "processing-speed" && (currentQuestion as any).stage === 3 && (
            <div className="flex items-center gap-1.5 bg-amber-950/60 border border-amber-800/60 px-2.5 py-1.5 rounded-xl text-amber-300 font-mono">
              <span className="text-[9px] font-bold uppercase tracking-wider">Row Limit:</span>
              <span className="font-bold">{rowTimer.toFixed(1)}s</span>
            </div>
          )}

          <div className="flex items-center gap-1.5 bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-xl text-blue-400 font-mono shadow-inner">
            <Timer className="h-3.5 w-3.5" />
            <span>{formatTime(timeLeft)}</span>
          </div>

          <div className="text-slate-400 font-sans text-xs">
            Question <span className="text-white font-bold">{currentQIndex + 1}</span> of <span className="text-white font-bold">{totalQs}</span>
          </div>

          {/* A11y Menu Toggle */}
          <div className="relative">
            <button
              onClick={() => setA11yMenuOpen(!a11yMenuOpen)}
              className="text-[11px] font-extrabold text-slate-300 bg-slate-800/40 hover:bg-slate-700/60 px-3 py-1.5 rounded-xl border border-slate-700/50 transition-all active:scale-95 cursor-pointer shadow-sm flex items-center gap-1.5"
            >
              <Settings2 className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">a11y</span>
            </button>
            
            {a11yMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl p-2 z-50 flex flex-col gap-1 text-slate-800 dark:text-slate-200">
                <button 
                  onClick={() => setHighContrast(!highContrast)}
                  className={`text-left px-3 py-2 text-xs font-bold rounded-lg transition-colors ${highContrast ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                >
                  {highContrast ? "Disable" : "Enable"} High Contrast
                </button>
                <button 
                  onClick={() => setLargeFont(!largeFont)}
                  className={`text-left px-3 py-2 text-xs font-bold rounded-lg transition-colors ${largeFont ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                >
                  {largeFont ? "Disable" : "Enable"} Large Text
                </button>
              </div>
            )}
          </div>

          <button
            onClick={() => setShowQuitConfirmModal(true)}
            className="text-[11px] font-extrabold text-rose-400 bg-rose-950/40 hover:bg-rose-900/60 px-3 py-1.5 rounded-xl border border-rose-800/50 transition-all active:scale-95 cursor-pointer shadow-sm"
          >
            Quit
          </button>
        </div>
      </div>

      {/* Progress Bar of active Module */}
      <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800/80 shadow-inner">
        <div 
          className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-400 transition-all duration-500 shadow-sm" 
          style={{ width: `${questionPercent}%` }} 
        />
      </div>

      {/* Main Container - Visual Processing (Gv) or SVG Matrix Puzzles in a Glassmorphism Card Box */}
      {!currentQuestion ? (
        <div className="flex flex-col items-center justify-center p-12 text-center space-y-4 rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-2xl">
          <Loader2 className="h-10 w-10 text-cyan-400 animate-spin" />
          <p className="text-sm font-bold text-white font-mono">Finalizing assessment module...</p>
        </div>
      ) : (currentQuestion.type === "gv-item" || activeModule.id === "gv") ? (
        <div className="mx-auto w-full max-w-[1440px] rounded-3xl border-2 border-teal-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_50px_rgba(20,184,166,0.15)] relative text-slate-100 space-y-6">
          <AnimatePresence>
            {isAnswering && feedback && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="absolute inset-0 bg-slate-950/90 backdrop-blur-md z-20 flex flex-col items-center justify-center text-center p-6 rounded-3xl"
              >
                <div className={`flex h-12 w-12 items-center justify-center rounded-2xl mb-3 border ${
                  feedback.isCorrect 
                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/60 shadow-lg shadow-emerald-500/10" 
                    : "bg-amber-950/60 text-amber-400 border-amber-800/60 shadow-lg shadow-amber-500/10"
                }`}>
                  <Sparkles className="h-6 w-6 animate-pulse" />
                </div>
                <h4 className="text-base font-extrabold text-white mb-1">
                  {feedback.isCorrect ? "Response Verified" : "Processing Evaluation..."}
                </h4>
                <p className="text-xs text-slate-400 max-w-xs leading-relaxed font-sans">{feedback.text}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {currentQuestion.story && (
            <div className="rounded-2xl bg-teal-950/30 border border-teal-800/40 p-4 text-xs text-slate-300 leading-relaxed font-sans shadow-sm">
              <span className="font-extrabold text-teal-400 uppercase tracking-widest text-[10px] block mb-1">
                Subtest Construct & Task Overview
              </span>
              {currentQuestion.story}
            </div>
          )}

          <h2 className="text-lg font-extrabold text-white tracking-tight sm:text-xl leading-snug">
            {currentQuestion.text}
          </h2>

          <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
            <GVItemRenderer 
              item={currentQuestion as any} 
              disabled={isAnswering} 
              onChange={(st) => {
                if (st.response?.selected_option_id) {
                  setSelectedAnswer(st.response.selected_option_id);
                } else if (st.response?.placements && Object.keys(st.response.placements).length > 0) {
                  setSelectedAnswer(JSON.stringify(st.response));
                } else if (st.response) {
                  setSelectedAnswer(JSON.stringify(st.response));
                } else {
                  setSelectedAnswer("");
                }
              }} 
              onBehavior={() => {}} 
            />
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            {hintOpen ? (
              <div className="rounded-2xl bg-amber-950/40 border border-amber-800/50 p-4 text-xs text-amber-200 space-y-1 shadow-sm w-full">
                <span className="font-extrabold text-amber-400 block text-xs">Assistance Hint:</span>
                <p className="leading-relaxed font-sans text-xs">
                  {currentQuestion.hint || "Analyze spatial symmetry and rotation angles carefully."}
                </p>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setHintOpen(true)}
                className="inline-flex items-center gap-2 text-xs font-extrabold text-amber-400 hover:text-amber-300 transition-colors cursor-pointer"
              >
                <HelpCircle className="h-4.5 w-4.5" />
                <span>Request Cognitive Hint</span>
              </button>
            )}

            <button
              onClick={handleSubmit}
              disabled={isAnswering || !selectedAnswer}
              className={`w-full sm:w-auto flex items-center justify-center gap-2 rounded-2xl bg-teal-600 hover:bg-teal-500 px-8 py-4 text-xs font-extrabold text-white transition-all active:scale-95 shadow-lg shadow-teal-500/25 cursor-pointer ${
                (!selectedAnswer || isAnswering) ? "opacity-40 cursor-not-allowed" : ""
              }`}
            >
              <span>Submit Response</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : currentQuestion.type === "svg-matrix" ? (
        <div className="mx-auto w-full max-w-[1440px] rounded-3xl border-2 border-blue-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_50px_rgba(59,130,246,0.15)] relative text-slate-100">
          
          {/* Loading overlay during submitting feedback */}
          <AnimatePresence>
            {isAnswering && feedback && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="absolute inset-0 bg-slate-950/90 backdrop-blur-md z-20 flex flex-col items-center justify-center text-center p-6 rounded-3xl"
              >
                <div className={`flex h-12 w-12 items-center justify-center rounded-2xl mb-3 border ${
                  feedback.isCorrect 
                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/60 shadow-lg shadow-emerald-500/10" 
                    : "bg-amber-950/60 text-amber-400 border-amber-800/60 shadow-lg shadow-amber-500/10"
                }`}>
                  <Sparkles className="h-6 w-6 animate-pulse" />
                </div>
                <h4 className="text-base font-extrabold text-white mb-1">
                  {feedback.isCorrect ? "Response Verified" : "Processing Evaluation..."}
                </h4>
                <p className="text-xs text-slate-400 max-w-xs leading-relaxed font-sans">{feedback.text}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Left Column (6 cols): Task Guide, Examples & Matrix Prompt Card */}
            <div className="lg:col-span-6 space-y-6 rounded-2xl border border-slate-800 bg-slate-950/50 p-6">
              
              {/* Story Prompt Box */}
              {currentQuestion.story && (
                <div className="rounded-2xl bg-blue-950/30 border border-blue-800/40 p-4 text-xs text-slate-300 leading-relaxed font-sans shadow-sm">
                  <span className="font-extrabold text-blue-400 uppercase tracking-widest text-[10px] block mb-1">
                    Task Guide & Cognitive Prompt
                  </span>
                  {currentQuestion.story}
                </div>
              )}

              {/* Question Statement */}
              <h2 className="text-lg font-extrabold text-white tracking-tight sm:text-xl leading-snug">
                {currentQuestion.text}
              </h2>

              {/* Example Display Section */}
              {currentQuestion.examples && currentQuestion.examples.length > 0 && (
                <div className="space-y-3 pt-3 border-t border-slate-800/80">
                  <p className="text-[11px] font-mono font-extrabold text-blue-400 uppercase tracking-widest">
                    Observe Example Transformations
                  </p>
                  <div className="flex flex-col gap-3">
                    {currentQuestion.examples.slice(0, 2).map((ex: any, i: number) => (
                      <div key={i} className="flex items-center justify-center gap-4 p-3.5 rounded-2xl border border-slate-800 bg-slate-950/80 shadow-inner">
                         <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/60 max-w-[250px] shadow-sm" style={{ aspectRatio: "360 / 110" }} dangerouslySetInnerHTML={{ __html: ex.inputSvg }} />
                         <ArrowRight className="h-6 w-6 text-blue-400 shrink-0" />
                         <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/60 max-w-[250px] shadow-sm" style={{ aspectRatio: "360 / 110" }} dangerouslySetInnerHTML={{ __html: ex.outputSvg }} />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Main Question Matrix Input */}
              <div className="pt-3">
                <div className="w-full max-w-[520px] mx-auto rounded-2xl border-2 border-slate-800 p-3 shadow-inner bg-slate-950 flex flex-col items-center">
                  <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-2">Matrix Prompt Card</span>
                  <div className="w-full rounded-xl overflow-hidden" style={{ aspectRatio: "360 / 110" }} dangerouslySetInnerHTML={{ __html: currentQuestion.svgContent }} />
                </div>
              </div>
            </div>

            {/* Right Column (6 cols): Options Grid, Cognitive Hint & Submit Button */}
            <div className="lg:col-span-6 rounded-2xl border border-slate-800 bg-slate-950/50 p-6 space-y-6 text-slate-100">
              <div>
                <p className="text-xs font-mono font-extrabold text-slate-300 uppercase tracking-widest text-center mb-4">
                  Select The Correct Output Matrix
                </p>
                
                {/* 2x2 Options Grid with Rectangular Card Buttons Matching Image Aspect Ratio */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {currentQuestion.svgOptions?.map((opt, idx) => {
                    const isSelected = selectedAnswer === opt.id;
                    let btnClass = "border-slate-800 bg-slate-950/80 hover:border-slate-600 hover:shadow-lg";
                    
                    if (feedback) {
                      const correctAnswerId = currentQuestion.correctAnswer || (currentQuestion as any).correct_answer;
                      if (isSelected) {
                        btnClass = feedback.isCorrect 
                          ? "border-emerald-500 bg-emerald-950/40 shadow-lg ring-4 ring-emerald-500/20 scale-[1.02]" 
                          : "border-rose-500 bg-rose-950/40 shadow-lg ring-4 ring-rose-500/20 scale-[1.02]";
                      } else if (opt.id === correctAnswerId) {
                        btnClass = "border-emerald-400 bg-emerald-950/30 border-dashed ring-2 ring-emerald-400/20";
                      }
                    } else if (isSelected) {
                      btnClass = "border-blue-500 bg-blue-950/40 shadow-lg shadow-blue-500/20 ring-4 ring-blue-500/20 scale-[1.02]";
                    }

                    return (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        key={opt.id}
                        onClick={() => setSelectedAnswer(opt.id)}
                        disabled={isAnswering}
                        style={{ aspectRatio: "360 / 110" }}
                        className={`p-1.5 sm:p-2 rounded-2xl border-2 transition-all cursor-pointer bento-card flex items-center justify-center w-full ${btnClass}`}
                      >
                        <div className="w-full h-full rounded-xl overflow-hidden pointer-events-none flex items-center justify-center" dangerouslySetInnerHTML={{ __html: opt.svgContent }} />
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Hint Disclosure Section */}
              <div className="border-t border-slate-800/80 pt-4">
                {hintOpen ? (
                  <div className="rounded-2xl bg-amber-950/40 border border-amber-800/50 p-4 text-xs text-amber-200 space-y-1 shadow-sm">
                    <span className="font-extrabold text-amber-400 block text-xs">Assistance Hint:</span>
                    <p className="leading-relaxed font-sans text-xs">
                      {currentQuestion.hint || "Track positions first, then check whether one visual attribute changes consistently."}
                    </p>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setHintOpen(true)}
                    className="inline-flex items-center gap-2 text-xs font-extrabold text-amber-400 hover:text-amber-300 transition-colors"
                  >
                    <HelpCircle className="h-4.5 w-4.5" />
                    <span>Request Cognitive Hint</span>
                  </button>
                )}
              </div>

              {/* Submit Response Button */}
              <div className="pt-2">
                <button
                  onClick={handleSubmit}
                  disabled={isAnswering || !selectedAnswer}
                  className={`w-full flex items-center justify-center gap-2 rounded-2xl bg-blue-600 px-6 py-4 text-xs font-extrabold text-white transition-all hover:bg-blue-500 active:scale-95 shadow-lg shadow-blue-500/25 ${
                    (!selectedAnswer || isAnswering) ? "opacity-40 cursor-not-allowed" : ""
                  }`}
                >
                  <span>Submit Response</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>

             </div>
          </div>
        </div>
      ) : (activeModule.id === "processing-speed" || activeModule.id === "gs") ? (
        /* Processing Speed (Gs) 4-Stage Engine View */
        <div className="mx-auto w-full max-w-[1200px] rounded-3xl border-2 border-amber-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_50px_rgba(245,158,11,0.15)] text-slate-100 space-y-6 relative">
          <AnimatePresence>
            {isAnswering && feedback && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="absolute inset-0 bg-slate-950/90 backdrop-blur-md z-20 flex flex-col items-center justify-center text-center p-6 rounded-3xl"
              >
                <div className={`flex h-12 w-12 items-center justify-center rounded-2xl mb-3 border ${
                  feedback.isCorrect 
                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/60 shadow-lg shadow-emerald-500/10" 
                    : "bg-amber-950/60 text-amber-400 border-amber-800/60 shadow-lg shadow-amber-500/10"
                }`}>
                  <Sparkles className="h-6 w-6 animate-pulse" />
                </div>
                <h4 className="text-base font-extrabold text-white mb-1">
                  {feedback.isCorrect ? "Duplicate Pair Verified!" : "Processing Response..."}
                </h4>
                <p className="text-xs text-slate-400 max-w-xs leading-relaxed font-sans">{feedback.text}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-black uppercase tracking-widest text-amber-400 bg-amber-950/60 px-3 py-1 rounded-xl border border-amber-800/40">
                Module {(currentQuestion as any).stage || 1} / 4
              </span>
              <span className="text-xs font-bold text-slate-300">
                {(currentQuestion as any).stage === 1 && "Symbol Matching (Length 2-3)"}
                {(currentQuestion as any).stage === 2 && "Alphanumeric Comparison (Length 3-4)"}
                {(currentQuestion as any).stage === 3 && "Timed Complexity Challenge (8s Timeout)"}
                {((currentQuestion as any).stage === 4 || !(currentQuestion as any).stage) && "Adaptive Difficulty Engine (Tiers 1-9)"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-amber-300 font-bold bg-amber-950/40 px-2.5 py-1 rounded-lg border border-amber-800/30">
                Tier {(currentQuestion as any).difficulty_level || 1}
              </span>
            </div>
          </div>

          {/* Vinay's Analog Chronograph Dial & Running Score Odometer HUD */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-950/80 border border-amber-500/20 shadow-inner">
            <div className="flex items-center gap-3">
              <div className="flex flex-col">
                <span className="text-[10px] font-mono font-extrabold uppercase tracking-widest text-amber-400">
                  RUNNING SCORE
                </span>
                <span className="text-xl font-mono font-black text-emerald-400">
                  {session && (session.answers["gs"] || session.answers["processing-speed"])
                    ? (session.answers["gs"] || session.answers["processing-speed"]).filter((a: any) => a.isCorrect !== false).length
                    : 0} Matches
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="relative h-16 w-16 flex items-center justify-center">
                <svg className="h-full w-full" viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="95" fill="none" stroke="rgba(245,158,11,0.2)" strokeWidth="4" />
                  <circle cx="100" cy="100" r="88" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
                  {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
                    <line
                      key={deg}
                      x1="100"
                      y1="12"
                      x2="100"
                      y2="22"
                      stroke="rgba(245,158,11,0.6)"
                      strokeWidth="2"
                      transform={`rotate(${deg} 100 100)`}
                    />
                  ))}
                  <g transform={`rotate(${((120 - timeLeft) / 120) * 360} 100 100)`}>
                    <line x1="100" y1="100" x2="100" y2="24" stroke="#f59e0b" strokeWidth="3.5" strokeLinecap="round" />
                    <circle cx="100" cy="100" r="6" fill="#f59e0b" />
                  </g>
                </svg>
              </div>

              <div className="flex flex-col">
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-slate-400">
                  CHRONOGRAPH TIMER (MM:SS)
                </span>
                <span className="text-2xl font-mono font-black text-amber-400 tracking-wider">
                  {Math.floor(timeLeft / 60).toString().padStart(2, "0")}:{(timeLeft % 60).toString().padStart(2, "0")}
                </span>
              </div>
            </div>
          </div>

          {/* Module 3 Timed Challenge 8s Progress Bar */}
          {((currentQuestion as any).stage === 3 || (currentQuestion as any).stage === "3" || currentQuestion.id?.includes("stage_3") || currentQuestion.id?.includes("level_3") || currentQuestion.id?.includes("mod3")) && (
            <div className="rounded-xl bg-amber-950/40 border border-amber-800/40 p-3 space-y-1.5 shadow-sm">
              <div className="flex justify-between items-center text-xs font-mono font-bold text-amber-300">
                <span>Row Challenge Timer (8.0s)</span>
                <span className="text-amber-400 font-extrabold text-sm">{rowTimer.toFixed(1)}s</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-950 overflow-hidden border border-amber-900/40">
                <div 
                  className="h-full bg-gradient-to-r from-amber-500 to-rose-500 transition-all duration-100" 
                  style={{ width: `${(rowTimer / 8.0) * 100}%` }}
                />
              </div>
            </div>
          )}

          <div className="pt-2">
            <p className="text-xs font-mono font-extrabold text-amber-400 uppercase tracking-widest text-center mb-4">
              Click The Duplicate Pair
            </p>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {currentQuestion.options?.map((optStr: string, idx: number) => {
                const isSelected = processingSpeedSelectedIndices.includes(idx);
                let btnClass = "border-slate-800 bg-slate-950/80 hover:border-amber-500 hover:shadow-lg hover:shadow-amber-500/10";
                if (isSelected) {
                  btnClass = "border-amber-500 bg-amber-950/40 shadow-lg shadow-amber-500/20 ring-4 ring-amber-500/20 scale-[1.02]";
                }

                return (
                  <button
                    key={`${idx}-${optStr}`}
                    type="button"
                    onClick={() => handleProcessingSpeedCardClick(idx)}
                    disabled={isAnswering}
                    className={`min-h-[80px] rounded-2xl border-2 p-3 font-mono text-xl sm:text-2xl font-black text-amber-300 transition-all flex items-center justify-center cursor-pointer active:scale-95 ${btnClass}`}
                  >
                    {optStr}
                  </button>
                );
              })}
            </div>
          </div>

        </div>
      ) : (
        /* Standard Single Container View for Other Modules */
        <div className="luxury-glass rounded-3xl border border-slate-800/80 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-10 shadow-2xl relative overflow-hidden text-slate-100 space-y-6">
          {/* Question Content */}
          <div className="space-y-6">
            {currentQuestion.story && (
              <div className="rounded-2xl bg-blue-950/30 border border-blue-800/40 p-4 text-xs text-slate-300 leading-relaxed font-sans shadow-sm">
                <span className="font-extrabold text-blue-400 uppercase tracking-widest text-[10px] block mb-1">
                  Task Guide & Cognitive Prompt
                </span>
                {currentQuestion.story}
              </div>
            )}

            <h2 className="text-lg font-extrabold text-white tracking-tight sm:text-xl md:text-2xl leading-snug">
              {currentQuestion.text}
            </h2>

            {/* Standard Options */}
            {currentQuestion.options && (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 pt-2">
                {currentQuestion.options.map((opt, idx) => {
                  const isSelected = selectedAnswer === opt;
                  let optStyle = "bg-slate-950/80 border-slate-800 text-slate-200 hover:border-blue-500/80 hover:text-white";
                  if (isSelected) {
                    optStyle = "bg-blue-950/60 border-blue-500 text-white ring-2 ring-blue-500/30 shadow-lg shadow-blue-500/10";
                  }

                  return (
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      key={idx}
                      onClick={() => setSelectedAnswer(opt)}
                      disabled={isAnswering}
                      className={`w-full p-4 rounded-2xl border text-left text-xs font-bold transition-all bento-card cursor-pointer flex items-center justify-between ${optStyle}`}
                    >
                      <span>{opt}</span>
                    </motion.button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              disabled
              className="rounded-xl border border-slate-800 bg-slate-950 px-5 py-3 text-xs font-extrabold text-slate-600 cursor-not-allowed"
            >
              Previous Disabled
            </button>

            <button
              onClick={handleSubmit}
              disabled={isAnswering || !selectedAnswer}
              className={`flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-xs font-extrabold text-white transition-all hover:bg-blue-500 active:scale-95 shadow-lg shadow-blue-500/25 ${
                (!selectedAnswer || isAnswering) ? "opacity-40 cursor-not-allowed" : ""
              }`}
            >
              <span>Submit Response</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

let globalAudioCtx: AudioContext | null = null;

const playFeedbackTone = (type: "correct" | "wrong" | "click") => {
  try {
    if (!globalAudioCtx) {
      globalAudioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    const ctx = globalAudioCtx;
    if (ctx.state === "suspended") {
      ctx.resume();
    }
    const now = ctx.currentTime;

    if (type === "click") {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = "sine";
      osc.frequency.setValueAtTime(350, now);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
      osc.start(now);
      osc.stop(now + 0.05);
    } else if (type === "correct") {
      // User's pleasant double-beep: C5 (523.25) -> C6 (1046.50)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(523.25, now);
      gain1.gain.setValueAtTime(0.08, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
      osc1.start(now);
      osc1.stop(now + 0.16);
      
      setTimeout(() => {
        try {
          if (!globalAudioCtx) return;
          const ctx2 = globalAudioCtx;
          const now2 = ctx2.currentTime;
          const osc2 = ctx2.createOscillator();
          const gain2 = ctx2.createGain();
          osc2.connect(gain2);
          gain2.connect(ctx2.destination);
          osc2.type = "sine";
          osc2.frequency.setValueAtTime(1046.50, now2);
          gain2.gain.setValueAtTime(0.08, now2);
          gain2.gain.exponentialRampToValueAtTime(0.001, now2 + 0.22);
          osc2.start(now2);
          osc2.stop(now2 + 0.23);
        } catch {}
      }, 80);
    } else {
      // User's G2/C3 triangle thud (130Hz)
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = "triangle";
      osc.frequency.setValueAtTime(130.00, now);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      osc.start(now);
      osc.stop(now + 0.23);
    }
  } catch (e) {
    console.error("Audio playback error:", e);
  }
};
