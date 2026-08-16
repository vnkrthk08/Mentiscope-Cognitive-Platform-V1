import os
import shutil
import zipfile

BASE_DIR = r"C:\Users\venka\Desktop\trail iitm\mentiscope-live-integration"
OUTPUT_DIR = os.path.join(BASE_DIR, "scratch", "mentiscope_package")
ZIP_OUTPUT = r"C:\Users\venka\Desktop\Mentiscope_Production_Host_Ready.zip"

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Create directory structure
dirs_to_create = [
    "frontend",
    "frontend/public",
    "frontend/src",
    "backend",
    "backend/modules",
    "database",
    "database/migrations",
    "docs",
    "scripts",
    "standalone_reference_modules",
]
for d in dirs_to_create:
    os.makedirs(os.path.join(OUTPUT_DIR, d), exist_ok=True)

# 2. Helper copy functions
def copy_dir(src, dst, ignore_patterns=None):
    if not os.path.exists(src):
        return
    if ignore_patterns is None:
        ignore_patterns = ["node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".git", "*.pyc"]
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignore_patterns))

def copy_file(src, dst):
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

print("Copying Frontend files...")
copy_dir(os.path.join(BASE_DIR, "src"), os.path.join(OUTPUT_DIR, "frontend", "src"))
copy_dir(os.path.join(BASE_DIR, "public"), os.path.join(OUTPUT_DIR, "frontend", "public"))
for f in ["index.html", "package.json", "package-lock.json", "tsconfig.json", "vite.config.ts", "server.ts", ".env.example"]:
    copy_file(os.path.join(BASE_DIR, f), os.path.join(OUTPUT_DIR, "frontend", f))

print("Copying Backend files...")
copy_dir(os.path.join(BASE_DIR, "backend", "modules"), os.path.join(OUTPUT_DIR, "backend", "modules"))
if os.path.exists(os.path.join(BASE_DIR, "backend", "gf_engine")):
    copy_dir(os.path.join(BASE_DIR, "backend", "gf_engine"), os.path.join(OUTPUT_DIR, "backend", "gf_engine"))

for f in ["main.py", "core_models.py", "database.py", "auth_router.py", "crisisScoringEngine.ts", "requirements.txt"]:
    copy_file(os.path.join(BASE_DIR, "backend", f), os.path.join(OUTPUT_DIR, "backend", f))

# Also copy requirements.txt to backend if missing
copy_file(os.path.join(BASE_DIR, "requirements.txt"), os.path.join(OUTPUT_DIR, "backend", "requirements.txt"))
copy_file(os.path.join(BASE_DIR, "mentiscope.db"), os.path.join(OUTPUT_DIR, "backend", "mentiscope.db"))

print("Copying Database files...")
copy_file(os.path.join(BASE_DIR, "mentiscope.db"), os.path.join(OUTPUT_DIR, "database", "mentiscope.db"))
if os.path.exists(os.path.join(BASE_DIR, "src", "db", "migrations")):
    copy_dir(os.path.join(BASE_DIR, "src", "db", "migrations"), os.path.join(OUTPUT_DIR, "database", "migrations"))

print("Copying Documentation...")
copy_file(os.path.join(BASE_DIR, "swagger.yaml"), os.path.join(OUTPUT_DIR, "docs", "API_SWAGGER_SPEC.yaml"))
copy_file(os.path.join(BASE_DIR, "INTEGRATION_GUIDE.md"), os.path.join(OUTPUT_DIR, "docs", "ARCHITECTURE_INTEGRATION_GUIDE.md"))
copy_file(os.path.join(BASE_DIR, "AGENTS.md"), os.path.join(OUTPUT_DIR, "docs", "AI_AGENTS_DEVELOPER_GUIDE.md"))
copy_file(os.path.join(BASE_DIR, "001_processing_speed.md"), os.path.join(OUTPUT_DIR, "docs", "PROCESSING_SPEED_SPEC.md"))

print("Copying Scripts...")
if os.path.exists(os.path.join(BASE_DIR, "scripts")):
    copy_dir(os.path.join(BASE_DIR, "scripts"), os.path.join(OUTPUT_DIR, "scripts"))
copy_file(os.path.join(BASE_DIR, "restore_and_run.py"), os.path.join(OUTPUT_DIR, "scripts", "restore_and_run.py"))

print("Copying Standalone Reference Modules...")
copy_dir(os.path.join(BASE_DIR, "ASAT_MentiScope_Integration_Ready"), os.path.join(OUTPUT_DIR, "standalone_reference_modules", "ASAT_Attention_Task"))
copy_dir(os.path.join(BASE_DIR, "CrisisDispatcher"), os.path.join(OUTPUT_DIR, "standalone_reference_modules", "Crisis_Dispatcher_Simulation"))
copy_dir(os.path.join(BASE_DIR, "mentiscope_csr"), os.path.join(OUTPUT_DIR, "standalone_reference_modules", "CSR_Stress_Resilience"))
copy_dir(os.path.join(BASE_DIR, "scratch_gf_module"), os.path.join(OUTPUT_DIR, "standalone_reference_modules", "Fluid_Intelligence_MVP"))
copy_dir(os.path.join(BASE_DIR, "synapse"), os.path.join(OUTPUT_DIR, "standalone_reference_modules", "Synapse_Quantitative_Engine"), ignore_patterns=["node_modules", "dist", ".venv", "venv", "__pycache__", "*.pyc"])

print("Writing Deployment & Hosting Documentation...")

# 1. Master README
with open(os.path.join(OUTPUT_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write("""# 🧠 Mentiscope - Multi-Module Cognitive Assessment Platform
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
""")

# 2. Frontend README
with open(os.path.join(OUTPUT_DIR, "frontend", "README.md"), "w", encoding="utf-8") as f:
    f.write("""# 🎨 Mentiscope Frontend Client
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS + Motion (Framer Motion)
- **Icons**: Lucide Icons
- **Data Viz**: Recharts + Custom SVG Visualizers

### Local Development:
```bash
npm install
npm run dev
```

### Production Build:
```bash
npm run build
```
Static production output will be generated in `dist/`.
""")

# 3. Backend README
with open(os.path.join(OUTPUT_DIR, "backend", "README.md"), "w", encoding="utf-8") as f:
    f.write("""# ⚙️ Mentiscope Psychometric Backend API
- **Framework**: FastAPI (Python 3.11+) + Uvicorn
- **ORM & DB**: SQLAlchemy + SQLite (`mentiscope.db`)
- **Validation**: Pydantic v2

### Local Execution:
```bash
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive API Documentation:
Visit `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc`.
""")

# 4. Docker Compose
with open(os.path.join(OUTPUT_DIR, "docker-compose.yml"), "w", encoding="utf-8") as f:
    f.write("""version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mentiscope-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./mentiscope.db
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mentiscope-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: always
""")

# 5. Backend Dockerfile
with open(os.path.join(OUTPUT_DIR, "backend", "Dockerfile"), "w", encoding="utf-8") as f:
    f.write("""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

# 6. Frontend Dockerfile
with open(os.path.join(OUTPUT_DIR, "frontend", "Dockerfile"), "w", encoding="utf-8") as f:
    f.write("""FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
""")

# 7. HOSTING_DEPLOYMENT_GUIDE.md
with open(os.path.join(OUTPUT_DIR, "HOSTING_DEPLOYMENT_GUIDE.md"), "w", encoding="utf-8") as f:
    f.write("""# 🌐 Mentiscope Production Hosting & Deployment Guide

This guide covers step-by-step instructions for hosting Mentiscope on popular cloud providers.

---

## 📦 Option 1: Docker Compose (Recommended for Any VPS / AWS EC2 / DigitalOcean)

1. Upload the extracted folder to your server via SSH/SFTP.
2. Run:
```bash
docker compose up -d --build
```
3. Your application is live at `http://your-server-ip:5173` with the backend at `http://your-server-ip:8000`.

---

## ☁️ Option 2: Split Cloud Hosting (Vercel + Render)

### Frontend on Vercel:
1. Connect your repository or drag & drop the `frontend/` folder into [Vercel](https://vercel.com).
2. Framework Preset: `Vite`.
3. Root Directory: `frontend`.
4. Deploy!

### Backend on Render / Railway:
1. Create a **Web Service** on [Render](https://render.com) or [Railway](https://railway.app).
2. Root Directory: `backend`.
3. Environment: `Python 3`.
4. Build Command: `pip install -r requirements.txt`.
5. Start Command: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`.

---

## 🖥️ Option 3: Ubuntu Linux Server (Nginx + PM2 + Gunicorn/Uvicorn)

### 1. Backend Setup:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
# Run in background via systemd or pm2:
pm2 start "python3 -m uvicorn main:app --host 127.0.0.1 --port 8000" --name mentiscope-api
```

### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run build
# Serve dist folder using Nginx
```

### 3. Nginx Reverse Proxy Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /var/www/mentiscope/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
""")

print("Creating ZIP file...")
if os.path.exists(ZIP_OUTPUT):
    os.remove(ZIP_OUTPUT)

with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, OUTPUT_DIR)
            zipf.write(full_path, rel_path)

zip_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
print(f"SUCCESS! Zip created at: {ZIP_OUTPUT} ({zip_size_mb:.2f} MB)")
