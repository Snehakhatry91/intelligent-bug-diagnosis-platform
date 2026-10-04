import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { SubmitBugPage } from './pages/SubmitBugPage';
import { AnalysisResultsPage } from './pages/AnalysisResultsPage';
import { HistoricalDefectsPage } from './pages/HistoricalDefectsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DocumentationPage } from './pages/DocumentationPage';
import { api } from './api/client';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeSubmissionId, setActiveSubmissionId] = useState<string | null>(null);

  const handleSelectSubmission = (id: string) => {
    setActiveSubmissionId(id);
    setCurrentTab('results');
  };

  const handleSubmissionComplete = (id: string) => {
    setActiveSubmissionId(id);
    setCurrentTab('results');
  };

  const handleTriggerDemo = async (scenario: any) => {
    try {
      const sub = await api.submitBugText({
        title: scenario.title,
        raw_content: scenario.content,
        input_type: 'bug_report',
        environment_details: 'Synthetic Demonstration Benchmark Environment',
      });
      setActiveSubmissionId(sub.id);
      setCurrentTab('results');
    } catch (e: any) {
      alert(`Demo trigger failed: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#080b11] text-slate-100 flex flex-col font-sans">
      <Navbar 
        currentTab={currentTab} 
        setCurrentTab={setCurrentTab} 
        activeSubmissionId={activeSubmissionId} 
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {currentTab === 'dashboard' && (
          <DashboardPage
            onSelectSubmission={handleSelectSubmission}
            onNavigateSubmit={() => setCurrentTab('submit')}
            onTriggerDemo={handleTriggerDemo}
          />
        )}

        {currentTab === 'submit' && (
          <SubmitBugPage
            onSubmissionComplete={handleSubmissionComplete}
          />
        )}

        {currentTab === 'results' && (
          <AnalysisResultsPage
            submissionId={activeSubmissionId}
            onNavigateSubmit={() => setCurrentTab('submit')}
          />
        )}

        {currentTab === 'historical' && <HistoricalDefectsPage />}

        {currentTab === 'analytics' && <AnalyticsPage />}

        {currentTab === 'kb' && <KnowledgeBasePage />}

        {currentTab === 'eval' && <EvaluationPage />}

        {currentTab === 'docs' && <DocumentationPage />}
      </main>

      {/* Enterprise Footer */}
      <footer className="glass-panel border-t border-white/5 py-6 px-8 mt-auto text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="text-slate-400 font-semibold">Intelligent Bug Diagnosis Platform</span>
            <span className="mx-2">&bull;</span>
            <span>Infosys Internship Evaluation Project</span>
          </div>
          <div>
            <span>Copyright &copy; 2025 Vidzai Digital. MIT License.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
