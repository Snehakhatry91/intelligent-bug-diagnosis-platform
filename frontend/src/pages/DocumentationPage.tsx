import React from 'react';
import { 
  BookOpen, 
  Layers, 
  Cpu, 
  Database, 
  ShieldCheck, 
  Code,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';

export const DocumentationPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto animate-fade-in pb-16 text-slate-300 text-xs leading-relaxed">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-indigo-400" />
          Technical Architecture & Specification Documentation
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Detailed engineering documentation of the multi-agent diagnostic DAG, RAG vector indexing, and anti-hallucination policies.
        </p>
      </div>

      {/* 1. Multi-Agent DAG Flow */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-blue-400" />
          1. Multi-Agent Orchestration Directed Acyclic Graph (DAG)
        </h2>
        <p>
          The platform structures defect resolution as an autonomous multi-stage workflow where each specialized agent consumes the strongly-typed canonical <code className="text-blue-300 font-mono">BugAnalysisContext</code> and enriches it with domain-specific diagnostic signals.
        </p>
        <pre className="p-4 rounded-xl bg-slate-950 font-mono text-[11px] text-blue-300 border border-white/5 overflow-x-auto leading-relaxed">
{`Bug Submission (Raw Text / Stack Trace / File Upload)
       │
       ▼
[Agent 1: Triage Agent]
       ├── Classifies Severity (Critical, High, Medium, Low) & Priority
       └── Evaluates dynamic confidence and extracts empirical crash signals
       │
       ▼
[Agent 2: Log Analysis Agent]
       ├── Deterministic structural parsing of stack frames & lines
       └── Extracts exception type, error description, and failure point
       │
       ▼
[Supporting Service: RAG Retrieval Engine]
       ├── Generates 384-dimensional dense semantic query vectors
       └── Cosine search against Mozilla, Apache, & Eclipse historical corpora
       │
       ▼
[Agent 3: Duplicate Detection Agent]
       ├── Enforces single central similarity policy (>= 0.82 duplicate cutoff)
       └── Categorizes candidates as Duplicate, Related Issue, or Weak Match
       │
       ▼
[Agent 4: Root Cause Agent]
       ├── Four-tier attribution: Observed Facts, Historical Evidence, Inference
       └── Formulates anti-hallucinated failure hypothesis
       │
       ▼
[Agent 5: Remediation Agent]
       └── Generates actionable code patch snippets and automated test plans`}
        </pre>
      </div>

      {/* 2. Single Centralized Similarity Policy */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-400" />
          2. Single Centralized Vector Similarity Policy
        </h2>
        <p>
          To prevent threshold fragmentation, exactly one similarity policy is defined in <code className="text-purple-300 font-mono">backend/config.py</code> and used across all retrieval, duplicate detection, and evaluation scripts:
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border border-white/10 rounded-xl overflow-hidden">
            <thead className="bg-slate-900 text-slate-300 font-semibold border-b border-white/10">
              <tr>
                <th className="py-2.5 px-4">Cosine Similarity Band</th>
                <th className="py-2.5 px-4">Classification</th>
                <th className="py-2.5 px-4">System Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-300">
              <tr>
                <td className="py-2.5 px-4 font-mono text-rose-400 font-bold">&ge; 0.82</td>
                <td className="py-2.5 px-4 font-semibold text-white">Likely Duplicate</td>
                <td className="py-2.5 px-4">Flags as existing defect; links historical resolution and patch.</td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 font-mono text-amber-400 font-bold">0.65 &ndash; 0.81</td>
                <td className="py-2.5 px-4 font-semibold text-white">Related Issue</td>
                <td className="py-2.5 px-4">Provides precedent evidence; does NOT claim duplicate identity.</td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 font-mono text-slate-400 font-bold">0.45 &ndash; 0.64</td>
                <td className="py-2.5 px-4 font-semibold text-white">Weak Match</td>
                <td className="py-2.5 px-4">Weak architectural affinity; presented with low confidence.</td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 font-mono text-slate-500 font-bold">&lt; 0.45</td>
                <td className="py-2.5 px-4 font-semibold text-slate-500">Insufficient Evidence</td>
                <td className="py-2.5 px-4">Filtered out; explicitly returns "Insufficient historical evidence found".</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. Anti-Hallucination Guardrails */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          3. Anti-Hallucination Four-Tier Attribution
        </h2>
        <p>
          The system strictly delineates four levels of epistemic certainty in diagnostic findings:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-900 border-l-4 border-blue-500">
            <span className="font-bold text-white block mb-1">Tier 1: Observed Facts</span>
            Deterministic data extracted directly from stack frames, line numbers, and log headers.
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900 border-l-4 border-purple-500">
            <span className="font-bold text-white block mb-1">Tier 2: Historical Evidence</span>
            Actual precedent records retrieved from Mozilla, Apache, and Eclipse meeting the &ge; 0.45 similarity threshold.
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900 border-l-4 border-amber-500">
            <span className="font-bold text-white block mb-1">Tier 3: AI Inference</span>
            Hypothesized causal mechanisms clearly labelled as inference rather than confirmed truth.
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900 border-l-4 border-emerald-500">
            <span className="font-bold text-white block mb-1">Tier 4: Fix Recommendation</span>
            Actionable code patches, configuration guards, and automated test plans.
          </div>
        </div>
      </div>

      {/* 4. Historical Dataset Provenance */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          4. Historical Dataset Provenance
        </h2>
        <p>
          The platform incorporates verified historical defect records from three major open-source ecosystems:
        </p>
        <ul className="list-disc list-inside space-y-1.5 text-slate-300">
          <li><strong>Mozilla Bugzilla</strong>: Curated crash records with source provenance from Firefox, Necko HTTP channel, and Spidermonkey JS.</li>
          <li><strong>Apache Software Foundation Jira</strong>: Concurrency, connection pool, and OOM issues from Kafka, Cassandra, Lucene, and Tomcat.</li>
          <li><strong>Eclipse Foundation Bugzilla</strong>: Deadlock, UI threading, and memory leak defects from Platform UI, JDT, and Equinox OSGi.</li>
        </ul>
      </div>

      {/* 5. Reasoning Engine & Vector Architecture */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Code className="w-4 h-4 text-amber-400" />
          5. Reasoning Engine & Vector Architecture
        </h2>
        <p>
          The platform combines transformer-based semantic retrieval with deterministic heuristic reasoning for reproducible offline diagnosis. Optional local Ollama-based LLM assistance (<code className="text-amber-300 font-mono">llama3:8b</code>) can be configured where supported.
        </p>
        <p className="text-slate-400">
          <strong className="text-slate-200">Current Evaluation Implementation:</strong> Historical defect embeddings are stored in a persistent local vector index (<code className="text-cyan-300 font-mono">rag/vector_index.pkl</code>) and compared using cosine similarity via NumPy.<br />
          <strong className="text-slate-200">Production Scaling Option:</strong> The decoupled vector interface can be migrated to PostgreSQL with pgvector or distributed vector databases (e.g. Qdrant) for enterprise deployments.
        </p>
      </div>
    </div>
  );
};
