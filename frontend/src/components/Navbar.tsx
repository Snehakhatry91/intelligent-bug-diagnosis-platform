import React, { useEffect, useState } from 'react';
import { 
  Bug, 
  LayoutDashboard, 
  PlusCircle, 
  FileSearch, 
  Database, 
  BarChart3, 
  ShieldCheck, 
  FlaskConical, 
  BookOpen, 
  Activity
} from 'lucide-react';
import { api } from '../api/client';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  activeSubmissionId?: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab, activeSubmissionId }) => {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false));
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'submit', label: 'Submit Defect', icon: PlusCircle },
    { id: 'results', label: 'Diagnosis Findings', icon: FileSearch, badge: activeSubmissionId ? 'Active' : undefined },
    { id: 'historical', label: 'Historical Defects', icon: Database },
    { id: 'analytics', label: 'Defect Analytics', icon: BarChart3 },
    { id: 'kb', label: 'Verified Knowledge Base', icon: ShieldCheck },
    { id: 'eval', label: 'Empirical Evaluation', icon: FlaskConical },
    { id: 'docs', label: 'Documentation', icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setCurrentTab('dashboard')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition-transform">
            <Bug className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white group-hover:text-blue-400 transition-colors">
                IntelliBug
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
                Infosys AI
              </span>
            </div>
            <p className="text-xs text-slate-400">Diagnosis & Remediation Platform</p>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="hidden lg:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-xl border border-white/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`relative px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 ${
                  isActive 
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30 font-semibold' 
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {item.label}
                {item.badge && (
                  <span className="ml-1 text-[9px] font-bold px-1.5 py-0.2 rounded-full bg-emerald-500 text-white">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Health */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-white/10 text-xs text-slate-300">
            <Activity className={`w-3.5 h-3.5 ${healthy ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
            <span>{healthy ? 'Engine Online' : 'Checking API...'}</span>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="lg:hidden flex overflow-x-auto gap-2 pt-3 pb-1 no-scrollbar">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap flex items-center gap-1.5 ${
                isActive ? 'bg-blue-600 text-white' : 'bg-slate-900 text-slate-300'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
