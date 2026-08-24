import { ModuleConfig } from "../types";

export const MODULE_CONFIGS: ModuleConfig[] = [
  {
    id: "gf",
    name: "Fluid Intelligence (Gf)",
    taskName: "Rule Discovery Task",
    researcher: "Pranav Kumaravel",
    description: "Evaluates capacity to reason logically, identify novel abstract patterns, and solve unpracticed visual matrix problems using inductive and deductive rule discovery.",
    icon: "Cpu",
    apiBaseUrl: "/api/modules/gf",
    estimatedTime: "1m 45s",
    color: "indigo",
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
    estimatedTime: "4 mins",
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
    estimatedTime: "5 mins",
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
    estimatedTime: "3 mins",
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
    estimatedTime: "3 mins",
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
    estimatedTime: "6 mins",
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
    estimatedTime: "6 mins",
    color: "red",
    enabled: true
  }
];
