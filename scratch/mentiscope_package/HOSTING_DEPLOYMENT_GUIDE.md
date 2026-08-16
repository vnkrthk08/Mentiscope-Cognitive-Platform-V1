# 🌐 Mentiscope Production Hosting & Deployment Guide

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
