import React, { useRef } from "react";
import { User } from "../types";
import { MODULE_CONFIGS } from "../config/moduleConfig";
import { AssessmentService } from "../services/assessment/AssessmentService";
import GVAssessmentModule from "../modules/gv/GVAssessmentModule";
import { GV_CONSTRUCT, GVFinalResult, GV_MODULE_ID } from "../modules/gv/types";

interface Props {
  user: User;
  onNavigate: (page: string) => void;
}

export default function GVAssessmentPage({ user, onNavigate }: Props) {
  const session = useRef(AssessmentService.getOrCreateSession(user.id)).current;
  const context = {
    student_id: user.id,
    session_id: session.sessionId,
    module_id: GV_MODULE_ID,
    module_name: "Visual Processing Battery" as const,
    construct: GV_CONSTRUCT,
    difficulty: 2,
    access_token: user.token,
  };

  const handleCompleted = (result: GVFinalResult) => {
    const latest = AssessmentService.getSession() || session;
    const gvIndex = MODULE_CONFIGS.findIndex((module) => module.id === "gv");
    const updated = {
      ...latest,
      moduleScores: { ...latest.moduleScores, gv: result.metrics.raw_score },
      moduleMetrics: { ...(latest.moduleMetrics || {}), gv: result },
      currentModuleIndex: Math.max(latest.currentModuleIndex, gvIndex + 1),
      currentQuestionIndex: 0,
    };
    AssessmentService.saveSession(updated);
  };

  return <GVAssessmentModule context={context} onCompleted={handleCompleted} onExit={() => onNavigate("dashboard")} />;
}
