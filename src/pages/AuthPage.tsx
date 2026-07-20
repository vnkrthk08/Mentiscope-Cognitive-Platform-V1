import React, { useState } from "react";
import { AuthService } from "../services/auth/AuthService";
import { User, UserRole } from "../types";
import { 
  Brain, 
  Lock, 
  Mail, 
  User as UserIcon, 
  ChevronRight, 
  CheckSquare, 
  HelpCircle,
  FileText,
  KeyRound,
  ShieldAlert,
  ArrowLeft
} from "lucide-react";

interface AuthPageProps {
  onLoginSuccess: (user: User) => void;
  onNavigate: (page: string) => void;
  initialTab?: string;
}

type TabType = "student-login" | "student-register" | "intern-login" | "admin-login" | "forgot-password";

export default function AuthPage({ onLoginSuccess, onNavigate, initialTab }: AuthPageProps) {
  const [activeTab, setActiveTab] = useState<TabType>((initialTab as TabType) || "student-login");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  React.useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab as TabType);
    }
  }, [initialTab]);

  // Forms state
  const [rememberMe, setRememberMe] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Registration Form State
  const [regForm, setRegForm] = useState({
    name: "",
    email: "",
    age: "",
    gender: "Male",
    state: "Tamil Nadu",
    district: "Chennai",
    education: "Undergraduate",
    course: "Bachelor of Science",
    specialization: "Psychology",
    previousPercentage: "",
    collegeType: "Private",
    consent: false
  });

  const handleSetDemoCredentials = (role: UserRole) => {
    setError(null);
    setMessage(null);
    if (role === UserRole.STUDENT) {
      setLoginEmail("alex.mercer@candidate.edu");
      setLoginPassword("student123");
      setActiveTab("student-login");
    } else if (role === UserRole.INTERN) {
      setLoginEmail("clara@mentiscope.org");
      setLoginPassword("intern123");
      setActiveTab("intern-login");
    } else if (role === UserRole.SUPER_ADMIN) {
      setLoginEmail("admin@mentiscope.org");
      setLoginPassword("admin123");
      setActiveTab("admin-login");
    }
  };

  const handleStudentLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!loginEmail) {
      setError("Email address is required.");
      return;
    }
    setLoading(true);
    try {
      const user = await AuthService.studentLogin(loginEmail, rememberMe);
      onLoginSuccess(user);
      onNavigate("dashboard");
    } catch (e: any) {
      setError(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleInternLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!loginEmail || !loginPassword) {
      setError("Both ID/Email and password are required.");
      return;
    }
    setLoading(true);
    try {
      const user = await AuthService.internLogin(loginEmail, loginPassword);
      onLoginSuccess(user);
      onNavigate("intern");
    } catch (e: any) {
      setError(e.message || "Intern verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!loginEmail || !loginPassword) {
      setError("Email and password are required.");
      return;
    }
    setLoading(true);
    try {
      const user = await AuthService.adminLogin(loginEmail, loginPassword);
      onLoginSuccess(user);
      onNavigate("admin");
    } catch (e: any) {
      setError(e.message || "Admin login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleStudentRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!regForm.name || !regForm.email || !regForm.age || !regForm.previousPercentage || !regForm.district) {
      setError("Please complete all required demographic fields.");
      return;
    }
    const ageNum = parseInt(regForm.age);
    if (isNaN(ageNum) || ageNum < 15 || ageNum > 90) {
      setError("Please provide a valid participant age (15 to 90 years).");
      return;
    }
    const pctNum = parseFloat(regForm.previousPercentage);
    if (isNaN(pctNum) || pctNum < 0 || pctNum > 100) {
      setError("Please provide a valid previous examination percentage (0 to 100).");
      return;
    }
    if (!regForm.consent) {
      setError("Candidates must read and acknowledge the cognitive evaluation consent form.");
      return;
    }

    setLoading(true);
    try {
      const user = await AuthService.studentRegister({
        name: regForm.name,
        email: regForm.email,
        age: ageNum,
        gender: regForm.gender,
        state: regForm.state,
        district: regForm.district,
        education: regForm.education,
        course: regForm.course,
        specialization: regForm.specialization,
        previousExamPercentage: pctNum,
        collegeType: regForm.collegeType,
        consent: true
      });
      onLoginSuccess(user);
      onNavigate("dashboard");
    } catch (e: any) {
      setError(e.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!loginEmail) {
      setError("Please type your registered email.");
      return;
    }
    setLoading(true);
    try {
      await AuthService.requestForgotPassword(loginEmail);
      setMessage("A password reset link has been dispatched to your email address.");
      setTimeout(() => setActiveTab("student-login"), 3000);
    } catch (e: any) {
      setError("Failed to transmit forgot password link.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4 sm:p-6 lg:p-8 transition-colors duration-300 relative overflow-hidden">
      {/* Background ambient glowing radial effects */}
      <div className="absolute -left-20 -top-20 w-96 h-96 bg-blue-600/5 dark:bg-blue-600/10 blur-3xl rounded-full pointer-events-none" />
      <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-indigo-600/5 dark:bg-indigo-600/10 blur-3xl rounded-full pointer-events-none" />

      <div className="w-full max-w-lg bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-3xl p-5 sm:p-6 shadow-xl dark:shadow-none relative z-10 space-y-4">
        
        <div className="flex items-center gap-3 border-b border-slate-100 dark:border-slate-800/60 pb-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-500/10">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-sans font-extrabold tracking-tight text-2xl sm:text-3xl text-slate-950 dark:text-white leading-none">Mentiscope</h1>
            <p className="text-[9px] font-sans font-bold tracking-wider text-blue-600 dark:text-blue-400 uppercase mt-1">Gateway Portal</p>
          </div>
        </div>

        {/* Error alerts */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/30 text-xs font-semibold text-rose-800 dark:text-rose-400 flex items-start gap-2.5">
            <ShieldAlert className="h-4.5 w-4.5 shrink-0 text-rose-600 dark:text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Success message */}
        {message && (
          <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 text-xs font-semibold text-emerald-800 dark:text-emerald-400">
            {message}
          </div>
        )}

        {/* A. STUDENT LOGIN */}
        {activeTab === "student-login" && (
          <form onSubmit={handleStudentLogin} className="space-y-4">
            <div className="space-y-1.5">
              <h2 className="text-xl font-bold tracking-tight text-slate-950 dark:text-white">Candidate Assessment Login</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Access your saved evaluation session to start or resume cognitive testing.</p>
            </div>

            <div className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Candidate Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <input
                    type="email"
                    required
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="alex.mercer@candidate.edu"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-9 pr-3.5 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-1.5 font-semibold text-slate-700 dark:text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded border-slate-300 dark:border-slate-800 text-blue-600 bg-white dark:bg-slate-950 focus:ring-blue-500"
                  />
                  <span>Remember Candidate ID</span>
                </label>

                <button
                  type="button"
                  onClick={() => setActiveTab("forgot-password")}
                  className="font-bold text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Forgot Credentials?
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700 shadow-sm"
            >
              {loading ? "Establishing Session..." : "Access Candidate Portal"}
              <ChevronRight className="h-4 w-4" />
            </button>

            <div className="pt-2 text-center space-y-2">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("student-register");
                    setError(null);
                    setMessage(null);
                  }}
                  className="font-bold text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Create one here
                </button>
              </p>
              <div className="border-t border-slate-100 dark:border-slate-800/60 my-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("admin-login");
                    setError(null);
                    setMessage(null);
                  }}
                  className="text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400"
                >
                  Are you an administrator? Access Admin Portal
                </button>
              </div>
            </div>
          </form>
        )}

        {/* C. SUPER ADMIN LOGIN */}
        {activeTab === "admin-login" && (
          <form onSubmit={handleAdminLogin} className="space-y-4">
            <div className="space-y-1.5">
              <h2 className="text-xl font-bold tracking-tight text-slate-950 dark:text-white">Super Administrator Login</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Sign in with root administrative access to manage modules, students, settings, and logs.</p>
            </div>

            <div className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Administrator Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <input
                    type="email"
                    required
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="admin@mentiscope.org"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-9 pr-3.5 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Security Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <input
                    type="password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-9 pr-3.5 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700 shadow-sm"
            >
              {loading ? "Verifying Root Security..." : "Authorise & Enter System"}
              <ChevronRight className="h-4 w-4" />
            </button>

            <div className="pt-2 text-center">
              <button
                type="button"
                onClick={() => {
                  setActiveTab("student-login");
                  setError(null);
                  setMessage(null);
                }}
                className="text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400"
              >
                Are you a candidate? Return to Candidate Sign In
              </button>
            </div>
          </form>
        )}

        {/* D. CANDIDATE REGISTER */}
        {activeTab === "student-register" && (
          <form onSubmit={handleStudentRegister} className="space-y-4">
            <div className="space-y-1">
              <h2 className="text-xl font-bold tracking-tight text-slate-950 dark:text-white">Candidate Registration</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Mentiscope requires baseline demographics to score cognitive deviations correctly.</p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 max-h-[35vh] overflow-y-auto pr-2 border-y border-slate-100 dark:border-slate-800/80 py-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Full Name *</label>
                <input
                  type="text"
                  required
                  value={regForm.name}
                  onChange={(e) => setRegForm({ ...regForm, name: e.target.value })}
                  placeholder="Alex Mercer"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Email Address *</label>
                <input
                  type="email"
                  required
                  value={regForm.email}
                  onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
                  placeholder="alex@gmail.com"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Age *</label>
                <input
                  type="number"
                  required
                  value={regForm.age}
                  onChange={(e) => setRegForm({ ...regForm, age: e.target.value })}
                  placeholder="21"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Gender *</label>
                <select
                  value={regForm.gender}
                  onChange={(e) => setRegForm({ ...regForm, gender: e.target.value })}
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                >
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other / Non-binary</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">State / Region *</label>
                <input
                  type="text"
                  required
                  value={regForm.state}
                  onChange={(e) => setRegForm({ ...regForm, state: e.target.value })}
                  placeholder="Tamil Nadu"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">District *</label>
                <input
                  type="text"
                  required
                  value={regForm.district}
                  onChange={(e) => setRegForm({ ...regForm, district: e.target.value })}
                  placeholder="Chennai"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Current Education *</label>
                <select
                  value={regForm.education}
                  onChange={(e) => setRegForm({ ...regForm, education: e.target.value })}
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                >
                  <option>High School</option>
                  <option>Undergraduate</option>
                  <option>Postgraduate</option>
                  <option>Doctorate / PHD</option>
                  <option>Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Current Course *</label>
                <input
                  type="text"
                  required
                  value={regForm.course}
                  onChange={(e) => setRegForm({ ...regForm, course: e.target.value })}
                  placeholder="Bachelor of Science"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Specialization *</label>
                <input
                  type="text"
                  required
                  value={regForm.specialization}
                  onChange={(e) => setRegForm({ ...regForm, specialization: e.target.value })}
                  placeholder="Cognitive Science"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Previous Exam Score (%) *</label>
                <input
                  type="number"
                  required
                  value={regForm.previousPercentage}
                  onChange={(e) => setRegForm({ ...regForm, previousPercentage: e.target.value })}
                  placeholder="88.5"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">School / College Type *</label>
                <select
                  value={regForm.collegeType}
                  onChange={(e) => setRegForm({ ...regForm, collegeType: e.target.value })}
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none"
                >
                  <option>Govt</option>
                  <option>Private</option>
                </select>
              </div>
            </div>

            {/* Consent Checkbox */}
            <div className="bg-blue-50/50 dark:bg-blue-950/20 p-3 rounded-xl border border-blue-100/60 dark:border-blue-900/30 text-[11px] space-y-1.5 text-left">
              <div className="flex gap-2">
                <input
                  type="checkbox"
                  id="consent-check"
                  checked={regForm.consent}
                  onChange={(e) => setRegForm({ ...regForm, consent: e.target.checked })}
                  className="rounded border-slate-300 dark:border-slate-850 text-blue-600 bg-white dark:bg-slate-950 focus:ring-blue-500 mt-0.5"
                />
                <label htmlFor="consent-check" className="font-semibold text-slate-700 dark:text-slate-300 cursor-pointer">
                  I consent to submit my anonymised assessment data for psychometric research profiling.
                </label>
              </div>
              <p className="text-[10px] text-slate-400 dark:text-slate-500 pl-6 leading-normal">
                By submitting, you acknowledge that this study measures cognitive variables and does not constitute a clinical psychiatric diagnosis.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700 shadow-sm"
            >
              {loading ? "Registering Candidate..." : "Start Assessment Session"}
              <ChevronRight className="h-4 w-4" />
            </button>

            <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-4">
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setActiveTab("student-login");
                  setError(null);
                  setMessage(null);
                }}
                className="font-bold text-blue-600 dark:text-blue-400 hover:underline"
              >
                Sign in
              </button>
            </p>
          </form>
        )}

        {/* E. FORGOT PASSWORD */}
        {activeTab === "forgot-password" && (
          <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
            <button
              type="button"
              onClick={() => setActiveTab("student-login")}
              className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Return to Sign In</span>
            </button>

            <div className="space-y-1">
              <h2 className="text-xl font-bold tracking-tight text-slate-950 dark:text-white">Forgotten Credentials</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Provide your registered participant email address and we'll dispatch a link to reset your security keys.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="alex.mercer@candidate.edu"
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-9 pr-3.5 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-blue-700"
            >
              {loading ? "Transmitting Reset Link..." : "Request Access Recovery"}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
