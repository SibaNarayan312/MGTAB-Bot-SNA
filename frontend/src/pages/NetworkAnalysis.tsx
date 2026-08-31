import React, { useEffect, useState, useCallback } from 'react';
import { networkService } from '../services/networkService';
import { communityService } from '../services/communityService';
import { NetworkGraphData, NetworkFilterOptions } from '../types/network';
import { CommunitiesResponse } from '../types/community';
import { PageHeader } from '../components/common/PageHeader';
import { NetworkGraph } from '../components/network/NetworkGraph';
import { ErrorState } from '../components/common/ErrorState';
import { Filter, RefreshCw, Search, ShieldAlert, SlidersHorizontal } from 'lucide-react';

export const NetworkAnalysis: React.FC = () => {
  const [graphData, setGraphData] = useState<NetworkGraphData | null>(null);
  const [communities, setCommunities] = useState<CommunitiesResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [filters, setFilters] = useState<NetworkFilterOptions>({
    prediction: 'ALL',
    communityId: 'ALL',
    relationshipType: 'ALL',
    minDegree: 0,
    searchQuery: '',
    maxNodes: 100,
  });

  const [filterPanelOpen, setFilterPanelOpen] = useState<boolean>(true);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [graph, commList] = await Promise.all([
        networkService.getNetwork(filters),
        communityService.getCommunities(),
      ]);
      setGraphData(graph);
      setCommunities(commList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load network graph visualization.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const handleResetFilters = () => {
    setFilters({
      prediction: 'ALL',
      communityId: 'ALL',
      relationshipType: 'ALL',
      minDegree: 0,
      searchQuery: '',
      maxNodes: 100,
    });
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <PageHeader
        title="Multi-Relational Network Visualizer"
        subtitle="Interactive Cytoscape.js exploration with multi-edge relation types, GNN classification overlays, and topological community clustering"
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilterPanelOpen(!filterPanelOpen)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{filterPanelOpen ? 'Hide Filters' : 'Show Filters'}</span>
            </button>

            <button
              onClick={fetchGraph}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reload Graph</span>
            </button>
          </div>
        }
      />

      {/* Filter Toolbar */}
      {filterPanelOpen && (
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/90 shadow-lg space-y-3 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs font-semibold text-slate-300">
            <div className="flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-cyan-400" />
              <span>Graph Subgraph Filters</span>
            </div>
            <button
              onClick={handleResetFilters}
              className="text-xs text-slate-400 hover:text-cyan-400 transition-colors"
            >
              Reset Filters
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-xs">
            {/* Search Node ID */}
            <div>
              <label className="text-slate-400 block mb-1 text-[11px] font-medium">
                Search Node / Screen Name
              </label>
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="ID or name..."
                  value={filters.searchQuery}
                  onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
                  className="w-full pl-8 pr-2 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 font-mono text-xs focus:ring-1 focus:ring-cyan-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Prediction Filter */}
            <div>
              <label className="text-slate-400 block mb-1 text-[11px] font-medium">
                Prediction Class
              </label>
              <select
                value={filters.prediction}
                onChange={(e) =>
                  setFilters({ ...filters, prediction: e.target.value as NetworkFilterOptions['prediction'] })
                }
                className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs focus:ring-1 focus:ring-cyan-500 focus:outline-none"
              >
                <option value="ALL">All Accounts (All Classes)</option>
                <option value="BOT">Bot Accounts Only</option>
                <option value="HUMAN">Human Accounts Only</option>
              </select>
            </div>

            {/* Community Filter */}
            <div>
              <label className="text-slate-400 block mb-1 text-[11px] font-medium">
                Community Cluster
              </label>
              <select
                value={filters.communityId}
                onChange={(e) => setFilters({ ...filters, communityId: e.target.value })}
                className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs focus:ring-1 focus:ring-cyan-500 focus:outline-none"
              >
                <option value="ALL">All Communities</option>
                {communities?.communities.map((c) => (
                  <option key={c.id} value={c.id}>
                    Community #{c.id} ({c.member_count} members{c.status === 'potentially_coordinated' ? ' ⚠' : ''})
                  </option>
                ))}
              </select>
            </div>

            {/* Multi-Relational Type Filter */}
            <div>
              <label className="text-slate-400 block mb-1 text-[11px] font-medium">
                Edge Interaction Type
              </label>
              <select
                value={filters.relationshipType}
                onChange={(e) => setFilters({ ...filters, relationshipType: e.target.value })}
                className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 font-mono text-xs focus:ring-1 focus:ring-cyan-500 focus:outline-none"
              >
                <option value="ALL">All Relationships</option>
                <option value="RETWEET">RETWEET</option>
                <option value="MENTION">MENTION</option>
                <option value="FOLLOW">FOLLOW</option>
                <option value="FRIEND">FRIEND</option>
                <option value="REPLY">REPLY</option>
              </select>
            </div>

            {/* Min Degree Slider */}
            <div>
              <div className="flex justify-between text-slate-400 mb-1 text-[11px]">
                <span>Min Degree Threshold:</span>
                <span className="font-mono text-cyan-400 font-bold">{filters.minDegree}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={filters.minDegree}
                onChange={(e) => setFilters({ ...filters, minDegree: Number(e.target.value) })}
                className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
              />
            </div>
          </div>
        </div>
      )}

      {error && <ErrorState message={error} onRetry={fetchGraph} />}

      {/* Main Cytoscape Graph Canvas */}
      <div className="relative w-full">
        <NetworkGraph
          data={graphData}
          loading={loading}
          height="640px"
          showControls={true}
          showLegend={true}
          showDetailsPanel={true}
        />
      </div>

      {/* Performance & Filtering Advisory Note (Section 21 Requirement) */}
      <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-xs text-slate-400 font-mono">
        <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0" />
        <span>
          Showing filtered topological subgraph view. Use community filters or search to explore isolated dense clusters.
        </span>
      </div>
    </div>
  );
};
