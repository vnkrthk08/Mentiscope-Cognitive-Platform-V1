import React from "react";

export type ShapeType = "circle" | "triangle" | "square" | "star" | "diamond";
export type ColorKey = "red" | "blue" | "green" | "yellow" | "purple" | "orange";

export const SHAPES: ShapeType[] = ["circle", "triangle", "square", "star", "diamond"];

export const COLORS: Record<ColorKey, string> = {
  red: "#E53935",
  blue: "#1E88E5",
  green: "#43A047",
  yellow: "#FFB300",
  purple: "#8E24AA",
  orange: "#FB8C00",
};

export function randomShape(exclude: ShapeType[] = []): ShapeType {
  const pool = SHAPES.filter((s) => !exclude.includes(s));
  return pool[Math.floor(Math.random() * pool.length)];
}

export function randomColor(exclude: ColorKey[] = []): ColorKey {
  const keys = Object.keys(COLORS) as ColorKey[];
  const pool = keys.filter((c) => !exclude.includes(c));
  return pool[Math.floor(Math.random() * pool.length)];
}

export function randomNonTarget(): { shape: ShapeType; color: ColorKey } {
  let shape: ShapeType;
  let color: ColorKey;
  do {
    shape = randomShape();
    color = randomColor();
  } while (shape === "triangle" && color === "blue");
  return { shape, color };
}

interface ShapeRendererProps {
  shape: ShapeType;
  color: ColorKey | string;
  size?: number;
  className?: string;
  onClick?: () => void;
  shadow?: boolean;
}

export const ShapeRenderer: React.FC<ShapeRendererProps> = ({
  shape,
  color,
  size = 100,
  className = "",
  onClick,
  shadow = true,
}) => {
  const fillColor = COLORS[color as ColorKey] || color;
  const strokeColor = "rgba(255, 255, 255, 0.25)";
  const sw = 2;
  const c = size / 2;
  const r = c - sw;

  const starPoints = (cx: number, cy: number, outerR: number, innerR: number, points = 5) => {
    const pts: string[] = [];
    for (let i = 0; i < points * 2; i++) {
      const angle = (Math.PI / points) * i - Math.PI / 2;
      const radius = i % 2 === 0 ? outerR : innerR;
      pts.push(`${cx + radius * Math.cos(angle)},${cy + radius * Math.sin(angle)}`);
    }
    return pts.join(" ");
  };

  const renderPath = () => {
    switch (shape) {
      case "circle":
        return <circle cx={c} cy={c} r={r} fill={fillColor} stroke={strokeColor} strokeWidth={sw} />;
      case "triangle": {
        const pad = 8;
        const pts = `${c},${pad} ${size - pad},${size - pad} ${pad},${size - pad}`;
        return <polygon points={pts} fill={fillColor} stroke={strokeColor} strokeWidth={sw} />;
      }
      case "square": {
        const pad = 8;
        return (
          <rect
            x={pad}
            y={pad}
            width={size - pad * 2}
            height={size - pad * 2}
            rx={6}
            fill={fillColor}
            stroke={strokeColor}
            strokeWidth={sw}
          />
        );
      }
      case "star": {
        const pts = starPoints(c, c, r, r * 0.42, 5);
        return <polygon points={pts} fill={fillColor} stroke={strokeColor} strokeWidth={sw} />;
      }
      case "diamond": {
        const pts = `${c},${sw} ${size - sw},${c} ${c},${size - sw} ${sw},${c}`;
        return <polygon points={pts} fill={fillColor} stroke={strokeColor} strokeWidth={sw} />;
      }
      default:
        return <circle cx={c} cy={c} r={r} fill={fillColor} stroke={strokeColor} strokeWidth={sw} />;
    }
  };

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width={size}
      height={size}
      onClick={onClick}
      className={`select-none transition-transform duration-150 ${onClick ? "cursor-pointer hover:scale-105 active:scale-95" : ""} ${className}`}
      style={{
        filter: shadow ? `drop-shadow(0 0 10px ${fillColor}55)` : "none",
      }}
    >
      {renderPath()}
    </svg>
  );
};
