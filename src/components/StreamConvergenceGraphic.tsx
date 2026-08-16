import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Plus, 
  Settings2, 
  Scale, 
  TrendingUp, 
  FileText, 
  CheckCircle2,
  Sparkles,
  ArrowRight
} from "lucide-react";

interface StreamItem {
  id: string;
  name: string;
  reportName: string;
  icon: React.ElementType;
  matchScore: number;
  color: string;
  borderColor: string;
  bgActive: string;
  bgPill: string;
  textGlow: string;
  dotColor: string;
  yPos: number;
  curvePath: string;
}

const STREAMS: StreamItem[] = [
  {
    id: "medicine",
    name: "Medicine",
    reportName: "Medical & Health Sciences",
    icon: Plus,
    matchScore: 92,
    color: "#10b981", // Emerald
    borderColor: "border-emerald-500/80 hover:border-emerald-400",
    bgActive: "bg-emerald-950/70 border-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.35)]",
    bgPill: "bg-emerald-950/30",
    textGlow: "text-emerald-300",
    dotColor: "bg-emerald-400 shadow-[0_0_10px_#10b981]",
    yPos: 24,
    curvePath: "M 0 24 C 70 24, 110 106, 160 106"
  },
  {
    id: "engineering",
    name: "Engineering",
    reportName: "Engineering & Tech",
    icon: Settings2,
    matchScore: 94,
    color: "#38bdf8", // Sky blue / Cyan
    borderColor: "border-cyan-500/80 hover:border-cyan-400",
    bgActive: "bg-cyan-950/70 border-cyan-400 shadow-[0_0_20px_rgba(56,189,248,0.35)]",
    bgPill: "bg-cyan-950/30",
    textGlow: "text-cyan-300",
    dotColor: "bg-cyan-400 shadow-[0_0_10px_#38bdf8]",
    yPos: 78,
    curvePath: "M 0 78 C 60 78, 110 106, 160 106"
  },
  {
    id: "law",
    name: "Law",
    reportName: "Legal Studies & Policy",
    icon: Scale,
    matchScore: 89,
    color: "#f59e0b", // Amber
    borderColor: "border-amber-500/80 hover:border-amber-400",
    bgActive: "bg-amber-950/70 border-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.35)]",
    bgPill: "bg-amber-950/30",
    textGlow: "text-amber-300",
    dotColor: "bg-amber-400 shadow-[0_0_10px_#f59e0b]",
    yPos: 134,
    curvePath: "M 0 134 C 60 134, 110 106, 160 106"
  },
  {
    id: "commerce",
    name: "Commerce & Arts",
    reportName: "Commerce, Finance & Arts",
    icon: TrendingUp,
    matchScore: 91,
    color: "#a855f7", // Purple
    borderColor: "border-purple-500/80 hover:border-purple-400",
    bgActive: "bg-purple-950/70 border-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.35)]",
    bgPill: "bg-purple-950/30",
    textGlow: "text-purple-300",
    dotColor: "bg-purple-400 shadow-[0_0_10px_#a855f7]",
    yPos: 190,
    curvePath: "M 0 190 C 70 190, 110 106, 160 106"
  }
];

export default function StreamConvergenceGraphic() {
  const [activeStreamId, setActiveStreamId] = useState<string>("engineering");
  const [isAutoCycling, setIsAutoCycling] = useState<boolean>(true);

  // Auto-cycle through streams gently if user is not actively clicking
  useEffect(() => {
    if (!isAutoCycling) return;
    const interval = setInterval(() => {
      setActiveStreamId((prev) => {
        const currentIndex = STREAMS.findIndex((s) => s.id === prev);
        const nextIndex = (currentIndex + 1) % STREAMS.length;
        return STREAMS[nextIndex].id;
      });
    }, 4000);

    return () => clearInterval(interval);
  }, [isAutoCycling]);

  const activeStream = STREAMS.find((s) => s.id === activeStreamId) || STREAMS[1];

  const handleSelectStream = (id: string) => {
    setIsAutoCycling(false);
    setActiveStreamId(id);
  };

  return (
    <div className="w-full relative rounded-3xl border border-slate-800/80 bg-[#070c18]/95 p-5 sm:p-7 backdrop-blur-2xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.7)] overflow-hidden transition-all duration-300">
      
      {/* Background ambient radial glow */}
      <div 
        className="absolute inset-0 opacity-20 pointer-events-none transition-all duration-700 blur-3xl"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${activeStream.color}40, transparent 70%)`
        }}
      />

      {/* Grid container: Left Pills -> Center Curves -> Right Report Card */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 items-center gap-4 lg:gap-2">
        
        {/* Left Column: 4 Stream Pills */}
        <div className="lg:col-span-4 flex flex-col gap-3 justify-center">
          {STREAMS.map((stream) => {
            const Icon = stream.icon;
            const isSelected = stream.id === activeStreamId;

            return (
              <motion.button
                key={stream.id}
                type="button"
                onClick={() => handleSelectStream(stream.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`group relative flex items-center justify-between rounded-2xl border-2 px-4 py-2.5 sm:py-3 transition-all duration-300 text-left cursor-pointer select-none ${
                  isSelected 
                    ? stream.bgActive
                    : `border-slate-800 ${stream.bgPill} hover:border-slate-700`
                }`}
              >
                <div className="flex items-center gap-3">
                  <div 
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl transition-all duration-300"
                    style={{
                      backgroundColor: isSelected ? `${stream.color}25` : `${stream.color}15`,
                      color: stream.color,
                      border: `1px solid ${stream.color}${isSelected ? "80" : "30"}`
                    }}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className={`text-sm sm:text-base font-extrabold tracking-tight transition-colors ${
                    isSelected ? "text-white" : "text-slate-200 group-hover:text-white"
                  }`}>
                    {stream.name}
                  </span>
                </div>

                {/* Right edge connector dot */}
                <div 
                  className={`h-2.5 w-2.5 rounded-full transition-all duration-300 ${
                    isSelected ? stream.dotColor : "bg-slate-700 opacity-60"
                  }`} 
                />
              </motion.button>
            );
          })}
        </div>

        {/* Center Column: Smooth Convergence Curves SVG & Focal Node */}
        <div className="lg:col-span-3 flex items-center justify-center relative my-4 lg:my-0 h-44 lg:h-56">
          <svg 
            viewBox="0 0 220 212" 
            className="w-full h-full max-h-[220px] overflow-visible"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <radialGradient id="focalGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
                <stop offset="35%" stopColor={activeStream.color} stopOpacity="0.8" />
                <stop offset="100%" stopColor={activeStream.color} stopOpacity="0" />
              </radialGradient>
            </defs>

            {/* Background static connecting curves */}
            {STREAMS.map((stream) => {
              const isSelected = stream.id === activeStreamId;
              return (
                <g key={stream.id}>
                  {/* Subtle blur trail */}
                  <path
                    d={stream.curvePath}
                    stroke={stream.color}
                    strokeWidth={isSelected ? "3.5" : "1.5"}
                    strokeOpacity={isSelected ? "0.9" : "0.25"}
                    fill="none"
                    filter={isSelected ? "url(#glow)" : undefined}
                    className="transition-all duration-500"
                  />
                  {/* Active animated pulse particle moving along curve */}
                  <circle r={isSelected ? "4.5" : "2.5"} fill={isSelected ? "#ffffff" : stream.color} opacity={isSelected ? 1 : 0.6}>
                    <animateMotion
                      path={stream.curvePath}
                      dur={isSelected ? "1.8s" : "3.2s"}
                      repeatCount="indefinite"
                      keyPoints="0;1"
                      keyTimes="0;1"
                    />
                  </circle>
                </g>
              );
            })}

            {/* Central Convergence Focal Orb */}
            <g transform="translate(160, 106)">
              {/* Outer pulsing energy halo */}
              <circle r="36" fill={activeStream.color} opacity="0.08" className="animate-pulse" />
              <circle r="22" fill={activeStream.color} opacity="0.18" />
              <circle r="12" fill={activeStream.color} opacity="0.4" />
              {/* Glowing white/color core */}
              <circle r="6.5" fill="#ffffff" filter="url(#glow)" />
              <circle r="3.5" fill={activeStream.color} />
            </g>

            {/* Forward Arrow Indicator to Report Card */}
            <polygon
              points="198,99 212,106 198,113"
              fill="#38bdf8"
              opacity="0.9"
              filter="url(#glow)"
              className="animate-pulse"
            />
          </svg>
        </div>

        {/* Right Column: Stream Fit Report Card */}
        <div className="lg:col-span-5 flex flex-col justify-center">
          <div className="rounded-2xl border border-slate-800/90 bg-[#091122]/90 p-4 sm:p-5 space-y-4 shadow-xl relative overflow-hidden">
            
            {/* Header: File Icon + Title */}
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 shadow-sm">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm sm:text-base font-extrabold text-white tracking-tight">
                  Stream Fit Report
                </h3>
                <p className="text-[11px] text-slate-400 font-sans">
                  Find your potential career fit
                </p>
              </div>
            </div>

            {/* Best Matched Stream Highlight Box */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeStream.id}
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.98 }}
                transition={{ duration: 0.25 }}
                className="rounded-2xl border-2 p-3.5 sm:p-4 relative transition-all duration-300"
                style={{
                  borderColor: `${activeStream.color}90`,
                  backgroundColor: `${activeStream.color}10`,
                  boxShadow: `0 0 25px ${activeStream.color}20`
                }}
              >
                <span className="block text-[10px] font-mono font-bold tracking-widest text-slate-400 uppercase mb-1">
                  BEST MATCHED STREAM
                </span>

                <div className="flex items-center justify-between gap-2 mt-1">
                  <span className="text-base sm:text-lg font-black text-white tracking-tight">
                    {activeStream.reportName}
                  </span>

                  <div 
                    className="flex items-center justify-center px-3 py-1 rounded-xl text-xs sm:text-sm font-black text-white shadow-md shrink-0"
                    style={{
                      backgroundColor: activeStream.color,
                      boxShadow: `0 0 15px ${activeStream.color}60`
                    }}
                  >
                    {activeStream.matchScore}%
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Bottom Status Guarantee */}
            <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/30 px-3.5 py-2.5 flex items-center gap-2.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              <span className="text-xs font-bold text-slate-200 font-sans">
                Many paths, one clear answer.
              </span>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
