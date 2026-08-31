import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface DisclaimerBannerProps {
  className?: string;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({ className = '' }) => {
  return (
    <div
      className={`p-3 rounded-lg border border-amber-900/30 bg-amber-950/15 flex items-start gap-2.5 text-xs text-amber-200/80 ${className}`}
    >
      <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      <div className="leading-relaxed">
        <strong className="font-semibold text-amber-300">Research Disclaimer: </strong>
        Detection results indicate potentially coordinated behavioural patterns and topological anomalies. 
        These metrics are exploratory research indicators and should not be interpreted as definitive proof of malicious intent or verified disinformation campaigns.
      </div>
    </div>
  );
};
