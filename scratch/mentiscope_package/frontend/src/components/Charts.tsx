import React from "react";
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from "recharts";

// Modern colors for our design system
const COLORS = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#EC4899", "#3B82F6", "#10B981"];

/**
 * 1. Radar Chart: Visualises cognitive profiles across modules.
 */
interface CognitiveRadarProps {
  data: { subject: string; score: number; average?: number }[];
}

export function CognitiveRadar({ data }: CognitiveRadarProps) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#E2E8F0" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: "#475569", fontSize: 11, fontWeight: 500 }} 
          />
          <PolarRadiusAxis 
            angle={30} 
            domain={[0, 100]} 
            tick={{ fill: "#94A3B8", fontSize: 9 }} 
          />
          <Radar
            name="Your Score"
            dataKey="score"
            stroke="#2563EB"
            fill="#3B82F6"
            fillOpacity={0.25}
          />
          {data[0]?.average !== undefined && (
            <Radar
              name="Global Average"
              dataKey="average"
              stroke="#94A3B8"
              fill="#CBD5E1"
              fillOpacity={0.15}
            />
          )}
          <Tooltip 
            contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px", fontFamily: "sans-serif" }} 
          />
          <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * 2. Completion Rate Chart: Displays started vs completed assessments.
 */
interface CompletionAreaChartProps {
  data: { name: string; completed: number; started: number }[];
}

export function CompletionAreaChart({ data }: CompletionAreaChartProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#14B8A6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#14B8A6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorStarted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748B" }} stroke="#E2E8F0" />
          <YAxis tick={{ fontSize: 10, fill: "#64748B" }} stroke="#E2E8F0" />
          <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }} />
          <Legend wrapperStyle={{ fontSize: "11px", pt: 2 }} />
          <Area
            type="monotone"
            name="Session Completions"
            dataKey="completed"
            stroke="#14B8A6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorCompleted)"
          />
          <Area
            type="monotone"
            name="Session Starts"
            dataKey="started"
            stroke="#2563EB"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorStarted)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * 3. Module Difficulty comparison chart.
 */
interface ModuleDifficultyChartProps {
  data: { subject: string; score: number; difficulty: number; avgTimeSec: number }[];
}

export function ModuleDifficultyChart({ data }: ModuleDifficultyChartProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
          <XAxis dataKey="subject" tick={{ fontSize: 9, fill: "#64748B" }} stroke="#E2E8F0" />
          <YAxis tick={{ fontSize: 10, fill: "#64748B" }} stroke="#E2E8F0" />
          <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }} />
          <Legend wrapperStyle={{ fontSize: "11px" }} />
          <Bar name="Average Score %" dataKey="score" fill="#2563EB" radius={[4, 4, 0, 0]} />
          <Bar name="Relative Difficulty Index" dataKey="difficulty" fill="#F59E0B" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * 4. Demographic Pie Chart.
 */
interface DemographicPieChartProps {
  data: { name: string; value: number }[];
}

export function DemographicPieChart({ data }: DemographicPieChartProps) {
  return (
    <div className="h-64 w-full flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }} />
          <Legend wrapperStyle={{ fontSize: "11px" }} layout="vertical" align="right" verticalAlign="middle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * 5. Simple Line Chart for historical trend line analysis.
 */
interface PerformanceLineTrendProps {
  data: { month: string; average: number; activeStudents: number }[];
}

export function PerformanceLineTrend({ data }: PerformanceLineTrendProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
          <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#64748B" }} stroke="#E2E8F0" />
          <YAxis tick={{ fontSize: 10, fill: "#64748B" }} stroke="#E2E8F0" />
          <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }} />
          <Legend wrapperStyle={{ fontSize: "11px" }} />
          <Line
            type="monotone"
            name="Mean Cohort Score"
            dataKey="average"
            stroke="#8B5CF6"
            strokeWidth={3}
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
