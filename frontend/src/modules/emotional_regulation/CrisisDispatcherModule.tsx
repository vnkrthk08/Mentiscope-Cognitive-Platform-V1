import React, { useState, useEffect, useRef } from "react";
import { 
  ShieldAlert, 
  Flame, 
  AlertTriangle, 
  Truck, 
  Ambulance, 
  Shield, 
  LifeBuoy, 
  CheckCircle2, 
  Timer, 
  HeartHandshake, 
  ArrowRight,
  Play,
  RotateCcw
} from "lucide-react";

interface CrisisDispatcherModuleProps {
  sessionId: string;
  studentId: string;
  onComplete: (score: number, metrics: any) => void;
}

interface Scenario {
  id: string;
  module: number;
  type: string;
  title: string;
  description: string;
  location: string;
  severity: "Low" | "Medium" | "High" | "Critical";
  livesAtRisk: number;
  timeLimit: number; // seconds
  requiredResources: string[];
}

const SCENARIOS: Scenario[] = [
  // Module 1: Baseline Assessment
  {
    id: "m1_s1",
    module: 1,
    type: "Road Accident",
    title: "Minor Intersection Collision",
    description: "Two-vehicle collision at a major intersection. One driver has neck pain, traffic is congested.",
    location: "5th Ave & Main St",
    severity: "Low",
    livesAtRisk: 2,
    timeLimit: 25,
    requiredResources: ["Ambulance", "Police Unit"],
  },
  {
    id: "m1_s2",
    module: 1,
    type: "Medical Emergency",
    title: "Elderly Collapse in Public Park",
    description: "Elderly citizen collapsed on jogging track. Conscious but disoriented. Immediate vitals assessment needed.",
    location: "Centennial Park",
    severity: "Medium",
    livesAtRisk: 1,
    timeLimit: 20,
    requiredResources: ["Ambulance"],
  },
  {
    id: "m1_s3",
    module: 1,
    type: "Electrical Hazard",
    title: "Sparking High-Voltage Transformer",
    description: "Street transformer sparking violently near gathering crowd. Explosive sparks and fire risk.",
    location: "Elm Street Residential",
    severity: "High",
    livesAtRisk: 5,
    timeLimit: 20,
    requiredResources: ["Fire Truck", "Police Unit"],
  },

  // Module 2: Stress Induction (Strict timers, multi-resource emergency)
  {
    id: "m2_s1",
    module: 2,
    type: "Structural Fire",
    title: "Apartment Complex 3rd Floor Fire",
    description: "Flames spreading rapidly. Residents trapped on balconies, toxic black smoke in hallways.",
    location: "Sunset Apartments",
    severity: "Critical",
    livesAtRisk: 14,
    timeLimit: 12,
    requiredResources: ["Fire Truck", "Ambulance", "Rescue Team"],
  },
  {
    id: "m2_s2",
    module: 2,
    type: "Hazardous Gas Leak",
    title: "Underground Gas Main Rupture",
    description: "Strong methane odor at metro entrance. Immediate commercial concourse evacuation required.",
    location: "Downtown Metro Concourse",
    severity: "Critical",
    livesAtRisk: 25,
    timeLimit: 12,
    requiredResources: ["Police Unit", "Fire Truck"],
  },

  // Module 3: Failure & Recovery (Resilience & Adaptability)
  {
    id: "m3_s1",
    module: 3,
    type: "Structural Collapse",
    title: "Commercial Parking Deck Collapse",
    description: "Multi-level garage deck collapsed. Vehicles crushed, instability prevents direct entry.",
    location: "Central Plaza Garage",
    severity: "Critical",
    livesAtRisk: 8,
    timeLimit: 10,
    requiredResources: ["Rescue Team", "Ambulance"],
  },
  {
    id: "m3_s2",
    module: 3,
    type: "Industrial Chemical Spill",
    title: "Corrosive Chemical Reactor Leak",
    description: "Acid vapor cloud escaping toward nearby community perimeter. Neutralization units urgently needed.",
    location: "Industrial District Sector 4",
    severity: "Critical",
    livesAtRisk: 30,
    timeLimit: 10,
    requiredResources: ["Fire Truck", "Police Unit", "Rescue Team"],
  },

  // Module 4: Adaptive Challenge (Fast-changing parameters)
  {
    id: "m4_s1",
    module: 4,
    type: "Hospital Blackout",
    title: "ICU Emergency Power Grid Failure",
    description: "Hospital backup generators failed. ICU life-support on 8-minute battery reserve.",
    location: "St. Jude General Hospital",
    severity: "Critical",
    livesAtRisk: 22,
    timeLimit: 10,
    requiredResources: ["Ambulance", "Fire Truck", "Police Unit"],
  },
  {
    id: "m4_s2",
    module: 4,
    type: "Urban Wildfire",
    title: "Canyon Brush Fire Approaching Residences",
    description: "Sudden winds pushing rapid firefront into canyon estates. Immediate evacuation barricades needed.",
    location: "Canyon Ridge Estates",
    severity: "Critical",
    livesAtRisk: 45,
    timeLimit: 10,
    requiredResources: ["Fire Truck", "Police Unit", "Rescue Team"],
  },
];

const AVAILABLE_RESOURCES = [
  { name: "Ambulance", icon: Ambulance, color: "text-rose-400 border-rose-500/40 bg-rose-950/30" },
  { name: "Fire Truck", icon: Flame, color: "text-amber-400 border-amber-500/40 bg-amber-950/30" },
  { name: "Police Unit", icon: Shield, color: "text-blue-400 border-blue-500/40 bg-blue-950/30" },
  { name: "Rescue Team", icon: LifeBuoy, color: "text-emerald-400 border-emerald-500/40 bg-emerald-950/30" },
];

export default function CrisisDispatcherModule({ sessionId, studentId, onComplete }: CrisisDispatcherModuleProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedResources, setSelectedResources] = useState<string[]>([]);
  const [timeLeft, setTimeLeft] = useState<number>(SCENARIOS[0].timeLimit);
  const [gameplayPhase, setGameplayPhase] = useState<"intro" | "active" | "feedback">("intro");
  
  // Tactical Metrics
  const [panicClicks, setPanicClicks] = useState(0);
  const [totalCitizensSaved, setTotalCitizensSaved] = useState(0);
  const [totalLivesLost, setTotalLivesLost] = useState(0);
  const [decisionsHistory, setDecisionsHistory] = useState<Array<{ correct: boolean; rt: number; module: number }>>([]);
  const [feedbackState, setFeedbackState] = useState<{ isSuccess: boolean; title: string; desc: string } | null>(null);

  const scenarioStartTimeRef = useRef<number>(Date.now());
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const currentScenario = SCENARIOS[currentIndex];

  // 1. Timer countdown
  useEffect(() => {
    if (gameplayPhase !== "active") return;

    setTimeLeft(currentScenario.timeLimit);
    scenarioStartTimeRef.current = Date.now();

    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerIntervalRef.current!);
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [currentIndex, gameplayPhase]);

  // 2. Panic click counter (clicks anywhere on command center when stress timer is under 5 seconds)
  const handleContainerClick = () => {
    if (timeLeft <= 5 && gameplayPhase === "active") {
      setPanicClicks((p) => p + 1);
    }
  };

  // 3. Toggle resource selection
  const toggleResource = (name: string) => {
    setSelectedResources((prev) => 
      prev.includes(name) ? prev.filter((r) => r !== name) : [...prev, name]
    );
  };

  // 4. Timeout Event
  const handleTimeout = () => {
    const rt = Date.now() - scenarioStartTimeRef.current;
    setTotalLivesLost((l) => l + Math.ceil(currentScenario.livesAtRisk * 0.5));
    setDecisionsHistory((prev) => [...prev, { correct: false, rt, module: currentScenario.module }]);

    // Log to backend
    fetch("/api/modules/emotional-regulation/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        module: currentScenario.module,
        scenarioId: currentScenario.id,
        eventType: "TIMEOUT",
        decisionTimeMs: rt,
        panicClicks,
        livesAtRisk: currentScenario.livesAtRisk
      })
    }).catch(() => {});

    setFeedbackState({
      isSuccess: false,
      title: "CRITICAL TIMEOUT",
      desc: `Units failed to deploy in time. Secondary casualties reported at ${currentScenario.location}.`
    });
    setGameplayPhase("feedback");
  };

  // 5. Submit Resource Dispatch
  const handleDispatch = () => {
    if (selectedResources.length === 0 || gameplayPhase !== "active") return;
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

    const rt = Date.now() - scenarioStartTimeRef.current;
    
    // Check if user selected all required resources
    const req = currentScenario.requiredResources;
    const isCorrect = 
      req.length === selectedResources.length &&
      req.every((r) => selectedResources.includes(r));

    if (isCorrect) {
      setTotalCitizensSaved((s) => s + currentScenario.livesAtRisk);
    } else {
      setTotalLivesLost((l) => l + Math.ceil(currentScenario.livesAtRisk * 0.4));
    }

    setDecisionsHistory((prev) => [...prev, { correct: isCorrect, rt, module: currentScenario.module }]);

    // Log event to backend
    fetch("/api/modules/emotional-regulation/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        module: currentScenario.module,
        scenarioId: currentScenario.id,
        eventType: isCorrect ? "CORRECT_DECISION" : "WRONG_DECISION",
        decisionTimeMs: rt,
        panicClicks,
        livesAtRisk: currentScenario.livesAtRisk
      })
    }).catch(() => {});

    setFeedbackState({
      isSuccess: isCorrect,
      title: isCorrect ? "DISPATCH SUCCESSFUL" : "SUB-OPTIMAL ALLOCATION",
      desc: isCorrect
        ? `All ${currentScenario.livesAtRisk} citizens secured at ${currentScenario.location}. Perimeter stabilized.`
        : `Deployment mismatch. Required units were: ${req.join(", ")}.`
    });
    setGameplayPhase("feedback");
  };

  // 6. Next Scenario or Finish Assessment
  const handleNext = () => {
    setSelectedResources([]);
    const nextIdx = currentIndex + 1;

    if (nextIdx >= SCENARIOS.length) {
      finalizeAssessment();
    } else {
      setCurrentIndex(nextIdx);
      setGameplayPhase("active");
    }
  };

  // 7. Calculate scientific score and sync to backend
  const finalizeAssessment = async () => {
    const totalDecisions = decisionsHistory.length || 1;
    const corrects = decisionsHistory.filter((d) => d.correct).length;
    const accuracy = (corrects / totalDecisions) * 100;

    // Dimension estimates
    const recoveryResilience = Math.min(99, Math.max(50, Math.round(accuracy * 0.8 + 20)));
    const stressTolerance = Math.min(99, Math.max(45, Math.round(accuracy * 0.7 + Math.max(0, 30 - panicClicks * 3))));
    const adaptationPersistence = Math.min(99, Math.max(50, Math.round(accuracy * 0.85 + 15)));
    const decisionStability = Math.min(99, Math.max(50, Math.round(accuracy * 0.9 + 10)));

    // Weights: Recovery (30%), Stress (25%), Adaptation (25%), Stability (20%)
    const overallScore = Math.round(
      recoveryResilience * 0.30 +
      stressTolerance * 0.25 +
      adaptationPersistence * 0.25 +
      decisionStability * 0.20
    );

    const metrics = {
      overallScore,
      recoveryResilience,
      stressTolerance,
      adaptationPersistence,
      decisionStability,
      panicClicks,
      citizensSaved: totalCitizensSaved,
      livesLost: totalLivesLost,
      accuracyRate: Math.round(accuracy)
    };

    try {
      const res = await fetch("/api/modules/emotional-regulation/finish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId,
          studentId,
          scorePercentage: overallScore,
          metrics
        })
      });
      if (res.ok) {
        const data = await res.json();
        onComplete(data.scorePercentage || overallScore, data.metrics || metrics);
        return;
      }
    } catch (e) {
      console.warn("Crisis finish endpoint warning:", e);
    }

    onComplete(overallScore, metrics);
  };

  return (
    <div 
      onClick={handleContainerClick}
      className="mx-auto w-full max-w-4xl rounded-3xl border-2 border-red-500/30 bg-slate-950 p-6 sm:p-10 shadow-[0_0_50px_rgba(239,68,68,0.15)] text-slate-100 select-none"
    >
      
      {/* Command Center Tactical Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5 mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-red-950/70 border border-red-700/50 text-red-400 shadow-sm">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider bg-red-950 text-red-300 px-2 py-0.5 rounded border border-red-800">
                CRISIS DISPATCH HUD
              </span>
              <span className="text-xs font-mono text-slate-400">
                Module {currentScenario?.module} / 4
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              Emergency Dispatch Command Center
            </h2>
          </div>
        </div>

        {/* Live Incident Status Badges */}
        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2">
            <span className="text-slate-400 text-[10px] uppercase">Saved:</span>
            <span className="font-bold text-emerald-400">{totalCitizensSaved}</span>
          </div>
          <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2">
            <span className="text-slate-400 text-[10px] uppercase">Incident:</span>
            <span className="font-bold text-slate-200">{currentIndex + 1} / {SCENARIOS.length}</span>
          </div>
        </div>
      </div>

      {/* PHASE 1: INTRO TO SIMULATION */}
      {gameplayPhase === "intro" && (
        <div className="space-y-6 py-6 text-center max-w-lg mx-auto">
          <div className="space-y-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-red-400 block">
              High-Stress Emotional Regulation Assessment
            </span>
            <h3 className="text-2xl font-black text-white tracking-tight">
              Tactical Dispatch Simulation
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              You are the Chief Emergency Dispatcher. Review incoming high-urgency distress calls and deploy the exact combination of response units before timers expire. Maintain decision composure under strict stress!
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-left">
            {AVAILABLE_RESOURCES.map((res) => {
              const Icon = res.icon;
              return (
                <div key={res.name} className={`p-3 rounded-xl border flex items-center gap-2.5 ${res.color}`}>
                  <Icon className="h-5 w-5 shrink-0" />
                  <span className="text-xs font-bold">{res.name}</span>
                </div>
              );
            })}
          </div>

          <button
            onClick={() => setGameplayPhase("active")}
            className="w-full flex items-center justify-center gap-2 rounded-2xl bg-red-600 hover:bg-red-500 py-4 text-xs font-extrabold text-white transition-all shadow-lg shadow-red-600/30 cursor-pointer active:scale-95"
          >
            <Play className="h-4 w-4 fill-white" />
            <span>Engage Command Center</span>
          </button>
        </div>
      )}

      {/* PHASE 2: ACTIVE INCIDENT SCENARIO */}
      {gameplayPhase === "active" && (
        <div className="space-y-6">
          
          {/* Incident Emergency Banner */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase ${
                  currentScenario.severity === "Critical" 
                    ? "bg-red-950 text-red-400 border border-red-800 animate-pulse" 
                    : "bg-amber-950 text-amber-400 border border-amber-800"
                }`}>
                  Priority: {currentScenario.severity}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  📍 {currentScenario.location}
                </span>
              </div>

              {/* Countdown Timer Dial */}
              <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl font-mono text-sm font-black border ${
                timeLeft <= 5 
                  ? "bg-red-950/80 text-red-400 border-red-600 animate-bounce" 
                  : "bg-slate-800/80 text-white border-slate-700"
              }`}>
                <Timer className="h-4 w-4" />
                <span>00:{timeLeft < 10 ? `0${timeLeft}` : timeLeft}</span>
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-lg sm:text-xl font-extrabold text-white">
                {currentScenario.title}
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {currentScenario.description}
              </p>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono pt-2 border-t border-slate-800 text-slate-400">
              <span>Lives At Risk: <strong className="text-red-400 font-bold">{currentScenario.livesAtRisk}</strong></span>
              <span>Type: <strong className="text-slate-200">{currentScenario.type}</strong></span>
            </div>
          </div>

          {/* Unit Dispatch Bay */}
          <div className="space-y-3">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 block">
              Resource Deployment Bay (Select Units to Dispatch):
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {AVAILABLE_RESOURCES.map((res) => {
                const Icon = res.icon;
                const isSelected = selectedResources.includes(res.name);
                return (
                  <button
                    key={res.name}
                    type="button"
                    onClick={() => toggleResource(res.name)}
                    className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center justify-center gap-2 cursor-pointer active:scale-95 ${
                      isSelected
                        ? "border-red-500 bg-red-950/50 shadow-lg shadow-red-500/20 ring-2 ring-red-500/40"
                        : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
                    }`}
                  >
                    <Icon className={`h-8 w-8 ${isSelected ? "text-red-400" : "text-slate-400"}`} />
                    <span className="text-xs font-bold text-center">{res.name}</span>
                    <span className={`text-[9px] font-mono px-2 py-0.5 rounded ${isSelected ? "bg-red-900 text-red-200" : "bg-slate-800 text-slate-400"}`}>
                      {isSelected ? "ALLOCATED" : "STANDBY"}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dispatch Action Button */}
          <button
            onClick={handleDispatch}
            disabled={selectedResources.length === 0}
            className={`w-full flex items-center justify-center gap-2 rounded-2xl bg-red-600 hover:bg-red-500 py-4 text-xs font-extrabold text-white transition-all shadow-lg shadow-red-600/30 cursor-pointer active:scale-95 ${
              selectedResources.length === 0 ? "opacity-40 cursor-not-allowed" : ""
            }`}
          >
            <Truck className="h-4 w-4" />
            <span>Authorize & Deploy Units ({selectedResources.length} Selected)</span>
          </button>
        </div>
      )}

      {/* PHASE 3: FEEDBACK INTERMEDIATE SCREEN */}
      {gameplayPhase === "feedback" && feedbackState && (
        <div className="space-y-6 py-6 text-center max-w-lg mx-auto">
          <div className={`h-16 w-16 mx-auto rounded-2xl flex items-center justify-center border ${
            feedbackState.isSuccess 
              ? "bg-emerald-950/60 border-emerald-700/60 text-emerald-400" 
              : "bg-red-950/60 border-red-700/60 text-red-400"
          }`}>
            {feedbackState.isSuccess ? <CheckCircle2 className="h-8 w-8" /> : <AlertTriangle className="h-8 w-8" />}
          </div>

          <div className="space-y-2">
            <h3 className="text-2xl font-black text-white tracking-tight">
              {feedbackState.title}
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              {feedbackState.desc}
            </p>
          </div>

          <button
            onClick={handleNext}
            className="w-full flex items-center justify-center gap-2 rounded-2xl bg-blue-600 hover:bg-blue-500 py-4 text-xs font-extrabold text-white transition-all shadow-md shadow-blue-600/30 cursor-pointer active:scale-95"
          >
            <span>Proceed to Next Incident</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}

    </div>
  );
}
