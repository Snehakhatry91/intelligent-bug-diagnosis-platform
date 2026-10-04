import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  Database, 
  ArrowRight, 
  CheckCircle2, 
  UserCheck, 
  Clock, 
  Code,
  Layers,
  Sparkles
} from 'lucide-react';
import { api, KBEntryResponse } from '../api/client';

export const KnowledgeBasePage: React.FC = () => {
  const [entries, setEntries] = useState<KBEntryResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listKBEntries()
      .then(setEntries)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto animate-fade-in pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          Verified Knowledge Base & Memory Growth
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Self-improving enterprise defect memory. Only human-verified diagnoses and confirmed resolutions are promoted into the 384-dimensional vector store.
        </p>
      </div>

      {/* Visual Workflow Diagram */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
          Knowledge Base Promotion Lifecycle (Anti-Pollution Architecture)
        </span>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs">
          <div className="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <span className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 font-bold flex items-center justify-center mx-auto text-xs">1</span>
            <span className="font-semibold text-white block">Diagnosed Bug</span>
            <span className="text-[10px] text-slate-500">Multi-agent output</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-emerald-500/30 space-y-1">
            <span className="w-6 h-6 rounded-full bg-emerald-600/30 text-emerald-400 font-bold flex items-center justify-center mx-auto text-xs">2</span>
            <span className="font-semibold text-emerald-300 block">Human Verify</span>
            <span className="text-[10px] text-slate-500">Lead engineer sign-off</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <span className="w-6 h-6 rounded-full bg-indigo-600/30 text-indigo-400 font-bold flex items-center justify-center mx-auto text-xs">3</span>
            <span className="font-semibold text-white block">Normalization</span>
            <span className="text-[10px] text-slate-500">Sanitized format</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <span className="w-6 h-6 rounded-full bg-purple-600/30 text-purple-400 font-bold flex items-center justify-center mx-auto text-xs">4</span>
            <span className="font-semibold text-white block">Text Chunker</span>
            <span className="text-[10px] text-slate-500">Context boundaries</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-600/30 text-cyan-400 font-bold flex items-center justify-center mx-auto text-xs">5</span>
            <span className="font-semibold text-white block">Dense Embed</span>
            <span className="text-[10px] text-slate-500">384-dim unit vector</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-purple-500/30 space-y-1">
            <span className="w-6 h-6 rounded-full bg-purple-600 text-white font-bold flex items-center justify-center mx-auto text-xs">6</span>
            <span className="font-semibold text-purple-300 block">Vector Index</span>
            <span className="text-[10px] text-slate-500">Active RAG memory</span>
          </div>
        </div>
      </div>

      {/* Verified Entries Listing */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" />
            Active Verified Knowledge Base Entries ({entries.length})
          </h2>
          <span className="text-[11px] text-slate-400">Indexed in vector store</span>
        </div>

        {loading ? (
          <div className="text-center py-16 text-slate-500 text-xs">Loading verified solutions...</div>
        ) : entries.length === 0 ? (
          <div className="glass-panel p-12 rounded-2xl text-center space-y-3 border border-white/10">
            <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-sm font-bold text-white">No Verified Entries Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Run a diagnosis from the Dashboard or Submit page, review the findings, and click "Promote to Verified KB" to grow system memory!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {entries.map((entry) => (
              <div key={entry.id} className="glass-card p-6 rounded-2xl border border-white/5 space-y-4 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-emerald-400 font-bold">
                      KB-{entry.id.slice(0, 8).toUpperCase()}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                      {entry.component}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white leading-snug">{entry.title}</h3>
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Confirmed Root Cause</span>
                    <p className="text-slate-200 text-[11px] leading-relaxed">{entry.root_cause}</p>
                  </div>

                  <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
                    <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">Confirmed Remediation</span>
                    <p className="text-emerald-200 text-[11px] leading-relaxed">{entry.resolution}</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-400" />
                    <span>Verified by: <strong className="text-slate-200">{entry.verified_by}</strong></span>
                  </div>
                  <span>{new Date(entry.verified_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
