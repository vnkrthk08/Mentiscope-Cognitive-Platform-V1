import { useEffect, useState, useRef } from 'react';

/**
 * TimerBar — Animated countdown bar with color transitions
 */
export default function TimerBar({ duration, onTimeout, paused = false }) {
  const [remaining, setRemaining] = useState(duration);
  const intervalRef = useRef(null);
  const startRef = useRef(Date.now());

  useEffect(() => {
    setRemaining(duration);
    startRef.current = Date.now();

    if (paused) return;

    intervalRef.current = setInterval(() => {
      const elapsed = (Date.now() - startRef.current) / 1000;
      const newRemaining = Math.max(0, duration - elapsed);
      setRemaining(newRemaining);

      if (newRemaining <= 0) {
        clearInterval(intervalRef.current);
        onTimeout?.();
      }
    }, 100);

    return () => clearInterval(intervalRef.current);
  }, [duration, paused]);

  const percentage = (remaining / duration) * 100;
  const colorClass = percentage > 50 ? 'safe' : percentage > 25 ? 'warning' : 'danger';

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: 4,
        fontSize: 13,
        fontWeight: 600,
      }}>
        <span>⏱️ Time Remaining</span>
        <span style={{
          color: colorClass === 'danger' ? '#DC3545' : colorClass === 'warning' ? '#FFC107' : '#28A745',
          animation: colorClass === 'danger' ? 'countdownPulse 0.8s infinite' : 'none',
        }}>
          {Math.ceil(remaining)}s
        </span>
      </div>
      <div className="timer-bar-container">
        <div
          className={`timer-bar-fill ${colorClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
