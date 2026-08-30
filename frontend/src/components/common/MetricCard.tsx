import React from 'react';
import { LucideIcon } from 'lucide-react';
import { LoadingSkeleton } from './LoadingSkeleton';

interface MetricCardProps {
  title: string;
  value?: string | number;
  subValue?: string;
  subText?: string;
  icon?: LucideIcon;
  variant?: 'default' | 'bot' | 'human' | 'warning' | 'cyan';
  loading?: boolean;
  tooltip?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subValue,
  subText,
  icon: Icon,
  variant = 'default',
  loading = false,
  tooltip,
}) => {
  if (loading) {
    return <LoadingSkeleton className="h-32 rounded-xl" />;
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'bot':
        return {
          card: 'border-red-900/40 bg-gradient-to-br from-red-950/20 to-slate-900/80',
          iconBg: 'bg-red-500/10 text-red-400 border border-red-500/20',
          valueColor: 'text-red-400',
        };
      case 'human':
        return {
          card: 'border-emerald-900/40 bg-gradient-to-br from-emerald-950/20 to-slate-900/80',
          iconBg: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
          valueColor: 'text-emerald-400',
        };
      case 'warning':
        return {
          card: 'border-amber-900/40 bg-gradient-to-br from-amber-950/20 to-slate-900/80',
          iconBg: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
          valueColor: 'text-amber-400',
        };
      case 'cyan':
        return {
          card: 'border-cyan-900/40 bg-gradient-to-br from-cyan-950/20 to-slate-900/80',
          iconBg: 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20',
          valueColor: 'text-cyan-400',
        };
      default:
        return {
          card: 'border-slate-800 bg-slate-900/80',
          iconBg: 'bg-slate-800 text-slate-300 border border-slate-700/50',
          valueColor: 'text-slate-100',
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div
      className={`relative p-5 rounded-xl border transition-all duration-200 hover:border-slate-700 shadow-lg ${styles.card}`}
      title={tooltip}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg ${styles.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className={`text-2xl font-bold tracking-tight font-mono ${styles.valueColor}`}>
          {value ?? '—'}
        </span>
        {subValue && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {subValue}
          </span>
        )}
      </div>

      {subText && (
        <p className="mt-2 text-xs text-slate-400 line-clamp-1">
          {subText}
        </p>
      )}
    </div>
  );
};
