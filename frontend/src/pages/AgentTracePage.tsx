import { useState, useEffect } from 'react';
import { Sparkles, Brain, Shield, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { AgentNode, AGENT_PIPELINE } from '../components/cards/AgentNode';
import type { AgentStep } from '../types';

export const AgentTracePage = () => {
  const [status, setStatus] = useState<'idle' | 'running' | 'complete'>('idle');
  const [activeStep, setActiveStep] = useState(0);
  const [steps, setSteps] = useState<AgentStep[]>(AGENT_PIPELINE);

  useEffect(() => {
    if (status !== 'running') return;
    const interval = setInterval(() => {
      setActiveStep(prev => {
        if (prev >= steps.length - 1) {
          setStatus('complete');
          toast.success('Agent orchestration complete! Recommendations generated.');
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 1200);
    return () => clearInterval(interval);
  }, [status, steps.length]);

  useEffect(() => {
    setSteps(AGENT_PIPELINE.map((s, i) => ({
      ...s,
      status: status === 'complete' ? 'complete' : status === 'running' && i <= activeStep ? (i === activeStep ? 'running' : 'complete') : 'idle',
    })));
  }, [status, activeStep]);

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Agent Orchestration Console"
        description="Visualize multi-agent LangGraph workflow execution, node status, and reasoning traces in real-time."
        actions={
          <button 
            onClick={() => { setStatus('running'); setActiveStep(0); }} 
            disabled={status === 'running'} 
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-blue-400 disabled:to-indigo-400 text-white text-sm font-semibold rounded-lg flex items-center gap-2 shadow transition-all duration-150"
          >
            <Sparkles className="h-4 w-4" /> {status === 'running' ? 'Running Agent Chain...' : 'Trigger Agent Chain'}
          </button>
        }
      />

      {/* Decision Workflow Overview Bar */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
        <h3 className="font-bold text-sm text-gray-800 dark:text-gray-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Brain className="h-4 w-4 text-blue-500" /> Planner Decision Engine Workflow
        </h3>
        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-gray-500">
          <span className="px-3 py-1.5 bg-gray-50 dark:bg-gray-800 border border-gray-250 dark:border-gray-705 rounded-lg text-gray-800 dark:text-gray-200">
            Receive Account Context
          </span>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <span className="px-3 py-1.5 bg-gray-50 dark:bg-gray-800 border border-gray-250 dark:border-gray-705 rounded-lg text-gray-800 dark:text-gray-200">
            Analyze Health & Transcripts
          </span>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <span className="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg text-blue-600 dark:text-blue-400 font-bold">
            Determine Graph Routing
          </span>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <span className="px-3 py-1.5 bg-gray-50 dark:bg-gray-800 border border-gray-250 dark:border-gray-705 rounded-lg text-gray-800 dark:text-gray-200">
            Execute Target Agents
          </span>
          <ArrowRight className="h-4 w-4 text-gray-400" />
          <span className="px-3 py-1.5 bg-gray-50 dark:bg-gray-800 border border-gray-250 dark:border-gray-705 rounded-lg text-gray-800 dark:text-gray-200">
            Synthesize Recommendations
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Execution Log Stream */}
        <div className="bg-gray-950 border border-gray-900 text-gray-100 rounded-xl p-5 font-mono text-xs space-y-3 flex flex-col h-[500px]">
          <div className="flex items-center justify-between border-b border-gray-900 pb-2">
            <span className="text-gray-500 font-bold flex items-center gap-1.5">
              <Shield className="h-4 w-4 text-indigo-500" /> ORCHESTRATOR STREAM
            </span>
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          </div>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            <p className="text-gray-400">&gt; Initializing LangGraph builder pipeline...</p>
            <p className="text-gray-400">&gt; Connection established with SQLite and local vector indexes.</p>
            {status === 'running' && steps.slice(0, activeStep + 1).map((s, i) => (
              <div key={i} className="space-y-1">
                <p className="text-blue-400">&gt; [{s.name}] Executing node...</p>
                <p className="text-gray-300 ml-3">&gt;&gt; Input: {s.desc}</p>
                {i < activeStep && (
                  <p className="text-green-450 ml-3 font-semibold">&gt;&gt; Success: {s.resultSummary}</p>
                )}
              </div>
            ))}
            {status === 'complete' && (
              <div className="space-y-1">
                <p className="text-green-400 font-bold">&gt; [Planner] Graph processing completed successfully.</p>
                <p className="text-green-400">&gt; 3 prioritized next best actions written back to recommendations database.</p>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Connected Node Flow */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100">Live Agent Collaboration Graph</h3>
            <div className="flex gap-2 text-xs">
              <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 bg-blue-500 rounded-full" /> Running</span>
              <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 bg-green-500 rounded-full" /> Complete</span>
            </div>
          </div>
          <div className="space-y-1 max-w-xl mx-auto">
            {steps.map((step, idx) => (
              <AgentNode
                key={step.name}
                step={step}
                index={idx}
                isLast={idx === steps.length - 1}
                isActive={status === 'running' && activeStep === idx}
                isComplete={status === 'complete' || (status === 'running' && activeStep > idx)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
