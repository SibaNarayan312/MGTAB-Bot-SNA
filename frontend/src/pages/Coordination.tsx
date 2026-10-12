import React, { useEffect, useState } from 'react';
import { coordinationService } from '../services/coordinationService';
import { CoordinationSummaryResponse } from '../types/coordination';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';
import { CoordinatedGroupCard } from '../components/coordination/CoordinatedGroupCard';
import { ChartCard } from '../components/common/ChartCard';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyState } from '../components/common/EmptyState';
import { formatNumber, formatDecimal } from '../utils/formatters';
import { ShieldAlert, Activity, Sparkles } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const Coordination: React.FC = () => {
  const [data, setData] = useState<CoordinationSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCoordination = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await coordinationService.getCoordinationAnalysis();
      setData(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch coordination analysis.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCoordination();
  }, []);

  const signalChartData = data?.top_coordination_signals || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Coordinated Behavioral Analysis"
        subtitle="Detection of synchronized multi-account behaviors, topological amplification clusters, and shared entities"
      />

      {/* Mandatory Academic Disclaimer Banner */}
      <DisclaimerBanner />

      {error && <ErrorState message={error} onRetry={fetchCoordination} />}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Flagged Coordinated Clusters"
          value={formatNumber(data?.total_flagged_groups)}
          subText="Community Subgraphs"
          icon={ShieldAlert}
          loading={loading}
          variant="warning"
        />
        <MetricCard
          title="Avg Coordination Score"
          value={formatDecimal(data?.average_coordination_score, 3)}
          subText="Score range [0.0 - 1.0]"
          icon={Activity}
          loading={loading}
          variant="cyan"
        />
        <MetricCard
          title="Active Signal Types"
          value={formatNumber(data?.top_coordination_signals?.length)}
          subText="Temporal &amp; Topological"
          icon={Sparkles}
          loading={loading}
        />
      </div>

      {/* Coordination Signal Frequency Chart */}
      <ChartCard
        title="Observed Coordination Signals Frequency"
        subtitle="Distribution of multi-relational behavioral flags detected across flagged clusters"
        loading={loading}
      >
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={signalChartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" fontSize={10} />
              <YAxis
                type="category"
                dataKey="signal"
                stroke="#64748b"
                fontSize={10}
                width={180}
                tickFormatter={(val: string) => (val.length > 28 ? `${val.slice(0, 28)}...` : val)}
              />
              <Tooltip
                formatter={(val: unknown) => [
                  typeof val === 'number' ? val : 0,
                  'Flagged Clusters',
                ]}
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="frequency" fill="#f59e0b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Flagged Coordinated Groups List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              Identified Potentially Coordinated Groups
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Ranked by coordination score based on topological structure and shared interaction density
            </p>
          </div>
        </div>

        {loading && (
          <div className="space-y-4">
            <LoadingSkeleton className="h-48 w-full rounded-xl" count={3} />
          </div>
        )}

        {!loading && (!data?.groups || data.groups.length === 0) && (
          <EmptyState
            title="No Coordinated Groups Detected"
            description="The current graph partition does not exhibit behavioral or topological coordination anomalies."
          />
        )}

        {!loading && data?.groups && (
          <div className="space-y-4">
            {data.groups.map((group) => (
              <CoordinatedGroupCard key={group.group_id} group={group} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
