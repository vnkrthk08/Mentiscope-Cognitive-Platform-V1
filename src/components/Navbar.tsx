import React from "react";
import { User, UserRole } from "../types";
import { AuthService } from "../services/auth/AuthService";
import { Brain, LogOut, User as UserIcon, Shield, Briefcase, ChevronRight, Sun, Moon, Volume2, VolumeX } from "lucide-react";

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
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-slate-800/85 bg-white/85 dark:bg-slate-950/85 backdrop-blur-md transition-colors duration-300">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo and Brand */}
        <div 
          onClick={() => onNavigate("landing")} 
          className="flex cursor-pointer items-center gap-3 transition-all hover:opacity-95"
        >
          <img 
            src="/logo_mentiscope.png" 
            alt="Mentiscope Logo" 
            className="h-14 w-14 object-cover rounded-2xl transition-all duration-300 hover:scale-105 border border-slate-200/30 dark:border-slate-800/50 shadow-sm" 
          />
          <div>
            <span className="font-sans font-extrabold tracking-tight text-slate-950 dark:text-white text-2xl sm:text-3xl lg:text-4xl leading-none">
              Mentiscope
            </span>
            <span className="ml-2 text-[10px] font-sans font-bold tracking-wide text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-950/50 px-2 py-1 rounded-md hidden sm:inline-block border border-blue-100 dark:border-blue-900/50 align-middle">
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
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              {soundEnabled ? <Volume2 className="h-4.5 w-4.5" /> : <VolumeX className="h-4.5 w-4.5 text-red-500" />}
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              {theme === "dark" ? <Sun className="h-4.5 w-4.5 text-amber-500" /> : <Moon className="h-4.5 w-4.5" />}
            </button>
          </div>

          {user ? (
            <div className="flex items-center gap-3">
              {/* Role Indicator Badge */}
              <div className="hidden items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium sm:flex bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-slate-800">
                {user.role === UserRole.SUPER_ADMIN && (
                  <>
                    <Shield className="h-3 w-3 text-red-500" />
                    <span className="text-red-700 dark:text-red-400">Super Admin</span>
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

              {/* User Profile Trigger */}
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white shadow-sm">
                  {user.name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2)}
                </div>
                <div className="hidden flex-col leading-none md:flex">
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{user.name}</span>
                  <span className="text-[9px] text-slate-500 dark:text-slate-400">{user.email}</span>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={() => {
                  AuthService.logout();
                  onLogout();
                }}
                title="Sign out of your session"
                className="flex items-center gap-1 rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden text-xs font-semibold lg:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <button
                onClick={() => onNavigate("landing")}
                className="hidden text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 md:inline-block"
              >
                Home
              </button>
              <button
                onClick={() => onNavigate("auth", "student-login")}
                className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-1.5 text-sm font-semibold text-slate-700 dark:text-slate-350 transition-all hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Candidate Portal
              </button>
              <button
                onClick={() => onNavigate("auth", "admin-login")}
                className="flex items-center gap-1.5 rounded-lg bg-slate-900 dark:bg-blue-600 px-4 py-1.5 text-sm font-semibold text-white transition-all hover:bg-slate-850 dark:hover:bg-blue-500 hover:scale-[1.02] active:scale-[0.98] shadow-sm shadow-slate-900/10 dark:shadow-blue-500/15"
              >
                <span>Admin Access</span>
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
