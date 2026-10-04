/**
 * Centralized API Client for Backend Services
 */

const API_BASE = '/api';

export interface SubmissionResponse {
  id: string;
  title: string;
  raw_content: string;
  input_type: string;
  environment_details?: string | null;
  file_name?: string | null;
  file_size_bytes?: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TriageResult {
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  priority: 'High' | 'Medium' | 'Low';
  affected_component: string;
  confidence: number;
  reasoning: string;
  signals: string[];
}

export interface StackFrame {
  file: string;
  line?: number | null;
  function?: string | null;
  code_context?: string | null;
}

export interface LogAnalysisResult {
  exception_type?: string | null;
  error_message?: string | null;
  failure_point?: string | null;
  affected_code_path?: string | null;
  key_log_signals: string[];
  stack_frames: StackFrame[];
  raw_extracted_facts: string[];
  parsing_notes: string;
}

export interface HistoricalEvidenceItem {
  issue_id: string;
  project: string;
  title: string;
  similarity_score: number;
  classification: string;
  resolution?: string | null;
  fix_patch_summary?: string | null;
  source_url?: string | null;
  component?: string | null;
}

export interface DuplicateDetectionResult {
  is_duplicate: boolean;
  top_matches: HistoricalEvidenceItem[];
  duplicate_threshold: number;
  related_threshold: number;
  summary: string;
}

export interface RootCauseResult {
  hypothesis: string;
  confidence: number;
  observed_facts: string[];
  historical_evidence: string[];
  ai_inference: string[];
  evidence_status: string;
}

export interface RecommendedTest {
  test_type: string;
  description: string;
  test_code_or_command?: string | null;
}

export interface RemediationRecommendation {
  action: string;
  explanation: string;
  affected_area: string;
  implementation_guidance: string;
  supporting_evidence: string[];
  confidence: number;
  recommended_tests: RecommendedTest[];
  code_patch?: string | null;
}

export interface TimelineStage {
  stage_name: string;
  status: string;
  duration_ms: number;
  timestamp: string;
  notes?: string | null;
}

export interface BugAnalysisContext {
  submission_id: string;
  submission: SubmissionResponse;
  triage?: TriageResult | null;
  log_analysis?: LogAnalysisResult | null;
  rag_retrieval: HistoricalEvidenceItem[];
  duplicate_detection?: DuplicateDetectionResult | null;
  root_cause?: RootCauseResult | null;
  remediation?: RemediationRecommendation | null;
  timeline: TimelineStage[];
  errors: string[];
  created_at: string;
  completed_at?: string | null;
}

export interface DistributionCount {
  name: string;
  count: number;
  percentage: number;
}

export interface AnalyticsSummary {
  total_submissions: number;
  completed_analyses: number;
  pending_analyses: number;
  failed_analyses: number;
  verified_kb_entries: number;
  historical_corpus_size: number;
  duplicate_rate_percentage: number;
  severity_distribution: DistributionCount[];
  priority_distribution: DistributionCount[];
  component_distribution: DistributionCount[];
  exception_distribution: DistributionCount[];
  reconciliation_verified: boolean;
}

export interface HistoricalDefect {
  issue_id: string;
  project: string;
  source: string;
  title: string;
  description: string;
  component: string;
  severity: string;
  priority: string;
  status: string;
  resolution: string;
  fix_patch_summary: string;
  source_url: string;
  created_at?: string | null;
}

export interface KBEntryResponse {
  id: string;
  submission_id: string;
  title: string;
  component: string;
  severity: string;
  root_cause: string;
  resolution: string;
  verified_by: string;
  verification_notes: string;
  verified_at: string;
  vector_indexed: boolean;
}

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch('/health');
    return res.json();
  },

  // Submissions
  submitBugText: async (payload: { title: string; raw_content: string; input_type?: string; environment_details?: string }) => {
    const res = await fetch(`${API_BASE}/submissions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Submission failed');
    }
    return res.json() as Promise<SubmissionResponse>;
  },

  submitBugFile: async (formData: FormData) => {
    const res = await fetch(`${API_BASE}/submissions/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json() as Promise<SubmissionResponse>;
  },

  listSubmissions: async (): Promise<SubmissionResponse[]> => {
    const res = await fetch(`${API_BASE}/submissions`);
    return res.json();
  },

  getSubmission: async (id: string): Promise<SubmissionResponse> => {
    const res = await fetch(`${API_BASE}/submissions/${id}`);
    return res.json();
  },

  // Diagnosis
  runDiagnosis: async (submissionId: string): Promise<BugAnalysisContext> => {
    const res = await fetch(`${API_BASE}/diagnosis/run/${submissionId}`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Diagnosis failed');
    }
    return res.json();
  },

  getDiagnosis: async (submissionId: string): Promise<BugAnalysisContext> => {
    const res = await fetch(`${API_BASE}/diagnosis/${submissionId}`);
    if (!res.ok) {
      throw new Error('Diagnosis record not found');
    }
    return res.json();
  },

  // Historical
  listHistoricalDefects: async (params?: { project?: string; severity?: string; search?: string }): Promise<HistoricalDefect[]> => {
    const query = new URLSearchParams();
    if (params?.project) query.set('project', params.project);
    if (params?.severity) query.set('severity', params.severity);
    if (params?.search) query.set('search', params.search);
    const res = await fetch(`${API_BASE}/historical?${query.toString()}`);
    return res.json();
  },

  searchHistorical: async (query: string, top_k = 5): Promise<HistoricalEvidenceItem[]> => {
    const res = await fetch(`${API_BASE}/historical/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k }),
    });
    return res.json();
  },

  // Analytics
  getAnalytics: async (): Promise<AnalyticsSummary> => {
    const res = await fetch(`${API_BASE}/analytics`);
    return res.json();
  },

  // Knowledge Base
  listKBEntries: async (): Promise<KBEntryResponse[]> => {
    const res = await fetch(`${API_BASE}/knowledge-base`);
    return res.json();
  },

  promoteVerifiedBug: async (payload: {
    analysis_id: string;
    verified_by: string;
    verification_notes: string;
    confirmed_root_cause: string;
    confirmed_resolution: string;
  }): Promise<KBEntryResponse> => {
    const res = await fetch(`${API_BASE}/knowledge-base/promote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Promotion failed');
    }
    return res.json();
  },
};
