import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CoordinatedGroup } from '../../types/coordination';
import { formatNumber, formatPercent, formatDecimal } from '../../utils/formatters';
import { ShieldAlert, Users, Network, Hash, AtSign, ArrowRight } from 'lucide-react';

interface CoordinatedGroupCardProps {
  group: CoordinatedGroup;
}

export const CoordinatedGroupCard: React.FC<CoordinatedGroupCardProps> = ({ group }) => {
  const navigate = useNavigate();

  return (
    <div className="p-5 rounded-xl border border-amber-900/40 bg-gradient-to-br from-amber-950/15 via-slate-900/90 to-slate-950 rounded-xl shadow-xl space-y-4 hover:border-amber-700/60 transition-all">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-2 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-bold text-slate-100 font-mono">
              Group #{group.group_id} &bull; Community {group.community_id}
            </h3>
          </div>
          {group.primary_topic && (
            <p className="text-xs text-amber-200/80 mt-1">{group.primary_topic}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
              Coordination Score
            </span>
            <span className="text-base font-bold font-mono text-amber-400">
              {formatDecimal(group.coordination_score, 3)}
            </span>
          </div>
          <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
            {group.status}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
          <div className="flex items-center gap-1 text-slate-400 mb-1">
            <Users className="w-3.5 h-3.5" />
            <span>Members</span>
          </div>
          <span className="font-mono font-bold text-slate-200">
            {formatNumber(group.member_count)}
          </span>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
          <span className="text-slate-400 block mb-1">Bot Accounts</span>
          <span className="font-mono font-bold text-red-400">
            {formatNumber(group.bot_count)}
          </span>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
          <span className="text-slate-400 block mb-1">Bot Ratio</span>
          <span className="font-mono font-bold text-red-400">
            {formatPercent(group.bot_ratio)}
          </span>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
          <div className="flex items-center gap-1 text-slate-400 mb-1">
            <Network className="w-3.5 h-3.5" />
            <span>Density</span>
          </div>
          <span className="font-mono font-bold text-cyan-400">
            {formatDecimal(group.subgraph_density, 3)}
          </span>
        </div>
      </div>

      {/* Detected Signals */}
      {group.signals && group.signals.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">
            Observed Behavioral Signals
          </span>
          <div className="space-y-1.5">
            {group.signals.map((sig, idx) => (
              <div
                key={idx}
                className="p-2 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs flex items-start justify-between gap-2"
              >
                <div>
                  <span className="font-semibold text-slate-200">{sig.signal}</span>
                  {sig.description && (
                    <p className="text-[11px] text-slate-400 mt-0.5">{sig.description}</p>
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

      {/* Shared Entities (Hashtags, URLs, Target Accounts) */}
      {group.shared_entities && (
        <div className="pt-2 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {group.shared_entities.hashtags && (
            <div>
              <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1">
                <Hash className="w-3 h-3 text-cyan-400" />
                Shared Hashtags
              </span>
              <div className="flex flex-wrap gap-1">
                {group.shared_entities.hashtags.map((h, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[10px]">
                    {h.tag} ({h.count})
                  </span>
                ))}
              </div>
            </div>
          )}

          {group.shared_entities.target_accounts && (
            <div>
              <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1">
                <AtSign className="w-3 h-3 text-purple-400" />
                Common Target Accounts
              </span>
              <div className="flex flex-wrap gap-1">
                {group.shared_entities.target_accounts.map((t, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-purple-300 font-mono text-[10px]">
                    {t.target} ({t.count})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Navigation action */}
      <div className="pt-2 flex justify-end">
        <button
          onClick={() => navigate(`/communities/${group.community_id}`)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
        >
          <span>Explore Community #{group.community_id}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
