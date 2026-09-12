import React from 'react';
import { Terminal, FileSpreadsheet, FileText, Search, ShieldCheck, Sparkles, ArrowRight } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

export const HeroEmptyState: React.FC = () => {
  const { sendMessage } = useChatStore();

  const quickActions = [
    {
      icon: Terminal,
      title: 'Python Sandbox Execution',
      desc: 'Write and verify a sensor tolerance checker script inside Bubblewrap sandbox.',
      prompt: 'Write a Python script to validate sensor tolerance readings from CSV, compute mean variance, and run it in the isolated sandbox.',
      badge: 'Code Sandbox'
    },
    {
      icon: FileSpreadsheet,
      title: 'Audited Spreadsheet (.xlsx)',
      desc: 'Generate multi-component tolerance calculation sheet with live Excel formulas.',
      prompt: 'Create an audited Excel spreadsheet for industrial valve and pump tolerances with live calculation formulas (=AVERAGE, =MAX) and PASS/FAIL thresholds.',
      badge: 'OpenPyXL'
    },
    {
      icon: FileText,
      title: 'Metrology Scan Ingestion (.docx)',
      desc: 'Synthesize findings into an official engineering clearance Approval Note.',
      prompt: 'Draft an official ISO 9001 quality clearance approval note in docx format for industrial turbine blade inspection with findings and recommendations.',
      badge: 'Docx Generator'
    },
    {
      icon: Search,
      title: 'SOP Knowledge Search (ChromaDB)',
      desc: 'Query local vector store for air-gapped SOPs and ISO maintenance clauses.',
      prompt: 'Search the local air-gapped knowledge base for turbine blade tip clearance tolerances according to SOP-04 and defense material procurement protocols.',
      badge: 'Hybrid RAG'
    }
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-3xl mx-auto space-y-8 select-none animate-fade-in">
      {/* Brand & Headline */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-crimson-950/40 border border-crimson-800/50 text-crimson-400 text-xs font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-crimson-500 animate-pulse"></span>
          <span>Zero-Egress Sovereign Workspace</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
          Engineering Intelligence for{' '}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-crimson-400 to-rose-600">
            Air-Gapped Operations
          </span>
        </h1>

        <p className="text-text-secondary text-xs sm:text-sm max-w-xl mx-auto leading-relaxed">
          High-performance local multi-model orchestration with real-time token streaming, isolated kernel code execution, and cryptographic deliverable verification.
        </p>
      </div>

      {/* 4 Quick Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
        {quickActions.map((action, idx) => {
          const Icon = action.icon;
          return (
            <button
              key={idx}
              onClick={() => sendMessage(action.prompt)}
              className="group p-4 bg-surface hover:bg-surface-hover border border-border hover:border-crimson-600/40 rounded-xl transition-all duration-200 shadow-sm flex flex-col justify-between space-y-3 cursor-pointer"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="p-2 bg-background rounded-lg border border-border group-hover:border-crimson-600/30 transition-colors">
                    <Icon className="w-4 h-4 text-crimson-500 group-hover:scale-110 transition-transform" />
                  </div>
                  <span className="text-[10px] font-mono text-text-muted bg-surface-subtle px-2 py-0.5 rounded border border-border">
                    {action.badge}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-text-primary group-hover:text-crimson-400 transition-colors">
                  {action.title}
                </h3>
                <p className="text-[11px] text-text-muted leading-relaxed">
                  {action.desc}
                </p>
              </div>

              <div className="flex items-center gap-1 text-[11px] text-crimson-500 font-medium group-hover:translate-x-0.5 transition-transform pt-1">
                <span>Dispatch prompt</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
