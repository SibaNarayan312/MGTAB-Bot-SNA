import React, { useEffect, useState } from 'react';
import { checkBackendHealth } from '../../services/api';
import { BackendStatus } from '../../types/api';
import { Server, RefreshCw } from 'lucide-react';

export const BackendStatusBadge: React.FC = () => {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const fetchStatus = async () => {
    setChecking(true);
    try {
      const res = await checkBackendHealth();
      setStatus(res);
    } catch {
      setStatus({
        connected: false,
        isMock: true,
        baseUrl: 'http://localhost:8000',
        version: 'Offline',
      });
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border transition-all ${
          status?.isMock
            ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
            : status?.connected
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            : 'bg-red-500/10 text-red-400 border-red-500/30'
        }`}
        title={`API Endpoint: ${status?.baseUrl || '—'}`}
      >
        <span
          className={`w-2 h-2 rounded-full ${
            status?.isMock
              ? 'bg-amber-400 animate-pulse'
              : status?.connected
              ? 'bg-emerald-400'
              : 'bg-red-500'
          }`}
        />
        <Server className="w-3 h-3" />
        <span className="hidden sm:inline font-sans font-medium text-[11px]">
          {status?.isMock
            ? 'Mock Adapter (MGTAB)'
            : status?.connected
            ? `FastAPI Live (${status.latencyMs}ms)`
            : 'API Disconnected'}
        </span>
      </div>

      <button
        onClick={fetchStatus}
        disabled={checking}
        className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all border border-transparent hover:border-slate-700"
        title="Check Backend Connection"
        aria-label="Refresh Backend Connection"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin text-cyan-400' : ''}`} />
      </button>
    </div>
  );
};
