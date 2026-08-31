import React from 'react';
import { UserNetworkMetrics } from '../../types/user';
import { formatNumber, formatDecimal } from '../../utils/formatters';
import { Network, Activity, GitCommit, Share2, Compass, Layers } from 'lucide-react';

interface UserMetricsGridProps {
  metrics?: UserNetworkMetrics;
}

export const UserMetricsGrid: React.FC<UserMetricsGridProps> = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 text-xs text-slate-400">
        No network metrics available for this account.
      </div>
    );
  }

  const items = [
    {
      label: 'Degree (Total)',
      value: formatNumber(metrics.degree),
      icon: Network,
      color: 'text-cyan-400',
    },
    {
      label: 'In-Degree',
      value: formatNumber(metrics.in_degree),
      icon: GitCommit,
      color: 'text-emerald-400',
    },
    {
      label: 'Out-Degree',
      value: formatNumber(metrics.out_degree),
      icon: Share2,
      color: 'text-amber-400',
    },
    {
      label: 'PageRank Score',
      value: formatDecimal(metrics.pagerank, 5),
      icon: Activity,
      color: 'text-purple-400',
    },
    {
      label: 'Betweenness Centrality',
      value: formatDecimal(metrics.betweenness, 4),
      icon: Compass,
      color: 'text-blue-400',
    },
    {
      label: 'Clustering Coefficient',
      value: formatDecimal(metrics.clustering, 4),
      icon: Layers,
      color: 'text-rose-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div
            key={item.label}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/70 space-y-1 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-[11px] font-medium">{item.label}</span>
              <Icon className={`w-3.5 h-3.5 ${item.color}`} />
            </div>
            <div className={`text-base font-bold font-mono ${item.color}`}>
              {item.value}
            </div>
          </div>
        );
      })}
    </div>
  );
};
