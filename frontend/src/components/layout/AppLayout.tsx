import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopHeader } from './TopHeader';

export const AppLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex font-sans antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Sidebar Navigation */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          sidebarCollapsed ? 'pl-20' : 'pl-0 lg:pl-64'
        }`}
      >
        <TopHeader onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />

        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
          <Outlet />
        </main>

        <footer className="py-4 px-6 border-t border-slate-900 bg-slate-950/60 text-center text-xs text-slate-400">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
            <span>
              SNA-Based Detection of Coordinated Misinformation and Bot-Like Behaviour &bull; MGTAB Benchmark
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              Research Prototype &bull; React + TypeScript + Cytoscape.js
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
};
