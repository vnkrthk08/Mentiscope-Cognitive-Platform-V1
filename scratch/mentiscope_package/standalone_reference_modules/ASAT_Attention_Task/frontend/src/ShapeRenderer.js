/* =====================================================
   ASAT – SVG Shape Renderer Component
   Shapes: Circle, Triangle, Square, Star, Diamond
   Colors: Red, Blue, Green, Yellow, Purple, Orange
   ===================================================== */

export const SHAPES = ['circle', 'triangle', 'square', 'star', 'diamond'];

export const COLORS = {
  red:    '#E53935',
  blue:   '#1E88E5',
  green:  '#43A047',
  yellow: '#FFB300',
  purple: '#8E24AA',
  orange: '#FB8C00',
};

const COLOR_KEYS = Object.keys(COLORS);

/** Get a random shape name */
export function randomShape(exclude = []) {
  const pool = SHAPES.filter(s => !exclude.includes(s));
  return pool[Math.floor(Math.random() * pool.length)];
}

/** Get a random color key */
export function randomColor(exclude = []) {
  const pool = COLOR_KEYS.filter(c => !exclude.includes(c));
  return pool[Math.floor(Math.random() * pool.length)];
}

/** Generate a random non-target stimulus */
export function randomNonTarget() {
  let shape, color;
  do {
    shape = randomShape();
    color = randomColor();
  } while (shape === 'triangle' && color === 'blue');
  return { shape, color };
}

/**
 * Render an SVG shape element.
 * @param {string} shape  - 'circle' | 'triangle' | 'square' | 'star' | 'diamond'
 * @param {string} color  - key in COLORS or hex string
 * @param {number} size   - px (default 100)
 * @returns {SVGElement}
 */
export function renderShape(shape, color, size = 100) {
  const fill   = COLORS[color] || color;
  const stroke = 'rgba(255,255,255,0.2)';
  const sw     = 2;
  const ns     = 'http://www.w3.org/2000/svg';
  const c      = size / 2;
  const r      = c - sw;

  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.style.filter = `drop-shadow(0 0 8px ${fill}66)`;

  let el;

  switch (shape) {
    case 'circle': {
      el = document.createElementNS(ns, 'circle');
      el.setAttribute('cx', c);
      el.setAttribute('cy', c);
      el.setAttribute('r', r);
      break;
    }
    case 'triangle': {
      const pad = 8;
      const pts = [
        `${c},${pad}`,
        `${size - pad},${size - pad}`,
        `${pad},${size - pad}`,
      ].join(' ');
      el = document.createElementNS(ns, 'polygon');
      el.setAttribute('points', pts);
      break;
    }
    case 'square': {
      const pad = 8;
      el = document.createElementNS(ns, 'rect');
      el.setAttribute('x', pad);
      el.setAttribute('y', pad);
      el.setAttribute('width', size - pad * 2);
      el.setAttribute('height', size - pad * 2);
      el.setAttribute('rx', 6);
      break;
    }
    case 'star': {
      el = document.createElementNS(ns, 'polygon');
      const pts = starPoints(c, c, r, r * 0.4, 5);
      el.setAttribute('points', pts);
      break;
    }
    case 'diamond': {
      const pts = [
        `${c},${sw}`,
        `${size - sw},${c}`,
        `${c},${size - sw}`,
        `${sw},${c}`,
      ].join(' ');
      el = document.createElementNS(ns, 'polygon');
      el.setAttribute('points', pts);
      break;
    }
    default: {
      el = document.createElementNS(ns, 'circle');
      el.setAttribute('cx', c);
      el.setAttribute('cy', c);
      el.setAttribute('r', r);
    }
  }

  el.setAttribute('fill', fill);
  el.setAttribute('stroke', stroke);
  el.setAttribute('stroke-width', sw);
  svg.appendChild(el);

  return svg;
}

/** Compute star polygon points */
function starPoints(cx, cy, outerR, innerR, numPoints) {
  const pts = [];
  for (let i = 0; i < numPoints * 2; i++) {
    const angle = (Math.PI / numPoints) * i - Math.PI / 2;
    const r = i % 2 === 0 ? outerR : innerR;
    pts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
  }
  return pts.join(' ');
}

/**
 * Create a row of shapes for selective attention.
 * @param {number} count - number of shapes
 * @param {boolean} includeTarget - whether to include the target (blue triangle)
 * @param {number} targetIndex - where to place target
 * @param {number} size - shape size
 * @returns {{ shapes: Array<{shape,color}>, targetIndex: number }}
 */
export function buildSelectiveRow(count, includeTarget = false, targetIdx = null, size = 80) {
  const shapes = [];
  const forcedTarget = includeTarget
    ? (targetIdx !== null ? targetIdx : Math.floor(Math.random() * count))
    : -1;

  for (let i = 0; i < count; i++) {
    if (i === forcedTarget) {
      shapes.push({ shape: 'triangle', color: 'blue' });
    } else {
      let s;
      // Avoid accidentally creating blue triangles as distractors
      do { s = randomNonTarget(); } while (s.shape === 'triangle' && s.color === 'blue');
      shapes.push(s);
    }
  }

  return { shapes, targetIndex: forcedTarget };
}

/** Get shape label for display */
export function shapeLabel(shape) {
  return shape.charAt(0).toUpperCase() + shape.slice(1);
}

/** Get color label for display */
export function colorLabel(color) {
  return color.charAt(0).toUpperCase() + color.slice(1);
}
