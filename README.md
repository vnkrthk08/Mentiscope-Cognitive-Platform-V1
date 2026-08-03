# 🧠 Mentiscope - Multi-Module Cognitive & Psychometric Assessment Platform

> **Incubated at NIRMAAN, IIT Madras (Pre-Incubator)**  
> *Scientifically Validated, AI-Powered Cognitive Evaluation Battery*

---

## 📌 Executive Overview

**Mentiscope** is a state-of-the-art cognitive evaluation capsule developed by a multidisciplinary team of AI researchers, technologists, and psychometricians. It bridges human potential and opportunity through standardized, data-driven cognitive battery testing.

The platform measures foundational cognitive domains—such as **Processing Speed ($G_s$)**, **Fluid Intelligence ($G_f$)**, **Visual Processing ($G_v$)**, **Working Memory Span ($G_{sm}$)**, **Cognitive Stress & Resilience (CSR)**, and **Quantitative Reasoning ($G_q$)**—delivering instant norm-referenced scores, visual analytics, and personalized coaching recommendations.

---

## ✨ Key Features & Capability Matrix

- **Adaptive Psychometric Engine**: Dynamic item difficulty scaling (Tiers 1–9) with live accuracy and speed-bonus weighting.
- **ROM-like Persistent Session Storage**: Full assessment history and reports synced to SQLite (`mentiscope.db`) across logins and refreshes.
- **Interactive Analog Chronograph**: Live SVG time-tracking dial and real-time running score HUD.
- **Multi-Role Authentication**: Dedicated portals for Candidate Students and Super Administrators.
- **Visual Processing ($G_v$) Battery**: Includes Mental Rotation (SR), Paper Folding (Vz), Hidden Figures (CF), and Mystery Map Builder (CS/SS).
- **Interactive AI Coaching Reports**: Instant PDF/Visual diagnostic dashboards with norm-referenced percentiles.

---

## 🛠️ Technology Stack

| Layer | Technology Used |
|-------|-----------------|
| **Frontend Framework** | React 19 + TypeScript + Vite |
| **Styling & UI** | Tailwind CSS + Motion (Framer Motion) + Lucide Icons |
| **Data Visualization** | Recharts + Custom SVG Engine |
| **Backend API** | Python 3.13+ + FastAPI + Uvicorn |
| **ORM & Database** | SQLAlchemy + SQLite (`mentiscope.db`) |
| **Proxy / Server** | Express.js (Node.js) + Vite Dev Middleware |

---

## 📁 Repository Structure

```text
mentiscope-live-integration/
├── backend/                        # Python FastAPI Backend Services
│   ├── modules/
│   │   ├── processing_speed/       # Processing Speed (Gs) Engine & Router
│   │   ├── fluid_intelligence/     # Fluid Intelligence (Gf) Engine & Router
│   │   ├── gv/                     # Visual Processing (Gv) Battery Engine
│   │   ├── gsm/                    # Working Memory Span (Gsm) Engine
│   │   ├── csr/                    # Cognitive Stress & Resilience (CSR) Engine
│   │   └── quantitative/           # Quantitative Reasoning Engine
│   ├── core_models.py              # SQLAlchemy DB Models (SavedAssessmentSession, Users)
│   ├── database.py                 # SQLite Engine Connection & Session Pool
│   └── main.py                     # Primary FastAPI Application Entrypoint
├── src/                            # React 19 + TypeScript Frontend
│   ├── components/                 # Reusable UI (Navbar, Footer, Modals)
│   ├── config/                     # Module Configurations & Item Banks
│   ├── context/                    # Auth & Quiz Context Providers
│   ├── modules/                    # Subtest Renderers (GVItemRenderer, etc.)
│   ├── pages/                      # Application Views (LandingPage, StudentDashboard, AssessmentRunner, ReportPage)
│   ├── services/                   # AssessmentService & AuthService
│   └── types/                      # TypeScript Interface Definitions
├── server.ts                       # Express Server & Proxy Bridge to Port 8000
├── package.json                    # Frontend Dependencies & Scripts
├── requirements.txt                # Python Backend Dependencies
└── README.md                       # Project Documentation
```

---

## 🚀 Local Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/vnkrthk08/Mentiscope-Main-v1v.git
cd Mentiscope-Main-v1v
```

### 2. Install & Run Frontend
```bash
# Install Node.js dependencies
npm install

# Start Express & Vite Development Server (Port 5173)
npm run dev
```

### 3. Install & Run Backend (In a Separate Terminal)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI Backend (Port 8000)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Cognitive Module Battery Breakdown

| Module ID | Construct Name | Evaluated Domain |
|-----------|----------------|------------------|
| **Gs** | Processing Speed | Rapid visual discrimination & motor-free decision speed |
| **Gf** | Fluid Intelligence | Matrix reasoning, pattern deduction & abstract logic |
| **Gv** | Visual Processing | Mental rotation, paper folding, hidden figures & spatial scanning |
| **Gsm** | Working Memory | Forward/backward digit spans & spatial grid sequence recall |
| **CSR** | Stress & Resilience | Decision stability under high-pressure time constraints |
| **Gq** | Quantitative Reasoning | Numerical problem-solving & mathematical logic |

---

## 📧 Contact & Organizational Metadata

- **Incubation Partner**: The Pre-Incubator, NIRMAAN, IIT Madras, Chennai, India  
- **Email**: `assesmentcognitive@gmail.com`  
- **Support Contacts**: `+91 90371 88431` | `+91 99477 83548`  
- **License**: Proprietary / All Rights Reserved © 2026 Mentiscope  
