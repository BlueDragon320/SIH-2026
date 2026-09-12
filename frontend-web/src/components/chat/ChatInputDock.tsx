import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowUp,
  Paperclip,
  Square,
  Sparkles,
  Layers,
  X,
  FileText,
  FileCode,
  FileSpreadsheet,
  Image as ImageIcon
} from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

export const ChatInputDock: React.FC = () => {
  const {
    sendMessage,
    isStreaming,
    stopStreaming,
    selectedModel,
    setSelectedModel,
    ragEnabled,
    setRagEnabled,
    models
  } = useChatStore();

  const [prompt, setPrompt] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [prompt]);

  const handleSend = () => {
    if ((!prompt.trim() && attachments.length === 0) || isStreaming) return;
    sendMessage(prompt.trim(), attachments);
    setPrompt('');
    setAttachments([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments(prev => [...prev, ...newFiles]);
    }
  };

  const removeAttachment = (idx: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== idx));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      setAttachments(prev => [...prev, ...droppedFiles]);
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto w-full select-none">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`glass-dock rounded-2xl p-2.5 transition-all duration-200 ${
          isDragging ? 'border-crimson-500 ring-2 ring-crimson-600/30' : ''
        }`}
      >
        {/* Dismissible Attachment Chips */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 px-2 pb-2.5 border-b border-border/40">
            {attachments.map((file, idx) => {
              const isImg = file.type.startsWith('image/');
              const isCode = file.name.endsWith('.py') || file.name.endsWith('.json') || file.name.endsWith('.sh');
              const isSheet = file.name.endsWith('.xlsx') || file.name.endsWith('.csv');

              return (
                <div
                  key={idx}
                  className="flex items-center gap-1.5 px-2.5 py-1 bg-surface border border-border rounded-lg text-xs font-mono text-text-secondary shadow-sm"
                >
                  {isImg && <ImageIcon className="w-3.5 h-3.5 text-crimson-400" />}
                  {isCode && <FileCode className="w-3.5 h-3.5 text-amber-400" />}
                  {isSheet && <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />}
                  {!isImg && !isCode && !isSheet && <FileText className="w-3.5 h-3.5 text-text-muted" />}

                  <span className="truncate max-w-[150px]">{file.name}</span>
                  <span className="text-[10px] text-text-dim">
                    ({(file.size / 1024).toFixed(0)} KB)
                  </span>

                  <button
                    onClick={() => removeAttachment(idx)}
                    className="p-0.5 text-text-muted hover:text-text-primary rounded"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Input Textarea */}
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder={
            ragEnabled
              ? 'Ask question against air-gapped ChromaDB knowledge base...'
              : selectedModel === 'Auto'
              ? 'Ask anything (Auto-Routes to Coding, Reasoning, Math, or Vision)...'
              : `Message ${selectedModel}...`
          }
          className="w-full bg-transparent border-0 px-3 py-2 text-xs sm:text-sm text-text-primary placeholder:text-text-muted focus:outline-none resize-none font-sans leading-relaxed"
        />

        {/* Bottom Dock Controls */}
        <div className="flex items-center justify-between pt-1 px-1.5 text-xs">
          <div className="flex items-center gap-2">
            {/* Attachment Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 text-text-muted hover:text-text-primary hover:bg-surface rounded-lg transition-colors"
              title="Attach files (PDF, DOCX, CSV, XLSX, PNG, PY)"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* RAG Search Toggle */}
            <button
              onClick={() => setRagEnabled(!ragEnabled)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-mono text-[11px] border transition-colors ${
                ragEnabled
                  ? 'bg-amber-950/50 border-amber-800/60 text-amber-300'
                  : 'bg-surface/60 border-border text-text-muted hover:text-text-secondary'
              }`}
              title="Toggle ChromaDB Vector Knowledge Retrieval"
            >
              <Layers className="w-3 h-3" />
              <span>RAG</span>
            </button>

            {/* Auto-Route / Force Model Toggle */}
            <div className="hidden sm:flex items-center gap-1.5 bg-surface/80 border border-border px-2 py-1 rounded-lg text-[11px] font-mono">
              <Sparkles className="w-3 h-3 text-crimson-500" />
              <select
                value={selectedModel}
                onChange={e => setSelectedModel(e.target.value)}
                className="bg-transparent text-text-primary outline-none cursor-pointer"
              >
                <option value="Auto">⚡ Auto-Route</option>
                {models.filter(m => m.is_installed).map(m => (
                  <option key={m.ollama_tag} value={m.ollama_tag}>
                    {m.name} ({m.ollama_tag})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Send or Stop Generation Button */}
          <div className="flex items-center gap-2">
            {isStreaming ? (
              <button
                onClick={stopStreaming}
                className="p-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl shadow-sm transition-transform active:scale-95"
                title="Stop generation"
              >
                <Square className="w-4 h-4 fill-white" />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!prompt.trim() && attachments.length === 0}
                className="p-2 bg-crimson-600 hover:bg-crimson-500 disabled:opacity-30 disabled:hover:bg-crimson-600 text-white rounded-xl shadow-sm transition-transform active:scale-95"
                title="Send message (Enter)"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
      <div className="text-center pt-2 text-[10px] text-text-dim select-none">
        Workbench Auto-Route operates 100% on-premises. Kernel code execution is isolated via Bubblewrap.
      </div>
    </div>
  );
};
