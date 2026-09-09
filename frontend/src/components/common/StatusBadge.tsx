import React from 'react';
import { getPredictionBadgeConfig, getCommunityRiskConfig } from '../../utils/formatters';

interface StatusBadgeProps {
  type: 'prediction' | 'risk';
  value?: string ;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  type,
  value,
  className = '',
}) => {
  if (type === 'prediction') {
    const config = getPredictionBadgeConfig(value);
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider ${config.badgeClass} ${className}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${config.dotClass}`} />
        {config.label}
      </span>
    );
  }

  const config = getCommunityRiskConfig(value);
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold ${config.badgeClass} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotClass}`} />
      {config.label}
    </span>
  );
};
