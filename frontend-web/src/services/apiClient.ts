import { HardwareStatus, NetworkStatus, ModelOption, RAGChunk } from '../types';

const API_BASE = '/api/v1';

export const apiClient = {
  // Hardware & Network Telemetry
  async getHardwareStatus(): Promise<HardwareStatus> {
    const res = await fetch(`${API_BASE}/hardware-status`);
    if (!res.ok) throw new Error('Failed to fetch hardware status');
    return res.json();
  },

  async getNetworkStatus(): Promise<NetworkStatus> {
    const res = await fetch(`${API_BASE}/network-status`);
    if (!res.ok) throw new Error('Failed to fetch network status');
    return res.json();
  },

  // Models
  async getModels(): Promise<{ models: ModelOption[]; total_registered: number }> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch registered models');
    return res.json();
  },

  async getOllamaLibrary(): Promise<{ models: any[] }> {
    const res = await fetch(`${API_BASE}/models/ollama-library`);
    if (!res.ok) throw new Error('Failed to fetch ollama library');
    return res.json();
  },

  async pullModel(ollama_tag: string): Promise<any> {
    const res = await fetch(`${API_BASE}/models/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ollama_tag }),
    });
    return res.json();
  },

  async getPullStatus(tag: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/models/pull/${encodeURIComponent(tag)}/status`);
    return res.json();
  },

  // Tasks & Agent Orchestration
  async submitTask(payload: {
    prompt: string;
    attachments?: string[];
    manual_model_override?: string | null;
    task_id?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to submit agent task');
    return res.json();
  },

  async getTaskStatus(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/task/${encodeURIComponent(taskId)}`);
    if (!res.ok) throw new Error(`Task ${taskId} not found`);
    return res.json();
  },

  async deleteTask(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/task/${encodeURIComponent(taskId)}`, {
      method: 'DELETE',
    });
    return res.json();
  },

  async listTasks(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/tasks`);
    if (!res.ok) return [];
    return res.json();
  },

  // Tool Invocation (Sandbox, Spreadsheet, etc.)
  async invokeTool(toolName: string, toolArgs: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/tools/${encodeURIComponent(toolName)}/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool_args: toolArgs }),
    });
    if (!res.ok) throw new Error(`Failed to invoke tool ${toolName}`);
    return res.json();
  },

  // File Workspace
  async uploadFile(file: File): Promise<{ filename: string; absolute_path: string; size_bytes: number }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/workspace/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('File upload failed');
    return res.json();
  },

  getDownloadUrl(filename: string): string {
    return `${API_BASE}/workspace/download/${encodeURIComponent(filename)}`;
  },

  // Knowledge Base RAG
  async queryRagChunks(query: string, top_k: number = 4): Promise<{ query: string; results: RAGChunk[]; total_results: number }> {
    const res = await fetch(`${API_BASE}/knowledge-base/query-chunks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k }),
    });
    if (!res.ok) throw new Error('Failed to query knowledge base chunks');
    return res.json();
  },

  async listKbDocuments(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/knowledge-base/documents`);
    if (!res.ok) return [];
    return res.json();
  },

  async ingestDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/knowledge-base/ingest`, {
      method: 'POST',
      body: formData,
    });
    return res.json();
  }
};
