# 🧠 Mentiscope - Multi-Module Cognitive Assessment Platform
> **Incubated at NIRMAAN, IIT Madras (Pre-Incubator)**
> *Production Deployment & Hosting Package*

---

## 📁 Package Organization

This package is structured specifically for production web hosting and deployment:

```text
mentiscope-production-package/
├── frontend/                     # React 19 + TypeScript + Vite Client Application
│   ├── src/                      # UI Components, Pages, State, Services
│   ├── public/                   # Static Public Assets
│   ├── package.json              # Frontend Dependencies & Scripts
│   ├── vite.config.ts            # Vite Build Configuration
│   └── server.ts                 # Production Express Server & Proxy Bridge
│
├── backend/                      # Python FastAPI Psychometric Engine
│   ├── modules/                  # 6 Core Cognitive Engines (Gs, Gf, Gv, Gsm, CSR, Gq)
│   ├── core_models.py            # SQLite Database Schemas & Session Store
│   ├── database.py               # SQLAlchemy Database Engine Connection
│   ├── main.py                   # FastAPI Application Entrypoint
│   ├── requirements.txt          # Python Backend Dependencies
│   └── mentiscope.db             # Pre-seeded SQLite Database
│
├── database/                     # Database Artifacts & SQL Migrations
│   ├── mentiscope.db             # Initialized SQLite Database
│   └── migrations/               # Schema Creation & Analytics SQL Migrations
│
├── docs/                         # Specifications & Engineering Guidelines
│   ├── API_SWAGGER_SPEC.yaml     # OpenAPI 3.0 REST Specification
│   ├── ARCHITECTURE_INTEGRATION_GUIDE.md
│   ├── AI_AGENTS_DEVELOPER_GUIDE.md
│   └── PROCESSING_SPEED_SPEC.md
│
├── standalone_reference_modules/ # Standalone reference builds & Postman collections
│   ├── ASAT_Attention_Task/
│   ├── Crisis_Dispatcher_Simulation/
│   ├── CSR_Stress_Resilience/
│   ├── Fluid_Intelligence_MVP/
│   └── Synapse_Quantitative_Engine/
│
├── scripts/                      # Migration & Recovery Automation Scripts
├── docker-compose.yml            # Containerized Production Orchestration
├── HOSTING_DEPLOYMENT_GUIDE.md   # Step-by-Step Production Hosting Guide
└── README.md
```

---

## 🚀 Quick Start (Local or Server)

### 1. Launch Backend (FastAPI - Port 8000)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Launch Frontend (React / Vite - Port 5173 / 3000)
```bash
cd frontend
npm install
npm run dev
```

Visit the application at: `http://localhost:5173`

---

## ☁️ Production Hosting Options

Refer to `HOSTING_DEPLOYMENT_GUIDE.md` for full instructions on deploying to:
- **Docker / Docker Compose** (Single command deployment)
- **Vercel / Netlify** (Frontend) + **Render / Railway** (Backend)
- **AWS EC2 / DigitalOcean Droplet / Ubuntu Linux VPS** (Nginx + PM2 + Systemd)
