import React from "react";
import { AlertTriangle, X } from "lucide-react";

interface QuizExitWarningModalProps {
  onStay: () => void;
  onLeave: () => void;
}

export default function QuizExitWarningModal({ onStay, onLeave }: QuizExitWarningModalProps) {
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl shadow-slate-900/20 overflow-hidden">
        {/* Header */}
        <div className="flex items-start gap-4 p-6 pb-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-950/60">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Leave Assessment?</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
              Your progress will be lost. This attempt will be marked{" "}
              <span className="font-semibold text-amber-600 dark:text-amber-400">incomplete</span>.
            </p>
          </div>
        </div>

        {/* Warning note */}
        <div className="mx-6 mb-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/30 p-3">
          <p className="text-xs text-rose-700 dark:text-rose-400 font-medium leading-relaxed">
            ⚠️ All answers recorded so far in this session will not be saved. Your cognitive report cannot be generated for an incomplete attempt.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 p-6 pt-2">
          <button
            onClick={onStay}
            className="flex-1 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700 shadow-sm shadow-blue-600/20"
          >
            Stay & Continue
          </button>
          <button
            onClick={onLeave}
            className="flex-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 transition-all hover:bg-rose-50 dark:hover:bg-rose-950/30 hover:text-rose-700 dark:hover:text-rose-400 hover:border-rose-200 dark:hover:border-rose-900/50"
          >
            Leave Anyway
          </button>
        </div>
      </div>
    </div>
  );
}
