import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Brain,
  CheckCircle2,
  Clock3,
  Eye,
  Loader2,
  Map,
  RefreshCw,
  RotateCw,
  ScanSearch,
  ShieldCheck,
  Shapes,
} from "lucide-react";
import { GVService, GVApiError } from "../../services/modules/gv";
import { createGVEvent } from "./events";
import GVItemRenderer from "./GVItemRenderer";
import { clearGVProgress, loadGVProgress, saveGVProgress } from "./storage";
import {
  AssessmentLaunchContext,
  GVClientEvent,
  GVFinalResult,
  GVItem,
  GVResponseState,
  GVStartResponse,
} from "./types";

interface Props {
  context: AssessmentLaunchContext;
  onCompleted: (result: GVFinalResult) => void;
  onExit: () => void;
}

type Phase = "loading" | "instructions" | "practice" | "assessment" | "finishing" | "result" | "error";

const EMPTY_RESPONSE: GVResponseState = {
  response: null,
  selectionChanges: 0,
  rotationAttempts: 0,
  placementAttempts: 0,
  timeToFirstInteractionMs: null,
};

const SUBTEST_DETAILS = [
  { id: "mental_rotation", name: "Mental Rotation", ability: "Spatial Relations (SR)", icon: RotateCw, summary: "Recognise an object after orientation changes while rejecting mirror images." },
  { id: "paper_folding", name: "Paper Folding", ability: "Visualization (Vz)", icon: Shapes, summary: "Mentally unfold a punched sheet and predict the resulting spatial pattern." },
  { id: "hidden_figures", name: "Hidden Figures", ability: "Flexibility of Closure (CF)", icon: ScanSearch, summary: "Locate a simple target embedded within visually complex information." },
  { id: "mystery_map", name: "Mystery Map Builder", ability: "CS · CF · SR · Vz · SS", icon: Map, summary: "Study, rotate, and place map regions using visual closure and spatial scanning." },
];

function errorMessage(error: unknown): string {
  if (error instanceof GVApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "An unexpected error interrupted the Visual Processing assessment.";
}

function safePercent(value: number | null): string {
  return value === null ? "Not administered" : `${Math.round(value)}%`;
}

export default function GVAssessmentModule({ context, onCompleted, onExit }: Props) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [startData, setStartData] = useState<GVStartResponse | null>(null);
  const [practiceIndex, setPracticeIndex] = useState(0);
  const [assessmentIndex, setAssessmentIndex] = useState(0);
  const [responseState, setResponseState] = useState<GVResponseState>(EMPTY_RESPONSE);
  const [practiceFeedback, setPracticeFeedback] = useState<{ correct: boolean; message: string } | null>(null);
  const [result, setResult] = useState<GVFinalResult | null>(null);
  const [error, setError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [retryable, setRetryable] = useState(true);
  const sessionStartedAt = useRef(Date.now());
  const itemStartedAt = useRef(Date.now());
  const events = useRef<GVClientEvent[]>([]);
  const finishing = useRef(false);
  const mounted = useRef(true);

  const currentItem: GVItem | null = useMemo(() => {
    if (!startData) return null;
    if (phase === "practice") return startData.practice_items[practiceIndex] || null;
    if (phase === "assessment") return startData.assessment_items[assessmentIndex] || null;
    return null;
  }, [startData, phase, practiceIndex, assessmentIndex]);

  const addEvent = useCallback((event: GVClientEvent) => {
    events.current.push(event);
  }, []);

  const emit = useCallback((type: Parameters<typeof createGVEvent>[2], item?: GVItem | null, response: Record<string, unknown> = {}) => {
    addEvent(createGVEvent(context, sessionStartedAt.current, type, { item, response }));
  }, [addEvent, context]);

  const startAssessment = useCallback(async () => {
    setPhase("loading");
    setError("");
    try {
      const data = await GVService.start(context);
      if (!mounted.current) return;
      setStartData(data);
      sessionStartedAt.current = new Date(data.start_time).getTime() || Date.now();
      if (data.status === "completed" && data.completed_result) {
        setResult(data.completed_result);
        clearGVProgress(context.session_id);
        onCompleted(data.completed_result);
        setPhase("result");
        return;
      }
      const saved = loadGVProgress(context.session_id);
      const serverIndex = Math.min(data.current_item_index, data.assessment_items.length);
      if (saved?.phase === "assessment" || serverIndex > 0) {
        setPracticeIndex(data.practice_items.length);
        setAssessmentIndex(Math.max(saved?.assessmentIndex || 0, serverIndex));
        setPhase(serverIndex >= data.assessment_items.length ? "finishing" : "assessment");
      } else if (saved?.phase === "practice") {
        setPracticeIndex(Math.min(saved.practiceIndex, data.practice_items.length - 1));
        setPhase("practice");
      } else {
        setPhase("instructions");
      }
      if (data.status === "new") emit("session_started", null, { difficulty: data.difficulty });
    } catch (caught) {
      if (!mounted.current) return;
      const apiError = caught instanceof GVApiError ? caught : null;
      setRetryable(apiError?.retryable ?? true);
      setError(errorMessage(caught));
      setPhase("error");
    }
  }, [context, emit]);

  useEffect(() => {
    mounted.current = true;
    void startAssessment();
    return () => {
      mounted.current = false;
    };
  }, [startAssessment]);

  useEffect(() => {
    if (!currentItem) return;
    itemStartedAt.current = Date.now();
    setResponseState(EMPTY_RESPONSE);
    setPracticeFeedback(null);
    emit("item_presented", currentItem);
    const items = phase === "practice" ? startData?.practice_items : startData?.assessment_items;
    const index = phase === "practice" ? practiceIndex : assessmentIndex;
    const previous = items && index > 0 ? items[index - 1] : null;
    if (!previous || previous.subtest_id !== currentItem.subtest_id) emit("subtest_started", currentItem);
  }, [currentItem?.item_id, phase]);

  useEffect(() => {
    if (!startData) return;
    if (phase === "instructions" || phase === "practice" || phase === "assessment") {
      saveGVProgress(context.session_id, { phase, practiceIndex, assessmentIndex });
    }
  }, [phase, practiceIndex, assessmentIndex, context.session_id, startData]);

  useEffect(() => {
    if (phase === "finishing" && startData && !finishing.current) void finish();
  }, [phase, startData]);

  const beginPractice = () => {
    emit("instructions_viewed", null);
    emit("practice_started", startData?.practice_items[0] || null);
    setPracticeIndex(0);
    setPhase("practice");
  };

  const handleBehavior = (type: "option_selected" | "piece_selected" | "piece_rotated" | "piece_placed", response: Record<string, unknown>) => {
    if (!currentItem) return;
    emit(type, currentItem, response);
  };

  const submitCurrent = async () => {
    if (!currentItem || !responseState.response || submitting) return;
    setSubmitting(true);
    setError("");
    const elapsed = Math.max(0, Date.now() - itemStartedAt.current);
    emit("answer_submitted", currentItem, { practice: currentItem.practice });
    const bufferedEvents = events.current;
    events.current = [];
    try {
      const acknowledgement = await GVService.answer({
        submission_id: crypto.randomUUID(),
        session_id: context.session_id,
        item_id: currentItem.item_id,
        response: responseState.response,
        practice: currentItem.practice,
        time_taken_ms: elapsed,
        attempt_number: 1,
        selection_changes: responseState.selectionChanges,
        rotation_attempts: responseState.rotationAttempts,
        placement_attempts: responseState.placementAttempts,
        time_to_first_interaction_ms: responseState.timeToFirstInteractionMs,
        device_metadata: {
          viewport_width: window.innerWidth,
          viewport_height: window.innerHeight,
          input_mode: "select-and-place",
          user_agent_family: navigator.userAgent.slice(0, 120),
        },
        events: bufferedEvents,
      }, context.access_token);
      if (!mounted.current) return;
      if (currentItem.practice) {
        setPracticeFeedback(acknowledgement.practice_feedback || { correct: true, message: "Practice response recorded." });
      } else {
        advanceAssessment();
      }
    } catch (caught) {
      events.current = [...bufferedEvents, ...events.current];
      setError(errorMessage(caught));
    } finally {
      if (mounted.current) setSubmitting(false);
    }
  };

  const advancePractice = () => {
    if (!startData || !currentItem) return;
    emit("item_completed", currentItem, { practice: true });
    const isLast = practiceIndex >= startData.practice_items.length - 1;
    const next = startData.practice_items[practiceIndex + 1];
    if (!next || next.subtest_id !== currentItem.subtest_id) emit("subtest_completed", currentItem, { practice: true });
    if (isLast) {
      emit("practice_completed", currentItem);
      setAssessmentIndex(Math.max(0, startData.current_item_index));
      setPhase("assessment");
    } else {
      setPracticeIndex((value) => value + 1);
    }
  };

  const advanceAssessment = () => {
    if (!startData || !currentItem) return;
    emit("item_completed", currentItem);
    const isLast = assessmentIndex >= startData.assessment_items.length - 1;
    const next = startData.assessment_items[assessmentIndex + 1];
    if (!next || next.subtest_id !== currentItem.subtest_id) emit("subtest_completed", currentItem);
    if (isLast) {
      setPhase("finishing");
    } else {
      setAssessmentIndex((value) => value + 1);
    }
  };

  const finish = async () => {
    if (finishing.current) return;
    finishing.current = true;
    setPhase("finishing");
    setError("");
    emit("assessment_finished", currentItem);
    const bufferedEvents = events.current;
    events.current = [];
    try {
      const finalResult = await GVService.finish(context.session_id, bufferedEvents, context.access_token);
      if (!mounted.current) return;
      setResult(finalResult);
      clearGVProgress(context.session_id);
      setPhase("result");
      onCompleted(finalResult);
    } catch (caught) {
      events.current = [...bufferedEvents, ...events.current];
      setError(errorMessage(caught));
      setPhase("assessment");
      if (startData) setAssessmentIndex(Math.max(0, startData.assessment_items.length - 1));
    } finally {
      finishing.current = false;
    }
  };

  if (phase === "loading") {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4 px-6 text-center">
        <Loader2 className="h-10 w-10 animate-spin text-teal-600" />
        <div><h2 className="text-lg font-bold text-slate-900">Preparing Visual Processing Battery</h2><p className="mt-1 text-sm text-slate-500">Validating platform session and retrieving safe assessment items…</p></div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="mx-auto flex min-h-[65vh] max-w-xl flex-col items-center justify-center px-6 text-center">
        <div className="rounded-3xl border border-amber-200 bg-white p-8 shadow-sm">
          <AlertTriangle className="mx-auto h-10 w-10 text-amber-600" />
          <h2 className="mt-4 text-xl font-extrabold text-slate-900">Unable to open the assessment</h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">{error}</p>
          <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
            {retryable && <button type="button" onClick={() => void startAssessment()} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-5 py-3 text-sm font-bold text-white hover:bg-teal-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300"><RefreshCw className="h-4 w-4" /> Retry safely</button>}
            <button type="button" onClick={onExit} className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-300">Return to dashboard</button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === "instructions") {
    return (
      <div className="mx-auto max-w-6xl space-y-7 px-4 py-8 sm:px-6 lg:px-8">
        {GVService.isMockMode() && <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-900">Demo mode is active. Responses and result values are illustrative and are not official assessment scores.</div>}
        <section className="overflow-hidden rounded-3xl border border-teal-100 bg-white shadow-sm">
          <div className="bg-gradient-to-br from-teal-700 to-cyan-700 px-6 py-8 text-white sm:px-10 sm:py-12">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div className="max-w-3xl"><span className="rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em]">CHC Visual Processing · Gv</span><h1 className="mt-5 text-3xl font-black tracking-tight sm:text-5xl">Visual Processing Battery</h1><p className="mt-4 max-w-2xl text-sm leading-7 text-teal-50 sm:text-base">A structured visual-spatial assessment covering rotation, transformation, closure, scanning, and map reconstruction. Accuracy is primary; time is recorded only as a secondary process indicator.</p></div>
              <div className="grid grid-cols-2 gap-3 text-center text-xs font-bold"><div className="rounded-2xl border border-white/20 bg-white/10 p-4"><Brain className="mx-auto mb-2 h-6 w-6" />4 subtests</div><div className="rounded-2xl border border-white/20 bg-white/10 p-4"><Clock3 className="mx-auto mb-2 h-6 w-6" />~12 minutes</div><div className="rounded-2xl border border-white/20 bg-white/10 p-4"><ShieldCheck className="mx-auto mb-2 h-6 w-6" />Server scored</div><div className="rounded-2xl border border-white/20 bg-white/10 p-4"><Eye className="mx-auto mb-2 h-6 w-6" />No live results</div></div>
            </div>
          </div>
          <div className="grid gap-4 p-6 sm:grid-cols-2 sm:p-10">
            {SUBTEST_DETAILS.map(({ id, name, ability, icon: Icon, summary }) => <article key={id} className="rounded-2xl border border-slate-200 bg-slate-50/60 p-5"><div className="flex items-start gap-4"><span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-teal-100 text-teal-700"><Icon className="h-5 w-5" /></span><div><h2 className="font-extrabold text-slate-900">{name}</h2><p className="mt-0.5 text-xs font-bold uppercase tracking-wider text-teal-700">{ability}</p><p className="mt-2 text-sm leading-relaxed text-slate-600">{summary}</p></div></div></article>)}
          </div>
        </section>
        <section className="grid gap-4 md:grid-cols-3"><div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-bold text-slate-900">Before you begin</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">Use a stable screen, reduce distractions, and complete the practice examples first. The module does not collect additional personal details.</p></div><div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-bold text-slate-900">During scored items</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">Correctness is intentionally not shown. You may revise a selection before submitting, but each scored item is submitted once.</p></div><div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-bold text-slate-900">Accessible controls</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">All choices are keyboard-focusable. Map tasks support select, rotate, and numbered-slot placement without requiring drag-and-drop.</p></div></section>
        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-between"><button type="button" onClick={onExit} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-300"><ArrowLeft className="h-4 w-4" /> Return to dashboard</button><button type="button" onClick={beginPractice} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-6 py-3 text-sm font-bold text-white shadow-sm hover:bg-teal-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300">Begin guided practice <ArrowRight className="h-4 w-4" /></button></div>
      </div>
    );
  }

  if (phase === "finishing") {
    return <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4 px-6 text-center"><Loader2 className="h-10 w-10 animate-spin text-teal-600" /><div><h2 className="text-xl font-extrabold text-slate-900">Calculating your module metrics</h2><p className="mt-2 max-w-md text-sm leading-relaxed text-slate-500">The backend is validating stored answers, event quality, and server timestamps. Please keep this page open.</p></div></div>;
  }

  if (phase === "result" && result) {
    const metricCards = [
      ["Visualization (Vz)", result.metrics.visualization_vz], ["Spatial Relations (SR)", result.metrics.spatial_relations_sr], ["Visual Closure (CS)", result.metrics.visual_closure_cs], ["Flexibility of Closure (CF)", result.metrics.flexibility_of_closure_cf], ["Spatial Scanning (SS)", result.metrics.spatial_scanning_ss], ["Visual Memory (MV)", result.metrics.visual_memory_mv],
    ] as const;
    return (
      <div className="mx-auto max-w-6xl space-y-7 px-4 py-8 sm:px-6 lg:px-8">
        {GVService.isMockMode() && <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-900">Demonstration result only. API mode is required for official backend scoring.</div>}
        <section className="rounded-3xl border border-teal-100 bg-white p-6 shadow-sm sm:p-10"><div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"><div><div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700"><CheckCircle2 className="h-7 w-7" /></div><h1 className="mt-5 text-3xl font-black tracking-tight text-slate-900">Visual Processing Battery completed</h1><p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-600">Your official module metrics were calculated from stored responses by the Gv backend. These pilot-stage results are non-diagnostic and should not be interpreted as standardized norms.</p></div><div className="min-w-52 rounded-3xl bg-gradient-to-br from-teal-700 to-cyan-700 p-6 text-center text-white"><span className="text-xs font-bold uppercase tracking-[0.2em] text-teal-100">Overall Gv score</span><strong className="mt-2 block text-6xl font-black">{Math.round(result.metrics.raw_score)}</strong><span className="text-sm text-teal-100">out of 100</span></div></div></section>
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{metricCards.map(([label, value]) => <article key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-2xl font-black text-slate-900">{safePercent(value)}</p></article>)}</section>
        <section className="grid gap-4 lg:grid-cols-2"><div className="rounded-2xl border border-slate-200 bg-white p-6"><h2 className="font-extrabold text-slate-900">Subtest performance</h2><dl className="mt-4 space-y-3 text-sm">{[["Mental Rotation", result.metrics.mental_rotation_accuracy], ["Paper Folding", result.metrics.paper_folding_accuracy], ["Hidden Figures", result.metrics.hidden_figures_accuracy], ["Mystery Map", result.metrics.mystery_map_accuracy]].map(([label, value]) => <div key={String(label)} className="flex items-center justify-between border-b border-slate-100 pb-3"><dt className="text-slate-600">{label}</dt><dd className="font-extrabold text-teal-700">{safePercent(value as number | null)}</dd></div>)}</dl></div><div className="rounded-2xl border border-slate-200 bg-white p-6"><h2 className="font-extrabold text-slate-900">Result-quality indicators</h2><dl className="mt-4 space-y-3 text-sm"><div className="flex justify-between border-b border-slate-100 pb-3"><dt className="text-slate-600">First-attempt accuracy</dt><dd className="font-bold">{Math.round(result.metrics.first_attempt_accuracy)}%</dd></div><div className="flex justify-between border-b border-slate-100 pb-3"><dt className="text-slate-600">Average response time</dt><dd className="font-bold">{result.metrics.average_response_time.toFixed(1)} s</dd></div><div className="flex justify-between border-b border-slate-100 pb-3"><dt className="text-slate-600">Corrections</dt><dd className="font-bold">{result.metrics.correction_count}</dd></div><div className="flex justify-between"><dt className="text-slate-600">System confidence in result quality</dt><dd className="font-bold">{Math.round(result.metrics.confidence_score)}%</dd></div></dl><p className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">The confidence value describes event completeness, response consistency, coverage, and technical stability. It is not the student’s personal confidence.</p></div></section>
        <div className="flex justify-end"><button type="button" onClick={onExit} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-6 py-3 text-sm font-bold text-white hover:bg-teal-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300">Return to dashboard <ArrowRight className="h-4 w-4" /></button></div>
      </div>
    );
  }

  if (!startData || !currentItem) return null;
  const isPractice = phase === "practice";
  const index = isPractice ? practiceIndex : assessmentIndex;
  const total = isPractice ? startData.practice_items.length : startData.assessment_items.length;
  const progress = Math.round(((index + (isPractice ? 0 : 1)) / Math.max(total, 1)) * 100);

  return (
    <div className="mx-auto max-w-6xl space-y-5 px-4 py-6 sm:px-6 lg:px-8">
      {GVService.isMockMode() && <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-xs font-semibold text-amber-900">Demo mode · illustrative responses only</div>}
      <header className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"><div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><span className="text-[11px] font-bold uppercase tracking-[0.18em] text-teal-700">{isPractice ? "Guided practice" : "Scored assessment"}</span><h1 className="mt-1 text-xl font-black text-slate-900">{currentItem.subtest_name}</h1><p className="mt-1 text-xs text-slate-500">Primary ability: {currentItem.primary_ability} · Difficulty {currentItem.difficulty_level}</p></div><div className="text-sm font-bold text-slate-600">Item {index + 1} of {total}</div></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-teal-600 transition-all" style={{ width: `${progress}%` }} /></div></header>
      <main className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8"><div className="mb-6"><h2 className="text-xl font-extrabold leading-snug text-slate-900 sm:text-2xl">{currentItem.prompt}</h2><p className="mt-2 text-sm leading-relaxed text-slate-500">{isPractice ? "Practice feedback is shown after submission." : "Choose carefully. Correctness is not displayed during scored items."}</p></div><GVItemRenderer item={currentItem} disabled={submitting || Boolean(practiceFeedback)} onChange={setResponseState} onBehavior={handleBehavior} />
        {practiceFeedback && <div aria-live="polite" className={`mt-6 rounded-2xl border p-4 ${practiceFeedback.correct ? "border-emerald-200 bg-emerald-50 text-emerald-900" : "border-amber-200 bg-amber-50 text-amber-900"}`}><p className="font-bold">{practiceFeedback.correct ? "Practice complete" : "Review this example"}</p><p className="mt-1 text-sm">{practiceFeedback.message}</p></div>}
        {error && <div aria-live="assertive" className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-800">{error} Your response has not been advanced; retrying is safe.</div>}
        <div className="mt-7 flex flex-col-reverse gap-3 border-t border-slate-100 pt-5 sm:flex-row sm:items-center sm:justify-between"><button type="button" onClick={() => { emit("navigation_attempted", currentItem, { destination: "dashboard" }); onExit(); }} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-300"><ArrowLeft className="h-4 w-4" /> Save and exit</button>{practiceFeedback ? <button type="button" onClick={advancePractice} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-6 py-3 text-sm font-bold text-white hover:bg-teal-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300">Continue <ArrowRight className="h-4 w-4" /></button> : <button type="button" disabled={!responseState.response || submitting} onClick={() => void submitCurrent()} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-6 py-3 text-sm font-bold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-slate-300 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300">{submitting && <Loader2 className="h-4 w-4 animate-spin" />}{isPractice ? "Check practice" : index === total - 1 ? "Submit final item" : "Submit and continue"}<ArrowRight className="h-4 w-4" /></button>}</div>
      </main>
    </div>
  );
}
