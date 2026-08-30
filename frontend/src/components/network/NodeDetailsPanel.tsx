import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GraphNodeData } from '../../types/network';
import { StatusBadge } from '../common/StatusBadge';
import { ProbabilityBar } from '../common/ProbabilityBar';
import { formatNumber, formatDecimal } from '../../utils/formatters';
import { User, X, ExternalLink, Activity, Network as NetIcon } from 'lucide-react';

interface NodeDetailsPanelProps {
  node: GraphNodeData | null;
  onClose: () => void;
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node, onClose }) => {
  const navigate = useNavigate();

  if (!node) return null;

  return (
    <div className="absolute top-4 right-4 z-20 w-80 max-h-[calc(100%-2rem)] overflow-y-auto p-4 rounded-xl bg-slate-900/95 border border-slate-800 backdrop-blur-md shadow-2xl space-y-4 animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-slate-800 text-cyan-400 border border-slate-700">
            <User className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-100 font-mono">
              {node.label || `User ${node.id}`}
            </h4>
            {node.screen_name && (
              <span className="text-[11px] text-slate-400 font-mono">
                @{node.screen_name}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
          aria-label="Close details"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Prediction Status & Probability */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
            Prediction
          </span>
          <StatusBadge type="prediction" value={node.prediction} />
        </div>

        {node.probability !== undefined && (
          <ProbabilityBar probability={node.probability} />
        )}
      </div>

      {/* SNA Topology Metrics */}
      <div className="space-y-2 pt-2 border-t border-slate-800">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
          <NetIcon className="w-3.5 h-3.5 text-cyan-400" />
          <span>Network Metrics</span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block">Degree</span>
            <span className="font-mono font-bold text-slate-200">
              {formatNumber(node.degree)}
            </span>
          </div>

          <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block">PageRank</span>
            <span className="font-mono font-bold text-cyan-400">
              {formatDecimal(node.pagerank, 5)}
            </span>
          </div>

          {node.community_id && (
            <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-400 block">Community</span>
              <span className="font-mono font-bold text-purple-400">
                #{node.community_id}
              </span>
            </div>
          )}

          {node.clustering !== undefined && (
            <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-400 block">Clustering</span>
              <span className="font-mono font-bold text-slate-200">
                {formatDecimal(node.clustering, 3)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Action to User Deep Dive */}
      <div className="pt-2">
        <button
          onClick={() => navigate(`/users/${node.id}`)}
          className="w-full py-2 px-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm"
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Full User Analysis</span>
          <ExternalLink className="w-3.5 h-3.5 ml-auto" />
        </button>
      </div>
    </div>
  );
};
