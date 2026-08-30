import React from 'react';
import { LoadingSkeleton } from './LoadingSkeleton';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  loading?: boolean;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  badge,
  actions,
  children,
  loading = false,
  className = '',
}) => {
  return (
    <div className={`p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg flex flex-col ${className}`}>
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-100 uppercase tracking-wide">
              {title}
            </h3>
            {badge}
          </div>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      <div className="flex-1 w-full relative min-h-[220px]">
        {loading ? (
          <div className="w-full h-full min-h-[220px] flex items-center justify-center">
            <LoadingSkeleton className="w-full h-full min-h-[200px]" />
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};
