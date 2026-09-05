import React from "react";
import { User, UserRole } from "../types";
import { AuthService } from "../services/auth/AuthService";
import { 
  Brain, 
  LogOut, 
  User as UserIcon, 
  Shield, 
  Briefcase, 
  ChevronRight, 
  Sun, 
  Moon, 
  Volume2, 
  VolumeX, 
  FileText,
  GraduationCap,
  BookOpen,
  MapPin,
  Calendar,
  Award
} from "lucide-react";

interface NavbarProps {
  user: User | null;
  onLogout: () => void;
  onNavigate: (page: string, subPage?: string) => void;
  currentPage: string;
  theme: "light" | "dark";
  setTheme: (theme: "light" | "dark") => void;
  soundEnabled: boolean;
  setSoundEnabled: (enabled: boolean) => void;
}

export default function Navbar({ 
  user, 
  onLogout, 
  onNavigate, 
  currentPage,
  theme,
  setTheme,
  soundEnabled,
  setSoundEnabled
}: NavbarProps) {
  const [profileOpen, setProfileOpen] = React.useState(false);
  const profileDropdownRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 dark:border-slate-800/85 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl transition-colors duration-300">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo and Brand */}
        <div 
          onClick={() => {
            onNavigate("landing");
            const scrollContainer = document.getElementById("landing-scroll-container");
            if (scrollContainer) {
              scrollContainer.scrollTo({ top: 0, behavior: "smooth" });
            }
            window.scrollTo({ top: 0, behavior: "smooth" });
          }} 
          className="flex cursor-pointer items-center gap-3 transition-all spring-press hover:opacity-95"
        >
          <img 
            src="/logo_mentiscope.png" 
            alt="Mentiscope Logo" 
            className="h-10 w-10 object-cover rounded-xl transition-all duration-300 hover:scale-105 border border-slate-200/30 dark:border-slate-800/50 shadow-sm" 
          />
          <div>
            <span className="font-sans font-extrabold tracking-tight text-slate-950 dark:text-white text-xl sm:text-2xl leading-none">
              Mentiscope
            </span>
            <span className="ml-2 text-[9px] font-sans font-bold tracking-wide text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-950/50 px-2 py-0.5 rounded-full hidden sm:inline-block border border-blue-100 dark:border-blue-900/50 align-middle">
              NIRMAAN, IIT Madras
            </span>
          </div>
        </div>

        {/* Navigation / User / Settings Section */}
        <div className="flex items-center gap-4">
          
          {/* Theme & Sound Control Icons */}
          <div className="flex items-center gap-2 mr-2 border-r border-slate-200 dark:border-slate-800 pr-4">
            {/* Audio Toggle */}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              title={soundEnabled ? "Mute sound effects" : "Unmute sound effects"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 spring-press transition-colors"
            >
              {soundEnabled ? <Volume2 className="h-4.5 w-4.5" /> : <VolumeX className="h-4.5 w-4.5 text-red-500" />}
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 spring-press transition-colors"
            >
              {theme === "dark" ? <Sun className="h-4.5 w-4.5 text-amber-500 transition-transform active:rotate-45" /> : <Moon className="h-4.5 w-4.5 transition-transform active:-rotate-45" />}
            </button>
          </div>

          {user ? (
            <div className="flex items-center gap-3">
              {/* Role Indicator Badge */}
              <div className="hidden items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium sm:flex bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-slate-800">
                {user.role === UserRole.SUPER_ADMIN && (
                  <>
                    <Shield className="h-3 w-3 text-red-500" />
                    <span className="text-red-700 dark:text-red-400">Admin</span>
                  </>
                )}
                {user.role === UserRole.INTERN && (
                  <>
                    <Briefcase className="h-3 w-3 text-amber-500" />
                    <span className="text-amber-700 dark:text-amber-400">Psychology Intern</span>
                  </>
                )}
                {user.role === UserRole.STUDENT && (
                  <>
                    <UserIcon className="h-3 w-3 text-blue-500" />
                    <span className="text-blue-700 dark:text-blue-400">Candidate</span>
                  </>
                )}
              </div>

              {/* Navigation Links for Active User Dashboard */}
              <button
                onClick={() => onNavigate("landing")}
                className={`text-sm font-semibold transition-colors hover:text-blue-600 dark:hover:text-blue-400 ${
                  currentPage === "landing"
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-600 dark:text-slate-400"
                }`}
              >
                Home
              </button>

              <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />

              <button
                onClick={() => {
                  if (user.role === UserRole.SUPER_ADMIN) onNavigate("admin");
                  else if (user.role === UserRole.INTERN) onNavigate("intern");
                  else onNavigate("dashboard");
                }}
                className={`text-sm font-semibold transition-colors hover:text-blue-600 dark:hover:text-blue-400 ${
                  ["dashboard", "admin", "intern"].includes(currentPage)
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-600 dark:text-slate-400"
                }`}
              >
                Dashboard
              </button>

              <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />

              {/* User Profile Trigger & Demographic Dropdown */}
              <div className="relative" ref={profileDropdownRef}>
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  title="Click to view candidate profile details"
                  className="flex items-center gap-2 hover:bg-slate-150/40 dark:hover:bg-slate-900/60 p-1.5 rounded-xl transition-all cursor-pointer text-left"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white shadow-sm shrink-0">
                    {user.name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2)}
                  </div>
                  <div className="hidden flex-col leading-none md:flex">
                    <span className="text-xs font-bold text-slate-805 dark:text-slate-205">{user.name}</span>
                    <span className="text-[9px] text-slate-500 dark:text-slate-400 mt-0.5">{user.email}</span>
                  </div>
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-3.5 w-[340px] rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.15)] dark:shadow-[0_20px_50px_rgba(0,0,0,0.45)] z-55 transition-all duration-300">
                    
                    {/* Header: User Profile Info */}
                    <div className="flex items-center gap-3.5 border-b border-slate-100 dark:border-slate-800 pb-4 mb-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 font-extrabold text-white text-base shadow-lg shadow-blue-500/20">
                        {user.name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2)}
                      </div>
                      <div className="flex flex-col min-w-0">
                        <h4 className="text-sm font-extrabold text-slate-900 dark:text-white truncate leading-tight">{user.name}</h4>
                        <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono mt-0.5 truncate">{user.email}</p>
                        <div className="flex items-center gap-1.5 mt-1.5">
                          <span className="text-[9px] font-bold uppercase tracking-wider bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-900/30">
                            {user.role === UserRole.SUPER_ADMIN ? "Super Admin" : "Candidate Student"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Candidate Demographics Grid */}
                    {user.role === UserRole.STUDENT && (
                      <div className="space-y-4">
                        {/* Section 1: Personal Attributes */}
                        <div className="space-y-2">
                          <span className="text-[9px] font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block">Personal Info</span>
                          <div className="grid grid-cols-2 gap-2">
                            {user.age && (
                              <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                <Calendar className="h-4 w-4 text-blue-500 shrink-0" />
                                <div className="min-w-0">
                                  <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Age</span>
                                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5">{user.age} yrs</span>
                                </div>
                              </div>
                            )}
                            {user.gender && (
                              <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                <UserIcon className="h-4 w-4 text-emerald-500 shrink-0" />
                                <div className="min-w-0">
                                  <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Gender</span>
                                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5">{user.gender}</span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Section 2: Academic Profile */}
                        <div className="space-y-2">
                          <span className="text-[9px] font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block">Academic Profile</span>
                          <div className="space-y-2">
                            {user.education && (
                              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                <GraduationCap className="h-4.5 w-4.5 text-indigo-500 shrink-0" />
                                <div className="min-w-0">
                                  <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Education Level</span>
                                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5 truncate">{user.education}</span>
                                </div>
                              </div>
                            )}
                            {user.course && (
                              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                <BookOpen className="h-4.5 w-4.5 text-purple-500 shrink-0" />
                                <div className="min-w-0">
                                  <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Course & Discipline</span>
                                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5 truncate">{user.course}</span>
                                </div>
                              </div>
                            )}
                            {user.specialization && (
                              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                <Brain className="h-4.5 w-4.5 text-pink-500 shrink-0" />
                                <div className="min-w-0">
                                  <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Specialization</span>
                                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5 truncate">{user.specialization}</span>
                                </div>
                              </div>
                            )}
                            <div className="grid grid-cols-2 gap-2">
                              {user.collegeType && (
                                <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                  <Shield className="h-4 w-4 text-teal-500 shrink-0" />
                                  <div className="min-w-0">
                                    <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">College</span>
                                    <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5">{user.collegeType}</span>
                                  </div>
                                </div>
                              )}
                              {user.previousExamPercentage !== undefined && (
                                <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                                  <Award className="h-4 w-4 text-amber-500 shrink-0" />
                                  <div className="min-w-0">
                                    <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Last Exam</span>
                                    <span className="text-[11px] font-bold text-slate-850 dark:text-slate-200 leading-tight block mt-0.5">{user.previousExamPercentage}%</span>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Section 3: Geographic Data */}
                        <div className="space-y-2">
                          <span className="text-[9px] font-mono font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest block">Geographic Origin</span>
                          <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80">
                            <MapPin className="h-4.5 w-4.5 text-rose-500 shrink-0" />
                            <div className="min-w-0">
                              <span className="text-[8px] text-slate-400 dark:text-slate-550 block leading-none font-bold uppercase">Region</span>
                              <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5 truncate">
                                {user.district ? `${user.district}, ` : ""}{user.state}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Footer Actions */}
                    <div className="border-t border-slate-150 dark:border-slate-800 pt-4 mt-4 flex flex-col gap-2">
                      {user.role === UserRole.STUDENT ? (
                        <>
                          <button
                            onClick={() => {
                              setProfileOpen(false);
                              onNavigate("dashboard");
                            }}
                            className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-slate-105 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 py-2 text-xs font-bold transition-all active:scale-[0.98] cursor-pointer border border-slate-200/50 dark:border-slate-700"
                          >
                            <span>View Portal Dashboard</span>
                          </button>
                          
                          <button
                            onClick={() => {
                              setProfileOpen(false);
                              onNavigate("profile");
                            }}
                            className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white py-2.5 text-xs font-bold transition-all shadow-md shadow-blue-500/10 active:scale-[0.98] cursor-pointer"
                          >
                            <span>Amend Registration Profile</span>
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => {
                            setProfileOpen(false);
                            onNavigate("admin");
                          }}
                          className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white py-2.5 text-xs font-bold transition-all shadow-md shadow-blue-500/10 active:scale-[0.98] cursor-pointer"
                        >
                          <span>View Admin Dashboard</span>
                        </button>
                      )}

                      <button
                        onClick={() => {
                          setProfileOpen(false);
                          AuthService.logout();
                          onLogout();
                        }}
                        className="w-full flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-rose-500/10 hover:text-rose-600 dark:hover:text-rose-450 text-slate-600 dark:text-slate-400 py-2 text-xs font-bold transition-all active:scale-[0.98] cursor-pointer"
                      >
                        <LogOut className="h-3.5 w-3.5" />
                        <span>Sign Out Session</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              {/* <button
                  type="button"
                  onClick={() => handleSetDemoCredentials(UserRole.INTERN)}
                  className="px-2 py-1 rounded-lg bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:teal-400 text-[10px] font-bold hover:bg-teal-100 transition-colors"
                >
                  Intern
                </button> */}
              <button
                onClick={() => onNavigate("landing")}
                className="hidden text-sm font-semibold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:white transition-colors md:inline-block px-2.5 py-1.5"
              >
                Home
              </button>

              {/* Modern Glass & Glow Outline Candidate Portal Button */}
              <button
                onClick={() => onNavigate("auth", "student-login")}
                className="group relative flex items-center gap-2 rounded-xl border border-cyan-500/30 dark:border-cyan-400/30 bg-slate-900/60 dark:bg-slate-900/70 backdrop-blur-md px-4 py-2 text-xs sm:text-sm font-bold text-slate-900 dark:text-white transition-all duration-300 hover:border-cyan-400 dark:hover:border-cyan-300 hover:bg-cyan-500/10 dark:hover:bg-cyan-400/10 hover:shadow-[0_0_15px_rgba(6,182,212,0.15)] active:scale-[0.98]"
              >
                <UserIcon className="h-4 w-4 text-cyan-500 dark:text-cyan-400 transition-transform duration-300 group-hover:scale-110" />
                <span>Candidate Portal</span>
              </button>

              {/* Modern Glass & Glow Outline Admin Access Button */}
              <button
                onClick={() => onNavigate("auth", "admin-login")}
                className="group flex items-center gap-2 rounded-xl border border-blue-400/40 bg-blue-600/90 dark:bg-blue-600/90 backdrop-blur-md px-4 py-2 text-xs sm:text-sm font-bold text-white transition-all duration-300 hover:bg-blue-500 dark:hover:bg-blue-500 hover:border-blue-300 hover:shadow-[0_0_18px_rgba(59,130,246,0.25)] hover:scale-[1.02] active:scale-[0.98]"
              >
                <Shield className="h-4 w-4 text-white/90 transition-transform duration-300 group-hover:rotate-12" />
                <span>Admin Access</span>
                <ChevronRight className="h-4 w-4 text-white/80 transition-transform duration-300 group-hover:translate-x-0.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
