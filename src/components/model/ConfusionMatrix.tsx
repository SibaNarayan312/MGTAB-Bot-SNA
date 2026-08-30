import React from 'react';
import { ConfusionMatrixData } from '../../types/model';
import { formatNumber, formatPercent } from '../../utils/formatters';

interface ConfusionMatrixProps {
  data: ConfusionMatrixData;
}

export const ConfusionMatrix: React.FC<ConfusionMatrixProps> = ({ data }) => {
  const total = data.true_negative + data.false_positive + data.false_negative + data.true_positive;

  const tnPct = total > 0 ? data.true_negative / total : 0;
  const fpPct = total > 0 ? data.false_positive / total : 0;
  const fnPct = total > 0 ? data.false_negative / total : 0;
  const tpPct = total > 0 ? data.true_positive / total : 0;

  return (
    <div className="w-full space-y-4">
      {/* Matrix Visual Container */}
      <div className="grid grid-cols-[auto_1fr_1fr] gap-2 items-center text-xs font-mono">
        {/* Top Header Row for Predicted */}
        <div />
        <div className="text-center font-semibold text-slate-300 py-1 bg-slate-900/60 rounded border border-slate-800">
          Predicted Human
        </div>
        <div className="text-center font-semibold text-slate-300 py-1 bg-slate-900/60 rounded border border-slate-800">
          Predicted Bot
        </div>

        {/* Row 1: Actual Human */}
        <div className="font-semibold text-slate-300 pr-2 text-right">
          Actual Human
        </div>
        {/* True Negative (TN) */}
        <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/20 text-center space-y-1 shadow-inner">
          <span className="text-[10px] uppercase font-sans font-bold text-emerald-400 block tracking-wider">
            True Negative (TN)
          </span>
          <div className="text-xl font-bold text-emerald-300">
            {formatNumber(data.true_negative)}
          </div>
          <span className="text-[10px] text-emerald-400/80 block">
            {formatPercent(tnPct)} of test set
          </span>
        </div>

        {/* False Positive (FP) */}
        <div className="p-4 rounded-xl border border-red-500/30 bg-red-950/20 text-center space-y-1 shadow-inner">
          <span className="text-[10px] uppercase font-sans font-bold text-amber-400 block tracking-wider">
            False Positive (FP)
          </span>
          <div className="text-xl font-bold text-red-300">
            {formatNumber(data.false_positive)}
          </div>
          <span className="text-[10px] text-red-400/80 block">
            {formatPercent(fpPct)} of test set
          </span>
        </div>

        {/* Row 2: Actual Bot */}
        <div className="font-semibold text-slate-300 pr-2 text-right">
          Actual Bot
        </div>
        {/* False Negative (FN) */}
        <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 text-center space-y-1 shadow-inner">
          <span className="text-[10px] uppercase font-sans font-bold text-amber-400 block tracking-wider">
            False Negative (FN)
          </span>
          <div className="text-xl font-bold text-amber-300">
            {formatNumber(data.false_negative)}
          </div>
          <span className="text-[10px] text-amber-400/80 block">
            {formatPercent(fnPct)} of test set
          </span>
        </div>

        {/* True Positive (TP) */}
        <div className="p-4 rounded-xl border border-cyan-500/40 bg-cyan-950/20 text-center space-y-1 shadow-inner">
          <span className="text-[10px] uppercase font-sans font-bold text-cyan-400 block tracking-wider">
            True Positive (TP)
          </span>
          <div className="text-xl font-bold text-cyan-300">
            {formatNumber(data.true_positive)}
          </div>
          <span className="text-[10px] text-cyan-400/80 block">
            {formatPercent(tpPct)} of test set
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 font-mono">
        <span>Total Test Samples: {formatNumber(total)}</span>
        <span>Accuracy Check: {formatPercent((data.true_negative + data.true_positive) / total)}</span>
      </div>
    </div>
  );
};
