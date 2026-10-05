import React, { useEffect, useState } from 'react';
import { 
  Database, 
  Search, 
  Filter, 
  ExternalLink, 
  ShieldCheck, 
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';
import { api, HistoricalDefect, HistoricalEvidenceItem } from '../api/client';

export const HistoricalDefectsPage: React.FC = () => {
  const [defects, setDefects] = useState<HistoricalDefect[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [semanticMode, setSemanticMode] = useState(false);
  const [semanticResults, setSemanticResults] = useState<HistoricalEvidenceItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDefects = async () => {
    setLoading(true);
    try {
      if (semanticMode && searchQuery.trim()) {
        const matches = await api.searchHistorical(searchQuery);
        setSemanticResults(matches);
      } else {
        const data = await api.listHistoricalDefects({
          project: selectedProject !== 'all' ? selectedProject : undefined,
          severity: selectedSeverity !== 'all' ? selectedSeverity : undefined,
          search: searchQuery.trim() || undefined,
        });
        setDefects(data);
      }
    } catch (e) {
      console.error('Failed to fetch historical defects', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDefects();
  }, [selectedProject, selectedSeverity, semanticMode]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDefects();
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-purple-400" />
            Historical Defect Knowledge Base
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Curated defect repository with source provenance from Mozilla Bugzilla, Apache Jira, and Eclipse Bugzilla ecosystems.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-900 border border-white/10 p-1 rounded-xl text-xs">
          <button
            type="button"
            onClick={() => setSemanticMode(false)}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              !semanticMode ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            Structured Filter
          </button>
          <button
            type="button"
            onClick={() => setSemanticMode(true)}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1 ${
              semanticMode ? 'bg-purple-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Vector Semantic Search
          </button>
        </div>
      </div>

      {/* Search & Filters */}
      <form onSubmit={handleSearchSubmit} className="glass-panel p-4 rounded-xl border border-white/10 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={semanticMode ? "Enter crash text or query for 384-dim semantic similarity search..." : "Search by keyword, issue ID, or component..."}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
          />
        </div>

        {!semanticMode && (
          <>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-950 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Ecosystems</option>
              <option value="Mozilla">Mozilla Bugzilla</option>
              <option value="Apache">Apache Jira</option>
              <option value="Eclipse">Eclipse Bugzilla</option>
            </select>

            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-950 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </>
        )}

        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all cursor-pointer"
        >
          {semanticMode ? 'Search Vectors' : 'Filter'}
        </button>
      </form>

      {/* Results View */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-xs">
          Loading defect corpus...
        </div>
      ) : semanticMode ? (
        <div className="space-y-3">
          <div className="text-xs font-semibold text-slate-400">
            Vector Similarity Matches ({semanticResults.length}) using Centralized Cosine Policy
          </div>
          {semanticResults.length === 0 ? (
            <div className="glass-panel p-8 rounded-xl text-center text-xs text-slate-500">
              No historical matches met the evidence threshold (&ge; 0.45).
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {semanticResults.map((m, i) => (
                <div key={i} className="glass-card p-5 rounded-xl border border-white/5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-blue-400">{m.issue_id}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      m.similarity_score >= 0.82 ? 'bg-rose-500/20 text-rose-300' :
                      m.similarity_score >= 0.65 ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {(m.similarity_score * 100).toFixed(1)}% Similarity ({m.classification})
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-white leading-tight">{m.title}</h3>
                  <div className="p-3 rounded-lg bg-slate-950 border border-white/5 text-[11px] text-emerald-300">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Fix Patch Summary</span>
                    {m.fix_patch_summary || 'Resolution detailed in upstream record.'}
                  </div>
                  {m.source_url && (
                    <a
                      href={m.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[10px] text-blue-400 hover:text-blue-300 inline-flex items-center gap-1"
                    >
                      <span>Upstream {m.project} Source</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {defects.map((def) => (
            <div key={def.issue_id} className="glass-card p-5 rounded-xl border border-white/5 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-purple-400">{def.issue_id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    def.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                    def.severity === 'High' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                    'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {def.severity}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-white leading-tight">{def.title}</h3>
                <p className="text-[11px] text-slate-400 line-clamp-3">{def.description}</p>
              </div>

              <div className="space-y-3 pt-2 border-t border-white/5">
                <div className="p-2.5 rounded-lg bg-slate-950 text-[11px] text-slate-300 font-mono">
                  <span className="text-[10px] text-slate-500 block uppercase">Resolution / Fix</span>
                  <div className="text-emerald-300 text-[10px] truncate">{def.fix_patch_summary}</div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[150px]">{def.component}</span>
                  <a
                    href={def.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-400 hover:text-blue-300 flex items-center gap-1"
                  >
                    <span>{def.project} Bugzilla/Jira</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
