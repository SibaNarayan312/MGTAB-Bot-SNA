import React from 'react';
import { Hash, AtSign, Link as LinkIcon } from 'lucide-react';

interface UserRelationshipListProps {
  activity?: {
    total_tweets_sampled?: number;
    hashtags?: string[];
    mentioned_users?: string[];
    urls_shared?: string[];
  };
}

export const UserRelationshipList: React.FC<UserRelationshipListProps> = ({ activity }) => {
  if (!activity) {
    return (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 text-xs text-slate-400">
        No recent entity activity sampled for this user.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Hashtags */}
      {activity.hashtags && activity.hashtags.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <Hash className="w-3.5 h-3.5 text-cyan-400" />
            <span>Frequent Hashtags</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {activity.hashtags.map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 rounded bg-slate-800 text-cyan-300 font-mono text-[11px] border border-slate-700/60"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Mentioned Users */}
      {activity.mentioned_users && activity.mentioned_users.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <AtSign className="w-3.5 h-3.5 text-purple-400" />
            <span>Frequent Mention Targets</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {activity.mentioned_users.map((user, idx) => (
              <span
                key={idx}
                className="px-2 py-1 rounded bg-slate-800 text-purple-300 font-mono text-[11px] border border-slate-700/60"
              >
                @{user}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Shared URLs */}
      {activity.urls_shared && activity.urls_shared.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <LinkIcon className="w-3.5 h-3.5 text-amber-400" />
            <span>Shared URLs &amp; Domains</span>
          </div>
          <div className="space-y-1">
            {activity.urls_shared.map((url, idx) => (
              <div
                key={idx}
                className="px-2.5 py-1.5 rounded bg-slate-950/80 text-amber-300/90 font-mono text-[11px] border border-slate-800 truncate"
              >
                {url}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
