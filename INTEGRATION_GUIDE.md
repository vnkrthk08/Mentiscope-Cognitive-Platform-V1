# Mentiscope Cognitive Assessment Platform - Integration Guide

Welcome! This guide is written to help developers and AI assistants understand the architecture of Mentiscope and follow the exact same guidelines, styles, and data structures to integrate new cognitive modules or update existing ones.

---

## 1. Project Overview & Context
Mentiscope is a cognitive assessment platform incubated at **NIRMAAN, IIT Madras**. The landing page contains a 7-module snap-scroll structure, a scientific foundation visual hub using `/image1.png` at 100% opacity, and an assessment guidelines overview card.

### Key Details & Contacts:
- **Email Contact**: `assesmentcognitive@gmail.com`
- **Phone Contacts**: `9037188431`, `9947783548`
- **Project Branding Logo**: Located at [public/logo_mentiscope.png](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/public/logo_mentiscope.png) (used for navigation headers and footers).
- **Incubator Logo (NIRMAAN)**: Located at [public/logo.svg](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/public/logo.svg) (retained for incubation credentials and badges).
- **Tab Title & Favicon**: Customized in [index.html](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/index.html) to show **Mentiscope** referencing the PNG icon.

---

## 2. Core Assessment Battery (The 7 Pillars)
The platform is built around a standardized 7-module battery. Spatial and perceptual modules (M8 & M9) have been removed.

| ID | Module Name | Key Metrics Logged |
|----|-------------|--------------------|
| **M1** | Processing Speed | Choice reaction latency, keypress correctness, accuracy curve |
| **M2** | Attention Control | Focus shift time, distractor omission/commission errors |
| **M3** | Working Memory | Target matching correctness, response lag |
| **M4** | Lexical Memory | Recall word recognition speed, association hits |
| **M5** | Memory Span | Sequence recall length, forward/backward sequence checks |
| **M6** | Fluid Intelligence | Pattern deduction response times, matrix accuracy |
| **M7** | Cognitive Flexibility | Switch cost latency (task rule switching), target accuracy |

---

## 3. Architecture & Configurations

### A. Registering & Configuring Modules
Cognitive modules are defined in [src/config/moduleConfig.ts](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/src/config/moduleConfig.ts):
- Every module has a unique ID (`M1` to `M7`), visual icon, brief description, duration indicator, and completion badge.
- When creating a new module, add its metadata to `MODULE_CONFIGS`.

### B. Questions & Test Data
Questions, trial structures, or test parameters are stored in [src/config/questionsData.ts](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/src/config/questionsData.ts):
- Standardized datasets (like processing speed stimuli, word lists, or matrix patterns) should be declared here.
- This separates test data from visual component logic, making localization and customization effortless.

---

## 4. Guidelines for Integrating a New Cognitive Test Module

Follow this step-by-step workflow to integrate a new cognitive assessment module:

### Step 1: Create the Test Page Component
Create a new React component under `src/pages/` (e.g., `AttentionTest.tsx` or `FluidTest.tsx`).
- **Layout & Aesthetics**: Use the global modern glassmorphic theme. Use HSL blue/teal accents. Ensure support for both dark mode and light mode.
- **Instruction Stage**: Start with an introduction view outlining the task rules, keyboard controls, and interactive mock trials (sandbox demo).
- **Live Assessment Stage**: Ensure a distraction-free environment. Provide clean visual prompts, progress bars, and keyboard event listeners (`keydown`).
- **Data Capture**: Log every trial's latency (in milliseconds using `performance.now()`), response correct/incorrect state, and sequence number.

### Step 2: Implement Active Proctoring / Tab Focus Tracking
To ensure candidate integrity, implement real-time focus tracking using standard Page Visibility APIs:
```typescript
useEffect(() => {
  const handleVisibilityChange = () => {
    if (document.hidden) {
      // User minimized the tab, switched applications, or changed windows
      console.warn("Active Proctoring Warning: Tab focus lost.");
      // Increment focus violation flag, pause timer, or show alert modal
    }
  };

  document.addEventListener("visibilitychange", handleVisibilityChange);
  return () => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
  };
}, []);
```

### Step 3: Register Routing & Navigation in App.tsx
- Locate [src/App.tsx](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/src/App.tsx).
- Add state routing to manage navigation to the new test view when a candidate launches it from the main dashboard or current assessment flow.

### Step 4: Handle State Saving & Final Reports
- Store completed test scores in `localStorage` or push to the backend server.
- Update [src/pages/ReportPage.tsx](file:///c:/Users/venka/Desktop/trail%20iitm/mentiscope-processing-speed-live-integration/src/pages/ReportPage.tsx) to read the new score data, compute percentiles, and display visual bar charts/gauges matching the other 7 modules.

---

## 5. Design Checklist (Senior Web Designer Rules)
- **Contrast Guidelines**: Ensure all text has proper contrast on both dark and light modes.
- **Interactive Micro-animations**: Use subtle scale/hover triggers (`hover:scale-102 transition-all duration-300`) for all primary buttons and widgets.
- **Icons**: Utilize the `lucide-react` package for consistent vector iconography.
- **Responsive Layout**: Design mobile-first using responsive Tailwind grids (`grid-cols-1 lg:grid-cols-12`). Ensure it is comfortable on desktop browsers.

Happy coding! Let's keep the user experience premium, smooth, and scientifically accurate.
