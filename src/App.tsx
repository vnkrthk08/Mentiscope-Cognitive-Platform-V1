import React, { useState, useEffect } from "react";
import { User, UserRole } from "./types";
import { AuthService } from "./services/auth/AuthService";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import StudentDashboard from "./pages/StudentDashboard";
import AssessmentRunner from "./pages/AssessmentRunner";
import ReportPage from "./pages/ReportPage";
import InternDashboard from "./pages/InternDashboard";
import SuperAdminDashboard from "./pages/SuperAdminDashboard";
import { motion, AnimatePresence } from "motion/react";

export default function App() {
  const [currentPage, setCurrentPage] = useState<string>("landing");
  const [user, setUser] = useState<User | null>(null);
  const [authTab, setAuthTab] = useState<string>("student-login");

  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("mentiscope_theme");
    return saved === "dark" ? "dark" : "light";
  });

  const [soundEnabled, setSoundEnabled] = useState<boolean>(() => {
    const saved = localStorage.getItem("mentiscope_sound");
    return saved !== "false";
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("mentiscope_theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("mentiscope_sound", String(soundEnabled));
  }, [soundEnabled]);

  // Sync user state on mount
  useEffect(() => {
    const saved = AuthService.getCurrentUser();
    if (saved) {
      setUser(saved);
    }
  }, []);

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage("landing");
  };

  const handleNavigate = (page: string, targetTab?: string) => {
    if (targetTab) {
      setAuthTab(targetTab);
    }
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Redirect to sign-in helper
  const handleStartAssessment = () => {
    if (!user) {
      handleNavigate("auth");
    } else if (user.role === UserRole.STUDENT) {
      handleNavigate("assessment");
    } else {
      alert("Please log in as a student candidate to start cognitive assessments.");
    }
  };

  // State-Based Router Switch
  const renderPage = () => {
    switch (currentPage) {
      case "landing":
        return <LandingPage onNavigate={handleNavigate} />;
      case "auth":
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
        if (!user) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return <AssessmentRunner user={user} onNavigate={handleNavigate} soundEnabled={soundEnabled} />;
      case "report":
        if (!user) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return <ReportPage user={user} onNavigate={handleNavigate} />;
      case "intern":
        if (!user || user.role !== UserRole.INTERN) {
          return <AuthPage onLoginSuccess={handleLoginSuccess} onNavigate={handleNavigate} initialTab={authTab} />;
        }
        return <InternDashboard user={user} onNavigate={handleNavigate} />;
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

      {/* Main Page Canvas with Micro-Animations */}
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22, ease: "easeInOut" }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>

    </div>
  );
}
