import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ScreenId, StudentProfile, AppEvent, SessionScores } from '../types';
import type { AssessmentResult, BackendQuestion } from '../services/assessmentApi';

interface AssessmentContextType {
  // Global View/Module State
  currentScreen: ScreenId;
  setCurrentScreen: React.Dispatch<React.SetStateAction<ScreenId>>;
  currentModule: string;
  setCurrentModule: React.Dispatch<React.SetStateAction<string>>;
  currentQuestion: BackendQuestion | null;
  setCurrentQuestion: React.Dispatch<React.SetStateAction<BackendQuestion | null>>;

  // User/Session State
  profile: StudentProfile | null;
  setProfile: React.Dispatch<React.SetStateAction<StudentProfile | null>>;
  assessmentId: string | null;
  setAssessmentId: React.Dispatch<React.SetStateAction<string | null>>;
  sessionId: string | null;
  setSessionId: React.Dispatch<React.SetStateAction<string | null>>;

  // Progress/Results State
  completedScreens: string[];
  setCompletedScreens: React.Dispatch<React.SetStateAction<string[]>>;
  sessionScores: SessionScores | null;
  setSessionScores: React.Dispatch<React.SetStateAction<SessionScores | null>>;
  backendResult: any | null;
  setBackendResult: React.Dispatch<React.SetStateAction<any | null>>;

  // Telemetry Log State
  events: AppEvent[];
  setEvents: React.Dispatch<React.SetStateAction<AppEvent[]>>;
  showLoggerDock: boolean;
  setShowLoggerDock: React.Dispatch<React.SetStateAction<boolean>>;

  // Helpers
  logEvent: (action: string, status: 'SUCCESS' | 'INFO' | 'WARNING' | 'ERROR', details: string, payload?: any) => void;
  handleNavigate: (target: ScreenId) => void;
  handleInitializeIdentity: (newProfile: StudentProfile) => void;
  handleChallengeComplete: (screen: ScreenId, xpEarned: number, unused?: null, result?: any) => void;
  handleCompleteSession: (finalScores: SessionScores, sessionEvents: AppEvent[], result?: any | null) => void;
  handleClearLogs: () => void;
}

export const AssessmentContext = createContext<AssessmentContextType | undefined>(undefined);

export const useAssessment = () => {
  const context = useContext(AssessmentContext);
  if (!context) {
    throw new Error('useAssessment must be used within an AssessmentProvider');
  }
  return context;
};

export const AssessmentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentScreen, setCurrentScreen] = useState<ScreenId>('splash');
  const [currentModule, setCurrentModule] = useState<string>('gq');
  const [currentQuestion, setCurrentQuestion] = useState<BackendQuestion | null>(null);
  
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const [sessionScores, setSessionScores] = useState<SessionScores | null>(null);
  const [backendResult, setBackendResult] = useState<any | null>(null);
  const [completedScreens, setCompletedScreens] = useState<string[]>([]);
  const [showLoggerDock, setShowLoggerDock] = useState(false);

  const [events, setEvents] = useState<AppEvent[]>([
    {
      id: 'evt-init-sys',
      timestamp: '04:41:02',
      screen: 'splash',
      action: 'SYSTEM_BOOT',
      status: 'SUCCESS',
      details: 'Neural Synaptic Cognitive Core booted successfully.',
    },
    {
      id: 'evt-ws-sys',
      timestamp: '04:41:03',
      screen: 'splash',
      action: 'WEBSOCKET_OPEN',
      status: 'INFO',
      details: 'Metric pipeline connected to secure educational DB cluster.',
    }
  ]);

  const logEvent = (action: string, status: 'SUCCESS' | 'INFO' | 'WARNING' | 'ERROR', details: string, payload?: any) => {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    const newEvent: AppEvent = {
      id: `evt-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: timeStr,
      screen: currentScreen,
      action,
      status,
      details,
      payload,
    };
    setEvents((prev) => [newEvent, ...prev]);
  };

  const handleNavigate = (target: ScreenId) => {
    logEvent('Screen Navigation', 'INFO', `Switched viewport matrix to ${target.toUpperCase()}`);
    setCurrentScreen(target);
  };

  const handleInitializeIdentity = (newProfile: StudentProfile) => {
    setProfile(newProfile);
    setCurrentScreen('gq-assessment');
  };

  const handleChallengeComplete = (screen: ScreenId, xpEarned: number, unused?: null, result?: any) => {
    if (!completedScreens.includes(screen)) {
      setCompletedScreens((prev) => [...prev, screen]);
    }
    
    if (result) {
      setBackendResult(result);
    }
    
    if (profile) {
      const nextXp = profile.xp + xpEarned;
      const nextLevel = Math.floor(nextXp / 1000) + 1;
      
      let nextSessionScores = profile.lastSessionScores;
      
      if (result && result.module_name && result.metrics && result.metrics.accuracy !== undefined) {
        const baseScores = nextSessionScores || {
          rawScore: 0,
          normalizedScore: 0,
          percentile: 50,
          subScores: { PatternBot: 0, CompareBot: 0, VisionBot: 0, SolverBot: 0 },
          confidenceScore: 0.8
        };
        
        const moduleName = result.module_name;
        // Map accuracy (0-1) to score (0-100) or use existing raw scores
        const newScore = Math.max(10, Math.round(result.metrics.accuracy * 100));
        
        const newSubScores = {
          ...baseScores.subScores,
          [moduleName]: newScore
        };
        
        const scoresArr = Object.values(newSubScores);
        const newNormalizedScore = Math.round(scoresArr.reduce((a, b) => a + (b as number), 0) / scoresArr.length);
        
        nextSessionScores = {
          ...baseScores,
          subScores: newSubScores as any,
          normalizedScore: newNormalizedScore
        };
      }
      
      setProfile((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          xp: nextXp,
          level: nextLevel,
          lastSessionScores: nextSessionScores,
          completedNodes: Array.from(new Set([...prev.completedNodes, screen])),
        };
      });
      
      logEvent('XP MILESTONE AWARDED', 'SUCCESS', `Awarded +${xpEarned} XP to student profile. Level is now ${nextLevel}.`);
    }

    if (screen === 'solver-route' || screen === 'neural-core' || screen === 'pattern-bot' || screen === 'decision-core' || screen === 'vision-bot' || screen === 'analytics-core') {
      setTimeout(() => {
        setCurrentScreen('success');
      }, 1000);
    }
  };

  const handleCompleteSession = (finalScores: SessionScores, sessionEvents: AppEvent[], result?: any | null) => {
    setSessionScores(finalScores);
    setBackendResult(result ?? null);
    
    // Calculate base XP based on normalized score
    let xpEarned = Math.round(finalScores.normalizedScore * 10);
    
    // Time-weighted bonus logic
    if (result?.metrics?.average_reaction_time) {
      const avgReactionTime = result.metrics.average_reaction_time;
      // Faster times give a multiplier. E.g. < 4000ms gives bonus up to 1.5x
      const timeBonus = Math.max(1.0, 1.5 - (avgReactionTime / 12000));
      xpEarned = Math.round(xpEarned * timeBonus);
    }
    
    if (profile) {
      const nextXp = profile.xp + xpEarned;
      const nextLevel = Math.floor(nextXp / 1000) + 1;
      
      setProfile({
        ...profile,
        xp: nextXp,
        level: nextLevel,
        lastSessionScores: finalScores,
        completedNodes: Array.from(new Set([...profile.completedNodes, 'gq-assessment']))
      });
      
      logEvent('XP MILESTONE AWARDED', 'SUCCESS', `Awarded +${xpEarned} XP for Gq Assessment. Level is now ${nextLevel}.`);
    }
    setEvents((prev) => [...sessionEvents, ...prev]);
    if (!completedScreens.includes('gq-assessment')) {
      setCompletedScreens((prev) => [...prev, 'gq-assessment']);
    }
    setCurrentScreen('success');
  };

  const handleClearLogs = () => {
    setEvents([]);
    logEvent('Telemetry cleared', 'WARNING', 'User purged event queue');
  };

  return (
    <AssessmentContext.Provider value={{
      currentScreen, setCurrentScreen,
      currentModule, setCurrentModule,
      currentQuestion, setCurrentQuestion,
      profile, setProfile,
      assessmentId, setAssessmentId,
      sessionId, setSessionId,
      completedScreens, setCompletedScreens,
      sessionScores, setSessionScores,
      backendResult, setBackendResult,
      events, setEvents,
      showLoggerDock, setShowLoggerDock,
      logEvent,
      handleNavigate,
      handleInitializeIdentity,
      handleChallengeComplete,
      handleCompleteSession,
      handleClearLogs
    }}>
      {children}
    </AssessmentContext.Provider>
  );
};
