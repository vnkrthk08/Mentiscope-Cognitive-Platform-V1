import React from "react";
import { Mail, Phone, MapPin, Award } from "lucide-react";

interface FooterProps {
  onNavigate: (page: string) => void;
}

export default function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="w-full border-t border-slate-200 dark:border-slate-900 bg-slate-50 dark:bg-slate-950 py-16 text-slate-600 dark:text-slate-400 transition-colors duration-300">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-12">
          
          {/* Brand Column */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-2.5">
              <img 
                src="/logo_mentiscope.png" 
                alt="Mentiscope Logo" 
                className="h-14 w-14 object-cover rounded-2xl border border-slate-200/30 dark:border-slate-800/50 shadow-sm" 
              />
              <span className="font-sans font-extrabold tracking-tight text-xl text-slate-900 dark:text-white">
                Mentiscope
              </span>
            </div>
            <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400 max-w-sm">
              An innovative, scientifically validated cognitive assessment platform incubated at NIRMAAN, IIT Madras, dedicated to helping candidates unlock their potential.
            </p>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/30 px-3 py-0.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/30">
              <Award className="h-3.5 w-3.5" />
              <span>Incubated at NIRMAAN, IIT Madras</span>
            </div>
          </div>

          {/* Navigation Links Column */}
          <div className="md:col-span-3">
            <h3 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-widest mb-5">
              Explore
            </h3>
            <ul className="space-y-3 text-sm font-medium">
              <li>
                <a href="#hero" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors">
                  Home
                </a>
              </li>
              <li>
                <a href="#about" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors">
                  About Mentiscope
                </a>
              </li>
              <li>
                <a href="#audience" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors">
                  Target Cohorts
                </a>
              </li>
              <li>
                <a href="#workflow" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors">
                  Assessment Timeline
                </a>
              </li>
            </ul>
          </div>

          {/* Contact Details Column */}
          <div className="md:col-span-4">
            <h3 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-widest mb-5">
              Contact & Support
            </h3>
            <ul className="space-y-4 text-sm font-medium">
              <li className="flex items-center gap-2.5">
                <Mail className="h-4.5 w-4.5 text-blue-600 dark:text-blue-400 shrink-0" />
                <a href="mailto:assesmentcognitive@gmail.com" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors font-sans">
                  assesmentcognitive@gmail.com
                </a>
              </li>
              <li className="flex items-start gap-2.5">
                <Phone className="h-4.5 w-4.5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <div className="text-slate-500 dark:text-slate-400 font-sans space-y-0.5">
                  <p>90371 88431</p>
                  <p>99477 83548</p>
                </div>
              </li>
              <li className="flex items-start gap-2.5">
                <MapPin className="h-4.5 w-4.5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <span className="text-slate-500 dark:text-slate-400">
                  NIRMAAN, IIT Madras, Chennai, India
                </span>
              </li>
            </ul>
          </div>

        </div>

        <div className="mt-16 border-t border-slate-200/60 dark:border-slate-800/80 pt-8 flex flex-col items-center justify-between gap-4 sm:flex-row text-xs text-slate-400 dark:text-slate-500 font-medium font-sans">
          <p>© 2026 Mentiscope. All rights reserved.</p>
          <div className="flex gap-4">
            <span className="text-slate-400 dark:text-slate-500">Incubator Partner: NIRMAAN, IIT Madras</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
