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

async function handleResponse<T>(res: Response, defaultErrorMsg: string): Promise<T> {
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.toLowerCase().includes('application/json');

  if (!res.ok) {
    let errorDetail = '';
    try {
      const text = await res.text();
      if (isJson) {
        try {
          const json = JSON.parse(text);
          errorDetail = json.detail || json.message || json.error || text;
        } catch {
          errorDetail = text.trim();
        }
      } else {
        // Safe check for HTML response pages (e.g. 502/504 gateway errors)
        if (text.includes('<!DOCTYPE') || text.includes('<html')) {
          errorDetail = `${defaultErrorMsg}: Server returned HTML error (HTTP ${res.status} ${res.statusText || 'Error'})`;
        } else {
          errorDetail = text.trim() || `${defaultErrorMsg} (HTTP ${res.status} ${res.statusText || ''})`.trim();
        }
      }
    } catch {
      errorDetail = `${defaultErrorMsg} (HTTP ${res.status} ${res.statusText || ''})`.trim();
    }
    throw new Error(errorDetail || `${defaultErrorMsg} (HTTP ${res.status})`);
  }

  // When res.ok is true, ensure response is valid JSON and not an HTML SPA fallback
  if (!isJson) {
    const text = await res.text();
    if (text.includes('<!DOCTYPE') || text.includes('<html')) {
      throw new Error(`Expected JSON but received HTML response (HTTP ${res.status}). Verify API rewrite configuration.`);
    }
    try {
      return JSON.parse(text) as T;
    } catch {
      throw new Error(`Expected JSON from server but received non-JSON payload (HTTP ${res.status})`);
    }
  }

  try {
    const text = await res.text();
    return JSON.parse(text) as T;
  } catch {
    throw new Error(`Invalid JSON syntax in server response (HTTP ${res.status})`);
  }
}

export const api = {
  // Health
  getHealth: async (): Promise<any> => {
    const res = await fetch('/health');
    return handleResponse<any>(res, 'Health check failed');
  },

  // Submissions
  submitBugText: async (payload: { title: string; raw_content: string; input_type?: string; environment_details?: string }): Promise<SubmissionResponse> => {
    const res = await fetch(`${API_BASE}/submissions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SubmissionResponse>(res, 'Submission failed');
  },

  submitBugFile: async (formData: FormData): Promise<SubmissionResponse> => {
    const res = await fetch(`${API_BASE}/submissions/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<SubmissionResponse>(res, 'Upload failed');
  },

  listSubmissions: async (): Promise<SubmissionResponse[]> => {
    const res = await fetch(`${API_BASE}/submissions`);
    return handleResponse<SubmissionResponse[]>(res, 'Failed to list submissions');
  },

  getSubmission: async (id: string): Promise<SubmissionResponse> => {
    const res = await fetch(`${API_BASE}/submissions/${id}`);
    return handleResponse<SubmissionResponse>(res, 'Failed to fetch submission');
  },

  // Diagnosis
  runDiagnosis: async (submissionId: string): Promise<BugAnalysisContext> => {
    const res = await fetch(`${API_BASE}/diagnosis/run/${submissionId}`, { method: 'POST' });
    return handleResponse<BugAnalysisContext>(res, 'Diagnosis failed');
  },

  getDiagnosis: async (submissionId: string): Promise<BugAnalysisContext> => {
    const res = await fetch(`${API_BASE}/diagnosis/${submissionId}`);
    return handleResponse<BugAnalysisContext>(res, 'Diagnosis record not found');
  },

  // Historical
  listHistoricalDefects: async (params?: { project?: string; severity?: string; search?: string }): Promise<HistoricalDefect[]> => {
    const query = new URLSearchParams();
    if (params?.project) query.set('project', params.project);
    if (params?.severity) query.set('severity', params.severity);
    if (params?.search) query.set('search', params.search);
    const res = await fetch(`${API_BASE}/historical?${query.toString()}`);
    return handleResponse<HistoricalDefect[]>(res, 'Failed to fetch historical defects');
  },

  searchHistorical: async (query: string, top_k = 5): Promise<HistoricalEvidenceItem[]> => {
    const res = await fetch(`${API_BASE}/historical/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k }),
    });
    return handleResponse<HistoricalEvidenceItem[]>(res, 'Historical search failed');
  },

  // Analytics
  getAnalytics: async (): Promise<AnalyticsSummary> => {
    const res = await fetch(`${API_BASE}/analytics`);
    return handleResponse<AnalyticsSummary>(res, 'Failed to fetch analytics');
  },

  getEvaluationMetrics: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/analytics/evaluation`);
    return handleResponse<any>(res, 'Failed to fetch evaluation metrics');
  },

  // Knowledge Base
  listKBEntries: async (): Promise<KBEntryResponse[]> => {
    const res = await fetch(`${API_BASE}/knowledge-base`);
    return handleResponse<KBEntryResponse[]>(res, 'Failed to fetch knowledge base entries');
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
    return handleResponse<KBEntryResponse>(res, 'Promotion failed');
  },
};

export const apiClient = api;

