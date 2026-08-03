export interface CalibrationMetrics {
  rc: number; // Rule Complexity (1-5)
  cs: number; // Cognitive Steps (1-5)
  rp: number; // Representation Complexity (1-5)
  wm: number; // Working Memory Load (1-5)
  dc: number; // Decision Complexity (1-5)
  vp: number; // Visual Processing (1-5)
  cl: number; // Constraint Load (1-5)
  t: number;  // Expected Time (1-5)
}

export interface Question {
  id: string; // e.g. PB-T04-L3-V08
  templateId: string; // e.g. PB-T04
  module: 'PatternBot' | 'CompareBot' | 'VisionBot' | 'SolverBot';
  templateName: string;
  difficultyLevel: number; // 1 to 5
  calculatedDifficulty: number; // e.g. 3.2
  calibration: CalibrationMetrics;
  storyTheme: string;
  narrative: string;
  data: any; // Dynamic data structure representing the question parameters
  questionText: string;
  options: string[];
  correctAnswer: string;
  hint: string;
  errorTypes: { [key: string]: string }; // Map options to error categories
}

// Rotational Story Themes
export const STORY_THEMES = [
  'Energy Cells',
  'AI Memory Core',
  'Space Navigation Matrix',
  'Quantum Signals',
  'Satellite Repair System',
  'Colony Power Grid',
  'Neural Pulses',
  'Bio Signals Lab'
];

export const THEME_ICONS: { [key: string]: string } = {
  'Energy Cells': '🔋',
  'AI Memory Core': '🧠',
  'Space Navigation Matrix': '🚀',
  'Quantum Signals': '⚛️',
  'Satellite Repair System': '🛰️',
  'Colony Power Grid': '⚡',
  'Neural Pulses': '🧬',
  'Bio Signals Lab': '🔬'
};

// Generate a random seed number based on theme or string
function selectTheme(idx: number): string {
  return STORY_THEMES[idx % STORY_THEMES.length];
}

// Calculate Deliverable 2 Weighted Difficulty Score
export function calculateDifficultyScore(m: CalibrationMetrics): number {
  return Number((
    0.25 * m.rc +
    0.20 * m.cs +
    0.15 * m.rp +
    0.10 * m.wm +
    0.10 * m.dc +
    0.05 * m.vp +
    0.10 * m.cl +
    0.05 * m.t
  ).toFixed(2));
}

// Maps 1.0 - 5.0 score to L1-L5
export function mapDifficultyToLevel(score: number): number {
  if (score <= 1.8) return 1;
  if (score <= 2.6) return 2;
  if (score <= 3.4) return 3;
  if (score <= 4.2) return 4;
  return 5;
}

/**
 * Generate a dynamic question for a specific module and difficulty level
 */
export function generateQuestion(
  module: 'PatternBot' | 'CompareBot' | 'VisionBot' | 'SolverBot',
  targetLevel: number,
  sessionQuestionIndex: number = 0
): Question {
  const theme = selectTheme(sessionQuestionIndex + targetLevel * 3);
  const variantNum = Math.floor(1 + Math.random() * 15);
  const variantStr = `V${variantNum < 10 ? '0' : ''}${variantNum}`;
  
  // Base default calibration metrics to be refined per question
  let calibration: CalibrationMetrics = {
    rc: targetLevel,
    cs: Math.max(1, targetLevel - 1),
    rp: Math.max(1, targetLevel - 2),
    wm: Math.max(1, targetLevel - 1),
    dc: Math.max(1, targetLevel - 2),
    vp: Math.max(1, targetLevel - 3),
    cl: module === 'SolverBot' ? Math.max(2, targetLevel) : 1,
    t: targetLevel
  };

  let templateId = '';
  let templateName = '';
  let narrative = '';
  let questionText = '';
  let options: string[] = [];
  let correctAnswer = '';
  let hint = '';
  let data: any = {};
  let errorTypes: { [key: string]: string } = {};

  if (module === 'PatternBot') {
    // Determine which template based on target level
    let tIdx = Math.min(10, Math.max(1, (targetLevel - 1) * 2 + (sessionQuestionIndex % 2) + 1));
    templateId = `PB-T${tIdx < 10 ? '0' : ''}${tIdx}`;
    
    // Story intro
    const themeIcon = THEME_ICONS[theme] || '🤖';
    
    switch (tIdx) {
      case 1:
      case 2: {
        templateName = tIdx === 1 ? 'Arithmetic Progression' : 'Geometric Progression';
        calibration.rc = tIdx === 1 ? 1 : 2;
        calibration.cs = 1;
        calibration.rp = 1;
        calibration.wm = 2;
        calibration.dc = 1;
        calibration.vp = 2;
        calibration.t = 2;
        
        const start = Math.floor(2 + Math.random() * 10);
        const ratioOrDiff = Math.floor(2 + Math.random() * 4);
        const sequence: number[] = [];
        
        if (tIdx === 1) {
          // Arithmetic
          for (let i = 0; i < 4; i++) {
            sequence.push(start + i * ratioOrDiff);
          }
          correctAnswer = String(start + 4 * ratioOrDiff);
          hint = `Look at the difference between consecutive terms. It is constant (+${ratioOrDiff}).`;
          data = { sequence, type: 'arithmetic', difference: ratioOrDiff };
          
          const wrong1 = String(start + 4 * ratioOrDiff + 2);
          const wrong2 = String(start + 4 * ratioOrDiff - ratioOrDiff - 1);
          const wrong3 = String(start * (4 + ratioOrDiff));
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'AP_ERROR',
            [wrong2]: 'RANDOM',
            [wrong3]: 'GP_ERROR'
          };
        } else {
          // Geometric
          for (let i = 0; i < 4; i++) {
            sequence.push(start * Math.pow(ratioOrDiff, i));
          }
          correctAnswer = String(start * Math.pow(ratioOrDiff, 4));
          hint = `Each term is multiplied by a constant ratio (x${ratioOrDiff}).`;
          data = { sequence, type: 'geometric', ratio: ratioOrDiff };
          
          const wrong1 = String(sequence[3] + ratioOrDiff); // Addition error
          const wrong2 = String(sequence[3] * (ratioOrDiff + 1));
          const wrong3 = String(sequence[3] * 2);
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'GP_ERROR', // treated as arithmetic
            [wrong2]: 'RANDOM',
            [wrong3]: 'ALT_ERROR'
          };
        }
        
        narrative = `${themeIcon} The ${theme} monitor displays a sequential data packet stream. One of the packet blocks is corrupted.`;
        questionText = `Determine the next integer sequence node value: [ ${sequence.join(', ')}, ? ]`;
        break;
      }
      case 3:
      case 4: {
        templateName = tIdx === 3 ? 'Increasing Difference' : 'Recursive Pattern';
        calibration.rc = tIdx === 3 ? 3 : 4;
        calibration.cs = 3;
        calibration.rp = 2;
        calibration.wm = 3;
        calibration.dc = 2;
        calibration.vp = 2;
        calibration.t = 3;
        
        if (tIdx === 3) {
          // Increasing difference (second order)
          // diffs: d, d+k, d+2k, d+3k
          const start = Math.floor(2 + Math.random() * 5);
          const baseDiff = Math.floor(2 + Math.random() * 3);
          const acc = Math.floor(1 + Math.random() * 2);
          const sequence: number[] = [start];
          let currentDiff = baseDiff;
          for (let i = 0; i < 4; i++) {
            sequence.push(sequence[sequence.length - 1] + currentDiff);
            currentDiff += acc;
          }
          correctAnswer = String(sequence[sequence.length - 1] + currentDiff);
          hint = `The difference between terms is not constant, it increases by ${acc} each step. Diffs: ${baseDiff}, ${baseDiff+acc}, ${baseDiff+2*acc}...`;
          data = { sequence, type: 'second-order', baseDiff, acc };
          
          const wrong1 = String(sequence[sequence.length - 1] + baseDiff); // constant diff assumption
          const wrong2 = String(sequence[sequence.length - 1] + currentDiff + 3);
          const wrong3 = String(sequence[sequence.length - 1] * 2);
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'ALT_ERROR', // constant difference assumed
            [wrong2]: 'RANDOM',
            [wrong3]: 'REC_ERROR'
          };
        } else {
          // Recursive (e.g. prev * 2 + 1)
          const start = Math.floor(2 + Math.random() * 4);
          const mult = 2;
          const constant = 1;
          const sequence: number[] = [start];
          for (let i = 0; i < 4; i++) {
            sequence.push(sequence[sequence.length - 1] * mult + constant);
          }
          correctAnswer = String(sequence[sequence.length - 1] * mult + constant);
          hint = `Each term is double the previous term plus one (x${mult} + ${constant}).`;
          data = { sequence, type: 'recursive', mult, constant };
          
          const wrong1 = String(sequence[sequence.length - 1] * mult); // missed constant addition
          const wrong2 = String(sequence[sequence.length - 1] + 16);
          const wrong3 = String(sequence[sequence.length - 1] * 3);
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'REC_ERROR', // missed constant addition
            [wrong2]: 'AP_ERROR',
            [wrong3]: 'RANDOM'
          };
        }
        
        narrative = `${themeIcon} The synaptic core of the ${theme} reports a feedback escalation sequence.`;
        questionText = `Unlock the progression sequence below: [ ${data.sequence.join(', ')}, ? ]`;
        break;
      }
      case 5:
      case 8: {
        templateName = tIdx === 5 ? 'Alternating Pattern' : 'Fibonacci Pattern';
        calibration.rc = 4;
        calibration.cs = 4;
        calibration.rp = 2;
        calibration.wm = 4;
        calibration.dc = 2;
        calibration.vp = 2;
        calibration.t = 4;
        
        if (tIdx === 5) {
          // Alternating sequence (two merged sequences)
          // Odd positions: +A. Even positions: *B
          const start1 = Math.floor(2 + Math.random() * 5);
          const start2 = Math.floor(10 + Math.random() * 5);
          const diff = 2;
          const mult = 2;
          const sequence: number[] = [start1, start2, start1 + diff, start2 * mult, start1 + 2 * diff, start2 * mult * mult];
          // next term is odd position: start1 + 3 * diff
          correctAnswer = String(start1 + 3 * diff);
          hint = `This is a dual sequence. Odd positions add ${diff} (${start1} -> ${start1+diff} -> ${start1+2*diff}). Even positions double.`;
          data = { sequence, type: 'alternating', diff, mult };
          
          const wrong1 = String(sequence[sequence.length - 1] * mult); // applied even rule instead of odd
          const wrong2 = String(sequence[sequence.length - 1] + diff);
          const wrong3 = String(sequence[sequence.length - 1] - 5);
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'ALT_ERROR', // single sequence thinking
            [wrong2]: 'AP_ERROR',
            [wrong3]: 'RANDOM'
          };
        } else {
          // Fibonacci
          const start1 = Math.floor(1 + Math.random() * 3);
          const start2 = Math.floor(2 + Math.random() * 3);
          const sequence: number[] = [start1, start2];
          for (let i = 0; i < 4; i++) {
            sequence.push(sequence[sequence.length - 1] + sequence[sequence.length - 2]);
          }
          correctAnswer = String(sequence[sequence.length - 1] + sequence[sequence.length - 2]);
          hint = `Add the last two terms together to get the next term. (e.g. ${sequence[3]} + ${sequence[4]} = ${sequence[5]}).`;
          data = { sequence, type: 'fibonacci' };
          
          const wrong1 = String(sequence[sequence.length - 1] + 5); // treated as AP
          const wrong2 = String(sequence[sequence.length - 1] * 2 - 1);
          const wrong3 = String(sequence[sequence.length - 1] + sequence[sequence.length - 2] - 2);
          options = [correctAnswer, wrong1, wrong2, wrong3];
          errorTypes = {
            [wrong1]: 'AP_ERROR',
            [wrong2]: 'REC_ERROR',
            [wrong3]: 'RANDOM'
          };
        }
        narrative = `${themeIcon} The bio-signals in the ${theme} are fluctuating in nested frequencies.`;
        questionText = `Stabilize the wave vector: [ ${data.sequence.join(', ')}, ? ]`;
        break;
      }
      default: {
        templateName = 'Matrix Pattern Logic';
        calibration.rc = 5;
        calibration.cs = 5;
        calibration.rp = 3;
        calibration.wm = 5;
        calibration.dc = 3;
        calibration.vp = 4;
        calibration.t = 5;
        
        // 3x3 matrix pattern
        // Row-wise sum rule: Row 1 sum = X, Row 2 sum = X, Row 3 sum = X
        const sum = 30;
        const matrix = [
          [12, 10, 8],
          [5, 15, 10],
          [14, 7, 0] // 0 is empty slot
        ];
        correctAnswer = '9';
        hint = `Examine the horizontal rows. The sum of the integers in each row equals exactly ${sum}.`;
        data = { matrix, type: 'matrix', sum };
        
        const wrong1 = '11';
        const wrong2 = '6';
        const wrong3 = '14';
        options = [correctAnswer, wrong1, wrong2, wrong3];
        errorTypes = {
          [wrong1]: 'GP_ERROR',
          [wrong2]: 'RANDOM',
          [wrong3]: 'REC_ERROR'
        };
        
        narrative = `${themeIcon} The central gate processor in ${theme} requires a matrix coordinate key override.`;
        questionText = `Find the value of '?' in the grid processor:
Row 1: [ 12 | 10 | 8 ]
Row 2: [  5 | 15 | 10 ]
Row 3: [ 14 |  7 |  ? ]`;
        break;
      }
    }
  } else if (module === 'CompareBot') {
    let tIdx = Math.min(10, Math.max(1, (targetLevel - 1) * 2 + (sessionQuestionIndex % 2) + 1));
    templateId = `CB-T${tIdx < 10 ? '0' : ''}${tIdx}`;
    const themeIcon = THEME_ICONS[theme] || '⚖️';
    
    switch (tIdx) {
      case 1: {
        templateName = 'Magnitude Comparison';
        calibration.rc = 1;
        calibration.cs = 1;
        calibration.rp = 1;
        calibration.wm = 1;
        calibration.dc = 2;
        calibration.vp = 1;
        calibration.t = 1;
        
        const val1 = Math.floor(150 + Math.random() * 300);
        const val2 = Math.floor(150 + Math.random() * 300);
        const larger = val1 > val2 ? val1 : val2;
        
        correctAnswer = String(larger);
        hint = `Perform a basic comparison of both numbers. ${val1} vs ${val2}.`;
        data = { val1, val2 };
        options = [String(val1), String(val2)];
        
        narrative = `${themeIcon} The ${theme} storage system reports two storage sector levels. We need to route load to the larger one.`;
        questionText = `Which vector magnitude is larger? Sector Alpha: ${val1} or Sector Beta: ${val2}?`;
        break;
      }
      case 2: {
        templateName = 'Percentage Comparison';
        calibration.rc = 2;
        calibration.cs = 2;
        calibration.rp = 2;
        calibration.wm = 2;
        calibration.dc = 2;
        calibration.vp = 2;
        calibration.t = 2;
        
        // compare e.g., 20% of 150 (30) vs 40% of 70 (28)
        const pct1 = 20;
        const amt1 = 150;
        const pct2 = 40;
        const amt2 = 70;
        
        const calc1 = (pct1 / 100) * amt1; // 30
        const calc2 = (pct2 / 100) * amt2; // 28
        
        correctAnswer = `${pct1}% of ${amt1} (${calc1})`;
        hint = `Calculate the percentage value for both and compare. Vector A is ${pct1}% of ${amt1} = ${calc1}. Vector B is ${pct2}% of ${amt2} = ${calc2}.`;
        data = { pct1, amt1, pct2, amt2, calc1, calc2 };
        options = [correctAnswer, `${pct2}% of ${amt2} (${calc2})`, 'Both are equal', 'Insufficient data'];
        
        narrative = `${themeIcon} Calibrating sub-reactors inside ${theme}. Compare their energy outputs.`;
        questionText = `Which reactor output is larger? Reactor A (${pct1}% of ${amt1} units) or Reactor B (${pct2}% of ${amt2} units)?`;
        break;
      }
      case 3:
      case 6: {
        templateName = tIdx === 3 ? 'Fraction Comparison' : 'Mixed Representation Comparison';
        calibration.rc = 3;
        calibration.cs = 2;
        calibration.rp = 2;
        calibration.wm = 3;
        calibration.dc = 3;
        calibration.vp = 2;
        calibration.t = 3;
        
        if (tIdx === 3) {
          // 5/8 (0.625) vs 7/11 (0.636)
          correctAnswer = '7/11';
          hint = `Convert both fractions to decimals to compare. 5/8 is 0.625. 7/11 is approximately 0.636. Therefore, 7/11 is larger.`;
          data = { frac1: '5/8', frac2: '7/11', dec1: 0.625, dec2: 0.636 };
          options = ['5/8', '7/11', 'They are equal', 'None of these'];
          errorTypes = {
            '5/8': 'Fraction conversion error',
            'They are equal': 'Decimal confusion'
          };
          
          narrative = `${themeIcon} The ${theme} reports sub-channel bandwidth fractions.`;
          questionText = `Which storage bandwidth fraction is larger? Sub-channel 1: 5/8 or Sub-channel 2: 7/11?`;
        } else {
          // 3/5 (0.60) vs 58% (0.58)
          correctAnswer = '3/5';
          hint = `Convert 3/5 to a percentage: 3/5 = 60%. 60% is greater than 58%.`;
          data = { frac: '3/5', pct: '58%', decFrac: 0.60, decPct: 0.58 };
          options = ['3/5', '58%', 'Equal representation', 'No overlap'];
          errorTypes = {
            '58%': 'Percentage calculation error',
            'Equal representation': 'Decimal confusion'
          };
          
          narrative = `${themeIcon} Dual-format feedback received from ${theme} signal arrays.`;
          questionText = `Which cognitive load efficiency index is larger? Array Core: 3/5 or Grid Array: 58%?`;
        }
        break;
      }
      case 4:
      case 5: {
        templateName = tIdx === 4 ? 'Ratio Comparison' : 'Decimal Comparison';
        calibration.rc = 3;
        calibration.cs = 3;
        calibration.rp = 2;
        calibration.wm = 3;
        calibration.dc = 3;
        calibration.vp = 2;
        calibration.t = 3;
        
        if (tIdx === 4) {
          // 3:5 (0.6) vs 5:8 (0.625)
          correctAnswer = '5:8';
          hint = `Write ratios as fractions and divide: 3/5 = 0.60, 5/8 = 0.625. Thus, 5:8 represents a larger proportion.`;
          data = { ratio1: '3:5', ratio2: '5:8', dec1: 0.60, dec2: 0.625 };
          options = ['3:5', '5:8', 'They are identical', 'Indeterminate'];
          errorTypes = {
            '3:5': 'Ratio misunderstanding',
            'They are identical': 'Decimal confusion'
          };
          
          narrative = `${themeIcon} Analyzing chemical power compound mixtures in the ${theme}.`;
          questionText = `Which oxygen-to-nitrogen stabilization ratio is higher? Catalyst Alfa: 3:5 or Catalyst Beta: 5:8?`;
        } else {
          // 0.089 vs 0.12
          correctAnswer = '0.12';
          hint = `Be careful with trailing digits! 0.12 is equivalent to 0.120, which is larger than 0.089.`;
          data = { dec1: 0.089, dec2: 0.12 };
          options = ['0.089', '0.12', 'They are equal', '0.009'];
          errorTypes = {
            '0.089': 'Decimal confusion',
            '0.009': 'Estimation bias'
          };
          
          narrative = `${themeIcon} Read pressure logs of active steam seals in ${theme}.`;
          questionText = `Identify the larger pressure valve reading: 0.089 bar vs 0.12 bar.`;
        }
        break;
      }
      default: {
        templateName = 'Equivalent Expressions & Estimation';
        calibration.rc = 4;
        calibration.cs = 4;
        calibration.rp = 2;
        calibration.wm = 4;
        calibration.dc = 4;
        calibration.vp = 2;
        calibration.t = 4;
        
        // CB-T07: 4*3+5 (17) vs 2*8+1 (17) -> Equivalent
        correctAnswer = 'Both expressions are equal';
        hint = `Evaluate both math equations: Expression A is 4 * 3 + 5 = 17. Expression B is 2 * 8 + 1 = 17. They are equal.`;
        data = { exp1: '4 * 3 + 5', exp2: '2 * 8 + 1', val1: 17, val2: 17 };
        options = ['Expression A is larger', 'Expression B is larger', 'Both expressions are equal', 'They cannot be resolved'];
        errorTypes = {
          'Expression A is larger': 'Percentage calculation error',
          'Expression B is larger': 'Decimal confusion'
        };
        
        narrative = `${themeIcon} Resolving signal pulse equivalence metrics inside ${theme}.`;
        questionText = `Compare the computational power values of: Expression A: "4 * 3 + 5" vs Expression B: "2 * 8 + 1".`;
        break;
      }
    }
  } else if (module === 'VisionBot') {
    let tIdx = Math.min(10, Math.max(1, (targetLevel - 1) * 2 + (sessionQuestionIndex % 2) + 1));
    templateId = `VB-T${tIdx < 10 ? '0' : ''}${tIdx}`;
    const themeIcon = THEME_ICONS[theme] || '📊';
    
    switch (tIdx) {
      case 1:
      case 2: {
        templateName = tIdx === 1 ? 'Bar Graph Analysis' : 'Table Dataset Analysis';
        calibration.rc = 2;
        calibration.cs = 2;
        calibration.rp = 3;
        calibration.wm = 3;
        calibration.dc = 2;
        calibration.vp = 3;
        calibration.t = 2;
        
        if (tIdx === 1) {
          // Bar Graph of 4 sectors
          const values = [45, 62, 35, 78];
          const labels = ['Sector Alfa', 'Sector Beta', 'Sector Gamma', 'Sector Delta'];
          correctAnswer = 'Sector Delta (78)';
          hint = `Examine the bar heights. Sector Delta reaches the highest index of 78, while Sector Beta is 62.`;
          data = { labels, values, chartType: 'bar' };
          options = ['Sector Delta (78)', 'Sector Beta (62)', 'Sector Alfa (45)', 'Sector Gamma (35)'];
          errorTypes = {
            'Sector Beta (62)': 'Misread graph',
            'Sector Gamma (35)': 'Wrong average'
          };
          
          narrative = `${themeIcon} The ${theme} telemetry control panel plots power loads.`;
          questionText = `Which grid sector possesses the maximum active load according to the bar metrics? [ Alfa: 45 | Beta: 62 | Gamma: 35 | Delta: 78 ]`;
        } else {
          // Table Analysis
          const dataset = [
            { id: 'R1', coreA: 10, coreB: 15 },
            { id: 'R2', coreA: 20, coreB: 18 },
            { id: 'R3', coreA: 15, coreB: 25 }
          ];
          correctAnswer = 'Row 3 (Sum 40)';
          hint = `Sum the Core A and Core B metrics for each row: Row 1 = 25. Row 2 = 38. Row 3 = 40. Row 3 is highest.`;
          data = { dataset, chartType: 'table' };
          options = ['Row 3 (Sum 40)', 'Row 2 (Sum 38)', 'Row 1 (Sum 25)', 'Row 2 and 3 are equal'];
          errorTypes = {
            'Row 2 (Sum 38)': 'Calculation error',
            'Row 1 (Sum 25)': 'Misread graph'
          };
          
          narrative = `${themeIcon} Examine the micro-array core telemetry matrix in ${theme}.`;
          questionText = `Which telemetry node row has the highest combined signal throughput?
Row 1: [ Core A: 10 | Core B: 15 ]
Row 2: [ Core A: 20 | Core B: 18 ]
Row 3: [ Core A: 15 | Core B: 25 ]`;
        }
        break;
      }
      case 3:
      case 4: {
        templateName = tIdx === 3 ? 'Line Graph Trend' : 'Pie Chart Percentage';
        calibration.rc = 3;
        calibration.cs = 3;
        calibration.rp = 3;
        calibration.wm = 3;
        calibration.dc = 3;
        calibration.vp = 3;
        calibration.t = 3;
        
        if (tIdx === 3) {
          // Line graph trend
          correctAnswer = 'Overall Upward Trend with peak at Index 5';
          hint = `Look at the chronological progression of points: 22 -> 31 -> 28 -> 45 -> 58 -> 52. The general movement is increasing.`;
          data = { points: [22, 31, 28, 45, 58, 52], chartType: 'line' };
          options = [
            'Overall Upward Trend with peak at Index 5',
            'Steady decline with valley at Index 3',
            'Flat stationary signal curve',
            'Chaotic erratic frequency shift'
          ];
          errorTypes = {
            'Steady decline with valley at Index 3': 'Trend misunderstanding',
            'Flat stationary signal curve': 'Calculation error'
          };
          
          narrative = `${themeIcon} The oscilloscope in ${theme} records feedback output levels over 6 epochs.`;
          questionText = `Interpret the trend trajectory of values: Epochs 1-6 are [ 22, 31, 28, 45, 58, 52 ] respectively.`;
        } else {
          // Pie chart
          correctAnswer = 'Oxygen (45%)';
          hint = `The slices are: Oxygen (45%), Nitrogen (30%), Carbon (15%), Argon (10%). Oxygen represents nearly half the composition.`;
          data = { slices: [45, 30, 15, 10], labels: ['Oxygen', 'Nitrogen', 'Carbon', 'Argon'], chartType: 'pie' };
          options = ['Oxygen (45%)', 'Nitrogen (30%)', 'Carbon (15%)', 'Argon (10%)'];
          errorTypes = {
            'Nitrogen (30%)': 'Misread graph',
            'Carbon (15%)': 'Wrong average'
          };
          
          narrative = `${themeIcon} High-altitude composition metrics of biosignals inside ${theme}.`;
          questionText = `Which composition segment makes up the single largest component in the pie allocation?`;
        }
        break;
      }
      default: {
        templateName = 'Multi-source Grid Heatmap';
        calibration.rc = 4;
        calibration.cs = 4;
        calibration.rp = 4;
        calibration.wm = 4;
        calibration.dc = 3;
        calibration.vp = 4;
        calibration.t = 4;
        
        // Heatmap Grid: 3x3
        // [ 10, 40, 15 ]
        // [ 90, 12, 60 ]
        // [ 20, 30, 85 ]
        correctAnswer = 'Node (2, 1) at value 90';
        hint = `Find the cell with the largest numerical load: Row 2, Col 1 is 90. Row 3, Col 3 is 85.`;
        data = { grid: [[10, 40, 15], [90, 12, 60], [20, 30, 85]], chartType: 'heatmap' };
        options = ['Node (2, 1) at value 90', 'Node (3, 3) at value 85', 'Node (1, 2) at value 40', 'Node (2, 3) at value 60'];
        errorTypes = {
          'Node (3, 3) at value 85': 'Wrong maximum/minimum',
          'Node (1, 2) at value 40': 'Misread graph'
        };
        
        narrative = `${themeIcon} The thermal sensor heatmap matrix in ${theme} shows localized CPU core hot spots.`;
        questionText = `Identify the coordinates [Row, Col] of the thermal spike with maximum temperature:
Row 1: [ 10 | 40 | 15 ]
Row 2: [ 90 | 12 | 60 ]
Row 3: [ 20 | 30 | 85 ]`;
        break;
      }
    }
  } else {
    // SolverBot
    let tIdx = Math.min(10, Math.max(1, (targetLevel - 1) * 2 + (sessionQuestionIndex % 2) + 1));
    templateId = `SB-T${tIdx < 10 ? '0' : ''}${tIdx}`;
    const themeIcon = THEME_ICONS[theme] || '🎯';
    
    switch (tIdx) {
      case 1: {
        templateName = 'Equal Distribution Planning';
        calibration.rc = 1;
        calibration.cs = 2;
        calibration.rp = 2;
        calibration.wm = 2;
        calibration.dc = 2;
        calibration.cl = 2;
        calibration.t = 2;
        
        const totalLoad = 120;
        const slots = 4;
        correctAnswer = '30 units per slot';
        hint = `To find equal distribution, divide the total load by slots: ${totalLoad} / ${slots} = 30.`;
        data = { totalLoad, slots };
        options = ['30 units per slot', '40 units per slot', '25 units per slot', '20 units per slot'];
        errorTypes = {
          '40 units per slot': 'Capacity miscalculation',
          '25 units per slot': 'Arithmetic error'
        };
        
        narrative = `${themeIcon} High volume load balancing required in ${theme} backup batteries.`;
        questionText = `How should you distribute ${totalLoad} reserve cells equally across ${slots} sub-nodes?`;
        break;
      }
      case 2:
      case 3: {
        templateName = tIdx === 2 ? 'Capacity Optimization' : 'Resource Allocation';
        calibration.rc = 3;
        calibration.cs = 3;
        calibration.rp = 2;
        calibration.wm = 3;
        calibration.dc = 3;
        calibration.cl = 3;
        calibration.t = 3;
        
        if (tIdx === 2) {
          // Minimum drone fleet calculation (Delivery of 520 units. Large=80, Med=40, Small=20)
          correctAnswer = '6 Large, 1 Medium';
          hint = `Large drone holds 80. Large count = 520 / 80 = 6 (480 units). Remainder = 40. Large medium counts needed: 6 Large (480) + 1 Medium (40) = 520. Minimum fleet size = 7.`;
          data = { target: 520, large: 80, med: 40, small: 20 };
          options = ['6 Large, 1 Medium', '5 Large, 3 Medium', '13 Medium', '26 Small'];
          errorTypes = {
            '5 Large, 3 Medium': 'Non-optimal solution',
            '13 Medium': 'Allocation mistake',
            '26 Small': 'Capacity miscalculation'
          };
          
          narrative = `${themeIcon} Delivering heavy isotope rods in ${theme}. Minimum flight fleet is needed.`;
          questionText = `Calculate the optimal fleet config to deliver exactly 520 resource units using the minimum total drones: [ Large Drone: 80 caps | Medium: 40 caps | Small: 20 caps ]`;
        } else {
          // Distributed constraints: 12 Cells total. Sector A (Hub) >= 4, Sector B (Cryo) <= 5, Sector C (Bio) === 3
          correctAnswer = 'Hub: 5, Cryo: 4, Bio: 3';
          hint = `Verify constraints: Total must equal 12. Hub (5) >= 4 [OK]. Cryo (4) <= 5 [OK]. Bio (3) === 3 [OK]. Sum: 5+4+3=12 [OK].`;
          data = { total: 12, constraints: ['Hub >= 4', 'Cryo <= 5', 'Bio = 3'] };
          options = ['Hub: 5, Cryo: 4, Bio: 3', 'Hub: 3, Cryo: 6, Bio: 3', 'Hub: 6, Cryo: 3, Bio: 3', 'Hub: 4, Cryo: 4, Bio: 4'];
          errorTypes = {
            'Hub: 3, Cryo: 6, Bio: 3': 'Ignored constraints',
            'Hub: 4, Cryo: 4, Bio: 4': 'Non-optimal solution'
          };
          
          narrative = `${themeIcon} Allocate exactly 12 power cells to 3 sectors inside ${theme}.`;
          questionText = `Which power cells allocation satisfies all safety constraints simultaneously:
- Sector A (Hub): Needs at least 4 cells
- Sector B (Cryo Lab): Cannot exceed 5 cells
- Sector C (Biosphere): Needs exactly 3 cells`;
        }
        break;
      }
      default: {
        templateName = 'Multi-constraint Routing Optimization';
        calibration.rc = 5;
        calibration.cs = 5;
        calibration.rp = 3;
        calibration.wm = 4;
        calibration.dc = 4;
        calibration.cl = 5;
        calibration.t = 5;
        
        correctAnswer = 'Grid Route [A -> C -> D] at Cost 14';
        hint = `Check paths from Start node A to Target D:
- Path A -> B -> D: Cost 6 + 10 = 16.
- Path A -> C -> D: Cost 5 + 9 = 14.
Path A -> C -> D is the absolute shortest path at cost 14.`;
        data = { nodes: ['A', 'B', 'C', 'D'], links: { 'A-B': 6, 'A-C': 5, 'B-D': 10, 'C-D': 9 } };
        options = ['Grid Route [A -> C -> D] at Cost 14', 'Grid Route [A -> B -> D] at Cost 16', 'Direct Jump [A -> D] at Cost 20', 'Route [A -> B -> C -> D] at Cost 22'];
        errorTypes = {
          'Grid Route [A -> B -> D] at Cost 16': 'Non-optimal solution',
          'Direct Jump [A -> D] at Cost 20': 'Arithmetic error'
        };
        
        narrative = `${themeIcon} A courier drone in ${theme} needs to travel from Source Core A to Target Gate D.`;
        questionText = `Find the shortest routing path through the relay points: [ Alfa-Beta: 6 | Alfa-Gamma: 5 | Beta-Delta: 10 | Gamma-Delta: 9 ]`;
        break;
      }
    }
  }

  const calculatedDifficulty = calculateDifficultyScore(calibration);
  const difficultyLevel = mapDifficultyToLevel(calculatedDifficulty);

  // Randomly shuffle options to meet Deliverable 4 distractor randomizer criteria
  const shuffledOptions = [...options].sort(() => Math.random() - 0.5);

  return {
    id: `${templateId}-${difficultyLevel}-V${variantStr.slice(1)}`,
    templateId,
    module,
    templateName,
    difficultyLevel,
    calculatedDifficulty,
    calibration,
    storyTheme: theme,
    narrative,
    data,
    questionText,
    options: shuffledOptions,
    correctAnswer,
    hint,
    errorTypes
  };
}
