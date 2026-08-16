import { AssessmentProvider, useAssessment } from './context/AssessmentContext';
import { GqAssessment } from './components/GqAssessment';
import { IntakeScreen } from './components/IntakeScreen';
import { MapScreen } from './components/MapScreen';
import { SolverBotScreen } from './components/SolverBotScreen';
import { NeuralCoreScreen } from './components/NeuralCoreScreen';
import { DecisionCoreScreen } from './components/DecisionCoreScreen';
import { AnalyticsScreen } from './components/AnalyticsScreen';
import { AdminScreen } from './components/AdminScreen';
import { SuccessScreen } from './components/SuccessScreen';
import { EventLogger } from './components/EventLogger';
import { QuickNavigator } from './components/QuickNavigator';
import { Database, Terminal } from 'lucide-react';

function AppContent() {
  const {
    currentScreen,
    profile,
    showLoggerDock,
    setShowLoggerDock,
    events,
    handleNavigate,
  } = useAssessment();

  return (
    <div className="min-h-screen bg-[#070b13] p-3 md:p-4 text-slate-100 font-sans flex flex-col relative antialiased selection:bg-cyan-500 selection:text-slate-950">
      <div className="flex-1 flex flex-col bg-[#020617] border border-slate-800/80 rounded-2xl relative overflow-hidden shadow-2xl">
        {/* Upper Navigation Header Bar (High-Tech Tactical Terminal style) */}
        <header className="sticky top-0 z-40 bg-[#020617] border-b border-slate-900 px-6 py-3.5 flex items-center justify-between font-mono">
          <div 
            onClick={() => handleNavigate('splash')}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_#22d3ee]"></span>
            <span className="text-xs uppercase tracking-[0.2em] font-bold text-cyan-400">MISSION_ID: SYNAPSE-99</span>
          </div>

          {/* Dynamic header stats */}
          <div className="flex items-center gap-6 text-xs text-slate-400 font-mono">
            <div className="hidden sm:flex items-center gap-1.5">
              <span>System Status:</span>
              <span className="text-cyan-400 font-bold uppercase tracking-wider">Optimal</span>
            </div>
            
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
              <span className="text-slate-500">XP:</span>
              <span className="bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded text-cyan-400 font-bold">
                {profile ? profile.xp.toLocaleString() : '2,450'}
              </span>
            </div>

            {/* Admin toggle visible on deep pages */}
            {currentScreen !== 'splash' && profile?.role === 'admin' && (
              <button
                onClick={() => handleNavigate(currentScreen === 'admin-control' ? 'map' : 'admin-control')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded border text-[10px] font-mono font-bold transition ${
                  currentScreen === 'admin-control'
                    ? 'bg-rose-500/20 border-rose-500 text-rose-300'
                    : 'bg-[#0f172a] border-slate-800 text-slate-400 hover:text-rose-400 hover:border-slate-700'
                }`}
              >
                <span>ADMIN</span>
              </button>
            )}

            {/* Live telemetry visible on deep pages */}
            {currentScreen !== 'splash' && (
              <button
                onClick={() => setShowLoggerDock(!showLoggerDock)}
                className={`p-1.5 rounded border transition ${
                  showLoggerDock 
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400' 
                    : 'bg-[#0f172a] border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
                title="Toggle Live Telemetry Terminal"
              >
                <Terminal className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </header>

        {/* Main Container Workspace */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 py-8 flex flex-col gap-8 justify-center">
          
          {/* VIEW ROUTING MANAGER */}

          {/* 1. SPLASH SCREEN (Futuristic Tactical UI style matching Screenshot 1) */}
          {currentScreen === 'splash' && (
            <div className="flex-1 flex flex-col items-center justify-center max-w-4xl mx-auto py-8 text-center space-y-12 w-full animate-fade-in">
              {/* Logo area with glowing gradient and broken-image indicator (highly stylized, faithful to screenshot) */}
              <div className="relative flex flex-col items-center">
                <div className="absolute -inset-10 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
                
                <div className="flex items-center gap-3 bg-slate-900/40 border border-slate-800 px-4 py-2.5 rounded-xl text-slate-400 font-mono text-xs shadow-lg">
                  {/* Broken image style icon and text for authenticity */}
                  <div className="w-5 h-5 border border-slate-700 rounded flex items-center justify-center bg-slate-950 text-slate-500 text-[10px]">
                    ✕
                  </div>
                  <span>SYNAPSE Logo</span>
                </div>
              </div>

              {/* Glowing huge title */}
              <div className="space-y-4">
                <h1 className="text-6xl md:text-7xl font-black tracking-[0.25em] text-cyan-400 font-space select-none drop-shadow-[0_0_15px_rgba(34,211,238,0.35)]">
                  SYNAPSE
                </h1>
                
                {/* Centered spaced slogan with horizontal divider lines */}
                <div className="flex items-center justify-center gap-4 text-xs font-mono tracking-[0.2em] text-slate-400 font-bold">
                  <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-cyan-500/50"></div>
                  <span>TRAIN AN AI. DISCOVER YOUR THINKING.</span>
                  <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-cyan-500/50"></div>
                </div>
              </div>

              {/* Three stats cards in single row (matching Screenshot 1) */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mx-auto">
                <div className="bg-[#0f172a]/40 border border-slate-800/80 p-5 rounded-lg flex flex-col items-start font-mono text-left">
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Neural Load</span>
                  <span className="text-lg font-black text-cyan-400">84.2%</span>
                </div>

                <div className="bg-[#0f172a]/40 border border-slate-800/80 p-5 rounded-lg flex flex-col items-start font-mono text-left">
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Active Nodes</span>
                  <span className="text-lg font-black text-cyan-400">12,402</span>
                </div>

                <div className="bg-[#0f172a]/40 border border-slate-800/80 p-5 rounded-lg flex flex-col items-start font-mono text-left">
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Encryption</span>
                  <span className="text-lg font-black text-cyan-400">AES-QNTM</span>
                </div>
              </div>

              {/* High-contrast neon bordered buttons */}
              <div className="flex flex-col sm:flex-row gap-4 w-full justify-center max-w-md">
                <button
                  onClick={() => handleNavigate('intake')}
                  className="px-10 py-4 bg-slate-950 hover:bg-cyan-950/20 border-2 border-dashed border-cyan-400 text-cyan-400 font-mono font-bold text-sm uppercase tracking-widest rounded-lg shadow-lg hover:shadow-cyan-400/20 transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer group"
                >
                  <span>START MISSION</span>
                  <span className="group-hover:translate-x-1.5 transition">→</span>
                </button>
                
                {profile?.role === 'admin' && (
                  <button
                    onClick={() => handleNavigate('admin-control')}
                    className="px-10 py-4 bg-slate-950 hover:bg-slate-900 border border-dashed border-slate-800 text-slate-400 hover:text-slate-200 font-mono font-bold text-sm uppercase tracking-widest rounded-lg transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <span>ADMIN ACCESS</span>
                    <span>🎛️</span>
                  </button>
                )}
              </div>

              {/* Bottom protocol specs footer */}
              <div className="text-[10px] font-mono text-slate-600 tracking-wider">
                EST. 2024 &bull; PRIVACY_PROTOCOL_V4
              </div>
            </div>
          )}

          {/* 2. STUDENT INTAKE FORM */}
          {currentScreen === 'intake' && <IntakeScreen />}

          {/* 3. MISSION MAP */}
          {currentScreen === 'map' && <MapScreen />}

        {/* ADAPTIVE ASSESSMENTS */}
        {currentScreen === 'gq-assessment' && <GqAssessment />}

        {/* 4. SOLVERBOT CHALLENGES */}
        {(currentScreen === 'solver-capacity' || currentScreen === 'solver-resource' || currentScreen === 'solver-route') && (
          <SolverBotScreen />
        )}

        {/* 5. NEURAL CORE & PATTERNBOT CHALLENGES */}
        {(currentScreen === 'neural-core' || currentScreen === 'pattern-bot') && (
          <NeuralCoreScreen />
        )}

        {/* 6. DECISION CORE EQUILIBRIUM BALANCE */}
        {currentScreen === 'decision-core' && <DecisionCoreScreen />}

        {/* 7. ANALYTICS, SUITES, VISIONBOT, WAVE CHALLENGE, EXPOSURES */}
        {(currentScreen === 'vision-bot' || currentScreen === 'cognitive-analytics' || currentScreen === 'cognitive-profile' || currentScreen === 'analytics-core' || currentScreen === 'item-exposure') && (
          <AnalyticsScreen />
        )}

        {/* 8. ADMIN MISSION OVERRIDE CONTROL */}
        {currentScreen === 'admin-control' && <AdminScreen />}

        {/* 9. MISSION SUCCESS MILSTONE SUMMARY */}
        {currentScreen === 'success' && <SuccessScreen />}

        {/* 10. REAL-TIME EVENT LOGGER */}
        {currentScreen === 'event-logger' && <EventLogger />}

        {/* Embedded Bottom slide-out live terminal log stream (If showLoggerDock active) */}
        {showLoggerDock && (
          <div className="border-t border-cyan-500/20 bg-slate-950/95 shadow-2xl p-4 rounded-xl font-mono text-xs">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-3">
              <span className="text-cyan-400 font-bold tracking-wider flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5" /> LIVE TELEMETRY DEVIATION STREAM
              </span>
              <button 
                onClick={() => setShowLoggerDock(false)}
                className="text-slate-500 hover:text-slate-300 font-bold"
              >
                ✕ CLOSE
              </button>
            </div>
            <div className="h-40 overflow-y-auto space-y-1.5 scrollbar-thin">
              {events.slice(0, 10).map((ev) => (
                <div key={ev.id} className="flex items-start gap-3 hover:bg-slate-900/40 p-1 rounded">
                  <span className="text-slate-500">[{ev.timestamp}]</span>
                  <span className={`font-bold px-1 py-0.5 rounded text-[10px] ${
                    ev.status === 'SUCCESS' 
                      ? 'bg-emerald-500/10 text-emerald-400' 
                      : ev.status === 'ERROR' 
                      ? 'bg-rose-500/10 text-rose-400' 
                      : 'bg-cyan-500/10 text-cyan-400'
                  }`}>
                    {ev.action}
                  </span>
                  <span className="text-slate-300">{ev.details}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Embedded Global quick controller console dock */}
      <QuickNavigator />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AssessmentProvider>
      <AppContent />
    </AssessmentProvider>
  );
}
