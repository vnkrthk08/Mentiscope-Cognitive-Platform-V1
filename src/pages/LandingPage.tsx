import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { MODULE_CONFIGS, NINE_PILLARS_CONFIG } from "../config/moduleConfig";
import Footer from "../components/Footer";
import StreamConvergenceGraphic from "../components/StreamConvergenceGraphic";
import { motion, AnimatePresence, useScroll, useSpring } from "motion/react";
import {
  Brain,
  Award,
  Sparkles,
  ArrowRight,
  ChevronRight,
  ShieldCheck,
  Compass,
  Mail,
  Phone,
  MapPin,
  CheckCircle,
  FileText,
  BookOpen,
  GraduationCap,
  Briefcase,
  Trophy,
  UserPlus,
  ClipboardList,
  Activity,
  BarChart4,
  Hourglass,
  Clock,
  Play,
  Cpu,
  Calculator,
  Box,
  Zap,
  Eye,
  UserCheck,
  ShieldAlert,
  Headphones,
  Layers,
  FlaskConical,
  Target,
  X,
  Info,
  ExternalLink
} from "lucide-react";

import { User, UserRole } from "../types";
import { AuthService } from "../services/auth/AuthService";

/* ---------- 10 Modules Bento Tiers (2 Featured + 4 Cognitive + 4 Specialized) ---------- */
const FEATURED_MODULES = [
  NINE_PILLARS_CONFIG.find(m => m.id === "gf") || NINE_PILLARS_CONFIG[0],
  NINE_PILLARS_CONFIG.find(m => m.id === "riasec") || NINE_PILLARS_CONFIG[7],
];

const CORE_COGNITIVE_MODULES = [
  NINE_PILLARS_CONFIG.find(m => m.id === "gq") || NINE_PILLARS_CONFIG[2],
  NINE_PILLARS_CONFIG.find(m => m.id === "gv") || NINE_PILLARS_CONFIG[3],
  NINE_PILLARS_CONFIG.find(m => m.id === "gsm") || NINE_PILLARS_CONFIG[4],
  NINE_PILLARS_CONFIG.find(m => m.id === "gs") || NINE_PILLARS_CONFIG[5],
];

const SPECIALIZED_MODULES = [
  NINE_PILLARS_CONFIG.find(m => m.id === "attention") || NINE_PILLARS_CONFIG[6],
  NINE_PILLARS_CONFIG.find(m => m.id === "gc") || NINE_PILLARS_CONFIG[1],
  NINE_PILLARS_CONFIG.find(m => m.id === "emotional_regulation") || NINE_PILLARS_CONFIG[8],
  NINE_PILLARS_CONFIG.find(m => m.id === "auditory_verbal") || NINE_PILLARS_CONFIG[9],
];

const CONSTRUCT_META: Record<string, {
  shortCode: string;
  chcLabel: string;
  categoryTag: string;
  benchmarkMetric: string;
}> = {
  gf: {
    shortCode: "Gf",
    chcLabel: "Fluid Reasoning",
    categoryTag: "CHC Core",
    benchmarkMetric: "Inductive Rule Discovery",
  },
  gc: {
    shortCode: "Gc",
    chcLabel: "Crystallized Knowledge",
    categoryTag: "CHC Core",
    benchmarkMetric: "Knowledge & Comprehension",
  },
  gq: {
    shortCode: "Gq",
    chcLabel: "Quantitative Ability",
    categoryTag: "CHC Core",
    benchmarkMetric: "Adaptive Math Decision Arena",
  },
  gv: {
    shortCode: "Gv",
    chcLabel: "Visual-Spatial Processing",
    categoryTag: "Spatial Synthesis",
    benchmarkMetric: "2D/3D Mental Rotation",
  },
  gsm: {
    shortCode: "Gsm",
    chcLabel: "Short-Term Working Memory",
    categoryTag: "CHC Core",
    benchmarkMetric: "Active Retention Span",
  },
  gs: {
    shortCode: "Gs",
    chcLabel: "Perceptual Speed",
    categoryTag: "Speed & Fluency",
    benchmarkMetric: "Symbol Matrix Matching",
  },
  attention: {
    shortCode: "Attn",
    chcLabel: "Inhibitory Control",
    categoryTag: "Cognitive Control",
    benchmarkMetric: "Adaptive Shape Stroop",
  },
  riasec: {
    shortCode: "Holland",
    chcLabel: "Vocational Profiling",
    categoryTag: "RIASEC Model",
    benchmarkMetric: "6 Holland Dimensions",
  },
  emotional_regulation: {
    shortCode: "EQ",
    chcLabel: "Affective Resilience",
    categoryTag: "Stress Dispatch",
    benchmarkMetric: "Crisis Simulation Index",
  },
  auditory_verbal: {
    shortCode: "Aud-V",
    chcLabel: "Auditory & Verbal Cognition",
    categoryTag: "Dual Domain",
    benchmarkMetric: "Acoustic Comprehension",
  },
};

interface PillarColorTheme {
  borderHover: string;
  iconBg: string;
  badge: string;
  glowGradient: string;
  accentBar: string;
  lightShadow: string;
  textAccent: string;
}

const PILLAR_COLOR_THEMES: Record<string, PillarColorTheme> = {
  indigo: {
    borderHover: "hover:border-indigo-400/80 dark:hover:border-indigo-500/70",
    iconBg: "bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/60 shadow-indigo-500/10",
    badge: "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300 border-indigo-200/80 dark:border-indigo-800/60",
    glowGradient: "from-indigo-500/15 via-indigo-500/5 to-transparent",
    accentBar: "from-indigo-500 to-blue-600",
    lightShadow: "hover:shadow-indigo-500/10 dark:hover:shadow-indigo-500/5",
    textAccent: "text-indigo-600 dark:text-indigo-400",
  },
  blue: {
    borderHover: "hover:border-blue-400/80 dark:hover:border-blue-500/70",
    iconBg: "bg-blue-50 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/60 shadow-blue-500/10",
    badge: "bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 border-blue-200/80 dark:border-blue-800/60",
    glowGradient: "from-blue-500/15 via-blue-500/5 to-transparent",
    accentBar: "from-blue-500 to-indigo-600",
    lightShadow: "hover:shadow-blue-500/10 dark:hover:shadow-blue-500/5",
    textAccent: "text-blue-600 dark:text-blue-400",
  },
  emerald: {
    borderHover: "hover:border-emerald-400/80 dark:hover:border-emerald-500/70",
    iconBg: "bg-emerald-50 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/60 shadow-emerald-500/10",
    badge: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300 border-emerald-200/80 dark:border-emerald-800/60",
    glowGradient: "from-emerald-500/15 via-emerald-500/5 to-transparent",
    accentBar: "from-emerald-500 to-teal-600",
    lightShadow: "hover:shadow-emerald-500/10 dark:hover:shadow-emerald-500/5",
    textAccent: "text-emerald-600 dark:text-emerald-400",
  },
  cyan: {
    borderHover: "hover:border-cyan-400/80 dark:hover:border-cyan-500/70",
    iconBg: "bg-cyan-50 dark:bg-cyan-950/70 text-cyan-600 dark:text-cyan-400 border border-cyan-100 dark:border-cyan-900/60 shadow-cyan-500/10",
    badge: "bg-cyan-50 text-cyan-700 dark:bg-cyan-950/80 dark:text-cyan-300 border-cyan-200/80 dark:border-cyan-800/60",
    glowGradient: "from-cyan-500/15 via-cyan-500/5 to-transparent",
    accentBar: "from-cyan-500 to-blue-600",
    lightShadow: "hover:shadow-cyan-500/10 dark:hover:shadow-cyan-500/5",
    textAccent: "text-cyan-600 dark:text-cyan-400",
  },
  teal: {
    borderHover: "hover:border-teal-400/80 dark:hover:border-teal-500/70",
    iconBg: "bg-teal-50 dark:bg-teal-950/70 text-teal-600 dark:text-teal-400 border border-teal-100 dark:border-teal-900/60 shadow-teal-500/10",
    badge: "bg-teal-50 text-teal-700 dark:bg-teal-950/80 dark:text-teal-300 border-teal-200/80 dark:border-teal-800/60",
    glowGradient: "from-teal-500/15 via-teal-500/5 to-transparent",
    accentBar: "from-teal-500 to-emerald-600",
    lightShadow: "hover:shadow-teal-500/10 dark:hover:shadow-teal-500/5",
    textAccent: "text-teal-600 dark:text-teal-400",
  },
  amber: {
    borderHover: "hover:border-amber-400/80 dark:hover:border-amber-500/70",
    iconBg: "bg-amber-50 dark:bg-amber-950/70 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-900/60 shadow-amber-500/10",
    badge: "bg-amber-50 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 border-amber-200/80 dark:border-amber-800/60",
    glowGradient: "from-amber-500/15 via-amber-500/5 to-transparent",
    accentBar: "from-amber-500 to-orange-600",
    lightShadow: "hover:shadow-amber-500/10 dark:hover:shadow-amber-500/5",
    textAccent: "text-amber-600 dark:text-amber-400",
  },
  rose: {
    borderHover: "hover:border-rose-400/80 dark:hover:border-rose-500/70",
    iconBg: "bg-rose-50 dark:bg-rose-950/70 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/60 shadow-rose-500/10",
    badge: "bg-rose-50 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 border-rose-200/80 dark:border-rose-800/60",
    glowGradient: "from-rose-500/15 via-rose-500/5 to-transparent",
    accentBar: "from-rose-500 to-red-600",
    lightShadow: "hover:shadow-rose-500/10 dark:hover:shadow-rose-500/5",
    textAccent: "text-rose-600 dark:text-rose-400",
  },
  violet: {
    borderHover: "hover:border-violet-400/80 dark:hover:border-violet-500/70",
    iconBg: "bg-violet-50 dark:bg-violet-950/70 text-violet-600 dark:text-violet-400 border border-violet-100 dark:border-violet-900/60 shadow-violet-500/10",
    badge: "bg-violet-50 text-violet-700 dark:bg-violet-950/80 dark:text-violet-300 border-violet-200/80 dark:border-violet-800/60",
    glowGradient: "from-violet-500/15 via-violet-500/5 to-transparent",
    accentBar: "from-violet-500 to-purple-600",
    lightShadow: "hover:shadow-violet-500/10 dark:hover:shadow-violet-500/5",
    textAccent: "text-violet-600 dark:text-violet-400",
  },
  red: {
    borderHover: "hover:border-red-400/80 dark:hover:border-red-500/70",
    iconBg: "bg-red-50 dark:bg-red-950/70 text-red-600 dark:text-red-400 border border-red-100 dark:border-red-900/60 shadow-red-500/10",
    badge: "bg-red-50 text-red-700 dark:bg-red-950/80 dark:text-red-300 border-red-200/80 dark:border-red-800/60",
    glowGradient: "from-red-500/15 via-red-500/5 to-transparent",
    accentBar: "from-red-500 to-rose-600",
    lightShadow: "hover:shadow-red-500/10 dark:hover:shadow-red-500/5",
    textAccent: "text-red-600 dark:text-red-400",
  },
  purple: {
    borderHover: "hover:border-purple-400/80 dark:hover:border-purple-500/70",
    iconBg: "bg-purple-50 dark:bg-purple-950/70 text-purple-600 dark:text-purple-400 border border-purple-100 dark:border-purple-900/60 shadow-purple-500/10",
    badge: "bg-purple-50 text-purple-700 dark:bg-purple-950/80 dark:text-purple-300 border-purple-200/80 dark:border-purple-800/60",
    glowGradient: "from-purple-500/15 via-purple-500/5 to-transparent",
    accentBar: "from-purple-500 to-pink-600",
    lightShadow: "hover:shadow-purple-500/10 dark:hover:shadow-purple-500/5",
    textAccent: "text-purple-600 dark:text-purple-400",
  },
};

const MODULE_RESEARCH_DETAILS: Record<string, {
  streamRelevance: string;
  scientificBasis: string;
  normSample: string;
  sampleInsight: string;
}> = {
  gf: {
    streamRelevance: "High indicator for Engineering, Computer Science, and Data Science.",
    scientificBasis: "Cattell-Horn-Carroll (CHC) Fluid Reasoning index. Evaluates non-verbal abstract induction and deduction independent of prior schooling.",
    normSample: "Calibrated against secondary and higher secondary STEM cohorts.",
    sampleInsight: "Strong abstract pattern recognition correlates with computational and algorithmic problem-solving adaptability."
  },
  gc: {
    streamRelevance: "High indicator for Law, Journalism, Civil Services, and Humanities.",
    scientificBasis: "Cattell-Horn-Carroll (CHC) Crystallized Intelligence. Measures lexical depth, semantic reasoning, and contextual knowledge assimilation.",
    normSample: "Multi-domain contextual comprehension battery.",
    sampleInsight: "Predicts superior case analysis, structured debate, and contextual reading comprehension in professional environments."
  },
  gq: {
    streamRelevance: "Essential for STEM, Actuarial Science, Quantitative Finance, and Economics.",
    scientificBasis: "Quantitative Knowledge (Gq) with adaptive Item Response Theory (IRT) calibrated under strict latency constraints.",
    normSample: "Dynamic item bank with varying computational loads.",
    sampleInsight: "Measures numerical fluency and probabilistic estimation under high-speed decision constraints."
  },
  gv: {
    streamRelevance: "Critical for Architecture, Surgery/Medicine, Industrial Design, and Mechanical Engineering.",
    scientificBasis: "Visual Processing (Gv) spatial manipulation. Assesses mental rotation, multi-perspective synthesis, and coordinate tracking.",
    normSample: "3D perspective transformation and topological navigation tasks.",
    sampleInsight: "Essential for mentally visualizing complex spatial systems, surgical pathways, and physical structural mechanics."
  },
  gsm: {
    streamRelevance: "High predictor for Academic Rigor, Competitive Exams (JEE/NEET/UPSC), and Research.",
    scientificBasis: "Short-Term Working Memory (Gsm). Measures dual-stream retention and real-time buffer updating under cognitive distraction.",
    normSample: "Dynamic classroom scenario multi-item recall paradigms.",
    sampleInsight: "Buffers critical facts while actively processing secondary inputs without cognitive overload."
  },
  gs: {
    streamRelevance: "Crucial for Clinical Medicine, Aviation, Emergency Management, and Real-Time Trading.",
    scientificBasis: "Processing Speed (Gs). Assesses visual scanning efficiency, symbol discrimination, and decision latency without motor artifacts.",
    normSample: "High-frequency perceptual discrimination matrices.",
    sampleInsight: "Ensures rapid, high-accuracy decision making when time is of the essence."
  },
  attention: {
    streamRelevance: "Fundamental across all disciplines, particularly Complex Problem Solving and Analytical Research.",
    scientificBasis: "Selective Visual Attention & Inhibitory Control (Stroop & ASAT architecture). Gauges distractor suppression and focus maintenance.",
    normSample: "Dynamic perceptual distractor streams and Stroop interference.",
    sampleInsight: "Determines resilience against sensory distractions and sustained focus during extended analytical sessions."
  },
  riasec: {
    streamRelevance: "Holistic career alignment across Holland's 6 dimensions: Realistic, Investigative, Artistic, Social, Enterprising, and Conventional.",
    scientificBasis: "Holland RIASEC Hexagon psychometric taxonomy, integrated with behavioral simulation scenarios.",
    normSample: "Interactive day-in-the-life project simulation choices.",
    sampleInsight: "Maps personal vocational affinity to real-world career clusters, preventing stream-interest mismatch."
  },
  emotional_regulation: {
    streamRelevance: "High predictor for Leadership, Healthcare, Corporate Management, and High-Stakes Operations.",
    scientificBasis: "Affective Psychometrics & Stress Dispatch Resilience. Measures decision stability under simulated emergency scenarios.",
    normSample: "Dynamic simulated dispatch crises with conflicting urgency cues.",
    sampleInsight: "Evaluates emotional stability, preventing cognitive paralysis during high-stakes emergencies."
  },
  auditory_verbal: {
    streamRelevance: "High indicator for Clinical Medicine, Counseling, Legal Advocacy, Media, and International Relations.",
    scientificBasis: "Dual-Domain Auditory & Verbal processing. Measures phonological working memory, speech comprehension, and verbal delivery synthesis.",
    normSample: "50 real-time auditory dilemma simulations.",
    sampleInsight: "Combines listening comprehension with expressive verbal fluency for persuasive communication."
  }
};

interface LandingPageProps {
  user?: User | null;
  onNavigate?: (page: string, subPage?: string) => void;
}

export default function LandingPage({ user, onNavigate }: LandingPageProps) {
  const navigate = useNavigate();
  const currentUser = user !== undefined ? user : AuthService.getCurrentUser();

  const handleLoginOrDashboard = () => {
    if (currentUser) {
      const targetDashboard = currentUser.role === UserRole.SUPER_ADMIN ? "admin" : "dashboard";
      if (onNavigate) {
        onNavigate(targetDashboard);
      } else {
        navigate(currentUser.role === UserRole.SUPER_ADMIN ? "/admin" : "/dashboard");
      }
    } else {
      if (onNavigate) {
        onNavigate("auth", "student-login");
      } else {
        navigate("/login");
      }
    }
  };

  const scrollRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ container: scrollRef });
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30, restDelta: 0.001 });

  const [contactForm, setContactForm] = useState({ name: "", email: "", institution: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState<string>("home");
  const [selectedModuleId, setSelectedModuleId] = useState<string>("gq");
  const [inspectedModule, setInspectedModule] = useState<typeof NINE_PILLARS_CONFIG[0] | null>(null);

  // Hero Live Reaction Test Widget State
  const [reactionState, setReactionState] = useState<"idle" | "waiting" | "ready" | "result">("idle");
  const [reactionStartTime, setReactionStartTime] = useState<number>(0);
  const [reactionResultTime, setReactionResultTime] = useState<number | null>(null);
  const [reactionTimeoutId, setReactionTimeoutId] = useState<any>(null);

  const startReactionTest = () => {
    setReactionState("waiting");
    setReactionResultTime(null);
    const randomDelay = 1500 + Math.random() * 2000;
    const timeout = setTimeout(() => {
      setReactionState("ready");
      setReactionStartTime(Date.now());
    }, randomDelay);
    setReactionTimeoutId(timeout);
  };

  const handleReactionClick = () => {
    if (reactionState === "waiting") {
      if (reactionTimeoutId) clearTimeout(reactionTimeoutId);
      setReactionState("idle");
      alert("⚠️ Too early! Wait for the screen to turn GREEN before clicking.");
    } else if (reactionState === "ready") {
      const elapsed = Date.now() - reactionStartTime;
      setReactionResultTime(elapsed);
      setReactionState("result");
    } else {
      startReactionTest();
    }
  };

  const sections = ["home", "about", "audience", "modules", "workflow", "benefits", "contact"];

  useEffect(() => {
    const originalHash = window.location.hash.substring(1);
    
    // Always force the address bar to show #home
    window.history.replaceState(null, "", "#home");

    // Scroll to the original targeted section if it exists on load
    if (originalHash && originalHash !== "home" && sections.includes(originalHash)) {
      const el = document.getElementById(originalHash);
      if (el) {
        setTimeout(() => {
          el.scrollIntoView({ behavior: "smooth" });
          setActiveSection(originalHash);
        }, 100);
      }
    }

    const observerOptions = {
      root: document.getElementById("landing-scroll-container"),
      rootMargin: "0px",
      threshold: 0.4
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          setActiveSection((prev) => (prev !== id ? id : prev));
        }
      });
    }, observerOptions);

    sections.forEach((s) => {
      const el = document.getElementById(s);
      if (el) observer.observe(el);
    });

    return () => {
      sections.forEach((s) => {
        const el = document.getElementById(s);
        if (el) observer.unobserve(el);
      });
    };
  }, []);

  const handleDotClick = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
      setActiveSection(id);
      
      // Ensure hash stays #home even after clicking standard module dot indicators
      if (window.location.hash !== "#home") {
        window.history.replaceState(null, "", "#home");
      }
    }
  };

  const handleSubmitContact = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Institution inquiry submitted:", contactForm);
    setSubmitted(true);
    setContactForm({ name: "", email: "", institution: "", message: "" });
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <div className="relative bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300">
      
      {/* Top Animated Scroll Progress Bar */}
      <motion.div 
        style={{ scaleX }} 
        className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 via-cyan-400 to-indigo-600 z-[100] origin-left shadow-sm shadow-blue-500/50" 
      />

      {/* Floating Dot Indicator */}
      <div className="fixed right-6 top-1/2 z-50 -translate-y-1/2 space-y-4 hidden md:flex flex-col">
        {sections.map((sec) => (
          <button
            key={sec}
            onClick={() => handleDotClick(sec)}
            title={`Go to ${sec}`}
            className="group flex items-center justify-end gap-3 text-right focus:outline-none"
          >
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-505 dark:text-slate-400">
              {sec === "home" ? "Welcome" : sec === "audience" ? "For Whom" : sec === "benefits" ? "Why it works" : sec.charAt(0).toUpperCase() + sec.slice(1)}
            </span>
            <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${
              activeSection === sec
                ? "bg-blue-600 border-blue-600 scale-125 shadow-md shadow-blue-500/20"
                : "border-slate-350 dark:border-slate-700 bg-transparent hover:border-slate-500 dark:hover:border-slate-400"
            }`} />
          </button>
        ))}
      </div>

      {/* Continuous Smooth Scroll Container */}
      <div 
        ref={scrollRef}
        id="landing-scroll-container"
        className="h-[calc(100vh-5rem)] overflow-y-auto scroll-smooth"
      >
        
        {/* 1. Hero Section */}
        <section 
          id="home"
          className="relative overflow-hidden bg-white dark:bg-slate-950 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-12"
        >
          {/* Animated luxury background blobs */}
          <div className="absolute top-10 right-10 w-96 h-96 rounded-full bg-blue-500/10 dark:bg-blue-500/15 blur-3xl pointer-events-none animate-float" />
          <div className="absolute bottom-10 left-10 w-80 h-80 rounded-full bg-indigo-500/5 dark:bg-indigo-500/10 blur-3xl pointer-events-none animate-float delay-500" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(37,99,235,0.03),transparent_50%)] dark:bg-[radial-gradient(ellipse_at_top_right,rgba(37,99,235,0.12),transparent_50%)]" />

          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 w-full">
            <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12">
              
              {/* Left Column: Headline and Badges */}
              <motion.div 
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.7 }}
                className="lg:col-span-7 space-y-6"
              >
                {/* Stream Guidance Badge */}
                <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 dark:bg-blue-950/50 px-4 py-1.5 text-xs font-semibold text-blue-700 dark:text-blue-300 border border-blue-200/80 dark:border-blue-800/60 shadow-sm animate-scale-in">
                  <Compass className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0" />
                  <span>Find Your Right Stream — Before You Have To Choose</span>
                </div>
                
                <h1 className="font-sans text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl lg:text-6xl leading-[1.1] animate-fade-up delay-100">
                  Mentiscope <br />
                  <span className="gradient-text glow-text text-3xl sm:text-4xl lg:text-5xl font-bold block mt-2 pb-2 leading-tight">
                    Know your stream before you choose it
                  </span>
                </h1>
                
                <p className="max-w-xl text-base sm:text-lg text-slate-650 dark:text-slate-350 leading-relaxed animate-fade-up delay-200">
                  A 15-minute assessment based on how you actually solve problems - not what your relatives think you're good at. Get a clear recommendation across Medicine, Engineering, Law, and beyond.
                </p>

                {/* Incubator Partnership Card */}
                <div className="flex flex-wrap items-center gap-4 pt-2 animate-fade-up delay-300">
                  <div className="flex items-center gap-3 bg-white/40 dark:bg-slate-900/40 backdrop-blur-md px-4 py-2.5 rounded-xl border border-slate-200/60 dark:border-slate-800/80 shadow-sm hover:border-blue-300 dark:hover:border-blue-900/80 hover:shadow-md hover:shadow-blue-500/5 transition-all">
                    <img src="/logo.svg" alt="NIRMAAN Logo" className="h-10 w-auto object-contain filter dark:brightness-110" />
                    <div>
                      <p className="text-[9px] uppercase tracking-wider text-slate-400 font-bold leading-none">Incubated At</p>
                      <p className="text-xs font-extrabold text-slate-700 dark:text-slate-200 mt-1">The Pre-Incubator, NIRMAAN, IIT Madras</p>
                    </div>
                  </div>
                </div>
                
                {/* CTA Buttons */}
                <div className="flex flex-col gap-3.5 sm:flex-row sm:items-center animate-fade-up delay-400">
                  <button
                    onClick={handleLoginOrDashboard}
                    className="group flex items-center justify-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 px-6 py-3.5 text-base font-semibold text-white transition-all hover:shadow-lg hover:shadow-blue-500/30 active:scale-[0.98] animate-pulse-glow cursor-pointer"
                  >
                    <span>Start my assessment</span>
                    <ArrowRight className="h-4.5 w-4.5 group-hover:translate-x-1 transition-transform" />
                  </button>
                  <button
                    onClick={() => handleDotClick("modules")}
                    className="group flex items-center justify-center gap-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 px-6 py-3.5 text-base font-semibold text-slate-700 dark:text-slate-350 transition-all duration-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 hover:border-blue-500/30 dark:hover:border-blue-500/30 hover:text-blue-600 dark:hover:text-blue-400 hover:-translate-y-0.5 hover:shadow-md dark:hover:shadow-[0_8px_20px_-6px_rgba(59,130,246,0.12)] active:scale-[0.98] active:translate-y-0 cursor-pointer"
                  >
                    <span>See how it works</span>
                    <ChevronRight className="h-4.5 w-4.5 transition-transform duration-300 group-hover:rotate-90" />
                  </button>
                </div>

                {/* Trust Badges */}
                <div className="pt-6 border-t border-slate-100 dark:border-slate-900 flex flex-wrap items-center gap-6 text-xs text-slate-505 dark:text-slate-400 flex-row animate-fade-up delay-500">
                  <div className="flex items-center gap-1.5 font-semibold text-slate-600 dark:text-slate-350">
                    <Award className="h-4 w-4 text-emerald-500" />
                    <span>Incubated at IIT Madras</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-semibold text-slate-600 dark:text-slate-350">
                    <ShieldCheck className="h-4 w-4 text-indigo-500" />
                    <span>Scientifically Validated</span>
                  </div>
                </div>
              </motion.div>

              {/* Right Column: Visual Overview Card */}
              <motion.div 
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.7, delay: 0.2 }}
                className="lg:col-span-5 relative hidden lg:block"
              >
                {/* Background ambient glowing radial effects */}
                <div className="absolute -left-12 -top-12 -right-12 -bottom-12 bg-gradient-to-tr from-blue-600/10 to-indigo-600/15 blur-3xl rounded-full" />
                
                {/* Outer Glass Container */}
                <div className="bento-card relative p-6 space-y-5 border border-slate-200/80 dark:border-slate-800/80 shadow-2xl">
                  
                  {/* Top Widget Header */}
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-[11px] font-mono font-bold tracking-widest text-slate-500 dark:text-slate-400 uppercase">
                        Interactive Live Mini-Test
                      </span>
                    </div>
                    <span className="text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-0.5 rounded-full border border-blue-100 dark:border-blue-900/50">
                      Calibrate Your Reaction Time
                    </span>
                  </div>

                  {/* Reaction Test Interactive Box */}
                  <div 
                    onClick={handleReactionClick}
                    className={`cursor-pointer rounded-2xl p-6 text-center transition-all duration-300 spring-press border-2 flex flex-col items-center justify-center min-h-[160px] ${
                      reactionState === "idle" 
                        ? "bg-slate-50 dark:bg-slate-900/80 border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-500" 
                        : reactionState === "waiting"
                        ? "bg-amber-500/10 border-amber-500 text-amber-600 dark:text-amber-400 animate-pulse"
                        : reactionState === "ready"
                        ? "bg-emerald-500 text-white border-emerald-600 shadow-lg shadow-emerald-500/30 scale-105"
                        : "bg-blue-600 text-white border-blue-700 shadow-lg shadow-blue-500/30"
                    }`}
                  >
                    {reactionState === "idle" && (
                      <>
                        <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400 mb-2 animate-bounce" />
                        <h4 className="text-sm font-extrabold text-slate-900 dark:text-white">Click to Start Live Reaction Test</h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Test your visual reaction time right here</p>
                      </>
                    )}

                    {reactionState === "waiting" && (
                      <>
                        <Hourglass className="h-8 w-8 text-amber-500 animate-spin mb-2" />
                        <h4 className="text-base font-extrabold text-amber-600 dark:text-amber-400">Wait for GREEN...</h4>
                        <p className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-1">Do not click yet!</p>
                      </>
                    )}

                    {reactionState === "ready" && (
                      <>
                        <Sparkles className="h-9 w-9 text-white animate-spin-slow mb-1" />
                        <h4 className="text-xl font-black text-white tracking-tight uppercase">CLICK NOW!</h4>
                      </>
                    )}

                    {reactionState === "result" && reactionResultTime !== null && (
                      <>
                        <Trophy className="h-8 w-8 text-amber-300 mb-1" />
                        <h4 className="text-3xl font-black text-white tracking-tight">{reactionResultTime} ms</h4>
                        <p className="text-xs font-bold text-blue-100 mt-1">
                          {reactionResultTime < 200 
                            ? "Exceptional Processing Speed — Top 1% Percentile" 
                            : reactionResultTime < 250 
                            ? "Elevated Processing Speed — Top 5% Percentile" 
                            : reactionResultTime < 320 
                            ? "Above-Average Processing Speed" 
                            : reactionResultTime < 450 
                            ? "Average Processing Speed" 
                            : reactionResultTime < 700 
                            ? "Below-Average Processing Speed" 
                            : reactionResultTime < 1500 
                            ? "Low Processing Speed — Attention Recommended" 
                            : "Delayed Response — Possible Attention Lapse"}
                        </p>
                        <span className="text-[10px] font-medium text-blue-200 underline mt-2">Click to try again</span>
                      </>
                    )}
                  </div>

                  {/* Quick Benchmark Stats Row */}
                  <div className="grid grid-cols-3 gap-2.5 text-center pt-1">
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 rounded-xl">
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Duration</p>
                      <p className="text-xs font-extrabold text-slate-900 dark:text-white mt-0.5">15 min total</p>
                    </div>
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 rounded-xl">
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Assessment</p>
                      <p className="text-xs font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">4 modules</p>
                    </div>
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 rounded-xl">
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Results</p>
                      <p className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">Instant report</p>
                    </div>
                  </div>

                  {/* Info Footer Callout */}
                  <div className="mt-4 pt-4 border-t border-slate-150 dark:border-slate-800/80 text-[11px] text-slate-500 dark:text-slate-455 leading-relaxed font-sans font-semibold text-center">
                    Please ensure a stable internet connection and a quiet environment before starting the assessment.
                  </div>
                </div>
              </motion.div>

            </div>
          </div>
        </section>

        {/* 2. About Section */}
        <section 
          id="about" 
          className="relative bg-slate-50 dark:bg-slate-950/20 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-16"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.02),transparent_40%)] dark:bg-[radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.06),transparent_40%)]" />
          
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
              
              {/* Left Column: Heading and Branding */}
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="lg:col-span-5 space-y-6"
              >
                <div className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 dark:bg-blue-950/30 px-3.5 py-1 text-xs font-semibold text-blue-700 dark:text-blue-400 border border-blue-100/50 dark:border-blue-900/30 shadow-sm">
                  <span>Platform Overview</span>
                </div>
                
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
                  Bridging the Gap <br />
                  Between Human <br />
                  <span className="gradient-text glow-text font-bold inline-block pb-1">
                    Potential & Opportunity
                  </span>
                </h2>
                
                <div className="h-1.5 w-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 animate-gradient-shift" />
                
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400 leading-relaxed max-w-sm">
                  Evaluates cognitive abilities, aptitude, personality, and learning preferences to empower decisions through science.
                </p>
              </motion.div>

              {/* Right Column: Narrative Glass Card */}
              <motion.div 
                initial={{ opacity: 0, y: 35 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7 }}
                className="lg:col-span-7"
              >
                <div className="bento-card rounded-3xl p-8 sm:p-10 shadow-lg space-y-6">
                  <p className="text-slate-650 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
                    <strong>Mentiscope</strong> is an innovative cognitive assessment platform incubated at NIRMAAN, IIT Madras, dedicated to helping students, job aspirants, and professionals discover their true potential through scientifically designed assessments. By integrating cognitive science, psychometrics, and artificial intelligence, the platform evaluates cognitive abilities, aptitude, personality, and learning preferences to generate personalized insights. These assessments empower individuals to make informed academic, career, and personal development decisions.
                  </p>
                  
                  <div className="border-t border-slate-200 dark:border-slate-800/80 my-4" />
                  
                  <p className="text-slate-650 dark:text-slate-350 text-sm sm:text-base leading-relaxed">
                    Mentiscope also supports schools, colleges, training institutions, and employers with data-driven tools for talent identification, career guidance, and skill assessment. Instead of providing only test scores, the platform delivers comprehensive reports with visual analytics, benchmarking, and personalized recommendations for continuous improvement. With a vision to make scientific assessment accessible to everyone, Mentiscope aims to bridge the gap between human potential and opportunity through technology-driven innovation.
                  </p>
                </div>
              </motion.div>

            </div>
          </div>
        </section>

        {/* 3. Target Audience Section */}
        <section 
          id="audience" 
          className="relative bg-slate-55 dark:bg-slate-900/35 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto mb-12 space-y-4"
            >
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Target Cohorts
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                For Whom?
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Mentiscope is built to deliver scientifically validated, intelligent cognitive evaluations for a wide range of candidate cohorts:
              </p>
            </motion.div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  icon: BookOpen,
                  title: "School Students",
                  desc: "Specifically designed for Class 7 to 12. Helps identify learning patterns, cognitive development milestones, and academic strengths.",
                  badge: "Class 7 – 12",
                  color: "bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400"
                },
                {
                  icon: GraduationCap,
                  title: "College Students",
                  desc: "Helps higher education students uncover learning preferences, specialize their skill sets, and navigate career pathways based on cognitive metrics.",
                  badge: "Undergrad & Postgrad",
                  color: "bg-teal-50 dark:bg-teal-950/60 text-teal-650 dark:text-teal-400"
                },
                {
                  icon: Briefcase,
                  title: "Job Seekers",
                  desc: "Empowers job seekers to identify key cognitive assets, align with standard profiles, and build self-awareness for industry placement.",
                  badge: "Placement Readiness",
                  color: "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400"
                },
                {
                  icon: Trophy,
                  title: "Competitive Aspirants",
                  desc: "Evaluates aptitude, working memory bounds, speed, and focus precision to help benchmark readiness for competitive exams.",
                  badge: "Aspirants",
                  color: "bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-455"
                }
              ].map((cohort, index) => (
                <motion.div
                  key={cohort.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bento-card rounded-2xl p-6 shadow-sm flex flex-col justify-between group cursor-default"
                >
                  <div>
                    <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${cohort.color} mb-5 group-hover:scale-110 transition-transform duration-300`}>
                      <cohort.icon className="h-6 w-6" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {cohort.title}
                    </h3>
                    <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400 font-sans">
                      {cohort.desc}
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                      {cohort.badge}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* 4. Assessment Modules Grid */}
        <section 
          id="modules" 
          className="relative bg-white dark:bg-slate-950 border-y border-slate-200/80 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-20 overflow-hidden"
        >
          {/* Ambient Lighting Gradients */}
          <div className="absolute top-12 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-b from-blue-500/10 via-indigo-500/5 to-transparent blur-3xl pointer-events-none" />
          <div className="absolute -bottom-20 right-0 w-96 h-96 bg-purple-500/5 dark:bg-purple-500/10 blur-3xl pointer-events-none" />

          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            
            {/* Clean, Normal Section Header */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto mb-14 space-y-3"
            >
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                The Scientific Pillars (10 Modules)
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Cognitive & Psychometric Evaluation Battery
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
                10 scientifically designed constructs developed by NIRMAAN IIT Madras researchers for comprehensive human potential profiling.
              </p>
            </motion.div>

            {/* 10 Modules Modern Bento Deck (2 Featured + 4 Cognitive + 4 Specialized) */}
            <div className="space-y-7">
              
              {/* Tier 1: 2 Flagship Anchor Modules */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {FEATURED_MODULES.map((mod, i) => {
                  const meta = CONSTRUCT_META[mod.id] || {
                    shortCode: `M${i + 1}`,
                    chcLabel: "Standard Construct",
                    categoryTag: "Evaluation Battery",
                    benchmarkMetric: "Cognitive Indicator",
                  };
                  const isActive = MODULE_CONFIGS.some((m) => m.id === mod.id);
                  const iconMap: Record<string, any> = {
                    Cpu, BookOpen, Calculator, Box, Activity, Zap, Eye, Compass, UserCheck, ShieldAlert, Headphones
                  };
                  const IconComponent = iconMap[mod.icon] || Compass;

                  return (
                    <motion.div
                      key={mod.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: i * 0.08 }}
                      onClick={() => setInspectedModule(mod)}
                      className="group relative rounded-2xl p-6 sm:p-7 bg-white dark:bg-slate-900/70 border border-slate-200/90 dark:border-slate-800 hover:border-blue-500/40 dark:hover:border-blue-500/40 shadow-sm hover:shadow-xl dark:hover:shadow-[0_12px_32px_-8px_rgba(0,0,0,0.4)] hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col justify-between overflow-hidden"
                    >
                      {/* Ambient corner light */}
                      <div className="absolute top-0 right-0 w-44 h-44 bg-gradient-to-bl from-blue-500/8 via-indigo-500/4 to-transparent blur-2xl pointer-events-none group-hover:scale-110 transition-transform duration-500" />

                      <div>
                        {/* Top Meta Row */}
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/50 group-hover:scale-105 transition-transform duration-300">
                              <IconComponent className="h-5.5 w-5.5" />
                            </div>
                            <div>
                              <span className="text-[10px] font-mono font-extrabold uppercase tracking-wider text-blue-600 dark:text-blue-400 block leading-none mb-0.5">
                                {meta.categoryTag}
                              </span>
                              <span className="text-xs font-mono font-bold text-slate-400 dark:text-slate-500">
                                {meta.shortCode}
                              </span>
                            </div>
                          </div>

                          {isActive ? (
                            <span className="inline-flex items-center gap-1.5 font-mono text-[10px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200/80 dark:border-emerald-800/60 px-2.5 py-1 rounded-full shadow-xs">
                              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                              Active Battery
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 font-mono text-[10px] font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700/60 px-2.5 py-1 rounded-full">
                              <CheckCircle className="h-3 w-3 text-slate-400" />
                              Full Battery Spec
                            </span>
                          )}
                        </div>

                        {/* Title & Task */}
                        <h3 className="text-xl font-extrabold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors mb-1.5">
                          {mod.name}
                        </h3>

                        {mod.taskName && (
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 dark:bg-slate-800/80 border border-slate-200/70 dark:border-slate-700/60 text-xs font-mono text-slate-700 dark:text-slate-300 mb-3 shadow-xs">
                            <span className="h-1.5 w-1.5 rounded-full bg-blue-500 shrink-0" />
                            <span className="text-slate-400 dark:text-slate-500 font-sans text-[10px] uppercase font-bold">Protocol:</span>
                            <span className="font-semibold text-slate-800 dark:text-slate-200 truncate">{mod.taskName}</span>
                          </div>
                        )}

                        {/* Description */}
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-sans mb-4">
                          {mod.description}
                        </p>

                        {/* Micro-Visual for Featured Anchor Cards */}
                        {mod.id === "gf" && (
                          <div className="mb-4 p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="grid grid-cols-3 gap-1.5 p-1.5 bg-slate-200/70 dark:bg-slate-900 rounded-lg">
                                {[1,2,3,4,5,6,7,8].map(n => (
                                  <div key={n} className="h-2 w-2 rounded-xs bg-blue-500/70" />
                                ))}
                                <div className="h-2 w-2 rounded-xs bg-emerald-500 animate-pulse" />
                              </div>
                              <div>
                                <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">Rule Induction Matrix</p>
                                <p className="text-[10px] text-slate-400">Non-verbal pattern discovery</p>
                              </div>
                            </div>
                            <span className="text-[10px] font-mono font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded">
                              Matrix IRT
                            </span>
                          </div>
                        )}

                        {mod.id === "riasec" && (
                          <div className="mb-4 p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
                            <p className="text-[10px] font-mono font-bold text-slate-400 uppercase mb-1.5">6 Holland Vocational Dimensions</p>
                            <div className="flex flex-wrap gap-1.5">
                              {["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"].map(dim => (
                                <span key={dim} className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60">
                                  {dim}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Card Footer: Researcher & Time */}
                      <div className="flex items-center justify-between pt-3.5 border-t border-slate-200/80 dark:border-slate-800/80 text-xs">
                        <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                          <GraduationCap className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                          <span className="text-slate-400 font-normal">Lead:</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-200">{mod.researcher}</span>
                        </div>
                        <div className="flex items-center gap-1 text-slate-400 font-mono text-[11px]">
                          <Clock className="h-3 w-3" />
                          <span>{mod.estimatedTime}</span>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Tier 2: 4 Core Cognitive Ability Modules */}
              <div>
                <div className="flex items-center gap-2 mb-3.5 px-1">
                  <span className="h-2 w-2 rounded-full bg-blue-500" />
                  <h4 className="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                    Core Cognitive Architecture (CHC Theory)
                  </h4>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4.5">
                  {CORE_COGNITIVE_MODULES.map((mod, i) => {
                    const meta = CONSTRUCT_META[mod.id] || {
                      shortCode: `M${i + 3}`,
                      chcLabel: "Standard Construct",
                      categoryTag: "Evaluation Battery",
                      benchmarkMetric: "Cognitive Indicator",
                    };
                    const isActive = MODULE_CONFIGS.some((m) => m.id === mod.id);
                    const iconMap: Record<string, any> = {
                      Cpu, BookOpen, Calculator, Box, Activity, Zap, Eye, Compass, UserCheck, ShieldAlert, Headphones
                    };
                    const IconComponent = iconMap[mod.icon] || Compass;

                    return (
                      <motion.div
                        key={mod.id}
                        initial={{ opacity: 0, y: 15 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.4, delay: i * 0.05 }}
                        onClick={() => setInspectedModule(mod)}
                        className="group relative rounded-2xl p-5 bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 hover:border-blue-500/40 dark:hover:border-blue-500/40 shadow-xs hover:shadow-lg dark:hover:shadow-[0_8px_24px_rgba(0,0,0,0.3)] hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col justify-between"
                      >
                        <div>
                          {/* Header */}
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/50 group-hover:scale-105 transition-transform duration-300">
                              <IconComponent className="h-4.5 w-4.5" />
                            </div>
                            <span className="text-[10px] font-mono font-extrabold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-full border border-blue-100 dark:border-blue-900/50">
                              {meta.shortCode}
                            </span>
                          </div>

                          {/* Title */}
                          <h4 className="font-extrabold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors text-sm mb-1 leading-snug">
                            {mod.name}
                          </h4>

                          {/* Task Name */}
                          {mod.taskName && (
                            <p className="text-[11px] font-mono text-blue-500 dark:text-blue-400 truncate mb-2">
                              {mod.taskName}
                            </p>
                          )}

                          {/* Description */}
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed font-sans line-clamp-3 mb-3">
                            {mod.description}
                          </p>
                        </div>

                        {/* Footer: Researcher & Time */}
                        <div className="pt-2.5 border-t border-slate-100 dark:border-slate-800/80 text-[10px] space-y-1.5">
                          <div className="flex items-center gap-1 text-slate-500 dark:text-slate-400 truncate">
                            <span className="text-slate-400">Lead:</span>
                            <span className="font-semibold text-slate-700 dark:text-slate-300 truncate">{mod.researcher}</span>
                          </div>
                          <div className="flex items-center justify-between text-slate-400 font-mono">
                            <span>{mod.estimatedTime}</span>
                            {isActive ? (
                              <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                Active
                              </span>
                            ) : (
                              <span className="text-slate-400">Spec</span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Tier 3: 4 Specialized Aptitude, Behavioral & Auditory Modules */}
              <div>
                <div className="flex items-center gap-2 mb-3.5 px-1">
                  <span className="h-2 w-2 rounded-full bg-indigo-500" />
                  <h4 className="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                    Specialized Aptitude, Behavioral & Auditory Constructs
                  </h4>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4.5">
                  {SPECIALIZED_MODULES.map((mod, i) => {
                    const meta = CONSTRUCT_META[mod.id] || {
                      shortCode: `M${i + 7}`,
                      chcLabel: "Standard Construct",
                      categoryTag: "Evaluation Battery",
                      benchmarkMetric: "Cognitive Indicator",
                    };
                    const isActive = MODULE_CONFIGS.some((m) => m.id === mod.id);
                    const iconMap: Record<string, any> = {
                      Cpu, BookOpen, Calculator, Box, Activity, Zap, Eye, Compass, UserCheck, ShieldAlert, Headphones
                    };
                    const IconComponent = iconMap[mod.icon] || Compass;

                    return (
                      <motion.div
                        key={mod.id}
                        initial={{ opacity: 0, y: 15 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.4, delay: i * 0.05 }}
                        onClick={() => setInspectedModule(mod)}
                        className="group relative rounded-2xl p-5 bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 hover:border-indigo-500/40 dark:hover:border-indigo-500/40 shadow-xs hover:shadow-lg dark:hover:shadow-[0_8px_24px_rgba(0,0,0,0.3)] hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col justify-between"
                      >
                        <div>
                          {/* Header */}
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/50 group-hover:scale-105 transition-transform duration-300">
                              <IconComponent className="h-4.5 w-4.5" />
                            </div>
                            <span className="text-[10px] font-mono font-extrabold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-100 dark:border-indigo-900/50">
                              {meta.shortCode}
                            </span>
                          </div>

                          {/* Title */}
                          <h4 className="font-extrabold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors text-sm mb-1 leading-snug">
                            {mod.name}
                          </h4>

                          {/* Task Name */}
                          {mod.taskName && (
                            <p className="text-[11px] font-mono text-indigo-500 dark:text-indigo-400 truncate mb-2">
                              {mod.taskName}
                            </p>
                          )}

                          {/* Description */}
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed font-sans line-clamp-3 mb-3">
                            {mod.description}
                          </p>
                        </div>

                        {/* Footer: Researcher & Time */}
                        <div className="pt-2.5 border-t border-slate-100 dark:border-slate-800/80 text-[10px] space-y-1.5">
                          <div className="flex items-center gap-1 text-slate-500 dark:text-slate-400 truncate">
                            <span className="text-slate-400">Lead:</span>
                            <span className="font-semibold text-slate-700 dark:text-slate-300 truncate">{mod.researcher}</span>
                          </div>
                          <div className="flex items-center justify-between text-slate-400 font-mono">
                            <span>{mod.estimatedTime}</span>
                            {isActive ? (
                              <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                Active
                              </span>
                            ) : (
                              <span className="text-slate-400">Spec</span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

            </div>

          </div>

          {/* Interactive Scientific Deep Dive Modal */}
          <AnimatePresence>
            {inspectedModule && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setInspectedModule(null)}
                  className="fixed inset-0 bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm"
                />

                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  transition={{ duration: 0.2 }}
                  className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-200 dark:border-slate-800 z-10 max-h-[90vh] overflow-y-auto"
                >
                  {/* Close button */}
                  <button
                    onClick={() => setInspectedModule(null)}
                    className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                  >
                    <X className="h-5 w-5" />
                  </button>

                  {/* Modal Header */}
                  <div className="flex items-start gap-4 mb-6">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${PILLAR_COLOR_THEMES[inspectedModule.color]?.iconBg || "bg-blue-50 text-blue-600"}`}>
                      {(() => {
                        const iconMap: Record<string, any> = {
                          Cpu, BookOpen, Calculator, Box, Activity, Zap, Eye, Compass, UserCheck, ShieldAlert, Headphones
                        };
                        const Icon = iconMap[inspectedModule.icon] || Compass;
                        return <Icon className="h-6 w-6" />;
                      })()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/70 px-2 py-0.5 rounded-full border border-blue-200/60 dark:border-blue-800/60">
                          {CONSTRUCT_META[inspectedModule.id]?.shortCode || "Construct"}
                        </span>
                        <span className="text-xs font-mono text-slate-400">
                          {CONSTRUCT_META[inspectedModule.id]?.chcLabel}
                        </span>
                      </div>
                      <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                        {inspectedModule.name}
                      </h3>
                      {inspectedModule.taskName && (
                        <p className="text-xs font-mono text-blue-500 dark:text-blue-400 mt-0.5">
                          Task Protocol: {inspectedModule.taskName}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Researcher & Institution Pill */}
                  <div className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 mb-6">
                    <GraduationCap className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0" />
                    <div className="text-xs">
                      <span className="text-slate-400">Lead Researcher: </span>
                      <strong className="text-slate-800 dark:text-slate-200 font-semibold">{inspectedModule.researcher}</strong>
                      <span className="text-slate-400"> · NIRMAAN, IIT Madras</span>
                    </div>
                  </div>

                  {/* Detailed Description */}
                  <div className="space-y-4 text-xs sm:text-sm text-slate-650 dark:text-slate-350 leading-relaxed font-sans">
                    <p>{inspectedModule.description}</p>

                    {MODULE_RESEARCH_DETAILS[inspectedModule.id] && (
                      <>
                        <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-900/40 space-y-2">
                          <h4 className="text-xs font-bold text-blue-800 dark:text-blue-300 uppercase tracking-wider flex items-center gap-1.5">
                            <Compass className="h-4 w-4" />
                            Academic & Career Stream Alignment
                          </h4>
                          <p className="text-xs text-blue-900/80 dark:text-blue-200/90 leading-relaxed">
                            {MODULE_RESEARCH_DETAILS[inspectedModule.id].streamRelevance}
                          </p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
                            <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block mb-1">
                              Theoretical Grounding
                            </span>
                            <p className="text-xs text-slate-600 dark:text-slate-300">
                              {MODULE_RESEARCH_DETAILS[inspectedModule.id].scientificBasis}
                            </p>
                          </div>
                          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
                            <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block mb-1">
                              Predictive Metric
                            </span>
                            <p className="text-xs text-slate-600 dark:text-slate-300">
                              {MODULE_RESEARCH_DETAILS[inspectedModule.id].sampleInsight}
                            </p>
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Modal Footer CTA */}
                  <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
                    <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      Testing Duration: {inspectedModule.estimatedTime}
                    </span>
                    <button
                      onClick={() => {
                        setInspectedModule(null);
                        handleLoginOrDashboard();
                      }}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-blue-500/20 flex items-center gap-1.5 cursor-pointer"
                    >
                      <span>Take Full Assessment</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </section>

        {/* 5. Assessment Module Workflow Section */}
        <section 
          id="workflow" 
          className="relative bg-white dark:bg-slate-950 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto mb-16 space-y-4"
            >
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Assessment Journey
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Assessment Module Workflow
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                A seamless, scientifically designed 4-step process to evaluate capabilities and receive personalized development paths:
              </p>
            </motion.div>

            <div className="relative">
              {/* Clean static gradient connector line */}
              <div className="absolute top-1/2 left-8 right-8 h-0.5 bg-gradient-to-r from-blue-500/20 via-teal-500/20 via-indigo-500/20 to-rose-500/20 dark:from-blue-500/30 dark:via-teal-500/30 dark:via-indigo-500/30 dark:to-rose-500/30 -translate-y-1/2 hidden lg:block z-0 rounded-full" />

              <div className="grid grid-cols-1 gap-8 lg:grid-cols-4 relative z-10">
                
                {/* Step 1 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -3 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                  className="bento-card spring-press rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group cursor-default"
                >
                  <div className="absolute -top-3.5 left-6 bg-blue-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-2 border-white dark:border-slate-950 shadow-sm">
                    01
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mb-4 transition-transform duration-300 group-hover:scale-105">
                      <UserPlus className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">Register / Login</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                      Initialize your evaluation session by signing up or logging in with your secure ID and password.
                    </p>
                  </div>
                </motion.div>

                {/* Step 2 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -3 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.2 }}
                  className="bento-card spring-press rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group cursor-default"
                >
                  <div className="absolute -top-3.5 left-6 bg-teal-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-2 border-white dark:border-slate-950 shadow-sm">
                    02
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400 mb-4 transition-transform duration-300 group-hover:scale-105">
                      <ClipboardList className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-2 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">Submit Details</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                      Provide demographics (Age, Gender, Education, Marks %, School/College Type, District, State) for baseline comparison.
                    </p>
                  </div>
                </motion.div>

                {/* Step 3 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -3 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.3 }}
                  className="bento-card spring-press rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group cursor-default"
                >
                  <div className="absolute -top-3.5 left-6 bg-indigo-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-2 border-white dark:border-slate-950 shadow-sm">
                    03
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mb-4 transition-transform duration-300 group-hover:scale-105">
                      <Activity className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">Take Test</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                      Complete a comprehensive battery of 10 cognitive modules, evaluating memory span, attention, processing speed, and auditory reasoning.
                    </p>
                  </div>
                </motion.div>

                {/* Step 4 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -3 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.4 }}
                  className="bento-card spring-press rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group cursor-default"
                >
                  <div className="absolute -top-3.5 left-6 bg-rose-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-2 border-white dark:border-slate-950 shadow-md">
                    04
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 mb-4 transition-transform duration-300 group-hover:scale-105">
                      <BarChart4 className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-2 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">Generate Report</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                      Instantly download visual reports with performance benchmarks, custom analytics, and personalized growth recommendations.
                    </p>
                  </div>
                </motion.div>

              </div>
            </div>
          </div>
        </section>

        {/* 6. Unified Science & Benefits Section */}
        <section 
          id="benefits" 
          className="relative overflow-hidden bg-slate-50 dark:bg-slate-900/30 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-6"
        >
          {/* Animated luxury background blobs */}
          <div className="absolute top-1/4 right-1/10 w-96 h-96 rounded-full bg-blue-500/5 dark:bg-blue-500/10 blur-3xl pointer-events-none animate-float" />
          <div className="absolute bottom-1/4 left-1/10 w-80 h-80 rounded-full bg-indigo-500/5 dark:bg-indigo-500/8 blur-3xl pointer-events-none animate-float delay-300" />
          
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10 space-y-6">
            
            {/* Header Area */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-3xl mx-auto space-y-1"
            >
              <h2 className="text-[10px] font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Why it works
              </h2>
              <p className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-3xl">
                Backed by real science, not guesswork
              </p>
              <p className="text-xs text-slate-555 dark:text-slate-405 max-w-xl mx-auto leading-relaxed">
                Mentiscope combines proven psychometric research with AI, incubated and validated at IIT Madras's NIRMAAN program.
              </p>
            </motion.div>

            {/* Stream Convergence Interactive Diagram */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{ duration: 0.6 }}
              className="relative mx-auto max-w-5xl group"
            >
              <StreamConvergenceGraphic />
            </motion.div>

            {/* Core Diagnostics Grid below the top image */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{ duration: 0.6 }}
              className="space-y-5"
            >
              <div className="text-center max-w-2xl mx-auto space-y-0.5">
                <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  How we find your fit
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                  We look at how you think, not just what you know, to match you with the stream where you'll actually thrive.
                </p>
              </div>

              {/* 4-Column Feature Grid with Dynamic Effects */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto items-stretch">
                {[
                  {
                    icon: Brain,
                    title: "Whole-picture assessment",
                    desc: "We look at memory, focus, and problem-solving, not just one test score.",
                    isHighlight: false,
                    cardStyle: "border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/50 hover:border-blue-400/60 dark:hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10",
                    iconColor: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60"
                  },
                  {
                    icon: Award,
                    title: "Backed by IIT Madras",
                    desc: "Built and validated through NIRMAAN, IIT Madras's incubation program.",
                    isHighlight: true,
                    cardStyle: "border-2 border-blue-500/80 dark:border-blue-400/80 bg-gradient-to-b from-blue-50/80 via-white/60 to-blue-50/40 dark:from-blue-950/50 dark:via-slate-900/60 dark:to-slate-900/70 shadow-lg shadow-blue-500/15 hover:shadow-xl hover:shadow-blue-500/25 hover:border-blue-400",
                    iconColor: "text-blue-600 dark:text-blue-300 bg-blue-100 dark:bg-blue-900/70 ring-2 ring-blue-500/30"
                  },
                  {
                    icon: ShieldCheck,
                    title: "Fair & accurate results",
                    desc: "Smart monitoring keeps your results honest and reliable.",
                    isHighlight: false,
                    cardStyle: "border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/50 hover:border-indigo-400/60 dark:hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/10",
                    iconColor: "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60"
                  },
                  {
                    icon: Sparkles,
                    title: "Insights, not just answers",
                    desc: "Get a personalized report explaining why a stream fits you, not just a label.",
                    isHighlight: false,
                    cardStyle: "border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/50 hover:border-purple-400/60 dark:hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10",
                    iconColor: "text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/60"
                  }
                ].map((feat, i) => (
                  <motion.div 
                    key={feat.title}
                    whileHover={{ y: -4, transition: { duration: 0.2 } }}
                    className={`custom-glass rounded-xl p-4 flex gap-3.5 items-start cursor-default border ${feat.cardStyle} flex-row h-full transition-all duration-300 relative group/card`}
                  >
                    {feat.isHighlight && (
                      <div className="absolute -top-2.5 right-3 px-2 py-0.5 rounded-full bg-blue-600 text-white text-[9px] font-extrabold tracking-wider uppercase shadow-md shadow-blue-500/30">
                        TRUST ANCHOR
                      </div>
                    )}
                    <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${feat.iconColor} transition-transform duration-300 group-hover/card:scale-110`}>
                      <feat.icon className="h-5 w-5" />
                    </div>
                    <div className="space-y-1 text-left flex-1">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">{feat.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">{feat.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

          </div>
        </section>

        {/* 7. Contact Section */}
        <section 
          id="contact" 
          className="relative bg-white dark:bg-slate-950 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{ duration: 0.6 }}
              className="mx-auto max-w-3xl text-center mb-10"
            >
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Get in Touch
              </h2>
              <p className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Contact Us
              </p>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                Have questions or want to collaborate? Connect with the Mentiscope team.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
              
              {/* Contact Details */}
              <motion.div 
                initial={{ opacity: 0, x: -25 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: false, amount: 0.2 }}
                transition={{ duration: 0.6 }}
                className="lg:col-span-4 space-y-6"
              >
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                    <Mail className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Email Address</p>
                    <p className="text-xs text-slate-555 dark:text-slate-400 font-mono">assesmentcognitive@gmail.com</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                    <Phone className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Phone Support</p>
                    <p className="text-xs text-slate-555 dark:text-slate-400 font-mono">ph: +91 9037188431, +91 9947783548</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                    <MapPin className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Incubation Partner</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">NIRMAAN, IIT Madras, Chennai, India</p>
                  </div>
                </div>
              </motion.div>

              {/* Inquiry Form */}
              <motion.div 
                initial={{ opacity: 0, x: 25 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: false, amount: 0.2 }}
                transition={{ duration: 0.6 }}
                className="lg:col-span-8"
              >
                <form onSubmit={handleSubmitContact} className="luxury-glass premium-border-glow space-y-4 rounded-2xl p-6 sm:p-8">
                  {submitted && (
                    <div className="rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 p-4 text-sm text-emerald-800 dark:text-emerald-300 flex items-center gap-2.5">
                      <CheckCircle className="h-5 w-5 text-emerald-600" />
                      <span>Message successfully sent! The Mentiscope team will email you shortly.</span>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 dark:text-slate-350 mb-1.5">Full Name</label>
                      <input
                        type="text"
                        required
                        value={contactForm.name}
                        onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                        placeholder="Your Name"
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 dark:text-slate-355 mb-1.5">Email Address</label>
                      <input
                        type="email"
                        required
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                        placeholder="your.email@example.com"
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-350 mb-1.5">School / College / Organization</label>
                    <input
                      type="text"
                      required
                      value={contactForm.institution}
                      onChange={(e) => setContactForm({ ...contactForm, institution: e.target.value })}
                      placeholder="Your Institution Name"
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-350 mb-1.5">Your Message</label>
                    <textarea
                      rows={4}
                      required
                      value={contactForm.message}
                      onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                      placeholder="Write your message here..."
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 py-2.5 text-sm font-semibold text-white transition-all duration-300 hover:shadow shadow-sm shadow-blue-500/10 active:scale-[0.99]"
                  >
                    Send Message
                  </button>
                </form>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Footer at the end of scrollable landing page */}
        <Footer onNavigate={onNavigate} />
      </div>
    </div>
  );
}
