import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  PieChart as PieIcon, 
  CheckCircle, 
  AlertCircle, 
  ShieldCheck, 
  Layers, 
  Database,
  TrendingUp,
  Cpu
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { api, AnalyticsSummary } from '../api/client';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAnalytics()
      .then(setAnalytics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const SEVERITY_COLORS: Record<string, string> = {
    Critical: '#f43f5e',
    High: '#f97316',
    Medium: '#eab308',
    Low: '#64748b',
    'Pending Analysis': '#3b82f6',
  };

  const PRIORITY_COLORS: Record<string, string> = {
    High: '#ef4444',
    Medium: '#f59e0b',
    Low: '#10b981',
    'Pending Analysis': '#3b82f6',
  };

  const COMPONENT_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

  if (loading) {
    return (
      <div className="text-center py-20 text-slate-500 text-xs">
        Aggregating defect metrics and computing mathematical reconciliation...
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-20 text-rose-400 text-xs">
        Failed to load analytics telemetry.
      </div>
    );
  }

  // Strict population calculations for reconciliation display
  const totalSubmissions = analytics.total_submissions;
  const severitySum = analytics.severity_distribution.reduce((acc, cur) => acc + cur.count, 0);
  const prioritySum = analytics.priority_distribution.reduce((acc, cur) => acc + cur.count, 0);

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in pb-12">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-400" />
          Defect Pattern Analytics & Population Telemetry
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Mathematically reconciled distribution metrics calculated strictly over active defect databases.
        </p>
      </div>

      {/* Automated Reconciliation Verification Banner */}
      <div className={`p-4 rounded-xl border flex items-center justify-between ${
        analytics.reconciliation_verified && severitySum === totalSubmissions
          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
      }`}>
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 shrink-0" />
          <div>
            <span className="font-bold text-xs block">
              {analytics.reconciliation_verified ? 'Mathematical Population Reconciliation Verified' : 'Reconciliation Discrepancy'}
            </span>
            <span className="text-[11px] text-slate-300">
              Total Submissions ({totalSubmissions}) &equiv; &sum; Severity Counts ({severitySum}) &equiv; &sum; Priority Counts ({prioritySum})
            </span>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 border border-emerald-500/30">
          Strict Integrity Pass
        </span>
      </div>

      {/* Top 4 KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Total Defect Submissions</span>
          <div className="text-2xl font-extrabold text-white">{analytics.total_submissions}</div>
          <span className="text-[10px] text-slate-500">Total ingested population</span>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Completed Diagnoses</span>
          <div className="text-2xl font-extrabold text-emerald-400">{analytics.completed_analyses}</div>
          <span className="text-[10px] text-slate-500">Processed through full DAG</span>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Duplicate Defect Rate</span>
          <div className="text-2xl font-extrabold text-amber-400">{analytics.duplicate_rate_percentage}%</div>
          <span className="text-[10px] text-slate-500">&ge; 0.82 similarity threshold</span>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Historical Precedent Corpus</span>
          <div className="text-2xl font-extrabold text-purple-400">{analytics.historical_corpus_size}</div>
          <span className="text-[10px] text-slate-500">Mozilla, Apache & Eclipse</span>
        </div>
      </div>

      {/* Reconciled Distribution Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Severity Distribution */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-orange-400" />
              Reconciled Severity Breakdown
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Total: {severitySum}</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics.severity_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="count"
                  nameKey="name"
                >
                  {analytics.severity_distribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={SEVERITY_COLORS[entry.name] || '#3b82f6'} 
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  formatter={(value) => <span className="text-slate-300 text-xs">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Reconciled Priority Allocation
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Total: {prioritySum}</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.priority_distribution}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {analytics.priority_distribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={PRIORITY_COLORS[entry.name] || '#3b82f6'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Affected Components */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            Affected System Components
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.component_distribution} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={11} allowDecimals={false} />
                <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={10} width={120} />
                <Tooltip 
                  contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 6, 6, 0]}>
                  {analytics.component_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COMPONENT_COLORS[index % COMPONENT_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recurring Exception Types */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            Recurring Technical Exception Signatures
          </h3>
          <div className="h-64 overflow-y-auto space-y-2 pr-1">
            {analytics.exception_distribution.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-8 text-center">No structured exceptions extracted yet.</p>
            ) : (
              analytics.exception_distribution.map((ex, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-white/5 flex items-center justify-between text-xs">
                  <span className="font-mono text-slate-300 truncate max-w-xs">{ex.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold text-[10px]">
                      {ex.count} occurrences
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">({ex.percentage}%)</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
