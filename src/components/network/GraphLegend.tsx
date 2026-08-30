import React from 'react';
import { RELATIONSHIP_COLORS } from '../../utils/cytoscapeConfig';

export const GraphLegend: React.FC = () => {
  return (
    <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/90 backdrop-blur-sm text-xs space-y-2.5 shadow-lg">
      <div>
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
          Node Classifications
        </span>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 border border-red-300" />
            <span className="text-slate-300 text-[11px]">Bot Account</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 border border-emerald-300" />
            <span className="text-slate-300 text-[11px]">Human Account</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full border-2 border-amber-400 bg-transparent shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
            <span className="text-slate-300 text-[11px]">Seed / Center</span>
          </div>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
          Multi-Relational Edges (MGTAB)
        </span>
        <div className="grid grid-cols-2 gap-x-3 gap-y-1">
          {Object.entries(RELATIONSHIP_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-slate-300 text-[10px] font-mono">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
