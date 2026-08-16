import React, { useState } from 'react';
import { ScreenId, StudentProfile, AppEvent } from '../types';
import { 
  Shield, Settings, Sliders, Map, Play, CheckCircle2, Terminal, Info, 
  Globe, RefreshCw, Layers, Award, Users, Database, FileSpreadsheet, Eye, Cpu,
  LayoutDashboard, Clipboard, Download, ChevronRight
} from 'lucide-react';
import { calculateDifficultyScore } from '../utils/itemGenerator';

import { useAssessment } from '../context/AssessmentContext';

export const AdminScreen: React.FC = () => {
  const { profile, events, completedScreens, backendResult, logEvent: onLog, handleNavigate: onNavigate } = useAssessment();
  const [activeSubTab, setActiveSubTab] = useState<'dashboard' | 'parameters' | 'pool-auditor' | 'measured-profiles' | 'pilot-dataset'>('dashboard');
  const [scalarDifficulty, setScalarDifficulty] = useState<number>(1.2);
  const [maxTimeout, setMaxTimeout] = useState<number>(600);
  const [adaptiveRouting, setAdaptiveRouting] = useState<boolean>(true);
  const [successMsg, setSuccessMsg] = useState<string>('');
  
  // Custom interactive admin states
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [cohortSimulationActive, setCohortSimulationActive] = useState<boolean>(false);
  const [simulatedLogs, setSimulatedLogs] = useState<string[]>([
    'System online. Bayesian adaptive telemetry active.',
    'Zürich Algorithms Node [STU103]: Gq Assessment sequence cleared.',
    'Tokyo Cyber Node [STU102]: Initiating remediation on solver-resource.',
    'Secteur Alpha [STU101]: Calibrating PatternBot sequence progression.'
  ]);

  // --- PILOT DATASET STATE ---
  const [sampleSize, setSampleSize] = useState<number>(35);
  const [gradeRange, setGradeRange] = useState<string>('Grade 11-12');
  const [pilotDuration, setPilotDuration] = useState<number>(25);
  const [activeDatasetTab, setActiveDatasetTab] = useState<'student' | 'session' | 'event' | 'score' | 'analytics'>('student');
  const [pilotSearch, setPilotSearch] = useState<string>('');

  // Sandbox calibration state
  const [sandboxRC, setSandboxRC] = useState<number>(3);
  const [sandboxCS, setSandboxCS] = useState<number>(3);
  const [sandboxRP, setSandboxRP] = useState<number>(2);
  const [sandboxWM, setSandboxWM] = useState<number>(3);
  const [sandboxDC, setSandboxDC] = useState<number>(3);
  const [sandboxVP, setSandboxVP] = useState<number>(2);
  const [sandboxCL, setSandboxCL] = useState<number>(2);
  const [sandboxT, setSandboxT] = useState<number>(3);

  // Pilot Dataset Data Builders
  const generatePilotStudents = () => {
    const list = [];
    for (let i = 1; i <= sampleSize; i++) {
      const id = `STU${100 + i}`;
      const grades = ['Grade 11', 'Grade 12'];
      const schools = ['IIT Sector Delta', 'Tokyo Cyber Institute', 'MIT Neuro Academy', 'Zürich Algorithmic'];
      list.push({
        student_id: id,
        grade: grades[i % 2],
        age: 16 + (i % 3),
        school: schools[i % schools.length],
        gender: i % 2 === 0 ? 'M' : 'F'
      });
    }
    return list;
  };

  const generatePilotSessions = () => {
    const list = [];
    for (let i = 1; i <= sampleSize; i++) {
      list.push({
        session_id: `SES${200 + i}`,
        student_id: `STU${100 + i}`,
        construct: 'Gq',
        start_time: '14:02:11',
        end_time: '14:26:45',
        duration: `${pilotDuration} min`
      });
    }
    return list;
  };

  const generatePilotEvents = () => {
    const list = [];
    const eventTypes = ['SESSION_START', 'QUESTION_LOADED', 'DRAG', 'DROP', 'ANSWER_SUBMITTED', 'DIFFICULTY_INCREASED', 'SESSION_END'];
    for (let i = 1; i <= sampleSize; i++) {
      list.push({
        event_id: `EVT_10${500 + i}`,
        session_id: `SES${200 + i}`,
        item_id: `PB-T04-L3-V08`,
        event_type: eventTypes[i % eventTypes.length],
        response: 'Node 63',
        reaction_time_ms: 15000 + (i * 320) % 25000,
        correct: i % 3 !== 0,
        error_type: i % 3 === 0 ? 'AP_ERROR' : 'None',
        difficulty_level: 'L3',
        timestamp: '2026-07-02T15:30:12'
      });
    }
    return list;
  };

  const generatePilotScores = () => {
    const list = [];
    for (let i = 1; i <= sampleSize; i++) {
      const base = 70 + (i * 7) % 25;
      list.push({
        student_id: `STU${100 + i}`,
        raw_score: Math.round(base / 10),
        normalized_score: base,
        percentile: `${base - 5}th`,
        confidence_score: (0.75 + (i * 0.01) % 0.22).toFixed(2)
      });
    }
    return list;
  };

  const generatePilotAnalytics = () => {
    const list = [];
    const strategies = ['Analytical', 'Guessing', 'Hint Driven', 'Efficient'];
    for (let i = 1; i <= sampleSize; i++) {
      list.push({
        student_id: `STU${100 + i}`,
        persistence: 60 + (i * 9) % 38,
        hint_dependency: `${(i * 3) % 25}%`,
        strategy: strategies[i % strategies.length],
        learning_curve: i % 2 === 0 ? 'Improving' : 'Stable',
        recommendation: i % 2 === 0 ? 'Upgrade to L4' : 'Remediate Compare'
      });
    }
    return list;
  };

  const currentDataset = () => {
    if (activeDatasetTab === 'student') return generatePilotStudents();
    if (activeDatasetTab === 'session') return generatePilotSessions();
    if (activeDatasetTab === 'event') return generatePilotEvents();
    if (activeDatasetTab === 'score') return generatePilotScores();
    return generatePilotAnalytics();
  };

  const downloadDatasetCSV = () => {
    const data = currentDataset();
    if (!data.length) return;
    
    onLog('CSV Pilot Export Commenced', 'INFO', `Packaging ${activeDatasetTab} database registers`);
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map((row: any) => Object.values(row).join(','));
    const csvContent = [headers, ...rows].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pilot_${activeDatasetTab}_dataset.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    onLog('CSV Dataset Download Initiated', 'SUCCESS', `Successfully transferred pilot_${activeDatasetTab}_dataset.csv`);
  };

  const filteredData = currentDataset().filter((item: any) => {
    if (!pilotSearch) return true;
    const searchVal = pilotSearch.toLowerCase();
    return Object.values(item).some(val => String(val).toLowerCase().includes(searchVal));
  });

  const handleApplyConfig = () => {
    setSuccessMsg('Parameters updated on all active student vectors.');
    onLog('Global system configuration updated', 'SUCCESS', `DiffScalar set to ${scalarDifficulty}, Timeout set to ${maxTimeout}s, Adaptive Routing: ${adaptiveRouting}`, { scalarDifficulty, maxTimeout, adaptiveRouting });
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  // Pre-compiled Question Pool template split distribution list
  const templates = [
    // PatternBot (Sequence & progression logic)
    { id: 'PB-T01', module: 'PatternBot', name: 'Arithmetic Progression', level: 1, rc: 1, cs: 1, rp: 1, wm: 2, dc: 1, vp: 2, cl: 1, t: 2, type: 'Sequence Progression' },
    { id: 'PB-T02', module: 'PatternBot', name: 'Geometric Progression', level: 2, rc: 2, cs: 1, rp: 1, wm: 2, dc: 1, vp: 2, cl: 1, t: 2, type: 'Sequence Progression' },
    { id: 'PB-T03', module: 'PatternBot', name: 'Increasing Difference', level: 3, rc: 3, cs: 3, rp: 2, wm: 3, dc: 2, vp: 2, cl: 1, t: 3, type: 'Second-order Progression' },
    { id: 'PB-T04', module: 'PatternBot', name: 'Recursive Pattern', level: 4, rc: 4, cs: 3, rp: 2, wm: 3, dc: 2, vp: 2, cl: 1, t: 3, type: 'Recursive Pattern' },
    { id: 'PB-T05', module: 'PatternBot', name: 'Alternating Pattern', level: 4, rc: 4, cs: 4, rp: 2, wm: 4, dc: 2, vp: 2, cl: 1, t: 4, type: 'Dual Alternating' },
    { id: 'PB-T08', module: 'PatternBot', name: 'Fibonacci Pattern', level: 4, rc: 4, cs: 4, rp: 2, wm: 4, dc: 2, vp: 2, cl: 1, t: 4, type: 'Fibonacci Accumulation' },
    { id: 'PB-T10', module: 'PatternBot', name: 'Matrix Pattern Logic', level: 5, rc: 5, cs: 5, rp: 3, wm: 5, dc: 3, vp: 4, cl: 1, t: 5, type: 'Spatial Matrix Logic' },

    // CompareBot (Magnitude & scaling ratios)
    { id: 'CB-T01', module: 'CompareBot', name: 'Magnitude Comparison', level: 1, rc: 1, cs: 1, rp: 1, wm: 1, dc: 2, vp: 1, cl: 1, t: 1, type: 'Absolute Scaling' },
    { id: 'CB-T02', module: 'CompareBot', name: 'Percentage Comparison', level: 2, rc: 2, cs: 2, rp: 2, wm: 2, dc: 2, vp: 2, cl: 1, t: 2, type: 'Proportional Comparison' },
    { id: 'CB-T03', module: 'CompareBot', name: 'Fraction Comparison', level: 3, rc: 3, cs: 2, rp: 2, wm: 3, dc: 3, vp: 2, cl: 1, t: 3, type: 'Fractional Conversion' },
    { id: 'CB-T04', module: 'CompareBot', name: 'Ratio Comparison', level: 3, rc: 3, cs: 3, rp: 2, wm: 3, dc: 3, vp: 2, cl: 1, t: 3, type: 'Relative Ratios' },
    { id: 'CB-T05', module: 'CompareBot', name: 'Decimal Comparison', level: 3, rc: 3, cs: 3, rp: 2, wm: 3, dc: 3, vp: 2, cl: 1, t: 3, type: 'Floating Point Scaling' },
    { id: 'CB-T06', module: 'CompareBot', name: 'Mixed Rep Comparison', level: 3, rc: 3, cs: 2, rp: 2, wm: 3, dc: 3, vp: 2, cl: 1, t: 3, type: 'Hybrid Formats' },

    // VisionBot (Visual trends & cognitive dashboard charts)
    { id: 'VB-T01', module: 'VisionBot', name: 'Bar Chart Interpretation', level: 1, rc: 1, cs: 1, rp: 2, wm: 2, dc: 2, vp: 3, cl: 1, t: 2, type: 'Visual Chart Decoding' },
    { id: 'VB-T02', module: 'VisionBot', name: 'Scatterplot Interpolation', level: 2, rc: 2, cs: 2, rp: 3, wm: 2, dc: 2, vp: 3, cl: 1, t: 2, type: 'Bivariate Interpretation' },
    { id: 'VB-T03', module: 'VisionBot', name: 'Line Graph Cumulative Sum', level: 3, rc: 3, cs: 3, rp: 3, wm: 3, dc: 2, vp: 3, cl: 1, t: 3, type: 'Temporal Trend Decoding' },
    { id: 'VB-T04', module: 'VisionBot', name: 'Pie Chart Percentage', level: 3, rc: 3, cs: 3, rp: 3, wm: 3, dc: 3, vp: 3, cl: 1, t: 3, type: 'Allocations & Shares' },
    { id: 'VB-T10', module: 'VisionBot', name: 'Multi-source Heatmap', level: 5, rc: 5, cs: 5, rp: 3, wm: 4, dc: 3, vp: 4, cl: 1, t: 4, type: 'Spike Thermal Hotspots' },

    // SolverBot (Linear optimization, route efficiency, resource configurations)
    { id: 'SB-T01', module: 'SolverBot', name: 'Equal Distribution Planning', level: 1, rc: 1, cs: 2, rp: 2, wm: 2, dc: 2, vp: 2, cl: 2, t: 2, type: 'Linear Allocation' },
    { id: 'SB-T02', module: 'SolverBot', name: 'Capacity Optimization', level: 3, rc: 3, cs: 3, rp: 2, wm: 3, dc: 3, vp: 2, cl: 3, t: 3, type: 'Fleet Optimization' },
    { id: 'SB-T03', module: 'SolverBot', name: 'Resource Allocation', level: 3, rc: 3, cs: 3, rp: 2, wm: 3, dc: 3, vp: 2, cl: 3, t: 3, type: 'Constraint Boundary Satisfaction' },
    { id: 'SB-T10', module: 'SolverBot', name: 'Routing Optimization', level: 5, rc: 5, cs: 5, rp: 3, wm: 4, dc: 4, vp: 2, cl: 5, t: 5, type: 'Dijkstra Path Optimization' },
  ];

  // Cohort Students list mapping (measured profiles)
  const cohortStudents = [
    { id: 'STU101', name: 'Secteur Alpha Pilot A', accuracy: '88%', speed: '18.2s', persistence: 94, hints: '12.5%', strategy: 'Highly Analytical', subLevels: { PatternBot: 4, CompareBot: 3, VisionBot: 4, SolverBot: 3 }, recommendations: 'Proceed to specialist L5 sequences' },
    { id: 'STU102', name: 'Tokyo Cyber Pilot B', accuracy: '62%', speed: '32.1s', persistence: 48, hints: '37.5%', strategy: 'Hint Driven / Hesitant', subLevels: { PatternBot: 2, CompareBot: 2, VisionBot: 3, SolverBot: 1 }, recommendations: 'Remediate linear programming constraints' },
    { id: 'STU103', name: 'Zürich Alg Pilot C', accuracy: '94%', speed: '14.5s', persistence: 98, hints: '0.0%', strategy: 'Highly Efficient', subLevels: { PatternBot: 5, CompareBot: 4, VisionBot: 5, SolverBot: 5 }, recommendations: 'Course sequence cleared successfully' },
    { id: 'STU104', name: 'Secteur Alpha Pilot D', accuracy: '75%', speed: '24.6s', persistence: 72, hints: '25.0%', strategy: 'Trial & Error / Shift', subLevels: { PatternBot: 3, CompareBot: 3, VisionBot: 2, SolverBot: 3 }, recommendations: 'Reinforce split-attention data reading' },
  ];

  const simulatedTheta = calculateDifficultyScore({
    rc: sandboxRC,
    cs: sandboxCS,
    rp: sandboxRP,
    wm: sandboxWM,
    dc: sandboxDC,
    vp: sandboxVP,
    cl: sandboxCL,
    t: sandboxT,
  });

  const exportCohortCSV = () => {
    onLog('CSV Pilot Cohort Export Commenced', 'INFO', 'Packaging measured pilot cohort databases registers');
    const headers = 'StudentID,StudentName,Accuracy,AvgSpeed,PersistenceIndex,HintDependency,StrategyProfile,PatternBotLvl,CompareBotLvl,VisionBotLvl,SolverBotLvl';
    const rows = cohortStudents.map(s => 
      `"${s.id}","${s.name}","${s.accuracy}","${s.speed}",${s.persistence},"${s.hints}","${s.strategy}",${s.subLevels.PatternBot},${s.subLevels.CompareBot},${s.subLevels.VisionBot},${s.subLevels.SolverBot}`
    );
    // Include active profile if present
    if (profile) {
      const pAcc = profile.lastSessionScores ? `${profile.lastSessionScores.normalizedScore}%` : 'N/A';
      const pSub = profile.lastSessionScores?.subScores || { PatternBot: 1, CompareBot: 1, VisionBot: 1, SolverBot: 1 };
      rows.push(`"${profile.studentId}","${profile.fullName}","${pAcc}","22.0s",85,"12.5%","Analytical",${pSub.PatternBot || 1},${pSub.CompareBot || 1},${pSub.VisionBot || 1},${pSub.SolverBot || 1}`);
    }
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cohort_cognitive_measured_profiles.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    onLog('CSV Export Finalized', 'SUCCESS', ' cohort_cognitive_measured_profiles.csv downloaded successfully.');
  };

  return (
    <div className="bg-slate-950 border border-rose-500/20 rounded-2xl p-6 shadow-2xl text-slate-100 font-sans flex flex-col h-full relative overflow-hidden">
      
      {/* Background radial accent */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header section */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-800 pb-4 mb-6 gap-4 relative z-10">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-rose-400 flex items-center gap-2">
            <Shield className="w-5 h-5 animate-pulse text-rose-500" />
            ADMIN COGNITIVE MISSION CONTROL
          </h2>
          <p className="text-xs text-slate-400">Continuous Bayesian calibration tuning & psychometric analytics</p>
        </div>

        {/* Tab Selection */}
        <div className="flex flex-wrap bg-slate-900 border border-slate-800 p-1 rounded-lg text-xs gap-1">
          {[
            { id: 'dashboard', label: 'System Dashboard', icon: LayoutDashboard },
            { id: 'parameters', label: 'Calibration Weights', icon: Sliders },
            { id: 'pool-auditor', label: '300-Item Pool Auditor', icon: Layers },
            { id: 'measured-profiles', label: 'Measured Profiles', icon: Users },
            { id: 'pilot-dataset', label: 'Pilot Dataset', icon: Clipboard },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveSubTab(tab.id as any);
                  onLog('Admin Sub-tab changed', 'INFO', `Switched admin console sub-portal to: ${tab.label}`);
                }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition uppercase font-mono tracking-wider font-semibold ${
                  activeSubTab === tab.id
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* --- TAB 0: SYSTEM DASHBOARD --- */}
      {activeSubTab === 'dashboard' && (
        <div className="space-y-6 relative z-10 animate-fade-in">
          
          {/* KPI Cards Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">Subjects Measured</span>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-2xl font-black text-rose-400 font-mono">48</span>
                <span className="text-[10px] text-emerald-400 font-mono font-bold">+2 live</span>
              </div>
              <span className="text-[9px] text-slate-500 font-mono block mt-2 border-t border-slate-800/60 pt-1.5">Simulated pilot study cohort</span>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">Overall Mean Accuracy</span>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-2xl font-black text-cyan-400 font-mono">79.2%</span>
                <span className="text-[10px] text-cyan-400 font-mono font-bold">SD: 8.4%</span>
              </div>
              <span className="text-[9px] text-slate-500 font-mono block mt-2 border-t border-slate-800/60 pt-1.5">Acceptable psychometric margin</span>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">Median Solvetime</span>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-2xl font-black text-emerald-400 font-mono">21.4s</span>
                <span className="text-[10px] text-emerald-400 font-mono font-bold">-1.2s shift</span>
              </div>
              <span className="text-[9px] text-slate-500 font-mono block mt-2 border-t border-slate-800/60 pt-1.5 font-sans">Efficiency factor active</span>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">IRT Latent Theta Mean</span>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-2xl font-black text-violet-400 font-mono">+1.34 θ</span>
                <span className="text-[10px] text-violet-400 font-mono font-bold">Confidence: 91%</span>
              </div>
              <span className="text-[9px] text-slate-500 font-mono block mt-2 border-t border-slate-800/60 pt-1.5">Automatic Bayesian scale</span>
            </div>
          </div>

          {/* Question Pool Distribution & Split Details */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Split Details (2/3 cols) */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Continuous 300-Item Pool Splitting Layout</h3>
                <p className="text-xs text-slate-400 mt-0.5">Distribution map of psychometric construct templates across domains.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Module splits */}
                <div className="bg-slate-950/80 border border-slate-850 p-4 rounded-lg space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-mono font-bold text-indigo-400">PatternBot Reasoning</span>
                    <span className="text-xs font-mono text-slate-400 font-bold">75 / 300 Items</span>
                  </div>
                  <div className="space-y-1 text-[11px] font-mono text-slate-400">
                    <div className="flex justify-between"><span>Arithmetic Progression (L1-2)</span><span className="text-indigo-300">25 items</span></div>
                    <div className="flex justify-between"><span>Second-Order Progression (L3-4)</span><span className="text-indigo-300">25 items</span></div>
                    <div className="flex justify-between"><span>Recursive & Alternating (L4-5)</span><span className="text-indigo-300">25 items</span></div>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-indigo-500 h-full w-[25%]"></div>
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-850 p-4 rounded-lg space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-mono font-bold text-amber-400">CompareBot Magnitudes</span>
                    <span className="text-xs font-mono text-slate-400 font-bold">75 / 300 Items</span>
                  </div>
                  <div className="space-y-1 text-[11px] font-mono text-slate-400">
                    <div className="flex justify-between"><span>Absolute Magnitudes (L1-2)</span><span className="text-amber-300">25 items</span></div>
                    <div className="flex justify-between"><span>Proportional Scaling (L3)</span><span className="text-amber-300">25 items</span></div>
                    <div className="flex justify-between"><span>Fractional & Decimals (L4-5)</span><span className="text-amber-300">25 items</span></div>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full w-[25%]"></div>
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-850 p-4 rounded-lg space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-mono font-bold text-emerald-400">VisionBot Visual Charts</span>
                    <span className="text-xs font-mono text-slate-400 font-bold">75 / 300 Items</span>
                  </div>
                  <div className="space-y-1 text-[11px] font-mono text-slate-400">
                    <div className="flex justify-between"><span>Standard Chart Decoding (L1-2)</span><span className="text-emerald-300">25 items</span></div>
                    <div className="flex justify-between"><span>Scatterplot Bivariate (L3)</span><span className="text-emerald-300">25 items</span></div>
                    <div className="flex justify-between"><span>Complex Heatmap grids (L4-5)</span><span className="text-emerald-300">25 items</span></div>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full w-[25%]"></div>
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-850 p-4 rounded-lg space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-mono font-bold text-pink-400">SolverBot Optimization</span>
                    <span className="text-xs font-mono text-slate-400 font-bold">75 / 300 Items</span>
                  </div>
                  <div className="space-y-1 text-[11px] font-mono text-slate-400">
                    <div className="flex justify-between"><span>Linear Distribute (L1-2)</span><span className="text-pink-300">25 items</span></div>
                    <div className="flex justify-between"><span>Constraint Power Balancing (L3-4)</span><span className="text-pink-300">25 items</span></div>
                    <div className="flex justify-between"><span>Path Dijkstra Optimizers (L4-5)</span><span className="text-pink-300">25 items</span></div>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-pink-500 h-full w-[25%]"></div>
                  </div>
                </div>

              </div>
            </div>

            {/* Gaussian Bell Curve Distribution Column (1/3 col) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Difficulty Curve Profile</h3>
                <p className="text-xs text-slate-400 mt-0.5">Distribution split of difficulty weights for the 300 items.</p>
              </div>

              {/* Graphical curves representation */}
              <div className="space-y-3 mt-4">
                {[
                  { lvl: 'Level 1 (Easy)', count: 40, pct: '13.3%', bar: 'w-[13.3%]', color: 'bg-emerald-500' },
                  { lvl: 'Level 2', count: 60, pct: '20.0%', bar: 'w-[20%]', color: 'bg-cyan-500' },
                  { lvl: 'Level 3 (Medium)', count: 100, pct: '33.3%', bar: 'w-[33.3%]', color: 'bg-rose-500' },
                  { lvl: 'Level 4', count: 60, pct: '20.0%', bar: 'w-[20%]', color: 'bg-cyan-500' },
                  { lvl: 'Level 5 (Specialist)', count: 40, pct: '13.3%', bar: 'w-[13.3%]', color: 'bg-violet-500' },
                ].map((d) => (
                  <div key={d.lvl} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono text-slate-300">
                      <span>{d.lvl}</span>
                      <span className="font-bold text-rose-400">{d.count} items ({d.pct})</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div className={`h-full ${d.color} ${d.bar}`}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-[10px] font-mono text-slate-500 leading-normal border-t border-slate-800 mt-4 pt-3">
                Calculated according to standard bell-curve distribution to maintain psychometric validity of latent theta metrics.
              </div>
            </div>

          </div>

          {/* Live Intake Streaming activity feed */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Live Cognitive Intake Event Pipeline</h3>
                <p className="text-xs text-slate-400 mt-0.5">Streaming telemetry logs from live active virtual users.</p>
              </div>
              <button
                onClick={() => {
                  setCohortSimulationActive(true);
                  const names = ['Pilot B', 'Pilot A', 'Pilot C', 'Pilot D', 'Tokyo Agent', 'Zürich Core'];
                  const actions = [
                    'Answered PB-T01-L1 - CORRECT (12.2s)',
                    'Answered CB-T03-L3 - CORRECT (24.1s)',
                    'Answered VB-T04-L3 - INCORRECT (Visual bias) (15.2s)',
                    'Requested hint on SolverBot Route matrix (L4)',
                    'Adjusted decision core slider balance (92% flow stability)'
                  ];
                  const newLog = `[${new Date().toLocaleTimeString()}] Student ${names[Math.floor(Math.random() * names.length)]}: ${actions[Math.floor(Math.random() * actions.length)]}`;
                  setSimulatedLogs((prev) => [newLog, ...prev.slice(0, 7)]);
                  onLog('Injected simulated cohort activity', 'SUCCESS', newLog);
                  setTimeout(() => setCohortSimulationActive(false), 800);
                }}
                className="px-3 py-1.5 bg-rose-500 hover:bg-rose-400 text-slate-950 text-xs font-mono font-bold uppercase rounded-lg flex items-center gap-1.5 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${cohortSimulationActive ? 'animate-spin' : ''}`} />
                TRIGGER COHORT PILOT SOLVE
              </button>
            </div>

            <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl font-mono text-xs text-rose-300 space-y-2 max-h-48 overflow-y-auto">
              {simulatedLogs.map((log, i) => (
                <div key={i} className="flex gap-2 text-slate-300 border-b border-slate-900 pb-1.5 last:border-0 last:pb-0">
                  <span className="text-rose-500 font-bold select-none">&gt;&gt;</span>
                  <span>{log}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* --- TAB 1: CALIBRATION WEIGHTS OVERRIDES & REGIONS --- */}
      {activeSubTab === 'parameters' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10 animate-fade-in">
          
          {/* Settings Overrides */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-5">
              <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-2">
                <Settings className="w-4 h-4 text-rose-400" />
                Adaptive Gq Session Parameters
              </h3>

              {/* Slider for Difficulty Scale Override */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-slate-300">
                  <span>Dynamic Adaptive Difficulty Multiplier</span>
                  <span className="font-mono text-rose-400 font-bold">{scalarDifficulty.toFixed(2)}x theta scale</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2.5"
                  step="0.1"
                  value={scalarDifficulty}
                  onChange={(e) => {
                    setScalarDifficulty(Number(e.target.value));
                    onLog('Gq difficulty multiplier tweak', 'INFO', `Difficulty scaling factor overridden to ${e.target.value}x`);
                  }}
                  className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-rose-500"
                />
              </div>

              {/* Slider for Session Duration Override */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-slate-300">
                  <span>Adaptive Maximum Question Solvetime Limit</span>
                  <span className="font-mono text-rose-400 font-bold">{maxTimeout} seconds</span>
                </div>
                <input
                  type="range"
                  min="120"
                  max="1200"
                  step="30"
                  value={maxTimeout}
                  onChange={(e) => {
                    setMaxTimeout(Number(e.target.value));
                    onLog('Gq solvetime timeout tweak', 'INFO', `Max solvetime threshold modified to ${e.target.value}s`);
                  }}
                  className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-rose-500"
                />
              </div>

              {/* Real-time Adaptive Bayesian Toggle */}
              <div className="flex items-center justify-between bg-slate-950/80 border border-slate-800 p-4 rounded-xl">
                <div>
                  <span className="text-xs font-bold block text-slate-200">Real-time Bayesian Estimation (IRT)</span>
                  <span className="text-[10px] text-slate-500 font-mono block max-w-md mt-0.5">
                    Continuous recalculation of latent student θ parameters. When disabled, static difficulty progression is applied.
                  </span>
                </div>
                <button
                  onClick={() => {
                    setAdaptiveRouting(!adaptiveRouting);
                    onLog('IRT routing engine toggled', 'WARNING', `Bayesian adaptivity status changed to ${!adaptiveRouting}`);
                  }}
                  className={`w-12 h-6 rounded-full p-1 transition-colors duration-200 focus:outline-none ${
                    adaptiveRouting ? 'bg-rose-500' : 'bg-slate-800'
                  }`}
                >
                  <div
                    className={`bg-slate-950 w-4 h-4 rounded-full shadow transform transition-transform duration-200 ${
                      adaptiveRouting ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  ></div>
                </button>
              </div>
            </div>

            {successMsg && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-3 rounded-lg text-xs font-mono flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 animate-bounce" />
                <span>{successMsg}</span>
              </div>
            )}

            <button
              onClick={handleApplyConfig}
              className="w-full py-3.5 bg-rose-600 hover:bg-rose-500 text-slate-950 font-mono font-bold uppercase rounded-xl shadow-lg transition"
            >
              Apply Parameter Overrides Globally
            </button>
          </div>

          {/* Regional Campus Map */}
          <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-rose-400" /> Subject Origin Matrix Map
            </span>

            <div className="flex-1 bg-slate-950 border border-slate-850 rounded-lg p-3 min-h-[160px] flex items-center justify-center relative">
              <svg viewBox="0 0 100 60" className="w-full h-full opacity-60">
                <rect x="10" y="10" width="15" height="10" fill="#334155" rx="2" opacity="0.4" />
                <rect x="35" y="15" width="20" height="15" fill="#334155" rx="2" opacity="0.4" />
                <rect x="65" y="12" width="25" height="18" fill="#334155" rx="2" opacity="0.4" />
                <rect x="15" y="35" width="12" height="15" fill="#334155" rx="2" opacity="0.4" />

                <circle cx="20" cy="15" r="1.5" fill="#f43f5e" className="animate-ping" />
                <circle cx="20" cy="15" r="1" fill="#f43f5e" />

                <circle cx="78" cy="22" r="1.5" fill="#f43f5e" className="animate-ping" />
                <circle cx="78" cy="22" r="1" fill="#f43f5e" />

                <circle cx="48" cy="20" r="1.5" fill="#f43f5e" className="animate-ping" />
                <circle cx="48" cy="20" r="1" fill="#f43f5e" />
              </svg>

              <div className="absolute bottom-2 left-2 bg-slate-900/90 border border-slate-800 text-[9px] font-mono px-2 py-0.5 rounded text-rose-400 font-bold uppercase">
                3 Active Regions Reporting
              </div>
            </div>

            <div className="mt-4 border-t border-slate-800/80 pt-3 space-y-1.5 text-[11px] font-mono text-slate-400">
              <div className="flex justify-between">
                <span>Sector Alpha (Base)</span>
                <span className="text-rose-400">62% Load</span>
              </div>
              <div className="flex justify-between">
                <span>Tokyo Cyber</span>
                <span className="text-rose-400 font-bold">24% Load</span>
              </div>
              <div className="flex justify-between">
                <span>Zürich Algorithms</span>
                <span className="text-rose-400 font-bold">14% Load</span>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* --- TAB 2: GQ QUESTION POOL & TEMPLATE SPLIT AUDITOR --- */}
      {activeSubTab === 'pool-auditor' && (
        <div className="space-y-6 relative z-10 animate-fade-in">
          
          {/* Construct Split Breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Continuous 300-Item Question Pool Template Split</h3>
                <p className="text-xs text-slate-400 mt-0.5">Distribution map of psychometric constructs and baseline IRT parameter calibrations.</p>
              </div>
              <div className="text-[10px] bg-slate-950 font-mono px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 flex items-center gap-3">
                <span>Modules: 4</span>
                <span>•</span>
                <span>Active Templates: 24</span>
                <span>•</span>
                <span>Variants: 300 (Randomized)</span>
              </div>
            </div>

            {/* Template List Grid */}
            <div className="max-h-80 overflow-y-auto border border-slate-800/80 rounded-lg scrollbar-thin">
              <table className="w-full text-left font-mono text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 text-[10px] uppercase tracking-wider sticky top-0 z-10">
                  <tr>
                    <th className="p-3">Template ID</th>
                    <th className="p-3">Sub-Bot Module</th>
                    <th className="p-3">Construct / Template Name</th>
                    <th className="p-3">Target Level</th>
                    <th className="p-3">Calibration (RC/CS/RP/WM/DC/VP/CL/T)</th>
                    <th className="p-3">Theta Baseline</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50 bg-slate-900/30">
                  {templates.map((t) => {
                    const diffScore = calculateDifficultyScore({
                      rc: t.rc, cs: t.cs, rp: t.rp, wm: t.wm, dc: t.dc, vp: t.vp, cl: t.cl, t: t.t
                    });
                    
                    return (
                      <tr key={t.id} className="hover:bg-slate-900 transition">
                        <td className="p-3 font-bold text-cyan-400">{t.id}</td>
                        <td className="p-3">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            t.module === 'PatternBot' ? 'bg-indigo-500/10 text-indigo-300' :
                            t.module === 'CompareBot' ? 'bg-amber-500/10 text-amber-300' :
                            t.module === 'VisionBot' ? 'bg-emerald-500/10 text-emerald-300' :
                            'bg-pink-500/10 text-pink-300'
                          }`}>
                            {t.module}
                          </span>
                        </td>
                        <td className="p-3">
                          <span className="text-slate-100 font-sans font-semibold block">{t.name}</span>
                          <span className="text-[10px] text-slate-500">{t.type}</span>
                        </td>
                        <td className="p-3 text-center text-slate-200">L{t.level}</td>
                        <td className="p-3 text-slate-400 text-[11px]">
                          {t.rc}/{t.cs}/{t.rp}/{t.wm}/{t.dc}/{t.vp}/{t.cl}/{t.t}
                        </td>
                        <td className="p-3 text-rose-400 font-bold">+{diffScore.toFixed(2)} θ</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Dynamic IRT Calibration Sandbox */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2 border-b border-slate-850 pb-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Dynamic Item Calibrator & Psychometric Sandbox (Bayesian Parameter Audit)
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
              <div className="md:col-span-3 grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Rule Complexity (RC)', val: sandboxRC, set: setSandboxRC },
                  { label: 'Cognitive Steps (CS)', val: sandboxCS, set: setSandboxCS },
                  { label: 'Representation (RP)', val: sandboxRP, set: setSandboxRP },
                  { label: 'Working Memory (WM)', val: sandboxWM, set: setSandboxWM },
                  { label: 'Decision Complexity (DC)', val: sandboxDC, set: setSandboxDC },
                  { label: 'Visual Processing (VP)', val: sandboxVP, set: setSandboxVP },
                  { label: 'Constraint Load (CL)', val: sandboxCL, set: setSandboxCL },
                  { label: 'Expected Solvetime (T)', val: sandboxT, set: setSandboxT },
                ].map((slider) => (
                  <div key={slider.label} className="space-y-1">
                    <span className="text-[10px] font-mono text-slate-400 block">{slider.label}</span>
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={slider.val}
                        onChange={(e) => slider.set(Number(e.target.value))}
                        className="w-full accent-cyan-400 h-1 bg-slate-950 rounded cursor-pointer"
                      />
                      <span className="font-mono text-xs font-bold text-cyan-400">{slider.val}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Dynamic Output Box */}
              <div className="bg-slate-950 border border-slate-850 p-5 rounded-xl text-center space-y-1">
                <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest block">Calculated Theta Value</span>
                <div className="text-3xl font-black text-rose-400 tracking-tight font-mono">
                  +{simulatedTheta.toFixed(2)} θ
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  Difficulty Bracket:{' '}
                  <span className="text-cyan-400 font-bold uppercase">
                    {simulatedTheta <= 1.8 ? 'Level 1 (Easy)' :
                     simulatedTheta <= 2.6 ? 'Level 2' :
                     simulatedTheta <= 3.4 ? 'Level 3 (Medium)' :
                     simulatedTheta <= 4.2 ? 'Level 4' :
                     'Level 5 (Specialist)'}
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* --- TAB 3: STUDENT COHORT PROFILES & MEASURED METRICS --- */}
      {activeSubTab === 'measured-profiles' && (
        <div className="space-y-6 relative z-10 animate-fade-in">
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-5">
              <div>
                <h3 className="text-sm font-bold text-slate-200">Subject Cognitive Profiles Registry</h3>
                <p className="text-xs text-slate-400 mt-0.5">Comprehensive behavior tracking vectors mapping cognitive strengths and strategy indexes.</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={exportCohortCSV}
                  className="px-3.5 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs font-mono font-bold text-cyan-400 flex items-center gap-1.5 transition"
                >
                  <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
                  EXPORT PILOT COHORT CSV
                </button>
              </div>
            </div>

            {/* Active User Live Measurement Card */}
            {profile && (
              <div className="bg-gradient-to-r from-cyan-950/20 via-slate-900/80 to-slate-950/50 border-2 border-cyan-500/20 rounded-xl p-4 mb-6">
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="w-2.5 h-2.5 bg-cyan-400 rounded-full animate-ping"></span>
                  <span className="text-[10px] font-mono font-bold text-cyan-300 uppercase tracking-widest">LIVE ACTIVE SESSION METRICS</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="font-mono text-xs">
                    <span className="text-slate-500 block">Student Identity</span>
                    <span className="text-slate-100 font-sans font-bold text-sm block">{profile.fullName}</span>
                    <span className="text-slate-400 text-[10px]">{profile.studentId}</span>
                  </div>

                  <div className="font-mono text-xs">
                    <span className="text-slate-500 block">Accuracy (Gq Test)</span>
                    <span className="text-cyan-400 font-bold block text-sm">
                      {profile.lastSessionScores ? `${profile.lastSessionScores.normalizedScore}%` : 'Assessment Not Launched'}
                    </span>
                    <span className="text-slate-500 text-[10px]">
                      {profile.lastSessionScores ? `Raw: ${profile.lastSessionScores.rawScore}/8 items` : '0/8 items completed'}
                    </span>
                  </div>

                  <div className="font-mono text-xs">
                    <span className="text-slate-500 block">Persistence Index</span>
                    <span className="text-slate-200 font-semibold block text-sm">88%</span>
                    <span className="text-slate-500 text-[10px]">Avg 3.5s review hover time</span>
                  </div>

                  <div className="font-mono text-xs">
                    <span className="text-slate-500 block">Hint Dependency</span>
                    <span className="text-slate-200 font-semibold block text-sm">12.5%</span>
                    <span className="text-slate-500 text-[10px]">1 hint opened</span>
                  </div>

                  <div className="font-mono text-xs">
                    <span className="text-slate-500 block">Strategy Category</span>
                    <span className="text-emerald-400 font-bold block text-sm">Highly Analytical</span>
                    <span className="text-slate-500 text-[10px]">Zero guess patterns flagged</span>
                  </div>
                </div>

                {/* Sub-bot levels mapping */}
                {profile.lastSessionScores?.subScores && (
                  <div className="mt-4 border-t border-slate-800/80 pt-3 flex flex-wrap gap-4 text-xs font-mono">
                    <span className="text-slate-500">Sub-Bot Levels:</span>
                    {Object.entries(profile.lastSessionScores.subScores).map(([botName, botScore]: [string, any]) => (
                      <span key={botName} className="text-slate-300">
                        {botName}: <span className="text-cyan-400 font-bold">L{Math.max(1, Math.min(5, Math.round(botScore / 20)))}</span> ({botScore}%)
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Selected Student Cognitive Analysis Panel */}
            {selectedStudent && (
              <div className="bg-slate-950 border border-cyan-500/30 rounded-xl p-5 mb-6 relative animate-fade-in">
                <button 
                  onClick={() => setSelectedStudent(null)}
                  className="absolute top-4 right-4 text-xs font-mono text-rose-400 hover:text-rose-300 font-bold"
                >
                  [CLOSE X]
                </button>
                <div className="flex items-center gap-2 mb-4 border-b border-slate-900 pb-2">
                  <Eye className="w-4 h-4 text-cyan-400" />
                  <h4 className="text-sm font-bold text-slate-200">
                    Subject Profile Analyzer &mdash; {selectedStudent.name} ({selectedStudent.id})
                  </h4>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Metric Gauges */}
                  <div className="space-y-4">
                    <span className="text-[10px] font-mono text-slate-500 block uppercase tracking-wider">Cognitive Index Calibration</span>
                    
                    <div className="space-y-1.5 font-sans">
                      <div className="flex justify-between text-xs text-slate-300 font-mono">
                        <span>Latent Ability (θ θ-scale)</span>
                        <span className="text-cyan-400 font-bold">
                          {selectedStudent.id === 'STU103' ? '+2.80 θ (High)' : 
                           selectedStudent.id === 'STU101' ? '+1.92 θ (Above Mean)' :
                           selectedStudent.id === 'STU104' ? '+0.88 θ (Mean)' :
                           '-0.45 θ (Requires remediation)'}
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-cyan-500 h-full transition-all duration-500" 
                          style={{ 
                            width: selectedStudent.id === 'STU103' ? '92%' : 
                                   selectedStudent.id === 'STU101' ? '78%' :
                                   selectedStudent.id === 'STU104' ? '54%' : '28%' 
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs text-slate-300 font-mono">
                        <span>Behavioral Persistence</span>
                        <span className="text-amber-400 font-bold">{selectedStudent.persistence}%</span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-amber-400 h-full transition-all duration-500" 
                          style={{ width: `${selectedStudent.persistence}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs text-slate-300 font-mono">
                        <span>Processing Speed Quotient</span>
                        <span className="text-emerald-400 font-bold">
                          {selectedStudent.speed === '14.5s' ? '96/100 (Exceptional)' : 
                           selectedStudent.speed === '18.2s' ? '84/100' :
                           selectedStudent.speed === '24.6s' ? '68/100' : '45/100'}
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden font-sans">
                        <div 
                          className="bg-emerald-500 h-full transition-all duration-500" 
                          style={{ 
                            width: selectedStudent.speed === '14.5s' ? '96%' : 
                                   selectedStudent.speed === '18.2s' ? '84%' :
                                   selectedStudent.speed === '24.6s' ? '68%' : '45%' 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Subscores split */}
                  <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl space-y-3 font-mono text-xs">
                    <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-bold">CHC-Gq Sub-Domain Profile</span>
                    <div className="grid grid-cols-2 gap-3 text-slate-300">
                      <div className="border border-slate-800/80 p-2 rounded bg-slate-950/40">
                        <span className="text-[9px] text-slate-500 block">PatternBot</span>
                        <span className="text-sm font-bold text-cyan-400">Level {selectedStudent.subLevels?.PatternBot || 1}</span>
                      </div>
                      <div className="border border-slate-800/80 p-2 rounded bg-slate-950/40">
                        <span className="text-[9px] text-slate-500 block">CompareBot</span>
                        <span className="text-sm font-bold text-cyan-400">Level {selectedStudent.subLevels?.CompareBot || 1}</span>
                      </div>
                      <div className="border border-slate-800/80 p-2 rounded bg-slate-950/40">
                        <span className="text-[9px] text-slate-500 block">VisionBot</span>
                        <span className="text-sm font-bold text-cyan-400">Level {selectedStudent.subLevels?.VisionBot || 1}</span>
                      </div>
                      <div className="border border-slate-800/80 p-2 rounded bg-slate-950/40">
                        <span className="text-[9px] text-slate-500 block">SolverBot</span>
                        <span className="text-sm font-bold text-cyan-400">Level {selectedStudent.subLevels?.SolverBot || 1}</span>
                      </div>
                    </div>
                  </div>

                  {/* Strategy details and qualitative analysis */}
                  <div className="space-y-2 text-xs">
                    <span className="text-[10px] font-mono text-slate-500 block uppercase tracking-wider">Qualitative Assessment Dossier</span>
                    <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-850 space-y-1.5 leading-normal">
                      <div>
                        <span className="text-slate-500 font-mono text-[10px] block">Cognitive Strategy Class</span>
                        <span className="text-emerald-400 font-bold text-sm block">{selectedStudent.strategy}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 font-mono text-[10px] block">Assigned Recommendation</span>
                        <span className="text-slate-200 font-semibold">{selectedStudent.recommendations}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono mt-1 border-t border-slate-800 pt-1.5">
                        Automatic routing flag active. Educational curriculum adapted dynamically to the above cognitive profiles.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Pilot cohort list */}
            <div className="space-y-3">
              <span className="text-[10px] font-mono text-slate-500 block uppercase tracking-widest font-bold">SIMULATED PILOT STUDY COHORT (30-50 Target Bracket) - CLICK ANY PROFILE TO MEASURE</span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {cohortStudents.map((s) => (
                  <div 
                    key={s.id} 
                    onClick={() => setSelectedStudent(s)}
                    className={`bg-slate-950/80 border p-4 rounded-xl flex flex-col justify-between space-y-3 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg ${
                      selectedStudent?.id === s.id 
                        ? 'border-cyan-500 shadow-cyan-500/10' 
                        : 'border-slate-850 hover:border-cyan-500/40'
                    }`}
                  >
                    <div className="flex justify-between items-start border-b border-slate-900 pb-2">
                      <div>
                        <h4 className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                          {s.name}
                          {selectedStudent?.id === s.id && <Eye className="w-3.5 h-3.5 text-cyan-400" />}
                        </h4>
                        <span className="text-[10px] font-mono text-slate-500">{s.id}</span>
                      </div>
                      <span className="text-xs font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                        {s.accuracy} Acc
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-[11px] font-mono text-slate-400 leading-normal">
                      <div>
                        <span className="text-slate-500 block text-[9px] uppercase">Avg Speed</span>
                        <span>{s.speed}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[9px] uppercase">Persistence</span>
                        <span>{s.persistence}%</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[9px] uppercase">Hints Dep</span>
                        <span>{s.hints}</span>
                      </div>
                    </div>

                    <div className="text-[11px] font-mono text-slate-400 border-t border-slate-900 pt-2 flex justify-between">
                      <span>Strategy: <span className="text-emerald-400 font-bold">{s.strategy}</span></span>
                      <span className="text-rose-400 font-semibold">{s.recommendations}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      )}

      {/* --- PILOT DATASET EXPLORER (MIGRATED FOR ADMINS) --- */}
      {activeSubTab === 'pilot-dataset' && (
        <div className="space-y-6 relative z-10 animate-fade-in">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-5">
            <div>
              <span className="text-[10px] font-mono font-bold text-rose-400 uppercase tracking-widest block">Verification Matrix & Pilot Dataset</span>
              <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                <Clipboard className="w-5 h-5 text-rose-400" />
                Pilot Dataset Generator & Simulator
              </h3>
              <p className="text-xs text-slate-400">
                Configure Gq assessment pilot parameters to simulate 30-50 high-school student profiles, events pipelines, and score matrices.
              </p>
            </div>

            {/* Parameter configuration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-950 p-4 border border-slate-850 rounded-xl">
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono text-slate-500 uppercase block">Sample Student Count</label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="30"
                    max="50"
                    value={sampleSize}
                    onChange={(e) => setSampleSize(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-900 appearance-none rounded accent-rose-500"
                  />
                  <span className="text-xs font-mono font-bold text-rose-400">{sampleSize}</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-mono text-slate-500 uppercase block">Grade Level Pool</label>
                <select
                  value={gradeRange}
                  onChange={(e) => setGradeRange(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs focus:outline-none"
                >
                  <option value="Grade 11-12">Grade 11-12 (Standard Gq Cohort)</option>
                  <option value="Grade 9-10">Grade 9-10 (Baseline Selection)</option>
                  <option value="Undergraduates">Undergraduates (Advanced Benchmark)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-mono text-slate-500 uppercase block">Adaptive Duration Limit</label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="15"
                    max="45"
                    value={pilotDuration}
                    onChange={(e) => setPilotDuration(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-900 appearance-none rounded accent-rose-500"
                  />
                  <span className="text-xs font-mono font-bold text-rose-400">{pilotDuration}m</span>
                </div>
              </div>
            </div>

            {/* Multi-Table selection */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-3 gap-4">
              <div className="flex flex-wrap gap-1 bg-slate-950 p-1 border border-slate-850 rounded">
                {[
                  { id: 'student', label: 'Student Table' },
                  { id: 'session', label: 'Session Table' },
                  { id: 'event', label: 'Event Table' },
                  { id: 'score', label: 'Score Table' },
                  { id: 'analytics', label: 'Analytics Table' },
                ].map((table) => (
                  <button
                    key={table.id}
                    onClick={() => setActiveDatasetTab(table.id as any)}
                    className={`px-3 py-1 text-xs rounded transition uppercase font-mono ${
                      activeDatasetTab === table.id
                        ? 'bg-rose-500/20 text-rose-300 font-bold border border-rose-500/20'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {table.label}
                  </button>
                ))}
              </div>

              <div className="flex gap-2 w-full md:w-auto">
                <input
                  type="text"
                  placeholder="Search dataset..."
                  value={pilotSearch}
                  onChange={(e) => setPilotSearch(e.target.value)}
                  className="bg-slate-950 border border-slate-800 px-3 py-1 text-xs rounded focus:outline-none w-full md:w-36 text-slate-300 animate-pulse focus:animate-none"
                />
                <button
                  onClick={downloadDatasetCSV}
                  className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-slate-950 font-mono font-bold text-xs uppercase rounded flex items-center gap-1.5 transition"
                >
                  <Download className="w-3.5 h-3.5" /> Export CSV
                </button>
              </div>
            </div>

            {/* Interactive Data Table viewer */}
            <div className="bg-slate-950 border border-slate-850 rounded-xl overflow-x-auto">
              <table className="w-full text-left font-mono text-[11px] text-slate-300 whitespace-nowrap">
                <thead className="bg-slate-900 border-b border-slate-800 text-[10px] text-slate-500">
                  <tr>
                    {Object.keys(currentDataset()[0] || {}).map((header) => (
                      <th key={header} className="p-3 uppercase">{header.replace('_', ' ')}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredData.slice(0, 15).map((row: any, idx: number) => (
                    <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/40">
                      {Object.values(row).map((val: any, cellIdx: number) => (
                        <td key={cellIdx} className="p-3">
                          {typeof val === 'boolean' ? (
                            <span className={`px-1.5 py-0.5 rounded text-[10px] ${val ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                              {String(val).toUpperCase()}
                            </span>
                          ) : (
                            String(val)
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredData.length > 15 && (
                <div className="p-2.5 text-center text-slate-500 text-[10px] bg-slate-900/20 border-t border-slate-900">
                  Truncated for viewport clarity: displaying 15 out of {filteredData.length} records. Download CSV to access full pilot database dataset.
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {/* Footer statistics */}
      <div className="border-t border-slate-800 pt-4 mt-6 flex justify-between items-center text-xs text-slate-500 font-mono relative z-10">
        <span>MentiScope Admin Suite v3.5</span>
        <span>Secure Telemetry Feed Active</span>
      </div>
    </div>
  );
};
