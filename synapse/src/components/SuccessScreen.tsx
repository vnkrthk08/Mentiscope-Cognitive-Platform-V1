import React from 'react';
import { ScreenId } from '../types';
import { Compass, ShieldCheck, ArrowUpRight } from 'lucide-react';
import type { AssessmentResult } from '../services/assessmentApi';

import { useAssessment } from '../context/AssessmentContext';

export const SuccessScreen: React.FC = () => {
  const { handleNavigate: onContinue, logEvent: onLog, backendResult, sessionScores } = useAssessment();
  
  const metrics = backendResult?.metrics;
  const recommendations = backendResult?.recommendations;

  const handleProceedToAnalytics = () => {
    onLog('Proceeded to Cognitive Analytics', 'INFO', 'User clicked main success CTA: CONTINUE TO ANALYTICS');
    onContinue('cognitive-analytics');
  };

  const handleReturnToMap = () => {
    onLog('Returned to Tactical Map', 'INFO', 'User clicked secondary success CTA: RETURN TO MAP');
    onContinue('map');
  };

  return (
    <div className="max-w-2xl mx-auto bg-[#020617] border border-slate-900 rounded-3xl p-6 md:p-10 text-slate-100 font-sans relative overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.8)] flex flex-col justify-between select-none">
      
      {/* High-tech overlay matrix pattern */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle, #22d3ee 1px, transparent 1px),
            linear-gradient(to right, #22d3ee 1px, transparent 1px),
            linear-gradient(to bottom, #22d3ee 1px, transparent 1px)
          `,
          backgroundSize: '24px 24px, 24px 24px, 24px 24px',
        }}
      />

      {/* Atmospheric ambient cosmic glowing nebulae */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl pointer-events-none animate-pulse"></div>

      {/* TOP STATUS BAR (Matching layout from Image 3) */}
      <div className="flex items-center justify-between border-b border-slate-900/60 pb-4 mb-8 font-mono text-[10px] text-slate-500 relative z-10">
        <div className="flex items-center gap-1.5 font-bold tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>MISSION_ID: {backendResult?.assessment_id || 'SYNAPSE_01'}</span>
        </div>
        
        <div className="bg-cyan-950/20 border border-cyan-500/25 px-2.5 py-1 rounded text-cyan-400 font-bold uppercase tracking-widest">
          {metrics ? `${metrics.accuracy?.toFixed(0)}% ACC` : '+450 XP'}
        </div>
      </div>

      {/* HEADER SECTION */}
      <div className="text-center space-y-3 mb-8 relative z-10">
        <span className="inline-block bg-cyan-950/20 border border-cyan-500/20 text-cyan-400 text-[9px] font-mono font-bold tracking-[0.25em] uppercase px-3 py-1 rounded-full shadow-[inset_0_1px_8px_rgba(34,211,238,0.15)]">
          COGNITIVE LEVEL UP DETECTED
        </span>
        <h2 className="text-4xl md:text-5xl font-black tracking-widest text-white font-space uppercase">
          MISSION SUCCESS
        </h2>
      </div>

      {/* CENTRAL GLOWING ALIGNMENT COMPASS GRAPHIC & SIDE STATS */}
      <div className="relative flex items-center justify-center my-10 min-h-[220px] z-10">
        
        {/* Floating Stat Card - Left Side (BOOST +150 XP) */}
        <div className="absolute left-2 md:left-10 bg-[#070b13]/90 border border-slate-850 p-3 rounded-xl flex items-center gap-2.5 shadow-xl font-mono text-left z-20 hover:scale-105 transition-transform duration-300">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/40 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <ArrowUpRight className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[8px] text-slate-500 font-bold uppercase block tracking-wider">REWARD COGNITIVE</span>
            <span className="text-[11px] font-black text-cyan-400 block tracking-wide font-mono">BOOST +150 XP</span>
          </div>
        </div>

        {/* Floating Stat Card - Right Side (INTEGRITY 100% -> LVL {metrics?.highest_level_reached}) */}
        <div className="absolute right-2 md:right-10 bg-[#070b13]/90 border border-slate-850 p-3 rounded-xl flex items-center gap-2.5 shadow-xl font-mono text-left z-20 hover:scale-105 transition-transform duration-300">
          <div className="w-8 h-8 rounded-lg bg-emerald-950/40 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[8px] text-slate-500 font-bold uppercase block tracking-wider">SYSTEM METRICS</span>
            <span className="text-[11px] font-black text-emerald-400 block tracking-wide font-mono font-bold">LVL {metrics?.highest_level_reached || 1}</span>
          </div>
        </div>

        {/* Central Complex Graphic structure (Rotated Concentric Squares and Glowing Neon Hexagon) */}
        <div className="relative w-44 h-44 flex items-center justify-center">
          {/* Rotated Square Grid Frames */}
          <div className="absolute inset-0 border border-slate-900 rounded-lg transform rotate-45 pointer-events-none scale-110"></div>
          <div className="absolute inset-0 border border-cyan-500/10 rounded-lg transform rotate-12 pointer-events-none scale-105"></div>
          <div className="absolute inset-0 border border-violet-500/15 rounded-lg transform -rotate-12 pointer-events-none scale-105"></div>
          
          {/* Inner Glowing Hexagon Frame */}
          <div 
            className="absolute w-32 h-32 bg-[#050914] border-2 border-cyan-500/40 rounded-[2rem] flex items-center justify-center shadow-[0_0_35px_rgba(34,211,238,0.25)]"
            style={{
              clipPath: 'polygon(50% 0%, 93% 25%, 93% 75%, 50% 100%, 7% 75%, 7% 25%)',
            }}
          >
            {/* Ambient Radial center shine */}
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-transparent to-violet-500/15"></div>
            
            {/* Technical architect compass inside representing the "Pattern Architect" title */}
            <Compass className="w-14 h-14 text-cyan-400 relative z-10 animate-pulse" strokeWidth={1.5} />
          </div>

          {/* Decorative outer ticks */}
          <div className="absolute inset-x-0 top-1/2 h-[1px] bg-cyan-400/20 pointer-events-none"></div>
          <div className="absolute inset-y-0 left-1/2 w-[1px] bg-cyan-400/20 pointer-events-none"></div>
        </div>
      </div>

      {/* UNLOCKED MILESTONE DESCRIPTION DETAILS */}
      <div className="text-center space-y-2 mb-10 relative z-10 font-mono">
        <span className="text-[9px] text-slate-500 tracking-[0.2em] font-bold uppercase block">
          NEW TITLE UNLOCKED
        </span>
        <h3 className="text-2xl md:text-3xl font-black text-white tracking-wide uppercase select-none">
          {metrics ? `Confidence ${metrics.confidence_index?.toFixed(0)}%` : 'The Pattern Architect'}
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed max-w-lg mx-auto font-sans pt-2">
          {backendResult
            ? `Assessment completed successfully. Accuracy: ${metrics?.accuracy}%. Questions: ${metrics?.questions_attempted}. Average Response Time: ${metrics?.average_reaction_time} ms. Highest Difficulty: ${metrics?.highest_level_reached}.`
            : 'Assessment completed.'}
        </p>

        {backendResult && (
          <div className="grid grid-cols-2 gap-4 mt-8 text-left">
            {sessionScores && (
              <div className="col-span-2 bg-slate-900 rounded-xl p-4 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.1)] flex justify-between items-center">
                <span className="text-[10px] text-emerald-500 uppercase font-bold">Overall GQ Score</span>
                <span className="text-2xl font-black text-emerald-400">{sessionScores.normalizedScore}</span>
              </div>
            )}
            <div className="bg-slate-900 rounded-xl p-4 flex flex-col justify-between">
              <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Accuracy</span>
              <span className="text-lg font-bold text-cyan-400">{metrics?.accuracy || 0}%</span>
            </div>
            <div className="bg-slate-900 rounded-xl p-4 flex flex-col justify-between">
              <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Reaction</span>
              <span className="text-lg font-bold text-cyan-400">{metrics?.average_reaction_time || 0} ms</span>
            </div>
            <div className="bg-slate-900 rounded-xl p-4 flex flex-col justify-between">
              <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Confidence</span>
              <span className="text-lg font-bold text-cyan-400">{metrics?.confidence_index}%</span>
            </div>
            <div className="bg-slate-900 rounded-xl p-4 flex flex-col justify-between">
              <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Highest Level</span>
              <span className="text-lg font-bold text-cyan-400">{metrics?.highest_level_reached}</span>
            </div>
            
            {/* System Diagnostics Block */}
            <div className="col-span-2 bg-[#070b13] rounded-xl p-4 border border-slate-800/80 mt-4">
              <span className="text-[10px] text-slate-500 uppercase font-bold block mb-2 tracking-widest flex items-center justify-between">
                <span>SYSTEM DIAGNOSTICS</span>
                <span className="text-cyan-500/50">RAW TELEMETRY</span>
              </span>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-900 overflow-x-auto">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-800/50">
                  <span className="text-[9px] text-slate-600">ASSESSMENT_ID:</span>
                  <span className="text-[11px] text-cyan-400 font-bold user-select-all">{backendResult.assessment_id || 'N/A'}</span>
                </div>
                <pre className="text-[9px] text-slate-400 font-mono">
                  {JSON.stringify(backendResult.metrics, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* DUAL ACTION CALL TO ACTIONS */}
      <div className="space-y-4 relative z-10 mt-6">
        
        {/* Continue to analytics (Primary, neon border styled matching Image 3) */}
        <button
          onClick={handleProceedToAnalytics}
          className="w-full py-4 bg-slate-950 hover:bg-cyan-950/20 border-2 border-dashed border-cyan-400 text-cyan-400 font-mono font-bold text-xs uppercase tracking-[0.2em] rounded-xl shadow-[0_0_20px_rgba(34,211,238,0.15)] hover:shadow-[0_0_30px_rgba(34,211,238,0.3)] hover:scale-[1.01] transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
        >
          <span>CONTINUE TO ANALYTICS</span>
        </button>

        {/* Return to map (Secondary, simpler uppercase font block link) */}
        <button
          onClick={handleReturnToMap}
          className="w-full py-2 bg-transparent text-slate-500 hover:text-slate-300 font-mono font-bold text-[10px] tracking-widest uppercase transition-colors cursor-pointer"
        >
          RETURN TO MAP
        </button>
      </div>
    </div>
  );
};

