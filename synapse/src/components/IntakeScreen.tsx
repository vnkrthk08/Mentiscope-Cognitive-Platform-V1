import React, { useState } from 'react';
import { StudentProfile } from '../types';
import { useAssessment } from '../context/AssessmentContext';
import { 
  User, 
  Fingerprint, 
  Award, 
  Calendar, 
  School, 
  Zap, 
  ShieldCheck, 
  Monitor, 
  Lock,
  ChevronDown
} from 'lucide-react';

export const IntakeScreen: React.FC = () => {
  const { handleInitializeIdentity, logEvent } = useAssessment();
  const [fullName, setFullName] = useState('');
  const [studentId, setStudentId] = useState('');
  const [academy, setAcademy] = useState('');
  const [age, setAge] = useState(18);
  const [tier, setTier] = useState<'Novice' | 'Adept' | 'Specialist'>('Adept');
  const [role, setRole] = useState<'user' | 'admin'>('user');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !studentId.trim() || !academy.trim()) {
      setErrorMsg('Full identity vector, Student ID, and Academy designation are required.');
      logEvent('Identity initialization failed', 'ERROR', 'User attempted submit with missing fields', { studentId });
      return;
    }

    const profile: StudentProfile = {
      studentId: studentId.trim().toUpperCase(),
      fullName: fullName.trim(),
      age,
      tier,
      academy: academy.trim(),
      xp: 2450,
      level: 1,
      role,
      completedNodes: [],
    };

    logEvent('Neural Identity Sync Complete', 'SUCCESS', `Initialized ${fullName} from ${academy} (Tier: ${tier}, Role: ${role})`, profile);
    handleInitializeIdentity(profile);
  };

  return (
    <div className="min-h-[85vh] w-full flex items-center justify-center relative overflow-hidden font-mono text-slate-100 py-6">
      
      {/* LEFT DECORATIVE VERTICAL BAR matching Screenshot 2 */}
      <div className="hidden lg:flex flex-col items-center justify-between absolute left-0 top-1/2 -translate-y-1/2 h-4/5 text-[10px] text-slate-600 select-none pointer-events-none tracking-[0.2em]">
        <div className="flex items-center gap-4 origin-left -rotate-90 translate-y-32">
          <span>DATA STREAM CONNECTIVITY:</span>
          <span className="text-emerald-500 font-bold">STABLE</span>
          <div className="w-16 h-[1px] bg-slate-800"></div>
        </div>
        <div className="flex items-center gap-4 origin-left -rotate-90 -translate-y-20">
          <span>SUB-NEURAL PROTOCOL:</span>
          <span className="text-cyan-500 font-bold">ACTIVE</span>
          <div className="w-16 h-[1px] bg-slate-800"></div>
        </div>
      </div>

      {/* RIGHT DECORATIVE VERTICAL BAR matching Screenshot 2 */}
      <div className="hidden lg:flex flex-col items-center justify-between absolute right-0 top-1/2 -translate-y-1/2 h-4/5 text-[10px] text-slate-600 select-none pointer-events-none tracking-[0.2em]">
        <div className="flex items-center gap-4 origin-right rotate-90 -translate-y-32">
          <span>IDENTITY CONSTRUCTION MODE</span>
          <div className="w-16 h-[1px] bg-slate-800"></div>
        </div>
        <div className="flex items-center gap-4 origin-right rotate-90 translate-y-20">
          <span>SESSION REF:</span>
          <span className="text-cyan-400 font-bold">SYNAPSE-99-ALPHA</span>
          <div className="w-16 h-[1px] bg-slate-800"></div>
        </div>
      </div>

      {/* Main Content Flow */}
      <div className="w-full max-w-xl mx-auto flex flex-col items-center space-y-8 z-10">
        
        {/* Header Block matching Screenshot 2 */}
        <div className="text-center w-full space-y-4">
          <div className="flex items-center justify-center gap-4 text-[10px] font-bold text-cyan-400 tracking-[0.3em] uppercase">
            <div className="h-[1px] w-8 bg-cyan-500/30"></div>
            <span>PROTOCOL START</span>
            <div className="h-[1px] w-8 bg-cyan-500/30"></div>
          </div>

          <h2 className="text-4xl md:text-5xl font-black font-space tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-light-blue-200 to-white drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]">
            Initialize Identity
          </h2>

          <p className="text-[9px] text-slate-500 tracking-[0.15em] font-bold uppercase">
            AUTH_SEQUENCE: VERIFYING_SYNAPSE_CONNECTION
          </p>
        </div>

        {/* Tactical Central Form Card matching Screenshot 2 */}
        <form 
          onSubmit={handleSubmit} 
          className="w-full bg-[#0a1224]/50 border border-slate-800/80 rounded-2xl p-6 md:p-8 space-y-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)] relative overflow-hidden backdrop-blur-sm"
        >
          {/* Accent lighting strip */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent"></div>
          {/* Subtle form background glow */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

          {/* 1. STUDENT_ID */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
              STUDENT_ID
            </label>
            <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
              <Fingerprint className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
              <input
                type="text"
                required
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="Enter Student ID"
                className="bg-transparent text-sm font-bold text-slate-200 focus:outline-none w-full tracking-wider"
              />
            </div>
          </div>

          {/* 2. DESIGNATION_NAME */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
              DESIGNATION_NAME
            </label>
            <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
              <User className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  if (errorMsg) setErrorMsg('');
                }}
                placeholder="OPERATIVE_FULL_NAME"
                className="bg-transparent text-sm font-bold text-slate-200 placeholder-slate-700 focus:outline-none w-full tracking-wide"
              />
            </div>
            {errorMsg && (
              <p className="text-rose-400 text-[10px] font-bold uppercase tracking-wider mt-1">
                !! {errorMsg}
              </p>
            )}
          </div>

          {/* 3. TEMPORAL_AGE & TIER_LEVEL Row */}
          <div className="grid grid-cols-2 gap-4">
            
            {/* Left Column: Temporal Age */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
                TEMPORAL_AGE
              </label>
              <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
                <Calendar className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
                <input
                  type="number"
                  min="12"
                  max="45"
                  value={age || ''}
                  onChange={(e) => {
                    setAge(Number(e.target.value));
                    logEvent('Age adjusted', 'INFO', `Operative age set to ${e.target.value}`);
                  }}
                  placeholder="00"
                  className="bg-transparent text-sm font-bold text-slate-200 placeholder-slate-700 focus:outline-none w-full tracking-wide"
                />
              </div>
            </div>

            {/* Right Column: Tier Level */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
                TIER_LEVEL
              </label>
              <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
                <Award className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
                <select
                  value={tier}
                  onChange={(e) => {
                    const selected = e.target.value as 'Novice' | 'Adept' | 'Specialist';
                    setTier(selected);
                    logEvent('Cognition level calibrated', 'INFO', `Tier selected: ${selected}`);
                  }}
                  className="bg-transparent text-xs font-bold text-slate-200 focus:outline-none w-full appearance-none pr-6 cursor-pointer tracking-wide"
                >
                  <option value="Novice" className="bg-[#070b13] text-slate-300">K-12 / NOVICE</option>
                  <option value="Adept" className="bg-[#070b13] text-slate-300">K-12 / ADEPT</option>
                  <option value="Specialist" className="bg-[#070b13] text-slate-300">GRAD / SPECIALIST</option>
                </select>
                <ChevronDown className="w-4 h-4 text-slate-500 absolute right-4 pointer-events-none" />
              </div>
            </div>

          </div>

          {/* 4. ACADEMY_SOURCE */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
              ACADEMY_SOURCE
            </label>
            <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
              <School className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
              <input
                type="text"
                required
                value={academy}
                onChange={(e) => setAcademy(e.target.value)}
                placeholder="Enter College Name"
                className="bg-transparent text-sm font-bold text-slate-200 focus:outline-none w-full tracking-wider"
              />
            </div>
          </div>

          {/* SYSTEM ACCESS ROLE */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] block">
              SYSTEM_ACCESS_ROLE
            </label>
            <div className="relative flex items-center bg-[#070b13]/80 border border-slate-900/80 rounded-xl px-4 py-3.5 focus-within:border-cyan-500/40 transition">
              <ShieldCheck className="w-5 h-5 text-cyan-500/60 mr-3 flex-shrink-0" />
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as 'user' | 'admin')}
                className="bg-transparent text-xs font-bold text-slate-200 focus:outline-none w-full appearance-none pr-6 cursor-pointer tracking-wide"
              >
                <option value="user" className="bg-[#070b13] text-slate-300">STANDARD OPERATIVE</option>
                <option value="admin" className="bg-[#070b13] text-slate-300">SYSTEM ADMINISTRATOR</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-500 absolute right-4 pointer-events-none" />
            </div>
          </div>

          {/* 5. CONSTRUCT BUTTON with Dashed Cyan Glow border matching Screenshot 2 */}
          <div className="pt-4">
            <div className="p-1 rounded-xl border-2 border-dashed border-cyan-400/40 hover:border-cyan-400 transition duration-300 shadow-[0_0_15px_rgba(34,211,238,0.1)] hover:shadow-[0_0_20px_rgba(34,211,238,0.2)]">
              <button
                type="submit"
                className="w-full py-4 bg-[#0a1224] text-slate-200 hover:text-white font-black uppercase tracking-[0.25em] rounded-lg transition duration-200 flex items-center justify-center gap-3 text-xs"
              >
                <span>CONSTRUCT</span>
                <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />
              </button>
            </div>
          </div>

        </form>

        {/* Footer Pill & Custom Indicators matching Screenshot 2 */}
        <div className="flex flex-col items-center space-y-4">
          
          {/* Status Badge Pill */}
          <div className="flex items-center gap-2 px-4 py-1.5 bg-slate-900/60 border border-slate-800 rounded-full text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
            <span>Gq: UNINITIALIZED</span>
            <span className="text-slate-600 font-normal">|</span>
            <span className="text-slate-500 flex items-center gap-1">
              ⚙️ KERNEL: v.99.1-BETA
            </span>
          </div>

          {/* Small tactile square buttons with icons */}
          <div className="flex items-center gap-2.5">
            <button 
              type="button"
              className="w-9 h-9 bg-slate-900/30 hover:bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-300 transition"
              title="Secure Firewall"
            >
              <Lock className="w-4 h-4 text-cyan-500/60" />
            </button>
            <button 
              type="button"
              className="w-9 h-9 bg-slate-900/30 hover:bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-300 transition"
              title="Monitor Matrix Link"
            >
              <Monitor className="w-4 h-4 text-cyan-500/60" />
            </button>
            <button 
              type="button"
              className="w-9 h-9 bg-slate-900/30 hover:bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-300 transition"
              title="Operative Configuration"
            >
              <User className="w-4 h-4 text-cyan-500/60" />
            </button>
          </div>

        </div>

      </div>

    </div>
  );
};
