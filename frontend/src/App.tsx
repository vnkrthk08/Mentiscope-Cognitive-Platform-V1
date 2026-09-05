import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { User, UserRole } from "./types";
import { AuthService } from "./services/auth/AuthService";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import StudentDashboard from "./pages/StudentDashboard";
import AssessmentRunner from "./pages/AssessmentRunner";
import ReportPage from "./pages/ReportPage";
import SuperAdminDashboard from "./pages/SuperAdminDashboard";
import EditProfilePage from "./pages/EditProfilePage";
import GVAssessmentPage from "./pages/GVAssessmentPage";
import { AssessmentService } from "./services/assessment/AssessmentService";
import { MODULE_CONFIGS } from "./config/moduleConfig";
import { motion, AnimatePresence } from "motion/react";
import { ShieldAlert, AlertTriangle } from "lucide-react";

const pageToPath: Record<string, string> = {
  landing: "/",
  auth: "/auth",
  dashboard: "/dashboard",
  assessment: "/dashboard/exam",
  "gv-assessment": "/dashboard/gv-exam",
  profile: "/dashboard/profile",
  report: "/report",
  admin: "/admin"
};

const pathToPage: Record<string, string> = {
  "/": "landing",
  "/home": "landing",
  "/auth": "auth",
  "/login": "auth",
  "/dashboard": "dashboard",
  "/dashboard/exam": "assessment",
  "/exam": "assessment",
  "/dashboard/gv-exam": "gv-assessment",
  "/gv-exam": "gv-assessment",
  "/dashboard/profile": "profile",
  "/profile": "profile",
  "/report": "report",
  "/admin": "admin"
};

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(() => AuthService.getCurrentUser());
  const [authTab, setAuthTab] = useState<string>("student-login");

  // Navigation Guard / Exit Confirm Modal state
  const [showExitModal, setShowExitModal] = useState<boolean>(false);
  const [pendingNavigation, setPendingNavigation] = useState<{ page: string; targetTab?: string } | null>(null);

  const getPageFromPath = (path: string): string => {
    if (path.startsWith("/dashboard/gv-exam") || path.startsWith("/gv-exam")) return "gv-assessment";
    if (path.startsWith("/dashboard/exam") || path.startsWith("/exam")) return "assessment";
    if (path.startsWith("/dashboard/results")) return "dashboard";
    return pathToPage[path] || "landing";
  };

  const [currentPage, setCurrentPage] = useState<string>(() => {
    return getPageFromPath(location.pathname);
  });

  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("mentiscope_theme");
    return saved === "dark" ? "dark" : "light";
  });

  const [soundEnabled, setSoundEnabled] = useState<boolean>(() => {
    const saved = localStorage.getItem("mentiscope_sound");
    return saved !== "false";
  });

  // Sync theme
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("mentiscope_theme", theme);
  }, [theme]);

  // Sync sound preference
  useEffect(() => {
    localStorage.setItem("mentiscope_sound", String(soundEnabled));
  }, [soundEnabled]);

  // Sync browser URL location changes -> currentPage state
  useEffect(() => {
    const targetPage = getPageFromPath(location.pathname);
    if (targetPage === "auth" && user) {
      const targetDashboard = user.role === UserRole.SUPER_ADMIN ? "admin" : "dashboard";
      setCurrentPage(targetDashboard);
      navigate(pageToPath[targetDashboard] || "/dashboard", { replace: true });
      return;
    }
    if (targetPage !== currentPage) {
      // If candidate is inside active exam and clicks browser back/forward URL change
      const isQuizActive = sessionStorage.getItem("quiz_in_progress") === "true";
      if (currentPage === "assessment" && targetPage !== "assessment" && isQuizActive) {
        setShowExitModal(true);
        setPendingNavigation({ page: targetPage });
        // Revert URL to /dashboard/exam until confirmed
        navigate(location.pathname, { replace: true });
      } else {
        setCurrentPage(targetPage);
      }
    }
  }, [location.pathname, user]);

  // Browser refresh / tab close guard when taking exam
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (currentPage === "assessment") {
        e.preventDefault();
        e.returnValue = "Warning: If you leave now, your exam progress will not be saved.";
        return e.returnValue;
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [currentPage]);

  const executeNavigation = (page: string, targetTab?: string) => {
    if (targetTab) {
      setAuthTab(targetTab);
    }
    setCurrentPage(page);

    const targetPath = pageToPath[page] || "/";
    if (location.pathname !== targetPath) {
      navigate(targetPath);
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
    setTimeout(() => {
      const scrollContainer = document.getElementById("landing-scroll-container");
      if (scrollContainer) {
        scrollContainer.scrollTo({ top: 0, behavior: "smooth" });
      }
    }, 10);
  };

  const handleNavigate = (page: string, targetTab?: string) => {
    // If user is already logged in and navigating to auth/login page, redirect directly to dashboard
    if (page === "auth" && user) {
      const targetDashboard = user.role === UserRole.SUPER_ADMIN ? "admin" : "dashboard";
      executeNavigation(targetDashboard);
      return;
    }

    // Intercept navigation if candidate is currently taking an exam
    const isQuizActive = sessionStorage.getItem("quiz_in_progress") === "true";
    if (currentPage === "assessment" && page !== "assessment" && isQuizActive) {
      setPendingNavigation({ page, targetTab });
      setShowExitModal(true);
      return;
    }
    executeNavigation(page, targetTab);
  };

  const confirmExitExam = () => {
    setShowExitModal(false);
    if (pendingNavigation) {
      executeNavigation(pendingNavigation.page, pendingNavigation.targetTab);
      setPendingNavigation(null);
    }
  };

  const cancelExitExam = () => {
    setShowExitModal(false);
    setPendingNavigation(null);
  };

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(loggedInUser);
    if (loggedInUser.role === UserRole.SUPER_ADMIN) {
      handleNavigate("admin");
    // } else if (loggedInUser.role === UserRole.INTERN) { // Intern role handling removed
      // handleNavigate("intern"); // Intern navigation removed
    } else {
      handleNavigate("dashboard");
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setUser(null);
    handleNavigate("landing");
  };

  const handleStartAssessment = () => {
    if (!user) {
      handleNavigate("auth");
    } else if (user.role === UserRole.STUDENT) {
      const activeSession = AssessmentService.getOrCreateSession(user.id);
      const selectedModule = MODULE_CONFIGS[activeSession.currentModuleIndex];
      handleNavigate(AssessmentService.getRunnerPage(selectedModule?.id || ""));
    } else {
      alert("Please log in as a student candidate to start cognitive assessments.");
    }
  };

  // State-Based Router Switch with URL Syncing
  const renderPage = () => {
    switch (currentPage) {
      case "landing":
        return <LandingPage user={user} onNavigate={handleNavigate} />;
      case "auth":
        if (user) {
          if (user.role === UserRole.SUPER_ADMIN) {
            return <SuperAdminDashboard user={user} onNavigate={handleNavigate} />;
          }
          return (
            <StudentDashboard
              user={user}
              onNavigate={handleNavigate}
              onStartAssessment={handleStartAssessment}
            />
          );
        }
        return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
      case "dashboard":
        if (!user) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return (
          <StudentDashboard
            user={user}
            onNavigate={handleNavigate}
            onStartAssessment={handleStartAssessment}
          />
        );
      case "assessment":
        const activeCandidate = user || {
          id: "stud_demo_candidate",
          name: "Candidate Student",
          email: "student@mentiscope.org",
          role: UserRole.STUDENT
        };
        return <AssessmentRunner user={activeCandidate} onNavigate={handleNavigate} soundEnabled={soundEnabled} />;
      case "gv-assessment":
        const gvCandidate = user || {
          id: "stud_demo_candidate",
          name: "Candidate Student",
          email: "student@mentiscope.org",
          role: UserRole.STUDENT,
          token: ""
        };
        return <GVAssessmentPage user={gvCandidate} onNavigate={handleNavigate} />;
      case "report":
        if (!user) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return <ReportPage user={user} onNavigate={handleNavigate} />;

      case "profile":
        if (!user) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return (
          <EditProfilePage 
            user={user}
            onSave={(updatedUser) => {
              setUser(updatedUser);
              AuthService.saveUserSession(updatedUser);
              handleNavigate("dashboard");
            }}
            onCancel={() => handleNavigate("dashboard")}
          />
        );

      case "admin":
        if (!user || user.role !== UserRole.SUPER_ADMIN) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return <SuperAdminDashboard user={user} onNavigate={handleNavigate} />;
      default:
        return <LandingPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans selection:bg-blue-600/10 selection:text-blue-600 transition-colors duration-300">
      
      {/* Dynamic Header */}
      <Navbar
        user={user}
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
        theme={theme}
        setTheme={setTheme}
        soundEnabled={soundEnabled}
        setSoundEnabled={setSoundEnabled}
      />

      {/* Main Page Area */}
      <main className="flex-1">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* EXAM EXIT CONFIRMATION MODAL DIALOG */}
      <AnimatePresence>
        {showExitModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="w-full max-w-md rounded-3xl border border-rose-500/30 bg-white dark:bg-slate-900 p-6 sm:p-7 shadow-2xl space-y-6"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 shrink-0">
                  <ShieldAlert className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
                    Exit Cognitive Assessment?
                  </h3>
                  <p className="text-xs font-mono font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider mt-0.5">
                    Unsaved Progress Alert
                  </p>
                </div>
              </div>

              <div className="bg-rose-50/60 dark:bg-rose-950/30 p-4 rounded-2xl border border-rose-100 dark:border-rose-900/40 space-y-1.5 text-xs text-rose-900 dark:text-rose-200">
                <div className="flex items-center gap-1.5 font-bold">
                  <AlertTriangle className="h-4 w-4 shrink-0 text-rose-600 dark:text-rose-400" />
                  <span>Warning: Progress Will Be Lost</span>
                </div>
                <p className="leading-relaxed font-sans text-[11px] opacity-90">
                  If you leave or navigate away from the test area now, your active exam progress will not be saved and your ongoing session will be terminated.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <button
                  onClick={cancelExitExam}
                  className="flex-1 rounded-xl bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 text-xs font-bold transition-all shadow-md shadow-blue-500/20 active:scale-[0.98]"
                >
                  Stay & Continue Exam
                </button>
                <button
                  onClick={confirmExitExam}
                  className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-rose-50 dark:hover:bg-rose-950/40 hover:text-rose-600 dark:hover:text-rose-400 px-4 py-3 text-xs font-bold transition-all active:scale-[0.98]"
                >
                  Exit Without Saving
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
