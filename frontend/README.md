# Mentiscope Cognitive Platform - Frontend Service

The web client for the Mentiscope Cognitive Assessment Battery built with React 19, TypeScript, Tailwind CSS v4, Recharts, and Express.

## Available Scripts

In the `frontend` directory:

```bash
# Run local development server (port 5173 with proxy to backend port 8000)
npm run dev

# Build production client and server bundles
npm run build

# Start production server
npm run start
```

## Environment Configuration

Copy `.env.example` to `.env`:

```env
PORT=5173
BACKEND_URL=http://127.0.0.1:8000
GEMINI_API_KEY=your_gemini_api_key_here
```
