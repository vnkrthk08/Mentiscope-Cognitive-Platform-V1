import React, { useState } from "react";
import { User } from "../types";
import { AuthService } from "../services/auth/AuthService";
import { 
  User as UserIcon, 
  Calendar, 
  GraduationCap, 
  BookOpen, 
  MapPin, 
  Shield, 
  Award, 
  Save, 
  X,
  ChevronLeft
} from "lucide-react";

interface EditProfilePageProps {
  user: User;
  onSave: (updatedUser: User) => void;
  onCancel: () => void;
}

export default function EditProfilePage({ user, onSave, onCancel }: EditProfilePageProps) {
  const [name, setName] = useState(user.name);
  const [age, setAge] = useState<number | undefined>(user.age);
  const [gender, setGender] = useState(user.gender || "");
  const [education, setEducation] = useState(user.education || "");
  const [course, setCourse] = useState(user.course || "");
  const [specialization, setSpecialization] = useState(user.specialization || "");
  const [collegeType, setCollegeType] = useState(user.collegeType || "");
  const [previousExamPercentage, setPreviousExamPercentage] = useState<number | undefined>(user.previousExamPercentage);
  const [state, setState] = useState(user.state || "");
  const [district, setDistrict] = useState(user.district || "");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Form validations
    if (!name.trim()) {
      setError("Registered Name is a required field.");
      return;
    }
    if (age !== undefined && (age < 15 || age > 99)) {
      setError("Please enter a valid age between 15 and 99.");
      return;
    }
    if (previousExamPercentage !== undefined && (previousExamPercentage < 0 || previousExamPercentage > 100)) {
      setError("Academic percentage score must be between 0% and 100%.");
      return;
    }

    const updatedUser: User = {
      ...user,
      name: name.trim(),
      age: age,
      gender: gender || undefined,
      education: education || undefined,
      course: course || undefined,
      specialization: specialization || undefined,
      collegeType: collegeType || undefined,
      previousExamPercentage: previousExamPercentage,
      state: state.trim(),
      district: district.trim()
    };

    const saved = await AuthService.updateProfile(updatedUser);
    onSave(saved);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      {/* Back to Dashboard navigation hook */}
      <button 
        onClick={onCancel}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors group cursor-pointer"
      >
        <ChevronLeft className="h-4 w-4 transition-transform group-hover:-translate-x-0.5" />
        <span>Return to Dashboard</span>
      </button>

      {/* Header Panel */}
      <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 sm:p-8 shadow-sm">
        <h1 className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-2xl flex items-center gap-2">
          <UserIcon className="h-6 w-6 text-blue-600 dark:text-blue-500" />
          <span>Edit Candidate Demographic Profile</span>
        </h1>
        <p className="text-xs text-slate-450 dark:text-slate-400 mt-2 leading-relaxed max-w-2xl">
          Amending your baseline demographic indicators ensures correct psychometric classification and diagnostic reporting. Please review all fields carefully before saving.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/40 text-xs font-bold text-rose-600 dark:text-rose-450">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section: Account & Personal Info */}
          <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 space-y-5">
            <h3 className="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest border-b border-slate-100 dark:border-slate-800/80 pb-2">
              Identity & Personal Parameters
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">Account Email (Immutable)</label>
                <input 
                  type="text" 
                  value={user.email} 
                  disabled 
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 p-3 text-xs font-mono text-slate-500 dark:text-slate-400 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-450 dark:text-slate-400 mb-1.5">Registered Name</label>
                <div className="relative">
                  <UserIcon className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                  <input 
                    type="text" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                    placeholder="Enter full name"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-11 pr-4 py-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Candidate Age</label>
                  <div className="relative">
                    <Calendar className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                    <input 
                      type="number" 
                      value={age === undefined ? "" : age} 
                      onChange={(e) => setAge(e.target.value ? parseInt(e.target.value) : undefined)} 
                      placeholder="e.g. 21"
                      className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-11 pr-4 py-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Gender Category</label>
                  <select 
                    value={gender} 
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Non-Binary">Non-Binary</option>
                    <option value="Other">Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Section: Academic Info */}
          <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 space-y-5">
            <h3 className="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest border-b border-slate-100 dark:border-slate-800/80 pb-2">
              Academic Baseline Credentials
            </h3>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Education Level</label>
                  <select 
                    value={education} 
                    onChange={(e) => setEducation(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select Education</option>
                    <option value="High School">High School</option>
                    <option value="Undergraduate">Undergraduate</option>
                    <option value="Postgraduate">Postgraduate</option>
                    <option value="Doctorate">Doctorate / Ph.D.</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">College Type</label>
                  <select 
                    value={collegeType} 
                    onChange={(e) => setCollegeType(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select College Type</option>
                    <option value="Public">Public / State University</option>
                    <option value="Private">Private Institution</option>
                    <option value="Semi-Government">Semi-Government</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Registered Course / Program</label>
                <div className="relative">
                  <BookOpen className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                  <input 
                    type="text" 
                    value={course} 
                    onChange={(e) => setCourse(e.target.value)} 
                    placeholder="e.g. Bachelor of Science"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-11 pr-4 py-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Specialization</label>
                  <input 
                    type="text" 
                    value={specialization} 
                    onChange={(e) => setSpecialization(e.target.value)} 
                    placeholder="e.g. Cognitive Science"
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-400 mb-1.5">Last Exam Score % (Read-Only)</label>
                  <div className="relative">
                    <Award className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                    <input 
                      type="number" 
                      value={previousExamPercentage === undefined ? "" : previousExamPercentage} 
                      disabled 
                      className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 pl-11 pr-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 cursor-not-allowed"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section: Geographic Profile */}
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 space-y-5">
          <h3 className="text-xs font-mono font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest border-b border-slate-100 dark:border-slate-800/80 pb-2">
            Geographic Demographics
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-500 mb-1.5">State / Territory</label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                <input 
                  type="text" 
                  value={state} 
                  onChange={(e) => setState(e.target.value)} 
                  placeholder="e.g. Tamil Nadu"
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-11 pr-4 py-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-455 dark:text-slate-500 mb-1.5">District / Region</label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                <input 
                  type="text" 
                  value={district} 
                  onChange={(e) => setDistrict(e.target.value)} 
                  placeholder="e.g. Chennai"
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 pl-11 pr-4 py-3 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Action Panel: Save & Cancel Buttons */}
        <div className="flex items-center justify-end gap-3.5 pt-4 border-t border-slate-200/50 dark:border-slate-800/50">
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-850 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-650 dark:text-slate-350 px-5 py-3 text-xs font-bold transition-all cursor-pointer"
          >
            <X className="h-4 w-4" />
            <span>Discard Changes</span>
          </button>
          
          <button
            type="submit"
            className="flex items-center justify-center gap-1.5 rounded-xl bg-blue-650 hover:bg-blue-700 text-white px-5 py-3 text-xs font-bold transition-all shadow-md shadow-blue-500/10 active:scale-[0.98] cursor-pointer"
          >
            <Save className="h-4 w-4" />
            <span>Save & Continue</span>
          </button>
        </div>
      </form>
    </div>
  );
}
