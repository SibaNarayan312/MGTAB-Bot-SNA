import React from 'react';
import { ModelMetadata } from '../../types/model';
import { formatNumber } from '../../utils/formatters';
import { Cpu, Database, Calendar, Layers, GitBranch } from 'lucide-react';

interface ModelMetaCardProps {
  metadata: ModelMetadata;
}

export const ModelMetaCard: React.FC<ModelMetaCardProps> = ({ metadata }) => {
  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100">{metadata.model_name}</h3>
          </div>
          {metadata.architecture_type && (
            <p className="text-xs text-slate-400 mt-1">{metadata.architecture_type}</p>
          )}
        </div>
        {metadata.model_version && (
          <span className="px-2 py-0.5 rounded font-mono text-xs bg-slate-800 text-cyan-300 border border-slate-700">
            {metadata.model_version}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-2 border-t border-slate-800">
        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400 mb-1">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>Dataset</span>
          </div>
          <div className="font-semibold text-slate-200 truncate">{metadata.dataset_name}</div>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400 mb-1">
            <GitBranch className="w-3.5 h-3.5 text-purple-400" />
            <span>Split Protocol</span>
          </div>
          <div className="font-semibold text-slate-200">{metadata.validation_split || '80/20'}</div>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400 mb-1">
            <Layers className="w-3.5 h-3.5 text-emerald-400" />
            <span>GNN Layers</span>
          </div>
          <div className="font-mono font-bold text-slate-200">
            {metadata.graph_layers || '3 Layers (128-dim)'}
          </div>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 block mb-1">Train Samples</span>
          <span className="font-mono font-bold text-slate-200">
            {formatNumber(metadata.training_samples)}
          </span>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 block mb-1">Test Samples</span>
          <span className="font-mono font-bold text-slate-200">
            {formatNumber(metadata.test_samples)}
          </span>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400 mb-1">
            <Calendar className="w-3.5 h-3.5 text-amber-400" />
            <span>Evaluated On</span>
          </div>
          <span className="font-mono text-slate-200">{metadata.evaluation_date || 'Latest'}</span>
        </div>
      </div>
    </div>
  );
};
