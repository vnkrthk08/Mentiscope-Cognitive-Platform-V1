import React, { useEffect, useMemo, useRef, useState } from "react";
import { Eye, RotateCw } from "lucide-react";
import { GVItem, GVOption, GVResponseState } from "./types";

interface RendererProps {
  item: GVItem;
  disabled: boolean;
  onChange: (state: GVResponseState) => void;
  onBehavior: (type: "option_selected" | "piece_selected" | "piece_rotated" | "piece_placed", response: Record<string, unknown>) => void;
}

type Point = [number, number];
type Segment = [Point, Point];

function ShapeGraphic({ data, label }: { data: Record<string, unknown>; label?: string }) {
  const shape = (data.shape || data) as { cells?: number[][]; color?: string };
  const cells = shape.cells || [];
  const rotation = Number(data.rotation || 0);
  const mirror = Boolean(data.mirror);
  const size = 26;
  const maxX = Math.max(0, ...cells.map((cell) => Number(cell[0]))) + 1;
  const maxY = Math.max(0, ...cells.map((cell) => Number(cell[1]))) + 1;
  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox={`0 0 ${Math.max(maxX, maxY) * size + 12} ${Math.max(maxX, maxY) * size + 12}`} className="h-28 w-28" role="img" aria-label={label || "Geometric figure"}>
        <g transform={`translate(${(maxX * size + 12) / 2} ${(maxY * size + 12) / 2}) rotate(${rotation}) scale(${mirror ? -1 : 1} 1) translate(${-(maxX * size) / 2} ${-(maxY * size) / 2})`}>
          {cells.map((cell, index) => (
            <rect key={`${cell[0]}-${cell[1]}-${index}`} x={Number(cell[0]) * size + 1} y={Number(cell[1]) * size + 1} width={size - 2} height={size - 2} rx="4" fill={shape.color || "#0d9488"} stroke="#0f172a" strokeWidth="1.5" />
          ))}
        </g>
      </svg>
    </div>
  );
}

function HoleGrid({ holes, label }: { holes: number[][]; label: string }) {
  return (
    <div className="grid h-28 w-28 grid-cols-4 overflow-hidden rounded-lg border-2 border-slate-300 bg-white" role="img" aria-label={label}>
      {Array.from({ length: 16 }).map((_, index) => {
        const row = Math.floor(index / 4);
        const col = index % 4;
        const punched = holes.some(([x, y]) => x === col && y === row);
        return (
          <div key={index} className="relative border border-slate-200">
            {punched && <span className="absolute left-1/2 top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-slate-800" />}
          </div>
        );
      })}
    </div>
  );
}

function SegmentGraphic({ segments, label }: { segments: Segment[]; label: string }) {
  return (
    <svg viewBox="0 0 100 100" className="h-28 w-full max-w-40" role="img" aria-label={label}>
      {segments.map((segment, index) => (
        <line key={index} x1={segment[0][0]} y1={segment[0][1]} x2={segment[1][0]} y2={segment[1][1]} stroke="#0f766e" strokeWidth="3" strokeLinecap="round" />
      ))}
    </svg>
  );
}

const CELL_CLASS: Record<string, string> = {
  grass: "bg-emerald-100",
  road: "bg-stone-300",
  water: "bg-sky-200",
  building: "bg-orange-200",
  park: "bg-lime-200",
  sand: "bg-amber-100",
};

function MapGrid({ map, label }: { map: string[][]; label: string }) {
  const columns = map[0]?.length || 1;
  return (
    <div className="grid aspect-square w-full max-w-md overflow-hidden rounded-2xl border-4 border-white shadow-lg ring-1 ring-slate-200" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }} role="img" aria-label={label}>
      {map.flatMap((row, rowIndex) => row.map((cell, colIndex) => (
        <div key={`${rowIndex}-${colIndex}`} className={`relative aspect-square border border-white/60 ${CELL_CLASS[cell] || "bg-slate-100"}`}>
          {cell === "road" && <span className="absolute inset-y-0 left-1/2 w-1 -translate-x-1/2 bg-white/70" />}
          {cell === "water" && <span className="absolute inset-x-1 top-1/2 h-0.5 bg-white/70" />}
          {cell === "building" && <span className="absolute left-1/2 top-1/2 h-1/2 w-1/2 -translate-x-1/2 -translate-y-1/2 rounded-sm bg-orange-500/70" />}
          {cell === "park" && <span className="absolute left-1/2 top-1/2 h-2/5 w-2/5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-600/60" />}
        </div>
      )))}
    </div>
  );
}

function rotateMatrix<T>(matrix: T[][], degrees: number): T[][] {
  let output = matrix.map((row) => [...row]);
  const turns = ((degrees % 360) + 360) % 360 / 90;
  for (let turn = 0; turn < turns; turn += 1) {
    output = output[0].map((_, column) => output.map((row) => row[column]).reverse());
  }
  return output;
}

function PiecePreview({ piece, rotation }: { piece: Record<string, unknown>; rotation: number }) {
  const cells = rotateMatrix((piece.cells || []) as string[][], rotation);
  return <MapGrid map={cells} label={`Map piece rotated ${rotation} degrees`} />;
}

function SingleChoiceRenderer({ item, disabled, onChange, onBehavior }: RendererProps) {
  const [selected, setSelected] = useState<string>("");
  const firstInteraction = useRef<number | null>(null);
  const renderedAt = useRef(Date.now());
  const changes = useRef(0);

  useEffect(() => {
    setSelected("");
    firstInteraction.current = null;
    renderedAt.current = Date.now();
    changes.current = 0;
    onChange({ response: null, selectionChanges: 0, rotationAttempts: 0, placementAttempts: 0, timeToFirstInteractionMs: null });
  }, [item.item_id || item.id]);

  const choose = (option: GVOption) => {
    if (disabled) return;
    if (firstInteraction.current === null) firstInteraction.current = Math.max(0, Date.now() - renderedAt.current);
    if (selected && selected !== option.option_id) changes.current += 1;
    setSelected(option.option_id);
    onBehavior("option_selected", { option_id: option.option_id });
    onChange({
      response: { selected_option_id: option.option_id },
      selectionChanges: changes.current,
      rotationAttempts: 0,
      placementAttempts: 0,
      timeToFirstInteractionMs: firstInteraction.current,
    });
  };

  const stimulus = item.stimulus;
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-teal-100 bg-teal-50/50 p-5">
        {item.subtest_id === "mental_rotation" && <ShapeGraphic data={stimulus} label="Target geometric figure" />}
        {item.subtest_id === "paper_folding" && (
          <div className="flex flex-col items-center gap-4 text-center">
            <HoleGrid holes={(stimulus.punched || []) as number[][]} label="Punch location on folded paper" />
            <div className="flex flex-wrap justify-center gap-2 text-xs font-semibold text-teal-800">
              {((stimulus.folds || []) as Array<Record<string, unknown>>).map((fold, index) => (
                <span key={index} className="rounded-full border border-teal-200 bg-white px-3 py-1">Fold {index + 1}: {String(fold.axis)} → {String(fold.direction)}</span>
              ))}
            </div>
          </div>
        )}
        {item.subtest_id === "hidden_figures" && <SegmentGraphic segments={(stimulus.target_segments || []) as Segment[]} label="Target figure to locate" />}
      </div>

      <fieldset disabled={disabled}>
        <legend className="sr-only">Answer options</legend>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {item.options.map((option, index) => {
            const active = selected === option.option_id;
            return (
              <button
                key={option.option_id}
                type="button"
                aria-pressed={active}
                aria-label={`Option ${index + 1}`}
                onClick={() => choose(option)}
                className={`min-h-40 rounded-2xl border-2 p-4 transition focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300 ${active ? "border-teal-600 bg-teal-50 shadow-md" : "border-slate-200 bg-white hover:border-teal-300 hover:shadow-sm"}`}
              >
                <span className="mb-2 block text-left text-xs font-bold uppercase tracking-wider text-slate-500">Option {index + 1}</span>
                {item.subtest_id === "mental_rotation" && <ShapeGraphic data={option.payload} label={`Option ${index + 1} geometric figure`} />}
                {item.subtest_id === "paper_folding" && <div className="flex justify-center"><HoleGrid holes={(option.payload.holes || []) as number[][]} label={`Option ${index + 1} hole pattern`} /></div>}
                {item.subtest_id === "hidden_figures" && <SegmentGraphic segments={(option.payload.segments || []) as Segment[]} label={`Option ${index + 1} complex figure`} />}
              </button>
            );
          })}
        </div>
      </fieldset>
    </div>
  );
}

interface Placement {
  pieceId: string;
  slotIndex: number;
  rotation: number;
}

function MapPlacementRenderer({ item, disabled, onChange, onBehavior }: RendererProps) {
  const map = (item.stimulus?.map || []) as string[][];
  const pieces = (item.stimulus?.pieces || []) as Array<Record<string, unknown>>;
  const cols = Number(item.stimulus?.cols || 2);
  const rows = Number(item.stimulus?.rows || 2);
  const studySeconds = Number(item.stimulus?.study_seconds || 5);
  const [studyLeft, setStudyLeft] = useState(studySeconds);
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);
  const [rotations, setRotations] = useState<Record<string, number>>({});
  const [placements, setPlacements] = useState<Record<number, Placement>>({});
  const firstInteraction = useRef<number | null>(null);
  const renderedAt = useRef(Date.now());
  const selectionChanges = useRef(0);
  const rotationAttempts = useRef(0);
  const placementAttempts = useRef(0);

  useEffect(() => {
    const initial = Object.fromEntries((pieces || []).map((piece) => [String(piece.piece_id), Number(piece.initial_rotation || 0)]));
    setStudyLeft(studySeconds);
    setSelectedPieceId(null);
    setRotations(initial);
    setPlacements({});
    firstInteraction.current = null;
    renderedAt.current = Date.now();
    selectionChanges.current = 0;
    rotationAttempts.current = 0;
    placementAttempts.current = 0;
    onChange({ response: null, selectionChanges: 0, rotationAttempts: 0, placementAttempts: 0, timeToFirstInteractionMs: null });
  }, [item.item_id || item.id]);

  useEffect(() => {
    if (studyLeft <= 0) return;
    const timer = window.setTimeout(() => setStudyLeft((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [studyLeft]);

  const pieceById = useMemo(() => Object.fromEntries(pieces.map((piece) => [String(piece.piece_id), piece])), [pieces]);
  const placedPieceIds = new Set(Object.values(placements).map((placement) => placement.pieceId));

  const publish = (nextPlacements: Record<number, Placement>, nextRotations = rotations) => {
    const complete = Object.keys(nextPlacements).length === pieces.length;
    const responsePlacements = Object.fromEntries(
      Object.values(nextPlacements).map((placement) => [placement.pieceId, { slot_index: placement.slotIndex, rotation: nextRotations[placement.pieceId] || 0 }]),
    );
    onChange({
      response: complete ? { placements: responsePlacements } : null,
      selectionChanges: selectionChanges.current,
      rotationAttempts: rotationAttempts.current,
      placementAttempts: placementAttempts.current,
      timeToFirstInteractionMs: firstInteraction.current,
    });
  };

  const markFirst = () => {
    if (firstInteraction.current === null) firstInteraction.current = Math.max(0, Date.now() - renderedAt.current);
  };

  const selectPiece = (pieceId: string) => {
    if (disabled || studyLeft > 0) return;
    markFirst();
    if (selectedPieceId && selectedPieceId !== pieceId) selectionChanges.current += 1;
    setSelectedPieceId(pieceId);
    onBehavior("piece_selected", { piece_id: pieceId });
  };

  const rotatePiece = (pieceId: string) => {
    if (disabled || studyLeft > 0) return;
    markFirst();
    rotationAttempts.current += 1;
    const next = { ...rotations, [pieceId]: ((rotations[pieceId] || 0) + 90) % 360 };
    setRotations(next);
    const slot = Object.values(placements).find((placement) => placement.pieceId === pieceId);
    const nextPlacements = slot ? { ...placements, [slot.slotIndex]: { ...slot, rotation: next[pieceId] } } : placements;
    if (slot) setPlacements(nextPlacements);
    onBehavior("piece_rotated", { piece_id: pieceId, rotation: next[pieceId] });
    publish(nextPlacements, next);
  };

  const placeSelected = (slotIndex: number) => {
    if (disabled || studyLeft > 0 || !selectedPieceId) return;
    markFirst();
    placementAttempts.current += 1;
    const next = { ...placements };
    for (const [key, placement] of Object.entries(next)) {
      if (placement.pieceId === selectedPieceId) delete next[Number(key)];
    }
    const displaced = next[slotIndex]?.pieceId;
    next[slotIndex] = { pieceId: selectedPieceId, slotIndex, rotation: rotations[selectedPieceId] || 0 };
    setPlacements(next);
    setSelectedPieceId(displaced || null);
    onBehavior("piece_placed", { piece_id: selectedPieceId, slot_index: slotIndex, rotation: rotations[selectedPieceId] || 0 });
    publish(next);
  };

  if (studyLeft > 0) {
    return (
      <div className="flex flex-col items-center gap-6 rounded-3xl border border-teal-100 bg-teal-50/40 p-6 sm:p-8" aria-live="polite">
        <div className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-bold text-teal-700 shadow-sm"><Eye className="h-4 w-4" /> Study the complete map: {studyLeft}s</div>
        <MapGrid map={map} label="Complete map to remember" />
        <p className="max-w-xl text-center text-sm text-slate-600">Notice roads, water, landmarks, and the position of each region. The reference will hide before placement begins.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <div>
        <h3 className="mb-3 text-sm font-bold text-slate-700">Reconstruction board</h3>
        <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }} aria-label="Map reconstruction slots">
          {Array.from({ length: cols * rows }).map((_, slotIndex) => {
            const placement = placements[slotIndex];
            return (
              <button
                key={slotIndex}
                type="button"
                disabled={disabled}
                onClick={() => placeSelected(slotIndex)}
                aria-label={`Slot ${slotIndex + 1}${placement ? ` containing ${placement.pieceId}` : " empty"}`}
                className={`aspect-square min-h-24 rounded-2xl border-2 border-dashed p-2 transition focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300 ${placement ? "border-teal-500 bg-white" : selectedPieceId ? "border-teal-300 bg-teal-50 hover:border-teal-500" : "border-slate-300 bg-slate-50"}`}
              >
                {placement ? <PiecePreview piece={pieceById[placement.pieceId]} rotation={rotations[placement.pieceId] || 0} /> : <span className="text-xs font-bold text-slate-400">Slot {slotIndex + 1}</span>}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-bold text-slate-700">Piece tray</h3>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-1">
          {pieces.map((piece, index) => {
            const pieceId = String(piece.piece_id);
            const active = selectedPieceId === pieceId;
            const placed = placedPieceIds.has(pieceId);
            return (
              <div key={pieceId} className={`rounded-2xl border p-3 ${active ? "border-teal-500 bg-teal-50" : "border-slate-200 bg-white"}`}>
                <button type="button" disabled={disabled} onClick={() => selectPiece(pieceId)} aria-pressed={active} className="w-full rounded-xl focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300">
                  <span className="mb-2 block text-left text-[11px] font-bold uppercase tracking-wider text-slate-500">Piece {index + 1}{placed ? " · placed" : ""}</span>
                  <PiecePreview piece={piece} rotation={rotations[pieceId] || 0} />
                </button>
                <button type="button" disabled={disabled} onClick={() => rotatePiece(pieceId)} className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-300" aria-label={`Rotate piece ${index + 1} clockwise`}>
                  <RotateCw className="h-4 w-4" /> Rotate 90°
                </button>
              </div>
            );
          })}
        </div>
        <p className="mt-4 text-xs leading-relaxed text-slate-500">Accessible placement: select a piece, rotate it using the button, then choose a numbered slot. Selecting a placed piece lets you move it.</p>
      </div>
    </div>
  );
}

export default function GVItemRenderer(props: RendererProps) {
  if (!props.item || !props.item.stimulus) return null;
  return props.item.response_type === "map_placement" ? <MapPlacementRenderer {...props} /> : <SingleChoiceRenderer {...props} />;
}
