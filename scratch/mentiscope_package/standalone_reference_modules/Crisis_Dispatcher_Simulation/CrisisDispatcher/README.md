# 🚨 Crisis Dispatcher

An emergency response simulation platform that evaluates emotional regulation of higher secondary students (Grades 11–12) through behavioural assessment.

## Tech Stack

- **Frontend:** React 19, Vite 6, Ant Design 5, Recharts, React Router 7
- **Backend:** Node.js, Express.js, MongoDB (Mongoose), JWT Authentication
- **Architecture:** REST API, Modular folder structure

## Getting Started

### Prerequisites
- Node.js 18+
- MongoDB (local or Atlas)

### 1. Clone and Install

```bash
# Install server dependencies
cd server
npm install

# Install client dependencies
cd ../client
npm install
```

### 2. Configure Environment

Edit `server/.env` with your MongoDB URI and JWT secret.

### 3. Seed Admin Account

```bash
cd server
npm run seed
```

Default admin: `admin@crisisapp.com` / `Admin@123`

### 4. Start Development

```bash
# Terminal 1: Start backend
cd server
npm run dev

# Terminal 2: Start frontend
cd client
npm run dev
```

- Frontend: http://localhost:5173
- Backend: http://localhost:5000

## Assessment Modules

| Module | Purpose | Key Metrics |
|--------|---------|-------------|
| 1. Baseline | Normal decision-making | Reaction Time, Accuracy |
| 2. Stress | Stress tolerance | Panic Clicks, RT under pressure |
| 3. Failure & Recovery | Recovery after setbacks | Recovery Latency, Persistence |
| 4. Adaptive Challenge | Adaptability | Strategy Changes, Adaptation Rate |

## Scoring Dimensions (Weighted)

- **Recovery & Resilience** — 30%
- **Stress Tolerance** — 25%
- **Adaptation & Persistence** — 25%
- **Decision Stability** — 20%

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register | Public | Student registration |
| POST | /api/auth/login | Public | Login |
| GET | /api/student/profile | Student | Get profile |
| GET | /api/student/result | Student | Get results |
| POST | /api/assessment/start | Student | Start assessment |
| POST | /api/assessment/event | Student | Log event |
| POST | /api/assessment/complete | Student | Complete & score |
| GET | /api/admin/dashboard | Admin | Dashboard stats |
| GET | /api/admin/students | Admin | Student list |
| GET | /api/admin/events | Admin | Event logs |
| GET | /api/admin/results | Admin | Results & analytics |
