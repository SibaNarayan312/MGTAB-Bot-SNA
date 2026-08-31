import React from 'react';
import { FeatureImportance } from '../../types/user';
import { formatPercent } from '../../utils/formatters';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface FeatureImportanceChartProps {
  explanations?: FeatureImportance[];
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({ explanations }) => {
  if (!explanations || explanations.length === 0) {
    return (
      <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 text-xs text-slate-400 text-center">
        Explanation data is not available for this prediction.
      </div>
    );
  }

  // Sort by highest importance
  const sorted = [...explanations].sort((a, b) => b.importance - a.importance);

  return (
    <div className="space-y-3.5">
      {sorted.map((item, idx) => {
        const percent = Math.min(100, Math.max(0, item.importance * 100));
        const isBotPush = item.direction === 'positive';
        const isHumanPush = item.direction === 'negative';

        return (
          <div key={idx} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5">
                {isBotPush && <ArrowUpRight className="w-3.5 h-3.5 text-red-400 shrink-0" />}
                {isHumanPush && <ArrowDownRight className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                {!item.direction && <Minus className="w-3.5 h-3.5 text-slate-500 shrink-0" />}
                <span className="font-semibold text-slate-200">{item.feature}</span>
              </div>
              <span className="font-mono font-bold text-cyan-400">
                {formatPercent(item.importance)}
              </span>
            </div>

            {/* Custom Styled Bar */}
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden border border-slate-700/40">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isBotPush
                    ? 'bg-gradient-to-r from-red-600 to-rose-500'
                    : isHumanPush
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-400'
                    : 'bg-gradient-to-r from-cyan-600 to-blue-500'
                }`}
                style={{ width: `${percent}%` }}
              />
            </div>

            {item.description && (
              <p className="text-[11px] text-slate-400 pl-5 leading-tight">
                {item.description}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};
