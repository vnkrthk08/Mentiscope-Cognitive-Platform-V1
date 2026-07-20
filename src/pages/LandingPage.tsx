import React, { useState, useEffect } from "react";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import Footer from "../components/Footer";
import { motion } from "motion/react";
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
  BarChart4
} from "lucide-react";

interface LandingPageProps {
  onNavigate: (page: string) => void;
}

export default function LandingPage({ onNavigate }: LandingPageProps) {
  const [contactForm, setContactForm] = useState({ name: "", email: "", institution: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState<string>("home");

  const sections = ["home", "about", "audience", "modules", "workflow", "benefits", "science", "contact"];

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
      threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          // Guard state update to prevent redundant re-renders during active scrolling
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
      
      {/* Floating Dot Indicator */}
      <div className="fixed right-6 top-1/2 z-50 -translate-y-1/2 space-y-4 hidden md:flex flex-col">
        {sections.map((sec) => (
          <button
            key={sec}
            onClick={() => handleDotClick(sec)}
            title={`Go to ${sec}`}
            className="group flex items-center justify-end gap-3 text-right focus:outline-none"
          >
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              {sec === "home" ? "Welcome" : sec === "audience" ? "For Whom" : sec.charAt(0).toUpperCase() + sec.slice(1)}
            </span>
            <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${
              activeSection === sec
                ? "bg-blue-600 border-blue-600 scale-125 shadow-md shadow-blue-500/20"
                : "border-slate-350 dark:border-slate-700 bg-transparent hover:border-slate-500 dark:hover:border-slate-400"
            }`} />
          </button>
        ))}
      </div>

      {/* Snap Scroll Container */}
      <div 
        id="landing-scroll-container"
        className="h-[calc(100vh-5rem)] overflow-y-auto snap-y snap-mandatory scroll-smooth"
      >
        
        {/* 1. Hero Section */}
        <section 
          id="home"
          className="relative overflow-hidden bg-white dark:bg-slate-950 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-12"
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(37,99,235,0.05),transparent_50%)] dark:bg-[radial-gradient(ellipse_at_top_right,rgba(37,99,235,0.15),transparent_50%)]" />
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 w-full">
            <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12">
              <div className="lg:col-span-7 space-y-6">
                
                {/* Badge */}
                <div className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 dark:bg-blue-950/40 px-3 py-1 text-xs font-semibold text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-900/50">
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Unlock Your Potential – Transform Your Future</span>
                </div>
                
                <h1 className="font-sans text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl lg:text-6xl leading-[1.1]">
                  Mentiscope <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 text-3xl sm:text-4xl lg:text-5xl font-bold block mt-2 pb-2 leading-tight">
                    Cognitive Assessment Capsule
                  </span>
                </h1>
                
                <p className="max-w-xl text-base sm:text-lg text-slate-650 dark:text-slate-350 leading-relaxed">
                  Developed by a multidisciplinary team of AI experts, technologists, researchers, academicians, and psychologists to deliver scientifically validated and intelligent cognitive assessment solutions.
                </p>

                {/* Incubation Badge */}
                <div className="flex flex-wrap items-center gap-4 pt-2">
                  <div className="flex items-center gap-3 bg-slate-50 dark:bg-slate-900/60 px-4 py-2.5 rounded-xl border border-slate-200/60 dark:border-slate-800">
                    <img src="/logo.svg" alt="NIRMAAN Logo" className="h-10 w-auto object-contain filter dark:brightness-110" />
                    <div>
                      <p className="text-[9px] uppercase tracking-wider text-slate-400 font-bold leading-none">Incubated At</p>
                      <p className="text-xs font-extrabold text-slate-700 dark:text-slate-200 mt-1">The Pre-Incubator, NIRMAAN, IIT Madras</p>
                    </div>
                  </div>
                </div>
                
                {/* CTA Buttons */}
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <button
                    onClick={() => onNavigate("auth")}
                    className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-base font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/20 active:scale-[0.98]"
                  >
                    <span>Start Assessment Portal</span>
                    <ArrowRight className="h-4.5 w-4.5" />
                  </button>
                  <button
                    onClick={() => handleDotClick("modules")}
                    className="group flex items-center justify-center gap-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 px-6 py-3.5 text-base font-semibold text-slate-700 dark:text-slate-300 transition-all duration-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 hover:border-blue-500/30 dark:hover:border-blue-500/30 hover:text-blue-600 dark:hover:text-blue-400 hover:-translate-y-0.5 hover:shadow-md dark:hover:shadow-[0_8px_20px_-6px_rgba(59,130,246,0.12)] active:scale-[0.98] active:translate-y-0"
                  >
                    <span>Explore Modules</span>
                    <ChevronRight className="h-4.5 w-4.5 transition-transform duration-300 group-hover:rotate-90" />
                  </button>
                </div>

                {/* Trust Factor Row */}
                <div className="pt-6 border-t border-slate-100 dark:border-slate-900 flex flex-wrap items-center gap-6 text-xs text-slate-500 dark:text-slate-455 flex-row">
                  <div className="flex items-center gap-1.5 font-medium">
                    <Award className="h-4 w-4 text-emerald-500" />
                    <span>Incubated at IIT Madras</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-medium">
                    <ShieldCheck className="h-4 w-4 text-indigo-500" />
                    <span>Scientifically Validated</span>
                  </div>
                </div>
              </div>
              {/* Visual Capsule Illustration */}
              <div className="lg:col-span-5 relative hidden lg:block">
                {/* Background ambient glowing radial effects */}
                <div className="absolute -left-12 -top-12 -right-12 -bottom-12 bg-gradient-to-tr from-blue-600/10 to-indigo-600/15 blur-3xl rounded-full" />
                
                {/* Outer Glass Container */}
                <div className="relative rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/40 p-8 shadow-2xl shadow-slate-100/50 dark:shadow-none space-y-6 backdrop-blur-lg">
                  
                  {/* Top Header Card Info */}
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-4">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-blue-600 dark:bg-blue-400" />
                      <span className="text-[10px] font-mono font-bold tracking-widest text-slate-450 dark:text-slate-400 uppercase">
                        Assessment Overview
                      </span>
                    </div>
                    <span className="text-[10px] font-bold text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-0.5 rounded-full border border-blue-100 dark:border-blue-900/30">
                      7-Module Diagnostic Suite
                    </span>
                  </div>

                  {/* High-Level Parameters Row */}
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="p-3 bg-slate-50/50 dark:bg-slate-950/20 border border-slate-100 dark:border-slate-800/80 rounded-xl space-y-0.5">
                      <p className="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase">Est. Duration</p>
                      <p className="text-sm font-extrabold text-blue-600 dark:text-blue-400">~35 Mins</p>
                    </div>
                    <div className="p-3 bg-slate-50/50 dark:bg-slate-950/20 border border-slate-100 dark:border-slate-800/80 rounded-xl space-y-0.5">
                      <p className="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase">Assessment</p>
                      <p className="text-sm font-extrabold text-emerald-650 dark:text-emerald-450">7 Modules</p>
                    </div>
                    <div className="p-3 bg-slate-50/50 dark:bg-slate-950/20 border border-slate-100 dark:border-slate-800/80 rounded-xl space-y-0.5">
                      <p className="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase">Flow Type</p>
                      <p className="text-sm font-extrabold text-indigo-600 dark:text-indigo-400">Continuous</p>
                    </div>
                  </div>

                  {/* Core Platform Guidelines List */}
                  <div className="space-y-4 pt-2">
                    
                    {/* Item 1 */}
                    <div className="flex items-start gap-3">
                      <div className="flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-md bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mt-0.5">
                        <CheckCircle className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">Comprehensive Cognitive Metrics</h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal mt-0.5 font-sans">
                          Designed to evaluate fluid reasoning, memory capacity, processing speed, attention limits, and executive planning functions.
                        </p>
                      </div>
                    </div>

                    {/* Item 2 */}
                    <div className="flex items-start gap-3">
                      <div className="flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-655 dark:text-emerald-450 mt-0.5">
                        <ShieldCheck className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">Active Proctoring & Integrity Checks</h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal mt-0.5 font-sans">
                          Ensures evaluation integrity by logging active browser tab focus, window blur events, and navigation attempts.
                        </p>
                      </div>
                    </div>

                    {/* Item 3 */}
                    <div className="flex items-start gap-3">
                      <div className="flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mt-0.5">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">Detailed Diagnostic Report</h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal mt-0.5 font-sans">
                          Generates immediate visual scorecards with performance percentiles, analytical insights, and personalized growth recommendations.
                        </p>
                      </div>
                    </div>

                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800/80 text-[11px] text-slate-500 dark:text-slate-455 leading-relaxed font-sans font-medium text-center">
                    Please ensure a stable internet connection and a quiet environment before starting the assessment.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. About Section */}
        <section 
          id="about" 
          className="relative bg-slate-50 dark:bg-slate-950/20 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-16"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.03),transparent_40%)] dark:bg-[radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.08),transparent_40%)]" />
          
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
              
              {/* Left Column: Heading and Branding */}
              <div className="lg:col-span-5 space-y-6">
                <div className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 dark:bg-blue-950/30 px-3.5 py-1 text-xs font-semibold text-blue-700 dark:text-blue-400 border border-blue-100/50 dark:border-blue-900/30">
                  <span>Platform Overview</span>
                </div>
                
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
                  Bridging the Gap <br />
                  Between Human <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 inline-block pb-1">
                    Potential & Opportunity
                  </span>
                </h2>
                
                <div className="h-1.5 w-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400" />
                
                <p className="text-sm font-medium italic text-slate-500 dark:text-slate-400 leading-relaxed max-w-sm">
                  "Evaluates cognitive abilities, aptitude, personality, and learning preferences to empower decisions through science."
                </p>
              </div>

              {/* Right Column: Narrative Card */}
              <div className="lg:col-span-7">
                <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/40 p-8 sm:p-10 backdrop-blur-md shadow-lg shadow-slate-100/50 dark:shadow-none space-y-6">
                  <p className="text-slate-650 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
                    <strong>Mentiscope</strong> is an innovative cognitive assessment platform incubated at NIRMAAN, IIT Madras, dedicated to helping students, job aspirants, and professionals discover their true potential through scientifically designed assessments. By integrating cognitive science, psychometrics, and artificial intelligence, the platform evaluates cognitive abilities, aptitude, personality, and learning preferences to generate personalized insights. These assessments empower individuals to make informed academic, career, and personal development decisions.
                  </p>
                  
                  <div className="border-t border-slate-200 dark:border-slate-800/80 my-4" />
                  
                  <p className="text-slate-650 dark:text-slate-350 text-sm sm:text-base leading-relaxed">
                    Mentiscope also supports schools, colleges, training institutions, and employers with data-driven tools for talent identification, career guidance, and skill assessment. Instead of providing only test scores, the platform delivers comprehensive reports with visual analytics, benchmarking, and personalized recommendations for continuous improvement. With a vision to make scientific assessment accessible to everyone, Mentiscope aims to bridge the gap between human potential and opportunity through technology-driven innovation.
                  </p>
                </div>
              </div>

            </div>
          </div>
        </section>

        {/* Target Audience Section */}
        <section 
          id="audience" 
          className="relative bg-slate-50 dark:bg-slate-900/35 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
            <div className="text-center max-w-3xl mx-auto mb-12 space-y-4">
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Target Cohorts
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                For Whom?
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Mentiscope is built to deliver scientifically validated, intelligent cognitive evaluations for a wide range of candidate cohorts:
              </p>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {/* Cohort 1 */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-6 shadow-sm flex flex-col justify-between group hover-lift">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mb-5 group-hover:scale-110 transition-transform">
                    <BookOpen className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">School Students</h3>
                  <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                    Specifically designed for Class 7 to 12. Helps identify learning patterns, cognitive development milestones, and academic strengths.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">Class 7 – 12</span>
                </div>
              </div>

              {/* Cohort 2 */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-6 shadow-sm flex flex-col justify-between group hover-lift">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400 mb-5 group-hover:scale-110 transition-transform">
                    <GraduationCap className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">College Students</h3>
                  <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                    Helps higher education students uncover learning preferences, specialize their skill sets, and navigate career pathways based on cognitive metrics.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">Undergrad & Postgrad</span>
                </div>
              </div>

              {/* Cohort 3 */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-6 shadow-sm flex flex-col justify-between group hover-lift">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mb-5 group-hover:scale-110 transition-transform">
                    <Briefcase className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Job Seekers</h3>
                  <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                    Empowers job seekers to identify key cognitive assets, align with standard profiles, and build self-awareness for industry placement.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Job Seekers</span>
                </div>
              </div>

              {/* Cohort 4 */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-6 shadow-sm flex flex-col justify-between group hover-lift">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 mb-5 group-hover:scale-110 transition-transform">
                    <Trophy className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Competitive Aspirants</h3>
                  <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                    Evaluates aptitude, working memory bounds, speed, and focus precision to help benchmark readiness for competitive exams.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">Aspirants</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 3. Assessment Modules Grid */}
        <section 
          id="modules" 
          className="relative bg-white dark:bg-slate-950 border-y border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
            <div className="text-center max-w-3xl mx-auto mb-10 space-y-3">
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                The Seven Pillars
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Cognitive Evaluation Modules
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Each module targets a specific psychological cognitive layer, designed for comprehensive intelligence profiling.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {MODULE_CONFIGS.map((mod, i) => (
                <div
                  key={mod.id}
                  className="group relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-5 transition-all hover:border-blue-400/50 hover:shadow-md dark:hover:bg-slate-900/60 hover-lift"
                >
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-50 dark:bg-slate-900 group-hover:bg-blue-50 dark:group-hover:bg-blue-950/50 text-slate-700 dark:text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      <Compass className="h-5 w-5" />
                    </div>
                    <span className="text-[10px] font-mono font-bold text-slate-450 dark:text-slate-500 bg-slate-100 dark:bg-slate-900 px-2 py-0.5 rounded">
                      M{i + 1}
                    </span>
                  </div>
                  
                  <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors mb-1.5 text-sm sm:text-base">
                    {mod.name}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-4 line-clamp-3">
                    {mod.description}
                  </p>

                  <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-3 text-[11px] font-medium text-slate-400">
                    <span>Est. Time: {mod.estimatedTime}</span>
                    <span className="font-mono text-blue-650 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-950/30 px-1.5 py-0.5 rounded">REST API</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Assessment Module Workflow Section */}
        <section 
          id="workflow" 
          className="relative bg-white dark:bg-slate-950 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
            <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Assessment Journey
              </h2>
              <p className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Assessment Module Workflow
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                A seamless, scientifically designed 4-step process to evaluate capabilities and receive personalized development paths:
              </p>
            </div>

            <div className="relative">
              {/* Connection line for steps (desktop only) */}
              <div className="absolute top-1/2 left-4 right-4 h-0.5 bg-gradient-to-r from-blue-200 via-teal-200 to-indigo-200 dark:from-blue-900 dark:via-teal-900 dark:to-indigo-900 -translate-y-1/2 hidden lg:block z-0" />

              <div className="grid grid-cols-1 gap-8 lg:grid-cols-4 relative z-10">
                {/* Step 1 */}
                <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group hover:border-blue-500/50">
                  <div className="absolute -top-4 left-6 bg-blue-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-4 border-white dark:border-slate-950 shadow-md">
                    01
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 mb-5">
                      <UserPlus className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">Register / Login</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      Initialize your evaluation session by signing up or logging in with your secure ID and password.
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group hover:border-teal-500/50">
                  <div className="absolute -top-4 left-6 bg-teal-500 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-4 border-white dark:border-slate-950 shadow-md">
                    02
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-100 dark:bg-teal-950/60 text-teal-700 dark:text-teal-400 mb-5">
                      <ClipboardList className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">Submit Details</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      Provide demographics (Age, Gender, Education, Marks %, School/College Type, District, State) for baseline comparison.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group hover:border-indigo-500/50">
                  <div className="absolute -top-4 left-6 bg-indigo-600 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-4 border-white dark:border-slate-950 shadow-md">
                    03
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 mb-5">
                      <Activity className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">Take Test</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      Complete a comprehensive battery of 7 cognitive modules, evaluating memory span, attention, processing speed, and reasoning.
                    </p>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between relative group hover:border-rose-500/50">
                  <div className="absolute -top-4 left-6 bg-rose-500 text-white text-xs font-mono font-extrabold h-8 w-8 rounded-full flex items-center justify-center border-4 border-white dark:border-slate-950 shadow-md">
                    04
                  </div>
                  <div className="pt-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-455 mb-5">
                      <BarChart4 className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">Generate Report</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      Instantly download visual reports with performance benchmarks, custom analytics, and personalized growth recommendations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 6. Unified Science & Benefits Section */}
        <section 
          id="benefits" 
          className="relative overflow-hidden bg-slate-50 dark:bg-slate-900/30 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-6"
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
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative mx-auto max-w-4xl group"
            >
              <div className="absolute -inset-2 bg-gradient-to-tr from-blue-500/5 to-indigo-500/5 blur-xl rounded-2xl pointer-events-none" />
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-lg bg-white dark:bg-slate-950 p-1 premium-border-glow">
                <div className="overflow-hidden rounded-xl relative">
                  <img 
                    src="/image1.png" 
                    alt="Mentiscope Science Architecture" 
                    className="w-full h-auto object-cover max-h-[150px] transition-transform duration-700 group-hover:scale-102"
                  />
                </div>
              </div>
            </motion.div>

            {/* Core Diagnostics Grid below the top image */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="space-y-4"
            >
              <div className="text-center max-w-2xl mx-auto space-y-0.5">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Intelligent Cognitive Diagnostics
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
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
                    className={`custom-glass rounded-xl p-3 flex gap-2.5 items-start cursor-default border ${feat.border} flex-row`}
                  >
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-50/50 dark:bg-blue-950/60 text-blue-650 dark:text-blue-400">
                      <feat.icon className="h-4 w-4" />
                    </div>
                    <div className="space-y-0.5 text-left">
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">{feat.title}</h4>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight font-sans">{feat.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

          </div>
        </section>

        {/* 5. Contact Section */}
        <section 
          id="contact" 
          className="relative bg-white dark:bg-slate-950 border-t border-slate-150 dark:border-slate-900 min-h-[calc(100vh-5rem)] flex items-center snap-start w-full transition-colors duration-300 py-12"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
            <div className="mx-auto max-w-3xl text-center mb-10">
              <h2 className="text-xs font-mono font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Get in Touch
              </h2>
              <p className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                Contact Us
              </p>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                Have questions or want to collaborate? Connect with the Mentiscope team.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
              {/* Contact Details */}
              <div className="lg:col-span-4 space-y-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                    <Mail className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Email Address</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 font-sans">assesmentcognitive@gmail.com</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                    <Phone className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Phone Support</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 font-sans">ph: 9037188431, 9947783548</p>
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
              </div>

              {/* Inquiry Form */}
              <div className="lg:col-span-8">
                <form onSubmit={handleSubmitContact} className="space-y-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 p-6 sm:p-8">
                  {submitted && (
                    <div className="rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 p-4 text-sm text-emerald-800 dark:text-emerald-300 flex items-center gap-2.5">
                      <CheckCircle className="h-5 w-5 text-emerald-600" />
                      <span>Message successfully sent! The Mentiscope team will email you shortly.</span>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 dark:text-slate-350 mb-1.5">Full Name</label>
                      <input
                        type="text"
                        required
                        value={contactForm.name}
                        onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                        placeholder="Your Name"
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 dark:text-slate-350 mb-1.5">Email Address</label>
                      <input
                        type="email"
                        required
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                        placeholder="your.email@example.com"
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-350 mb-1.5">School / College / Organization</label>
                    <input
                      type="text"
                      required
                      value={contactForm.institution}
                      onChange={(e) => setContactForm({ ...contactForm, institution: e.target.value })}
                      placeholder="Your Institution Name"
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-350 mb-1.5">Your Message</label>
                    <textarea
                      rows={4}
                      required
                      value={contactForm.message}
                      onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                      placeholder="Write your message here..."
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700 hover:shadow"
                  >
                    Send Message
                  </button>
                </form>
              </div>
            </div>
          </div>
        </section>

        {/* Footer Section */}
        <section id="footer" className="snap-start w-full shrink-0">
          <Footer onNavigate={onNavigate} />
        </section>

      </div>
    </div>
  );
}
