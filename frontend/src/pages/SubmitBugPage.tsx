import React, { useState } from 'react';
import { 
  Upload, 
  FileText, 
  Terminal, 
  FileCode, 
  Send, 
  AlertCircle, 
  CheckCircle,
  FileCheck,
  X
} from 'lucide-react';
import { api } from '../api/client';

interface SubmitBugProps {
  onSubmissionComplete: (submissionId: string) => void;
}

export const SubmitBugPage: React.FC<SubmitBugProps> = ({ onSubmissionComplete }) => {
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [title, setTitle] = useState('');
  const [inputType, setInputType] = useState('bug_report');
  const [environmentDetails, setEnvironmentDetails] = useState('');
  const [rawContent, setRawContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sampleTemplates = [
    {
      label: 'Java NPE Stack Trace',
      title: 'NullPointerException in OrderProcessingService during checkout',
      type: 'stack_trace',
      env: 'Production JDK 17, Spring Boot 3.1.2',
      content: 'java.lang.NullPointerException: Cannot invoke "com.store.payment.PaymentMethod.getToken()" because "paymentMethod" is null\n\tat com.store.order.OrderProcessingService.executePayment(OrderProcessingService.java:142)\n\tat com.store.order.OrderProcessingService.processOrder(OrderProcessingService.java:88)\n\tat com.store.web.CheckoutController.submitCheckout(CheckoutController.java:54)',
    },
    {
      label: 'PostgreSQL Deadlock Log',
      title: 'Database connection pool exhausted and deadlock detected on PostgreSQL writer',
      type: 'error_log',
      env: 'PostgreSQL 15 Cluster, HikariCP max-pool-size=50',
      content: '2026-10-05 00:15:32.411 [http-nio-8080-exec-12] ERROR org.postgresql.core.v3.ConnectionFactoryImpl - Connection refused to PostgreSQL server at 10.0.4.12:5432\norg.postgresql.util.PSQLException: Connection to 10.0.4.12:5432 refused.\n2026-10-05 00:15:33.002 [HikariPool-1 housekeeper] WARN com.zaxxer.hikari.pool.HikariPool - ConnectionPool saturation: 50 connections active, 12 waiting, deadlock detected in thread pool.',
    },
    {
      label: 'JWT Auth Expiration',
      title: 'JWT Bearer Token expired returning 401 Unauthorized during API sync',
      type: 'error_log',
      env: 'Kong Gateway 3.4, Node.js JWT verifier',
      content: '2026-10-05T00:22:15.890Z [api-gateway] WARN auth.jwt.validator - TokenExpiredError: jwt expired\n401 Unauthorized: Authorization header token has expired.\nRequest headers: {"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}',
    },
  ];

  const handleApplyTemplate = (tmpl: any) => {
    setTitle(tmpl.title);
    setInputType(tmpl.type);
    setEnvironmentDetails(tmpl.env);
    setRawContent(tmpl.content);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      // 5MB limit
      if (file.size > 5 * 1024 * 1024) {
        setError('File exceeds maximum allowed size of 5 MB.');
        setSelectedFile(null);
        return;
      }
      const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
      if (!['.txt', '.log', '.md', '.json'].includes(ext)) {
        setError(`File extension '${ext}' not allowed. Allowed: .txt, .log, .md, .json`);
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError(null);
      if (!title) {
        setTitle(`Defect Log: ${file.name}`);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let subResponse;
      if (activeTab === 'text') {
        if (!title.trim() || title.length < 3) {
          throw new Error('Title must be at least 3 characters.');
        }
        if (!rawContent.trim() || rawContent.length < 5) {
          throw new Error('Content must be at least 5 characters.');
        }
        subResponse = await api.submitBugText({
          title,
          raw_content: rawContent,
          input_type: inputType,
          environment_details: environmentDetails || undefined,
        });
      } else {
        if (!selectedFile) {
          throw new Error('Please select a file to upload.');
        }
        const formData = new FormData();
        formData.append('file', selectedFile);
        if (title.trim()) formData.append('title', title);
        if (environmentDetails.trim()) formData.append('environment_details', environmentDetails);

        subResponse = await api.submitBugFile(formData);
      }

      onSubmissionComplete(subResponse.id);
    } catch (err: any) {
      setError(err.message || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Submit Defect for Diagnosis</h1>
        <p className="text-xs text-slate-400 mt-1">
          Ingest raw defect reports, Java/Python stack traces, system crash logs, or upload files up to 5MB.
        </p>
      </div>

      {/* Quick Template Fill Buttons */}
      <div className="glass-panel p-4 rounded-xl border border-white/10 space-y-2">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Quick Load Sample Defect Scenarios
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleTemplates.map((t, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyTemplate(t)}
              className="px-3 py-1.5 rounded-lg text-xs bg-slate-800/80 hover:bg-blue-600/30 border border-white/10 hover:border-blue-500/40 text-slate-300 hover:text-white transition-all"
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex gap-2 border-b border-white/10 pb-3">
        <button
          onClick={() => setActiveTab('text')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'text'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
              : 'bg-slate-900/60 text-slate-400 hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          Direct Text / Stack Trace / Log
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'file'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
              : 'bg-slate-900/60 text-slate-400 hover:text-white'
          }`}
        >
          <Upload className="w-4 h-4" />
          File Upload (Max 5 MB)
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-2xl border border-white/10 space-y-5">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">
            Defect Title or Incident Summary *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., NullPointerException in PaymentService during checkout"
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Input Category
            </label>
            <select
              value={inputType}
              onChange={(e) => setInputType(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="bug_report">General Bug Report</option>
              <option value="stack_trace">Crash Stack Trace</option>
              <option value="error_log">System / Server Error Log</option>
              <option value="file_upload">Uploaded Defect File</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Environment / System Context (Optional)
            </label>
            <input
              type="text"
              value={environmentDetails}
              onChange={(e) => setEnvironmentDetails(e.target.value)}
              placeholder="e.g., JDK 17, PostgreSQL 15, Spring Boot, Production"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
        </div>

        {activeTab === 'text' ? (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Raw Defect Content / Stack Trace / Error Stream *
            </label>
            <textarea
              required
              rows={10}
              value={rawContent}
              onChange={(e) => setRawContent(e.target.value)}
              placeholder="Paste full stack trace, exception dump, or defect report text here..."
              className="w-full px-4 py-3 rounded-xl bg-slate-950 font-mono text-xs text-slate-200 border border-white/10 focus:outline-none focus:border-blue-500 transition-colors leading-relaxed"
            />
          </div>
        ) : (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Defect File (.txt, .log, .md, .json - Maximum 5 MB) *
            </label>
            <div className="border-2 border-dashed border-white/10 hover:border-blue-500/50 rounded-2xl p-8 text-center bg-slate-950/40 transition-colors">
              {selectedFile ? (
                <div className="flex flex-col items-center gap-2 text-xs text-slate-300">
                  <FileCheck className="w-8 h-8 text-emerald-400" />
                  <span className="font-semibold text-white">{selectedFile.name}</span>
                  <span className="text-[11px] text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                  <button
                    type="button"
                    onClick={() => setSelectedFile(null)}
                    className="text-xs text-rose-400 hover:text-rose-300 mt-2 flex items-center gap-1"
                  >
                    <X className="w-3.5 h-3.5" /> Remove file
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer flex flex-col items-center gap-3">
                  <Upload className="w-8 h-8 text-slate-500 hover:text-blue-400 transition-colors" />
                  <span className="text-xs text-slate-300 font-medium">
                    Click to select or drag and drop defect log file
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Supports .txt, .log, .md, .json up to 5 MB
                  </span>
                  <input
                    type="file"
                    accept=".txt,.log,.md,.json"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              )}
            </div>
          </div>
        )}

        <div className="pt-2 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Enforces strict zero-execution policy & null-byte sanitization
          </span>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-xs shadow-lg shadow-blue-500/25 flex items-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
          >
            {loading ? (
              <span>Submitting...</span>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Submit & Run Diagnosis</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
