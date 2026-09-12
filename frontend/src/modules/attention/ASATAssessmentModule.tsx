import React, { useState, useEffect, useRef, useCallback } from "react";
import { ShapeRenderer, ShapeType, ColorKey, SHAPES, COLORS, randomShape, randomColor, randomNonTarget } from "./ShapeRenderer";
import { 
  Eye, 
  Target, 
  Zap, 
  RefreshCw, 
  ArrowRight, 
  CheckCircle2, 
  Play, 
  Sparkles, 
  Check, 
  AlertTriangle 
} from "lucide-react";

interface ASATAssessmentModuleProps {
  sessionId: string;
  studentId: string;
  onComplete: (score: number, metrics: any) => void;
}

type SubmoduleType = "sustained" | "selective" | "divided" | "executive";

const TOTAL_TRIALS = 14; // Streamlined 14 trials per submodule (56 total) for responsive testing flow

export default function ASATAssessmentModule({ sessionId, studentId, onComplete }: ASATAssessmentModuleProps) {
  const [currentSubmodule, setCurrentSubmodule] = useState<SubmoduleType>("sustained");
  const [phase, setPhase] = useState<"intro" | "running" | "isi" | "submodule_summary">("intro");
  const [trialIndex, setTrialIndex] = useState(0);

  // Subtest 1: Sustained Attention
  const [sustainedStimulus, setSustainedStimulus] = useState<{ shape: ShapeType; color: ColorKey; isTarget: boolean } | null>(null);
  const [sustainedHits, setSustainedHits] = useState(0);
  const [sustainedFalseAlarms, setSustainedFalseAlarms] = useState(0);
  const [sustainedRTs, setSustainedRTs] = useState<number[]>([]);

  // Subtest 2: Selective Attention
  const [selectiveRow, setSelectiveRow] = useState<Array<{ shape: ShapeType; color: ColorKey; isTarget: boolean }>>([]);
  const [selectiveHits, setSelectiveHits] = useState(0);
  const [selectiveFalseAlarms, setSelectiveFalseAlarms] = useState(0);
  const [selectiveRTs, setSelectiveRTs] = useState<number[]>([]);

  // Subtest 3: Divided Attention
  const [dividedStimulus, setDividedStimulus] = useState<{ shape: ShapeType; color: ColorKey; word: string; wordColor: ColorKey; isMatch: boolean } | null>(null);
  const [dividedHits, setDividedHits] = useState(0);
  const [dividedFalseAlarms, setDividedFalseAlarms] = useState(0);
  const [dividedRTs, setDividedRTs] = useState<number[]>([]);

  // Subtest 4: Executive Attention
  const [executiveRule, setExecutiveRule] = useState<ShapeType>("circle");
  const [executiveRow, setExecutiveRow] = useState<Array<{ shape: ShapeType; color: ColorKey }>>([]);
  const [executiveHits, setExecutiveHits] = useState(0);
  const [executiveErrors, setExecutiveErrors] = useState(0);
  const [executiveRTs, setExecutiveRTs] = useState<number[]>([]);

  // Submodule completed scores
  const [subscores, setSubscores] = useState<{ sustained?: number; selective?: number; divided?: number; executive?: number }>({});
  
  // Timing
  const stimStartTimeRef = useRef<number>(Date.now());
  const respondedRef = useRef<boolean>(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Submodule metadata
  const submoduleMeta = {
    sustained: {
      name: "Sustained Attention",
      targetText: "Press SPACEBAR or Click when you see a BLUE TRIANGLE",
      desc: "Measures continuous vigilance and resistance to visual fatigue over rapid sequential stimuli.",
      weight: "25% Weight"
    },
    selective: {
      name: "Selective Attention",
      targetText: "Click on the BLUE TRIANGLE among distracting shapes",
      desc: "Tests focus filtering and target isolation across cluttered visual environments.",
      weight: "25% Weight"
    },
    divided: {
      name: "Divided Attention (Dual Task)",
      targetText: "Press SPACEBAR or Click ONLY when Left Shape is BLUE TRIANGLE AND Right Word says BLUE",
      desc: "Evaluates split cognitive throughput across simultaneous perceptual streams.",
      weight: "20% Weight"
    },
    executive: {
      name: "Executive Attention (Rule Switching)",
      targetText: "Click the shape matching the dynamic RULE at the top",
      desc: "Assesses cognitive flexibility and rapid rule adaptation under time pressure.",
      weight: "30% Weight"
    }
  };

  // 1. Generate next trial for current submodule
  const spawnTrial = useCallback((sub: SubmoduleType, tIdx: number) => {
    respondedRef.current = false;
    stimStartTimeRef.current = Date.now();

    if (sub === "sustained") {
      const isTarget = Math.random() < 0.4;
      const stim = isTarget ? { shape: "triangle" as ShapeType, color: "blue" as ColorKey, isTarget: true } : { ...randomNonTarget(), isTarget: false };
      setSustainedStimulus(stim);
    } else if (sub === "selective") {
      const count = tIdx < 5 ? 5 : tIdx < 10 ? 8 : 10;
      const hasTarget = Math.random() < 0.7;
      const targetIdx = hasTarget ? Math.floor(Math.random() * count) : -1;
      const row = Array.from({ length: count }, (_, idx) => {
        if (idx === targetIdx) {
          return { shape: "triangle" as ShapeType, color: "blue" as ColorKey, isTarget: true };
        }
        return { ...randomNonTarget(), isTarget: false };
      });
      setSelectiveRow(row);
    } else if (sub === "divided") {
      const isMatch = Math.random() < 0.35;
      const colorWords = ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE"];
      if (isMatch) {
        setDividedStimulus({
          shape: "triangle",
          color: "blue",
          word: "BLUE",
          wordColor: "blue",
          isMatch: true
        });
      } else {
        const shapeObj = randomNonTarget();
        const randWord = colorWords[Math.floor(Math.random() * colorWords.length)];
        setDividedStimulus({
          shape: shapeObj.shape,
          color: shapeObj.color,
          word: randWord,
          wordColor: randomColor(),
          isMatch: false
        });
      }
    } else if (sub === "executive") {
      // Switch rule every 3-4 trials
      const rules: ShapeType[] = ["circle", "square", "triangle", "star", "diamond"];
      const activeRule = rules[Math.floor(tIdx / 3) % rules.length];
      setExecutiveRule(activeRule);

      const items = Array.from({ length: 6 }, () => ({
        shape: rules[Math.floor(Math.random() * rules.length)],
        color: randomColor()
      }));
      // Guarantee at least one matching item
      items[Math.floor(Math.random() * items.length)].shape = activeRule;
      setExecutiveRow(items);
    }

    setPhase("running");

    // Auto-advance if no response within duration
    const displayDuration = sub === "sustained" ? 1400 : sub === "divided" ? 1800 : 2500;
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      handleTrialTimeout(sub, tIdx);
    }, displayDuration);
  }, []);

  // 2. Timeout handling for unresponded trials
  const handleTrialTimeout = (sub: SubmoduleType, tIdx: number) => {
    if (respondedRef.current) return;
    respondedRef.current = true;

    // Log trial event to backend
    fetch("/api/modules/attention/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        submodule: sub,
        trialIndex: tIdx,
        stimulus: "timeout",
        response: "NONE",
        isCorrect: false,
        reactionTimeMs: 0
      })
    }).catch(() => {});

    advanceTrial(sub, tIdx);
  };

  // 3. User Response Handler
  const handleResponse = (sub: SubmoduleType, responseValue: string, isCorrect: boolean) => {
    if (respondedRef.current || phase !== "running") return;
    respondedRef.current = true;
    if (timerRef.current) clearTimeout(timerRef.current);

    const rt = Date.now() - stimStartTimeRef.current;

    if (sub === "sustained") {
      if (isCorrect) {
        setSustainedHits((h) => h + 1);
        setSustainedRTs((rts) => [...rts, rt]);
      } else {
        setSustainedFalseAlarms((fa) => fa + 1);
      }
    } else if (sub === "selective") {
      if (isCorrect) {
        setSelectiveHits((h) => h + 1);
        setSelectiveRTs((rts) => [...rts, rt]);
      } else {
        setSelectiveFalseAlarms((fa) => fa + 1);
      }
    } else if (sub === "divided") {
      if (isCorrect) {
        setDividedHits((h) => h + 1);
        setDividedRTs((rts) => [...rts, rt]);
      } else {
        setDividedFalseAlarms((fa) => fa + 1);
      }
    } else if (sub === "executive") {
      if (isCorrect) {
        setExecutiveHits((h) => h + 1);
        setExecutiveRTs((rts) => [...rts, rt]);
      } else {
        setExecutiveErrors((e) => e + 1);
      }
    }

    // Log event to backend
    fetch("/api/modules/attention/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        submodule: sub,
        trialIndex,
        stimulus: responseValue,
        response: responseValue,
        isCorrect,
        reactionTimeMs: rt
      })
    }).catch(() => {});

    advanceTrial(sub, trialIndex);
  };

  // 4. Advance trial or finish submodule
  const advanceTrial = (sub: SubmoduleType, currentIdx: number) => {
    setPhase("isi");
    const nextIdx = currentIdx + 1;

    setTimeout(() => {
      if (nextIdx >= TOTAL_TRIALS) {
        finishSubmodule(sub);
      } else {
        setTrialIndex(nextIdx);
        spawnTrial(sub, nextIdx);
      }
    }, 400); // 400ms inter-stimulus interval
  };

  // 5. Finish a submodule
  const finishSubmodule = (sub: SubmoduleType) => {
    let score = 70;
    if (sub === "sustained") {
      score = Math.min(99, Math.max(45, Math.round((sustainedHits / Math.max(1, TOTAL_TRIALS * 0.4)) * 75 + Math.max(0, 25 - sustainedFalseAlarms * 5))));
    } else if (sub === "selective") {
      score = Math.min(99, Math.max(45, Math.round((selectiveHits / Math.max(1, TOTAL_TRIALS * 0.7)) * 80 + Math.max(0, 20 - selectiveFalseAlarms * 5))));
    } else if (sub === "divided") {
      score = Math.min(99, Math.max(45, Math.round((dividedHits / Math.max(1, TOTAL_TRIALS * 0.35)) * 75 + Math.max(0, 25 - dividedFalseAlarms * 5))));
    } else if (sub === "executive") {
      score = Math.min(99, Math.max(45, Math.round((executiveHits / TOTAL_TRIALS) * 85 + Math.max(0, 15 - executiveErrors * 3))));
    }

    const updatedSubscores = { ...subscores, [sub]: score };
    setSubscores(updatedSubscores);

    if (sub === "sustained") {
      setCurrentSubmodule("selective");
      setPhase("intro");
      setTrialIndex(0);
    } else if (sub === "selective") {
      setCurrentSubmodule("divided");
      setPhase("intro");
      setTrialIndex(0);
    } else if (sub === "divided") {
      setCurrentSubmodule("executive");
      setPhase("intro");
      setTrialIndex(0);
    } else if (sub === "executive") {
      // Completed all 4!
      finalizeAssessment(updatedSubscores);
    }
  };

  // 6. Finalize complete ASAT assessment
  const finalizeAssessment = async (finalSubscores: { sustained?: number; selective?: number; divided?: number; executive?: number }) => {
    const s1 = finalSubscores.sustained || 75;
    const s2 = finalSubscores.selective || 75;
    const s3 = finalSubscores.divided || 75;
    const s4 = finalSubscores.executive || 75;

    // ASAT Psychometric Formula: 25% Sustained + 25% Selective + 20% Divided + 30% Executive
    const overallScore = Math.round(s1 * 0.25 + s2 * 0.25 + s3 * 0.20 + s4 * 0.30);

    const metrics = {
      submoduleScores: {
        sustained: s1,
        selective: s2,
        divided: s3,
        executive: s4
      },
      overallScore,
      completedAt: new Date().toISOString()
    };

    try {
      const res = await fetch("/api/modules/attention/finish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId,
          studentId,
          submoduleScores: finalSubscores,
          moduleResults: metrics
        })
      });
      if (res.ok) {
        const data = await res.json();
        onComplete(data.scorePercentage || overallScore, data.metrics || metrics);
        return;
      }
    } catch (e) {
      console.warn("Attention finish endpoint warning, using local score:", e);
    }

    onComplete(overallScore, metrics);
  };

  // Listen to keyboard spacebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" && phase === "running") {
        e.preventDefault();
        if (currentSubmodule === "sustained") {
          handleResponse("sustained", "SPACE", Boolean(sustainedStimulus?.isTarget));
        } else if (currentSubmodule === "divided") {
          handleResponse("divided", "SPACE", Boolean(dividedStimulus?.isMatch));
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [phase, currentSubmodule, sustainedStimulus, dividedStimulus]);

  // Clean timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const meta = submoduleMeta[currentSubmodule];

  return (
    <div className="mx-auto w-full max-w-4xl rounded-3xl border-2 border-rose-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-10 shadow-[0_0_50px_rgba(244,63,94,0.15)] text-slate-100">
      
      {/* Module Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-950/60 border border-rose-700/50 text-rose-400 shadow-sm">
            <Eye className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider bg-rose-950 text-rose-300 px-2 py-0.5 rounded border border-rose-800">
                ASAT Module
              </span>
              <span className="text-xs font-semibold text-slate-400">
                Subtest: {meta.name}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              Adaptive Shape Attention Task
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {["sustained", "selective", "divided", "executive"].map((sub, i) => {
            const isCurrent = currentSubmodule === sub;
            const isDone = subscores[sub as SubmoduleType] !== undefined;
            return (
              <div
                key={sub}
                className={`h-2.5 w-8 rounded-full transition-all ${
                  isDone ? "bg-emerald-500" : isCurrent ? "bg-rose-500 ring-2 ring-rose-400/40" : "bg-slate-800"
                }`}
                title={`Subtest ${i + 1}: ${sub}`}
              />
            );
          })}
        </div>
      </div>

      {/* PHASE 1: SUBMODULE INTRO SCREEN */}
      {phase === "intro" && (
        <div className="space-y-6 py-6 text-center max-w-lg mx-auto">
          <div className="space-y-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-rose-400 block">
              {meta.weight}
            </span>
            <h3 className="text-2xl font-black text-white tracking-tight">
              {meta.name}
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {meta.desc}
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-950/80 border border-rose-900/40 text-left space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase text-rose-400">
              <Target className="h-4 w-4" />
              <span>Target Rule:</span>
            </div>
            <p className="text-sm font-semibold text-rose-200">
              {meta.targetText}
            </p>
            {currentSubmodule === "sustained" && (
              <div className="flex items-center justify-center pt-2">
                <ShapeRenderer shape="triangle" color="blue" size={90} />
              </div>
            )}
          </div>

          <button
            onClick={() => {
              setTrialIndex(0);
              spawnTrial(currentSubmodule, 0);
            }}
            className="w-full flex items-center justify-center gap-2 rounded-2xl bg-rose-600 hover:bg-rose-500 py-4 text-xs font-extrabold text-white transition-all shadow-lg shadow-rose-600/30 cursor-pointer active:scale-95"
          >
            <Play className="h-4 w-4 fill-white" />
            <span>Start {meta.name}</span>
          </button>
        </div>
      )}

      {/* PHASE 2: RUNNING TRIALS */}
      {(phase === "running" || phase === "isi") && (
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-slate-800 pb-3">
            <span>Trial {trialIndex + 1} of {TOTAL_TRIALS}</span>
            <span className="text-rose-400 font-semibold">{meta.name}</span>
          </div>

          <div className="min-h-[260px] flex items-center justify-center rounded-2xl bg-slate-950/60 border border-slate-800/80 p-6 relative overflow-hidden">
            {phase === "isi" ? (
              <div className="h-3 w-3 rounded-full bg-slate-700 animate-ping" />
            ) : currentSubmodule === "sustained" && sustainedStimulus ? (
              <div className="flex flex-col items-center gap-4 animate-scaleUp">
                <ShapeRenderer shape={sustainedStimulus.shape} color={sustainedStimulus.color} size={130} />
                <span className="text-xs text-slate-400 font-mono">Press SPACEBAR or Click if Blue Triangle</span>
              </div>
            ) : currentSubmodule === "selective" ? (
              <div className="flex flex-wrap items-center justify-center gap-4 max-w-xl">
                {selectiveRow.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleResponse("selective", `${item.shape}_${item.color}`, item.isTarget)}
                    className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-rose-500 hover:bg-slate-800 transition-all cursor-pointer active:scale-95"
                  >
                    <ShapeRenderer shape={item.shape} color={item.color} size={65} />
                  </button>
                ))}
              </div>
            ) : currentSubmodule === "divided" && dividedStimulus ? (
              <div className="flex items-center justify-center gap-12 animate-scaleUp">
                <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Left Channel: Shape</span>
                  <ShapeRenderer shape={dividedStimulus.shape} color={dividedStimulus.color} size={90} />
                </div>
                <span className="text-2xl font-black text-slate-600">+</span>
                <div className="flex flex-col items-center gap-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 min-w-[140px]">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Right Channel: Word</span>
                  <span className="text-3xl font-black font-mono tracking-wider" style={{ color: COLORS[dividedStimulus.wordColor] }}>
                    {dividedStimulus.word}
                  </span>
                </div>
              </div>
            ) : currentSubmodule === "executive" ? (
              <div className="space-y-6 w-full text-center">
                <div className="inline-block px-4 py-2 rounded-xl bg-rose-950/80 border border-rose-700/60 text-xs font-mono font-bold text-rose-300">
                  CURRENT RULE: Click Any {executiveRule.toUpperCase()}
                </div>
                <div className="flex flex-wrap items-center justify-center gap-4">
                  {executiveRow.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleResponse("executive", item.shape, item.shape === executiveRule)}
                      className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-rose-500 hover:bg-slate-800 transition-all cursor-pointer active:scale-95"
                    >
                      <ShapeRenderer shape={item.shape} color={item.color} size={70} />
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </div>

          {/* Action response button for sustained & divided */}
          {(currentSubmodule === "sustained" || currentSubmodule === "divided") && (
            <div className="flex justify-center pt-2">
              <button
                onClick={() => {
                  if (currentSubmodule === "sustained") {
                    handleResponse("sustained", "SPACE", Boolean(sustainedStimulus?.isTarget));
                  } else {
                    handleResponse("divided", "SPACE", Boolean(dividedStimulus?.isMatch));
                  }
                }}
                className="w-full sm:w-80 flex items-center justify-center gap-2 rounded-2xl bg-rose-600 hover:bg-rose-500 py-3.5 text-xs font-extrabold text-white transition-all shadow-md shadow-rose-600/30 cursor-pointer active:scale-95"
              >
                <CheckCircle2 className="h-4 w-4" />
                <span>Target Match (SPACEBAR)</span>
              </button>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
