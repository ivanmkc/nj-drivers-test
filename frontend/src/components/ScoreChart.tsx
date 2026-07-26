import { useRef, useEffect, useCallback } from 'react';
import type { QuizResult } from '../types';
import { CHART_HEIGHT, MAX_CHART_ENTRIES } from '../constants';

interface ScoreChartProps {
  history: QuizResult[];
  passingPct: number;
}

export default function ScoreChart({ history, passingPct }: ScoreChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = CHART_HEIGHT * dpr;
    canvas.style.height = `${CHART_HEIGHT}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = CHART_HEIGHT;
    const pad = { top: 20, right: 16, bottom: 30, left: 36 };
    const plotW = W - pad.left - pad.right;
    const plotH = H - pad.top - pad.bottom;
    const data = history.slice(-MAX_CHART_ENTRIES);
    const n = data.length;

    ctx.clearRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#9ca3af';
    ctx.font = '11px system-ui';
    ctx.textAlign = 'right';
    for (const pct of [0, 25, 50, 75, 100]) {
      const y = pad.top + plotH - (pct / 100) * plotH;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(W - pad.right, y);
      ctx.stroke();
      ctx.fillText(pct + '%', pad.left - 6, y + 4);
    }

    // Passing line
    const passY = pad.top + plotH - (passingPct / 100) * plotH;
    ctx.strokeStyle = '#16a34a40';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, passY);
    ctx.lineTo(W - pad.right, passY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Data points
    const points = data.map((d, i) => ({
      x: pad.left + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW),
      y: pad.top + plotH - (d.pct / 100) * plotH,
      pct: d.pct,
    }));

    // Line
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    points.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
    ctx.stroke();

    // Fill
    ctx.beginPath();
    points.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
    ctx.lineTo(points[points.length - 1].x, pad.top + plotH);
    ctx.lineTo(points[0].x, pad.top + plotH);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, pad.top, 0, pad.top + plotH);
    grad.addColorStop(0, 'rgba(37, 99, 235, 0.2)');
    grad.addColorStop(1, 'rgba(37, 99, 235, 0.02)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Dots
    points.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = p.pct >= passingPct ? '#16a34a' : '#dc2626';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Labels
    ctx.fillStyle = '#9ca3af';
    ctx.font = '10px system-ui';
    ctx.textAlign = 'center';
    const startNum = history.length - data.length + 1;
    const step = n <= 10 ? 1 : 2;
    points.forEach((p, i) => {
      if (i % step === 0 || i === n - 1) {
        ctx.fillText('#' + (startNum + i), p.x, H - pad.bottom + 16);
      }
    });
  }, [history, passingPct]);

  useEffect(() => {
    draw();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const observer = new ResizeObserver(draw);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      height={CHART_HEIGHT}
      className="w-full"
      style={{ height: CHART_HEIGHT }}
    />
  );
}
