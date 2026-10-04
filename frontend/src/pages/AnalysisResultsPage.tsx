import React, { useEffect, useState } from 'react';
import { 
  Bug, 
  Activity, 
  ShieldAlert, 
  CheckCircle, 
  Copy, 
  Check, 
  Clock, 
  Code, 
  FileText, 
  Layers, 
  ExternalLink, 
  Sparkles, 
  ShieldCheck, 
  Terminal, 
  ChevronRight,
  Flame,
  AlertTriangle,
  Play,
  Cpu
} from 'lucide-react';
import { api, BugAnalysisContext } from '../api/client';

interface AnalysisResultsProps {
  submissionId: string | null;
  onNavigateSubmit: () => void;
}

export const AnalysisResultsPage: React.FC<AnalysisResultsProps> = ({
  submissionId,
  onNavigateSubmit,
}) => {
  const [context, setContext] = useState<BugAnalysisContext | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'structured' | 'json'>('structured');
  const [copied, setCopied] = useState(false);

  // Promotion modal state
  const [showPromoteModal, setShowPromoteModal] = useState(false);
  const [verifierName, setVerifierName] = useState('');
  const [verificationNotes, setVerificationNotes] = useState('');
  const [promoteSuccess, setPromoteSuccess] = useState(false);
  const [promoting, setPromoting] = useState(false);

  useEffect(() => {
    if (!submissionId) return;

    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      try {
        // Try getting existing diagnosis first
        try {
          const existing = await api.getDiagnosis(submissionId);
          setContext(existing);
          setLoading(false);
          return;
        } catch {
          // If not diagnosed yet, run diagnosis
          const result = await api.runDiagnosis(submissionId);
          setContext(result);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to retrieve diagnosis');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [submissionId]);

  const handleCopyJson = () => {
    if (!context) return;
    navigator.clipboard.writeText(JSON.stringify(context, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePromoteToKB = async () => {
    if (!context || !verifierName.trim()) return;
    setPromoting(true);
    try {
      await api.promoteVerifiedBug({
        analysis_id: context.submission_id,
        verified_by: verifierName,
        verification_notes: verificationNotes || 'Verified production fix applied.',
        confirmed_root_cause: context.root_cause?.hypothesis || 'Confirmed defect root cause.',
        confirmed_resolution: context.remediation?.action || 'Confirmed remediation applied.',
      });
      setPromoteSuccess(true);
      setTimeout(() => {
        setShowPromoteModal(false);
        setPromoteSuccess(false);
      }, 2000);
    } catch (e: any) {
      alert(`Promotion failed: ${e.message}`);
    } finally {
      setPromoting(false);
    }
  };

  if (!submissionId) {
    return (
      <div className="glass-panel p-12 rounded-2xl border border-white/10 text-center max-w-xl mx-auto my-12 space-y-4">
        <Bug className="w-12 h-12 text-slate-500 mx-auto" />
        <h2 className="text-lg font-bold text-white">No Defect Selected for Diagnosis</h2>
        <p className="text-xs text-slate-400">
          Select an active defect from the Dashboard or submit a new crash log to view multi-agent diagnostic findings.
        </p>
        <button
          onClick={onNavigateSubmit}
          className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-lg shadow-blue-500/25 transition-all"
        >
          Submit Defect Now
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="glass-panel p-16 rounded-2xl border border-white/10 text-center max-w-xl mx-auto my-12 space-y-6">
        <div className="relative w-16 h-16 mx-auto">
          <div className="w-16 h-16 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin" />
          <Sparkles className="w-6 h-6 text-blue-400 absolute inset-0 m-auto animate-pulse" />
        </div>
        <div>
          <h2 className="text-base font-bold text-white">Multi-Agent Pipeline Executing...</h2>
          <p className="text-xs text-slate-400 mt-2">
            Triage Agent &rarr; Log Analysis Agent &rarr; RAG Engine &rarr; Duplicate Detection &rarr; Root Cause &rarr; Remediation
          </p>
        </div>
      </div>
    );
  }

  if (error || !context) {
    return (
      <div className="glass-panel p-12 rounded-2xl border border-rose-500/20 text-center max-w-xl mx-auto my-12 space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Diagnosis Execution Failed</h2>
        <p className="text-xs text-rose-300">{error || 'Unknown error occurred'}</p>
        <button
          onClick={onNavigateSubmit}
          className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-medium"
        >
          Return to Submission
        </button>
      </div>
    );
  }

  const { submission, triage, log_analysis, duplicate_detection, root_cause, remediation, timeline } = context;

  const totalPipelineTime = timeline.reduce((acc, t) => acc + t.duration_ms, 0);

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto pb-12">
      {/* Top Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4 bg-gradient-to-r from-slate-900/90 to-slate-950">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                triage?.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                triage?.severity === 'High' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                triage?.severity === 'Medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                'bg-slate-700/50 text-slate-300 border border-slate-600/30'
              }`}>
                {triage?.severity || 'Assessing'} Severity
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
                {triage?.priority || 'Medium'} Priority
              </span>
              <span className="text-[11px] text-slate-400 font-mono">
                ID: {submission.id.slice(0, 13)}...
              </span>
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              {submission.title}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Component: <span className="text-slate-200 font-medium">{triage?.affected_component || 'General'}</span> | 
              Input: <span className="text-slate-200 uppercase font-mono">{submission.input_type}</span> | 
              Total Pipeline Latency: <span className="text-emerald-400 font-bold">{totalPipelineTime.toFixed(1)} ms</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowPromoteModal(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600 border border-emerald-500/30 text-emerald-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4" />
              Promote to Verified KB
            </button>
            <div className="bg-slate-900 border border-white/10 p-1 rounded-xl flex gap-1">
              <button
                onClick={() => setActiveTab('structured')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'structured' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Findings View
              </button>
              <button
                onClick={() => setActiveTab('json')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'json' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Raw JSON Context
              </button>
            </div>
          </div>
        </div>
      </div>

      {activeTab === 'json' ? (
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-300">Canonical BugAnalysisContext JSON Payload</span>
            <button
              onClick={handleCopyJson}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied to Clipboard' : 'Copy JSON'}
            </button>
          </div>
          <pre className="p-4 rounded-xl bg-slate-950 text-emerald-400 font-mono text-xs overflow-x-auto border border-white/5 leading-relaxed max-h-[600px]">
            {JSON.stringify(context, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column (2 Cols wide on desktop) */}
          <div className="lg:col-span-2 space-y-6">

            {/* STAGE 1: Triage Reasoning & Confidence */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Flame className="w-4 h-4 text-orange-400" />
                  Stage 1: Triage Agent Classification
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Confidence Score:</span>
                  <span className="text-xs font-bold text-blue-400 px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20">
                    {((triage?.confidence ?? 0.7) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-white/5">
                {triage?.reasoning || 'Diagnostic heuristics applied.'}
              </p>

              {triage?.signals && triage.signals.length > 0 && (
                <div>
                  <div className="text-[11px] font-semibold text-slate-400 mb-2">Detected Diagnostic Signals:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {triage.signals.map((sig, i) => (
                      <span key={i} className="px-2.5 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-mono border border-white/5">
                        {sig}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* STAGE 2: Deterministic Log Analysis */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                Stage 2: Deterministic Log Analysis Agent
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="bg-slate-900/70 p-3 rounded-xl border border-white/5">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Parsed Exception Signature</span>
                  <span className="font-semibold text-rose-300 font-mono text-[11px]">
                    {log_analysis?.exception_type || 'Unknown / Unstructured'}
                  </span>
                </div>

                <div className="bg-slate-900/70 p-3 rounded-xl border border-white/5">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Primary Failure Site</span>
                  <span className="font-semibold text-white font-mono text-[11px] truncate block">
                    {log_analysis?.failure_point || 'Unavailable'}
                  </span>
                </div>
              </div>

              {log_analysis?.stack_frames && log_analysis.stack_frames.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[11px] font-semibold text-slate-400 block">
                    Decompiled Stack Frames ({log_analysis.stack_frames.length})
                  </span>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                    {log_analysis.stack_frames.map((frame, i) => (
                      <div key={i} className="p-2 rounded-lg bg-slate-950 font-mono text-[11px] text-slate-300 border border-white/5 flex items-center justify-between">
                        <span className="text-blue-300 truncate">{frame.function || frame.file}</span>
                        <span className="text-slate-500 shrink-0 ml-2">Line {frame.line ?? 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* STAGE 5: Root Cause with 4-Tier Attribution */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  Stage 5: Root Cause Agent (Four-Tier Attribution)
                </h3>
                <span className="text-xs font-bold text-purple-400 px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20">
                  {((root_cause?.confidence ?? 0.8) * 100).toFixed(0)}% Confidence
                </span>
              </div>

              <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 text-xs text-purple-200">
                <span className="font-bold block text-white text-xs mb-1">Diagnosed Hypothesis:</span>
                {root_cause?.hypothesis || 'Diagnosis in progress...'}
              </div>

              {/* 4-Tier Attribution Grid */}
              <div className="space-y-3 pt-2">
                <div className="text-xs font-semibold text-slate-300">Four-Tier Diagnostic Attribution Guardrail:</div>

                <div className="space-y-2">
                  {/* Tier 1: Observed Facts */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border-l-4 border-blue-500 text-xs space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block">
                      1. Observed Facts (Deterministic Empirical Data)
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                      {root_cause?.observed_facts.map((fact, i) => (
                        <li key={i}>{fact}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Tier 2: Historical Evidence */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border-l-4 border-purple-500 text-xs space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 block">
                      2. Historical Precedent Evidence (RAG Corpus)
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                      {root_cause?.historical_evidence.map((ev, i) => (
                        <li key={i}>{ev}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Tier 3: AI Inference */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border-l-4 border-amber-500 text-xs space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 block">
                      3. AI Inference (Hypothesized Failure Mechanism)
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                      {root_cause?.ai_inference.map((inf, i) => (
                        <li key={i}>{inf}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Tier 4: Fix Recommendation */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border-l-4 border-emerald-500 text-xs space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">
                      4. Fix Recommendation (Actionable Engineering Guidance)
                    </span>
                    <p className="text-slate-200 text-[11px]">
                      {remediation?.action}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* STAGE 6: Remediation & Code Patch */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Code className="w-4 h-4 text-emerald-400" />
                Stage 6: Remediation Agent Fix Recommendation
              </h3>

              <div className="bg-emerald-950/20 p-4 rounded-xl border border-emerald-500/30 space-y-2">
                <span className="text-xs font-bold text-emerald-300 block">{remediation?.action}</span>
                <p className="text-xs text-slate-300 leading-relaxed">{remediation?.explanation}</p>
              </div>

              {remediation?.code_patch && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span className="font-semibold text-slate-300">Recommended Code Patch / Guard</span>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(remediation.code_patch || '');
                        alert('Code patch copied to clipboard');
                      }}
                      className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 cursor-pointer"
                    >
                      <Copy className="w-3 h-3" /> Copy Snippet
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-300 border border-white/5 overflow-x-auto leading-relaxed">
                    {remediation.code_patch}
                  </pre>
                </div>
              )}

              {remediation?.recommended_tests && remediation.recommended_tests.length > 0 && (
                <div className="space-y-2 pt-2">
                  <span className="text-xs font-semibold text-slate-300 block">Recommended Verification Tests</span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {remediation.recommended_tests.map((t, i) => (
                      <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-white/5 text-xs">
                        <span className="text-[10px] font-bold uppercase text-blue-400 block">{t.test_type}</span>
                        <p className="text-slate-300 text-[11px] mt-1">{t.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>

          {/* Right Column: Duplicate Detection, RAG Matches & Pipeline Timeline */}
          <div className="space-y-6">

            {/* STAGE 4: Duplicate Detection */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-400" />
                Stage 4: Duplicate Detection Agent
              </h3>

              <div className={`p-4 rounded-xl text-xs space-y-1 border ${
                duplicate_detection?.is_duplicate
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              }`}>
                <div className="font-bold flex items-center gap-1.5">
                  {duplicate_detection?.is_duplicate ? (
                    <>
                      <AlertTriangle className="w-4 h-4" />
                      Likely Duplicate Detected (&ge; {duplicate_detection?.duplicate_threshold * 100}%)
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Novel Defect (No Duplicate Precedent)
                    </>
                  )}
                </div>
                <p className="text-[11px] text-slate-300">{duplicate_detection?.summary}</p>
              </div>

              {/* STAGE 3: RAG Retrieval Matches */}
              <div className="space-y-3 pt-2">
                <span className="text-xs font-semibold text-slate-300 block">
                  Historical Precedent Matches ({context.rag_retrieval.length})
                </span>

                {context.rag_retrieval.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">Insufficient historical evidence found (&lt; 0.45 threshold).</p>
                ) : (
                  <div className="space-y-2">
                    {context.rag_retrieval.map((item, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1.5 text-xs hover:border-blue-500/30 transition-colors">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-blue-400 text-[11px]">{item.issue_id}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.2 rounded ${
                            item.similarity_score >= 0.82 ? 'bg-rose-500/20 text-rose-300' :
                            item.similarity_score >= 0.65 ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-700 text-slate-300'
                          }`}>
                            {(item.similarity_score * 100).toFixed(1)}% Sim
                          </span>
                        </div>
                        <h4 className="text-white text-[11px] font-medium leading-tight">{item.title}</h4>
                        <p className="text-[10px] text-slate-400 line-clamp-2">
                          Fix: {item.fix_patch_summary || item.resolution || 'Resolution available in upstream repo'}
                        </p>
                        {item.source_url && (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[10px] text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 mt-1"
                          >
                            <span>Upstream Source</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Pipeline Execution Telemetry */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-400" />
                Pipeline Execution Telemetry
              </h3>

              <div className="space-y-2">
                {timeline.map((stage, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs py-1.5 border-b border-white/5">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span className="text-slate-300">{stage.stage_name}</span>
                    </div>
                    <span className="font-mono text-emerald-400 font-semibold">{stage.duration_ms.toFixed(1)} ms</span>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex items-center justify-between text-xs font-bold text-white">
                <span>Total Pipeline Time:</span>
                <span className="font-mono text-blue-400">{totalPipelineTime.toFixed(1)} ms</span>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Promotion to Knowledge Base Modal */}
      {showPromoteModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 max-w-md w-full space-y-4 bg-slate-900">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              Promote to Verified Knowledge Base
            </h3>
            <p className="text-xs text-slate-300">
              Human verification gate: Once verified, this diagnosis is indexed into active 384-dimensional vector memory to assist future RAG retrievals.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Verified By (Engineer / Tech Lead) *</label>
                <input
                  type="text"
                  required
                  value={verifierName}
                  onChange={(e) => setVerifierName(e.target.value)}
                  placeholder="e.g., Lead QA Engineer"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Verification Notes</label>
                <textarea
                  rows={3}
                  value={verificationNotes}
                  onChange={(e) => setVerificationNotes(e.target.value)}
                  placeholder="Verified patch locally; passes integration test suites."
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {promoteSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle className="w-4 h-4 shrink-0" />
                <span>Successfully promoted and indexed in vector memory!</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowPromoteModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-medium cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={promoting || !verifierName.trim()}
                onClick={handlePromoteToKB}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50 transition-all cursor-pointer"
              >
                {promoting ? 'Indexing Vector...' : 'Confirm & Promote'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
