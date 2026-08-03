/* =====================================================
   ASAT – PDF Report Generator
   Uses jsPDF for client-side PDF generation
   ===================================================== */

import jsPDF from 'jspdf';

export function generatePDF({ student, scores, moduleResults, recs, today }) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
  const W = 210; // A4 width mm
  const margin = 18;
  let y = margin;

  const colors = {
    primary:   [26, 35, 126],
    accent:    [0, 188, 212],
    success:   [76, 175, 80],
    warning:   [251, 140, 0],
    error:     [229, 57, 53],
    dark:      [10, 10, 15],
    text:      [30, 30, 40],
    muted:     [120, 120, 140],
    white:     [255, 255, 255],
  };

  /* ── helpers ── */
  function setFont(size, style = 'normal', color = colors.text) {
    doc.setFontSize(size);
    doc.setFont('helvetica', style);
    doc.setTextColor(...color);
  }

  function fillRect(x, fx, fy, fw, fh, color) {
    doc.setFillColor(...color);
    doc.roundedRect(x ?? margin, fy, fw, fh, 3, 3, 'F');
  }

  function drawLine(ly = y, opacity = 0.15) {
    doc.setDrawColor(200, 200, 220);
    doc.setLineWidth(0.3);
    doc.line(margin, ly, W - margin, ly);
  }

  function addText(text, tx, ty, align = 'left') {
    doc.text(String(text), tx, ty, { align });
  }

  function scoreColor(score) {
    if (score >= 65) return colors.success;
    if (score >= 50) return colors.warning;
    return colors.error;
  }

  function scoreLabel(score) {
    if (score >= 80) return 'Excellent';
    if (score >= 65) return 'Good';
    if (score >= 50) return 'Average';
    return 'Needs Work';
  }

  /* ── HEADER BANNER ── */
  doc.setFillColor(...colors.primary);
  doc.rect(0, 0, W, 38, 'F');
  // Accent stripe
  doc.setFillColor(...colors.accent);
  doc.rect(0, 35, W, 3, 'F');

  setFont(22, 'bold', colors.white);
  addText('ASAT Attention Assessment Report', margin, 16);
  setFont(10, 'normal', [180, 210, 255]);
  addText('Adaptive Shape Attention Task | IIT Madras MentiScope Project', margin, 25);
  setFont(9, 'normal', [160, 190, 240]);
  addText(`Generated: ${today}`, margin, 32);

  y = 48;

  /* ── STUDENT INFO ── */
  doc.setFillColor(240, 242, 255);
  doc.roundedRect(margin, y, W - margin * 2, 26, 3, 3, 'F');
  setFont(10, 'bold', colors.primary);
  addText('Student Information', margin + 5, y + 7);
  setFont(9, 'normal', colors.text);
  addText(`Name: ${student.fullName}`, margin + 5, y + 14);
  addText(`ID: ${student.studentId}`, margin + 5, y + 20);
  addText(`Grade: ${student.grade}  |  Age: ${student.age}  |  School: ${student.school || 'Not specified'}`, W / 2, y + 14);
  y += 32;

  /* ── OVERALL SCORE ── */
  doc.setFillColor(...colors.primary);
  doc.roundedRect(margin, y, W - margin * 2, 28, 4, 4, 'F');
  setFont(12, 'bold', colors.white);
  addText('Overall Score', margin + 5, y + 9);
  setFont(24, 'bold', colors.accent);
  addText(`${scores.overall}/100`, margin + 5, y + 22);
  setFont(10, 'normal', [200, 220, 255]);
  addText(`Status: ${scoreLabel(scores.overall)} Attention`, margin + 50, y + 14);
  addText(`Percentile: ${scores.percentile}th`, margin + 50, y + 22);
  y += 34;

  /* ── MODULE SCORES ── */
  setFont(11, 'bold', colors.primary);
  addText('Module Scores', margin, y + 7);
  y += 12;

  const modules = [
    { name: 'Sustained Attention',  score: scores.sustained,  weight: '25%' },
    { name: 'Selective Attention',  score: scores.selective,  weight: '25%' },
    { name: 'Divided Attention',    score: scores.divided,    weight: '20%' },
    { name: 'Executive Attention',  score: scores.executive,  weight: '30%' },
  ];

  modules.forEach((m, i) => {
    const rowY = y + i * 16;
    // Row bg
    if (i % 2 === 0) {
      doc.setFillColor(246, 248, 255);
      doc.roundedRect(margin, rowY - 4, W - margin * 2, 14, 2, 2, 'F');
    }
    setFont(9, 'bold', colors.text);
    addText(m.name, margin + 4, rowY + 5);
    setFont(8, 'normal', colors.muted);
    addText(`Weight: ${m.weight}`, margin + 76, rowY + 5);
    // Score
    setFont(10, 'bold', scoreColor(m.score));
    addText(`${m.score}/100`, W - margin - 30, rowY + 5);
    setFont(8, 'normal', scoreColor(m.score));
    addText(scoreLabel(m.score), W - margin - 15, rowY + 5, 'right');
    // Progress bar bg
    doc.setFillColor(220, 225, 235);
    doc.roundedRect(margin + 105, rowY + 1, 50, 4, 2, 2, 'F');
    // Progress bar fill
    doc.setFillColor(...scoreColor(m.score));
    doc.roundedRect(margin + 105, rowY + 1, 50 * (m.score / 100), 4, 2, 2, 'F');
  });

  y += modules.length * 16 + 8;
  drawLine(y);
  y += 6;

  /* ── PERFORMANCE DETAILS ── */
  setFont(11, 'bold', colors.primary);
  addText('Performance Details', margin, y + 6);
  y += 12;

  const tableHeaders = ['Metric', 'Sustained', 'Selective', 'Divided', 'Executive'];
  const colW = (W - margin * 2) / 5;

  // Header row
  doc.setFillColor(...colors.primary);
  doc.roundedRect(margin, y, W - margin * 2, 9, 2, 2, 'F');
  setFont(8, 'bold', colors.white);
  tableHeaders.forEach((h, i) => addText(h, margin + i * colW + 3, y + 6));
  y += 10;

  const tableRows = [
    ['Hit Rate',
      `${moduleResults.sustained?.hitRate ?? '—'}%`,
      `${moduleResults.selective?.hitRate ?? '—'}%`,
      `${moduleResults.divided?.hitRate ?? '—'}%`,
      `—`
    ],
    ['Avg RT',
      `${moduleResults.sustained?.avgRT ?? '—'}ms`,
      `—`,
      `—ms`,
      `—`
    ],
    ['Errors / False',
      `${moduleResults.sustained?.missed ?? '—'} missed`,
      `${moduleResults.selective?.wrongClicks ?? '—'} false`,
      `${moduleResults.divided?.falsePresses ?? '—'} false`,
      `${moduleResults.executive?.errorCount ?? '—'} err`
    ],
    ['Key Metric',
      `RT SD: ${moduleResults.sustained?.rtStdDev ?? '—'}ms`,
      `Dist: ${moduleResults.selective?.distractorCost ?? '—'}ms`,
      `Split: ${moduleResults.divided?.splitCost ?? '—'}ms`,
      `Switch: ${moduleResults.executive?.switchCost ?? '—'}ms`
    ],
  ];

  tableRows.forEach((row, ri) => {
    if (ri % 2 === 0) {
      doc.setFillColor(246, 248, 255);
      doc.roundedRect(margin, y, W - margin * 2, 9, 1, 1, 'F');
    }
    setFont(7.5, ri === 0 ? 'bold' : 'normal', colors.text);
    row.forEach((cell, ci) => {
      addText(cell, margin + ci * colW + 3, y + 6);
    });
    y += 10;
  });

  y += 6;
  drawLine(y);
  y += 8;

  /* ── STRENGTHS & WEAKNESSES ── */
  setFont(11, 'bold', colors.primary);
  addText('Strengths', margin, y + 6);
  y += 12;

  const strong = modules.filter(m => m.score >= 65);
  const weak   = modules.filter(m => m.score < 65);

  if (strong.length === 0) {
    setFont(9, 'normal', colors.muted);
    addText('Keep practicing — continued effort will improve all areas.', margin + 4, y + 5);
    y += 12;
  } else {
    strong.forEach(m => {
      doc.setFillColor(232, 245, 233);
      doc.roundedRect(margin, y, W - margin * 2, 10, 2, 2, 'F');
      doc.setFillColor(...colors.success);
      doc.circle(margin + 5, y + 5, 2.5, 'F');
      setFont(9, 'bold', colors.success);
      addText(`${m.name} — ${m.score}/100`, margin + 12, y + 6);
      setFont(8, 'normal', colors.muted);
      addText(scoreLabel(m.score), W - margin - 5, y + 6, 'right');
      y += 13;
    });
  }

  y += 2;
  setFont(11, 'bold', colors.primary);
  addText('Areas to Improve', margin, y + 6);
  y += 12;

  if (weak.length === 0) {
    setFont(9, 'normal', colors.muted);
    addText('All areas are performing well. Excellent work!', margin + 4, y + 5);
    y += 12;
  } else {
    weak.forEach(m => {
      doc.setFillColor(255, 243, 224);
      doc.roundedRect(margin, y, W - margin * 2, 10, 2, 2, 'F');
      doc.setFillColor(...colors.warning);
      doc.circle(margin + 5, y + 5, 2.5, 'F');
      setFont(9, 'bold', colors.warning);
      addText(`${m.name} — ${m.score}/100`, margin + 12, y + 6);
      setFont(8, 'normal', colors.muted);
      addText('Needs improvement', W - margin - 5, y + 6, 'right');
      y += 13;
    });
  }

  drawLine(y + 4);
  y += 10;

  /* ── STUDY STRATEGIES ── */
  setFont(11, 'bold', colors.primary);
  addText('Study Strategies', margin, y + 6);
  y += 12;

  recs.strategies.forEach((s, i) => {
    setFont(9, 'normal', colors.text);
    const lines = doc.splitTextToSize(`${i + 1}. ${s}`, W - margin * 2 - 6);
    doc.text(lines, margin + 4, y + 5);
    y += lines.length * 6 + 4;
  });

  /* ── CAREER RECOMMENDATIONS ── */
  y += 2;
  setFont(11, 'bold', colors.primary);
  addText('Career Recommendations', margin, y + 6);
  y += 12;

  setFont(9, 'bold', colors.success);
  addText('Good Fit:', margin + 4, y + 5);
  setFont(9, 'normal', colors.text);
  addText(recs.careers.good.join(', '), margin + 28, y + 5);
  y += 10;

  if (recs.careers.poor.length) {
    setFont(9, 'bold', colors.warning);
    addText('Challenging:', margin + 4, y + 5);
    setFont(9, 'normal', colors.text);
    addText(recs.careers.poor.join(', '), margin + 32, y + 5);
    y += 10;
  }

  /* ── FOOTER ── */
  const pageH = 297;
  doc.setFillColor(...colors.primary);
  doc.rect(0, pageH - 14, W, 14, 'F');
  setFont(8, 'normal', [180, 210, 255]);
  addText('ASAT – Adaptive Shape Attention Task | IIT Madras MentiScope Project | © 2026', W / 2, pageH - 5, 'center');

  // Save PDF
  const fileName = `ASAT_Report_${student.studentId}_${today.replace(/ /g, '_')}.pdf`;
  doc.save(fileName);
}
