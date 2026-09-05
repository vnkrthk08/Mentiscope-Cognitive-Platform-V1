# 🧠 Mentiscope - Multi-Module Cognitive & Psychometric Assessment Platform

> **Incubated at NIRMAAN, IIT Madras (Pre-Incubator)**  
> *Scientifically Validated, AI-Powered Cognitive Evaluation Battery*

---

## 📌 Executive Overview

**Mentiscope** is a state-of-the-art cognitive evaluation capsule developed by a multidisciplinary team of AI researchers, technologists, and psychometricians. It bridges human potential and opportunity through standardized, data-driven cognitive battery testing across 10 scientific pillars:

1. **Fluid Intelligence ($G_f$)**
2. **Crystallized Intelligence ($G_c$)**
3. **Quantitative Reasoning ($G_q$)**
4. **Visual Processing ($G_v$)**
5. **Processing Speed ($G_s$)**
6. **Working Memory & Retrieval ($G_{sm}$)**
7. **RIASEC Vocational Interest Profiling**
8. **Attention & Executive Cognitive Control**
9. **Emotional Regulation & Stability**
10. **Auditory & Verbal Cognitive Assessment**

---

## 📁 Server-Host-Ready Repository Architecture

The repository is organized into distinct **Frontend** and **Backend** service directories, container-ready with Docker and Docker Compose:

```text
mentiscope-live-integration/
├── frontend/                     # React 19 + Vite + TypeScript Application
│   ├── src/                      # UI Components, Assessment Runner, Reports
│   ├── public/                   # Static Audio & Image Assets
│   ├── index.html                # Vite HTML Entrypoint
│   ├── package.json              # Node.js Dependencies & Build Scripts
│   ├── vite.config.ts            # Vite Configuration
│   ├── tsconfig.json             # TypeScript Configuration
│   ├── server.ts                 # Express Gateway & Reverse Proxy
│   ├── Dockerfile                # Production Container Definition
│   └── README.md                 # Frontend Documentation
│
├── backend/                      # Python FastAPI + SQLite Service
│   ├── main.py                   # FastAPI Application & Route Definitions
│   ├── database.py               # SQLAlchemy Database Connection Pool
│   ├── core_models.py            # SQLite Schema & Session Models
│   ├── auth_router.py            # Candidate Authentication & Management
│   ├── mentiscope.db             # Persistent SQLite Candidate Database
│   ├── requirements.txt          # Python Dependencies
│   ├── modules/                  # 10 Cognitive Assessment Batteries
│   │   ├── processing_speed/     # Gs Battery
│   │   ├── fluid_intelligence/   # Gf Battery
│   │   ├── gsm/                  # Working Memory
│   │   ├── csr/                  # Attention & Cognitive Control
│   │   ├── gv/                   # Visual Processing
│   │   ├── quantitative/         # Gq Battery
│   │   └── auditory_verbal/      # Module 10 Auditory & Verbal Battery
│   ├── Dockerfile                # Production Container Definition
│   └── README.md                 # Backend Documentation
│
├── docker-compose.yml            # Multi-Container Host Orchestration
├── .gitignore                    # Unified Clean Git Ignore Rules
└── README.md                     # Platform Documentation
```

---

## 🚀 Quickstart & Server Hosting

### Option 1: One-Click Docker Compose (Production Hosting)

```bash
# Build and run both Frontend (5173) and Backend (8000)
docker compose up --build -d
```

### Option 2: Running Locally

#### 1. Start Backend Service (Port 8000)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Start Frontend Service (Port 5173)
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** to access the application.
