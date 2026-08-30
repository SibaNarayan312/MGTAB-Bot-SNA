import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { userService } from '../services/userService';
import { UserProfile } from '../types/user';
import { NetworkGraphData } from '../types/network';
import { PageHeader } from '../components/common/PageHeader';
import { SearchBar } from '../components/common/SearchBar';
import { StatusBadge } from '../components/common/StatusBadge';
import { ProbabilityBar } from '../components/common/ProbabilityBar';
import { UserMetricsGrid } from '../components/users/UserMetricsGrid';
import { FeatureImportanceChart } from '../components/users/FeatureImportanceChart';
import { UserRelationshipList } from '../components/users/UserRelationshipList';
import { NetworkGraph } from '../components/network/NetworkGraph';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { formatNumber, formatDate } from '../utils/formatters';
import {
  User,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Network as NetIcon,
  ExternalLink,
  Sparkles,
  Search,
} from 'lucide-react';

export const UserAnalysis: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  const [selectedUserId, setSelectedUserId] = useState<string>(id || '123456789');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [userGraph, setUserGraph] = useState<NetworkGraphData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUserData = async (userId: string) => {
    setLoading(true);
    setError(null);
    try {
      const [userRes, graphRes] = await Promise.all([
        userService.getUser(userId),
        userService.getUserNetwork(userId),
      ]);
      setProfile(userRes);
      setUserGraph(graphRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to load data for user #${userId}.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      setSelectedUserId(id);
      fetchUserData(id);
    } else {
      fetchUserData(selectedUserId);
    }
  }, [id]);

  const handleSearch = (newId: string) => {
    setSelectedUserId(newId);
    navigate(`/users/${newId}`);
  };

  const sampleUsers = [
    { id: '123456789', label: 'Tech Trend Echo (Bot)', type: 'BOT' },
    { id: '987654321', label: 'Dr. Sarah Mitchell (Human)', type: 'HUMAN' },
    { id: '555123999', label: 'News Radar Bot (Bot)', type: 'BOT' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="User &amp; Node Investigation"
        subtitle="Individual GNN prediction probability, SNA centrality metrics, and local relational ego-graph"
      />

      {/* Prominent Search Bar Section */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex-1 max-w-xl">
            <SearchBar
              placeholder="Enter User ID (e.g., 123456789)..."
              initialValue={selectedUserId}
              onSearch={handleSearch}
              loading={loading}
            />
          </div>

          {/* Quick Select Buttons */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
            <span className="text-slate-400 text-[11px] shrink-0">Sample Nodes:</span>
            {sampleUsers.map((u) => (
              <button
                key={u.id}
                onClick={() => handleSearch(u.id)}
                className={`px-2.5 py-1 rounded-md text-xs font-mono transition-all border ${
                  selectedUserId === u.id
                    ? 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border-slate-700/50'
                }`}
              >
                {u.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && <ErrorState message={error} onRetry={() => fetchUserData(selectedUserId)} />}

      {loading && (
        <div className="space-y-4">
          <LoadingSkeleton className="h-44 w-full rounded-xl" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LoadingSkeleton className="h-80 w-full rounded-xl" />
            <LoadingSkeleton className="h-80 w-full rounded-xl" />
          </div>
        </div>
      )}

      {!loading && !profile && !error && (
        <EmptyState
          icon={Search}
          title="No User Selected"
          description="Enter an account User ID above to inspect GNN classifications and ego-network graphs."
        />
      )}

      {!loading && profile && (
        <div className="space-y-6">
          {/* Identity & Prediction Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/90 shadow-xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div className="flex items-start gap-4">
                <div className="p-3.5 rounded-xl bg-slate-800 text-cyan-400 border border-slate-700 shrink-0">
                  <User className="w-7 h-7" />
                </div>
                <div>
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-lg font-bold text-slate-100 font-mono">
                      {profile.name || `User #${profile.user_id}`}
                    </h2>
                    {profile.features?.verified && (
                      <span className="text-cyan-400" title="Verified Account">
                        <ShieldCheck className="w-4 h-4" />
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-slate-400 font-mono">
                    <span>ID: {profile.user_id}</span>
                    {profile.screen_name && <span>&bull; @{profile.screen_name}</span>}
                    {profile.community_id && (
                      <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30">
                        Community #{profile.community_id}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Prediction Badge & Confidence */}
              <div className="flex flex-col sm:items-end gap-2 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                    Model Prediction:
                  </span>
                  <StatusBadge type="prediction" value={profile.prediction} />
                </div>
                {profile.probability !== undefined && (
                  <div className="w-48">
                    <ProbabilityBar probability={profile.probability} showLabels={false} />
                  </div>
                )}
              </div>
            </div>

            {/* Account Metadata Features Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Followers</span>
                <span className="font-mono font-bold text-slate-200 text-sm">
                  {formatNumber(profile.features?.followers_count)}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Following</span>
                <span className="font-mono font-bold text-slate-200 text-sm">
                  {formatNumber(profile.features?.following_count)}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Statuses / Tweets</span>
                <span className="font-mono font-bold text-slate-200 text-sm">
                  {formatNumber(profile.features?.statuses_count)}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Tweet Rate/Day</span>
                <span className="font-mono font-bold text-amber-400 text-sm">
                  {profile.features?.tweet_frequency_per_day
                    ? `${profile.features.tweet_frequency_per_day.toFixed(1)}/day`
                    : '—'}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Default Profile</span>
                <span className="font-mono font-bold text-slate-200 text-sm flex items-center gap-1">
                  {profile.features?.default_profile ? (
                    <span className="text-red-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Yes
                    </span>
                  ) : (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <XCircle className="w-3.5 h-3.5" /> No
                    </span>
                  )}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Account Age</span>
                <span className="font-mono font-bold text-slate-200 text-sm">
                  {profile.features?.account_age_days
                    ? `${profile.features.account_age_days} days`
                    : formatDate(profile.features?.created_at)}
                </span>
              </div>
            </div>
          </div>

          {/* Social Network Analysis Metrics */}
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <NetIcon className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
                Social Network Analysis (SNA) Centrality Metrics
              </h3>
            </div>
            <UserMetricsGrid metrics={profile.network} />
          </div>

          {/* 2-Column: GNN Explainability + Ego-Network Preview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Explainability */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
                    GNN Model Explainability
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Feature importances contributing to this classification
                  </p>
                </div>
              </div>
              <FeatureImportanceChart explanations={profile.explanation} />
              
              {/* Sampled Entity Activity */}
              {profile.recent_activity && (
                <div className="pt-3 border-t border-slate-800">
                  <UserRelationshipList activity={profile.recent_activity} />
                </div>
              )}
            </div>

            {/* Neighborhood Subgraph Visualizer Preview */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <NetIcon className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
                    Local Ego-Network Subgraph
                  </h3>
                </div>
                <button
                  onClick={() => navigate('/network')}
                  className="inline-flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                >
                  <span>Open Full Network</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="flex-1 w-full min-h-[360px]">
                <NetworkGraph
                  data={userGraph}
                  height="380px"
                  showDetailsPanel={false}
                  showLegend={false}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
