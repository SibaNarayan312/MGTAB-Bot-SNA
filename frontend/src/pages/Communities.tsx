import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { communityService } from '../services/communityService';
import { CommunitiesResponse, CommunitySummary, CommunityDetails } from '../types/community';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { DataTable, Column } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { ErrorState } from '../components/common/ErrorState';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { formatNumber, formatPercent, formatDecimal } from '../utils/formatters';
import {
  UsersRound,
  ShieldAlert,
  Layers,
  X,
  ExternalLink,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

export const Communities: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  const [data, setData] = useState<CommunitiesResponse | null>(null);
  const [selectedCommunity, setSelectedCommunity] = useState<CommunityDetails | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCommunities = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await communityService.getCommunities();
      setData(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch community analysis.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDetails = async (commId: string | number) => {
    setLoadingDetails(true);
    try {
      const details = await communityService.getCommunityDetails(commId);
      setSelectedCommunity(details);
    } catch (err) {
      console.error('Failed to load community details', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  useEffect(() => {
    fetchCommunities();
  }, []);

  useEffect(() => {
    if (id) {
      fetchDetails(id);
    } else {
      setSelectedCommunity(null);
    }
  }, [id]);

  const handleSelectCommunity = (summary: CommunitySummary) => {
    navigate(`/communities/${summary.id}`);
  };

  const handleCloseDetails = () => {
    navigate('/communities');
    setSelectedCommunity(null);
  };

  // Table Columns Definition
  const columns: Column<CommunitySummary & Record<string, unknown>>[] = [
    {
      key: 'id',
      header: 'Community ID',
      sortable: true,
      render: (item) => (
        <span className="font-mono font-bold text-cyan-400">#{item.id}</span>
      ),
    },
    {
      key: 'member_count',
      header: 'Total Members',
      sortable: true,
      align: 'right',
      render: (item) => (
        <span className="font-mono font-bold text-slate-200">
          {formatNumber(item.member_count)}
        </span>
      ),
    },
    {
      key: 'bot_count',
      header: 'Bot Accounts',
      sortable: true,
      align: 'right',
      render: (item) => (
        <span className="font-mono font-bold text-red-400">
          {formatNumber(item.bot_count)}
        </span>
      ),
    },
    {
      key: 'bot_ratio',
      header: 'Bot %',
      sortable: true,
      align: 'right',
      render: (item) => (
        <span className="font-mono text-slate-300">
          {formatPercent(item.bot_ratio)}
        </span>
      ),
    },
    {
      key: 'coordination_score',
      header: 'Coordination Score',
      sortable: true,
      align: 'right',
      render: (item) => (
        <span
          className={`font-mono font-bold ${
            (item.coordination_score || 0) >= 0.75
              ? 'text-amber-400'
              : 'text-slate-400'
          }`}
        >
          {formatDecimal(item.coordination_score, 3)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Topological Risk Status',
      sortable: true,
      render: (item) => (
        <StatusBadge type="risk" value={item.status} />
      ),
    },
    {
      key: 'actions',
      header: 'Action',
      align: 'center',
      render: (item) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleSelectCommunity(item);
          }}
          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors inline-flex items-center gap-1"
        >
          <span>Inspect</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Community Analysis &amp; Topological Modularity"
        subtitle="Detection of modular graph partitions, density analysis, and bot concentration clusters"
      />

      {error && <ErrorState message={error} onRetry={fetchCommunities} />}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          title="Total Communities"
          value={formatNumber(data?.total_communities)}
          subText="Graph Partitions"
          icon={UsersRound}
          loading={loading}
          variant="cyan"
        />
        <MetricCard
          title="Largest Community"
          value={formatNumber(data?.overall_stats?.largest_community_size)}
          subText="Node Count"
          icon={Layers}
          loading={loading}
        />
        <MetricCard
          title="Avg Community Size"
          value={formatDecimal(data?.overall_stats?.average_community_size, 1)}
          subText="Members per cluster"
          icon={TrendingUp}
          loading={loading}
        />
        <MetricCard
          title="Suspicious / Flagged"
          value={formatNumber(data?.overall_stats?.flagged_communities_count)}
          subText="Coordination Score > 0.75"
          icon={ShieldAlert}
          loading={loading}
          variant="warning"
        />
      </div>

      {/* Community Main Table */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              Detected Graph Communities
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Click on any community row to inspect internal topology, signals, and active members
            </p>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={(data?.communities || []) as (CommunitySummary & Record<string, unknown>)[]}
          keyExtractor={(item) => item.id}
          loading={loading}
          onRowClick={handleSelectCommunity}
          pageSize={10}
        />
      </div>

      {/* Selected Community Detail Drawer / Inspector */}
      {selectedCommunity && (
        <div className="p-6 rounded-xl border border-cyan-800/60 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 shadow-2xl space-y-6 animate-in fade-in duration-300">
          {/* Header */}
          <div className="flex items-start justify-between pb-4 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-3">
                <span className="p-2 rounded-lg bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                  <UsersRound className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-lg font-bold text-slate-100 font-mono">
                    Community #{selectedCommunity.id} Deep Dive
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <StatusBadge type="risk" value={selectedCommunity.status} />
                    {selectedCommunity.primary_topics && (
                      <span className="text-xs text-slate-400">
                        &bull; {selectedCommunity.primary_topics.join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={handleCloseDetails}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700 transition-colors"
              aria-label="Close details"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {loadingDetails ? (
            <LoadingSkeleton className="h-64 w-full" />
          ) : (
            <div className="space-y-6">
              {/* Core Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Members</span>
                  <span className="font-mono font-bold text-slate-200 text-sm">
                    {formatNumber(selectedCommunity.member_count)}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Bot Accounts</span>
                  <span className="font-mono font-bold text-red-400 text-sm">
                    {formatNumber(selectedCommunity.bot_count)}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Bot Ratio</span>
                  <span className="font-mono font-bold text-red-400 text-sm">
                    {formatPercent(selectedCommunity.bot_ratio)}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Coordination Score</span>
                  <span className="font-mono font-bold text-amber-400 text-sm">
                    {formatDecimal(selectedCommunity.coordination_score, 3)}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Internal Density</span>
                  <span className="font-mono font-bold text-cyan-400 text-sm">
                    {formatDecimal(selectedCommunity.density, 3)}
                  </span>
                </div>
              </div>

              {/* Network Partition Statistics */}
              {selectedCommunity.network_statistics && (
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                    Partition Topology Statistics
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div>
                      <span className="text-slate-400 text-[11px] block">Internal Edges</span>
                      <span className="font-mono font-bold text-slate-200">
                        {formatNumber(selectedCommunity.network_statistics.internal_edges)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[11px] block">External Edges</span>
                      <span className="font-mono font-bold text-slate-200">
                        {formatNumber(selectedCommunity.network_statistics.external_edges)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[11px] block">Conductance</span>
                      <span className="font-mono font-bold text-cyan-400">
                        {formatDecimal(selectedCommunity.network_statistics.conductance, 3)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[11px] block">Clustering Coefficient</span>
                      <span className="font-mono font-bold text-slate-200">
                        {formatDecimal(selectedCommunity.network_statistics.clustering_coefficient, 3)}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Observed Signals */}
              {selectedCommunity.signals && selectedCommunity.signals.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                    Coordination Indicators &amp; Signals
                  </span>
                  <div className="space-y-2">
                    {selectedCommunity.signals.map((sig, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-xs flex items-start justify-between gap-3"
                      >
                        <div>
                          <span className="font-bold text-amber-300">{sig.signal}</span>
                          {sig.description && (
                            <p className="text-slate-400 text-[11px] mt-0.5">{sig.description}</p>
                          )}
                        </div>
                        {sig.score !== undefined && (
                          <span className="font-mono font-bold text-amber-400 shrink-0">
                            {formatDecimal(sig.score, 2)}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sample Members */}
              {selectedCommunity.members && selectedCommunity.members.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                    Top Active Community Members
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                    {selectedCommunity.members.map((member) => (
                      <div
                        key={member.user_id}
                        onClick={() => navigate(`/users/${member.user_id}`)}
                        className="p-3 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 cursor-pointer transition-all flex items-center justify-between text-xs group"
                      >
                        <div className="space-y-0.5">
                          <span className="font-mono font-semibold text-slate-200 group-hover:text-cyan-300">
                            @{member.screen_name || member.user_id}
                          </span>
                          <div className="flex items-center gap-1.5">
                            <StatusBadge type="prediction" value={member.prediction} />
                          </div>
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
