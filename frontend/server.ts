import express from "express";
import path from "path";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import { securityHeaders } from "./src/middleware/securityHeaders";
import { apiRateLimiter } from "./src/middleware/rateLimit";
import cookieParser from "cookie-parser";
import { corsMiddleware } from "./src/middleware/cors";
import { csrfProtection } from "./src/middleware/csrf";
import { staticFiles } from "./src/middleware/staticFiles";
import { apiV1Router } from "./src/routes/v1";

dotenv.config();

const app = express();
const PORT = parseInt(process.env.PORT || "5173", 10);

app.use(express.json());
app.use(securityHeaders);
app.use("/api", apiRateLimiter);
app.use(corsMiddleware);
app.use(cookieParser());
// app.use(csrfProtection);
app.use("/api/v1", csrfProtection);
app.use(staticFiles);

// Mount version 1 api routes
app.use("/api/v1", apiV1Router);

// Proxy Processing Speed, Fluid Intelligence, Visual Processing & Sessions API requests to the Python backend
const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";
app.all(["/api/modules/processing-speed*", "/api/modules/gf*", "/api/modules/csr*", "/api/modules/gv*", "/api/quantitative*", "/api/sessions*"], async (req, res) => {
  const targetUrl = `${BACKEND_URL}${req.originalUrl}`;
  try {
    const headers: Record<string, string> = {};
    for (const [key, value] of Object.entries(req.headers)) {
      if (typeof value === "string") {
        headers[key] = value;
      }
    }
    delete headers["host"];
    delete headers["expect"];

    const response = await fetch(targetUrl, {
      method: req.method,
      headers: headers,
      body: req.method !== "GET" && req.method !== "HEAD" ? JSON.stringify(req.body) : undefined,
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error: any) {
    console.error("Proxy error forwarding to Python backend:", error);
    res.status(500).json({ error: "Failed to connect to backend", details: error.message });
  }
});

// Initialize server-side Gemini client with recommended telemetry agent
const getGeminiClient = () => {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey || apiKey === "MY_GEMINI_API_KEY") {
    console.warn("GEMINI_API_KEY is not defined or is placeholder. Using mock analyzer fallback.");
    return null;
  }
  return new GoogleGenAI({
    apiKey: apiKey,
    httpOptions: {
      headers: {
        "User-Agent": "aistudio-build",
      },
    },
  });
};

// POST api/gemini/analyze to provide premium AI-powered cognitive coaching recommendations
app.post("/api/gemini/analyze", async (req, res) => {
  try {
    const { report } = req.body;
    if (!report) {
      return res.status(400).json({ error: "Missing report payload" });
    }

    const ai = getGeminiClient();
    if (!ai) {
      // Graceful local fallback if API key is not configured yet
      return res.json({
        insights: {
          strengths: report.strengths || ["Visual Processing (Gv)", "Attention Control"],
          weaknesses: report.weaknesses || ["Working Memory (Gsm)"],
          recommendations: [
            "Practice dual n-back working memory exercises daily for 10 minutes to expand executive span.",
            "Organize complex reasoning task structures visually before analyzing multi-factor matrices.",
            "Perform Stroop interference warm-up drills to sharpen visual focus under strict time pressure.",
            "Structure problem-solving environments to systematically offload high working-memory demands."
          ]
        }
      });
    }

    const promptText = `
      You are an expert neuropsychologist and cognitive assessment interpreter. 
      Analyze the following student's cognitive score results and generate a premium evaluation.
      
      Student Name: ${report.studentName}
      Age: ${report.studentAge}
      Gender: ${report.studentGender}
      
      Module Scores (percentage 0-100 where higher is superior cognitive capability):
      ${JSON.stringify(report.moduleScores, null, 2)}
      
      Requirements:
      1. strengths: Pick the top 2-3 modules where they excelled and provide high-level professional commentary explaining why they represent high cognitive assets.
      2. weaknesses: Pick the 1-2 modules with the lowest scores and explain the clinical or educational challenge this might represent.
      3. recommendations: Generate exactly 4 precise, scientifically-grounded, actionable coaching items, brain training games, or study techniques tailored directly to their profile.
    `;

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: promptText,
      config: {
        systemInstruction: "You are a professional educational psychologist specialized in quantitative cognitive evaluation. Deliver concise, supportive, and precise diagnostics.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            strengths: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "2 to 3 professional cognitive assets."
            },
            weaknesses: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "1 to 2 cognitive categories representing potential friction points."
            },
            recommendations: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "Exactly 4 high-value psychological coaching recommendation sentences."
            }
          },
          required: ["strengths", "weaknesses", "recommendations"]
        }
      }
    });

    const jsonStr = response.text ? response.text.trim() : "";
    if (jsonStr) {
      const parsedInsights = JSON.parse(jsonStr);
      return res.json({ insights: parsedInsights });
    } else {
      throw new Error("Empty text response received from Gemini.");
    }
  } catch (error: any) {
    console.error("Gemini analysis api error:", error);
    res.status(500).json({ error: "Failed to perform cognitive analysis", details: error.message });
  }
});

// API health endpoint
app.get("/api/health", (req, res) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

app.get("/api/version", (req, res) => {
  const pkg = require(path.join(process.cwd(), "package.json"));
  res.json({
    version: pkg.version,
    commit: process.env.COMMIT_HASH || "none",
    buildDate: process.env.BUILD_DATE || new Date().toISOString()
  });
});

app.post("/api/auth/refresh", (req, res) => {
  const refreshToken = req.cookies?.refreshToken;
  if (!refreshToken) {
    return res.status(401).json({ error: "No refresh token" });
  }
  // In a real app, verify the refresh token and issue a new access token
  const newAccessToken = "newAccessTokenMock";
  res.json({ accessToken: newAccessToken });
});

app.post("/api/auth/logout", (req, res) => {
  res.clearCookie("refreshToken");
  res.json({ success: true });
});

// Setup dev server or static file handlers
async function boot() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
    console.log("Vite development server middleware loaded.");
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
    console.log("Serving static production assets from dist/ folder.");
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server is running at http://localhost:${PORT}`);
  });
}

boot();
