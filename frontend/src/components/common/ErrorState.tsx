import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load analysis data',
  message = 'Unable to connect to the analysis server. Make sure the FastAPI backend is running and try again.',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`p-6 rounded-xl border border-red-900/40 bg-red-950/20 text-center flex flex-col items-center justify-center ${className}`}
    >
      <div className="p-3 rounded-full bg-red-500/10 text-red-400 mb-3 border border-red-500/30">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-semibold text-red-200 mb-1">{title}</h4>
      <p className="text-xs text-slate-300 max-w-md mb-4 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-all shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
