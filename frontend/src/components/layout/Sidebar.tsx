import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Network,
  UsersRound,
  ShieldAlert,
  Cpu,
  ChevronLeft,
  ChevronRight,
  Database,
  Radio,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

interface NavItem {
  label: string;
  to: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: 'Overview Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'User Analysis', to: '/users', icon: Users },
  { label: 'Network Analysis', to: '/network', icon: Network },
  { label: 'Community Analysis', to: '/communities', icon: UsersRound },
  { label: 'Coordination Analysis', to: '/coordination', icon: ShieldAlert, badge: '7 Flagged' },
  { label: 'Model Performance', to: '/model-performance', icon: Cpu },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  return (
    <aside
      className={`fixed top-0 left-0 h-screen z-30 flex flex-col bg-slate-950/95 border-r border-slate-800/80 transition-all duration-300 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/80">
        {!collapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="p-2 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-700 text-white shadow-md shadow-cyan-900/30">
              <Radio className="w-4 h-4 animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-black tracking-wider text-slate-100 font-mono">
                SNA SENTRY
              </span>
              <span className="text-[10px] text-cyan-400 font-mono tracking-tight">
                MGTAB GNN Intelligence
              </span>
            </div>
          </div>
        )}

        {collapsed && (
          <div className="mx-auto p-2 rounded-lg bg-cyan-600 text-white">
            <Radio className="w-5 h-5" />
          </div>
        )}

        <button
          onClick={onToggle}
          className={`p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800 transition-colors ${
            collapsed ? 'hidden' : 'block'
          }`}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-4 px-2 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
                }`
              }
              title={collapsed ? item.label : undefined}
            >
              <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" />
              {!collapsed && (
                <span className="flex-1 truncate tracking-tight">{item.label}</span>
              )}
              {!collapsed && item.badge && (
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Dataset & Research Benchmark Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        {!collapsed ? (
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 space-y-1">
            <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>MGTAB Benchmark</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Multi-relational Graph Twitter Dataset (10.2k nodes / 147k edges)
            </p>
          </div>
        ) : (
          <button
            onClick={onToggle}
            className="w-full flex justify-center p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800"
            aria-label="Expand sidebar"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </aside>
  );
};
