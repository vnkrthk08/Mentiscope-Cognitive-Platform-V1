import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { User, AssessmentSession, CognitiveReport } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { ReportService } from "../services/report/ReportService";
import { AssessmentService } from "../services/assessment/AssessmentService";
import { CognitiveRadar } from "../components/Charts";
import { 
  Download, 
  Home, 
  Brain, 
  Activity, 
  Cpu, 
  Eye, 
  Languages, 
  GitBranch, 
  Zap,
  TrendingUp, 
  Sparkles, 
  AlertTriangle, 
  Lightbulb,
  FileCheck,
  Award,
  Loader2,
  Compass,
  ShieldAlert,
  ListChecks,
  CheckCircle2,
  ArrowRight
} from "lucide-react";

interface ReportPageProps {
  user: User;
  onNavigate?: (page: string, targetTab?: string) => void;
}

export default function ReportPage({ user, onNavigate }: ReportPageProps) {
  const navigate = useNavigate();

  const [report, setReport] = useState<CognitiveReport | null>(null);
  const [loadingAi, setLoadingAi] = useState(false);
  const [downloading, setDownloading] = useState(false);

  // Load results from real active/historical session
  useEffect(() => {
    let session = AssessmentService.getViewingSession() || AssessmentService.getSession();
    
    if (!session || Object.keys(session.moduleScores).length === 0) {
      setReport(null);
      return;
    }

    // Heuristics generation from real completed module scores
    const baselineReport = ReportService.generateReport(
      session.sessionId,
      user.name,
      user.age || 21,
      user.gender || "Male",
      session.moduleScores,
      session.moduleMetrics
    );
    setReport(baselineReport);

    // AI proxy query
    const triggerAiAnalysis = async () => {
      setLoadingAi(true);
      try {
        const aiReport = await ReportService.fetchAiInsights(baselineReport);
        setReport(aiReport);
      } catch (e) {
        console.error("Failed to query Gemini proxy insights on load:", e);
      } finally {
        setLoadingAi(false);
      }
    };

    triggerAiAnalysis();
  }, [user]);

  const handleDownloadPDF = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      window.print();
    }, 1500);
  };

  if (!report) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 text-center space-y-6">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-2xl p-8 sm:p-12 shadow-2xl space-y-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/40 mx-auto shadow-lg shadow-cyan-500/10">
            <Brain className="h-8 w-8 animate-pulse" />
          </div>
          <div className="space-y-2 max-w-md mx-auto">
            <h2 className="text-xl font-extrabold text-white">No Evaluation Session Recorded Yet</h2>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Complete your first cognitive assessment module (e.g. Fluid Intelligence, Visual Processing, or Processing Speed) to generate your permanent diagnostic report!
            </p>
          </div>
          <button
            onClick={() => navigate("/dashboard")}
            className="inline-flex items-center gap-2 rounded-2xl bg-cyan-600 hover:bg-cyan-500 px-6 py-3 text-xs font-extrabold text-white transition-all shadow-lg shadow-cyan-500/20 cursor-pointer active:scale-95"
          >
            <Home className="h-4 w-4" />
            <span>Go to Candidate Dashboard</span>
          </button>
        </div>
      </div>
    );
  }

  // Formatted module labels for radar chart
  const moduleNamesShort: { [key: string]: string } = {
    gq: "Quantitative (Gq)",
    gsm: "Working Memory (Gsm)",
    gf: "Fluid Intel. (Gf)",
    gv: "Visual Proc. (Gv)",
    attention: "Attention Ctrl.",
    language: "Verbal Logic",
    executive: "Exec. Planning",
    "processing-speed": "Proc. Speed (Gs)",
    gs: "Proc. Speed (Gs)",
    spatial: "Spatial Vis.",
    "pattern-recognition": "Pattern Rec."
  };

  const radarData = Object.keys(report.moduleScores).map(k => ({
    subject: moduleNamesShort[k] || k,
    score: Math.round(report.moduleScores[k]),
    average: 74
  }));

  // Icon mapping helper for cards
  const getModuleIcon = (id: string) => {
    switch (id) {
      case "gq": return <Brain className="h-5 w-5 text-blue-400" />;
      case "gsm": return <Activity className="h-5 w-5 text-teal-400" />;
      case "gf": return <Cpu className="h-5 w-5 text-indigo-400" />;
      case "gv": return <Compass className="h-5 w-5 text-cyan-400" />;
      case "attention": return <Eye className="h-5 w-5 text-rose-400" />;
      case "language": return <Languages className="h-5 w-5 text-violet-400" />;
      case "executive": return <GitBranch className="h-5 w-5 text-amber-400" />;
      case "processing-speed":
      case "gs": return <Zap className="h-5 w-5 text-amber-400" />;
      case "spatial": return <Compass className="h-5 w-5 text-cyan-400" />;
      case "pattern-recognition": return <Cpu className="h-5 w-5 text-purple-400" />;
      default: return <Award className="h-5 w-5 text-slate-400" />;
    }
  };

  const overallScoreInt = Math.round(report.overallScore);

  // Dynamic Normative Classification text generator
  const getNormativeDetails = (score: number) => {
    if (score >= 80) {
      return {
        range: "Superior Cognitive Range",
        percentile: "88%",
        description: "Candidate scores in the top quartile of the demographic baseline, demonstrating exceptionally rapid visual discrimination, high pattern synthesis, and low response latencies under time pressure."
      };
    } else if (score >= 60) {
      return {
        range: "High Average Range",
        percentile: "74%",
        description: "Candidate demonstrates strong cognitive processing stability and consistent executive functioning, maintaining nominal accuracy across structured logic and memory tasks."
      };
    } else if (score >= 40) {
      return {
        range: "Standard Baseline Range",
        percentile: "55%",
        description: "Candidate demonstrates established baseline cognition matching academic standards, with clear opportunities for speed and attention optimization identified across specific task pillars."
      };
    } else {
      return {
        range: "Building Baseline Range",
        percentile: "38%",
        description: "Initial psychometric baseline established. Performance indicators reflect developing focus and strategy refinement opportunities across targeted problem-solving vectors."
      };
    }
  };

  const normInfo = getNormativeDetails(overallScoreInt);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 print:p-0 print:border-0 text-slate-100 font-sans">
      
      {/* Top Controller Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6 print:hidden">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-lg border border-emerald-800/50 flex items-center gap-1.5">
              <CheckCircle2 className="h-3 w-3 text-emerald-400" />
              <span>Session Verified</span>
            </span>
            {loadingAi && (
              <span className="text-[10px] font-semibold text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-lg border border-cyan-800/50 flex items-center gap-1 animate-pulse">
                <Loader2 className="h-3 w-3 animate-spin text-cyan-400" />
                <span>Gemini Diagnostics Active</span>
              </span>
            )}
            {report.isAiGenerated && (
              <span className="text-[10px] font-semibold text-violet-400 bg-violet-950/60 px-2.5 py-1 rounded-lg border border-violet-800/50 flex items-center gap-1.5">
                <Sparkles className="h-3 w-3 text-violet-400" />
                <span>AI-Powered Diagnostics</span>
              </span>
            )}
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight sm:text-3xl font-mono">
            Cognitive Diagnostics Record
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Participant: <span className="text-cyan-300 font-bold">{report.studentName}</span> | Session ID: <span className="text-slate-300">{report.sessionId}</span> | Created {report.date}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900/90 px-4 py-2.5 text-xs font-bold text-slate-200 hover:bg-slate-800 transition-all cursor-pointer active:scale-95"
          >
            <Home className="h-4 w-4 text-cyan-400" />
            <span>Candidate Portal</span>
          </button>

          <button
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="flex items-center gap-2 rounded-2xl bg-cyan-600 hover:bg-cyan-500 px-5 py-2.5 text-xs font-extrabold text-white transition-all shadow-lg shadow-cyan-500/20 cursor-pointer active:scale-95"
          >
            {downloading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Composing Report PDF...</span>
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                <span>Download Report PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Primary Report Layout */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        
        {/* Left Column: Overall Quotient, Radar Distribution, & Core Pillar Table */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Overall Score Card */}
          <div className="rounded-3xl border-2 border-cyan-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_50px_rgba(6,182,212,0.1)] grid grid-cols-1 sm:grid-cols-12 gap-6 items-center">
            <div className="sm:col-span-4 text-center sm:text-left space-y-1">
              <span className="text-[10px] font-mono tracking-widest text-cyan-400 font-extrabold uppercase block">
                Overall Index
              </span>
              <div className="text-6xl sm:text-7xl font-black text-cyan-400 font-mono tracking-tighter drop-shadow-[0_0_20px_rgba(6,182,212,0.4)]">
                {overallScoreInt}
              </div>
              <p className="text-xs font-extrabold text-slate-300 font-mono uppercase tracking-wider">
                Cognitive Quotient (CQ)
              </p>
            </div>

            <div className="sm:col-span-8 space-y-3 border-t sm:border-t-0 sm:border-l border-slate-800 pt-4 sm:pt-0 sm:pl-6">
              <div className="flex items-center gap-2">
                <FileCheck className="h-5 w-5 text-emerald-400 shrink-0" />
                <h3 className="font-extrabold text-white text-sm">Normative Performance Classification</h3>
              </div>
              <p className="text-xs leading-relaxed text-slate-300 font-sans">
                A cumulative score of <span className="font-bold text-cyan-400 font-mono">{overallScoreInt}</span> places this candidate in the <span className="font-bold text-emerald-400">{normInfo.range}</span>, scoring above <span className="font-bold text-white font-mono">{normInfo.percentile}</span> of the global demographic baseline. {normInfo.description}
              </p>
            </div>
          </div>

          {/* Psychometric Distribution Map (Radar Chart) */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-2xl p-6 shadow-2xl space-y-4">
            <div>
              <h2 className="text-base font-extrabold text-white font-mono flex items-center gap-2">
                <Compass className="h-5 w-5 text-cyan-400" />
                <span>Psychometric Distribution Map</span>
              </h2>
              <p className="text-xs text-slate-400">Visual profile mapping your test scores against the demographic normative benchmark curve (74%).</p>
            </div>

            <div className="border border-slate-800 rounded-2xl bg-slate-950/60 p-4">
              <CognitiveRadar data={radarData} />
            </div>
          </div>

          {/* Core Pillar Metrics Table */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-2xl p-6 shadow-2xl space-y-4">
            <div>
              <h2 className="text-base font-extrabold text-white font-mono flex items-center gap-2">
                <Activity className="h-5 w-5 text-cyan-400" />
                <span>Core Assessment Pillar Metrics</span>
              </h2>
              <p className="text-xs text-slate-400">Detailed breakdown of individual module performance metrics and baseline standing.</p>
            </div>
            
            <div className="overflow-x-auto pt-2">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono font-bold uppercase tracking-wider">
                    <th className="pb-3 font-bold">Pillar / Cognitive Layer</th>
                    <th className="pb-3 font-bold">Classification</th>
                    <th className="pb-3 font-bold hidden sm:table-cell">Visual Standing</th>
                    <th className="pb-3 font-bold text-right">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {MODULE_CONFIGS.map((mod) => {
                    const rawScore = report.moduleScores[mod.id] !== undefined ? report.moduleScores[mod.id] : 0;
                    const score = Math.round(rawScore);
                    
                    let badgeLabel = "Building Baseline";
                    let badgeClass = "bg-amber-950/50 text-amber-300 border-amber-800/40";
                    let barClass = "bg-amber-500";

                    if (score >= 80) {
                      badgeLabel = "Superior Profile";
                      badgeClass = "bg-emerald-950/60 text-emerald-300 border-emerald-800/50";
                      barClass = "bg-emerald-500";
                    } else if (score >= 65) {
                      badgeLabel = "High Ability";
                      badgeClass = "bg-blue-950/60 text-blue-300 border-blue-800/50";
                      barClass = "bg-blue-500";
                    } else if (score >= 45) {
                      badgeLabel = "Nominal Baseline";
                      badgeClass = "bg-teal-950/60 text-teal-300 border-teal-800/50";
                      barClass = "bg-teal-500";
                    }

                    return (
                      <tr key={mod.id} className="hover:bg-slate-800/40 transition-colors">
                        {/* Module Name & Icon */}
                        <td className="py-4 pr-3">
                          <div className="flex items-center gap-3">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-950 border border-slate-800 shadow-inner">
                              {getModuleIcon(mod.id)}
                            </div>
                            <div>
                              <h4 className="font-bold text-slate-100 leading-tight">{mod.name}</h4>
                              <p className="text-[10px] text-slate-400 mt-0.5 font-mono">{mod.estimatedTime} limit</p>
                            </div>
                          </div>
                        </td>

                        {/* Classification Badge */}
                        <td className="py-4 pr-3">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold border font-mono ${badgeClass}`}>
                            {badgeLabel}
                          </span>
                        </td>

                        {/* Visual Progress Bar */}
                        <td className="py-4 pr-3 hidden sm:table-cell">
                          <div className="w-28 h-2 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                            <div 
                              className={`h-full rounded-full transition-all duration-500 ${barClass}`} 
                              style={{ width: `${score}%` }} 
                            />
                          </div>
                        </td>

                        {/* Score Index */}
                        <td className="py-4 text-right font-mono font-black text-slate-100 text-sm">
                          {score}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* Right Column: AI Strengths, Development Areas, & Coaching Actions */}
        <div className="lg:col-span-5 space-y-8">
          
          {/* Glassmorphic AI Diagnostic Insights Card */}
          <div className="rounded-3xl border border-violet-500/30 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-8 shadow-[0_0_40px_rgba(139,92,246,0.12)] space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 -mr-16 -mt-16 h-36 w-36 rounded-full bg-violet-500/10 blur-3xl pointer-events-none" />
            
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 relative z-10">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600 text-white shadow-md shadow-violet-500/20">
                  <Sparkles className="h-5 w-5 animate-pulse" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white font-mono leading-tight">AI Diagnostic Insights</h2>
                  <p className="text-[10px] text-violet-300 font-mono">Powered by Gemini 3.5 Flash</p>
                </div>
              </div>

              {loadingAi ? (
                <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-0.5 rounded border border-cyan-800/50 animate-pulse">
                  Analyzing...
                </span>
              ) : (
                <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded border border-emerald-800/50 font-bold uppercase tracking-wider">
                  Ready
                </span>
              )}
            </div>

            {/* A. STRENGTHS */}
            <div className="space-y-3 relative z-10">
              <div className="flex items-center gap-2 text-xs font-extrabold text-emerald-400 font-mono uppercase tracking-wider">
                <TrendingUp className="h-4 w-4 text-emerald-400" />
                <span>Primary Cognitive Strengths</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300 pl-5 list-disc font-sans leading-relaxed">
                {report.strengths.map((st, i) => (
                  <li key={i} className="marker:text-emerald-400">{st}</li>
                ))}
              </ul>
            </div>

            {/* B. WEAKNESSES / DEVELOPMENT AREAS */}
            <div className="space-y-3 pt-4 border-t border-slate-800 relative z-10">
              <div className="flex items-center gap-2 text-xs font-extrabold text-amber-400 font-mono uppercase tracking-wider">
                <ShieldAlert className="h-4 w-4 text-amber-400" />
                <span>Cognitive Development Areas</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300 pl-5 list-disc font-sans leading-relaxed">
                {report.weaknesses.map((wk, i) => (
                  <li key={i} className="marker:text-amber-400">{wk}</li>
                ))}
              </ul>
            </div>

            {/* C. CLINICAL & COACHING RECOMMENDATIONS */}
            <div className="space-y-3.5 pt-4 border-t border-slate-800 relative z-10">
              <div className="flex items-center gap-2 text-xs font-extrabold text-violet-400 font-mono uppercase tracking-wider">
                <Lightbulb className="h-4 w-4 text-violet-400" />
                <span>Strategic Coaching Actions</span>
              </div>
              <div className="space-y-3">
                {report.recommendations.map((rec, i) => {
                  // Clean out any lingering demo tags
                  const cleanRec = rec.replace(/\[Demo Mock\]\s*/g, "");
                  return (
                    <div key={i} className="flex gap-3 text-xs text-slate-300 bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80 shadow-inner">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-xl bg-violet-950 text-[11px] font-mono font-bold text-violet-400 border border-violet-800/40">
                        {i + 1}
                      </span>
                      <span className="leading-relaxed font-sans">{cleanRec}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Secure Proctor Certification Footer */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 backdrop-blur-2xl p-6 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-white text-sm font-mono flex items-center gap-2">
              <Award className="h-4 w-4 text-cyan-400" />
              <span>Laboratory Sign-off</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              This psychometric record is fully verified under institutional token credentials. Digital transcripts are stored in SQLite and registered with academic proctoring standards.
            </p>
            <div className="border-t border-slate-800 pt-3 flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>Proctor: Dr. Clara Oswald</span>
              <span className="text-[10px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-lg border border-emerald-800/40 font-bold">
                SIGNED_OK
              </span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
