# Mentiscope Cognitive Assessment Platform

Mentiscope is a modern, scientific cognitive assessment platform incubated at **NIRMAAN, IIT Madras**. This repository contains the full web platform integration including the **Processing Speed (Gs)** assessment module and backend API services.

---

## 🚀 Getting Started

Follow these steps to clone, set up, and run the project locally on any machine:

### 1. Clone the repository
```bash
git clone https://github.com/vnkrthk08/Mentiscope-Main-v1v.git
cd Mentiscope-Main-v1v
```

### 2. Install & Start Frontend
```bash
npm install
npm run dev
```

### 3. Install & Start Backend (in a separate terminal)
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

---

## 🛠️ Project Architecture

- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + Motion
- **Backend API**: FastAPI (Python 3.13+) + SQLAlchemy + SQLite
- **Proxy**: Vite dev server proxies `/api/modules/processing-speed` requests directly to `http://localhost:8000`.

---

## 🧠 Core Assessment Battery (7 Pillars)

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

## 📧 Contact & Credentials
- **Incubated at**: NIRMAAN, IIT Madras
- **Email Contact**: assesmentcognitive@gmail.com
- **Phone Contacts**: +91 9037188431 | +91 9947783548
