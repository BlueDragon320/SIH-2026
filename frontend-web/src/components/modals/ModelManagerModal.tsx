import React, { useState, useEffect } from 'react';
import { X, Download, HardDrive, CheckCircle2, AlertCircle, RefreshCw, Cpu, Tag } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { apiClient } from '../../services/apiClient';

interface ModelManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ModelManagerModal: React.FC<ModelManagerModalProps> = ({ isOpen, onClose }) => {
  const { models, fetchModels } = useChatStore();
  const [pullTag, setPullTag] = useState('');
  const [isPulling, setIsPulling] = useState(false);
  const [pullMsg, setPullMsg] = useState<{ text: string; error?: boolean } | null>(null);
  const [ollamaLib, setOllamaLib] = useState<any[]>([]);

  const loadLibrary = async () => {
    try {
      const data = await apiClient.getOllamaLibrary();
      setOllamaLib(data.models || []);
    } catch {}
  };

  useEffect(() => {
    if (isOpen) {
      fetchModels();
      loadLibrary();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handlePull = async (tagToPull: string) => {
    const tag = tagToPull.trim();
    if (!tag) return;
    setIsPulling(true);
    setPullMsg({ text: `Triggering Ollama pull for ${tag}...` });
    try {
      const res = await apiClient.pullModel(tag);
      if (res.error) {
        setPullMsg({ text: `Failed: ${res.error}`, error: true });
      } else {
        setPullMsg({ text: `Pull started for ${tag} in background.` });
        setTimeout(() => {
          fetchModels();
          loadLibrary();
        }, 3000);
      }
    } catch (e: any) {
      setPullMsg({ text: e.message || 'Pull request failed', error: true });
    } finally {
      setIsPulling(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-surface border border-border rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-surface-subtle">
          <div className="flex items-center gap-2.5">
            <HardDrive className="w-5 h-5 text-crimson-500" />
            <div>
              <h2 className="text-sm font-semibold text-text-primary">Ollama Local Model Manager</h2>
              <p className="text-[11px] text-text-muted">Air-gapped model registry and on-device weights</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pull New Model Bar */}
        <div className="p-4 border-b border-border/80 bg-background/50 space-y-2">
          <label className="text-xs font-medium text-text-secondary">Pull / Download New Model</label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="e.g. qwen2.5-coder:7b, llama3.1:8b, deepseek-r1:7b"
              value={pullTag}
              onChange={e => setPullTag(e.target.value)}
              className="flex-1 bg-surface border border-border px-3 py-1.5 rounded-lg text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:border-crimson-500 font-mono"
            />
            <button
              onClick={() => handlePull(pullTag)}
              disabled={isPulling || !pullTag.trim()}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-crimson-600 hover:bg-crimson-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition-colors"
            >
              {isPulling ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              Pull
            </button>
          </div>

          {/* Quick presets */}
          <div className="flex items-center gap-1.5 pt-1">
            <span className="text-[10px] text-text-muted">Recommended:</span>
            {['qwen2.5-coder:7b', 'llama3.1:8b', 'deepseek-r1:7b', 'moondream:latest'].map(pt => (
              <button
                key={pt}
                onClick={() => setPullTag(pt)}
                className="text-[10px] font-mono px-2 py-0.5 bg-surface hover:bg-surface-hover border border-border rounded text-text-secondary hover:text-crimson-400 transition-colors"
              >
                {pt}
              </button>
            ))}
          </div>

          {pullMsg && (
            <div
              className={`text-xs px-2.5 py-1.5 rounded border ${
                pullMsg.error
                  ? 'bg-rose-950/40 border-rose-900/60 text-rose-300'
                  : 'bg-emerald-950/40 border-emerald-900/60 text-emerald-300'
              }`}
            >
              {pullMsg.text}
            </div>
          )}
        </div>

        {/* Installed Models List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-text-muted">Registered Models</span>
            <button
              onClick={() => {
                fetchModels();
                loadLibrary();
              }}
              className="text-xs text-text-muted hover:text-text-primary flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" />
              Refresh
            </button>
          </div>

          <div className="grid grid-cols-1 gap-2.5">
            {models.map(m => {
              const diskInfo = ollamaLib.find(
                om => om.name === m.ollama_tag || om.name?.startsWith(m.ollama_tag.split(':')[0])
              );
              const sizeGb = diskInfo?.size ? (diskInfo.size / (1024 * 1024 * 1024)).toFixed(2) : null;
              const quant = diskInfo?.details?.quantization_level || 'Q4_K_M';

              return (
                <div
                  key={m.name}
                  className="bg-surface-subtle border border-border rounded-lg p-3 flex items-start justify-between gap-3 hover:border-border-strong transition-colors"
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-text-primary">{m.name}</span>
                      <code className="text-[11px] font-mono text-crimson-400 bg-crimson-950/40 px-1.5 py-0.5 rounded border border-crimson-900/40">
                        {m.ollama_tag}
                      </code>
                      {m.is_installed ? (
                        <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-900/40 font-medium">
                          <CheckCircle2 className="w-2.5 h-2.5" /> Installed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] text-text-muted bg-surface px-1.5 py-0.5 rounded border border-border">
                          Not Installed
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-text-secondary leading-relaxed">{m.description}</p>
                    <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[10px] text-text-muted font-mono">
                      <span className="flex items-center gap-1">
                        <Cpu className="w-3 h-3 text-text-muted" /> ~{m.vram_gb} GB VRAM
                      </span>
                      {sizeGb && <span>• Size: {sizeGb} GB</span>}
                      {quant && <span>• Quant: {quant}</span>}
                    </div>
                  </div>

                  {!m.is_installed && (
                    <button
                      onClick={() => handlePull(m.ollama_tag)}
                      className="px-2.5 py-1 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded text-xs flex items-center gap-1.5 shrink-0"
                    >
                      <Download className="w-3 h-3" />
                      Download
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
