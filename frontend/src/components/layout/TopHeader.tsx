import React from 'react';
import { useLocation } from 'react-router-dom';
import { BackendStatusBadge } from './BackendStatusBadge';
import { Menu, Shield } from 'lucide-react';

interface TopHeaderProps {
  onToggleSidebar: () => void;
}

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': {
    title: 'Network Intelligence Overview',
    subtitle: 'High-level telemetry, community structures, and bot distribution in MGTAB',
  },
  '/users': {
    title: 'User & Node Investigation',
    subtitle: 'Deep GNN explainability, centrality metrics, and neighborhood subgraph preview',
  },
  '/network': {
    title: 'Multi-Relational Network Visualizer',
    subtitle: 'Interactive Cytoscape.js canvas with multi-edge relation types and community filtering',
  },
  '/communities': {
    title: 'Community Topology & Modularity',
    subtitle: 'Louvain/Leiden detected clusters, bot concentration, and conductance indices',
  },
  '/coordination': {
    title: 'Coordinated Behavioral Analysis',
    subtitle: 'Temporal synchronicity, shared entities, and suspicious subgraph formations',
  },
  '/model-performance': {
    title: 'Model Evaluation & GNN Benchmark',
    subtitle: 'Multi-relational RGCN validation metrics, confusion matrix, and ROC-AUC comparisons',
  },
};

export const TopHeader: React.FC<TopHeaderProps> = ({ onToggleSidebar }) => {
  const location = useLocation();
  const currentPath = Object.keys(pageTitles).find((path) =>
    location.pathname.startsWith(path)
  ) || '/dashboard';

  const pageInfo = pageTitles[currentPath] || {
    title: 'Research Dashboard',
    subtitle: 'SNA Detection of Coordinated Bot-Like Behaviour',
  };

  return (
    <header className="sticky top-0 z-20 h-16 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 px-4 md:px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800 lg:hidden"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-slate-200 tracking-tight">
                {pageInfo.title}
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700/50">
                MGTAB v1.0
              </span>
            </div>
            <p className="hidden md:block text-[11px] text-slate-400 truncate max-w-xl">
              {pageInfo.subtitle}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <BackendStatusBadge />
      </div>
    </header>
  );
};
