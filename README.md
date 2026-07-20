<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/9b5bee05-8bce-4813-bf7a-da7deab36df8

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

## Processing Speed module

Run the module API separately during development:

```bash
python -m pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

The Vite dev server proxies `/api/modules/processing-speed` to port 8000. The module is registered as `processing-speed` and exposes `POST /start`, `POST /answer`, `POST /finish`, and `GET /result` beneath that prefix.
