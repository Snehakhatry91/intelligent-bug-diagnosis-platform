import React, { useEffect, useState } from 'react';
import { 
  Play, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Database, 
  Cpu, 
  ArrowRight, 
  Sparkles,
  Zap,
  Shield,
  Layers
} from 'lucide-react';
import { api, AnalyticsSummary, SubmissionResponse } from '../api/client';

interface DashboardProps {
  onSelectSubmission: (id: string) => void;
  onNavigateSubmit: () => void;
  onTriggerDemo: (scenario: any) => void;
}

export const DashboardPage: React.FC<DashboardProps> = ({
  onSelectSubmission,
  onNavigateSubmit,
  onTriggerDemo,
}) => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [submissions, setSubmissions] = useState<SubmissionResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const demoScenarios = [
    {
      id: 'DEMO-01',
      title: 'NullPointerException in OrderProcessingService',
      type: 'NullPointer Dereference',
      content: 'java.lang.NullPointerException: Cannot invoke "PaymentMethod.getToken()" because "paymentMethod" is null\n\tat com.store.order.OrderProcessingService.executePayment(OrderProcessingService.java:142)',
      severity: 'High',
    },
    {
      id: 'DEMO-02',
      title: 'Database connection pool exhausted & deadlock detected',
      type: 'Database Deadlock',
      content: 'org.postgresql.util.PSQLException: Connection refused to 10.0.4.12:5432.\nHikariPool saturation: 50 active, deadlock detected in connection thread pool.',
      severity: 'Critical',
    },
    {
      id: 'DEMO-03',
      title: 'JWT Bearer Token expired returning 401 Unauthorized',
      type: 'JWT Auth Expired',
      content: '401 Unauthorized: TokenExpiredError: jwt expired at 2026-10-05T00:20:00Z.\nHeader: Authorization: Bearer eyJhbGciOiJIUzI1Ni...',
      severity: 'Medium',
    },
    {
      id: 'DEMO-04',
      title: 'SocketTimeoutException reading from shipping rate API',
      type: 'Network Timeout',
      content: 'java.net.SocketTimeoutException: Read timed out after 15000ms\n\tat org.apache.http.impl.io.ChunkedInputStream.read(ChunkedInputStream.java:175)',
      severity: 'High',
    },
    {
      id: 'DEMO-05',
      title: 'OutOfMemoryError: Java heap space during indexing',
      type: 'OOM Heap Exhaustion',
      content: 'java.lang.OutOfMemoryError: Java heap space\n\tat java.util.ArrayList.grow(ArrayList.java:237)\n\tat com.search.engine.IndexBatchWorker.aggregateTerms(IndexBatchWorker.java:215)',
      severity: 'High',
    },
  ];

  const loadData = async () => {
    try {
      setLoading(true);
      const [anData, subData] = await Promise.all([
        api.getAnalytics(),
        api.listSubmissions(),
      ]);
      setAnalytics(anData);
      setSubmissions(subData);
    } catch (e) {
      console.error('Failed to load dashboard data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel p-8 border border-white/10 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900">
        <div className="absolute -right-12 -top-12 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Autonomous Multi-Agent Defect Reasoning Engine
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mb-3">
            Intelligent Bug Diagnosis & Fix Recommendation
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed mb-6">
            Empowered by 6 specialized agents, RAG retrieval across Mozilla, Apache, and Eclipse defect repositories, 
            and deterministic stack trace decompilation to isolate root causes and formulate production-grade fixes.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onNavigateSubmit}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-xs shadow-lg shadow-blue-500/25 flex items-center gap-2 transition-all hover:scale-105"
            >
              <Zap className="w-4 h-4" />
              Submit Defect for Diagnosis
            </button>
            <a
              href="#demo-scenarios"
              className="px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-white/10 text-slate-200 font-medium text-xs transition-colors flex items-center gap-2"
            >
              <Play className="w-3.5 h-3.5 text-blue-400" />
              Launch 5 Demo Scenarios
            </a>
          </div>
        </div>
      </div>

      {/* KPI Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="glass-card p-5 rounded-xl border border-white/5">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Total Submissions</span>
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : analytics?.total_submissions ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Submitted defect queue</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Completed Analyses</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            {loading ? '...' : analytics?.completed_analyses ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">100% DAG pipeline resolved</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Historical Knowledge</span>
            <Database className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400">
            {loading ? '...' : analytics?.historical_corpus_size ?? 15}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Mozilla, Apache & Eclipse</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Duplicate Rate</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">
            {loading ? '...' : `${analytics?.duplicate_rate_percentage ?? 0}%`}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">&ge; 0.82 similarity cutoff</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-white/5">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Verified Solutions</span>
            <Shield className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400">
            {loading ? '...' : analytics?.verified_kb_entries ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Human-verified RAG memory</p>
        </div>
      </div>

      {/* 5 Required Synthetic Demo Scenarios Section */}
      <div id="demo-scenarios" className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Play className="w-4 h-4 text-blue-400" />
              Five Required Demonstration Scenarios
            </h2>
            <p className="text-xs text-slate-400">
              Synthetic benchmark cases executing end-to-end through Triage, Log Analysis, RAG, Duplicate Detection, Root Cause, and Remediation.
            </p>
          </div>
          <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-white/10">
            Synthetic Benchmark Suite
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {demoScenarios.map((sc) => (
            <div
              key={sc.id}
              className="glass-card p-4 rounded-xl border border-white/5 flex flex-col justify-between hover:border-blue-500/40 cursor-pointer group"
              onClick={() => onTriggerDemo(sc)}
            >
              <div>
                <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 mb-2">
                  <span className="text-blue-400 font-mono">{sc.id}</span>
                  <span className={`px-2 py-0.5 rounded ${
                    sc.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300' :
                    sc.severity === 'High' ? 'bg-orange-500/20 text-orange-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {sc.severity}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-white group-hover:text-blue-300 transition-colors line-clamp-2 mb-2">
                  {sc.title}
                </h3>
                <p className="text-[11px] text-slate-400 mb-3 font-mono">
                  {sc.type}
                </p>
              </div>

              <button
                className="w-full py-1.5 rounded-lg bg-blue-600/20 group-hover:bg-blue-600 text-blue-300 group-hover:text-white text-xs font-medium flex items-center justify-center gap-1.5 transition-all"
              >
                <span>Run Pipeline</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Submissions Table */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Recent Defect Submissions</h2>
            <p className="text-xs text-slate-400">Real-time status of ingested bug reports and stack traces</p>
          </div>
          <button
            onClick={loadData}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            Refresh Table
          </button>
        </div>

        {submissions.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No defect reports submitted yet. Submit a bug above or trigger one of the 5 demo cases!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-white/10 text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Title & Context</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Submitted</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {submissions.slice(0, 10).map((sub) => (
                  <tr key={sub.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-medium text-white max-w-md">
                      <div className="truncate">{sub.title}</div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">UUID: {sub.id}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-300 border border-white/5 uppercase font-mono">
                        {sub.input_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(sub.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
                        sub.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                        sub.status === 'PROCESSING' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30 animate-pulse' :
                        sub.status === 'FAILED' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                        'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}>
                        {sub.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => onSelectSubmission(sub.id)}
                        className="px-3 py-1.5 rounded-lg bg-blue-600/30 hover:bg-blue-600 text-blue-300 hover:text-white transition-all text-xs font-medium inline-flex items-center gap-1"
                      >
                        <span>View Diagnosis</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
