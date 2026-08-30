import React from 'react';
import { GraphEdgeData } from '../../types/network';
import { RELATIONSHIP_COLORS } from '../../utils/cytoscapeConfig';
import { formatNumber } from '../../utils/formatters';
import { Share2, X, ArrowRight } from 'lucide-react';

interface EdgeDetailsPanelProps {
  edge: GraphEdgeData | null;
  onClose: () => void;
}

export const EdgeDetailsPanel: React.FC<EdgeDetailsPanelProps> = ({ edge, onClose }) => {
  if (!edge) return null;

  const edgeColor = RELATIONSHIP_COLORS[edge.relationship] || '#64748B';

  return (
    <div className="absolute top-4 right-4 z-20 w-80 p-4 rounded-xl bg-slate-900/95 border border-slate-800 backdrop-blur-md shadow-2xl space-y-3 animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
            <Share2 className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wide">
              Edge Relationship
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">
              MGTAB Interaction
            </span>
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

      {/* Relationship Type Tag */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400">Interaction Type:</span>
        <span
          className="px-2.5 py-0.5 rounded text-xs font-mono font-bold text-white shadow-sm"
          style={{ backgroundColor: edgeColor }}
        >
          {edge.relationship}
        </span>
      </div>

      {/* Source to Target direction */}
      <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-2">
        <div className="flex items-center justify-between text-slate-400">
          <span>Source (Sender)</span>
          <span>Target (Receiver)</span>
        </div>
        <div className="flex items-center justify-between font-mono font-bold text-slate-200">
          <span className="truncate max-w-[100px]">{edge.source}</span>
          <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0 mx-2" />
          <span className="truncate max-w-[100px]">{edge.target}</span>
        </div>
      </div>

      {/* Edge Weight / Frequency */}
      {edge.weight !== undefined && (
        <div className="flex items-center justify-between text-xs pt-1">
          <span className="text-slate-400">Interaction Weight:</span>
          <span className="font-mono font-bold text-slate-200">
            {formatNumber(edge.weight)}
          </span>
        </div>
      )}
    </div>
  );
};
