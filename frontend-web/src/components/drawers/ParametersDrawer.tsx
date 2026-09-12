import React from 'react';
import { X, Sliders, RotateCcw, Sparkles, BookOpen, ShieldAlert, Binary } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

const PRESETS = [
  {
    name: 'Code Specialist',
    icon: '💻',
    prompt: 'You are an expert Python engineer and systems architect in an air-gapped environment. Provide clean, modular, production-ready code with complete type annotations, docstrings, and robust error handling.',
    temp: 0.1,
    numCtx: 16384,
  },
  {
    name: 'Industrial Auditor',
    icon: '🛡️',
    prompt: 'You are a Senior Quality Assurance and Compliance Auditor specialized in ISO 9001 and defense manufacturing. Evaluate component tolerances rigorously, structure formal findings, and verify safety margins against engineering standards.',
    temp: 0.2,
    numCtx: 8192,
  },
  {
    name: 'Math & Physics Deriver',
    icon: '📐',
    prompt: 'You are a theoretical physicist and applied mathematician. Derive formulas step-by-step using LaTeX notation. State all assumptions clearly and verify dimensional consistency.',
    temp: 0.1,
    numCtx: 8192,
  },
  {
    name: 'General Engineering Assistant',
    icon: '⚡',
    prompt: 'You are an expert autonomous engineering agent operating in a strictly air-gapped environment. Answer directly, concisely, and with high technical precision without disclaimers.',
    temp: 0.3,
    numCtx: 4096,
  }
];

export const ParametersDrawer: React.FC = () => {
  const { params, updateParams, resetParams, isParamsOpen, setParamsOpen } = useChatStore();

  if (!isParamsOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-80 sm:w-96 bg-surface border-l border-border shadow-2xl flex flex-col animate-slide-in-right">
      {/* Drawer Header */}
      <div className="p-4 border-b border-border flex items-center justify-between bg-surface-subtle">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-crimson-500" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-primary">
            Inference Parameters
          </h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={resetParams}
            className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded text-[11px] flex items-center gap-1 mr-1"
            title="Reset to defaults"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
          <button
            onClick={() => setParamsOpen(false)}
            className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        {/* Presets */}
        <div className="space-y-1.5">
          <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">
            Engineer Personas
          </label>
          <div className="grid grid-cols-2 gap-1.5">
            {PRESETS.map(p => (
              <button
                key={p.name}
                onClick={() => {
                  updateParams({
                    systemPrompt: p.prompt,
                    temperature: p.temp,
                    numCtx: p.numCtx,
                  });
                }}
                className="flex items-center gap-1.5 p-2 bg-surface-subtle hover:bg-surface-hover border border-border rounded-lg text-left transition-colors"
              >
                <span>{p.icon}</span>
                <span className="text-[11px] font-medium text-text-secondary truncate">{p.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* System Prompt */}
        <div className="space-y-1.5">
          <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted flex items-center justify-between">
            <span>System Prompt</span>
            <span className="text-[9px] text-text-dim">Per-chat instruction</span>
          </label>
          <textarea
            rows={4}
            value={params.systemPrompt}
            onChange={e => updateParams({ systemPrompt: e.target.value })}
            className="w-full bg-background border border-border rounded-lg p-2.5 text-xs text-text-primary focus:outline-none focus:border-crimson-500 font-sans leading-relaxed"
            placeholder="Set autonomous agent instructions..."
          />
        </div>

        {/* Temperature */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Temperature</label>
            <span className="font-mono text-crimson-400 font-medium">{params.temperature.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="1.0"
            step="0.05"
            value={params.temperature}
            onChange={e => updateParams({ temperature: parseFloat(e.target.value) })}
            className="w-full accent-crimson-600 bg-background h-1.5 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between text-[9px] text-text-dim font-mono">
            <span>Deterministic (0.0)</span>
            <span>Creative (1.0)</span>
          </div>
        </div>

        {/* Context Window (num_ctx) */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Context Window (num_ctx)</label>
            <span className="font-mono text-crimson-400 font-medium">{params.numCtx} tokens</span>
          </div>
          <select
            value={params.numCtx}
            onChange={e => updateParams({ numCtx: parseInt(e.target.value) })}
            className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-text-primary text-xs focus:outline-none focus:border-crimson-500 font-mono"
          >
            <option value={2048}>2,048 tokens (Ultra-low VRAM)</option>
            <option value={4096}>4,096 tokens (Default standard)</option>
            <option value={8192}>8,192 tokens (Large documents)</option>
            <option value={16384}>16,384 tokens (Full code repositories)</option>
            <option value={32768}>32,768 tokens (Max context capacity)</option>
          </select>
        </div>

        {/* Top P & Top K */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Top P</label>
            <input
              type="number"
              step="0.05"
              min="0"
              max="1"
              value={params.topP}
              onChange={e => updateParams({ topP: parseFloat(e.target.value) || 0.9 })}
              className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-primary font-mono"
            />
          </div>
          <div className="space-y-1">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Top K</label>
            <input
              type="number"
              min="1"
              max="100"
              value={params.topK}
              onChange={e => updateParams({ topK: parseInt(e.target.value) || 40 })}
              className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-primary font-mono"
            />
          </div>
        </div>

        {/* Repeat Penalty & Seed */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Repeat Penalty</label>
            <input
              type="number"
              step="0.05"
              min="1.0"
              max="2.0"
              value={params.repeatPenalty}
              onChange={e => updateParams({ repeatPenalty: parseFloat(e.target.value) || 1.1 })}
              className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-primary font-mono"
            />
          </div>
          <div className="space-y-1">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Seed (Optional)</label>
            <input
              type="number"
              placeholder="Random"
              value={params.seed === null ? '' : params.seed}
              onChange={e => updateParams({ seed: e.target.value ? parseInt(e.target.value) : null })}
              className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-primary font-mono"
            />
          </div>
        </div>

        {/* JSON Mode & Keep Alive */}
        <div className="space-y-3 pt-2 border-t border-border/60">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium text-text-primary">JSON Mode</span>
              <p className="text-[10px] text-text-muted">Enforce structured JSON output format</p>
            </div>
            <input
              type="checkbox"
              checked={params.formatJson}
              onChange={e => updateParams({ formatJson: e.target.checked })}
              className="w-4 h-4 accent-crimson-600 rounded cursor-pointer"
            />
          </div>

          <div className="space-y-1">
            <label className="font-mono text-[10px] uppercase tracking-wider text-text-muted">Keep Alive Memory Retention</label>
            <select
              value={params.keepAlive}
              onChange={e => updateParams({ keepAlive: e.target.value })}
              className="w-full bg-background border border-border rounded-lg px-2.5 py-1.5 text-text-primary text-xs focus:outline-none focus:border-crimson-500 font-mono"
            >
              <option value="5m">5 minutes (Frees VRAM quickly)</option>
              <option value="15m">15 minutes (Standard)</option>
              <option value="1h">1 hour</option>
              <option value="-1">Indefinite (Pin in GPU VRAM)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};
