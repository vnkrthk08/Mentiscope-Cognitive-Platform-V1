import { useMemo } from 'react';

const SIZE = 140;
const STROKE = 10;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getColor(score) {
  if (score >= 80) return '#28A745';
  if (score >= 60) return '#17A2B8';
  if (score >= 40) return '#FFC107';
  return '#DC3545';
}

export default function ScoreGauge({ score = 0, size = SIZE, label = 'Score' }) {
  const radius = (size - STROKE) / 2;
  const circumference = 2 * Math.PI * radius;

  const dashOffset = useMemo(() => {
    const progress = Math.max(0, Math.min(100, score)) / 100;
    return circumference * (1 - progress);
  }, [score, circumference]);

  const color = getColor(score);

  return (
    <div className="score-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e8e8e8"
          strokeWidth={STROKE}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1s ease, stroke 0.5s ease' }}
        />
      </svg>
      <span className="score-gauge-value" style={{ color, fontSize: size * 0.2 }}>
        {Math.round(score)}
      </span>
      <span className="score-gauge-label" style={{ fontSize: size * 0.08 }}>
        {label}
      </span>
    </div>
  );
}
