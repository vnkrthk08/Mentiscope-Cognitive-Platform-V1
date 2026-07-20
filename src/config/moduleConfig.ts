import { ModuleConfig } from "../types";

export const MODULE_CONFIGS: ModuleConfig[] = [
  {
    id: "gq",
    name: "General Cognitive Quotient",
    description: "Evaluates comprehensive deductive reasoning, logical deduction, and spatial pattern completion.",
    icon: "Brain",
    apiBaseUrl: "/api/modules/gq",
    estimatedTime: "4 mins",
    color: "blue",
    enabled: true
  },
  {
    id: "gsm",
    name: "Working Memory (GSM)",
    description: "Measures visual and auditory short-term recall using progressive span recall challenges.",
    icon: "Activity",
    apiBaseUrl: "/api/modules/gsm",
    estimatedTime: "5 mins",
    color: "teal",
    enabled: true
  },
  {
    id: "gf",
    name: "Fluid Intelligence (GF)",
    description: "Assesses capacity to think logically, analyze relationships, and solve novel visual matrix problems.",
    icon: "Cpu",
    apiBaseUrl: "/api/modules/gf",
    estimatedTime: "5 mins",
    color: "indigo",
    enabled: true
  },
  {
    id: "attention",
    name: "Attention & Cognitive Control",
    description: "Tests focus retention, inhibitory control, and cognitive resistance using Stroop stimuli.",
    icon: "Eye",
    apiBaseUrl: "/api/modules/attention",
    estimatedTime: "3 mins",
    color: "rose",
    enabled: true
  },
  {
    id: "language",
    name: "Linguistic & Verbal Reasoning",
    description: "Evaluates lexical comprehension, syntactic analysis, word associations, and semantic logic.",
    icon: "Languages",
    apiBaseUrl: "/api/modules/language",
    estimatedTime: "4 mins",
    color: "violet",
    enabled: true
  },
  {
    id: "executive",
    name: "Executive Function",
    description: "Measures planning, goal maintenance, sorting rules, and visual puzzle solving.",
    icon: "GitBranch",
    apiBaseUrl: "/api/modules/executive",
    estimatedTime: "5 mins",
    color: "amber",
    enabled: true
  },
  {
    id: "processing-speed",
    name: "Cognitive Processing Speed",
    description: "Measures speed of visual identification and motor-free decision making under progressive pressure.",
    icon: "Zap",
    apiBaseUrl: "/api/modules/processing-speed",
    estimatedTime: "3 mins",
    color: "emerald",
    enabled: true
  }
];
