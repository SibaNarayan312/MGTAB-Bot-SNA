import React from 'react';
import { formatPercent } from '../../utils/formatters';

interface ProbabilityBarProps {
  probability: number; // 0 to 1
  label?: string;
  showLabels?: boolean;
}

export const ProbabilityBar: React.FC<ProbabilityBarProps> = ({
  probability,
  label = 'Bot Likelihood',
  showLabels = true,
}) => {
  const clampedProb = Math.max(0, Math.min(1, probability));
  const botPercent = clampedProb * 100;
  const humanPercent = 100 - botPercent;

  const isHighRisk = clampedProb >= 0.7;
  const isModerate = clampedProb >= 0.4 && clampedProb < 0.7;

  return (
    <div className="w-full space-y-1.5">
      {showLabels && (
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400 font-medium">{label}</span>
          <span
            className={`font-mono font-bold ${
              isHighRisk
                ? 'text-red-400'
                : isModerate
                ? 'text-amber-400'
                : 'text-emerald-400'
            }`}
          >
            {formatPercent(clampedProb)}
          </span>
        </div>
      )}

      {/* Segmented Visual Progress Bar */}
      <div className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden flex border border-slate-700/50">
        <div
          className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-500"
          style={{ width: `${humanPercent}%` }}
          title={`Human Probability: ${humanPercent.toFixed(1)}%`}
        />
        <div
          className="h-full bg-gradient-to-r from-red-500 to-rose-600 transition-all duration-500"
          style={{ width: `${botPercent}%` }}
          title={`Bot Probability: ${botPercent.toFixed(1)}%`}
        />
      </div>

      {showLabels && (
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>Human ({humanPercent.toFixed(0)}%)</span>
          <span>Bot ({botPercent.toFixed(0)}%)</span>
        </div>
      )}
    </div>
  );
};
