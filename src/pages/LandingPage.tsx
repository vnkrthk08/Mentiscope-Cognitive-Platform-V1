import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import Footer from "../components/Footer";
import { motion, useScroll, useSpring } from "motion/react";
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
  ShieldAlert
} from "lucide-react";

import { User, UserRole } from "../types";
import { AuthService } from "../services/auth/AuthService";

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
              {sec === "home" ? "Welcome" : sec === "audience" ? "For Whom" : sec === "benefits" ? "Science & Benefits" : sec.charAt(0).toUpperCase() + sec.slice(1)}
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
                {/* Premium Glow Badge */}
                <div className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 dark:bg-blue-950/40 px-3.5 py-1 text-xs font-semibold text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-900/50 shadow-sm animate-scale-in">
                  <Sparkles className="h-3.5 w-3.5 animate-spin-slow text-blue-600 dark:text-blue-400" />
                  <span>Transforming Cognitive Assessment Technology</span>
                </div>
                
                <h1 className="font-sans text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl lg:text-6xl leading-[1.1] animate-fade-up delay-100">
                  Mentiscope <br />
                  <span className="gradient-text glow-text text-3xl sm:text-4xl lg:text-5xl font-bold block mt-2 pb-2 leading-tight">
                    Cognitive Assessment Capsule
                  </span>
                </h1>
                
                <p className="max-w-xl text-base sm:text-lg text-slate-650 dark:text-slate-350 leading-relaxed animate-fade-up delay-200">
                  Developed by a multidisciplinary team of AI experts, technologists, researchers, and psychologists to deliver scientifically validated and intelligent cognitive evaluations.
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
                    className="group flex items-center justify-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 px-6 py-3.5 text-base font-semibold text-white transition-all hover:shadow-lg hover:shadow-blue-500/30 active:scale-[0.98] animate-pulse-glow"
                  >
                    <span>{currentUser ? "Go to Portal Dashboard" : "Login & Get Started"}</span>
                    <ArrowRight className="h-4.5 w-4.5 group-hover:translate-x-1 transition-transform" />
                  </button>
                  <button
                    onClick={() => handleDotClick("modules")}
                    className="group flex items-center justify-center gap-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 px-6 py-3.5 text-base font-semibold text-slate-700 dark:text-slate-300 transition-all duration-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 hover:border-blue-500/30 dark:hover:border-blue-500/30 hover:text-blue-600 dark:hover:text-blue-400 hover:-translate-y-0.5 hover:shadow-md dark:hover:shadow-[0_8px_20px_-6px_rgba(59,130,246,0.12)] active:scale-[0.98] active:translate-y-0"
                  >
                    <span>Explore Modules</span>
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
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Avg RT</p>
                      <p className="text-xs font-extrabold text-slate-900 dark:text-white mt-0.5">265 ms</p>
                    </div>
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 rounded-xl">
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Modules</p>
                      <p className="text-xs font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">9 Tasks</p>
                    </div>
                    <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 rounded-xl">
                      <p className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">Precision</p>
                      <p className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">99.4%</p>
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
                
                <p className="text-sm font-medium italic text-slate-500 dark:text-slate-400 leading-relaxed max-w-sm">
                  "Evaluates cognitive abilities, aptitude, personality, and learning preferences to empower decisions through science."
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
          className="relative bg-white dark:bg-slate-950 border-y border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center w-full transition-colors duration-300 py-16"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto mb-12 space-y-3"
            >
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                The Nine Pillars
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Cognitive & Psychometric Evaluation Battery
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                9 scientifically designed constructs developed by NIRMAAN IIT Madras researchers for comprehensive human potential profiling.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {MODULE_CONFIGS.map((mod, i) => {
                const iconMap: Record<string, any> = {
                  Cpu, BookOpen, Calculator, Box, Activity, Zap, Eye, Compass, UserCheck, ShieldAlert
                };
                const IconComponent = iconMap[mod.icon] || Compass;

                return (
                  <motion.div
                    key={mod.id}
                    initial={{ opacity: 0, y: 25 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: i * 0.05 }}
                    className="group relative bento-card spring-press rounded-2xl p-5 cursor-default shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <div className="mb-3.5 flex items-center justify-between">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform duration-300">
                          <IconComponent className="h-5 w-5" />
                        </div>
                        <span className="text-[10px] font-mono font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-full border border-blue-100 dark:border-blue-900/40">
                          M{i + 1}
                        </span>
                      </div>
                      
                      <h3 className="font-extrabold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors mb-1 text-sm leading-snug">
                        {mod.name}
                      </h3>

                      {mod.taskName && (
                        <p className="text-[10px] font-mono font-bold text-blue-500 dark:text-blue-400 mb-2">
                          Task: {mod.taskName}
                        </p>
                      )}

                      <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed font-sans line-clamp-3 mb-3">
                        {mod.description}
                      </p>
                    </div>

                    <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-800/80 pt-2.5 text-[10px] font-semibold text-slate-400">
                      <span>Est: {mod.estimatedTime}</span>
                      <span className="font-mono text-blue-600 dark:text-blue-400 bg-blue-50/60 dark:bg-blue-950/40 px-1.5 py-0.5 rounded">Active</span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
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
                      Complete a comprehensive battery of 9 cognitive modules, evaluating memory span, attention, processing speed, and reasoning.
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
                Science & Benefits
              </h2>
              <p className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-3xl">
                Built on <span className="gradient-text glow-text font-bold">Psychometric Rigor</span>
              </p>
              <p className="text-xs text-slate-555 dark:text-slate-405 max-w-xl mx-auto leading-relaxed">
                Mentiscope unites enterprise-grade infrastructure with deep cognitive science, validated under NIRMAAN, IIT Madras.
              </p>
            </motion.div>

            {/* Image on top of the text */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{ duration: 0.6 }}
              className="relative mx-auto max-w-5xl group"
            >
              <div className="absolute -inset-2 bg-gradient-to-tr from-blue-500/5 to-indigo-500/5 blur-xl rounded-2xl pointer-events-none" />
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-lg bg-white dark:bg-slate-950 p-1 premium-border-glow">
                <div className="overflow-hidden rounded-xl relative">
                  <img 
                    src="/image1.png" 
                    alt="Mentiscope Science Architecture" 
                    className="w-full h-auto object-cover max-h-[280px] sm:max-h-[320px] transition-transform duration-700 group-hover:scale-102"
                  />
                </div>
              </div>
            </motion.div>

            {/* Core Diagnostics Grid below the top image */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{ duration: 0.6 }}
              className="space-y-4"
            >
              <div className="text-center max-w-2xl mx-auto space-y-0.5">
                <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  Intelligent Cognitive Diagnostics
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                  Tracks latency micro-variance, memory span, and attention bounds to generate a complete intelligence profile.
                </p>
              </div>

              {/* 4-Column Feature Grid (Mini Cards) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
                {[
                  {
                    icon: Brain,
                    title: "Multidimensional Metrics",
                    desc: "Fluid intelligence, memory, attention limits",
                    border: "border-blue-200 dark:border-blue-900/30"
                  },
                  {
                    icon: Award,
                    title: "Incubated Rigor",
                    desc: "Validated under NIRMAAN, IIT Madras parameters",
                    border: "border-teal-200 dark:border-teal-900/30"
                  },
                  {
                    icon: ShieldCheck,
                    title: "Active Proctoring",
                    desc: "Real-time focus and tab change tracking",
                    border: "border-indigo-200 dark:border-indigo-900/30"
                  },
                  {
                    icon: Sparkles,
                    title: "AI-Driven Insights",
                    desc: "Gemini-powered diagnostic coaching reports",
                    border: "border-rose-200 dark:border-rose-900/30"
                  }
                ].map((feat) => (
                  <div 
                    key={feat.title}
                    className={`custom-glass rounded-xl p-4 flex gap-3.5 items-start cursor-default border ${feat.border} flex-row`}
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50/50 dark:bg-blue-950/60 text-blue-650 dark:text-blue-400">
                      <feat.icon className="h-5 w-5" />
                    </div>
                    <div className="space-y-1 text-left">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">{feat.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 leading-tight font-sans">{feat.desc}</p>
                    </div>
                  </div>
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
