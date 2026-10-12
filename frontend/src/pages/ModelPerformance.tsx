import React, { useEffect, useState } from 'react';
import { modelService } from '../services/modelService';
import { ModelPerformanceResponse } from '../types/model';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { ChartCard } from '../components/common/ChartCard';
import { ConfusionMatrix } from '../components/model/ConfusionMatrix';
import { ROCCurveChart } from '../components/model/ROCCurveChart';
import { ModelMetaCard } from '../components/model/ModelMetaCard';
import { ErrorState } from '../components/common/ErrorState';
import { formatPercent, formatDecimal } from '../utils/formatters';
import {
  Cpu,
  Target,
  Award,
  Zap,
  Activity,
  GitCompare,
  Sparkles,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const ModelPerformance: React.FC = () => {
  const [data, setData] = useState<ModelPerformanceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformance = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await modelService.getModelPerformance();
      setData(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch model evaluation metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformance();
  }, []);

  const featureData = data?.feature_importances || [];
  const baselineData = data?.baseline_comparisons || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Model Performance &amp; Evaluation Benchmark"
        subtitle="Graph Neural Network (RGCN) classification metrics, confusion matrix, ROC-AUC curve, and baseline comparisons"
      />

      {error && <ErrorState message={error} onRetry={fetchPerformance} />}

      {/* Primary ML Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Accuracy"
          value={formatPercent(data?.metrics?.accuracy, 1)}
          subText="Test Set (1,020 samples)"
          icon={Award}
          loading={loading}
          variant="cyan"
        />
        <MetricCard
          title="Precision"
          value={formatPercent(data?.metrics?.precision, 1)}
          subText="Positive Predictive Value"
          icon={Target}
          loading={loading}
        />
        <MetricCard
          title="Recall / Sensitivity"
          value={formatPercent(data?.metrics?.recall, 1)}
          subText="True Positive Rate"
          icon={Zap}
          loading={loading}
        />
        <MetricCard
          title="F1-Score"
          value={formatPercent(data?.metrics?.f1_score, 1)}
          subText="Harmonic Mean"
          icon={Cpu}
          loading={loading}
          variant="human"
        />
        <MetricCard
          title="ROC-AUC"
          value={formatDecimal(data?.metrics?.roc_auc, 3)}
          subText="Area Under Curve"
          icon={Activity}
          loading={loading}
          variant="warning"
        />
      </div>

      {/* Model Metadata Card */}
      {data?.metadata && <ModelMetaCard metadata={data.metadata} />}

      {/* 2-Column: Confusion Matrix & ROC Curve */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Card */}
        <ChartCard
          title="Evaluation Confusion Matrix"
          subtitle="Stratified 20% holdout test distribution (Actual vs Predicted)"
          loading={loading}
        >
          {data?.confusion_matrix ? (
            <ConfusionMatrix data={data.confusion_matrix} />
          ) : (
            <div className="h-64 flex items-center justify-center text-xs text-slate-400">
              Confusion matrix data not available.
            </div>
          )}
        </ChartCard>

        {/* ROC-AUC Curve Chart */}
        <ChartCard
          title="Receiver Operating Characteristic (ROC)"
          subtitle="True Positive Rate vs False Positive Rate curve"
          loading={loading}
        >
          <ROCCurveChart rocCurve={data?.roc_curve} rocAuc={data?.metrics?.roc_auc} />
        </ChartCard>
      </div>

      {/* GNN Global Feature Importance & Baselines Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Importance */}
        <ChartCard
          title="Global GNN Feature Importances"
          subtitle="Top predictive relational and topological features"
          loading={loading}
        >
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={featureData}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 30, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={10} tickFormatter={(v) => formatPercent(v, 0)} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  stroke="#64748b"
                  fontSize={10}
                  width={170}
                  tickFormatter={(val: string) => (val.length > 26 ? `${val.slice(0, 26)}...` : val)}
                />
                <Tooltip
                  formatter={(val: unknown) => [
                    formatPercent(typeof val === 'number' ? val : 0),
                    'Importance',
                  ]}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Baseline Model Comparison Table */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <GitCompare className="w-4 h-4 text-cyan-400" />
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
                  Model Architecture Comparison
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Benchmark performance against traditional tabular and homogeneous baselines
                </p>
              </div>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Architecture</th>
                    <th className="py-2.5 px-3 text-right">Accuracy</th>
                    <th className="py-2.5 px-3 text-right">F1-Score</th>
                    <th className="py-2.5 px-3 text-right">ROC-AUC</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {baselineData.map((b, idx) => {
                    const isProposed = b.model_name.includes('Proposed');
                    return (
                      <tr
                        key={idx}
                        className={`transition-colors ${
                          isProposed ? 'bg-cyan-950/30 text-cyan-200 font-semibold' : 'hover:bg-slate-800/30'
                        }`}
                      >
                        <td className="py-3 px-3 flex items-center gap-1.5 font-sans">
                          {isProposed && <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                          <span>{b.model_name}</span>
                        </td>
                        <td className="py-3 px-3 text-right font-mono">{formatPercent(b.accuracy)}</td>
                        <td className="py-3 px-3 text-right font-mono">{formatPercent(b.f1_score)}</td>
                        <td className="py-3 px-3 text-right font-mono">{formatDecimal(b.roc_auc, 3)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-slate-400">
            <span className="text-cyan-400 font-semibold">Key Finding: </span>
            HistGradientBoosting (tabular, 806 features) achieves best F1 (88.63%), while the 2-layer RGCN leveraging graph structure directly achieves 0.9415 ROC-AUC on 788 node features across 7 relation types.
          </div>
        </div>
      </div>
    </div>
  );
};
