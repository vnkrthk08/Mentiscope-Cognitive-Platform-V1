import { ModuleConfig } from "../types";

/**
 * The full 9 scientific pillars of the Mentiscope platform developed at NIRMAAN IIT Madras.
 * Displayed across the Landing Page, Overview cards, and Institutional reports.
 */
export const NINE_PILLARS_CONFIG: ModuleConfig[] = [
  {
    id: "gf",
    name: "Fluid Intelligence (Gf)",
    taskName: "Rule Discovery Task",
    researcher: "Pranav Kumaravel",
    description: "Evaluates capacity to reason logically, identify novel abstract patterns, and solve unpracticed visual matrix problems using inductive and deductive rule discovery.",
    icon: "Cpu",
    apiBaseUrl: "/api/modules/gf",
    estimatedTime: "2 mins",
    color: "indigo",
    enabled: true
  },
  {
    id: "gc",
    name: "Crystallized Intelligence (Gc)",
    taskName: "Knowledge Application Task",
    researcher: "Sai Aditya Pragyan",
    description: "Measures depth of acquired knowledge, domain vocabulary, contextual comprehension, and real-world synthesis in diverse scenarios.",
    icon: "BookOpen",
    apiBaseUrl: "/api/modules/gc",
    estimatedTime: "2 mins",
    color: "blue",
    enabled: true
  },
  {
    id: "gq",
    name: "Quantitative Ability (Gq)",
    taskName: "Adaptive Quantitative Decision Arena",
    researcher: "Sagar R",
    description: "Evaluates numerical reasoning, mathematical logic, adaptive difficulty calibration, and quantitative estimation under timed conditions.",
    icon: "Calculator",
    apiBaseUrl: "/api/quantitative",
    estimatedTime: "2-3 mins",
    color: "emerald",
    enabled: true
  },
  {
    id: "gv",
    name: "Visual Processing (Gv)",
    taskName: "Mystery Map Builder",
    researcher: "Vedakshari",
    description: "Measures 2D/3D spatial manipulation, mental rotation, visual memory synthesis, and spatial relationship recognition.",
    icon: "Box",
    apiBaseUrl: "/api/modules/gv",
    estimatedTime: "2 mins",
    color: "cyan",
    enabled: true
  },
  {
    id: "gsm",
    name: "Working Memory (Gsm)",
    taskName: "Classroom Scenario Recall",
    researcher: "Suryansh Raj",
    description: "Tests active memory capacity, dual-task sequence retention, and information updating under controlled memory loads.",
    icon: "Activity",
    apiBaseUrl: "/api/modules/gsm",
    estimatedTime: "2 mins",
    color: "teal",
    enabled: true
  },
  {
    id: "gs",
    name: "Processing Speed (Gs)",
    taskName: "Advanced Perceptual Speed Matrix",
    researcher: "Vinay Kartheek Bathala",
    description: "Measures rapid visual discrimination, symbol matching precision, and motor-free decision speed under strict time pressure.",
    icon: "Zap",
    apiBaseUrl: "/api/modules/processing-speed",
    estimatedTime: "2 mins",
    color: "amber",
    enabled: true
  },
  {
    id: "attention",
    name: "Attention",
    taskName: "Adaptive Shape Attention Task (ASAT)",
    researcher: "Venkata Naga Charanjeet",
    description: "Evaluates sustained focus, selective visual attention, inhibitory control, and distractor rejection using dynamic Stroop & shape stimuli.",
    icon: "Eye",
    apiBaseUrl: "/api/modules/csr",
    estimatedTime: "2 mins",
    color: "rose",
    enabled: true
  },
  {
    id: "riasec",
    name: "Career Interest Assessment (RIASEC Model)",
    taskName: "Day-in-the-Life Project Simulation",
    researcher: "N.S Rakshna",
    description: "Profiles vocational interests across 6 Holland dimensions (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) through interactive simulations.",
    icon: "Compass",
    apiBaseUrl: "/api/modules/riasec",
    estimatedTime: "2-3 mins",
    color: "violet",
    enabled: true
  },
  {
    id: "emotional_regulation",
    name: "Emotional Regulation Assessment",
    taskName: "Crisis Dispatcher Simulation",
    researcher: "Evlin Sara Johny & Lakshmi Pramode",
    description: "Measures stress tolerance, emotional stability, decision consistency, and emergency response performance under high-pressure simulation.",
    icon: "ShieldAlert",
    apiBaseUrl: "/api/modules/emotional-regulation",
    estimatedTime: "2-3 mins",
    color: "red",
    enabled: true
  },
  {
    id: "auditory_verbal",
    name: "Auditory & Verbal Cognitive Assessment",
    taskName: "Dual-Domain Scenario Simulation",
    researcher: "Gowtham",
    description: "Evaluates active working memory, sustained auditory attention, comprehension, decision making, adaptability, metacognition, and verbal delivery fluency through 50 scenario simulations.",
    icon: "Headphones",
    apiBaseUrl: "http://127.0.0.1:8001/api/v1",
    estimatedTime: "2-3 mins",
    color: "purple",
    enabled: true,
    externalUrl: "http://localhost:3000"
  }
];

export const ALL_MODULE_CONFIGS = NINE_PILLARS_CONFIG;

/**
 * Active testing flow for candidate assessment runner.
 * Modules currently in active test rotation.
 */
export const MODULE_CONFIGS: ModuleConfig[] = [
  NINE_PILLARS_CONFIG[0], // Gf - Fluid Intelligence (2 mins)
  NINE_PILLARS_CONFIG[3], // Gv - Visual Processing (2 mins)
  NINE_PILLARS_CONFIG[5], // Gs - Processing Speed (2 mins)
  NINE_PILLARS_CONFIG[6], // Attention - ASAT (2 mins)
];
