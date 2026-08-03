import React from "react";
import { Mail, Phone, MapPin, Award, ArrowUpRight } from "lucide-react";

interface FooterProps {
  onNavigate?: (page: string) => void;
}

export default function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="relative w-full border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#030712] py-10 md:py-12 text-slate-600 dark:text-slate-400 transition-colors duration-300">
      
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Main 3-Column Compact Grid */}
        <div className="grid grid-cols-1 gap-10 md:grid-cols-12 pb-10 border-b border-slate-200/60 dark:border-slate-800/60">
          
          {/* Brand Column */}
          <div className="md:col-span-5 space-y-3.5">
            <div className="flex items-center gap-3">
              <img 
                src="/logo_mentiscope.png" 
                alt="Mentiscope Logo" 
                className="h-10 w-10 object-cover rounded-xl border border-slate-200/50 dark:border-slate-800 shadow-sm" 
              />
              <span className="font-sans font-extrabold tracking-tight text-xl text-slate-900 dark:text-white">
                Mentiscope
              </span>
            </div>
            <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400 max-w-sm">
              An innovative, scientifically validated cognitive assessment platform incubated at NIRMAAN, IIT Madras, dedicated to helping candidates unlock their potential.
            </p>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-0.5 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              <Award className="h-3.5 w-3.5 shrink-0" />
              <span>Incubated at NIRMAAN, IIT Madras</span>
            </div>
          </div>

          {/* Navigation Links Column */}
          <div className="md:col-span-3">
            <h3 className="font-bold text-slate-900 dark:text-white text-[11px] uppercase tracking-widest mb-4">
              Explore
            </h3>
            <ul className="space-y-2.5 text-xs font-medium">
              {[
                { label: "Home", href: "#hero" },
                { label: "About Mentiscope", href: "#about" },
                { label: "Target Cohorts", href: "#audience" },
                { label: "Assessment Timeline", href: "#workflow" },
              ].map((link) => (
                <li key={link.label}>
                  <a 
                    href={link.href} 
                    className="group inline-flex items-center gap-1 text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors"
                  >
                    <span>{link.label}</span>
                    <ArrowUpRight className="h-3 w-3 opacity-0 -translate-x-1 translate-y-1 transition-all duration-200 group-hover:opacity-100 group-hover:translate-x-0 group-hover:translate-y-0" />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Details Column */}
          <div className="md:col-span-4">
            <h3 className="font-bold text-slate-900 dark:text-white text-[11px] uppercase tracking-widest mb-4">
              Contact & Support
            </h3>
            <ul className="space-y-3 text-xs font-medium">
              <li className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400">
                  <Mail className="h-3.5 w-3.5" />
                </div>
                <a href="mailto:assesmentcognitive@gmail.com" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors font-sans">
                  assesmentcognitive@gmail.com
                </a>
              </li>
              <li className="flex items-start gap-2.5">
                <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 mt-0.5">
                  <Phone className="h-3.5 w-3.5" />
                </div>
                <div className="text-slate-500 dark:text-slate-400 font-sans space-y-0.5">
                  <p>+91 90371 88431</p>
                  <p>+91 99477 83548</p>
                </div>
              </li>
              <li className="flex items-start gap-2.5">
                <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 mt-0.5">
                  <MapPin className="h-3.5 w-3.5" />
                </div>
                <span className="text-slate-500 dark:text-slate-400">
                  NIRMAAN, IIT Madras, Chennai, India
                </span>
              </li>
            </ul>
          </div>

        </div>

        {/* Compact Bottom Metadata Bar */}
        <div className="pt-6 flex flex-col items-center justify-between gap-3 sm:flex-row text-[11px] text-slate-400 dark:text-slate-500 font-medium font-sans">
          <p>© 2026 Mentiscope. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span>Incubator Partner: NIRMAAN, IIT Madras</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
