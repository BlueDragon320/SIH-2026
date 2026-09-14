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

  // User Session Management
  initUserSessions: (user: any) => Promise<void>;
  clearUserSessions: () => void;
  clearAllChats: () => Promise<void>;

  // Streaming & Execution
  isStreaming: boolean;
  activeAbortController: AbortController | null;
  sendMessage: (prompt: string, attachments?: File[]) => Promise<void>;
  stopStreaming: () => void;
  regenerateLastMessage: () => Promise<void>;
}

// Immediately purge older version caches from localStorage
try {
  if (typeof window !== 'undefined' && window.localStorage) {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const k = localStorage.key(i);
      if (k && (k.startsWith('workbench_sessions_v1') || k.startsWith('workbench_sessions_v2') || k.startsWith('workbench_sessions_v3') || k === 'workbench_sessions_v2' || k === 'workbench_sessions_v3')) {
        localStorage.removeItem(k);
      }
    }
  }
} catch {}

function getUserStorageKey(): string {
  try {
    const token = localStorage.getItem('wb_access_token');
    if (token) {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const payload = JSON.parse(jsonPayload);
      if (payload.sub) {
        return `workbench_sessions_v4_${payload.sub}`;
      }
    }
  } catch {}
  return 'workbench_sessions_v4';
}

// Load initial sessions from localStorage
function loadSavedSessions(): Session[] {
  try {
    const key = getUserStorageKey();
    const data = localStorage.getItem(key) || localStorage.getItem('workbench_sessions_v4');
    if (data) return JSON.parse(data);
  } catch {}
  const defaultSession: Session = {
    id: `session_${Date.now()}`,
    title: 'New Chat',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    modelOverride: null,
    ragEnabled: false,
    messages: [],
  };
  return [defaultSession];
}

export async function syncChatToBackend(session: Session) {
  if (!session || !session.messages || session.messages.length === 0) return;
  try {
    await apiClient.syncUserChat(
      session.id,
      session.title || 'Untitled Chat',
      JSON.stringify(session.messages)
    );
  } catch (e) {
    // Offline or network error
  }
}

export async function syncAllSessionsToBackend() {
  try {
    const sessions = useChatStore.getState()?.sessions || [];
    for (const s of sessions) {
      if (s.messages && s.messages.length > 0) {
        await syncChatToBackend(s);
      }
    }
  } catch {}
}

let syncTimeout: any = null;
function saveSessions(sessions: Session[]) {
  const key = getUserStorageKey();
  try {
    localStorage.setItem(key, JSON.stringify(sessions));
    localStorage.setItem('workbench_sessions_v3', JSON.stringify(sessions));
  } catch {}

  // Immediate debounced synchronization to backend
  clearTimeout(syncTimeout);
  syncTimeout = setTimeout(() => {
    try {
      const activeId = useChatStore.getState()?.activeSessionId;
      const active = sessions.find(s => s.id === activeId) || sessions[0];
      if (active && active.messages && active.messages.length > 0) {
        syncChatToBackend(active);
      }
    } catch {}
  }, 100);
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
        code: extraData?.content || extraData?.code || '',
        language: 'python',
        filename: fname,
        stdout: extraData?.output || extraData?.stdout,
        stderr: extraData?.stderr,
        exitCode: extraData?.exit_code,
      },
    };
  }

  if (lower.endsWith('.xlsx') || lower.endsWith('.csv')) {
    return {
      id,
      type: 'sheet',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        sheetTitle: extraData?.sheet_title || extraData?.sheetTitle || 'Sheet1',
        headers: extraData?.headers || [],
        rows: extraData?.rows || [],
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
        title: extraData?.title || fname.replace(/\.docx$/i, '').replace(/_/g, ' '),
        background: extraData?.background || '',
        findings: extraData?.findings || [],
        recommendations: extraData?.recommendations || [],
        signoff_name: extraData?.signoff_name,
        findings_table: extraData?.findings_table,
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
    return {
      id,
      type: 'image',
      title: fname,
      timestamp,
      data: {
        filename: fname,
        url: extraData?.url || apiClient.getDownloadUrl(fname),
        caption: extraData?.description || extraData?.caption || '',
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
      activeArtifact: null,
      isArtifactOpen: false,
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
    apiClient.deleteUserChat(id).catch(() => {});
    if (filtered.length === 0) {
      get().createSession();
    }
  },

  initUserSessions: async (user: any) => {
    if (!user) return;
    const userKey = `workbench_sessions_v3_${user.id || user.username}`;
    let loadedSessions: Session[] = [];

    // 1. Try local cache
    try {
      const cached = localStorage.getItem(userKey);
      if (cached) {
        loadedSessions = JSON.parse(cached);
      }
    } catch {}

    // 2. Fetch authoritative chat sessions from server (database / json store)
    try {
      const serverChats = await apiClient.getUserChats();
      if (serverChats && serverChats.length > 0) {
        const mappedSessions: Session[] = serverChats.map((c: any) => {
          let parsedMsgs = [];
          try {
            parsedMsgs = typeof c.messages_json === 'string' ? JSON.parse(c.messages_json) : c.messages_json || [];
          } catch {}
          return {
            id: c.session_id,
            title: c.session_name || 'Untitled Chat',
            createdAt: c.created_at || new Date().toISOString(),
            updatedAt: c.updated_at || new Date().toISOString(),
            modelOverride: null,
            ragEnabled: false,
            messages: parsedMsgs,
          };
        });

        if (mappedSessions.length > 0) {
          loadedSessions = mappedSessions;
        }
      } else if (serverChats && serverChats.length === 0) {
        // Backend has no saved chats (clean state)
        loadedSessions = [];
      }
    } catch (e) {
      console.error('Failed to fetch user chats from server', e);
    }

    if (loadedSessions.length === 0) {
      loadedSessions = [{
        id: `session_${Date.now()}`,
        title: 'New Chat',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        modelOverride: null,
        ragEnabled: false,
        messages: [],
      }];
    }

    try {
      localStorage.setItem(userKey, JSON.stringify(loadedSessions));
      localStorage.setItem('workbench_sessions_v3', JSON.stringify(loadedSessions));
    } catch {}

    set({
      sessions: loadedSessions,
      activeSessionId: loadedSessions[0]?.id || null,
      activeArtifact: null,
      isArtifactOpen: false,
    });
  },

  clearUserSessions: () => {
    const defaultSession: Session = {
      id: `session_${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      modelOverride: null,
      ragEnabled: false,
      messages: [],
    };
    set({
      sessions: [defaultSession],
      activeSessionId: defaultSession.id,
      activeArtifact: null,
      isArtifactOpen: false,
    });
  },

  clearAllChats: async () => {
    try {
      await apiClient.clearAllUserChats();
    } catch (e) {
      console.error('Failed to clear chats on server', e);
    }
    const defaultSession: Session = {
      id: `session_${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      modelOverride: null,
      ragEnabled: false,
      messages: [],
    };
    saveSessions([defaultSession]);
    set({
      sessions: [defaultSession],
      activeSessionId: defaultSession.id,
      activeArtifact: null,
      isArtifactOpen: false,
    });
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
        code,
        content: code,
        save_as: filename,
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
          let previewText = '';
          try {
            if (
              file.name.endsWith('.csv') ||
              file.name.endsWith('.tsv') ||
              file.name.endsWith('.txt') ||
              file.name.endsWith('.json') ||
              file.name.endsWith('.md') ||
              file.name.endsWith('.py')
            ) {
              previewText = await file.text();
            }
          } catch {}
          uploadedAttachments.push({
            id: `att_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
            name: up.filename,
            size: up.size_bytes,
            type: file.type,
            path: up.absolute_path,
            content: previewText,
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

    // Scope files strictly to those shared in this specific chat session
    const previousChatAttachments = (session.messages || []).flatMap(m => m.attachments || []);
    const allChatAttachments = [...previousChatAttachments, ...uploadedAttachments];
    const chatAttachmentNames = Array.from(new Set(allChatAttachments.map((a: any) => a.name).filter(Boolean)));

    // -------------------------------------------------------------
    // PATH 1: AUTO ROUTING, RAG, OR ATTACHMENTS VIA ORCHESTRATOR
    // -------------------------------------------------------------
    if (selectedModel === 'Auto' || ragEnabled || chatAttachmentNames.length > 0) {
      const taskStartTime = Date.now();
      try {
        const taskRes = await apiClient.submitTask({
          prompt,
          attachments: chatAttachmentNames,
          manual_model_override: selectedModel === 'Auto' ? null : selectedModel,
        });

        const taskId = taskRes.task_id;
        const routedModel = taskRes.routing_decision?.ollama_tag || selectedModel;
        const taskType = taskRes.routing_decision?.task_type || 'agent_task';

        // Poll for task completion while showing running status and live step progress
        let completed = false;
        let pollCount = 0;
        const maxPolls = 250; // Allow up to 5 minutes for comprehensive analysis and code execution
        while (!completed && pollCount < maxPolls) {
          if (abortController.signal.aborted) {
            set({ isStreaming: false, activeAbortController: null });
            return;
          }
          await new Promise(r => setTimeout(r, 1200));
          pollCount++;

          const taskData = await apiClient.getTaskStatus(taskId).catch(() => null);
          if (taskData) {
            // Live step updates so user sees active progress on UI
            if (taskData.status === 'RUNNING' && taskData.steps && taskData.steps.length > 0) {
              const lastStep = taskData.steps[taskData.steps.length - 1];
              const stepNotice = `Analyzing ${chatAttachmentNames.join(', ')}...\n\n* Step (${taskData.steps.length}): **${lastStep.description || 'Processing data'}**`;
              const progressSessions = get().sessions.map(s => {
                if (s.id !== session.id) return s;
                return {
                  ...s,
                  messages: s.messages.map(m =>
                    m.id === assistantMessageId
                      ? {
                          ...m,
                          content: stepNotice,
                          steps: taskData.steps,
                          model: routedModel,
                        }
                      : m
                  ),
                };
              });
              set({ sessions: progressSessions });
            }

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
                    if (Array.isArray(out.generated_images)) {
                      for (const imgName of out.generated_images) {
                        if (typeof imgName === 'string' && !detectedArtifacts.some(a => a.title.toLowerCase() === imgName.toLowerCase())) {
                          const art = createArtifactForFile(imgName, { filename: imgName, type: 'image' });
                          if (art) detectedArtifacts.push(art);
                        }
                      }
                    }
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

              // 3. Scan combinedText for generated deliverables or chat attachments
              const combinedText = `${prompt} ${taskData.final_response || ''}`;
              const delivRegex = /\b([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*\.(?:docx|xlsx|pdf|png|jpg|jpeg|webp|csv))\b/gi;
              let delivMatch;
              while ((delivMatch = delivRegex.exec(combinedText)) !== null) {
                const detectedFname = delivMatch[1];
                const isChatAttachment = chatAttachmentNames.some(a => a.toLowerCase() === detectedFname.toLowerCase());
                const isGeneratedDeliverable = (taskData.final_response || '').toLowerCase().includes(detectedFname.toLowerCase());
                if ((isChatAttachment || isGeneratedDeliverable) && !detectedArtifacts.some(a => a.title.toLowerCase() === detectedFname.toLowerCase())) {
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
                          evalDurationMs: Date.now() - taskStartTime,
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
                const imageArt = detectedArtifacts.find(a => a.type === 'image');
                const wantsImage = /\b(image|images|chart|charts|plot|plots|graph|graphs|visual|visuals)\b/i.test(prompt);
                if (imageArt && (wantsImage || detectedArtifacts[0].type === 'code')) {
                  get().openArtifact(imageArt);
                } else {
                  get().openArtifact(detectedArtifacts[0]);
                }
              }
              return;
            }
          }
        }

        if (!completed) {
          const timeoutSessions = get().sessions.map(s => {
            if (s.id !== session.id) return s;
            return {
              ...s,
              messages: s.messages.map(m =>
                m.id === assistantMessageId
                  ? {
                      ...m,
                      content: `The analysis task for ${chatAttachmentNames.join(', ')} is taking longer than expected. The agent is still processing in the background.`,
                      model: routedModel,
                    }
                  : m
              ),
            };
          });
          saveSessions(timeoutSessions);
          set({
            sessions: timeoutSessions,
            isStreaming: false,
            activeAbortController: null,
          });
        }
        return; // Strict return: NEVER fall through to PATH 2!
      } catch (err: any) {
        console.error('Agent task error', err);
        const errSessions = get().sessions.map(s => {
          if (s.id !== session.id) return s;
          return {
            ...s,
            messages: s.messages.map(m =>
              m.id === assistantMessageId
                ? {
                    ...m,
                    content: `Error executing task: ${err.message || err}`,
                  }
                : m
            ),
          };
        });
        saveSessions(errSessions);
        set({ sessions: errSessions, isStreaming: false, activeAbortController: null });
        return; // Strict return: NEVER fall through to PATH 2!
      }
    }

    // -------------------------------------------------------------
    // PATH 2: DIRECT TOKEN-BY-TOKEN OLLAMA STREAMING
    // -------------------------------------------------------------
    const targetModel = selectedModel === 'Auto' ? 'qwen2.5-coder:7b' : selectedModel;

    // Convert session history to Ollama format, injecting file contents if available
    const chatHistory = updatedMessages.map((m, idx) => {
      let content = m.content;
      if (idx === updatedMessages.length - 2 && m.role === 'user' && m.attachments && m.attachments.length > 0) {
        const fileSnippets = m.attachments
          .filter((a: any) => a.content)
          .map((a: any) => `\n\n[Attached File Content (${a.name})]:\n${a.content.slice(0, 16000)}`)
          .join('\n');
        if (fileSnippets) {
          content = `${content}\n${fileSnippets}`;
        }
      }
      return {
        role: m.role,
        content,
      };
    });

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

            // Also inspect for deliverable filenames (shared in chat or generated deliverables)
            const delivRegex = /\b([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*\.(?:docx|xlsx|pdf|png|jpg|jpeg|webp|csv))\b/gi;
            let dMatch;
            const seenFiles = new Set<string>();
            while ((dMatch = delivRegex.exec(finalMsg.content)) !== null) {
              const dFname = dMatch[1];
              const isChatAttachment = chatAttachmentNames.some(a => a.toLowerCase() === dFname.toLowerCase());
              const isGenerated = /\.(?:png|jpg|jpeg|webp|svg|docx|xlsx|pdf)$/i.test(dFname);
              if ((isChatAttachment || isGenerated) && !seenFiles.has(dFname.toLowerCase()) && !detectedArtifacts.some(a => a.title.toLowerCase() === dFname.toLowerCase())) {
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

          // Open artifact drawer if artifact was extracted
          if (detectedArtifacts.length > 0) {
            const imageArt = detectedArtifacts.find(a => a.type === 'image');
            const wantsImage = /\b(image|images|chart|charts|plot|plots|graph|graphs|visual|visuals)\b/i.test(prompt);
            if (imageArt && (wantsImage || detectedArtifacts[0].type === 'code')) {
              get().openArtifact(imageArt);
            } else {
              get().openArtifact(detectedArtifacts[0]);
            }
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
