import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, RefreshCcw, Layers } from 'lucide-react';
import { GraphLayoutAlgorithm } from '../../types/network';

interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
  currentLayout: GraphLayoutAlgorithm;
  onLayoutChange: (layout: GraphLayoutAlgorithm) => void;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
  currentLayout,
  onLayoutChange,
}) => {
  return (
    <div className="flex items-center gap-1.5 p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 backdrop-blur-sm shadow-md">
      <button
        onClick={onZoomIn}
        className="p-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        title="Zoom In"
        aria-label="Zoom In"
      >
        <ZoomIn className="w-4 h-4" />
      </button>

      <button
        onClick={onZoomOut}
        className="p-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        title="Zoom Out"
        aria-label="Zoom Out"
      >
        <ZoomOut className="w-4 h-4" />
      </button>

      <button
        onClick={onFit}
        className="p-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        title="Fit to Screen"
        aria-label="Fit Graph"
      >
        <Maximize2 className="w-4 h-4" />
      </button>

      <button
        onClick={onReset}
        className="p-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        title="Re-run Layout"
        aria-label="Re-run Layout"
      >
        <RefreshCcw className="w-4 h-4" />
      </button>

      <div className="h-4 w-px bg-slate-800 mx-1" />

      {/* Layout Selector */}
      <div className="flex items-center gap-1 text-xs text-slate-400">
        <Layers className="w-3.5 h-3.5" />
        <select
          value={currentLayout}
          onChange={(e) => onLayoutChange(e.target.value as GraphLayoutAlgorithm)}
          className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-cyan-500 font-mono"
        >
          <option value="cose">Force Directed (COSE)</option>
          <option value="concentric">Concentric (PageRank)</option>
          <option value="circle">Circular</option>
          <option value="breadthfirst">Hierarchical (BFS)</option>
          <option value="grid">Grid Matrix</option>
        </select>
      </div>
    </div>
  );
};
