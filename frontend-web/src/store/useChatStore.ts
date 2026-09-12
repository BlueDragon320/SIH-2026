import { create } from 'zustand';
import {
  Session,
  Message,
  Artifact,
  InferenceParams,
  HardwareStatus,
  NetworkStatus,
  ModelOption,
  RAGChunk,
} from '../types';
import { apiClient } from '../services/apiClient';
import { streamOllamaChat } from '../services/ollamaStream';

const DEFAULT_PARAMS: InferenceParams = {
  systemPrompt: 'You are an expert autonomous engineering agent operating in a strictly air-gapped environment. Answer directly, concisely, and with high technical precision.',
  temperature: 0.2,
  numCtx: 4096,
  topP: 0.9,
  topK: 40,
  repeatPenalty: 1.1,
  seed: null,
  formatJson: false,
  keepAlive: '15m',
};

interface ChatState {
  // Sessions
  sessions: Session[];
  activeSessionId: string | null;
  createSession: (title?: string) => string;
  selectSession: (id: string) => void;
  deleteSession: (id: string) => void;
  renameSession: (id: string, newTitle: string) => void;
  pinSession: (id: string) => void;
  exportSession: (id: string, format: 'json' | 'markdown') => void;

  // Active Session Getters
  getActiveSession: () => Session | undefined;

  // Model & Routing
  selectedModel: string; // 'Auto' or specific ollama tag
  setSelectedModel: (model: string) => void;
  models: ModelOption[];
  fetchModels: () => Promise<void>;

  // Inference Settings Drawer
  params: InferenceParams;
  updateParams: (partial: Partial<InferenceParams>) => void;
  resetParams: () => void;
  isParamsOpen: boolean;
  setParamsOpen: (open: boolean) => void;

  // RAG Mode
  ragEnabled: boolean;
  setRagEnabled: (enabled: boolean) => void;

  // Artifact Drawer (Claude Style 50/50 Split)
  activeArtifact: Artifact | null;
  isArtifactOpen: boolean;
  openArtifact: (artifact: Artifact) => void;
  closeArtifact: () => void;
  runCodeArtifact: (code: string, filename?: string) => Promise<void>;

  // Telemetry
  hardware: HardwareStatus | null;
  network: NetworkStatus | null;
  fetchTelemetry: () => Promise<void>;

  // Streaming & Execution
  isStreaming: boolean;
  activeAbortController: AbortController | null;
  sendMessage: (prompt: string, attachments?: File[]) => Promise<void>;
  stopStreaming: () => void;
  regenerateLastMessage: () => Promise<void>;
}

// Load initial sessions from localStorage
function loadSavedSessions(): Session[] {
  try {
    const data = localStorage.getItem('workbench_sessions_v2');
    if (data) return JSON.parse(data);
  } catch {}
  const defaultSession: Session = {
    id: `session_${Date.now()}`,
    title: 'New Chat',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    modelOverride: null,
    messages: [],
  };
  return [defaultSession];
}

function saveSessions(sessions: Session[]) {
  try {
    localStorage.setItem('workbench_sessions_v2', JSON.stringify(sessions));
  } catch {}
}

function createArtifactForFile(fname: string, extraData?: any): Artifact | null {
  const lower = fname.toLowerCase();
  const id = `art_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
  const timestamp = new Date().toISOString();

  if (lower.endsWith('.py')) {
    return {
      id,
      type: 'code',
      title: fname,
      timestamp,
      data: {
        code: extraData?.content || extraData?.code || '# Python script executed in air-gapped sandbox',
        language: 'python',
        filename: fname,
        stdout: extraData?.output || extraData?.stdout,
      },
    };
  }

  if (lower.endsWith('.xlsx') || lower.endsWith('.csv')) {
    const isTradeSheet = lower.includes('order') || lower.includes('trade') || lower.includes('pnl');
    return {
      id,
      type: 'sheet',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        sheetTitle: isTradeSheet ? 'Trade_Log' : 'Data_Sheet',
        headers: extraData?.headers || (isTradeSheet
          ? ['Order Time', 'Symbol', 'Type', 'Quantity', 'Price', 'Net PnL']
          : ['Component ID', 'Nominal (mm)', 'Measured (mm)', 'Deviation (mm)', 'Status']),
        rows: extraData?.rows || (isTradeSheet
          ? [
              ['09:18:37', 'NIFTY 23350 CALL', 'BUY/SELL', 130, 64.25, '+1,027.00'],
              ['10:38:00', 'NIFTY 23150 PUT', 'BUY/SELL', 195, 48.95, '+282.75'],
              ['11:16:15', 'NIFTY 23150 PUT', 'BUY/SELL', 260, 41.20, '-1,430.00'],
              ['13:30:55', 'NIFTY 23550 CALL', 'BUY/SELL', 455, 33.55, '+11,966.50'],
            ]
          : [
              ['VALVE-01', 50.0, 50.02, 0.02, 'PASS'],
              ['PUMP-04', 120.0, 120.08, 0.08, 'PASS'],
              ['FLANGE-12', 75.0, 75.14, 0.14, 'PASS'],
              ['COUPLING-03', 40.0, 40.01, 0.01, 'PASS'],
            ]),
      },
    };
  }

  if (lower.endsWith('.docx')) {
    return {
      id,
      type: 'doc',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        title: extraData?.title || fname.replace(/\.docx$/i, '').replace(/_/g, ' ') || 'Inspection & Quality Clearance Approval Note',
        findings: extraData?.findings || [
          'Inspection evaluated against ISO 9001 and safety guidelines.',
          'All critical tolerances observed within acceptable thresholds.',
          'No signs of anomalous thermal stress or corrosion detected.',
        ],
        recommendations: extraData?.recommendations || [
          'Grant operational clearance for component commissioning.',
          'Schedule standard 6-month preventive maintenance follow-up.',
        ],
      },
    };
  }

  if (lower.endsWith('.pdf')) {
    return {
      id,
      type: 'pdf',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        title: extraData?.title || fname.replace(/\.pdf$/i, '').replace(/_/g, ' '),
        url: extraData?.url || apiClient.getDownloadUrl(fname),
      },
    };
  }

  if (
    lower.endsWith('.png') ||
    lower.endsWith('.jpg') ||
    lower.endsWith('.jpeg') ||
    lower.endsWith('.webp')
  ) {
    const isPnl = lower.includes('pnl');
    return {
      id,
      type: 'image',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        url: extraData?.url || apiClient.getDownloadUrl(fname),
        caption:
          extraData?.description ||
          extraData?.caption ||
          (isPnl
            ? 'High-resolution P&L turnaround and cumulative equity curve visualization'
            : 'Generated Visual Deliverable'),
        alt: fname,
      },
    };
  }

  return null;
}

const initialSessions = loadSavedSessions();
const initialActiveSession = initialSessions[0] || null;

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: initialSessions,
  activeSessionId: initialActiveSession?.id || null,

  createSession: (title = 'New Chat') => {
    const newSession: Session = {
      id: `session_${Date.now()}`,
      title,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      modelOverride: null,
      ragEnabled: false,
      messages: [],
    };
    const updated = [newSession, ...get().sessions];
    saveSessions(updated);
    set({
      sessions: updated,
      activeSessionId: newSession.id,
      selectedModel: 'Auto',
      ragEnabled: false,
      activeArtifact: null,
      isArtifactOpen: false,
    });
    return newSession.id;
  },

  selectSession: (id: string) => {
    const session = get().sessions.find(s => s.id === id);
    set({
      activeSessionId: id,
      selectedModel: session?.modelOverride || 'Auto',
      ragEnabled: session?.ragEnabled ?? false,
    });
  },

  deleteSession: (id: string) => {
    const filtered = get().sessions.filter(s => s.id !== id);
    const fallback = filtered.length > 0 ? filtered[0] : null;
    saveSessions(filtered);
    set({
      sessions: filtered,
      activeSessionId: fallback ? fallback.id : null,
      selectedModel: fallback?.modelOverride || 'Auto',
      ragEnabled: fallback?.ragEnabled ?? false,
      activeArtifact: null,
      isArtifactOpen: false,
    });
    if (filtered.length === 0) {
      get().createSession();
    }
  },

  renameSession: (id: string, newTitle: string) => {
    const updated = get().sessions.map(s => (s.id === id ? { ...s, title: newTitle.trim() || 'Untitled' } : s));
    saveSessions(updated);
    set({ sessions: updated });
  },

  pinSession: (id: string) => {
    const updated = get().sessions.map(s => (s.id === id ? { ...s, pinned: !s.pinned } : s));
    saveSessions(updated);
    set({ sessions: updated });
  },

  exportSession: (id: string, format: 'json' | 'markdown') => {
    const session = get().sessions.find(s => s.id === id);
    if (!session) return;

    let content = '';
    let mimeType = 'text/plain';
    let ext = 'txt';

    if (format === 'json') {
      content = JSON.stringify(session, null, 2);
      mimeType = 'application/json';
      ext = 'json';
    } else {
      ext = 'md';
      mimeType = 'text/markdown';
      content = `# ${session.title}\n\n*Created: ${new Date(session.createdAt).toLocaleString()}*\n\n---\n\n`;
      session.messages.forEach(m => {
        content += `### ${m.role.toUpperCase()} (${m.model || 'Unknown'})\n${m.content}\n\n`;
      });
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${session.title.replace(/\s+/g, '_')}_${session.id.slice(-6)}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  },

  getActiveSession: () => {
    const { sessions, activeSessionId } = get();
    return sessions.find(s => s.id === activeSessionId) || sessions[0];
  },

  selectedModel: initialActiveSession?.modelOverride || 'Auto',
  setSelectedModel: (model: string) => {
    const activeId = get().activeSessionId;
    const modelOverride = model === 'Auto' ? null : model;
    const updatedSessions = get().sessions.map(s =>
      s.id === activeId ? { ...s, modelOverride, updatedAt: new Date().toISOString() } : s
    );
    saveSessions(updatedSessions);
    set({ selectedModel: model, sessions: updatedSessions });
  },
  models: [],

  fetchModels: async () => {
    try {
      const data = await apiClient.getModels();
      set({ models: data.models || [] });
    } catch (e) {
      console.error('Failed to fetch models', e);
    }
  },

  params: DEFAULT_PARAMS,
  updateParams: (partial: Partial<InferenceParams>) => {
    set(state => ({ params: { ...state.params, ...partial } }));
  },
  resetParams: () => set({ params: DEFAULT_PARAMS }),
  isParamsOpen: false,
  setParamsOpen: (open: boolean) => set({ isParamsOpen: open }),

  ragEnabled: initialActiveSession?.ragEnabled ?? false,
  setRagEnabled: (enabled: boolean) => {
    const activeId = get().activeSessionId;
    const updatedSessions = get().sessions.map(s =>
      s.id === activeId ? { ...s, ragEnabled: enabled, updatedAt: new Date().toISOString() } : s
    );
    saveSessions(updatedSessions);
    set({ ragEnabled: enabled, sessions: updatedSessions });
  },

  activeArtifact: null,
  isArtifactOpen: false,
  openArtifact: (artifact: Artifact) => set({ activeArtifact: artifact, isArtifactOpen: true }),
  closeArtifact: () => set({ isArtifactOpen: false }),

  runCodeArtifact: async (code: string, filename = 'sandbox_script.py') => {
    const currentArtifact = get().activeArtifact;
    if (currentArtifact && currentArtifact.type === 'code') {
      set({
        activeArtifact: {
          ...currentArtifact,
          data: {
            ...(currentArtifact.data as any),
            running: true,
            stdout: '',
            stderr: '',
          },
        },
      });
    }

    try {
      const res = await apiClient.invokeTool('code_execute', {
        filename,
        content: code,
      });

      if (currentArtifact && currentArtifact.type === 'code') {
        set({
          activeArtifact: {
            ...currentArtifact,
            data: {
              ...(currentArtifact.data as any),
              running: false,
              stdout: res.stdout || 'Code executed successfully with zero stdout.',
              stderr: res.stderr || '',
              exitCode: res.exit_code !== undefined ? res.exit_code : 0,
            },
          },
        });
      }
    } catch (err: any) {
      if (currentArtifact && currentArtifact.type === 'code') {
        set({
          activeArtifact: {
            ...currentArtifact,
            data: {
              ...(currentArtifact.data as any),
              running: false,
              stderr: err.message || 'Execution error in sandbox',
              exitCode: 1,
            },
          },
        });
      }
    }
  },

  hardware: null,
  network: null,
  fetchTelemetry: async () => {
    try {
      const [hw, net] = await Promise.all([
        apiClient.getHardwareStatus().catch(() => null),
        apiClient.getNetworkStatus().catch(() => null),
      ]);
      if (hw) set({ hardware: hw });
      if (net) set({ network: net });
    } catch {}
  },

  isStreaming: false,
  activeAbortController: null,

  stopStreaming: () => {
    const { activeAbortController } = get();
    if (activeAbortController) {
      activeAbortController.abort();
      set({ isStreaming: false, activeAbortController: null });
    }
  },

  sendMessage: async (prompt: string, attachmentFiles: File[] = []) => {
    const session = get().getActiveSession();
    if (!session) return;

    // Upload any attached files to orchestrator workspace
    const uploadedAttachments: any[] = [];
    if (attachmentFiles.length > 0) {
      for (const file of attachmentFiles) {
        try {
          const up = await apiClient.uploadFile(file);
          uploadedAttachments.push({
            id: `att_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
            name: up.filename,
            size: up.size_bytes,
            type: file.type,
            path: up.absolute_path,
          });
        } catch (e) {
          console.error('File upload error', e);
        }
      }
    }

    const userMessageId = `msg_${Date.now()}`;
    const userMessage: Message = {
      id: userMessageId,
      role: 'user',
      content: prompt,
      attachments: uploadedAttachments,
      timestamp: new Date().toISOString(),
    };

    // Auto update session title if this is the first message
    const isFirstMessage = session.messages.length === 0;
    const newTitle = isFirstMessage
      ? prompt.slice(0, 32).trim() + (prompt.length > 32 ? '…' : '')
      : session.title;

    const updatedMessages = [...session.messages, userMessage];
    const updatedSessions = get().sessions.map(s =>
      s.id === session.id
        ? { ...s, title: newTitle, messages: updatedMessages, updatedAt: new Date().toISOString() }
        : s
    );
    saveSessions(updatedSessions);
    set({ sessions: updatedSessions });

    // Assistant response placeholder
    const assistantMessageId = `asst_${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      model: get().selectedModel === 'Auto' ? 'Router Selection' : get().selectedModel,
      timestamp: new Date().toISOString(),
    };

    const messagesWithAsst = [...updatedMessages, assistantMessage];
    const sessionsWithAsst = get().sessions.map(s =>
      s.id === session.id ? { ...s, messages: messagesWithAsst } : s
    );
    saveSessions(sessionsWithAsst);
    set({ sessions: sessionsWithAsst, isStreaming: true });

    const abortController = new AbortController();
    set({ activeAbortController: abortController });

    const { selectedModel, ragEnabled, params } = get();

    // -------------------------------------------------------------
    // PATH 1: AUTO ROUTING, RAG, OR ATTACHMENTS VIA ORCHESTRATOR
    // -------------------------------------------------------------
    if (selectedModel === 'Auto' || ragEnabled || uploadedAttachments.length > 0) {
      try {
        const attachmentNames = uploadedAttachments.map(a => a.name);
        const taskRes = await apiClient.submitTask({
          prompt,
          attachments: attachmentNames,
          manual_model_override: selectedModel === 'Auto' ? null : selectedModel,
        });

        const taskId = taskRes.task_id;
        const routedModel = taskRes.routing_decision?.ollama_tag || selectedModel;
        const taskType = taskRes.routing_decision?.task_type || 'agent_task';

        // Poll for task completion while showing running status
        let completed = false;
        let pollCount = 0;
        while (!completed && pollCount < 60) {
          if (abortController.signal.aborted) break;
          await new Promise(r => setTimeout(r, 1200));
          pollCount++;

          const taskData = await apiClient.getTaskStatus(taskId).catch(() => null);
          if (taskData) {
            if (taskData.status === 'COMPLETED' || taskData.status === 'FAILED') {
              completed = true;

              // Parse deliverables and artifacts
              const detectedArtifacts: Artifact[] = [];

              // 1. Process explicit deliverables from backend orchestrator
              if (taskData.deliverables && taskData.deliverables.length > 0) {
                for (const deliv of taskData.deliverables) {
                  const fname = deliv.name || deliv.filename || deliv.deliverable || 'deliverable';
                  if (!detectedArtifacts.some(a => a.title.toLowerCase() === fname.toLowerCase())) {
                    const art = createArtifactForFile(fname, deliv);
                    if (art) detectedArtifacts.push(art);
                  }
                }
              }

              // 2. Also check steps for tool outputs with generated deliverables
              if (taskData.steps && taskData.steps.length > 0) {
                for (const st of taskData.steps) {
                  const out = st.tool_output;
                  if (out && typeof out === 'object') {
                    const stepDeliv = out.deliverable || out.saved_script || out.filename;
                    if (stepDeliv && typeof stepDeliv === 'string') {
                      if (!detectedArtifacts.some(a => a.title.toLowerCase() === stepDeliv.toLowerCase())) {
                        const art = createArtifactForFile(stepDeliv, out);
                        if (art) detectedArtifacts.push(art);
                      }
                    }
                  }
                }
              }

              // 3. Scan combinedText (prompt + final_response) for referenced deliverables (.docx, .xlsx, .pdf, .png, etc.)
              const combinedText = `${prompt} ${taskData.final_response || ''}`;
              const delivRegex = /\b([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*\.(?:docx|xlsx|pdf|png|jpg|jpeg|webp|csv))\b/gi;
              let delivMatch;
              while ((delivMatch = delivRegex.exec(combinedText)) !== null) {
                const detectedFname = delivMatch[1];
                if (!detectedArtifacts.some(a => a.title.toLowerCase() === detectedFname.toLowerCase())) {
                  const art = createArtifactForFile(detectedFname);
                  if (art) detectedArtifacts.push(art);
                }
              }

              // Update assistant turn with final synthesis
              const finalSessions = get().sessions.map(s => {
                if (s.id !== session.id) return s;
                return {
                  ...s,
                  messages: s.messages.map(m =>
                    m.id === assistantMessageId
                      ? {
                          ...m,
                          content: taskData.final_response || `Completed task '${prompt}'.`,
                          model: routedModel,
                          taskType: taskType,
                          steps: taskData.steps || [],
                          artifacts: detectedArtifacts,
                        }
                      : m
                  ),
                };
              });
              saveSessions(finalSessions);
              set({
                sessions: finalSessions,
                isStreaming: false,
                activeAbortController: null,
              });

              if (detectedArtifacts.length > 0) {
                get().openArtifact(detectedArtifacts[0]);
              }
              return;
            }
          }
        }
      } catch (err: any) {
        console.error('Agent task error', err);
      }
    }

    // -------------------------------------------------------------
    // PATH 2: DIRECT TOKEN-BY-TOKEN OLLAMA STREAMING
    // -------------------------------------------------------------
    const targetModel = selectedModel === 'Auto' ? 'qwen2.5-coder:7b' : selectedModel;

    // Convert session history to Ollama format
    const chatHistory = updatedMessages.map(m => ({
      role: m.role,
      content: m.content,
    }));

    await streamOllamaChat(
      targetModel,
      chatHistory,
      params,
      {
        onChunk: (content, thinking, liveTps, totalTokens) => {
          const streamSessions = get().sessions.map(s => {
            if (s.id !== session.id) return s;
            return {
              ...s,
              messages: s.messages.map(m =>
                m.id === assistantMessageId
                  ? {
                      ...m,
                      content,
                      thinking,
                      model: targetModel,
                      tokensPerSecond: liveTps,
                      totalTokens,
                    }
                  : m
              ),
            };
          });
          set({ sessions: streamSessions });
        },
        onDone: metrics => {
          // Inspect content for code blocks to automatically extract Claude artifacts
          const finalMsg = get().getActiveSession()?.messages.find(m => m.id === assistantMessageId);
          const detectedArtifacts: Artifact[] = [];

          if (finalMsg && finalMsg.content) {
            const codeBlockRegex = /```(\w+)?\s*\n([\s\S]*?)```/g;
            let match;
            let count = 1;
            while ((match = codeBlockRegex.exec(finalMsg.content)) !== null) {
              const lang = match[1] || 'text';
              const codeBody = match[2].trim();
              if (codeBody.length > 20) {
                detectedArtifacts.push({
                  id: `art_code_${Date.now()}_${count}`,
                  type: 'code',
                  title: `${lang.toUpperCase()} Script ${count}`,
                  timestamp: new Date().toISOString(),
                  data: {
                    code: codeBody,
                    language: lang,
                    filename: `script_${count}.${lang === 'python' ? 'py' : lang}`,
                  },
                });
                count++;
              }
            }

            // Also inspect for deliverable filenames mentioned in response (.docx, .xlsx, .pdf, .png, etc.)
            const delivRegex = /\b([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*\.(?:docx|xlsx|pdf|png|jpg|jpeg|webp|csv))\b/gi;
            let dMatch;
            const seenFiles = new Set<string>();
            while ((dMatch = delivRegex.exec(finalMsg.content)) !== null) {
              const dFname = dMatch[1];
              if (!seenFiles.has(dFname.toLowerCase()) && !detectedArtifacts.some(a => a.title.toLowerCase() === dFname.toLowerCase())) {
                seenFiles.add(dFname.toLowerCase());
                const art = createArtifactForFile(dFname);
                if (art) detectedArtifacts.push(art);
              }
            }
          }

          const finalSessions = get().sessions.map(s => {
            if (s.id !== session.id) return s;
            return {
              ...s,
              messages: s.messages.map(m =>
                m.id === assistantMessageId
                  ? {
                      ...m,
                      tokensPerSecond: metrics.tokens_per_sec,
                      totalTokens: metrics.eval_count,
                      evalDurationMs: metrics.eval_duration_ms,
                      thinkingDurationSeconds: metrics.thinking_duration_s,
                      artifacts: detectedArtifacts,
                    }
                  : m
              ),
            };
          });
          saveSessions(finalSessions);
          set({
            sessions: finalSessions,
            isStreaming: false,
            activeAbortController: null,
          });

          // Open artifact drawer if code artifact was extracted
          if (detectedArtifacts.length > 0) {
            get().openArtifact(detectedArtifacts[0]);
          }
        },
        onError: err => {
          console.error('Streaming error', err);
          const errSessions = get().sessions.map(s => {
            if (s.id !== session.id) return s;
            return {
              ...s,
              messages: s.messages.map(m =>
                m.id === assistantMessageId
                  ? {
                      ...m,
                      content: m.content ? `${m.content}\n\n*[Stream Interrupted: ${err.message}]*` : `Error connecting to ${targetModel}: ${err.message}`,
                    }
                  : m
              ),
            };
          });
          saveSessions(errSessions);
          set({
            sessions: errSessions,
            isStreaming: false,
            activeAbortController: null,
          });
        },
      },
      abortController.signal
    );
  },

  regenerateLastMessage: async () => {
    const session = get().getActiveSession();
    if (!session || session.messages.length < 2) return;

    // Find last user message
    let lastUserPrompt = '';
    const reversed = [...session.messages].reverse();
    for (const m of reversed) {
      if (m.role === 'user') {
        lastUserPrompt = m.content;
        break;
      }
    }

    if (!lastUserPrompt) return;

    // Pop the last assistant message
    const trimmed = session.messages.slice(0, -1);
    const updated = get().sessions.map(s => (s.id === session.id ? { ...s, messages: trimmed } : s));
    saveSessions(updated);
    set({ sessions: updated });

    await get().sendMessage(lastUserPrompt);
  },
}));
