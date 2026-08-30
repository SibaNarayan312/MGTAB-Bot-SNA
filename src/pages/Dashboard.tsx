import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { statisticsService } from '../services/statisticsService';
import { OverviewStatistics } from '../types/statistics';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { ChartCard } from '../components/common/ChartCard';
import { ErrorState } from '../components/common/ErrorState';
import { formatNumber, formatPercent, formatDecimal } from '../utils/formatters';
import {
  Users,
  Share2,
  Bot,
  UserCheck,
  UsersRound,
  ShieldAlert,
  Activity,
  Network as NetIcon,
  ArrowUpRight,
  Info,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<OverviewStatistics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await statisticsService.getOverviewStatistics();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch network overview statistics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (error) {
    return <ErrorState message={error} onRetry={fetchStats} />;
  }

  // Distribution chart data
  const botHumanData = stats
    ? [
        { name: 'Human Accounts', value: stats.human_count, color: '#10B981' },
        { name: 'Bot Accounts', value: stats.bot_count, color: '#EF4444' },
      ]
    : [];

  const relationshipData = stats?.relationship_breakdown || [];
  const communityDistData = stats?.community_size_distribution || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Network Intelligence Overview"
        subtitle="Global social network metrics, community structures, and bot distribution in MGTAB benchmark"
        actions={
          <button
            onClick={() => navigate('/network')}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition-all"
          >
            <NetIcon className="w-3.5 h-3.5" />
            <span>Launch Network Visualizer</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        }
      />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          title="Total Users"
          value={formatNumber(stats?.total_users)}
          subText="MGTAB Benchmark"
          icon={Users}
          loading={loading}
          variant="cyan"
        />
        <MetricCard
          title="Total Relationships"
          value={formatNumber(stats?.total_relationships)}
          subText="Multi-relational edges"
          icon={Share2}
          loading={loading}
        />
        <MetricCard
          title="Bot Accounts"
          value={formatNumber(stats?.bot_count)}
          subValue={formatPercent(stats?.bot_ratio)}
          icon={Bot}
          loading={loading}
          variant="bot"
        />
        <MetricCard
          title="Human Accounts"
          value={formatNumber(stats?.human_count)}
          subValue={stats ? formatPercent(1 - stats.bot_ratio) : undefined}
          icon={UserCheck}
          loading={loading}
          variant="human"
        />
        <MetricCard
          title="Communities"
          value={formatNumber(stats?.community_count)}
          subText="Louvain Partitioning"
          icon={UsersRound}
          loading={loading}
        />
        <MetricCard
          title="Flagged Groups"
          value={formatNumber(stats?.flagged_groups_count)}
          subText="High Coordination Score"
          icon={ShieldAlert}
          loading={loading}
          variant="warning"
        />
      </div>

      {/* Primary Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot vs Human Donut Chart */}
        <ChartCard
          title="Account Classification Distribution"
          subtitle="Proportion of predicted bots vs verified organic humans"
          loading={loading}
        >
          <div className="w-full h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={botHumanData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {botHumanData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: unknown) => {
                    const num = typeof val === 'number' ? val : 0;
                    return [
                      `${formatNumber(num)} (${formatPercent(stats ? num / stats.total_users : 0)})`,
                      'Accounts',
                    ];
                  }}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Multi-Relational Edge Breakdown */}
        <ChartCard
          title="Multi-Relational Interactions"
          subtitle="Edge frequencies across relation types in MGTAB"
          loading={loading}
        >
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={relationshipData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="type" stroke="#64748b" fontSize={10} angle={-20} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => formatNumber(v)} />
                <Tooltip
                  formatter={(val: unknown) => [
                    formatNumber(typeof val === 'number' ? val : 0),
                    'Count',
                  ]}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Community Size Distribution */}
        <ChartCard
          title="Community Scale Distribution"
          subtitle="Grouping of modular communities by user size"
          loading={loading}
        >
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={communityDistData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="size_range" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip
                  formatter={(val: unknown) => [
                    formatNumber(typeof val === 'number' ? val : 0),
                    'Communities',
                  ]}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="community_count" fill="#818cf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Network SNA Topo Metrics Grid */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              Global Social Network Topo Metrics
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Computed by Network Analysis Module
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Density</span>
            <span className="font-mono font-bold text-cyan-400 text-sm">
              {formatDecimal(stats?.network?.density, 5)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Avg Degree</span>
            <span className="font-mono font-bold text-slate-200 text-sm">
              {formatDecimal(stats?.network?.average_degree, 2)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Clustering Coeff</span>
            <span className="font-mono font-bold text-slate-200 text-sm">
              {formatDecimal(stats?.network?.average_clustering, 3)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Modularity</span>
            <span className="font-mono font-bold text-purple-400 text-sm">
              {formatDecimal(stats?.network?.modularity, 3)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Components</span>
            <span className="font-mono font-bold text-slate-200 text-sm">
              {formatNumber(stats?.network?.connected_components)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Diameter</span>
            <span className="font-mono font-bold text-slate-200 text-sm">
              {formatNumber(stats?.network?.diameter)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">Transitivity</span>
            <span className="font-mono font-bold text-slate-200 text-sm">
              {formatDecimal(stats?.network?.transitivity, 3)}
            </span>
          </div>
        </div>
      </div>

      {/* System Insights Area (Section 11 requirement) */}
      <div className="p-5 rounded-xl border border-cyan-900/30 bg-gradient-to-r from-cyan-950/15 via-slate-900/90 to-slate-950 shadow-lg space-y-3">
        <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
          <Info className="w-4 h-4" />
          <span>Research Synthesis &amp; Automated Network Insights</span>
        </div>

        {stats?.system_insights && stats.system_insights.length > 0 ? (
          <div className="space-y-2">
            {stats.system_insights.map((insight: string, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed font-sans"
              >
                &bull; {insight}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400">No additional insights available.</p>
        )}
      </div>
    </div>
  );
};
