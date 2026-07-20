import { CognitiveReport } from "../../types";

export class ReportService {
  /**
   * Generates a cognitive evaluation report based on module score percentages.
   */
  static generateReport(
    sessionId: string,
    studentName: string,
    studentAge: number,
    studentGender: string,
    moduleScores: { [moduleId: string]: number }
  ): CognitiveReport {
    const keys = Object.keys(moduleScores);
    const sum = keys.reduce((acc, k) => acc + moduleScores[k], 0);
    const average = keys.length > 0 ? Math.round(sum / keys.length) : 0;

    // Default heuristics for strengths/weaknesses
    const strengths: string[] = [];
    const weaknesses: string[] = [];
    const recommendations: string[] = [];

    // Map module key to human name
    const moduleNames: { [key: string]: string } = {
      gq: "General Cognitive Quotient",
      gsm: "Working Memory (GSM)",
      gf: "Fluid Intelligence (GF)",
      attention: "Attention & Cognitive Control",
      language: "Linguistic & Verbal Reasoning",
      executive: "Executive Function",
      "processing-speed": "Cognitive Processing Speed"
    };

    keys.forEach(k => {
      const score = moduleScores[k];
      const name = moduleNames[k] || k;
      if (score >= 80) {
        strengths.push(name);
      } else if (score < 60) {
        weaknesses.push(name);
      }
    });

    // Fallbacks if empty
    if (strengths.length === 0) {
      // Find highest score
      let highestKey = keys[0];
      keys.forEach(k => {
        if (moduleScores[k] > (moduleScores[highestKey] || 0)) {
          highestKey = k;
        }
      });
      if (highestKey) strengths.push(moduleNames[highestKey] || highestKey);
    }

    if (weaknesses.length === 0) {
      // Find lowest score
      let lowestKey = keys[0];
      keys.forEach(k => {
        if (moduleScores[k] < (moduleScores[lowestKey] || 100)) {
          lowestKey = k;
        }
      });
      if (lowestKey && moduleScores[lowestKey] < 80) {
        weaknesses.push(moduleNames[lowestKey] || lowestKey);
      }
    }

    // Default static recommendations
    recommendations.push("Engage in deliberate visual matrix challenges to enhance Fluid Intelligence (GF).");
    recommendations.push("Utilize mnemonic chunking strategies and dual n-back sessions to scale Working Memory span.");
    recommendations.push("Practice focused attention mindfulness drills to overcome cognitive interference in high-pressure tasks.");
    recommendations.push("Incorporate structured cognitive scheduling and micro-goal setting to offload Executive demands.");

    return {
      sessionId,
      studentName,
      studentAge,
      studentGender,
      date: new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }),
      durationMinutes: 24, // Simulated average time
      overallScore: average,
      moduleScores,
      strengths,
      weaknesses,
      recommendations,
      isAiGenerated: false
    };
  }

  /**
   * Contacts our server's backend Gemini endpoint to generate high-fidelity,
   * professional psychological diagnostics instead of static text.
   */
  static async fetchAiInsights(report: CognitiveReport): Promise<CognitiveReport> {
    try {
      const response = await fetch("/api/gemini/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ report })
      });

      if (!response.ok) {
        throw new Error("Failed to contact server AI analyzer");
      }

      const data = await response.json();
      if (data && data.insights) {
        return {
          ...report,
          strengths: data.insights.strengths || report.strengths,
          weaknesses: data.insights.weaknesses || report.weaknesses,
          recommendations: data.insights.recommendations || report.recommendations,
          isAiGenerated: true
        };
      }
    } catch (e) {
      console.warn("AI insights retrieval failed, using standard heuristics:", e);
    }
    return report;
  }
}
