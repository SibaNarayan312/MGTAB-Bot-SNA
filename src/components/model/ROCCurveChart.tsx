import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { ROCPoint } from '../../types/model';
import { formatPercent, formatDecimal } from '../../utils/formatters';

interface ROCCurveChartProps {
  rocCurve?: ROCPoint[];
  rocAuc?: number;
}

export const ROCCurveChart: React.FC<ROCCurveChartProps> = ({ rocCurve, rocAuc }) => {
  if (!rocCurve || rocCurve.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-400">
        ROC Curve data not provided.
      </div>
    );
  }

  // Ensure points sorted by FPR
  const sortedPoints = [...rocCurve].sort((a, b) => a.fpr - b.fpr);

  return (
    <div className="w-full h-72 flex flex-col">
      <div className="flex-1 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sortedPoints} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="fpr"
              type="number"
              domain={[0, 1]}
              stroke="#64748b"
              fontSize={11}
              tickFormatter={(v) => formatPercent(v, 0)}
              label={{
                value: 'False Positive Rate (1 - Specificity)',
                position: 'insideBottom',
                offset: -12,
                fill: '#94a3b8',
                fontSize: 11,
              }}
            />
            <YAxis
              dataKey="tpr"
              type="number"
              domain={[0, 1]}
              stroke="#64748b"
              fontSize={11}
              tickFormatter={(v) => formatPercent(v, 0)}
              label={{
                value: 'True Positive Rate (Sensitivity)',
                angle: -90,
                position: 'insideLeft',
                offset: 12,
                fill: '#94a3b8',
                fontSize: 11,
              }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as ROCPoint;
                  return (
                    <div className="p-2.5 bg-slate-900 border border-slate-700 rounded-lg shadow-xl text-xs font-mono">
                      <div className="text-cyan-400 font-bold">ROC Point</div>
                      <div className="text-slate-300">TPR (Recall): {formatPercent(data.tpr, 2)}</div>
                      <div className="text-slate-400">FPR: {formatPercent(data.fpr, 2)}</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            {/* Random diagonal baseline (y = x) */}
            <ReferenceLine
              segment={[
                { x: 0, y: 0 },
                { x: 1, y: 1 },
              ]}
              stroke="#475569"
              strokeDasharray="4 4"
            />
            <Line
              type="monotone"
              dataKey="tpr"
              stroke="#06b6d4"
              strokeWidth={3}
              dot={{ r: 3, fill: '#06b6d4' }}
              activeDot={{ r: 6, fill: '#38bdf8' }}
              name="RGCN Multi-Relational Model"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {rocAuc !== undefined && (
        <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800 font-mono">
          <span className="text-slate-400">Area Under Curve (ROC-AUC):</span>
          <span className="font-bold text-cyan-400">{formatDecimal(rocAuc, 4)}</span>
        </div>
      )}
    </div>
  );
};
